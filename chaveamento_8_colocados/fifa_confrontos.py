#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 CONFRONTOS DO MATA-MATA - Copa do Mundo 2026
=============================================================================
Le o fifa_jogos.csv, calcula a classificacao de cada grupo, simula os jogos
pendentes via modelo de Poisson e exibe/exporta:
  - Classificacao dos grupos
  - Top-8 terceiros colocados
  - Confrontos dos 16 avos de final
  - Ranking dos 12 terceiros colocados (top-8 avancam)

Arquivos gerados:
  - fifa_classificacao_grupos.csv
  - fifa_terceiros_colocados.csv
  - fifa_chaveamento_16avos.csv
=============================================================================
"""

import csv
import math
from datetime import datetime
from collections import defaultdict
from pathlib import Path

ARQUIVO         = Path(__file__).parent / "fifa_jogos.csv"
CUTOFF_GRUPOS   = datetime(2026, 6, 28)
K_PSEUDO        = 4.0
MAX_GOLS        = 10

# ─── Leitura ─────────────────────────────────────────────────────────────────

def ler_jogos():
    grupo_ok, elim, pendentes = [], [], []
    with open(ARQUIVO, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if "2026" not in r.get("edicao", ""):
                continue
            try:
                dt = datetime.strptime(r["data"].strip(), "%d/%m/%Y %H:%M")
            except ValueError:
                continue
            casa = r["time_casa"].strip()
            fora = r["time_fora"].strip()
            gc   = r["gols_casa"].strip()
            gf   = r["gols_fora"].strip()
            r["_dt"] = dt
            if not casa or not fora:
                continue
            if dt >= CUTOFF_GRUPOS:
                elim.append(r)
            elif gc != "" and gf != "":
                grupo_ok.append(r)
            else:
                pendentes.append(r)
    return grupo_ok, elim, pendentes


# ─── Grupos ──────────────────────────────────────────────────────────────────

def identificar_grupos(jogos):
    viz = defaultdict(set)
    for r in jogos:
        viz[r["time_casa"].strip()].add(r["time_fora"].strip())
        viz[r["time_fora"].strip()].add(r["time_casa"].strip())
    visited, grupos = set(), []
    for t in sorted(viz):
        if t not in visited:
            grupo, fila = set(), [t]
            while fila:
                x = fila.pop()
                if x not in visited:
                    visited.add(x); grupo.add(x)
                    fila.extend(viz[x] - visited)
            grupos.append(sorted(grupo))
    grupos.sort()
    return {chr(65 + i): g for i, g in enumerate(grupos)}


# ─── Estatísticas ────────────────────────────────────────────────────────────

def _stats_vazias():
    return {"pts": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0}

def aplicar_jogo(stats, casa, fora, gc, gf):
    for t in (casa, fora):
        stats.setdefault(t, _stats_vazias())["j"] += 1
    stats[casa]["gp"] += gc; stats[casa]["gc"] += gf
    stats[fora]["gp"] += gf; stats[fora]["gc"] += gc
    if gc > gf:
        stats[casa]["v"] += 1; stats[casa]["pts"] += 3; stats[fora]["d"] += 1
    elif gc < gf:
        stats[fora]["v"] += 1; stats[fora]["pts"] += 3; stats[casa]["d"] += 1
    else:
        stats[casa]["e"] += 1; stats[casa]["pts"] += 1
        stats[fora]["e"] += 1; stats[fora]["pts"] += 1

def calcular_stats(jogos, times):
    stats = {t: _stats_vazias() for grupo in times.values() for t in grupo}
    for r in jogos:
        aplicar_jogo(stats, r["time_casa"].strip(), r["time_fora"].strip(),
                     int(r["gols_casa"]), int(r["gols_fora"]))
    return stats


# ─── Modelo Poisson ──────────────────────────────────────────────────────────

def _poisson_prob(lam, k):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def forca_times(stats):
    total_gp = sum(s["gp"] for s in stats.values())
    total_j  = sum(s["j"]  for s in stats.values())
    media    = total_gp / total_j if total_j else 1.0
    ataque, defesa = {}, {}
    for t, s in stats.items():
        j = s["j"]
        ataque[t] = (s["gp"] + K_PSEUDO * media) / (j + K_PSEUDO)
        defesa[t] = (s["gc"] + K_PSEUDO * media) / (j + K_PSEUDO)
    return ataque, defesa, media

def simular_jogo(casa, fora, ataque, defesa, media):
    lam_c = ataque[casa] * defesa[fora] / media if media else 1.0
    lam_f = ataque[fora] * defesa[casa] / media if media else 1.0
    prob_v = prob_e = prob_d = 0.0
    melhor, melhor_p = (0, 0), -1
    for gc in range(MAX_GOLS + 1):
        pc = _poisson_prob(lam_c, gc)
        for gf in range(MAX_GOLS + 1):
            pf = _poisson_prob(lam_f, gf)
            p  = pc * pf
            if gc > gf:   prob_v += p
            elif gc == gf: prob_e += p
            else:          prob_d += p
            if p > melhor_p:
                melhor_p, melhor = p, (gc, gf)
    return melhor, prob_v, prob_e, prob_d


# ─── Classificação ───────────────────────────────────────────────────────────

def rank_grupo(times, stats):
    return sorted(
        times,
        key=lambda t: (
            -stats[t]["pts"],
            -(stats[t]["gp"] - stats[t]["gc"]),
            -stats[t]["gp"],
        ),
    )


# ─── Top-8 terceiros colocados ───────────────────────────────────────────────

def top8_terceiros(grupos, stats):
    terceiros = []
    for letra, times in grupos.items():
        t = rank_grupo(times, stats)[2]
        s = stats[t]
        terceiros.append({
            "time": t, "grupo": letra,
            "pts": s["pts"], "sg": s["gp"] - s["gc"], "gp": s["gp"],
            "j": s["j"], "v": s["v"], "e": s["e"], "d": s["d"], "gc": s["gc"],
        })
    terceiros.sort(key=lambda x: (-x["pts"], -x["sg"], -x["gp"]))
    return terceiros


# ─── Exibição ────────────────────────────────────────────────────────────────

SEP = "=" * 72

def exibir_grupos(grupos, stats):
    print(SEP)
    print(" CLASSIFICAÇÃO DOS GRUPOS — Copa do Mundo 2026")
    print(SEP)
    for letra in sorted(grupos):
        times   = grupos[letra]
        ranking = rank_grupo(times, stats)
        print(f"\n▶ GRUPO {letra}")
        print(f"  {'':3} {'Seleção':<25} {'J':>2} {'V':>2} {'E':>2} {'D':>2} {'GP':>3} {'GC':>3} {'SG':>4} {'Pts':>4}")
        print("  " + "-" * 60)
        for pos, t in enumerate(ranking, 1):
            s   = stats[t]
            sg  = s["gp"] - s["gc"]
            ico = "✔" if pos <= 2 else " "
            print(f"  {ico}{pos:<2} {t:<25} {s['j']:>2} {s['v']:>2} {s['e']:>2} {s['d']:>2} "
                  f"{s['gp']:>3} {s['gc']:>3} {sg:>+4} {s['pts']:>4}")


def exibir_simulados(simulados):
    if not simulados:
        return
    print(f"\n{SEP}")
    print(" SIMULAÇÃO DOS JOGOS PENDENTES (modelo Poisson)")
    print(SEP)
    print(f"\n  {'Data':<18} {'Casa':<22} {'Placar':<9} {'Fora':<22} {'%V':>5} {'%E':>5} {'%D':>5}")
    print("  " + "-" * 72)
    for s in simulados:
        gc, gf = s["placar"]
        print(f"  {s['data']:<18} {s['casa']:<22} {gc}-{gf}       {s['fora']:<22} "
              f"{s['pv']:>4.0%} {s['pe']:>4.0%} {s['pd']:>4.0%}")


def exibir_top8(terceiros):
    print(f"\n{SEP}")
    print(" TERCEIROS COLOCADOS — As 12 seleções (✔ top-8 avançam para os 16 avos)")
    print(SEP)
    print(f"\n  {'':3} {'Seleção':<25} {'Grp':>4} {'J':>2} {'V':>2} {'E':>2} {'D':>2} {'GP':>3} {'GC':>3} {'SG':>4} {'Pts':>4}")
    print("  " + "-" * 66)
    for pos, t in enumerate(terceiros, 1):
        ico = "✔" if pos <= 8 else " "
        sg  = t["gp"] - t["gc"]
        print(f"  {ico}{pos:<2} {t['time']:<25} {t['grupo']:>4} {t['j']:>2} {t['v']:>2} "
              f"{t['e']:>2} {t['d']:>2} {t['gp']:>3} {t['gc']:>3} {sg:>+4} {t['pts']:>4}")
    print(f"\n  ✔ = classifica para os 16 avos  |  Os 8 melhores pontuados avançam")


def exibir_top8_geral(grupos, stats):
    pos_map = {}
    for letra, times in grupos.items():
        for pos, t in enumerate(rank_grupo(times, stats), 1):
            pos_map[t] = (letra, pos)

    todos = sorted(
        stats.items(),
        key=lambda x: (-x[1]["pts"], -(x[1]["gp"] - x[1]["gc"]), -x[1]["gp"]),
    )

    print(f"\n{SEP}")
    print(" TOP-8 MELHORES TIMES DA FASE DE GRUPOS")
    print(SEP)
    print(f"\n  {'':3} {'Seleção':<25} {'Grp':>5} {'J':>2} {'V':>2} {'E':>2} {'D':>2} {'GP':>3} {'GC':>3} {'SG':>4} {'Pts':>4}")
    print("  " + "-" * 68)
    for rank, (t, s) in enumerate(todos[:8], 1):
        sg  = s["gp"] - s["gc"]
        grp, pos = pos_map.get(t, ("?", "?"))
        print(f"  {rank:<3} {t:<25} {pos}º {grp:>2} {s['j']:>2} {s['v']:>2} {s['e']:>2} {s['d']:>2} "
              f"{s['gp']:>3} {s['gc']:>3} {sg:>+4} {s['pts']:>4}")


def exibir_chaveamento(elim_jogos, grupos, stats):
    print(f"\n{SEP}")
    print(" CHAVEAMENTO — 16 AVOS DE FINAL")
    print(SEP)

    pos_map = {}
    for letra, times in grupos.items():
        for pos, t in enumerate(rank_grupo(times, stats), 1):
            pos_map[t] = (letra, pos)

    definidos = [(r, r["time_casa"].strip(), r["time_fora"].strip())
                 for r in sorted(elim_jogos, key=lambda x: x["_dt"])
                 if r["time_casa"].strip() and r["time_fora"].strip()]

    pendentes = [r for r in sorted(elim_jogos, key=lambda x: x["_dt"])
                 if not r["time_casa"].strip() or not r["time_fora"].strip()]

    print(f"\n  {'#':<3} {'Data':<18} {'Time 1':<25} {'':4} {'Time 2':<25} {'Origem'}")
    print("  " + "-" * 82)
    for i, (r, casa, fora) in enumerate(definidos, 1):
        def info(t):
            if t in pos_map:
                p, l = pos_map[t][1], pos_map[t][0]
                return f"{p}º Grp {l}"
            return "3º lugar"
        print(f"  {i:<3} {r['data'].strip():<18} {casa:<25} {'vs':>4} {fora:<25} "
              f"{info(casa)} × {info(fora)}")

    if pendentes:
        print(f"\n  ⏳ {len(pendentes)} jogo(s) ainda a definir (aguardando resultados de hoje):")
        for r in pendentes:
            print(f"     {r['data'].strip():<18} — {r['estadio'].strip()}")

    return len(definidos)


# ─── Exportação CSV ──────────────────────────────────────────────────────────

PASTA = Path(__file__).parent

def exportar_classificacao(grupos, stats):
    arquivo = PASTA / "fifa_classificacao_grupos.csv"
    campos  = ["grupo", "posicao", "selecao", "jogos", "vitorias", "empates",
               "derrotas", "gols_pro", "gols_contra", "saldo_gols", "pontos", "classifica"]
    with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for letra in sorted(grupos):
            ranking = rank_grupo(grupos[letra], stats)
            for pos, t in enumerate(ranking, 1):
                s  = stats[t]
                sg = s["gp"] - s["gc"]
                w.writerow({
                    "grupo": letra, "posicao": pos, "selecao": t,
                    "jogos": s["j"], "vitorias": s["v"], "empates": s["e"],
                    "derrotas": s["d"], "gols_pro": s["gp"], "gols_contra": s["gc"],
                    "saldo_gols": sg, "pontos": s["pts"],
                    "classifica": "Sim" if pos <= 2 else "Nao",
                })
    print(f"  ✔ {arquivo.name}")


def exportar_top8_terceiros(terceiros):
    arquivo = PASTA / "fifa_terceiros_colocados.csv"
    campos  = ["posicao", "selecao", "grupo", "jogos", "vitorias", "empates",
               "derrotas", "gols_pro", "gols_contra", "saldo_gols", "pontos", "classifica"]
    with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for pos, t in enumerate(terceiros, 1):
            w.writerow({
                "posicao": pos, "selecao": t["time"], "grupo": t["grupo"],
                "jogos": t["j"], "vitorias": t["v"], "empates": t["e"],
                "derrotas": t["d"], "gols_pro": t["gp"], "gols_contra": t["gc"],
                "saldo_gols": t["sg"], "pontos": t["pts"],
                "classifica": "Sim" if pos <= 8 else "Nao",
            })
    print(f"  ✔ {arquivo.name}")


def exportar_chaveamento(elim_jogos, grupos, stats):
    arquivo = PASTA / "fifa_chaveamento_16avos.csv"
    campos  = ["jogo", "data", "time_1", "origem_time_1", "time_2", "origem_time_2",
               "estadio", "cidade", "status"]
    pos_map = {}
    for letra, times in grupos.items():
        for pos, t in enumerate(rank_grupo(times, stats), 1):
            pos_map[t] = (letra, pos)

    def origem(t):
        if t in pos_map:
            return f"{pos_map[t][1]}º Grupo {pos_map[t][0]}"
        return "3º lugar"

    ordenados = sorted(elim_jogos, key=lambda x: x["_dt"])
    with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for i, r in enumerate(ordenados, 1):
            casa = r["time_casa"].strip()
            fora = r["time_fora"].strip()
            definido = bool(casa and fora)
            w.writerow({
                "jogo": i,
                "data": r["data"].strip(),
                "time_1": casa if casa else "A definir",
                "origem_time_1": origem(casa) if casa else "",
                "time_2": fora if fora else "A definir",
                "origem_time_2": origem(fora) if fora else "",
                "estadio": r["estadio"].strip(),
                "cidade": r["cidade"].strip(),
                "status": "Definido" if definido else "Pendente",
            })
    print(f"  ✔ {arquivo.name}")


def exportar_tudo(grupos, stats, terceiros, elim_jogos):
    print(f"\n{SEP}")
    print(" ARQUIVOS CSV GERADOS")
    print(SEP)
    exportar_classificacao(grupos, stats)
    exportar_top8_terceiros(terceiros)
    exportar_chaveamento(elim_jogos, grupos, stats)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    grupo_ok, elim, pendentes = ler_jogos()
    grupos  = identificar_grupos(grupo_ok)
    stats   = calcular_stats(grupo_ok, grupos)  # apenas jogos reais

    # Simulação só para previsão — não altera stats reais
    ataque, defesa, media = forca_times(stats)
    simulados = []
    for r in sorted(pendentes, key=lambda x: x["_dt"]):
        casa = r["time_casa"].strip()
        fora = r["time_fora"].strip()
        placar, pv, pe, pd = simular_jogo(casa, fora, ataque, defesa, media)
        simulados.append({
            "data": r["data"].strip(), "casa": casa, "fora": fora,
            "placar": placar, "pv": pv, "pe": pe, "pd": pd,
        })

    terceiros = top8_terceiros(grupos, stats)  # baseado só em resultados reais

    exibir_grupos(grupos, stats)
    exibir_simulados(simulados)
    exibir_top8_geral(grupos, stats)
    exibir_top8(terceiros)
    n = exibir_chaveamento(elim, grupos, stats)
    exportar_tudo(grupos, stats, terceiros, elim)

    print(f"\n{SEP}")
    print(f"  Jogos computados (fase de grupos) : {len(grupo_ok)}")
    print(f"  Jogos simulados (pendentes hoje)  : {len(simulados)}")
    print(f"  Confrontos dos 16 avos definidos  : {n}")
    print(SEP)


if __name__ == "__main__":
    main()
