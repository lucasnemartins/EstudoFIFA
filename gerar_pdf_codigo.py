#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

ARQUIVO_SAIDA = "/Users/lucasmartins/Documents/FIFA/FIFA_2026_Estudo_do_Codigo.pdf"

# ── Cores ──────────────────────────────────────────────────────────────────
AZUL       = colors.HexColor("#003f7f")
AZUL_MED   = colors.HexColor("#0066cc")
AZUL_CLARO = colors.HexColor("#e8f0fe")
VERDE      = colors.HexColor("#1a5c38")
VERDE_BG   = colors.HexColor("#e8f5ee")
LARANJA    = colors.HexColor("#b84c00")
LARANJA_BG = colors.HexColor("#fff3e0")
ROXO       = colors.HexColor("#5b2c8d")
ROXO_BG    = colors.HexColor("#f3eeff")
CINZA_BG   = colors.HexColor("#f5f5f5")
CINZA_LIN  = colors.HexColor("#dddddd")
BRANCO     = colors.white

estilos = getSampleStyleSheet()

# Estilos de texto
titulo_capa = ParagraphStyle("titulo_capa", parent=estilos["Normal"],
    fontSize=24, textColor=BRANCO, alignment=TA_CENTER,
    fontName="Helvetica-Bold", spaceAfter=8)

sub_capa = ParagraphStyle("sub_capa", parent=estilos["Normal"],
    fontSize=12, textColor=colors.HexColor("#c0d8f5"),
    alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4)

h1 = ParagraphStyle("h1", parent=estilos["Normal"],
    fontSize=15, textColor=AZUL, fontName="Helvetica-Bold",
    spaceBefore=16, spaceAfter=6)

h2 = ParagraphStyle("h2", parent=estilos["Normal"],
    fontSize=12, textColor=AZUL_MED, fontName="Helvetica-Bold",
    spaceBefore=10, spaceAfter=4)

h3 = ParagraphStyle("h3", parent=estilos["Normal"],
    fontSize=10.5, textColor=VERDE, fontName="Helvetica-Bold",
    spaceBefore=8, spaceAfter=3)

corpo = ParagraphStyle("corpo", parent=estilos["Normal"],
    fontSize=9.5, textColor=colors.HexColor("#1a1a1a"),
    fontName="Helvetica", spaceAfter=5, leading=14,
    alignment=TA_JUSTIFY)

# Bloco de código normal
cod_est = ParagraphStyle("cod_est", parent=estilos["Normal"],
    fontSize=8, textColor=colors.HexColor("#1a1a2e"),
    fontName="Courier", spaceAfter=1, leading=12,
    leftIndent=10)

# Linha de código com destaque (comentário)
com_est = ParagraphStyle("com_est", parent=estilos["Normal"],
    fontSize=8, textColor=colors.HexColor("#2e7d32"),
    fontName="Courier-Oblique", spaceAfter=1, leading=12,
    leftIndent=10)

aviso_est = ParagraphStyle("aviso_est", parent=estilos["Normal"],
    fontSize=9, textColor=colors.HexColor("#5a3000"),
    fontName="Helvetica", spaceAfter=4, leading=13,
    backColor=LARANJA_BG, borderPad=6, leftIndent=8)

dica_est = ParagraphStyle("dica_est", parent=estilos["Normal"],
    fontSize=9, textColor=colors.HexColor("#1a3a5c"),
    fontName="Helvetica", spaceAfter=4, leading=13,
    backColor=AZUL_CLARO, borderPad=6, leftIndent=8)

rodape_est = ParagraphStyle("rodape_est", parent=estilos["Normal"],
    fontSize=7.5, textColor=colors.grey, alignment=TA_CENTER)


# ── Helpers ─────────────────────────────────────────────────────────────────

def hr(cor=CINZA_LIN, esp=6):
    return HRFlowable(width="100%", thickness=0.5, color=cor,
                      spaceAfter=esp, spaceBefore=4)

def secao(num, titulo):
    return [Spacer(1, 0.2*cm),
            Paragraph(f"{num}. {titulo}", h1), hr()]

def sub(titulo):
    return [Paragraph(titulo, h2)]

def subsub(titulo):
    return [Paragraph(titulo, h3)]

def p(txt):
    return Paragraph(txt, corpo)

def dica(txt):
    return Paragraph(f"💡 {txt}", dica_est)

def aviso(txt):
    return Paragraph(f"⚠️  {txt}", aviso_est)

def sp(n=0.3):
    return Spacer(1, n*cm)


def bloco_codigo(linhas_raw):
    """
    Recebe string multilinha e renderiza cada linha.
    Linhas que começam com # são destacadas em verde.
    """
    el = []
    caixa = []
    for linha in linhas_raw.strip().split("\n"):
        stripped = linha.strip()
        est = com_est if stripped.startswith("#") else cod_est
        safe = (linha
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace(" ", "&nbsp;"))
        caixa.append(Paragraph(safe, est))

    t = Table([[caixa]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CINZA_BG),
        ("BOX",           (0, 0), (-1, -1), 0.6, colors.HexColor("#aaaaaa")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    el.append(t)
    el.append(sp(0.2))
    return el


def tabela(cab, lin, widths=None):
    dados = [cab] + lin
    t = Table(dados, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  AZUL),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  BRANCO),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0),  8.5),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_BG]),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 1), (-1, -1), 8),
        ("GRID",           (0, 0), (-1, -1), 0.3, CINZA_LIN),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# CAPA
# ══════════════════════════════════════════════════════════════════════════════

def capa():
    el = []
    cab = Table(
        [[Paragraph("⚽  Copa do Mundo FIFA 2026", titulo_capa)],
         [Paragraph("Estudo Detalhado dos Códigos Python", sub_capa)],
         [Paragraph("Explicação linha por linha para iniciantes", sub_capa)]],
        colWidths=[17*cm])
    cab.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    el.append(cab)
    el.append(sp(0.8))

    info = [
        ["Arquivo 1", "fifa_estatisticas_jogos.py"],
        ["Arquivo 2", "fifa_ranking_oficial.py"],
        ["Nível",     "Iniciante a Intermediário"],
        ["Data",      "26 de junho de 2026"],
    ]
    t = Table(info, colWidths=[4*cm, 13*cm])
    t.setStyle(TableStyle([
        ("FONTNAME",       (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",       (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",      (0, 0), (0, -1), AZUL),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRANCO, CINZA_BG]),
        ("GRID",           (0, 0), (-1, -1), 0.3, CINZA_LIN),
        ("TOPPADDING",     (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
    ]))
    el.append(t)
    el.append(sp(0.6))
    el.append(p(
        "Este documento explica em detalhes cada parte dos dois scripts Python "
        "criados para extrair e analisar dados da Copa do Mundo FIFA 2026. "
        "O objetivo é que você entenda <b>o que cada linha faz</b>, <b>por que foi "
        "escrita assim</b> e <b>como reutilizar esses conceitos</b> em outros projetos."
    ))
    el.append(PageBreak())
    return el


# ══════════════════════════════════════════════════════════════════════════════
# ARQUIVO 1 — fifa_estatisticas_jogos.py
# ══════════════════════════════════════════════════════════════════════════════

def arquivo1():
    el = []

    el.append(Paragraph("ARQUIVO 1 — fifa_estatisticas_jogos.py", ParagraphStyle(
        "arq1", parent=estilos["Normal"], fontSize=14, textColor=BRANCO,
        fontName="Helvetica-Bold", alignment=TA_CENTER,
        backColor=VERDE, borderPad=10, spaceAfter=10)))
    el.append(p(
        "Este script baixa os eventos de cada jogo disputado (gols, faltas, "
        "chutes...) do endpoint <b>/timelines</b> da API da FIFA e gera 4 planilhas: "
        "artilharia, faltas, chutes e destaque por jogo."
    ))
    el.append(sp())

    # ── Bloco 1: Cabeçalho ──────────────────────────────────────────────────
    el += secao("1", "Cabeçalho e importações")
    el.append(p(
        "Todo script Python começa com as importações — dizemos ao Python "
        "quais ferramentas vamos usar. Cada <b>import</b> carrega uma biblioteca "
        "(conjunto de funções prontas)."
    ))
    el += bloco_codigo("""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ↑ Essas duas linhas dizem:
#   1. Use o Python 3 para rodar este arquivo
#   2. O arquivo usa caracteres UTF-8 (acentos, ç, ã...)

import csv          # lê e escreve arquivos .csv (planilhas)
import json         # lê e escreve arquivos .json (dados brutos)
import os           # acessa o sistema de arquivos (pastas, caminhos)
import re           # expressões regulares (extração de texto)
import time         # funções de tempo (ex: pausar o script)
from collections import defaultdict   # dicionário com valor padrão automático
from datetime import datetime, timezone  # manipulação de datas e horários
""")
    el.append(dica(
        "Bibliotecas como csv, json, os, re, time, collections e datetime "
        "já vêm instaladas com o Python. Só o 'requests' precisa ser instalado "
        "manualmente com: pip install requests"
    ))

    # ── Bloco 2: Configurações ──────────────────────────────────────────────
    el += secao("2", "Bloco de Configuração")
    el.append(p(
        "Agrupamos todas as configurações no topo do arquivo. Assim, se precisar "
        "mudar algo (ex: o número de jogadores no ranking), você altera aqui "
        "sem precisar procurar no meio do código."
    ))
    el += bloco_codigo("""
BASE            = "https://api.fifa.com/api/v3"  # URL base da API
ID_TEMPORADA    = "285023"   # ID da Copa 2026 na base da FIFA
ARQUIVO_ENTRADA = "fifa_jogos_completo.json"  # JSON gerado pelo extrator
PAUSA           = 0.25       # segundos de espera entre requisições
TOP_N           = 30         # quantos jogadores salvar em cada CSV

# Tabela de pontos — define o peso de cada tipo de evento no score
PONTOS = {
    0:  +4,    # Gol (Type 0 na API)
    41: +4,    # Gol de pênalti (Type 41)
    34: +3,    # Gol contra (Type 34) — peso menor
    1:  +2,    # Assistência (Type 1)
    12: +1,    # Chute a gol (Type 12)
    57: +1,    # Gol evitado / defesa (Type 57)
    18: -0.5,  # Falta cometida (Type 18)
    2:  -1,    # Cartão amarelo (Type 2)
    3:  -3,    # Cartão vermelho (Type 3)
}
""")
    el.append(dica(
        "Usar um dicionário para os pontos (em vez de vários if/elif) "
        "é mais limpo e fácil de ajustar. Para mudar o peso de um gol "
        "de 4 para 5, basta editar a linha '0: +4'."
    ))

    # ── Bloco 3: Sessão HTTP ────────────────────────────────────────────────
    el += secao("3", "Configuração da Sessão HTTP")
    el.append(p(
        "Criamos uma <b>sessão</b> para todas as requisições. Uma sessão é como "
        "abrir o navegador uma vez e manter as configurações para todos os sites "
        "que você visita — mais eficiente do que configurar cada requisição "
        "separadamente."
    ))
    el += bloco_codigo("""
SESSAO = requests.Session()
# Session() mantém cookies e headers entre requisições — mais eficiente
# do que usar requests.get() direto em cada chamada.

SESSAO.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    # ↑ Faz o servidor pensar que somos o navegador Chrome no Windows.
    #   Sem isso, a API pode rejeitar a requisição.

    "Accept": "application/json, text/plain, */*",
    # ↑ Avisamos que aceitamos resposta em JSON.

    "Origin":  "https://inside.fifa.com",
    "Referer": "https://inside.fifa.com/",
    # ↑ Fingimos que a requisição veio do site oficial da FIFA.
    #   É o mesmo que o navegador faz automaticamente.
})
""")

    # ── Bloco 4: Função texto() ─────────────────────────────────────────────
    el += secao("4", "Função: texto()")
    el.append(p(
        "A FIFA entrega nomes de times, estádios e eventos em múltiplos idiomas "
        "dentro de uma lista. Esta função escolhe o idioma desejado."
    ))
    el += bloco_codigo("""
def texto(lista, idioma="pt"):
    # Exemplo do que a API retorna:
    # [ {"Locale": "pt-BR", "Description": "França"},
    #   {"Locale": "en-GB", "Description": "France"} ]

    if not lista:
        return ""   # lista vazia → devolve string vazia

    if isinstance(lista, str):
        return lista  # já é texto puro → devolve direto

    for item in lista:
        loc = (item.get("Locale") or "").lower()
        # .lower() transforma "PT-BR" em "pt-br" para comparar sem maiúsculas

        if loc == idioma or loc.startswith(idioma):
            # "pt-br".startswith("pt") → True
            return item.get("Description", "")

    # Se não encontrou o idioma, usa o primeiro da lista (fallback)
    return lista[0].get("Description", "")
""")
    el.append(dica(
        "O padrão 'or \"\"' e 'or {}' aparece muito no código. "
        "Significa: 'se o valor for None ou vazio, use este valor padrão'. "
        "Evita erros quando a API não retorna um campo esperado."
    ))

    el.append(PageBreak())

    # ── Bloco 5: Função nome_jogador() ─────────────────────────────────────
    el += secao("5", "Função: nome_jogador() — Regex")
    el.append(p(
        "O nome do jogador vem embutido dentro do texto do EventDescription, "
        "no formato <i>'NOME (Seleção) fez algo'</i>. Usamos uma "
        "<b>expressão regular (regex)</b> para extrair as duas informações."
    ))
    el += bloco_codigo(r"""
def nome_jogador(evento):
    # Pega o texto da descrição do evento (ex: "Julian QUINONES (México) marca o gol!!")
    desc = texto(evento.get("EventDescription"))

    if not desc:
        return "", ""  # evento sem descrição → devolve vazio

    # re.match testa se o texto COMEÇA com o padrão fornecido.
    # Padrão: r"^([^(]+)\(([^)]+)\)"
    #
    #   ^          → início da string
    #   ([^(]+)    → GRUPO 1: qualquer caractere exceto "(" (o nome do jogador)
    #   \(         → um parêntese literal de abertura
    #   ([^)]+)    → GRUPO 2: qualquer caractere exceto ")" (o nome do time)
    #   \)         → um parêntese literal de fechamento
    m = re.match(r"^([^(]+)\(([^)]+)\)", desc.strip())

    if m:
        nome  = m.group(1).strip().title()
        # .strip() remove espaços nas bordas
        # .title() coloca cada palavra com inicial maiúscula
        # "julian quinones" → "Julian Quinones"

        time_nome = m.group(2).strip()
        return nome, time_nome

    return desc[:40], ""  # fallback: usa os primeiros 40 caracteres
""")
    el.append(tabela(
        ["Entrada (desc)", "nome retornado", "time retornado"],
        [
            ["Julian QUINONES (México) marca o gol!!", "Julian Quinones", "México"],
            ["Kylian MBAPPE (França) assistência",     "Kylian Mbappe",  "França"],
            ["VINICIUS JUNIOR (Brasil) falta sofrida", "Vinicius Junior","Brasil"],
        ],
        widths=[8*cm, 5*cm, 4*cm]
    ))

    # ── Bloco 6: Função ja_disputado() ─────────────────────────────────────
    el += secao("6", "Função: ja_disputado()")
    el.append(p(
        "A API retorna tanto jogos passados quanto futuros. Esta função "
        "verifica se a data do jogo já passou comparando com o momento atual."
    ))
    el += bloco_codigo("""
def ja_disputado(jogo):
    # A data do jogo vem assim: "2026-06-11T19:00:00Z"
    # (formato ISO 8601 — padrão internacional)
    iso = jogo.get("Date") or jogo.get("LocalDate")
    # "or" tenta o segundo campo se o primeiro for None/vazio

    if not iso:
        return False  # sem data → assume não disputado

    try:
        # Converte a string de data para um objeto datetime
        # [:19] pega só os primeiros 19 caracteres: "2026-06-11T19:00:00"
        d = datetime.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S")

        # datetime.now(timezone.utc) = momento atual em UTC
        # .replace(tzinfo=None) remove o fuso para comparar sem erro
        agora = datetime.now(timezone.utc).replace(tzinfo=None)

        return d < agora  # True se o jogo já aconteceu

    except Exception:
        return False  # se der qualquer erro na conversão, assume não disputado
""")

    # ── Bloco 7: Função salvar_csv() ────────────────────────────────────────
    el += secao("7", "Função: salvar_csv()")
    el.append(p(
        "Função genérica que salva qualquer lista de dicionários em CSV. "
        "Criamos uma função para isso para não repetir o mesmo código 4 vezes."
    ))
    el += bloco_codigo("""
def salvar_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        # "w"          → abre para escrita (cria ou sobrescreve)
        # newline=""   → necessário no Windows para não duplicar linhas
        # utf-8-sig    → UTF-8 com BOM (evita problema de acentos no Excel)

        w = csv.DictWriter(f, fieldnames=cabecalho)
        # DictWriter escreve dicionários como linhas de CSV
        # fieldnames define a ordem das colunas

        w.writeheader()    # escreve a linha de cabeçalho (nomes das colunas)
        w.writerows(linhas)  # escreve todas as linhas de dados de uma vez

    print(f"  Salvo: {caminho}")
""")
    el.append(dica(
        "A diferença entre csv.writer e csv.DictWriter: "
        "writer recebe listas ['valor1','valor2'], "
        "DictWriter recebe dicionários {'coluna': 'valor'}. "
        "DictWriter é mais seguro porque usa os nomes das colunas."
    ))

    el.append(PageBreak())

    # ── Bloco 8: Função main() parte 1 ─────────────────────────────────────
    el += secao("8", "Função main() — Carregando os dados")
    el.append(p(
        "A função <b>main()</b> é o coração do script. Ela chama todas as outras "
        "funções na ordem certa. Vamos estudá-la em partes."
    ))
    el += bloco_codigo("""
def main():
    # os.path.dirname(__file__) → pasta onde este script está salvo
    # os.path.abspath() → converte para caminho absoluto (ex: /Users/lucas/...)
    pasta = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()

    entrada = os.path.join(pasta, ARQUIVO_ENTRADA)
    # os.path.join une pasta + nome do arquivo de forma correta
    # (no Windows usa \\ , no Mac/Linux usa /)

    # Verifica se o arquivo JSON existe antes de tentar abrir
    if not os.path.exists(entrada):
        print(f"Arquivo não encontrado: {entrada}")
        return  # para a execução aqui

    # Abre e lê o JSON
    with open(entrada, encoding="utf-8") as f:
        dados = json.load(f)
    # json.load() lê o arquivo e converte para lista/dicionário Python
    # O "with" garante que o arquivo é fechado mesmo se der erro

    # Filtra só os jogos da Copa 2026
    jogos_2026 = [j for j in dados if str(j.get("IdSeason")) == ID_TEMPORADA]
    # List comprehension: cria nova lista só com itens que passam na condição
    # str() converte para string porque o ID pode vir como número ou texto

    # Filtra só os já disputados
    disputados = [j for j in jogos_2026 if ja_disputado(j)]
    print(f"{len(disputados)} jogos disputados encontrados.")
""")

    # ── Bloco 9: Acumuladores ───────────────────────────────────────────────
    el += secao("9", "Função main() — Acumuladores com defaultdict")
    el += bloco_codigo("""
    # defaultdict(lambda: {...}) cria um dicionário onde cada nova chave
    # recebe automaticamente o valor padrão definido pelo lambda.
    #
    # Sem defaultdict, precisaríamos verificar:
    #   if nome not in artilharia:
    #       artilharia[nome] = {"gols": 0, "time": ""}
    #   artilharia[nome]["gols"] += 1
    #
    # Com defaultdict, simplesmente:
    #   artilharia[nome]["gols"] += 1  ← funciona direto!

    artilharia  = defaultdict(lambda: {"gols": 0, "time": ""})
    faltas_rank = defaultdict(lambda: {"faltas": 0, "time": ""})
    chutes_rank = defaultdict(lambda: {"chutes": 0, "time": ""})
    destaque_jogos = []   # lista simples para guardar o destaque de cada jogo
""")

    # ── Bloco 10: Loop principal ────────────────────────────────────────────
    el += secao("10", "Função main() — Loop pelos jogos")
    el += bloco_codigo("""
    for i, jogo in enumerate(disputados):
        # enumerate() retorna (índice, item) — i vai de 0 até len-1

        # Extrai os 4 IDs necessários para montar a URL do /timelines
        idc  = jogo.get("IdCompetition")  # "17"
        ids  = jogo.get("IdSeason")       # "285023"
        idst = jogo.get("IdStage")        # ex: "289273"
        idm  = jogo.get("IdMatch")        # ex: "400021443"

        # Informações do jogo para o CSV de destaque
        nc = texto(jogo.get("Home", {}).get("TeamName"))  # nome do time casa
        nf = texto(jogo.get("Away", {}).get("TeamName"))  # nome do visitante
        gc = jogo.get("Home", {}).get("Score", "?")       # gols casa
        gf = jogo.get("Away", {}).get("Score", "?")       # gols fora
        data = (jogo.get("Date") or "")[:10]  # só a data: "2026-06-11"

        if not all([idc, ids, idst, idm]):
            continue  # pula jogos com IDs incompletos

        try:
            resp = SESSAO.get(
                f"{BASE}/timelines/{idc}/{ids}/{idst}/{idm}",
                params={"language": "pt"},
                timeout=15,  # desiste se demorar mais de 15 segundos
            )
            if not resp.ok:
                continue  # pula se a API retornou erro

            eventos = resp.json().get("Event", [])
            # .get("Event", []) → se "Event" não existir, retorna lista vazia

        except Exception as e:
            print(f"  Erro no jogo {idm}: {e}")
            continue

        time.sleep(PAUSA)  # pausa entre requisições para não sobrecarregar a API

        if (i + 1) % 16 == 0:   # a cada 16 jogos, mostra progresso
            print(f"  {i + 1}/{len(disputados)} jogos processados...")
""")

    el.append(PageBreak())

    # ── Bloco 11: Processamento dos eventos ─────────────────────────────────
    el += secao("11", "Função main() — Processando os eventos de cada jogo")
    el += bloco_codigo("""
        # Para cada jogo, zeramos o score de todos os jogadores
        score_jogo = defaultdict(lambda: {
            "score": 0, "time": "",
            "gols": 0, "assistencias": 0,
            "chutes": 0, "chances_criadas": 0, "faltas": 0,
        })

        for evento in eventos:
            tipo = evento.get("Type")  # número que identifica o evento
            nome, equipe = nome_jogador(evento)  # extrai nome e time

            if not nome:
                continue  # pula eventos sem jogador identificado

            p = score_jogo[nome]  # atalho para o dicionário deste jogador
            if not p["time"]:
                p["time"] = equipe  # registra o time na primeira aparição

            # ── Gol ou Gol de Pênalti ──────────────────────────────────────
            if tipo in (0, 41):
                artilharia[nome]["gols"] += 1   # acumulador global
                artilharia[nome]["time"]  = equipe
                p["gols"]            += 1        # contador por jogo
                p["chances_criadas"] += 1
                p["score"]           += PONTOS.get(tipo, 0)
                # PONTOS.get(tipo, 0) → busca no dicionário, usa 0 se não achar

            # ── Gol Contra ─────────────────────────────────────────────────
            elif tipo == 34:
                artilharia[nome]["gols"] += 1
                artilharia[nome]["time"]  = equipe
                p["gols"] += 1
                # Não soma chances_criadas nem score extra

            # ── Assistência ────────────────────────────────────────────────
            elif tipo == 1:
                p["assistencias"]    += 1
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[1]   # +2

            # ── Chute a Gol ────────────────────────────────────────────────
            elif tipo == 12:
                chutes_rank[nome]["chutes"] += 1
                chutes_rank[nome]["time"]    = equipe
                p["chutes"]          += 1
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[12]  # +1

            # ── Gol Evitado (defesa do goleiro) ───────────────────────────
            elif tipo == 57:
                p["chances_criadas"] += 1
                p["score"]           += PONTOS[57]  # +1

            # ── Falta Cometida ─────────────────────────────────────────────
            elif tipo == 18:
                faltas_rank[nome]["faltas"] += 1
                faltas_rank[nome]["time"]    = equipe
                p["faltas"] += 1
                p["score"]  += PONTOS[18]   # -0.5

            # ── Cartões ────────────────────────────────────────────────────
            elif tipo in (2, 3):
                p["score"] += PONTOS[tipo]  # amarelo=-1, vermelho=-3
""")

    # ── Bloco 12: Destaque do jogo ──────────────────────────────────────────
    el += secao("12", "Função main() — Encontrando o destaque do jogo")
    el += bloco_codigo("""
        # Após processar todos os eventos do jogo,
        # encontra o jogador com maior score

        if score_jogo:   # se tiver pelo menos um jogador registrado
            dest_nome, dest = max(
                score_jogo.items(),
                key=lambda x: x[1]["score"]
                # max() percorre todos os jogadores e retorna o de maior score
                # x é (nome, dicionário_de_stats)
                # x[1]["score"] acessa o score do dicionário
            )

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
                # round(x, 1) arredonda para 1 casa decimal: 15.5 em vez de 15.499...
            })
""")

    # ── Bloco 13: Salvando CSVs ─────────────────────────────────────────────
    el += secao("13", "Função main() — Ordenando e salvando os CSVs")
    el += bloco_codigo("""
    # Ordena artilharia do maior para o menor número de gols
    art = sorted(artilharia.items(), key=lambda x: -x[1]["gols"])
    # sorted() retorna nova lista ordenada (não altera o original)
    # .items() converte dicionário em lista de (chave, valor)
    # key=lambda x: -x[1]["gols"] → ordena pelo número de gols (negativo = decrescente)

    # Salva o CSV da artilharia
    salvar_csv(
        os.path.join(pasta, "fifa_artilharia.csv"),
        ["pos", "jogador", "time", "gols"],   # colunas
        [
            {"pos": i, "jogador": n, "time": v["time"], "gols": v["gols"]}
            for i, (n, v) in enumerate(art[:TOP_N], 1)
            # enumerate(art[:TOP_N], 1) → (1, item1), (2, item2)...
            # art[:TOP_N] → só os primeiros TOP_N itens
        ],
    )

    # O mesmo padrão se repete para faltas, chutes e destaque
    flt = sorted(faltas_rank.items(), key=lambda x: -x[1]["faltas"])
    cht = sorted(chutes_rank.items(), key=lambda x: -x[1]["chutes"])
    # destaque_jogos já é uma lista, não precisa ordenar para salvar
""")

    return el


# ══════════════════════════════════════════════════════════════════════════════
# ARQUIVO 2 — fifa_ranking_oficial.py
# ══════════════════════════════════════════════════════════════════════════════

def arquivo2():
    el = []

    el.append(PageBreak())

    el.append(Paragraph("ARQUIVO 2 — fifa_ranking_oficial.py", ParagraphStyle(
        "arq2", parent=estilos["Normal"], fontSize=14, textColor=BRANCO,
        fontName="Helvetica-Bold", alignment=TA_CENTER,
        backColor=ROXO, borderPad=10, spaceAfter=10)))
    el.append(p(
        "Este script usa os endpoints <b>/topscorers</b> e <b>/topcards</b> da FIFA — "
        "dados oficiais e agregados. É mais simples que o anterior porque "
        "faz apenas 2 requisições no total (uma para cada endpoint)."
    ))
    el.append(sp())

    # ── Bloco 14: Configuração ──────────────────────────────────────────────
    el += secao("14", "Configuração e pesos da pontuação")
    el += bloco_codigo("""
# Pesos definidos como constantes no topo — fácil de ajustar
PESO_GOL             = 4
PESO_ASSISTENCIA     = 2
PESO_CHUTE_NO_ALVO   = 1
PESO_CARTAO_AMARELO  = -1
PESO_CARTAO_VERMELHO = -3
PESO_FALTA_COMETIDA  = -0.5
# Usar constantes nomeadas é melhor do que escrever "4" direto no código
# porque fica claro o que significa cada número
""")

    # ── Bloco 15: Função buscar() ───────────────────────────────────────────
    el += secao("15", "Função: buscar() — Requisição genérica")
    el.append(p(
        "Esta função centraliza o código de requisição. Em vez de repetir "
        "o mesmo bloco de código para /topscorers e /topcards, chamamos "
        "buscar() duas vezes com endpoints diferentes."
    ))
    el += bloco_codigo("""
def buscar(endpoint, params=None):
    url = f"{BASE}/{endpoint}"
    # f-string monta a URL: "https://api.fifa.com/api/v3/topscorers"

    # Parâmetros padrão que vão em toda requisição
    params_base = {
        "idCompetition": ID_COMPETICAO,  # "17" = Copa do Mundo
        "idSeason":      ID_TEMPORADA,   # "285023" = 2026
        "language":      "pt",           # resposta em português
        "count":         200,            # máximo de resultados
    }

    # Se passamos parâmetros extras, adicionamos ao dicionário base
    if params:
        params_base.update(params)
        # .update() adiciona/sobrescreve chaves no dicionário

    resp = SESSAO.get(url, params=params_base, timeout=30)
    resp.raise_for_status()
    # raise_for_status() lança exceção se status != 200
    # (ex: 404 = não encontrado, 500 = erro no servidor)

    return resp.json().get("Results", [])
    # Retorna só a lista de resultados (o que nos interessa)
""")

    # ── Bloco 16: Função calcular_pontuacao() ───────────────────────────────
    el += secao("16", "Função: calcular_pontuacao()")
    el.append(p(
        "Separarmos o cálculo da pontuação em uma função própria tem duas vantagens: "
        "o código principal fica mais limpo, e podemos testar a fórmula isoladamente."
    ))
    el += bloco_codigo("""
def calcular_pontuacao(gols, assist, alvo, amarelo, vermelho, faltas):
    return round(
        gols    * PESO_GOL             +   # ex: 4 gols × 4 = 16 pontos
        assist  * PESO_ASSISTENCIA     +   # ex: 2 assist × 2 = 4 pontos
        alvo    * PESO_CHUTE_NO_ALVO   +   # ex: 9 chutes × 1 = 9 pontos
        amarelo * PESO_CARTAO_AMARELO  +   # ex: 0 amarelos × -1 = 0
        vermelho * PESO_CARTAO_VERMELHO +  # ex: 0 vermelhos × -3 = 0
        faltas  * PESO_FALTA_COMETIDA,     # ex: 0 faltas × -0.5 = 0
        1,  # arredonda para 1 casa decimal
    )
    # Mbappé: 4×4 + 2×2 + 9×1 = 16+4+9 = 29.0 pontos
""")

    # ── Bloco 17: Cruzamento dos endpoints ─────────────────────────────────
    el += secao("17", "main() — Cruzando /topscorers com /topcards")
    el.append(p(
        "Este é o trecho mais importante do script: cruzamos os dados de dois "
        "endpoints usando o ID do jogador como chave comum. "
        "A técnica é similar a um JOIN em SQL."
    ))
    el += bloco_codigo("""
    # 1. Busca os dois endpoints
    scorers = buscar("topscorers")   # 200 jogadores com stats ofensivas
    cartoes = buscar("topcards")     # 157 jogadores com cartões e faltas

    # 2. Cria dicionário indexado pelo IdPlayer para busca rápida
    #    Em vez de percorrer a lista inteira para achar cada jogador (lento),
    #    acessamos em tempo constante: cartoes_por_id["229397"]
    cartoes_por_id = {c["IdPlayer"]: c for c in cartoes}
    # dict comprehension: { chave: valor for item in lista }

    # 3. Para cada jogador dos topscorers, busca seus cartões
    jogadores = []
    for p in scorers:
        pid = p["IdPlayer"]   # ex: "229397" (ID do Messi)

        # .get(pid, {}) → busca pelo ID; se não tiver cartão, retorna {}
        c = cartoes_por_id.get(pid, {})

        # Extrai cada campo com "or 0" para garantir número mesmo se vier None
        gols    = p.get("Goals")           or 0
        assist  = p.get("Assists")         or 0
        alvo    = p.get("AttemptsOnTarget") or 0
        amarelo = c.get("YellowCards")     or 0  # c pode ser {} se não tiver
        vermelho = c.get("RedCards")       or 0
        faltas  = c.get("FoulsCommitted")  or 0

        pontuacao = calcular_pontuacao(gols, assist, alvo, amarelo, vermelho, faltas)

        jogadores.append({
            "jogador":              texto(p.get("PlayerName")),
            "pais":                 p.get("IdCountry", ""),
            "gols":                 gols,
            "assistencias":         assist,
            "participacoes_em_gol": gols + assist,  # Goal Contributions
            "pontuacao":            pontuacao,
            # ... outros campos
        })
""")

    # ── Bloco 18: Ordenação e salvamento ────────────────────────────────────
    el += secao("18", "main() — Ordenando por múltiplos critérios")
    el += bloco_codigo("""
    # Ordena por 3 critérios em ordem de prioridade:
    # 1º → maior Pontuação (negativo = decrescente)
    # 2º → maior Participações em Gol (desempate)
    # 3º → maior número de Gols (desempate final)
    jogadores.sort(key=lambda x: (
        -x["pontuacao"],
        -x["participacoes_em_gol"],
        -x["gols"],
    ))
    # sort() ordena no lugar (altera a lista original)
    # A chave é uma tupla: Python compara elemento por elemento

    # Adiciona o número de posição no ranking
    for i, j in enumerate(jogadores, 1):
        j["pos"] = i   # i começa em 1 (segundo argumento do enumerate)

    # Salva os TOP_N primeiros no CSV
    campos = ["pos", "jogador", "pais", "gols", "assistencias",
              "participacoes_em_gol", "chutes", "chutes_no_alvo",
              "cartoes_amarelos", "cartoes_vermelhos",
              "faltas_cometidas", "faltas_sofridas", "pontuacao"]

    with open(saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(jogadores[:TOP_N])
        # jogadores[:TOP_N] → fatia da lista: só os primeiros TOP_N itens
""")

    el.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # RESUMO COMPARATIVO
    # ══════════════════════════════════════════════════════════════════════
    el += secao("19", "Comparação entre os dois scripts")
    el.append(tabela(
        ["Característica", "fifa_estatisticas_jogos.py", "fifa_ranking_oficial.py"],
        [
            ["Endpoint usado",        "/timelines",                     "/topscorers + /topcards"],
            ["Nº de requisições",     "1 por jogo (64 no total)",       "Apenas 2"],
            ["Tempo de execução",     "~20 segundos",                   "~2 segundos"],
            ["Dados por jogador",     "Eventos do jogo (bruto)",        "Estatísticas agregadas (oficial)"],
            ["Destaque por jogo",     "Sim (score ponderado)",          "Não"],
            ["Dados são oficiais?",   "Parcialmente (nossa fórmula)",   "Sim (dados diretos da FIFA)"],
            ["Arquivo de entrada",    "fifa_jogos_completo.json",       "Nenhum (API direta)"],
            ["Arquivo de saída",      "4 CSVs",                         "1 CSV"],
        ],
        widths=[4.5*cm, 6.5*cm, 6*cm]
    ))

    el.append(sp(0.5))

    # ── Conceitos chave ─────────────────────────────────────────────────────
    el += secao("20", "Conceitos-chave para estudar mais")
    el.append(tabela(
        ["Conceito", "Onde aparece", "Para aprender mais"],
        [
            ["List comprehension",  "[j for j in lista if condição]",     "Python básico — listas"],
            ["defaultdict",         "acumuladores de stats",               "Python collections"],
            ["Regex (re.match)",    "extrair nome do jogador",             "Expressões regulares"],
            ["f-strings",           "montar URLs e mensagens",             "Python strings"],
            ["with open()",         "ler e salvar arquivos",               "Python I/O"],
            [".get(chave, padrão)", "acessar JSON sem erro",              "Python dicionários"],
            ["sorted() / .sort()",  "ordenar rankings",                    "Python ordenação"],
            ["enumerate()",         "loop com índice",                     "Python built-ins"],
            ["lambda",              "funções anônimas em sort/max",        "Python funções"],
            ["try/except",          "tratamento de erros da API",          "Python exceções"],
        ],
        widths=[4*cm, 6*cm, 7*cm]
    ))

    el.append(sp(0.5))
    el.append(hr())
    el.append(Paragraph(
        "Gerado em 26/06/2026  |  Projeto Copa do Mundo FIFA 2026  |  Python 3.12",
        rodape_est))

    return el


# ══════════════════════════════════════════════════════════════════════════════
# GERAR PDF
# ══════════════════════════════════════════════════════════════════════════════

def gerar():
    doc = SimpleDocTemplate(
        ARQUIVO_SAIDA, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
        title="FIFA 2026 — Estudo do Código",
        author="Lucas Martins",
    )
    doc.build(capa() + arquivo1() + arquivo2())
    print(f"PDF gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    gerar()
