# Analista de apostas desportivas

Agente de IA para Claude Code que analisa futebol, ténis, basquetebol (NBA e WNBA) e basebol e gere uma banca inicial de 20 €. Usa o método "preço primeiro": só recomenda quando uma casa paga acima do preço justo da Pinnacle (sem margem, pelo método de Shin). Mede-se pelo CLV, e não pelo instinto do LLM. As razões estão em `docs/plano-melhorias.md` e os testes com histórico em `docs/backtest.md`.

O orquestrador é o `CLAUDE.md`. Os subagentes estão em `.claude/agents/`:

| Subagente | Função |
|---|---|
| `estatistica-dados` | Varredura de valor, promoções, fecho, resultados, CLV e calibração |
| `analista-futebol`, `analista-tenis`, `analista-nba`, `analista-basebol` | Filtram as candidatas do seu desporto: valor real ou armadilha |
| `noticias-lesoes` | Lesões, suspensões, onzes, meteorologia; verificação pré-jogo |
| `gestao-risco` | Filtros, correlação, múltiplas, live, stop-loss, regra de paragem |
| `gestao-banca` | Regista recomendações e apostas; stakes a 1/4 Kelly com teto de 10%; métricas |

## Uso
- **Plano:** `/plano-diario`. Corre sozinho às 00:00 de Lisboa, com atualizações às 12:00 e às 18:00.
- **Pré-jogo:** `/pre-jogo REF`. É agendado sozinho 40 minutos antes de cada recomendação, para guardar a odd de fecho e confirmar onzes e lesões.
- **Apostas e resultados:** em linguagem natural (skill `/resultado`). Por exemplo: "apostei na 25/09 #1, 0,20 € a 2,15 na Betano" e depois "ganhou".
- **Métricas:**
  - `python3 scripts/banca.py metricas`: as tuas apostas (lucro, ROI, yield, acerto, CLV, evolução).
  - `python3 scripts/banca.py avaliacao`: o agente (CLV, calibração e regra de paragem).
- **Testes:** `python3 -m unittest discover -s tests`. Os testes do backtest precisam de `pip install -r requirements-backtest.txt`.

## Scripts
- **`scripts/odds.py`:**
  - `valor` varre as competições de `config.json` com jogos;
  - `odds` mostra o detalhe de uma competição;
  - `fecho` guarda a odd de fecho;
  - `resultados` liquida as recomendações;
  - `desportos` lista as competições ativas;
  - `fontes` mostra que fontes estão acessíveis agora;
  - `alvos` lê as fontes do GitHub (ténis e futebol, com a Pinnacle) e dá a odd mínima a procurar nas tuas casas.
- **`scripts/banca.py`:**
  - `estado`, `stake`, `metricas` e `avaliacao`;
  - `recomendar` aplica as regras em código e recusa o que as violar;
  - `registar` e `resultado` registam as apostas.
- **`scripts/backtest.py`:** testes com histórico real (ténis e futebol).

## Dados e configuração
- **Configuração:** `dados/config.json` tem as regras, os limiares, as competições e as tuas casas.
- **Registos:**
  - `dados/apostas.csv`: as tuas apostas;
  - `dados/recomendacoes.csv`: todas as recomendações;
  - `dados/varredura.json`: a última varredura;
  - `planos/`: os planos diários.
- **Odds:** a [The Odds API](https://the-odds-api.com) (chave gratuita de 500 créditos por mês), através da variável `ODDS_API_KEY`. A lista de jogos é gratuita; só se pedem odds onde há jogos. Há outras APIs em `docs/apis.md`.
- **Rede do ambiente cloud:** tem de permitir estes domínios, ou ter acesso total. Sem isso não há odds, e o plano é "não apostar".

Nenhuma aposta é garantida. Aposta só o que podes perder. +18.
