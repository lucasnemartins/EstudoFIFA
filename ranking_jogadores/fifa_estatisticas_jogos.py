#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 ESTATÍSTICAS POR JOGO - Copa 2026
=============================================================================
Varre o endpoint /timelines da API da FIFA para todos os jogos já
disputados da Copa 2026 e gera 4 arquivos CSV:

  - fifa_artilharia.csv      → gols por jogador
  - fifa_faltas.csv          → faltas cometidas por jogador
  - fifa_chutes.csv          → chutes a gol por jogador
  - fifa_destaque_jogo.csv   → melhor jogador por partida (score ponderado)

COMO USAR:
  1. Rode primeiro o fifa_extrair_jogos.py para ter o JSON base
  2. python fifa_estatisticas_jogos.py
=============================================================================
"""

import csv
import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime, timezone

# ─── Verifica a biblioteca requests ────────────────────────────────────────
try:
    import requests
except ImportError:
    print("ERRO: instale o requests com:  pip install requests")
    raise

# ─── Configuração ──────────────────────────────────────────────────────────
BASE             = "https://api.fifa.com/api/v3"
ID_TEMPORADA     = "285023"          # Copa do Mundo 2026
ARQUIVO_ENTRADA  = "fifa_jogos_completo.json"
PAUSA            = 0.25              # segundos entre requisições
TOP_N            = 30                # quantos jogadores salvar em cada ranking

# Pesos do score de destaque por jogo
PONTOS = {
    0:  +4,     # Gol
    41: +4,     # Gol de pênalti
    34: +3,     # Gol contra (menor peso)
    1:  +2,     # Assistência
    12: +1,     # Chute a gol
    57: +1,     # Gol evitado (defesa)
    18: -0.5,   # Falta cometida
    2:  -1,     # Cartão amarelo
    3:  -3,     # Cartão vermelho
}

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


def nome_jogador(evento):
    """
    Extrai nome e seleção do campo EventDescription.
    Formato esperado: 'NOME (Seleção) fez algo...'
    """
    desc = texto(evento.get("EventDescription"))
    if not desc:
        return "", ""
    m = re.match(r"^([^(]+)\(([^)]+)\)", desc.strip())
    if m:
        return m.group(1).strip().title(), m.group(2).strip()
    return desc[:40], ""


def ja_disputado(jogo):
    """Retorna True se o jogo já aconteceu (data passou)."""
    iso = jogo.get("Date") or jogo.get("LocalDate")
    if not iso:
        return False
    try:
        d = datetime.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S")
        return d < datetime.now(timezone.utc).replace(tzinfo=None)
    except Exception:
        return False


def salvar_csv(caminho, cabecalho, linhas):
    """Salva uma lista de dicionários em CSV com encoding UTF-8 BOM (abre certo no Excel)."""
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cabecalho)
        w.writeheader()
        w.writerows(linhas)
    print(f"  Salvo: {caminho}")


# ─── Programa principal ─────────────────────────────────────────────────────

def main():
    pasta = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    entrada = os.path.join(pasta, ARQUIVO_ENTRADA)

    # 1. Carrega o JSON base gerado pelo fifa_extrair_jogos.py
    if not os.path.exists(entrada):
        print(f"Arquivo não encontrado: {entrada}")
        print("Rode primeiro o fifa_extrair_jogos.py.")
        return

    print(f"Carregando {ARQUIVO_ENTRADA}...", flush=True)
    with open(entrada, encoding="utf-8") as f:
        dados = json.load(f)

    # 2. Filtra só os jogos da Copa 2026 já disputados
    jogos_2026 = [j for j in dados if str(j.get("IdSeason")) == ID_TEMPORADA]
    disputados = [j for j in jogos_2026 if ja_disputado(j)]
    print(f"{len(disputados)} jogos disputados encontrados.\n", flush=True)

    # 3. Acumuladores globais (somam dados de todos os jogos)
    artilharia   = defaultdict(lambda: {"gols": 0, "time": ""})
    faltas_rank  = defaultdict(lambda: {"faltas": 0, "time": ""})
    chutes_rank  = defaultdict(lambda: {"chutes": 0, "time": ""})
    destaque_jogos = []

    # 4. Percorre cada jogo e baixa seus eventos do endpoint /timelines
    print("Baixando eventos de cada jogo...", flush=True)
    erros = 0

    for i, jogo in enumerate(disputados):
        idc  = jogo.get("IdCompetition")
        ids  = jogo.get("IdSeason")
        idst = jogo.get("IdStage")
        idm  = jogo.get("IdMatch")

        casa = jogo.get("Home") or {}
        fora = jogo.get("Away") or {}
        nc   = texto(casa.get("TeamName"))
        nf   = texto(fora.get("TeamName"))
        gc   = casa.get("Score", "?")
        gf   = fora.get("Score", "?")
        data = (jogo.get("Date") or "")[:10]

        if not all([idc, ids, idst, idm]):
            erros += 1
            continue

        try:
            resp = SESSAO.get(
                f"{BASE}/timelines/{idc}/{ids}/{idst}/{idm}",
                params={"language": "pt"},
                timeout=15,
            )
            if not resp.ok:
                erros += 1
                continue
            eventos = resp.json().get("Event", [])
        except Exception as e:
            print(f"  Erro no jogo {idm}: {e}")
            erros += 1
            continue

        # 5. Processa cada evento do jogo atual
        score_jogo = defaultdict(lambda: {
            "score": 0, "time": "",
            "gols": 0, "assistencias": 0,
            "chutes": 0, "chances_criadas": 0,
            "faltas": 0,
        })

        for evento in eventos:
            tipo          = evento.get("Type")
            nome, equipe  = nome_jogador(evento)
            if not nome:
                continue

            p = score_jogo[nome]
            if not p["time"]:
                p["time"] = equipe

            # Acumuladores globais
            if tipo in (0, 41):             # gol / gol de pênalti
                artilharia[nome]["gols"] += 1
                artilharia[nome]["time"]  = equipe
                p["gols"]            += 1
                p["chances_criadas"] += 1
                p["score"]           += PONTOS.get(tipo, 0)

            elif tipo == 34:                # gol contra
                artilharia[nome]["gols"] += 1
                artilharia[nome]["time"]  = equipe
                p["gols"] += 1

            elif tipo == 1:                 # assistência
                p["assistencias"]    += 1
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[1]

            elif tipo == 12:                # chute a gol
                chutes_rank[nome]["chutes"] += 1
                chutes_rank[nome]["time"]    = equipe
                p["chutes"]          += 1
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[12]

            elif tipo == 57:                # gol evitado
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[57]

            elif tipo == 18:                # falta cometida
                faltas_rank[nome]["faltas"] += 1
                faltas_rank[nome]["time"]    = equipe
                p["faltas"] += 1
                p["score"]  += PONTOS[18]

            elif tipo in (2, 3):            # cartão amarelo / vermelho
                p["score"] += PONTOS[tipo]

        # 6. Destaque do jogo = jogador com maior score
        if score_jogo:
            dest_nome, dest = max(score_jogo.items(), key=lambda x: x[1]["score"])
            destaque_jogos.append({
                "data":            data,
                "jogo":            f"{nc} {gc} x {gf} {nf}",
                "destaque":        dest_nome,
                "time":            dest["time"],
                "gols":            dest["gols"],
                "assistencias":    dest["assistencias"],
                "chutes_a_gol":    dest["chutes"],
                "chances_criadas": dest["chances_criadas"],
                "faltas":          dest["faltas"],
                "score":           round(dest["score"], 1),
            })

        time.sleep(PAUSA)
        if (i + 1) % 16 == 0:
            print(f"  {i + 1}/{len(disputados)} jogos processados...", flush=True)

    print(f"\nConcluído. Erros: {erros}\n")

    # 7. Salva os 4 CSVs
    print("Salvando arquivos CSV...")

    art = sorted(artilharia.items(), key=lambda x: -x[1]["gols"])
    salvar_csv(
        os.path.join(pasta, "fifa_artilharia.csv"),
        ["pos", "jogador", "time", "gols"],
        [{"pos": i, "jogador": n, "time": v["time"], "gols": v["gols"]}
         for i, (n, v) in enumerate(art[:TOP_N], 1)],
    )

    flt = sorted(faltas_rank.items(), key=lambda x: -x[1]["faltas"])
    salvar_csv(
        os.path.join(pasta, "fifa_faltas.csv"),
        ["pos", "jogador", "time", "faltas"],
        [{"pos": i, "jogador": n, "time": v["time"], "faltas": v["faltas"]}
         for i, (n, v) in enumerate(flt[:TOP_N], 1)],
    )

    cht = sorted(chutes_rank.items(), key=lambda x: -x[1]["chutes"])
    salvar_csv(
        os.path.join(pasta, "fifa_chutes.csv"),
        ["pos", "jogador", "time", "chutes"],
        [{"pos": i, "jogador": n, "time": v["time"], "chutes": v["chutes"]}
         for i, (n, v) in enumerate(cht[:TOP_N], 1)],
    )

    salvar_csv(
        os.path.join(pasta, "fifa_destaque_jogo.csv"),
        ["data", "jogo", "destaque", "time", "gols",
         "assistencias", "chutes_a_gol", "chances_criadas", "faltas", "score"],
        destaque_jogos,
    )

    # 8. Exibe resumo no terminal
    print("\n=== ARTILHARIA (Top 10) ===")
    print(f"{'#':<4} {'Jogador':<28} {'Time':<22} {'Gols':>5}")
    print("-" * 62)
    for i, (n, v) in enumerate(art[:10], 1):
        print(f"{i:<4} {n:<28} {v['time']:<22} {v['gols']:>5}")

    print("\n=== RANKING DE FALTAS (Top 10) ===")
    print(f"{'#':<4} {'Jogador':<28} {'Time':<22} {'Faltas':>7}")
    print("-" * 64)
    for i, (n, v) in enumerate(flt[:10], 1):
        print(f"{i:<4} {n:<28} {v['time']:<22} {v['faltas']:>7}")

    print("\n=== CHUTES A GOL (Top 10) ===")
    print(f"{'#':<4} {'Jogador':<28} {'Time':<22} {'Chutes':>7}")
    print("-" * 64)
    for i, (n, v) in enumerate(cht[:10], 1):
        print(f"{i:<4} {n:<28} {v['time']:<22} {v['chutes']:>7}")

    print("\n=== DESTAQUES POR JOGO (Top 10 por score) ===")
    top10 = sorted(destaque_jogos, key=lambda x: x["score"], reverse=True)[:10]
    print(f"{'#':<4} {'Data':<12} {'Jogo':<36} {'Destaque':<26} {'Seleção':<22} {'Gols':>5} {'Assist':>7} {'Score':>6}")
    print("-" * 122)
    for i, r in enumerate(top10, 1):
        print(f"{i:<4} {r['data']:<12} {r['jogo'][:35]:<36} {r['destaque'][:25]:<26} {r['time']:<22} {r['gols']:>5} {r['assistencias']:>7} {r['score']:>6.1f}")

    print("\nPronto! 4 arquivos CSV gerados na pasta FIFA.")


if __name__ == "__main__":
    main()
