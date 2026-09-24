# Método comum dos analistas

Lê isto antes de analisar. As regras completas estão em `CLAUDE.md`; os números em `dados/config.json`.

## O teu papel: filtro, não adivinho
- **Quem encontra as candidatas é o preço.** A varredura (`python3 scripts/odds.py valor`) mostra as seleções em que uma casa paga acima do preço justo da Pinnacle. O teu trabalho é decidir se essa diferença é valor verdadeiro ou uma armadilha.
- **Não geres palpites próprios.** Opinar contra o mercado perdeu dinheiro nos estudos com LLMs. Contexto que o mercado já conhece (forma, xG, Elo, confrontos diretos) serve para justificar, não para mudar a probabilidade.
- **Ajuste máximo de 3 pontos percentuais** face ao preço justo, e só com um facto concreto, verificável e recente que o mercado ainda não refletiu (ex.: lesão confirmada há minutos). Por defeito, o ajuste é 0. O `banca.py` recusa ajustes maiores.
- **Nunca inventes dados.** Cada odd, estatística ou notícia leva fonte e hora da consulta. O que não conseguiste verificar fica marcado como "não verificado".
- **Contas:**
  - Valor esperado: EV = probabilidade × odd − 1.
  - Odd justa: 1 / probabilidade.
  - Odd mínima: 1,03 / probabilidade contra a Pinnacle, ou 1,05 / probabilidade contra a média das casas.
- **Zero candidatas aprovadas é uma resposta válida e frequente.**

## Armadilhas a verificar em cada candidata
1. **Odd desatualizada:** a casa ainda não acompanhou uma notícia ou um movimento. Vê a idade da odd (mais de 60 minutos exige confirmação) e o movimento (`mov`) desde a última varredura.
2. **Informação que explica a diferença:** lesão, onze, lançador, meteorologia, motivação. Se a notícia favorece o preço mais alto, o valor é real. Se a casa sabe algo que a Pinnacle ainda não refletiu, é armadilha.
3. **Regras de liquidação diferentes:** desistências no ténis, prolongamento no futebol e no basquetebol, troca de lançador no basebol. A mesma seleção pode pagar de forma diferente consoante a casa.
4. **Correlação** com outras apostas do dia (mesma equipa, mesmo facto).
5. **Mercado ou linha diferentes:** o mesmo nome com outra linha (ex.: handicap −1 contra −1,5) não é a mesma aposta.

## Fontes de dados
- **Varredura de valor:** `python3 scripts/odds.py valor --horas 36`. Os itens numerados são os que se passam ao `banca.py recomendar --item N`.
- **Detalhe de uma competição:** `python3 scripts/odds.py odds <chave> --mercados h2h,totals`. A lista de chaves ativas sai de `python3 scripts/odds.py desportos`.
- **Estatísticas e agenda (se a rede o permitir):**
  - ESPN: `https://site.api.espn.com/apis/site/v2/sports/<desporto>/<liga>/scoreboard?dates=AAAAMMDD` (ex.: `soccer/por.1`, `basketball/nba`, `basketball/wnba`, `baseball/mlb`, `tennis/atp`).
  - MLB: `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=AAAA-MM-DD&hydrate=probablePitcher`.
- **Outras APIs:** catálogo em `docs/apis.md`.
- **Pesquisa web** para notícias, lesões e contexto.
- **Sem API** (falta `ODDS_API_KEY` ou a rede está bloqueada): não há candidatas de preço. Podes descrever o dia, mas nada entra no plano.

## Níveis de confiança
- **Alta:**
  - preço justo da Pinnacle;
  - odd confirmada há 30 minutos ou menos;
  - EV ≥ 5%;
  - informação-chave confirmada (onze, lançador, lesões) e nenhuma notícia contra.
- **Média:**
  - Pinnacle com EV ≥ 3%, ou média das casas com EV ≥ 5%;
  - odd com 60 minutos ou menos;
  - no máximo uma incerteza por confirmar (ex.: onze).
- **Baixa:** odd não verificada ou antiga, dúvida sobre regras ou notícias, ou preço justo sem Pinnacle nem casas suficientes. **Não entra no plano.**

## Formato da resposta, por candidata
```
CANDIDATA [item N da varredura]
Veredicto: APROVAR | REJEITAR
Jogo/evento (data e hora de Lisboa) e competição:
Mercado e seleção · melhor odd (casa, idade) · preço justo (fonte):
Porque é que a odd está acima do justo:
Armadilhas verificadas (1–5 acima): o que viste em cada uma
Ajuste (pp) e facto que o justifica (fonte, hora): 0 | ±x
Probabilidade final:
Confiança (alta/média/baixa) e porquê:
Justificação (2–4 frases, com fontes):
O que invalidaria a aposta (para a verificação pré-jogo):

--- Análise profissional (contexto, não substitui o preço) ---
Confronto direto: resultados anteriores entre os dois lados, e em que superfície/condições.
Forma recente: últimos 5–8 jogos, onde jogaram na última semana (fadiga, viagem, fuso horário).
Estatísticas relevantes: as do desporto (ver os ficheiros de cada analista) — quando existirem e tiverem fonte.
Mercados secundários (totais, handicap, sets/tempos, etc.): para cada um, ou uma odd real de mercado com a
  casa e a fonte (e nesse caso passa pelas mesmas regras de valor e vai para o gestor de risco como candidata
  própria), ou, sem odd real, a tua leitura como informação — sempre rotulada "sem odd de mercado — não é aposta".
```
Se não houver candidatas do teu desporto: `SEM CANDIDATAS` e o motivo em 1–2 frases.

**Nunca inventes uma odd para simular um mercado secundário.** Sem odd real, a leitura fica só como informação;
só o preço mínimo real vira aposta.
