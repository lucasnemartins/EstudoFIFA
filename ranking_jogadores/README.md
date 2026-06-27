# ⚽ Copa do Mundo FIFA 2026 — Análise de Dados com Python

Projeto de extração, análise e previsão estatística da Copa do Mundo FIFA 2026 usando a **API pública da FIFA** e modelos estatísticos em Python puro.

> **Dados atualizados em:** 27/06/2026 — Fase de Grupos

---

## 📋 O que o projeto faz

| Módulo | O que entrega |
|--------|---------------|
| **Extrator de jogos** | Baixa todos os jogos das 23 edições da Copa (1930–2026) |
| **Previsão do campeão** | Simulação Monte Carlo com 50.000 iterações por distribuição de Poisson |
| **Palpite de hoje** | Probabilidades e placar mais provável para os jogos do dia |
| **Estatísticas por jogo** | Artilharia, faltas, chutes e destaque por partida via eventos de timeline |
| **Ranking oficial** | Top 50 jogadores cruzando `/topscorers` + `/topcards` da FIFA |

---

## 📊 Resultados — Copa do Mundo 2026

### 🥇 Ranking Oficial de Jogadores (Top 20)

> Pontuação = Gols×4 + Assist×2 + Chutes no Alvo×1 + Amarelo×−1 + Vermelho×−3 + Faltas×−0.5

| # | Jogador | País | Jogos | Min | Gols | Assist. | Part. em Gol | Chutes | No Alvo | 🟨 | 🟥 | Faltas | Pontuação |
|---|---------|------|:-----:|:---:|:----:|:-------:|:------------:|:------:|:-------:|:--:|:--:|:------:|:---------:|
| 1 | Kylian MBAPPE | FRA | 3 | 290 | 4 | 2 | 6 | 16 | 9 | 0 | 0 | 0 | **29.0** |
| 2 | Lionel MESSI | ARG | 2 | 187 | 5 | 0 | 5 | 13 | 8 | 0 | 0 | 0 | **28.0** |
| 3 | VINICIUS JUNIOR | BRA | 3 | 293 | 4 | 1 | 5 | 12 | 8 | 0 | 0 | 0 | **26.0** |
| 4 | Ousmane DEMBELE | FRA | 3 | 225 | 4 | 1 | 5 | 8 | 5 | 0 | 0 | 0 | **23.0** |
| 5 | Erling HAALAND | NOR | 2 | 207 | 4 | 0 | 4 | 9 | 6 | 0 | 0 | 0 | **22.0** |
| 6 | Deniz UNDAV | GER | 3 | 106 | 3 | 2 | 5 | 5 | 4 | 0 | 0 | 0 | **20.0** |
| 7 | Ismaila SARR | SEN | 3 | 274 | 3 | 1 | 4 | 12 | 5 | 0 | 0 | 0 | **19.0** |
| 8 | Jonathan DAVID | CAN | 3 | 270 | 3 | 0 | 3 | 13 | 7 | 0 | 0 | 0 | **19.0** |
| 9 | Johan MANZAMBI | SUI | 3 | 146 | 3 | 1 | 4 | 6 | 3 | 0 | 0 | 0 | **17.0** |
| 10 | Alexander ISAK | SWE | 3 | 296 | 1 | 3 | 4 | 6 | 5 | 0 | 0 | 0 | **15.0** |
| 11 | Brian BROBBEY | NED | 3 | 168 | 3 | 0 | 3 | 4 | 3 | 0 | 0 | 0 | **15.0** |
| 12 | MATHEUS CUNHA | BRA | 3 | 191 | 3 | 0 | 3 | 6 | 3 | 0 | 0 | 0 | **15.0** |
| 13 | Ismael SAIBARI | MAR | 3 | 255 | 3 | 0 | 3 | 10 | 3 | 0 | 0 | 0 | **15.0** |
| 14 | Cody GAKPO | NED | 3 | 268 | 2 | 1 | 3 | 9 | 5 | 0 | 0 | 0 | **15.0** |
| 15 | Ruben VARGAS | SUI | 3 | 193 | 2 | 1 | 3 | 6 | 4 | 0 | 0 | 0 | **14.0** |
| 16 | Mikel OYARZABAL | ESP | 3 | 232 | 2 | 1 | 3 | 11 | 4 | 0 | 0 | 0 | **14.0** |
| 17 | Ayase UEDA | JPN | 3 | 245 | 2 | 1 | 3 | 7 | 3 | 0 | 0 | 0 | **13.0** |
| 18 | Maxi ARAUJO | URU | 3 | 278 | 2 | 1 | 3 | 4 | 3 | 0 | 0 | 0 | **13.0** |
| 19 | CRISTIANO RONALDO | POR | 2 | 201 | 2 | 0 | 2 | 10 | 5 | 0 | 0 | 0 | **13.0** |
| 20 | Harry KANE | ENG | 2 | 204 | 2 | 0 | 2 | 10 | 4 | 0 | 0 | 0 | **12.0** |

---

### 🌍 Maiores Artilheiros All-Time — Copas do Mundo (1930–2026)

> Dados históricos (1930–2022) baseados nos registros oficiais da FIFA. Dados de 2026 atualizados em tempo real via API. ★ = Copa em andamento.

| # | Jogador | Seleção | Gols | Jogos | Copas |
|---|---------|---------|:----:|:-----:|:-----:|
| 1 | ⭐ Lionel Messi | Argentina | **18** ★ | 23 | 5 |
| 2 | Miroslav Klose | Alemanha | **16** | 27 | 4 |
| 3 | Ronaldo | Brasil | **15** | 19 | 3 |
| 4 | Gerd Müller | Alemanha | **14** | 12 | 2 |
| 5 | Just Fontaine | França | **13** | 6 | 1 |
| 6 | Uwe Seeler | Alemanha | **12** | 27 | 5 |
| 7 | Pelé | Brasil | **12** | 14 | 4 |
| 8 | Kylian Mbappé | França | **12** ★ | 14 | 2 |
| 9 | Jürgen Klinsmann | Alemanha | **11** | 19 | 3 |
| 10 | Harry Kane | Inglaterra | **11** ★ | 13 | 3 |
| 11 | Sándor Kocsis | Hungria | **11** | 5 | 1 |
| 12 | Cristiano Ronaldo | Portugal | **10** ★ | 26 | 7 |
| 13 | Karl-Heinz Rummenigge | Alemanha | **10** | 16 | 3 |
| 14 | Grzegorz Lato | Polônia | **10** | 14 | 2 |
| 15 | Thomas Müller | Alemanha | **10** | 13 | 2 |

> ★ ainda em campo na Copa 2026

---

### ⚽ Artilharia (Top 15)

| # | Jogador | Seleção | Gols |
|---|---------|---------|:----:|
| 1 | Lionel Messi | Argentina | **5** |
| 2 | Vinicius Junior | Brasil | **4** |
| 2 | Kylian Mbappe | França | **4** |
| 2 | Erling Haaland | Noruega | **4** |
| 2 | Ousmane Dembele | França | **4** |
| 6 | Ismael Saibari | Marrocos | 3 |
| 6 | Deniz Undav | Alemanha | 3 |
| 6 | Johan Manzambi | Suíça | 3 |
| 6 | Jonathan David | Canadá | 3 |
| 6 | Matheus Cunha | Brasil | 3 |
| 6 | Brian Brobbey | Holanda | 3 |
| 6 | Ismaila Sarr | Senegal | 3 |
| 13 | Julian Quinones | México | 2 |
| 13 | Cyle Larin | Canadá | 2 |
| 13 | Harry Kane | Inglaterra | 2 |

---

### 🎯 Chutes a Gol (Top 15)

| # | Jogador | Seleção | Chutes |
|---|---------|---------|:------:|
| 1 | Kylian Mbappe | França | **16** |
| 2 | Kenan Yildiz | Turquia | 14 |
| 3 | Jonathan David | Canadá | 13 |
| 3 | Lionel Messi | Argentina | 13 |
| 5 | Vinicius Junior | Brasil | 12 |
| 5 | Arda Guler | Turquia | 12 |
| 5 | Ismaila Sarr | Senegal | 12 |
| 8 | Hakan Calhanoglu | Turquia | 11 |
| 8 | Viktor Gyokeres | Suécia | 11 |
| 8 | Mikel Oyarzabal | Espanha | 11 |
| 11 | Julian Quinones | México | 10 |
| 11 | Achraf Hakimi | Marrocos | 10 |
| 11 | Ismael Saibari | Marrocos | 10 |
| 11 | Enner Valencia | Equador | 10 |
| 11 | Cristiano Ronaldo | Portugal | 10 |

---

### 🟨 Ranking de Faltas Cometidas (Top 15)

| # | Jogador | Seleção | Faltas |
|---|---------|---------|:------:|
| 1 | Andrés Cubas | Paraguai | **11** |
| 2 | Behruzjon Karimov | Uzbequistão | 8 |
| 3 | Lee Hanbeom | República da Coreia | 7 |
| 3 | Ermedin Demirovic | Bósnia e Herzegovina | 7 |
| 3 | Martin Experience | Haiti | 7 |
| 3 | Aleksandar Pavlovic | Alemanha | 7 |
| 3 | Hiroki Ito | Japão | 7 |
| 8 | Robin Hranac | Tchéquia | 6 |
| 8 | Juan Jose Caceres | Paraguai | 6 |
| 8 | Breel Embolo | Suíça | 6 |
| 8 | Jassem Gaber | Catar | 6 |
| 8 | Ricardo Rodriguez | Suíça | 6 |
| 8 | Neil El Aynaoui | Marrocos | 6 |
| 8 | Thomas Meunier | Bélgica | 6 |
| 8 | Rodrigo Bentancur | Uruguai | 6 |

---

### 🏆 Destaque por Jogo — Top 10 por Score

> Score calculado pela soma ponderada de eventos: gols (+4), assistências (+2), chutes (+1), faltas (−0.5), cartões...

| Data | Jogo | Destaque | Seleção | Gols | Assist. | Chutes | Score |
|------|------|----------|---------|:----:|:-------:|:------:|:-----:|
| 2026-06-18 | Canadá **6** × 0 Catar | Jonathan David | Canadá | 3 | 0 | 8 | **20.0** |
| 2026-06-17 | Argentina **3** × 0 Argélia | Lionel Messi | Argentina | 3 | 0 | 6 | **17.5** |
| 2026-06-22 | França **3** × 0 Iraque | Kylian Mbappe | França | 2 | 0 | 8 | **15.5** |
| 2026-06-24 | Escócia 0 × **3** Brasil | Vinicius Junior | Brasil | 2 | 0 | 8 | **15.5** |
| 2026-06-22 | Argentina **2** × 0 Áustria | Lionel Messi | Argentina | 2 | 0 | 7 | **15.0** |
| 2026-06-26 | Noruega 1 × **4** França | Ousmane Dembele | França | 3 | 0 | 3 | **15.0** |
| 2026-06-23 | Portugal **5** × 0 Uzbequistão | Cristiano Ronaldo | Portugal | 2 | 0 | 7 | **14.5** |
| 2026-06-17 | Inglaterra **4** × 2 Croácia | Harry Kane | Inglaterra | 2 | 0 | 7 | **14.0** |
| 2026-06-23 | Noruega **3** × 2 Senegal | Ismaila Sarr | Senegal | 2 | 0 | 6 | **14.0** |
| 2026-06-13 | EUA **4** × 1 Paraguai | Folarin Balogun | EUA | 2 | 0 | 5 | **13.0** |

---

### 📋 Classificação Geral — Fase de Grupos

> Ordenado por pontos e saldo de gols. Inclui todas as seleções com jogos disputados.

| # | Seleção | Jogos | V | E | D | Gols Pró | Gols Contra | Pts | Saldo |
|---|---------|:-----:|:--:|:--:|:--:|:--------:|:-----------:|:---:|:-----:|
| 1 | 🇫🇷 França | 3 | 3 | 0 | 0 | 10 | 2 | **9** | +8 |
| 2 | 🇲🇽 México | 3 | 3 | 0 | 0 | 6 | 0 | **9** | +6 |
| 3 | 🇳🇱 Holanda | 3 | 2 | 1 | 0 | 10 | 4 | **7** | +6 |
| 4 | 🇧🇷 Brasil | 3 | 2 | 1 | 0 | 7 | 1 | **7** | +6 |
| 5 | 🇨🇭 Suíça | 3 | 2 | 1 | 0 | 7 | 3 | **7** | +4 |
| 6 | 🇲🇦 Marrocos | 3 | 2 | 1 | 0 | 6 | 3 | **7** | +3 |
| 7 | 🇩🇪 Alemanha | 3 | 2 | 0 | 1 | 10 | 4 | **6** | +6 |
| 8 | 🇦🇷 Argentina | 2 | 2 | 0 | 0 | 5 | 0 | **6** | +5 |
| 9 | 🇺🇸 EUA | 3 | 2 | 0 | 1 | 8 | 4 | **6** | +4 |
| 10 | 🇨🇴 Colômbia | 2 | 2 | 0 | 0 | 4 | 1 | **6** | +3 |
| 11 | 🇨🇮 Costa do Marfim | 3 | 2 | 0 | 1 | 4 | 2 | **6** | +2 |
| 12 | 🇳🇴 Noruega | 3 | 2 | 0 | 1 | 8 | 7 | **6** | +1 |
| 13 | 🇯🇵 Japão | 3 | 1 | 2 | 0 | 7 | 3 | **5** | +4 |
| 14 | 🇪🇸 Espanha | 3 | 1 | 2 | 0 | 4 | 0 | **5** | +4 |
| 15 | 🇨🇦 Canadá | 3 | 1 | 1 | 1 | 8 | 3 | **4** | +5 |
| 16 | 🇵🇹 Portugal | 2 | 1 | 1 | 0 | 6 | 1 | **4** | +5 |
| 17 | 🇸🇪 Suécia | 3 | 1 | 1 | 1 | 7 | 7 | **4** | 0 |
| 18 | 🇺🇾 Uruguai | 3 | 0 | 3 | 0 | 3 | 3 | **3** | 0 |
| 19 | 🇸🇳 Senegal | 3 | 1 | 0 | 2 | 8 | 6 | **3** | +2 |
| 20 | 🇹🇷 Turquia | 3 | 1 | 0 | 2 | 3 | 5 | **3** | −2 |

---

## 🗂️ Arquivos do projeto

```
FIFA/
├── fifa_extrair_jogos.py        ← extrai jogos históricos + previsão do campeão
├── fifa_jogos_hoje.py           ← palpite para os jogos do dia
├── fifa_estatisticas_jogos.py   ← artilharia, faltas, chutes e destaque por jogo
├── fifa_ranking_oficial.py      ← ranking oficial com dados da FIFA
│
├── fifa_jogos_completo.json     ← base com 1.068 jogos (1930–2026)  [gerado]
├── fifa_jogos.csv               ← versão CSV da base completa        [gerado]
├── fifa_previsao_campeao_2026.csv  ← classificação geral da fase de grupos  [gerado]
├── fifa_palpite_hoje.csv        ← palpites do dia                    [gerado]
├── fifa_artilharia.csv          ← ranking de gols                    [gerado]
├── fifa_faltas.csv              ← ranking de faltas cometidas         [gerado]
├── fifa_chutes.csv              ← ranking de chutes a gol             [gerado]
├── fifa_destaque_jogo.csv       ← destaque (MVP) por partida          [gerado]
└── fifa_ranking_oficial.csv     ← ranking completo Top 50             [gerado]
```

---

## 🚀 Como usar

### Pré-requisitos

```bash
pip install requests reportlab
```

### 1. Extrair todos os jogos

```bash
python fifa_extrair_jogos.py
```

Gera `fifa_jogos_completo.json` e `fifa_jogos.csv` com **1.068 partidas** de todas as edições da Copa (1930–2026).

### 2. Palpite para os jogos de hoje

```bash
python fifa_jogos_hoje.py
```

Exemplo de saída:

| Hora | Mandante | Visitante | % Casa | % Empate | % Fora | Placar Previsto | Resultado Real | Acertou? |
|------|----------|-----------|:------:|:--------:|:------:|:---------------:|:--------------:|:--------:|
| 16:00 | Senegal | Iraque | 80.2% | 11.2% | 8.5% | 3 × 1 | 5 × 0 | ✅ Sim |
| 16:00 | Noruega | França | 18.6% | 16.6% | 64.8% | 1 × 2 | 1 × 4 | ✅ Sim |

### 3. Estatísticas por jogo

```bash
python fifa_estatisticas_jogos.py
```

> Requer que o passo 1 já tenha sido executado.

### 4. Ranking oficial (dados diretos da FIFA)

```bash
python fifa_ranking_oficial.py
```

---

## 🔌 API utilizada

**Base URL:** `https://api.fifa.com/api/v3`  
Não requer autenticação — apenas headers de browser.

| Endpoint | O que retorna |
|----------|---------------|
| `/seasons?idCompetition=17` | Lista de edições da Copa |
| `/calendar/matches` | Jogos de uma edição |
| `/timelines/{idc}/{ids}/{idst}/{idm}` | Eventos de um jogo (gols, faltas, chutes...) |
| `/topscorers?idCompetition=17&idSeason=285023` | Artilheiros oficiais |
| `/topcards?idCompetition=17&idSeason=285023` | Disciplina por jogador |

**IDs fixos:**
- `idCompetition = 17` → Copa do Mundo FIFA Masculina
- `idSeason = 285023` → Edição 2026

**Tipos de evento no `/timelines`:**

| Type | Evento | Pontos no score |
|:----:|--------|:---------------:|
| 0 | Gol | +4 |
| 1 | Assistência | +2 |
| 12 | Chute a gol | +1 |
| 57 | Defesa do goleiro | +1 |
| 18 | Falta cometida | −0.5 |
| 2 | Cartão amarelo | −1 |
| 3 | Cartão vermelho | −3 |
| 34 | Gol contra | +3 |
| 41 | Gol de pênalti | +4 |
| 5 | Substituição | — |
| 71 | Revisão VAR | — |

---

## 🧮 Modelos estatísticos

### Modelo de Poisson para previsão de gols

```
P(i, j) = Poisson(λ_casa, i) × Poisson(λ_fora, j)

λ_casa = força_ataque_mandante × força_defesa_visitante × média_gols_casa
λ_fora = força_ataque_visitante × força_defesa_mandante × média_gols_fora
```

A matriz de probabilidades cobre placares de 0×0 até 10×10 (121 combinações).

**Regularização** para seleções com poucos jogos (`K = 4.0`):
```
força_ataque = (gols_marcados + K × média_global) / (jogos + K)
```

### Monte Carlo — Previsão do campeão (50.000 simulações)

```
Para cada simulação:
  1. Simular fase de grupos (48 jogos) → classificar 32 seleções
  2. Simular mata-mata: Oitavas → Quartas → Semi → Final
  3. Registrar o campeão

% de título = (vezes que a seleção venceu) / 50.000 × 100
```

Amostragem de Poisson via algoritmo de Knuth:

```python
def poisson_knuth(lam):
    L, k, p = math.exp(-lam), 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1
```

---

## 🛠️ Técnicas e conceitos utilizados

| Conceito Python | Onde é usado |
|----------------|-------------|
| `requests.Session()` | Reutilizar conexão HTTP com headers fixos |
| `defaultdict` | Acumuladores de stats sem verificar se a chave existe |
| List comprehension | Filtrar jogos por temporada e data |
| Regex (`re.match`) | Extrair nome do jogador do campo `EventDescription` |
| `datetime` + `timezone` | Verificar se o jogo já foi disputado |
| `sorted()` + `lambda` | Ordenar rankings por múltiplos critérios |
| `enumerate()` | Loop com índice para numerar posições |
| `csv.DictWriter` | Salvar dicionários como CSV com UTF-8-BOM |
| Distribuição de Poisson | Modelar número esperado de gols por jogo |
| Monte Carlo | Simular o torneio completo 50.000 vezes |
| Cross-join por `IdPlayer` | Cruzar `/topscorers` com `/topcards` |

---

## 📦 Dependências

| Biblioteca | Uso | Instalação |
|-----------|-----|-----------|
| `requests` | Requisições HTTP para a API da FIFA | `pip install requests` |
| `reportlab` | Geração dos PDFs de documentação | `pip install reportlab` |
| `json`, `csv`, `os`, `re`, `time`, `math`, `random`, `datetime`, `collections` | Padrão do Python | já incluídas |

**Versão mínima:** Python 3.8+

---

## 📄 Documentação adicional

| Arquivo | Conteúdo |
|---------|---------|
| `DOCUMENTACAO.md` | Documentação técnica completa do projeto |
| `FIFA_2026_Documentacao_v2.pdf` | PDF explicativo para iniciantes (18 seções) |
| `FIFA_2026_Estudo_do_Codigo.pdf` | Código comentado linha por linha (20 seções) |

---

## 👤 Autor

**Lucas Martins**  
Projeto pessoal de análise de dados — Copa do Mundo FIFA 2026
