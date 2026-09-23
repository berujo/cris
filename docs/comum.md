# Método comum dos analistas

Lê isto antes de analisar. As regras completas estão em `CLAUDE.md`; os números em `dados/config.json`.

## Princípios
- **O mercado é o ponto de partida.** A probabilidade justa (odds sem margem, de preferência da Pinnacle) já reflete quase toda a informação pública. Só há valor quando tens uma razão concreta e verificável para discordar dela, ou quando uma casa paga acima da odd justa.
- **Ajuste máximo de 8 pontos percentuais** face à probabilidade justa do mercado. Se a tua estimativa se afasta mais, quase sempre o erro é teu: revê ou descarta.
- **Nunca inventes dados.** Cada odd, estatística ou notícia leva fonte e hora da consulta. O que não conseguiste verificar fica marcado como "não verificado".
- **Contas:** valor esperado (EV) = probabilidade estimada × odd − 1. Odd justa = 1 / probabilidade. Odd mínima aceitável = 1,04 / probabilidade (EV mínimo de 4%).
- **Zero candidatas é uma resposta válida e frequente.** Não forces apostas.

## Fontes de dados
- **Odds:** `python3 scripts/odds.py desportos` lista as competições ativas (não gasta créditos); `python3 scripts/odds.py odds <chave> --horas 36` mostra, por jogo, a odd justa, a melhor odd e o valor. Gasta créditos (500/mês no plano gratuito): pede só `h2h` salvo necessidade, e só as competições relevantes. Se falhar (sem `ODDS_API_KEY` ou rede bloqueada), procura as odds na web e indica a casa e a hora.
- **Estatísticas e agenda (se a rede o permitir):** `https://site.api.espn.com/apis/site/v2/sports/<desporto>/<liga>/scoreboard?dates=AAAAMMDD` (ex.: `soccer/por.1`, `soccer/eng.1`, `basketball/nba`, `basketball/wnba`, `baseball/mlb`, `tennis/atp`) e `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=AAAA-MM-DD&hydrate=probablePitcher`.
- **Pesquisa web** para o resto: forma, xG, ratings, lesões, notícias.

## Níveis de confiança
- **Alta:** odds confirmadas em várias casas, informação-chave confirmada (onze, lançador, lesões), a tua estimativa e o sinal de mercado apontam no mesmo sentido, EV ≥ 6%.
- **Média:** dados bons com uma incerteza relevante (ex.: onze por confirmar), EV ≥ 4%.
- **Baixa:** poucos dados, odds não verificadas ou estimativa assente num só argumento. **Não entra no plano.**

## Formato de cada candidata
```
CANDIDATA
Desporto e competição:
Jogo/evento (data e hora de Lisboa):
Mercado e seleção:
Tipo: simples | live (condição de entrada objetiva) | perna de múltipla
Melhor odd (casa, hora da consulta):
Probabilidade justa do mercado (fonte):
Probabilidade estimada:
EV:
Confiança (alta/média/baixa) e porquê:
Justificação (2–4 frases com dados concretos e fontes):
O que invalidaria a aposta:
```
Se não houver valor: `SEM CANDIDATAS` e o motivo em 1–2 frases.
