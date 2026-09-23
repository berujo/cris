# Analista de apostas desportivas

Agente de IA para Claude Code que analisa futebol, ténis, NBA e basebol, sugere apostas com valor esperado positivo e gere a banca (inicial: 20 €). O orquestrador é o `CLAUDE.md`; os subagentes estão em `.claude/agents/`:

| Subagente | Função |
|---|---|
| `analista-futebol`, `analista-tenis`, `analista-nba`, `analista-basebol` | Candidatas por desporto |
| `estatistica-dados` | Odds, probabilidades justas, validação, histórico |
| `noticias-lesoes` | Lesões, suspensões, onzes, meteorologia |
| `gestao-risco` | Filtros, correlação, múltiplas, live, "não apostar" |
| `gestao-banca` | Stop-loss, stakes (1/4 Kelly, teto de 10%), registo, métricas |

## Uso
- Plano do dia: `/plano-diario` (também corre sozinho todos os dias às 10:00 de Lisboa).
- Comunicar resultados em linguagem natural, ex.: "24/09 #1 ganhei, apostei 0,70 €, lucro 0,77 €" (skill `/resultado`).
- Métricas: `python3 scripts/banca.py metricas`.
- Testes: `python3 -m unittest discover -s tests`.

## Dados
- Regras numéricas: `dados/config.json`. Registo de apostas: `dados/apostas.csv`. Planos: `planos/`.
- Odds: `scripts/odds.py` usa a [The Odds API](https://the-odds-api.com) (chave gratuita, 500 créditos/mês) através da variável de ambiente `ODDS_API_KEY`.
- No ambiente cloud, a rede tem de permitir `api.the-odds-api.com`, `site.api.espn.com` e `statsapi.mlb.com`. Sem isso, o agente usa só a pesquisa web.

Nenhuma aposta é garantida. Aposta só o que podes perder. +18.
