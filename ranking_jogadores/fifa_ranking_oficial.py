#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 RANKING OFICIAL DE JOGADORES - Copa 2026
=============================================================================
Busca os endpoints oficiais da FIFA:
  - /topscorers → gols, assistências, chutes, chutes no alvo, minutos
  - /topcards   → cartões amarelos/vermelhos, faltas cometidas/sofridas

Cruza os dois e gera:
  - fifa_ranking_oficial.csv → ranking completo com Pontuação e Part. em Gol

COMO USAR:
  python fifa_ranking_oficial.py
  (Não precisa de nenhum arquivo local — busca direto da API)
=============================================================================
"""

import csv
import os

try:
    import requests
except ImportError:
    print("ERRO: instale o requests com:  pip install requests")
    raise

# ─── Configuração ──────────────────────────────────────────────────────────
BASE           = "https://api.fifa.com/api/v3"
ID_COMPETICAO  = "17"       # Copa do Mundo FIFA masculina
ID_TEMPORADA   = "285023"   # Edição 2026
TOP_N          = 50         # quantos jogadores incluir no CSV

# Pesos para calcular a Pontuação final de cada jogador
PESO_GOL              = 4
PESO_ASSISTENCIA      = 2
PESO_CHUTE_NO_ALVO    = 1
PESO_CARTAO_AMARELO   = -1
PESO_CARTAO_VERMELHO  = -3
PESO_FALTA_COMETIDA   = -0.5

ARQUIVO_SAIDA = "fifa_ranking_oficial.csv"

# ─── Sessão HTTP ────────────────────────────────────────────────────────────
SESSAO = requests.Session()
SESSAO.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Origin":          "https://inside.fifa.com",
    "Referer":         "https://inside.fifa.com/",
})


# ─── Funções auxiliares ─────────────────────────────────────────────────────

def texto(lista, idioma="pt"):
    """Extrai o texto no idioma desejado de uma lista de traduções da FIFA."""
    if not lista:
        return ""
    if isinstance(lista, str):
        return lista
    for item in lista:
        loc = (item.get("Locale") or "").lower()
        if loc == idioma or loc.startswith(idioma):
            return item.get("Description", "")
    return lista[0].get("Description", "")


def buscar(endpoint, params=None):
    """Faz a requisição e retorna a lista de resultados (Results)."""
    url = f"{BASE}/{endpoint}"
    params_base = {
        "idCompetition": ID_COMPETICAO,
        "idSeason":      ID_TEMPORADA,
        "language":      "pt",
        "count":         200,
    }
    if params:
        params_base.update(params)

    resp = SESSAO.get(url, params=params_base, timeout=30)
    resp.raise_for_status()
    return resp.json().get("Results", [])


def calcular_pontuacao(gols, assist, alvo, amarelo, vermelho, faltas):
    """
    Pontuação ponderada com base nos eventos oficiais.
    Gols e assistências têm peso maior por serem mais decisivos.
    Cartões e faltas têm peso negativo.
    """
    return round(
        gols    * PESO_GOL             +
        assist  * PESO_ASSISTENCIA     +
        alvo    * PESO_CHUTE_NO_ALVO   +
        amarelo * PESO_CARTAO_AMARELO  +
        vermelho * PESO_CARTAO_VERMELHO +
        faltas  * PESO_FALTA_COMETIDA,
        1,
    )


# ─── Programa principal ─────────────────────────────────────────────────────

def main():
    pasta  = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    saida  = os.path.join(pasta, ARQUIVO_SAIDA)

    # 1. Busca artilheiros e estatísticas ofensivas
    print("Buscando /topscorers...", flush=True)
    scorers = buscar("topscorers")
    print(f"  {len(scorers)} jogadores encontrados.")

    # 2. Busca dados de disciplina (cartões e faltas)
    print("Buscando /topcards...", flush=True)
    cartoes = buscar("topcards")
    print(f"  {len(cartoes)} jogadores encontrados.")

    # 3. Cria dicionário para cruzamento rápido pelo ID do jogador
    #    Assim: dado o IdPlayer de um artilheiro, achamos seus cartões em O(1)
    cartoes_por_id = {c["IdPlayer"]: c for c in cartoes}

    # 4. Monta o ranking combinado
    jogadores = []
    for p in scorers:
        pid = p["IdPlayer"]
        c   = cartoes_por_id.get(pid, {})   # dados de cartões (vazio se não tiver)

        # Estatísticas ofensivas (do /topscorers)
        gols    = p.get("Goals")           or 0
        assist  = p.get("Assists")          or 0
        chutes  = p.get("Shots")           or 0
        alvo    = p.get("AttemptsOnTarget") or 0
        jogos   = p.get("Matches")         or 0
        minutos = p.get("MinutesPlayed")   or 0

        # Estatísticas de disciplina (do /topcards)
        amarelo  = c.get("YellowCards")    or 0
        vermelho = c.get("RedCards")       or 0
        faltas   = c.get("FoulsCommitted") or 0
        sofreu   = c.get("FoulsSuffered")  or 0

        # Métricas calculadas
        part_em_gol = gols + assist
        pontuacao   = calcular_pontuacao(gols, assist, alvo, amarelo, vermelho, faltas)

        jogadores.append({
            "jogador":              texto(p.get("PlayerName")),
            "pais":                 p.get("IdCountry", ""),
            "jogos":                jogos,
            "minutos":              minutos,
            "gols":                 gols,
            "assistencias":         assist,
            "participacoes_em_gol": part_em_gol,
            "chutes":               chutes,
            "chutes_no_alvo":       alvo,
            "cartoes_amarelos":     amarelo,
            "cartoes_vermelhos":    vermelho,
            "faltas_cometidas":     faltas,
            "faltas_sofridas":      sofreu,
            "pontuacao":            pontuacao,
        })

    # 5. Ordena por Pontuação → Participações em Gol → Gols
    jogadores.sort(key=lambda x: (
        -x["pontuacao"],
        -x["participacoes_em_gol"],
        -x["gols"],
    ))

    # 6. Adiciona posição no ranking
    for i, j in enumerate(jogadores, 1):
        j["pos"] = i

    # 7. Salva CSV
    campos = [
        "pos", "jogador", "pais", "jogos", "minutos",
        "gols", "assistencias", "participacoes_em_gol",
        "chutes", "chutes_no_alvo",
        "cartoes_amarelos", "cartoes_vermelhos",
        "faltas_cometidas", "faltas_sofridas",
        "pontuacao",
    ]
    with open(saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(jogadores[:TOP_N])
    print(f"\nCSV salvo: {saida} ({min(TOP_N, len(jogadores))} jogadores)")

    # 8. Exibe Top 20 no terminal
    print(f"\n{'='*130}")
    print(" RANKING OFICIAL FIFA — Copa do Mundo 2026 | Top 20 por Pontuação")
    print(f"{'='*130}")
    print(f"{'#':<4} {'Jogador':<26} {'País':<5} {'Jogos':>6} {'Min':>5} "
          f"{'Gols':>5} {'Assist.':>8} {'Part.Gol':>9} "
          f"{'Chutes':>7} {'NoAlvo':>7} {'Am':>4} {'Vm':>4} {'Faltas':>7} {'Pontuação':>10}")
    print("-" * 130)

    for j in jogadores[:20]:
        print(
            f"{j['pos']:<4} {j['jogador'][:25]:<26} {j['pais']:<5} "
            f"{j['jogos']:>6} {j['minutos']:>5} "
            f"{j['gols']:>5} {j['assistencias']:>8} {j['participacoes_em_gol']:>9} "
            f"{j['chutes']:>7} {j['chutes_no_alvo']:>7} "
            f"{j['cartoes_amarelos']:>4} {j['cartoes_vermelhos']:>4} "
            f"{j['faltas_cometidas']:>7} {j['pontuacao']:>10.1f}"
        )

    print(f"\nLegenda:")
    print(f"  Part.Gol  = Participações em Gol (Gols + Assistências)")
    print(f"  NoAlvo    = Chutes no alvo")
    print(f"  Am / Vm   = Cartões Amarelo / Vermelho")
    print(f"\nPontuação = Gols×{PESO_GOL} + Assist×{PESO_ASSISTENCIA} + "
          f"NoAlvo×{PESO_CHUTE_NO_ALVO} + Amarelo×{PESO_CARTAO_AMARELO} + "
          f"Vermelho×{PESO_CARTAO_VERMELHO} + Faltas×{PESO_FALTA_COMETIDA}")


if __name__ == "__main__":
    main()
