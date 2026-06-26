#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 EXTRATOR DE JOGOS DA COPA DO MUNDO (API publica da FIFA - api.fifa.com/v3)
=============================================================================
O QUE ELE FAZ:
  1. Descobre TODAS as edicoes (temporadas) da Copa do Mundo, de 1930 ate hoje.
  2. Baixa todos os jogos de cada edicao.
  3. Gera uma planilha (CSV) com data legivel e uma coluna de VENCEDOR.
  4. Gera uma "previsao" de campeao de 2026 = ranking dos favoritos com base
     no desempenho real ate agora (heuristica simples, NAO e adivinhacao).
  5. Salva tambem o JSON cru completo (nada se perde).

COMO USAR:
  1. pip install requests
  2. python fifa_extrair_jogos.py
  (Os arquivos sao salvos na mesma pasta deste arquivo.)
=============================================================================
"""

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

print("=" * 60, flush=True)
print(" EXTRATOR DE JOGOS DA COPA DO MUNDO - iniciando...", flush=True)
print(" Python:", sys.version.split()[0], flush=True)
print(" Pasta atual:", os.getcwd(), flush=True)
print("=" * 60, flush=True)

try:
    import requests
except ImportError:
    print("\nERRO: a biblioteca 'requests' nao esta instalada.")
    print("Rode no terminal:  pip install requests")
    input("\nPressione ENTER para fechar...")
    sys.exit(1)

# =============================================================================
# CONFIGURACAO  --  mexa so aqui
# =============================================================================

ID_COMPETICAO = "17"           # 17 = Copa do Mundo FIFA masculina
ID_TEMPORADA_2026 = "285023"   # edicao de 2026 (usada para a previsao)

# Baixar TODAS as edicoes (1930..2026)? Se False, baixa so a de 2026.
TODAS_AS_EDICOES = True

# Plano B: se a descoberta automatica de temporadas falhar, cole aqui os
# idSeason que voce quiser (descubra-os pelo F12 > Network no site da FIFA).
# Ex.: TEMPORADAS_MANUAIS = ["285023", "255711"]
TEMPORADAS_MANUAIS = []

IDIOMA = "pt"
# Fuso horario para exibir os horarios dos jogos. A FIFA entrega tudo em UTC;
# -3 = horario de Brasilia. Troque se quiser outro (ex.: -4 para Manaus/AM, 0 para UTC).
FUSO_HORARIO = -3
POR_PAGINA = 1000              # alto o bastante para pegar uma edicao inteira
PAUSA = 0.4                    # pausa entre requisicoes (segundos)

# Baixar tambem eventos jogo a jogo (gols, cartoes, escalacoes)? Bem mais lento.
BAIXAR_DETALHE_DE_CADA_JOGO = False

ARQUIVO_JSON     = "fifa_jogos_completo.json"
ARQUIVO_CSV      = "fifa_jogos.csv"
ARQUIVO_PREVISAO = "fifa_previsao_campeao_2026.csv"
ARQUIVO_DETALHE  = "fifa_jogos_detalhe.json"

# =============================================================================
# DAQUI PRA BAIXO NAO PRECISA MEXER
# =============================================================================

BASE = "https://api.fifa.com/api/v3"

SESSAO = requests.Session()
SESSAO.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Origin": "https://inside.fifa.com",
    "Referer": "https://inside.fifa.com/",
})


def get(url, params=None, tentativas=4):
    """GET que devolve JSON. Tenta de novo se vier vazio/nao-JSON e, se falhar
    de vez, mostra o que chegou (para diagnosticar)."""
    ultimo_texto, ultimo_status = "", None
    for n in range(1, tentativas + 1):
        resp = SESSAO.get(url, params=params, timeout=30)
        ultimo_status, ultimo_texto = resp.status_code, (resp.text or "")
        if resp.ok and ultimo_texto.strip():
            try:
                return resp.json()
            except ValueError:
                pass
        espera = 1.5 * n
        print(f"    tentativa {n} falhou (status {ultimo_status}). Aguardando {espera:.0f}s...",
              flush=True)
        time.sleep(espera)
    print("\n  Nao consegui obter JSON valido da API.")
    print(f"  Ultimo status HTTP: {ultimo_status}")
    print("  Inicio da resposta (ate 500 caracteres):")
    print("  " + (ultimo_texto[:500] if ultimo_texto else "(vazia)"))
    raise RuntimeError("API nao devolveu JSON valido.")


def get_silencioso(url, params=None):
    """Igual ao get, mas devolve None em vez de quebrar (para testar endpoints)."""
    try:
        resp = SESSAO.get(url, params=params, timeout=30)
        if resp.ok and (resp.text or "").strip():
            return resp.json()
    except Exception:
        pass
    return None


def texto_localizado(lista, idioma=IDIOMA):
    """Campos da FIFA vem como lista de traducoes; escolhe a do idioma desejado."""
    if not lista:
        return ""
    if isinstance(lista, str):
        return lista
    for item in lista:
        loc = (item.get("Locale") or "").lower()
        if loc == idioma.lower() or loc.startswith(idioma.lower()):
            return item.get("Description", "")
    return lista[0].get("Description", "")


def padroniza_nome(nome):
    """Unifica selecoes que mudaram de nome.
    Alemanha + Alemanha Ocidental (RFA) viram uma so; a Oriental (RDA) fica separada."""
    if not nome:
        return nome
    n = nome.lower().strip()
    if "oriental" in n or "rda" in n or "east germany" in n:   # Alemanha Oriental: separada
        return nome
    if "aleman" in n or "germany" in n or "rfa" in n:          # Alemanha + Ocidental
        return "Alemanha"
    mapa = {  # sucessoras reconhecidas pela FIFA (opcional)
        "uniao sovietica": "Russia", "união soviética": "Russia", "urss": "Russia",
        "soviet union": "Russia",
        "iugoslavia": "Servia", "iugoslávia": "Servia", "yugoslavia": "Servia",
    }
    return mapa.get(n, nome)


def nome_time(time_dict):
    """Nome do time ja padronizado (Alemanha unificada etc.)."""
    return padroniza_nome(texto_localizado((time_dict or {}).get("TeamName")))


def descobrir_temporadas(id_competicao):
    """Tenta descobrir todas as temporadas (edicoes) da competicao.
    Retorna lista de dicts: {'id':..., 'nome':...}."""
    candidatos = [
        (f"{BASE}/competitions/{id_competicao}/seasons",
         {"count": 1000, "language": IDIOMA}),
        (f"{BASE}/seasons",
         {"idCompetition": id_competicao, "count": 1000, "language": IDIOMA}),
        (f"{BASE}/competitions/seasons",
         {"idCompetition": id_competicao, "count": 1000, "language": IDIOMA}),
    ]
    for url, params in candidatos:
        dados = get_silencioso(url, params)
        resultados = (dados or {}).get("Results") if isinstance(dados, dict) else None
        if resultados:
            temporadas = []
            for s in resultados:
                ids = s.get("IdSeason") or s.get("IdCompetitionSeason")
                if not ids:
                    continue
                temporadas.append({"id": str(ids), "nome": texto_localizado(s.get("Name"))})
            if temporadas:
                print(f"Descobertas {len(temporadas)} edicoes via {url}", flush=True)
                return temporadas
    return []


def baixar_jogos_de_uma_temporada(id_competicao, id_temporada):
    """Baixa os jogos de UMA edicao (sem 'from' - a API nao aceita esse parametro)."""
    params = {
        "idCompetition": id_competicao,
        "idSeason": id_temporada,
        "count": POR_PAGINA,
        "language": IDIOMA,
    }
    dados = get(f"{BASE}/calendar/matches", params=params)
    return dados.get("Results", []) or []


def formatar_data(iso, eh_utc=True):
    """'2026-06-11T20:00:00Z' (UTC) -> '11/06/2026 17:00' no fuso configurado.
    Se o horario nao for UTC (campo LocalDate), mostra como veio."""
    if not iso:
        return ""
    try:
        d = datetime.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S")
        if eh_utc:
            d = d + timedelta(hours=FUSO_HORARIO)
        return d.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(iso)


def _num(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


_AGORA = datetime.now(timezone.utc).replace(tzinfo=None)


def jogo_ja_disputado(jogo):
    """Um jogo conta como disputado se a data dele ja passou."""
    iso = jogo.get("Date") or jogo.get("LocalDate")
    if not iso:
        return False
    try:
        d = datetime.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S")
        return d < _AGORA
    except Exception:
        return False


def placares(jogo):
    """Devolve (gols_casa, gols_fora), procurando em mais de um campo possivel."""
    casa = jogo.get("Home") or {}
    fora = jogo.get("Away") or {}
    gc = _num(casa.get("Score"))
    gf = _num(fora.get("Score"))
    if gc is None:
        gc = _num(jogo.get("HomeTeamScore"))
    if gf is None:
        gf = _num(jogo.get("AwayTeamScore"))
    return gc, gf


def descobrir_vencedor(jogo):
    """Nome do pais vencedor, 'Empate', ou '' se o jogo ainda nao foi disputado."""
    if not jogo_ja_disputado(jogo):
        return ""

    casa = jogo.get("Home") or {}
    fora = jogo.get("Away") or {}
    nome_casa = nome_time(casa)
    nome_fora = nome_time(fora)

    gc, gf = placares(jogo)
    if gc is None or gf is None:
        return ""

    if gc > gf:
        return nome_casa
    if gf > gc:
        return nome_fora

    # empate no tempo normal: checa penaltis (mata-mata)
    pc = _num(jogo.get("HomeTeamPenaltyScore")) or _num(casa.get("PenaltyScore"))
    pf = _num(jogo.get("AwayTeamPenaltyScore")) or _num(fora.get("PenaltyScore"))
    if pc is not None and pf is not None and pc != pf:
        return (nome_casa if pc > pf else nome_fora) + " (penaltis)"

    return "Empate"


def linha_resumida(jogo):
    casa = jogo.get("Home") or {}
    fora = jogo.get("Away") or {}
    estadio = jogo.get("Stadium") or {}
    arbitros = jogo.get("Officials") or []
    arbitro = texto_localizado(arbitros[0].get("Name")) if arbitros else ""
    # "Date" vem em UTC (converter); se faltar, usa "LocalDate" (ja local, nao converter)
    data_iso = jogo.get("Date")
    eh_utc = True
    if not data_iso:
        data_iso = jogo.get("LocalDate")
        eh_utc = False

    return {
        "edicao": texto_localizado(jogo.get("SeasonName")),
        "data": formatar_data(data_iso, eh_utc),
        "time_casa": nome_time(casa),
        "gols_casa": casa.get("Score", ""),
        "gols_fora": fora.get("Score", ""),
        "time_fora": nome_time(fora),
        "pais_vencedor": descobrir_vencedor(jogo),
        "estadio": texto_localizado(estadio.get("Name")),
        "cidade": texto_localizado(estadio.get("CityName")),
        "publico": jogo.get("Attendance", ""),
        "arbitro": arbitro,
        "id_jogo": jogo.get("IdMatch", ""),
    }


def salvar_csv(linhas, caminho):
    if not linhas:
        print("Nenhuma linha para salvar no CSV.")
        return
    colunas = list(linhas[0].keys())
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(linhas)
    print(f"Planilha salva em: {caminho}", flush=True)


def salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"JSON salvo em: {caminho}", flush=True)


def calcular_previsao_2026(jogos):
    """Ranking dos favoritos de 2026 com base nos resultados ja disputados.
    Heuristica simples: pontos (vitoria=3, empate=1) + saldo de gols.
    NAO e uma previsao real, e so uma leitura do desempenho ate agora."""
    tabela = {}  # nome -> stats

    def slot(nome):
        return tabela.setdefault(nome, {
            "time": nome, "jogos": 0, "vitorias": 0, "empates": 0,
            "derrotas": 0, "gols_pro": 0, "gols_contra": 0, "pontos": 0,
        })

    for jogo in jogos:
        if str(jogo.get("IdSeason")) != str(ID_TEMPORADA_2026):
            continue
        casa, fora = jogo.get("Home") or {}, jogo.get("Away") or {}
        gc, gf = _num(casa.get("Score")), _num(fora.get("Score"))
        if gc is None or gf is None:
            continue  # nao disputado ainda
        nc = nome_time(casa)
        nf = nome_time(fora)
        if not nc or not nf:
            continue
        a, b = slot(nc), slot(nf)
        a["jogos"] += 1; b["jogos"] += 1
        a["gols_pro"] += gc; a["gols_contra"] += gf
        b["gols_pro"] += gf; b["gols_contra"] += gc
        if gc > gf:
            a["vitorias"] += 1; a["pontos"] += 3; b["derrotas"] += 1
        elif gf > gc:
            b["vitorias"] += 1; b["pontos"] += 3; a["derrotas"] += 1
        else:
            a["empates"] += 1; b["empates"] += 1
            a["pontos"] += 1; b["pontos"] += 1

    linhas = []
    for s in tabela.values():
        s["saldo_gols"] = s["gols_pro"] - s["gols_contra"]
        linhas.append(s)
    # ordena por pontos, depois saldo, depois gols feitos
    linhas.sort(key=lambda s: (s["pontos"], s["saldo_gols"], s["gols_pro"]), reverse=True)
    return linhas


def baixar_detalhe(jogos):
    detalhes, total = [], len(jogos)
    print(f"Baixando detalhe de {total} jogos (pode demorar)...", flush=True)
    for i, jogo in enumerate(jogos, 1):
        idc, ids = jogo.get("IdCompetition"), jogo.get("IdSeason")
        idstage, idm = jogo.get("IdStage"), jogo.get("IdMatch")
        if not all([idc, ids, idstage, idm]):
            continue
        try:
            detalhes.append(get(f"{BASE}/live/football/{idc}/{ids}/{idstage}/{idm}",
                                params={"language": IDIOMA}))
        except Exception as e:
            print(f"  aviso: falhou no jogo {idm}: {e}")
        if i % 20 == 0:
            print(f"  ... {i}/{total}", flush=True)
        time.sleep(PAUSA)
    return detalhes


def main():
    pasta = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    p = lambda nome: os.path.join(pasta, nome)
    print(f"Os arquivos serao salvos em:\n  {pasta}\n", flush=True)

    try:
        # 1) Define quais temporadas baixar
        if TODAS_AS_EDICOES:
            temporadas = descobrir_temporadas(ID_COMPETICAO)
            if not temporadas and TEMPORADAS_MANUAIS:
                temporadas = [{"id": t, "nome": t} for t in TEMPORADAS_MANUAIS]
            if not temporadas:
                print("Nao consegui descobrir as edicoes automaticamente.")
                print("Use o plano B: preencha TEMPORADAS_MANUAIS no topo do script")
                print("com os idSeason (descubra-os no F12 > Network do site da FIFA).")
                print("Por enquanto, vou baixar so a edicao de 2026.\n")
                temporadas = [{"id": ID_TEMPORADA_2026, "nome": "2026"}]
        else:
            temporadas = [{"id": ID_TEMPORADA_2026, "nome": "2026"}]

        # 2) Baixa os jogos de cada temporada
        todos = []
        for t in temporadas:
            print(f"Baixando edicao {t['nome']} (idSeason {t['id']})...", flush=True)
            try:
                jogos = baixar_jogos_de_uma_temporada(ID_COMPETICAO, t["id"])
                print(f"  -> {len(jogos)} jogos", flush=True)
                todos.extend(jogos)
            except Exception as e:
                print(f"  aviso: falhou nessa edicao: {e}", flush=True)
            time.sleep(PAUSA)

        if not todos:
            print("Nenhum jogo baixado. Verifique os IDs/edicoes.")
            return
        print(f"\nTotal geral: {len(todos)} jogos.\n", flush=True)

        # 3) Salva tudo cru + planilha resumida (data legivel + vencedor)
        salvar_json(todos, p(ARQUIVO_JSON))
        linhas = [linha_resumida(j) for j in todos]
        # ordena por data (jogos sem data vao para o fim)
        salvar_csv(linhas, p(ARQUIVO_CSV))

        # 4) Previsao / ranking de favoritos de 2026
        ranking = calcular_previsao_2026(todos)
        if ranking:
            salvar_csv(ranking, p(ARQUIVO_PREVISAO))
            print("\n--- FAVORITOS DE 2026 (por desempenho ate agora) ---")
            print("AVISO: heuristica simples baseada nos resultados ja disputados,")
            print("nao e uma previsao real de quem sera campeao.\n")
            print(f"{'#':<3}{'TIME':<22}{'J':>3}{'V':>3}{'E':>3}{'D':>3}{'SG':>5}{'PTS':>5}")
            for i, s in enumerate(ranking[:12], 1):
                print(f"{i:<3}{s['time'][:21]:<22}{s['jogos']:>3}{s['vitorias']:>3}"
                      f"{s['empates']:>3}{s['derrotas']:>3}{s['saldo_gols']:>5}{s['pontos']:>5}")
        else:
            print("\n(Sem jogos disputados de 2026 ainda para montar o ranking.)")

        # 5) (opcional) detalhe jogo a jogo
        if BAIXAR_DETALHE_DE_CADA_JOGO:
            salvar_json(baixar_detalhe(todos), p(ARQUIVO_DETALHE))

        print("\nPronto! Tudo certo.")

    except requests.HTTPError as e:
        print(f"\nErro de HTTP: {e}")
    except requests.ConnectionError as e:
        print(f"\nErro de conexao: {e}")
        print("Verifique internet/firewall/proxy para api.fifa.com.")
    except Exception as e:
        print(f"\nErro inesperado: {type(e).__name__}: {e}")
    finally:
        input("\nPressione ENTER para fechar...")


if __name__ == "__main__":
    main()