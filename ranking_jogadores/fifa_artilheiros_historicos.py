#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 ARTILHEIROS HISTÓRICOS - Todas as Copas do Mundo (1930-2026)
=============================================================================
Dataset com os artilheiros de cada Copa e ranking de carreira all-time.
Dados de 1930-2022 baseados nos registros oficiais da FIFA (hardcoded).
Dados de 2026 buscados em tempo real da API pública da FIFA.

Gera:
  - fifa_artilheiros_copa.csv    → artilheiros de cada edição
  - fifa_artilheiros_carreira.csv → gols acumulados na carreira (all-time)

COMO USAR:
  python fifa_artilheiros_historicos.py
=============================================================================
"""

import csv
from collections import defaultdict
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

PASTA = Path(__file__).parent

# ─── API FIFA 2026 ────────────────────────────────────────────────────────────
BASE_API       = "https://api.fifa.com/api/v3"
ID_COMPETICAO  = "17"
ID_TEMPORADA   = "285023"   # Copa 2026


def _texto(lista, idioma="pt"):
    if not lista:
        return ""
    if isinstance(lista, str):
        return lista
    for item in lista:
        loc = (item.get("Locale") or "").lower()
        if loc == idioma or loc.startswith(idioma):
            return item.get("Description", "")
    return lista[0].get("Description", "")


PAISES = {
    "AFG": "Afeganistão",      "ALB": "Albânia",           "ALG": "Argélia",
    "AND": "Andorra",          "ANG": "Angola",             "ARG": "Argentina",
    "ARM": "Armênia",          "AUS": "Austrália",          "AUT": "Áustria",
    "AZE": "Azerbaijão",       "BEL": "Bélgica",            "BEN": "Benin",
    "BFA": "Burkina Faso",     "BGD": "Bangladesh",         "BIH": "Bósnia",
    "BOL": "Bolívia",          "BRA": "Brasil",             "BUL": "Bulgária",
    "CAN": "Canadá",           "CHI": "Chile",              "CHN": "China",
    "CIV": "Costa do Marfim",  "CMR": "Camarões",           "COD": "Congo RD",
    "COL": "Colômbia",         "CRC": "Costa Rica",         "CRO": "Croácia",
    "CZE": "República Tcheca", "DEN": "Dinamarca",          "ECU": "Equador",
    "EGY": "Egito",            "ENG": "Inglaterra",         "ESP": "Espanha",
    "ETH": "Etiópia",          "FIN": "Finlândia",          "FRA": "França",
    "GAB": "Gabão",            "GER": "Alemanha",           "GHA": "Gana",
    "GRE": "Grécia",           "GTM": "Guatemala",          "HON": "Honduras",
    "HUN": "Hungria",          "IND": "Índia",              "IRI": "Irã",
    "IRL": "Irlanda",          "IRQ": "Iraque",             "ISL": "Islândia",
    "ISR": "Israel",           "ITA": "Itália",             "JAM": "Jamaica",
    "JOR": "Jordânia",         "JPN": "Japão",              "KOR": "Coreia do Sul",
    "KSA": "Arábia Saudita",   "KUW": "Kuwait",             "LBN": "Líbano",
    "LIB": "Líbia",            "MAR": "Marrocos",           "MEX": "México",
    "MLI": "Mali",             "MNE": "Montenegro",         "MOR": "Marrocos",
    "MWI": "Malawi",           "NED": "Holanda",            "NGA": "Nigéria",
    "NOR": "Noruega",          "NZL": "Nova Zelândia",      "PAK": "Paquistão",
    "PAN": "Panamá",           "PAR": "Paraguai",           "PER": "Peru",
    "PHI": "Filipinas",        "POL": "Polônia",            "POR": "Portugal",
    "QAT": "Catar",            "ROU": "Romênia",            "RSA": "África do Sul",
    "RUS": "Rússia",           "SCO": "Escócia",            "SEN": "Senegal",
    "SER": "Sérvia",           "SLO": "Eslováquia",         "SRB": "Sérvia",
    "SUI": "Suíça",            "SVN": "Eslovênia",          "SWE": "Suécia",
    "SYR": "Síria",            "THA": "Tailândia",          "TUN": "Tunísia",
    "TUR": "Turquia",          "UAE": "Emirados Árabes",    "UKR": "Ucrânia",
    "URU": "Uruguai",          "USA": "EUA",                "VEN": "Venezuela",
    "WAL": "País de Gales",    "YEM": "Iêmen",              "ZAM": "Zâmbia",
}


def _normalizar_nome(nome):
    """Converte 'Lionel MESSI' ou 'VINICIUS JUNIOR' para Title Case."""
    if not nome:
        return nome
    partes = nome.split()
    return " ".join(p.capitalize() if p.isupper() else p for p in partes)


def _pais(codigo):
    """Retorna o nome completo do país pelo código FIFA de 3 letras."""
    return PAISES.get(codigo, codigo)


def buscar_2026():
    """Retorna lista de (2026, 'EUA/Canadá/México', jogador, selecao, gols, jogos)."""
    if requests is None:
        print("  ⚠ requests não instalado — dados 2026 omitidos.")
        return [], None, None

    sessao = requests.Session()
    sessao.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept":          "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Origin":          "https://inside.fifa.com",
        "Referer":         "https://inside.fifa.com/",
    })

    try:
        resp = sessao.get(
            f"{BASE_API}/topscorers",
            params={
                "idCompetition": ID_COMPETICAO,
                "idSeason":      ID_TEMPORADA,
                "language":      "pt",
                "count":         100,
            },
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json().get("Results", [])
    except Exception as e:
        print(f"  ⚠ Erro ao buscar API 2026: {e}")
        return [], None, None

    sede = "EUA/Canadá/México"
    rows = []
    for p in results:
        gols  = p.get("Goals")   or 0
        jogos = p.get("Matches") or 0
        if gols == 0:
            continue
        jogador = _normalizar_nome(_texto(p.get("PlayerName")))
        selecao = _pais(p.get("IdCountry", ""))
        rows.append((2026, sede, jogador, selecao, gols, jogos))

    if not rows:
        return [], None, None

    lider = max(rows, key=lambda x: x[4])
    artilheiro_copa = (lider[2], lider[3], lider[4])
    return rows, artilheiro_copa, sede

# ─── Dataset histórico ───────────────────────────────────────────────────────
# Fonte: registros oficiais FIFA
# Formato: (ano, país_sede, jogador, seleção, gols, jogos)

ARTILHEIROS_POR_COPA = [
    # 1930 — Uruguai
    (1930, "Uruguai",      "Guillermo Stábile",  "Argentina",    8, 4),
    (1930, "Uruguai",      "Pedro Cea",           "Uruguai",      5, 4),
    (1930, "Uruguai",      "Bert Patenaude",      "EUA",          3, 3),
    (1930, "Uruguai",      "Guillermo Subiabre",  "Chile",        4, 3),
    # 1934 — Itália
    (1934, "Itália",       "Oldřich Nejedlý",    "Tchecoslováquia", 5, 4),
    (1934, "Itália",       "Angelo Schiavio",     "Itália",       4, 5),
    (1934, "Itália",       "Edmund Conen",        "Alemanha",     4, 4),
    # 1938 — França
    (1938, "França",       "Leônidas",            "Brasil",       7, 4),
    (1938, "França",       "Gyula Zsengellér",    "Hungria",      7, 4),
    (1938, "França",       "Silvio Piola",        "Itália",       5, 4),
    # 1950 — Brasil
    (1950, "Brasil",       "Ademir",              "Brasil",       8, 6),
    (1950, "Brasil",       "Oscar Míguez",        "Uruguai",      5, 4),
    (1950, "Brasil",       "Chico",               "Brasil",       4, 5),
    # 1954 — Suíça
    (1954, "Suíça",        "Sándor Kocsis",       "Hungria",     11, 5),
    (1954, "Suíça",        "Erich Probst",        "Áustria",      6, 5),
    (1954, "Suíça",        "Morlock",             "Alemanha",     6, 5),
    (1954, "Suíça",        "Helmut Rahn",         "Alemanha",     4, 5),
    (1954, "Suíça",        "Uwe Seeler",          "Alemanha",     2, 3),  # estreou jovem
    # 1958 — Suécia
    (1958, "Suécia",       "Just Fontaine",       "França",      13, 6),
    (1958, "Suécia",       "Pelé",                "Brasil",       6, 4),
    (1958, "Suécia",       "Helmut Rahn",         "Alemanha",     4, 5),
    (1958, "Suécia",       "Uwe Seeler",          "Alemanha",     2, 6),
    # 1962 — Chile
    (1962, "Chile",        "Garrincha",           "Brasil",       4, 5),
    (1962, "Chile",        "Vavá",                "Brasil",       4, 5),
    (1962, "Chile",        "Leonel Sánchez",      "Chile",        4, 6),
    (1962, "Chile",        "Dražan Jerković",     "Iugoslávia",   4, 5),
    (1962, "Chile",        "Flórián Albert",      "Hungria",      4, 4),
    (1962, "Chile",        "Valentin Ivanov",     "URSS",         4, 4),
    (1962, "Chile",        "Pelé",                "Brasil",       1, 2),  # lesionado
    (1962, "Chile",        "Uwe Seeler",          "Alemanha",     2, 6),
    # 1966 — Inglaterra
    (1966, "Inglaterra",   "Eusébio",             "Portugal",     9, 6),
    (1966, "Inglaterra",   "Helmut Haller",       "Alemanha",     6, 6),
    (1966, "Inglaterra",   "Geoff Hurst",         "Inglaterra",   4, 6),
    (1966, "Inglaterra",   "Uwe Seeler",          "Alemanha",     3, 6),
    (1966, "Inglaterra",   "Pelé",                "Brasil",       1, 2),  # lesionado
    # 1970 — México
    (1970, "México",       "Gerd Müller",         "Alemanha",    10, 6),
    (1970, "México",       "Jairzinho",           "Brasil",       7, 6),
    (1970, "México",       "Teofilo Cubillas",    "Peru",         5, 5),
    (1970, "México",       "Uwe Seeler",          "Alemanha",     3, 6),
    (1970, "México",       "Pelé",                "Brasil",       4, 6),
    # 1974 — Alemanha
    (1974, "Alemanha",     "Grzegorz Lato",       "Polônia",      7, 7),
    (1974, "Alemanha",     "Andrzej Szarmach",    "Polônia",      5, 7),
    (1974, "Alemanha",     "Gerd Müller",         "Alemanha",     4, 6),
    (1974, "Alemanha",     "Johan Neeskens",      "Holanda",      4, 7),
    # 1978 — Argentina
    (1978, "Argentina",    "Mario Kempes",        "Argentina",    6, 7),
    (1978, "Argentina",    "Teofilo Cubillas",    "Peru",         5, 6),
    (1978, "Argentina",    "Rob Rensenbrink",     "Holanda",      5, 7),
    (1978, "Argentina",    "Karl-Heinz Rummenigge","Alemanha",    3, 6),
    # 1982 — Espanha
    (1982, "Espanha",      "Paolo Rossi",         "Itália",       6, 7),
    (1982, "Espanha",      "Karl-Heinz Rummenigge","Alemanha",    5, 5),
    (1982, "Espanha",      "Zbigniew Boniek",     "Polônia",      4, 5),
    (1982, "Espanha",      "Grzegorz Lato",       "Polônia",      3, 7),
    # 1986 — México
    (1986, "México",       "Gary Lineker",        "Inglaterra",   6, 5),
    (1986, "México",       "Diego Maradona",      "Argentina",    5, 7),
    (1986, "México",       "Emilio Butragueño",   "Espanha",      5, 5),
    (1986, "México",       "Karl-Heinz Rummenigge","Alemanha",    2, 5),
    # 1990 — Itália
    (1990, "Itália",       "Salvatore Schillaci", "Itália",       6, 7),
    (1990, "Itália",       "Tomáš Skuhravý",      "Tchecoslováquia",5, 5),
    (1990, "Itália",       "Michel",              "Espanha",      4, 5),
    (1990, "Itália",       "Jürgen Klinsmann",    "Alemanha",     3, 7),
    (1990, "Itália",       "Gary Lineker",        "Inglaterra",   4, 7),
    # 1994 — EUA
    (1994, "EUA",          "Hristo Stoichkov",    "Bulgária",     6, 6),
    (1994, "EUA",          "Oleg Salenko",        "Rússia",       6, 3),
    (1994, "EUA",          "Jürgen Klinsmann",    "Alemanha",     5, 7),
    (1994, "EUA",          "Gabriel Batistuta",   "Argentina",    4, 4),
    (1994, "EUA",          "Romário",             "Brasil",       5, 7),
    # 1998 — França
    (1998, "França",       "Davor Šuker",         "Croácia",      6, 7),
    (1998, "França",       "Christian Vieri",     "Itália",       5, 5),
    (1998, "França",       "Marcelo Salas",       "Chile",        4, 4),
    (1998, "França",       "Gabriel Batistuta",   "Argentina",    5, 5),
    (1998, "França",       "Ronaldo",             "Brasil",       4, 7),
    (1998, "França",       "Jürgen Klinsmann",    "Alemanha",     3, 5),
    # 2002 — Coreia/Japão
    (2002, "Coreia/Japão", "Ronaldo",             "Brasil",       8, 7),
    (2002, "Coreia/Japão", "Rivaldo",             "Brasil",       5, 7),
    (2002, "Coreia/Japão", "Miroslav Klose",      "Alemanha",     5, 7),
    (2002, "Coreia/Japão", "Jon Dahl Tomasson",   "Dinamarca",    4, 4),
    (2002, "Coreia/Japão", "Gabriel Batistuta",   "Argentina",    1, 3),
    (2002, "Coreia/Japão", "Cristiano Ronaldo",   "Portugal",     0, 3),  # estreou, não marcou
    # 2006 — Alemanha
    (2006, "Alemanha",     "Miroslav Klose",      "Alemanha",     5, 7),
    (2006, "Alemanha",     "Hernán Crespo",       "Argentina",    3, 4),
    (2006, "Alemanha",     "Thierry Henry",       "França",       3, 6),
    (2006, "Alemanha",     "Ronaldo",             "Brasil",       3, 5),
    (2006, "Alemanha",     "Lionel Messi",        "Argentina",    1, 3),
    (2006, "Alemanha",     "Cristiano Ronaldo",   "Portugal",     1, 5),
    # 2010 — África do Sul
    (2010, "África do Sul","Thomas Müller",       "Alemanha",     5, 6),
    (2010, "África do Sul","David Villa",         "Espanha",      5, 7),
    (2010, "África do Sul","Wesley Sneijder",     "Holanda",      5, 7),
    (2010, "África do Sul","Diego Forlán",        "Uruguai",      5, 7),
    (2010, "África do Sul","Miroslav Klose",      "Alemanha",     4, 6),
    (2010, "África do Sul","Cristiano Ronaldo",   "Portugal",     1, 4),
    # 2014 — Brasil
    (2014, "Brasil",       "James Rodríguez",     "Colômbia",     6, 5),
    (2014, "Brasil",       "Thomas Müller",       "Alemanha",     5, 7),
    (2014, "Brasil",       "Neymar",              "Brasil",       4, 5),
    (2014, "Brasil",       "Miroslav Klose",      "Alemanha",     2, 7),
    (2014, "Brasil",       "Lionel Messi",        "Argentina",    4, 7),
    (2014, "Brasil",       "Cristiano Ronaldo",   "Portugal",     1, 3),
    # 2018 — Rússia
    (2018, "Rússia",       "Harry Kane",          "Inglaterra",   6, 6),
    (2018, "Rússia",       "Romelu Lukaku",       "Bélgica",      4, 6),
    (2018, "Rússia",       "Antoine Griezmann",   "França",       3, 7),
    (2018, "Rússia",       "Kylian Mbappé",       "França",       4, 7),
    (2018, "Rússia",       "Denis Cheryshev",     "Rússia",       4, 5),
    (2018, "Rússia",       "Lionel Messi",        "Argentina",    1, 4),
    (2018, "Rússia",       "Cristiano Ronaldo",   "Portugal",     4, 4),
    # 2022 — Catar
    (2022, "Catar",        "Kylian Mbappé",       "França",       8, 7),
    (2022, "Catar",        "Lionel Messi",        "Argentina",    7, 7),
    (2022, "Catar",        "Olivier Giroud",      "França",       4, 7),
    (2022, "Catar",        "Julian Álvarez",      "Argentina",    4, 7),
    (2022, "Catar",        "Cody Gakpo",          "Holanda",      3, 6),
    (2022, "Catar",        "Harry Kane",          "Inglaterra",   3, 5),
    (2022, "Catar",        "Enner Valencia",      "Equador",      3, 3),
    (2022, "Catar",        "Marcus Rashford",     "Inglaterra",   3, 5),
    (2022, "Catar",        "Cristiano Ronaldo",   "Portugal",     1, 5),
]


# ─── Artilheiro por Copa ─────────────────────────────────────────────────────

ARTILHEIRO_COPA = {
    1930: ("Guillermo Stábile", "Argentina", 8),
    1934: ("Oldřich Nejedlý",   "Tchecoslováquia", 5),
    1938: ("Leônidas",           "Brasil", 7),
    1950: ("Ademir",             "Brasil", 8),
    1954: ("Sándor Kocsis",      "Hungria", 11),
    1958: ("Just Fontaine",      "França", 13),
    1962: ("Garrincha / Vavá / Sánchez / Jerković / Albert / Ivanov", "Vários", 4),
    1966: ("Eusébio",            "Portugal", 9),
    1970: ("Gerd Müller",        "Alemanha", 10),
    1974: ("Grzegorz Lato",      "Polônia", 7),
    1978: ("Mario Kempes",       "Argentina", 6),
    1982: ("Paolo Rossi",        "Itália", 6),
    1986: ("Gary Lineker",       "Inglaterra", 6),
    1990: ("Salvatore Schillaci","Itália", 6),
    1994: ("Hristo Stoichkov / Oleg Salenko", "Bulgária/Rússia", 6),
    1998: ("Davor Šuker",        "Croácia", 6),
    2002: ("Ronaldo",            "Brasil", 8),
    2006: ("Miroslav Klose",     "Alemanha", 5),
    2010: ("Thomas Müller / Villa / Sneijder / Forlán", "Vários", 5),
    2014: ("James Rodríguez",    "Colômbia", 6),
    2018: ("Harry Kane",         "Inglaterra", 6),
    2022: ("Kylian Mbappé",      "França", 8),
}


# ─── Processamento ───────────────────────────────────────────────────────────

def calcular_carreira(extra_rows=None):
    """Calcula gols de carreira somando histórico + dados extras (ex: 2026)."""
    carreira = defaultdict(lambda: {"selecao": "", "gols": 0, "jogos": 0, "copas": 0})
    todas = list(ARTILHEIROS_POR_COPA) + (extra_rows or [])
    for ano, sede, jogador, selecao, gols, jogos in todas:
        c = carreira[jogador]
        c["selecao"]  = selecao
        c["gols"]    += gols
        c["jogos"]   += jogos
        c["copas"]   += 1
    return sorted(
        [{"jogador": k, **v} for k, v in carreira.items() if v["gols"] > 0],
        key=lambda x: (-x["gols"], -x["jogos"]),
    )


def exportar_copa(extra_rows=None, artilheiro_copa_extra=None):
    arq = PASTA / "fifa_artilheiros_copa.csv"
    campos = ["ano", "sede", "posicao", "jogador", "selecao", "gols", "jogos", "artilheiro_copa"]
    todas = list(ARTILHEIROS_POR_COPA) + (extra_rows or [])
    artilheiros = dict(ARTILHEIRO_COPA)
    if artilheiro_copa_extra:
        artilheiros[2026] = artilheiro_copa_extra

    with open(arq, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        anos = sorted(set(r[0] for r in todas), reverse=True)
        for ano in anos:
            rows = sorted([r for r in todas if r[0] == ano], key=lambda x: -x[4])
            for pos, (a, sede, jogador, selecao, gols, jogos) in enumerate(rows, 1):
                w.writerow({
                    "ano": ano, "sede": sede, "posicao": pos,
                    "jogador": jogador, "selecao": selecao,
                    "gols": gols, "jogos": jogos,
                    "artilheiro_copa": "Sim" if pos == 1 else "Nao",
                })
    print(f"  ✔ {arq.name}")
    return arq


def exportar_carreira(ranking):
    arq = PASTA / "fifa_artilheiros_carreira.csv"
    campos = ["posicao", "jogador", "selecao", "gols_total", "jogos_total", "copas_disputadas"]
    with open(arq, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for pos, r in enumerate(ranking, 1):
            w.writerow({
                "posicao": pos, "jogador": r["jogador"], "selecao": r["selecao"],
                "gols_total": r["gols"], "jogos_total": r["jogos"],
                "copas_disputadas": r["copas"],
            })
    print(f"  ✔ {arq.name}")


def exibir_terminal(ranking, artilheiros_copa, rows_2026, artilheiro_copa_extra):
    SEP = "=" * 70
    tem_2026 = bool(rows_2026)
    label = "1930–2026 (em andamento)" if tem_2026 else "1930–2022"

    print(f"\n{SEP}")
    print(f" TOP-20 ARTILHEIROS ALL-TIME — Copas do Mundo {label}")
    print(SEP)
    print(f"\n  {'Pos':<4} {'Jogador':<26} {'Seleção':<18} {'Gols':>5} {'Jogos':>6} {'Copas':>6}")
    print("  " + "-" * 64)
    for pos, r in enumerate(ranking[:20], 1):
        print(f"  {pos:<4} {r['jogador']:<26} {r['selecao']:<18} "
              f"{r['gols']:>5} {r['jogos']:>6} {r['copas']:>6}")

    print(f"\n{SEP}")
    print(f" ARTILHEIROS POR COPA (Chuteiras de Ouro / Líderes)")
    print(SEP)
    print(f"\n  {'Ano':<6} {'Sede':<22} {'Artilheiro':<28} {'Seleção':<15} {'Gols':>5}")
    print("  " + "-" * 79)

    copa_completa = dict(artilheiros_copa)
    if artilheiro_copa_extra:
        copa_completa[2026] = artilheiro_copa_extra

    todas = list(ARTILHEIROS_POR_COPA) + (rows_2026 or [])
    for ano in sorted(copa_completa, reverse=True):
        jogador, selecao, gols = copa_completa[ano]
        sede = next((r[1] for r in todas if r[0] == ano), "")
        em_andamento = " ★" if ano == 2026 else ""
        print(f"  {ano:<6} {sede:<22} {jogador:<28} {selecao:<15} {gols:>5}{em_andamento}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print(" ARTILHEIROS HISTÓRICOS — Copas do Mundo 1930–2026")
    print("=" * 70)

    print("\n Buscando dados de 2026 na API FIFA...", flush=True)
    rows_2026, artilheiro_copa_2026, sede_2026 = buscar_2026()
    if rows_2026:
        lider = artilheiro_copa_2026
        print(f"  ✔ {len(rows_2026)} jogadores com gol em 2026 | "
              f"Líder atual: {lider[0]} ({lider[1]}) — {lider[2]} gols")
    else:
        print("  ⚠ Sem dados de 2026 (API indisponível ou sem gols registrados)")

    ranking = calcular_carreira(extra_rows=rows_2026)

    print("\n Gerando arquivos CSV...")
    exportar_copa(extra_rows=rows_2026, artilheiro_copa_extra=artilheiro_copa_2026)
    exportar_carreira(ranking)
    exibir_terminal(ranking, ARTILHEIRO_COPA, rows_2026, artilheiro_copa_2026)

    copas = 22 + (1 if rows_2026 else 0)
    print(f"\n  Edições cobertas : 1930 a {'2026' if rows_2026 else '2022'} ({copas} Copas)")
    print(f"  Jogadores únicos : {len(ranking)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
