#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 PALPITE DOS JOGOS DE HOJE - Copa 2026
=============================================================================
Le o fifa_jogos_completo.json (gerado pelo fifa_extrair_jogos.py), encontra os
jogos marcados para HOJE e estima, para cada um, a chance de cada resultado:
vitoria do mandante / empate / vitoria do visitante.

COMO FUNCIONA (mesmo motor do simulador):
  - Mede a forca de ataque/defesa de cada selecao pelos jogos de 2026 ja
    disputados (com regularizacao para nao exagerar quem jogou pouco).
  - Estima quantos gols cada lado tende a marcar no confronto.
  - Usa a distribuicao de Poisson para calcular a probabilidade de cada placar
    e, somando, a chance de vitoria / empate / derrota.

LIMITES (importante):
  - E uma ESTIMATIVA. No comeco do torneio, com poucos jogos, e bem grosseira.
  - Ignora lesoes, suspensoes, contexto e a sorte do jogo.
  - Nao serve para aposta; serve para enxergar quem chega "favorito".

COMO USAR:
  python fifa_jogos_de_hoje.py
  (Tenha o fifa_jogos_completo.json na mesma pasta.)
=============================================================================
"""

import csv
import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

# ---------------- CONFIGURACAO ----------------
ID_TEMPORADA_2026 = "285023"
ARQUIVO_ENTRADA = "fifa_jogos_completo.json"
ARQUIVO_SAIDA   = "fifa_palpite_hoje.csv"
FUSO_HORARIO    = -3        # -3 = Brasilia. Define o que e "hoje" e os horarios.
DATA_ALVO       = ""        # vazio = hoje. Ou force uma data: "2026-06-27"
K_PSEUDO        = 4.0       # regularizacao (puxa times com poucos jogos p/ media)
MAX_GOLS        = 10        # teto de gols considerado no calculo de probabilidade
# -----------------------------------------------


def _num(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def texto_localizado(lista, idioma="pt"):
    if not lista:
        return ""
    if isinstance(lista, str):
        return lista
    for item in lista:
        loc = (item.get("Locale") or "").lower()
        if loc == idioma or loc.startswith(idioma):
            return item.get("Description", "")
    return lista[0].get("Description", "")


_AGORA = datetime.now(timezone.utc).replace(tzinfo=None)


def dt_local(iso):
    """Converte a data UTC do jogo para o fuso configurado (datetime ingenuo)."""
    if not iso:
        return None
    try:
        d = datetime.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S")
        return d + timedelta(hours=FUSO_HORARIO)
    except Exception:
        return None


def ja_disputado(jogo):
    d = dt_local(jogo.get("Date") or jogo.get("LocalDate"))
    agora_local = _AGORA + timedelta(hours=FUSO_HORARIO)
    return bool(d and d < agora_local)


def placares(jogo):
    casa, fora = jogo.get("Home") or {}, jogo.get("Away") or {}
    gc = _num(casa.get("Score"))
    if gc is None:
        gc = _num(jogo.get("HomeTeamScore"))
    gf = _num(fora.get("Score"))
    if gf is None:
        gf = _num(jogo.get("AwayTeamScore"))
    return gc, gf


def carregar_2026(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return [j for j in dados if str(j.get("IdSeason")) == str(ID_TEMPORADA_2026)]


def construir_forcas(jogos):
    gf, ga, n, nomes = {}, {}, {}, {}
    total_gols, total_partidas = 0, 0
    for j in jogos:
        casa, fora = j.get("Home") or {}, j.get("Away") or {}
        ic, if_ = casa.get("IdTeam"), fora.get("IdTeam")
        if not ic or not if_:
            continue
        nomes[ic] = texto_localizado(casa.get("TeamName")) or ic
        nomes[if_] = texto_localizado(fora.get("TeamName")) or if_
        if not ja_disputado(j):
            continue
        gc, gfo = placares(j)
        if gc is None or gfo is None:
            continue
        for t in (ic, if_):
            gf.setdefault(t, 0); ga.setdefault(t, 0); n.setdefault(t, 0)
        gf[ic] += gc; ga[ic] += gfo; n[ic] += 1
        gf[if_] += gfo; ga[if_] += gc; n[if_] += 1
        total_gols += gc + gfo
        total_partidas += 1
    media = (total_gols / (2 * total_partidas)) if total_partidas else 1.3
    ataque, defesa = {}, {}
    for t in nomes:
        nt = n.get(t, 0)
        ataque[t] = ((gf.get(t, 0) + K_PSEUDO * media) / (nt + K_PSEUDO)) / media if media else 1.0
        defesa[t] = ((ga.get(t, 0) + K_PSEUDO * media) / (nt + K_PSEUDO)) / media if media else 1.0
    return ataque, defesa, media, nomes, total_partidas


def poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def probabilidades(casa, fora, ataque, defesa, media):
    """Devolve (p_casa, p_empate, p_fora) e os gols esperados de cada lado."""
    lc = media * ataque.get(casa, 1.0) * defesa.get(fora, 1.0)
    lf = media * ataque.get(fora, 1.0) * defesa.get(casa, 1.0)
    p_casa = p_emp = p_fora = 0.0
    for i in range(MAX_GOLS + 1):
        for j in range(MAX_GOLS + 1):
            p = poisson_pmf(i, lc) * poisson_pmf(j, lf)
            if i > j:
                p_casa += p
            elif i == j:
                p_emp += p
            else:
                p_fora += p
    return p_casa, p_emp, p_fora, lc, lf


def placar_mais_provavel(lc, lf, resultado):
    """Placar exato mais provavel COERENTE com o palpite.
    resultado: 'casa' (mandante vence), 'empate' ou 'fora' (visitante vence)."""
    melhor, melhor_p = None, -1.0
    for i in range(MAX_GOLS + 1):
        pi = poisson_pmf(i, lc)
        for j in range(MAX_GOLS + 1):
            if resultado == "casa" and not i > j:
                continue
            if resultado == "empate" and i != j:
                continue
            if resultado == "fora" and not i < j:
                continue
            p = pi * poisson_pmf(j, lf)
            if p > melhor_p:
                melhor_p, melhor = p, (i, j)
    return melhor if melhor else (0, 0)


def main():
    pasta = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    entrada = os.path.join(pasta, ARQUIVO_ENTRADA)
    saida = os.path.join(pasta, ARQUIVO_SAIDA)

    if not os.path.exists(entrada):
        print(f"Nao encontrei {ARQUIVO_ENTRADA} nesta pasta.")
        print("Rode antes o fifa_extrair_jogos.py.")
        input("\nENTER para fechar...")
        return

    jogos = carregar_2026(entrada)
    if not jogos:
        print("Nenhum jogo de 2026 no arquivo.")
        input("\nENTER para fechar...")
        return

    ataque, defesa, media, nomes, n_disputados = construir_forcas(jogos)

    # define a data alvo ("hoje" no fuso, ou a DATA_ALVO informada)
    if DATA_ALVO.strip():
        alvo = datetime.strptime(DATA_ALVO.strip(), "%Y-%m-%d").date()
    else:
        alvo = (_AGORA + timedelta(hours=FUSO_HORARIO)).date()

    de_hoje = []
    for j in jogos:
        d = dt_local(j.get("Date") or j.get("LocalDate"))
        if d and d.date() == alvo:
            de_hoje.append((d, j))
    de_hoje.sort(key=lambda x: x[0])

    print(f"Base: {n_disputados} jogos de 2026 ja disputados | media gols/time: {media:.2f}")
    print(f"Data alvo: {alvo.strftime('%d/%m/%Y')} | jogos encontrados: {len(de_hoje)}\n")

    if not de_hoje:
        print("Nenhum jogo nessa data. Dica: ajuste DATA_ALVO no topo, ou rode")
        print("o fifa_extrair_jogos.py de novo para atualizar a base.")
        input("\nENTER para fechar...")
        return

    print("ESTIMATIVA estatistica, NAO um resultado garantido.\n")
    linhas = []
    acertos = total_avaliados = 0
    for d, j in de_hoje:
        casa, fora = j.get("Home") or {}, j.get("Away") or {}
        ic, if_ = casa.get("IdTeam"), fora.get("IdTeam")
        nc = texto_localizado(casa.get("TeamName")) or "(a definir)"
        nf = texto_localizado(fora.get("TeamName")) or "(a definir)"

        if not ic or not if_:
            print(f"{d.strftime('%H:%M')}  {nc} x {nf}  -> times ainda nao definidos")
            continue

        pc, pe, pf, lc, lf = probabilidades(ic, if_, ataque, defesa, media)
        # palpite: maior probabilidade
        opcoes = {"casa": (pc, f"vitoria de {nc}"),
                  "empate": (pe, "empate"),
                  "fora": (pf, f"vitoria de {nf}")}
        palpite_cod = max(opcoes, key=lambda k: opcoes[k][0])
        palpite_txt = opcoes[palpite_cod][1]

        # placar exato mais provavel, COERENTE com o palpite (ex.: "2 x 1")
        gi, gj = placar_mais_provavel(lc, lf, palpite_cod)
        placar_previsto = f"{gi} x {gj}"

        # resultado real, se o jogo ja terminou
        gc, gf = placares(j)
        tem_resultado = ja_disputado(j) and gc is not None and gf is not None
        if tem_resultado:
            if gc > gf:
                real_cod, vencedor_real = "casa", nc
            elif gf > gc:
                real_cod, vencedor_real = "fora", nf
            else:
                real_cod, vencedor_real = "empate", "Empate"
            placar_real = f"{gc} x {gf}"
            acertou = "Sim" if real_cod == palpite_cod else "Nao"
            total_avaliados += 1
            acertos += 1 if acertou == "Sim" else 0
        else:
            placar_real, vencedor_real, acertou = "", "", "-"

        print(f"{d.strftime('%H:%M')}  {nc} x {nf}")
        print(f"     {nc}: {pc*100:4.1f}%   empate: {pe*100:4.1f}%   {nf}: {pf*100:4.1f}%")
        print(f"     palpite: {palpite_txt}   |   placar previsto: {placar_previsto}")
        if tem_resultado:
            marca = "OK" if acertou == "Sim" else "X "
            print(f"     RESULTADO REAL: {placar_real}  ({vencedor_real})   "
                  f"[{marca} palpite {'certo' if acertou=='Sim' else 'errado'}]")
        else:
            print("     (ainda nao disputado - placar acima e previsao)")
        print()

        linhas.append({
            "hora": d.strftime("%H:%M"),
            "mandante": nc, "visitante": nf,
            "chance_mandante_%": round(pc * 100, 1),
            "chance_empate_%": round(pe * 100, 1),
            "chance_visitante_%": round(pf * 100, 1),
            "placar_previsto": placar_previsto,
            "gols_esperados_mandante": round(lc, 2),
            "gols_esperados_visitante": round(lf, 2),
            "palpite": palpite_txt,
            "placar_real": placar_real,
            "vencedor_real": vencedor_real,
            "palpite_acertou": acertou,
        })

    if total_avaliados:
        print(f"Palpites avaliados hoje: {acertos}/{total_avaliados} certos "
              f"({100*acertos/total_avaliados:.0f}%).\n")

    if linhas:
        with open(saida, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
            w.writeheader(); w.writerows(linhas)
        print(f"Planilha salva em: {saida}")
    input("\nENTER para fechar...")


if __name__ == "__main__":
    main()