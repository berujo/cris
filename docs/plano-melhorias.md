# Plano de melhorias: lucro a longo prazo

**Objetivo:** o agente deixa de tentar adivinhar resultados melhor do que o mercado e passa a procurar preços. Aposta quando uma casa paga acima do preço justo da Pinnacle, e cada recomendação é avaliada pelo CLV (valor face à odd de fecho).

**Porquê (evidência):**
- Nos estudos de 2026, os LLMs não bateram o mercado:
  - No Mundial 2026, nenhum de quatro LLMs bateu a precisão das odds, e o Claude perdeu 18%.
  - No KellyBench, todos os modelos perderam dinheiro, e o melhor ficou em −8%.
- A nossa regra atual, aplicada às previsões desses LLMs, deu cerca de +1% em 91 apostas, o que é puro ruído.
- A estratégia de preço (Kaunitz et al.) foi lucrativa em 10 anos de dados e com dinheiro real.
- O CLV dá sinal ao fim de cerca de 35 apostas. Pelo lucro, seriam precisas milhares.

Estado: ✅ feito · ⏳ à espera de ti · ❌ bloqueado

## Fase 0 — Pré-requisitos (do teu lado)
- ⏳ Abrir a rede do ambiente (acesso total, ou os domínios de `docs/apis.md`).
- ⏳ Variável de ambiente `ODDS_API_KEY` (chave gratuita em the-odds-api.com).
- ⏳ Dizer em que casas tens conta, para comparar odds entre elas; fica em `casas` no `dados/config.json`.
- Opcional: um plano pago da The Odds API, se quiseres mais de 2 ou 3 verificações de valor por dia.

## Fase 1 — Medir: CLV e calibração ✅
1. `dados/recomendacoes.csv`: todas as recomendações ficam registadas, mesmo as que não apostas. Cada uma guarda o id do evento, a hora de início, a odd, o preço justo e a probabilidade final.
2. `banca.py recomendar`, e novas colunas em `apostas.csv`: `casa`, `ref` (ligação à recomendação) e `prob_fecho`.
3. `odds.py fecho`: guarda a probabilidade justa da Pinnacle perto do início do jogo (fecho).
4. `odds.py resultados`: liquida as recomendações com a API de resultados.
5. `banca.py avaliacao`: mostra o CLV médio, a percentagem de apostas com CLV positivo, o ROI em papel e a calibração (Brier do agente contra o do mercado). Mostra também se os ajustes do agente acrescentam valor e aplica a **regra de paragem**: se o CLV médio for ≤ 0 ao fim de 100 recomendações com fecho, pára-se e revê-se.
6. As métricas das tuas apostas passam a mostrar o CLV médio.

## Fase 2 — Motor de preço ✅
1. Tirar a margem com o **método de Shin** em vez do método proporcional, porque corrige o viés favorito–azarão.
2. `odds.py valor`: varre as competições com jogos (o calendário da API é gratuito, só as odds gastam créditos). Por seleção mostra:
   - o preço justo da Pinnacle;
   - a melhor odd e a casa;
   - o EV;
   - a **odd mínima** para as tuas casas;
   - a idade da odd;
   - o movimento desde a última varredura.
3. `dados/config.json` passa a ter:
   - EV mínimo de 3% contra a Pinnacle e de 5% quando não há Pinnacle (preço de consenso);
   - ajuste máximo do agente de 3 pontos percentuais;
   - as competições, incluindo ligas secundárias;
   - as tuas casas;
   - as casas excluídas (exchanges);
   - uma reserva mínima de créditos da API.

## Fase 3 — Regras e agentes ✅
1. `CLAUDE.md`: novos filtros, CLV como métrica principal, regra de paragem, não reforçar a banca e distribuir as apostas pelas casas.
2. `docs/comum.md`: o método passa a ser "preço primeiro". O LLM é um filtro e não gera probabilidades.
3. Os analistas passam de gerar apostas a filtrá-las. Procuram armadilhas:
   - odd desatualizada;
   - regras de liquidação diferentes entre casas (ex.: desistências no ténis);
   - notícias que expliquem a diferença de preço;
   - correlação entre apostas.
4. `estatistica-dados`: faz a varredura de valor, compara as promoções das casas portuguesas (SuperOdds, Power Odds, boosts), recolhe o fecho e os resultados, e corre a avaliação.
5. `gestao-risco`: aplica os novos limiares, verifica a idade da odd e a regra de paragem.
6. `gestao-banca`: regista as recomendações e mostra o CLV.
7. Skills: `plano-diario` com o fluxo novo, `resultado` com a referência, a casa e o registo antes do jogo, e uma skill nova, `pre-jogo`.

## Fase 4 — Horários ✅
1. Manter o plano às 00:00 de Lisboa.
2. Nova Routine de atualização às 12:00 e às 18:00 de Lisboa: nova varredura, notícias e fecho.
3. Verificação **pré-jogo** 40 minutos antes de cada recomendação, agendada automaticamente pelo plano. Recolhe o fecho, confirma onzes e lesões, dá o veredicto e envia uma notificação.

## Fase 5 — Modelos e testes com histórico ✅ (o ponto 4 está ⏳, à espera da rede)
1. `scripts/backtest.py` com dados históricos reais, já acessíveis pelo GitHub:
   - **Ténis ATP 2010–2018** (Pinnacle e outras casas): a estratégia de preço, por limiar, e um Elo por superfície contra a Pinnacle.
   - **Futebol 2005–2026** (Bet365, máximas de cerca de 17 casas e Elo): o Elo contra o mercado, e o valor nas odds máximas.
2. Relatório em `docs/backtest.md`. Os limiares da Fase 2 são revistos com estes resultados.
   **Resultado:**
   - O Elo perde para o mercado nos dois desportos, por isso nenhum modelo próprio entra no processo.
   - Apostar na melhor odd acima do preço justo deu lucro significativo: +2,4% a +5,1% no futebol e +4,1% a +16,4% no ténis.
   - Uma só casa mole acima da Pinnacle não se confirmou: é preciso ter várias contas.
   - Os limiares de 3% e 5% mantêm-se.
3. Regra: um modelo só entra no processo se melhorar a log-loss do mercado fora da amostra e as apostas que gera tiverem ROI positivo em pelo menos 1000 apostas.
4. Quando a rede abrir: repetir com football-data.co.uk (que tem a odd de fecho da Pinnacle) e com tennis-data.co.uk até 2026.

## Fase 6 — Validação ✅
Testes automáticos, uma simulação de um dia completo com dados de exemplo, a documentação, o commit e o push.

## Fase 7 — Pesquisa de 25/09/2026 ✅ (relatório: `reports/Melhorias do agente de apostas.md`)
Pesquisa em 7 frentes (preço justo sem Pinnacle e CLV, mercados secundários do ténis, ineficiências do ténis, regras de desistência das casas portuguesas, Kelly com várias apostas, fontes acessíveis, LLMs e práticas em Portugal). Notas em `research_notes/Melhorias do agente de apostas/`. Aplicado:
1. **CLV no caminho do consenso:** cada leitura do tennisexplorer fica em `dados/consenso.json`; o `odds.py fecho` usa a última recolha posterior à recomendação e anterior ao início, com a antecedência (≤ 2 h boa; > 6 h não medido) e o movimento do consenso (M). Antes, este caminho nunca media o CLV e a regra de paragem não podia disparar.
2. **Odd mínima contra o consenso:** max(5%, 0,02/(p − 0,02)) (Kaunitz), + 2 pp com recolha velha (> 3 h) ou longe do início (> 12 h), + 1 pp nos azarões dos Challengers; ITF e exibições de fora. Preço justo do consenso pelo pior caso entre Shin e potência.
3. **Stake sobre o EV calibrado:** EV_cal = a + k·EV_aparente, com prior k = 0,5 (consenso) ou 0,7 (Pinnacle), atualizado pela regressão do CLV sobre o EV (peso n/(n + 50)). Com o 1/4 de Kelly sobre o EV aparente, a probabilidade de chegar ao stop-loss era ~9%; assim fica perto de 1%.
4. **Filtros determinísticos:** EV > 15% só com `--confirmado`; uma só casa acima da mínima exige o dobro do EV; ajuste positivo dos subagentes desligado; uma aposta por jogo; ⚠ quando o consenso anda ≥ 5 pp para o azarão; teto de exposição opcional (`teto_exposicao_pct`, desligado pela regra 10).
5. **Medição:** registos-sombra (odds vistas nas casas, para medir a cobertura), stake 0 registada para o CLV, avaliação com IC 95%, segmentos (circuito, lado, casa, fonte do fecho) e parte do EV confirmada.
6. **Ténis:** `odds.py mercados` (sets, "ganha um set", total e handicap de jogos) com um modelo de pontos corrigido (σ = 0,065; testado em 8 596 encontros ATP); `odds.py ev` para odds aumentadas e freebets; freebets na banca; tabela de regras de desistência e fórmula p_PT em `docs/comum.md`.
7. **Agentes e fontes:** perguntas fechadas, ângulos (fadiga, jet lag, calor, motivação) só como razão para rejeitar, `docs/apis.md` corrigido.

Por decidir pelo utilizador: ligar o teto de exposição (25% = 5 € numa banca de 20 €); a faixa de odds para freebets.

## Depois de implementado: como avaliar
- **Semanas 1–4:** o plano gera recomendações e registo-as todas, mesmo que não apostes. Se apostares, que seja com as stakes mínimas. O objetivo é ter CLV médio acima de 0.
- **Ao fim de 100 recomendações com fecho:** decidir se se continua ou se revê o método, pela regra de paragem.
- **Não reforçar a banca** antes de haver pelo menos 200 apostas com CLV positivo. Se as casas limitarem a conta, distribuir as apostas pelas outras.
