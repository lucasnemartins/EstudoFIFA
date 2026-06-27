# Documentação — Projeto Copa do Mundo FIFA 2026

## Visão Geral

Este projeto extrai, processa e analisa dados da Copa do Mundo FIFA 2026 diretamente da **API pública oficial da FIFA** (`https://api.fifa.com/api/v3`), sem necessidade de chave de acesso ou autenticação.

---

## Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `fifa_extrair_jogos.py` | Extrai todos os jogos de todas as edições da Copa (1930–2026) |
| `fifa_jogos_hoje.py` | Gera palpites estatísticos para os jogos do dia |
| `fifa.ipynb` | Notebook com visualizações históricas (gráficos) |
| `fifa_jogos_completo.json` | JSON cru com todos os 1.068 jogos baixados |
| `fifa_jogos.csv` | Planilha resumida com data legível e vencedor |
| `fifa_previsao_campeao_2026.csv` | Ranking simples de favoritos por pontos |
| `fifa_artilharia.csv` | Artilharia extraída dos eventos de timeline |
| `fifa_faltas.csv` | Ranking de faltas por jogador |
| `fifa_chutes.csv` | Ranking de chutes a gol por jogador |
| `fifa_destaque_jogo.csv` | Melhor jogador por partida (com gols, assist. e chances criadas) |
| `fifa_palpite_hoje.csv` | Palpites do dia com resultado real (quando disponível) |

---

## 1. API Pública da FIFA

### Base URL
```
https://api.fifa.com/api/v3
```

### Por que funciona sem autenticação?
A API é a mesma usada pelo site `inside.fifa.com`. Basta simular um navegador com os headers corretos:

```python
SESSAO.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://inside.fifa.com",
    "Referer": "https://inside.fifa.com/",
})
```

### Endpoints utilizados

| Endpoint | O que retorna |
|----------|---------------|
| `GET /seasons?idCompetition=17` | Lista todas as edições da Copa do Mundo |
| `GET /calendar/matches?idCompetition=17&idSeason={id}` | Todos os jogos de uma edição |
| `GET /timelines/17/{idSeason}/{idStage}/{idMatch}` | Eventos minuto a minuto de um jogo |
| `GET /topscorers?idCompetition=17&idSeason={id}` | Artilheiros oficiais com estatísticas |
| `GET /topcards?idCompetition=17&idSeason={id}` | Cartões e faltas oficiais por jogador |

> **Nota:** IDs importantes: `idCompetition=17` (Copa do Mundo masculina), `idSeason=285023` (edição 2026).

---

## 2. Extração de Jogos (`fifa_extrair_jogos.py`)

### Fluxo

```
1. GET /seasons → descobre as 23 edições (1930 a 2026)
2. Para cada edição:
   GET /calendar/matches → baixa todos os jogos
3. Salva fifa_jogos_completo.json (1.068 jogos)
4. Gera fifa_jogos.csv (com data legível e coluna de vencedor)
5. Gera fifa_previsao_campeao_2026.csv (ranking por pontos)
```

### Tratamento de nomes multilíngues

A FIFA entrega nomes de times e estádios como **lista de traduções**:

```json
"TeamName": [
  { "Locale": "pt-BR", "Description": "França" },
  { "Locale": "en-GB", "Description": "France" }
]
```

Função para extrair o idioma desejado:

```python
def texto_localizado(lista, idioma="pt"):
    for item in lista:
        if item["Locale"].lower().startswith(idioma):
            return item["Description"]
    return lista[0]["Description"]  # fallback para o primeiro disponível
```

### Padronização de nomes históricos

Times que mudaram de nome ao longo da história são unificados:

```python
def padroniza_nome(nome):
    # Alemanha + Alemanha Ocidental (RFA) → "Alemanha"
    if "aleman" in nome.lower() or "germany" in nome.lower():
        return "Alemanha"
    mapa = {
        "uniao sovietica": "Russia",
        "iugoslavia": "Servia",
    }
    return mapa.get(nome.lower(), nome)
```

---

## 3. Modelo Estatístico de Palpites (`fifa_jogos_hoje.py`)

### Distribuição de Poisson

O modelo usa a **distribuição de Poisson**, que representa bem a natureza de gols em futebol (eventos raros e independentes):

```
P(k gols) = e^(-λ) × λ^k / k!
```

Onde `λ` é o número esperado de gols de cada time no confronto.

### Passo 1 — Calcular força de cada seleção

Com base nos jogos já disputados, calculamos o índice de **ataque** e **defesa** de cada time:

```python
K = 4.0  # fator de regularização (suaviza times com poucos jogos)

ataque[time] = ((gols_marcados + K × média) / (jogos + K)) / média
defesa[time]  = ((gols_sofridos + K × média) / (jogos + K)) / média
```

O `K` puxa times com poucos jogos em direção à média geral, evitando distorções.

### Passo 2 — Gols esperados no confronto

```python
λ_casa = média × ataque[casa] × defesa[fora]
λ_fora = média × ataque[fora] × defesa[casa]
```

### Passo 3 — Probabilidades via Poisson

Somamos as probabilidades de todos os placares possíveis (0×0 até 10×10):

```python
for i in range(11):         # gols do mandante
    for j in range(11):     # gols do visitante
        p = poisson(i, λ_casa) × poisson(j, λ_fora)
        if i > j: p_vitória_casa += p
        if i == j: p_empate      += p
        if i < j: p_vitória_fora += p
```

### Placar mais provável

Além das probabilidades, o modelo identifica o placar exato mais provável **coerente com o palpite**:

```python
# Filtra apenas placares onde o palpite se confirma
# e retorna aquele com maior probabilidade
def placar_mais_provavel(λ_casa, λ_fora, resultado):
    for i, j in todos_os_placares:
        if resultado == "casa" and i > j:
            candidatos.append((i, j, p))
    return max(candidatos, key=lambda x: x[2])
```

---

## 4. Simulação Monte Carlo (Previsão do Campeão)

Para estimar a probabilidade de cada seleção ser campeã, rodamos **50.000 simulações** completas do torneio.

### Fluxo de cada simulação

```
1. Simula os jogos pendentes da fase de grupos
   → amostra gols de distribuições de Poisson independentes

2. Classifica os 12 grupos
   → top 2 de cada grupo + 8 melhores 3os = 32 classificados

3. Simula o mata-mata (32 → 16 → 8 → 4 → 2 → 1)
   → empates no tempo normal vão a pênaltis (probabilidade proporcional à força ofensiva)

4. Registra o campeão
```

### Amostragem de Poisson

```python
def amostrar_poisson(lam):
    # Método de Knuth: simula via produto de uniformes
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        p *= random.random()
        k += 1
    return k - 1
```

### Pênaltis simulados

```python
# Probabilidade proporcional à força de ataque do time
prob_a = ataque[time_a] / (ataque[time_a] + ataque[time_b])
vencedor = time_a if random.random() < prob_a else time_b
```

### Resultado

Após 50.000 simulações:
```
% de campeão = (nº de vezes que o time venceu) / 50.000 × 100
```

---

## 5. Extração de Eventos por Jogo (`/timelines`)

### Endpoint

```
GET /api/v3/timelines/17/{idSeason}/{idStage}/{idMatch}
```

Retorna até **80+ eventos por jogo**, cada um com:

```json
{
  "Type": 0,
  "MatchMinute": "9'",
  "IdPlayer": "429157",
  "IdTeam": "43911",
  "EventDescription": [
    { "Locale": "pt-BR", "Description": "Julian QUINONES (México) marca o gol!!" }
  ]
}
```

### Todos os tipos de eventos mapeados (64 jogos varridos)

| Tipo | Evento | Total | Tem Jogador |
|------|--------|------:|:-----------:|
| 0 | Gol | 169 | Sim |
| 1 | Assistência | 136 | Sim |
| 2 | Cartão amarelo | 150 | Sim |
| 3 | Cartão vermelho | 9 | Sim |
| 5 | Substituição | 592 | Sim |
| 6 | Pênalti marcado | 8 | Sim |
| 7 | Horário de início | 126 | Não |
| 8 | Horário de término | 124 | Não |
| 12 | Chute a gol | 1.531 | Sim |
| 15 | Impedimento | 209 | Sim |
| 16 | Escanteio | 555 | Sim |
| 18 | Falta | 1.259 | Sim |
| 26 | Fim do jogo | 62 | Não |
| 34 | Gol contra | 12 | Sim |
| 41 | Gol de pênalti | 6 | Sim |
| 57 | Gol evitado | 312 | Sim |
| 71 | VAR | 18 | Não |
| 79/80 | Cara ou coroa (sorteio) | 64 | Não |
| 83/85 | Atraso | 124 | Não |

### Extração do nome do jogador

O nome vem embutido no `EventDescription` no formato `"NOME (Seleção) ação"`:

```python
import re

def nome_jogador(evento):
    desc = texto_localizado(evento.get("EventDescription"))
    m = re.match(r'^([^(]+)\(([^)]+)\)', desc.strip())
    if m:
        nome  = m.group(1).strip().title()  # ex: "Julian Quinones"
        time  = m.group(2).strip()          # ex: "México"
        return nome, time
    return desc[:40], ""
```

---

## 6. Estatísticas Oficiais da FIFA

Além do `/timelines`, foram encontrados dois endpoints com **dados oficiais** agregados por jogador:

### `/topscorers`

```
GET /topscorers?idCompetition=17&idSeason=285023&language=pt&count=200
```

Campos retornados:
- `Goals` — gols marcados
- `Assists` — assistências
- `Shots` — total de chutes
- `AttemptsOnTarget` — chutes no alvo
- `Matches` / `MinutesPlayed` — jogos e minutos
- `PenaltiesScored` — pênaltis convertidos
- `GoalsScoredByLeftFoot` / `RightFoot` / `Head` — gols por tipo

### `/topcards`

```
GET /topcards?idCompetition=17&idSeason=285023&language=pt&count=200
```

Campos retornados:
- `YellowCards` / `RedCards` / `DoubleYellowCards`
- `FoulsCommitted` — faltas cometidas
- `FoulsSuffered` — faltas sofridas
- `PenaltyFouls` — faltas que geraram pênalti

> **Nota:** Endpoints de "Man of the Match" oficial (`/motm`, `/awards`, `/ratings`, `/manofthematch`) foram todos testados e retornam **404** — a FIFA não expõe esse dado na API pública.

---

## 7. Ranking de Desempenho (Pontuação)

Como a FIFA não disponibiliza um "destaque por jogo" oficial, foi criada uma **pontuação ponderada** com base nos eventos:

| Evento | Pontos |
|--------|-------:|
| Gol / Gol de pênalti | +4 |
| Assistência | +2 |
| Chute no alvo | +1 |
| Gol evitado (defesa) | +1 |
| Falta cometida | −0.5 |
| Cartão amarelo | −1 |
| Cartão vermelho | −3 |

### Participações em Gol (Goal Contributions)

Métrica padrão internacional:

```
Participações em Gol = Gols + Assistências
```

### Chances Criadas

Métrica ofensiva que soma todas as ações que geraram oportunidade:

```
Chances Criadas = Gols + Assistências + Chutes + Gols evitados
```

---

## 8. Top 20 — Ranking Final (dados oficiais FIFA)

| # | Jogador | País | Gols | Assist. | Part. em Gol | Chutes | No Alvo | Pontuação |
|---|---------|------|-----:|-------:|-------------:|-------:|--------:|----------:|
| 1 | Kylian Mbappé | FRA | 4 | 2 | 6 | 16 | 9 | 29.0 |
| 2 | Lionel Messi | ARG | 5 | 0 | 5 | 13 | 8 | 28.0 |
| 3 | Vinicius Junior | BRA | 4 | 1 | 5 | 12 | 8 | 26.0 |
| 4 | Ousmane Dembélé | FRA | 4 | 1 | 5 | 8 | 5 | 23.0 |
| 5 | Erling Haaland | NOR | 4 | 0 | 4 | 9 | 6 | 22.0 |
| 6 | Deniz Undav | GER | 3 | 2 | 5 | 5 | 4 | 20.0 |
| 7 | Ismaila Sarr | SEN | 3 | 1 | 4 | 12 | 5 | 19.0 |
| 8 | Jonathan David | CAN | 3 | 0 | 3 | 13 | 7 | 19.0 |
| 9 | Johan Manzambi | SUI | 3 | 1 | 4 | 6 | 3 | 17.0 |
| 10 | Alexander Isak | SWE | 1 | 3 | 4 | 6 | 5 | 15.0 |
| 11 | Brian Brobbey | NED | 3 | 0 | 3 | 4 | 3 | 15.0 |
| 12 | Matheus Cunha | BRA | 3 | 0 | 3 | 6 | 3 | 15.0 |
| 13 | Ismael Saibari | MAR | 3 | 0 | 3 | 10 | 3 | 15.0 |
| 14 | Cody Gakpo | NED | 2 | 1 | 3 | 9 | 5 | 15.0 |
| 15 | Mikel Oyarzabal | ESP | 2 | 1 | 3 | 10 | 4 | 14.0 |
| 16 | Ruben Vargas | SUI | 2 | 1 | 3 | 6 | 4 | 14.0 |
| 17 | Maxi Araujo | URU | 2 | 1 | 3 | 4 | 3 | 13.0 |
| 18 | Ayase Ueda | JPN | 2 | 1 | 3 | 7 | 3 | 13.0 |
| 19 | Cristiano Ronaldo | POR | 2 | 0 | 2 | 10 | 5 | 13.0 |
| 20 | Harry Kane | ENG | 2 | 0 | 2 | 10 | 4 | 12.0 |

---

## 9. Fluxo Completo Resumido

```
API FIFA (api.fifa.com/api/v3)
│
├── /seasons                → 23 edições da Copa (1930–2026)
│
├── /calendar/matches       → 1.068 jogos
│   ├── fifa_jogos_completo.json
│   └── fifa_jogos.csv
│
├── /timelines (64 jogos)   → 80+ eventos por jogo
│   ├── fifa_artilharia.csv
│   ├── fifa_faltas.csv
│   ├── fifa_chutes.csv
│   └── fifa_destaque_jogo.csv
│
├── /topscorers             → estatísticas oficiais de gols/chutes
│   └── ranking top 20 com Pontuação
│
├── /topcards               → estatísticas oficiais de cartões/faltas
│   └── cruzado com /topscorers
│
└── Modelos internos
    ├── Poisson             → palpites dos jogos do dia
    └── Monte Carlo (50k)   → % de chance de ser campeão
```

---

*Gerado em 26/06/2026 | Dados: API pública FIFA api.fifa.com/api/v3*
