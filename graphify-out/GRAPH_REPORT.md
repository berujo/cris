# Graph Report - cris  (2026-09-25)

## Corpus Check
- 36 files · ~76,335 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .csv 2)

## Summary
- 601 nodes · 1161 edges · 35 communities (31 shown, 4 thin omitted)
- Extraction: 91% EXTRACTED · 8% INFERRED · 1% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.81)
- Token cost: 464,595 input · 0 output

## Community Hubs (Navigation)
- Regras e agentes
- Fontes e alvos diários
- Memória e plano de melhorias
- Backtest histórico
- Modelo de pontos (tenis.py)
- Teoria dos mercados secundários
- Fontes de fecho e CLV
- Preço justo sem Pinnacle
- Fecho e API de odds
- LLMs em apostas
- Regras de desistência
- Alvos, avaliação e calibração
- Testes da banca
- Núcleo da banca
- Eficiência do mercado de ténis
- Suite de testes
- Catálogo de APIs
- Recomendação e regra de paragem
- Kelly com incerteza
- Testes das fontes GitHub
- Viés favorito-azarão
- Maldição do vencedor
- Kelly simultâneo
- Line shopping e limitação
- Teste do dia completo
- Testes do consenso
- Cálculo e validação da stake
- Promoções e fiscalidade PT
- Estatísticas do CLV
- Limiares de EV
- Métricas das apostas
- Testes de odds
- Taxas de desistência
- Testes do backtest
- Testes dos mercados

## God Nodes (most connected - your core abstractions)
1. `CLAUDE.md (orquestrador)` - 35 edges
2. `Medir primeiro, apostar menos e melhor (relatorio de melhorias)` - 33 edges
3. `Preço justo de mercados secundários de ténis a partir da odd do vencedor` - 25 edges
4. `docs/comum.md` - 24 edges
5. `README: Analista de apostas desportivas` - 21 edges
6. `docs/apis.md` - 20 edges
7. `Preço justo a partir da média das casas e CLV com snapshots de consenso` - 20 edges
8. `cmd_alvos()` - 19 edges
9. `Skill plano-diario` - 19 edges
10. `Subagente gestao-risco` - 18 edges

## Surprising Connections (you probably didn't know these)
- `dist_mercado() (implementação de referência stdlib)` --semantically_similar_to--> `cmd_mercados()`  [AMBIGUOUS] [semantically similar]
  research_notes/Melhorias do agente de apostas/mercados_secundarios.md → scripts/odds.py
- `Calibracao do EV por regressao CLV ~ EV aparente` --semantically_similar_to--> `calibracao()`  [INFERRED] [semantically similar]
  research_notes/Melhorias do agente de apostas/kelly_selecao_adversa.md → scripts/banca.py
- `penaltyblog (PyPI)` --semantically_similar_to--> `shin()`  [INFERRED] [semantically similar]
  research_notes/Melhorias do agente de apostas/fontes_dados.md → scripts/odds.py
- `Método da potência (power)` --semantically_similar_to--> `potencia()`  [INFERRED] [semantically similar]
  research_notes/Melhorias do agente de apostas/preco_justo_clv.md → scripts/odds.py
- `Teto total de exposicao de 25% da banca (1/4 x 100%)` --conceptually_related_to--> `em_jogo()`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/kelly_selecao_adversa.md → scripts/banca.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Pipeline do plano diário (varredura → analistas → notícias → validação → risco → banca)** — _claude_skills_plano_diario_skill, _claude_agents_estatistica_dados, _claude_agents_analista_futebol, _claude_agents_analista_tenis, _claude_agents_analista_nba, _claude_agents_analista_basebol, _claude_agents_noticias_lesoes, _claude_agents_gestao_risco, _claude_agents_gestao_banca [EXTRACTED 1.00]
- **Analistas por desporto como filtros (docs/comum.md, APROVAR/REJEITAR)** — _claude_agents_analista_futebol, _claude_agents_analista_tenis, _claude_agents_analista_nba, _claude_agents_analista_basebol, docs_comum, claude_ajuste_maximo_3pp [EXTRACTED 1.00]
- **Medição do agente pelo CLV (fecho, registo, avaliação, regra de paragem)** — claude_clv, _claude_skills_pre_jogo_skill, _claude_skills_resultado_skill, scripts_odds, scripts_banca, dados_recomendacoes, claude_regra_de_paragem [INFERRED 0.85]
- **Evidencia de que LLMs/modelos nao batem o mercado -> LLM como veto** — docs_backtest_fifa2026llm, reports_melhorias_do_agente_de_apostas_kellybench, reports_melhorias_do_agente_de_apostas_belief_to_trade, reports_melhorias_do_agente_de_apostas_wilkens_2021, reports_melhorias_do_agente_de_apostas_kovalchik_2016, docs_backtest_modelos_proprios_perdem, reports_melhorias_do_agente_de_apostas_subagentes_como_veto, docs_comum_filtro_nao_adivinho [INFERRED 0.85]
- **Caminho do consenso: odd minima Kaunitz, EV calibrado, CLV por movimento M** — reports_melhorias_do_agente_de_apostas_limiar_consenso_kaunitz, reports_melhorias_do_agente_de_apostas_vantagem_56_pct, reports_melhorias_do_agente_de_apostas_ev_calibrado, reports_melhorias_do_agente_de_apostas_identidade_clv_consenso, reports_melhorias_do_agente_de_apostas_serie_consensos_git, docs_plano_melhorias_fase_7, docs_comum_odd_minima [EXTRACTED 1.00]
- **Fontes de dados acessiveis via GitHub (sem Pinnacle publica)** — docs_apis_mriganka_codes_tennis_data, docs_apis_aimidas1_pinnacle_bet365_odds_data, docs_apis_char2mant_futbol_veri_aynasi, docs_apis_aneeshers_tennis_sackmann_archive, docs_apis_pinnacle_fora_das_fontes_publicas, docs_apis_regra_fontes_acessiveis [EXTRACTED 1.00]
- **Fontes de fecho para CLV em 2026 sem Pinnacle** — research_notes_melhorias_do_agente_de_apostas_fontes_dados_char2mant_futbol_veri_aynasi, research_notes_melhorias_do_agente_de_apostas_fontes_dados_tennis_data_co_uk, research_notes_melhorias_do_agente_de_apostas_fontes_dados_fecho_betfair_exchange, research_notes_melhorias_do_agente_de_apostas_fontes_dados_huhao_football_odds_mirror [EXTRACTED 1.00]
- **Pipeline de preço de mercados secundários de ténis (Shin → calibração L,d → mistura → mercados)** — research_notes_melhorias_do_agente_de_apostas_mercados_secundarios_calibracao_nivel_diferenca, research_notes_melhorias_do_agente_de_apostas_mercados_secundarios_nivel_l_spw, research_notes_melhorias_do_agente_de_apostas_mercados_secundarios_mistura_normal_diferenca_servico, research_notes_melhorias_do_agente_de_apostas_mercados_secundarios_dist_mercado, research_notes_melhorias_do_agente_de_apostas_mercados_secundarios_dist_encontro, scripts_odds_shin [EXTRACTED 1.00]
- **Famílias de regras de desistência no ténis** — research_notes_melhorias_do_agente_de_apostas_regras_desistencia_regra_encontro_tem_de_acabar, research_notes_melhorias_do_agente_de_apostas_regras_desistencia_regra_um_set, research_notes_melhorias_do_agente_de_apostas_regras_desistencia_regra_primeira_bola, research_notes_melhorias_do_agente_de_apostas_regras_desistencia_ajuste_desistencia_assimetrica [EXTRACTED 1.00]
- **Tennis favourite-longshot bias evidence** — research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_favourite_longshot_bias, research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_forrest_mchale_2007, research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_lahvicka_2014, research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_abinzano_muga_santamaria, research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_casco_normalization, research_notes_melhorias_do_agente_de_apostas_ineficiencias_tenis_whelan_2024 [EXTRACTED 1.00]
- **Recommended calcular_stake pipeline (calibrate, 1/4 Kelly, caps, rounding)** — research_notes_melhorias_do_agente_de_apostas_kelly_selecao_adversa_ordem_calcular_stake, research_notes_melhorias_do_agente_de_apostas_kelly_selecao_adversa_calibracao_clv_ev, research_notes_melhorias_do_agente_de_apostas_kelly_selecao_adversa_teto_exposicao_25, research_notes_melhorias_do_agente_de_apostas_kelly_selecao_adversa_arredondamento_stake_minima, research_notes_melhorias_do_agente_de_apostas_kelly_selecao_adversa_kelly_incerteza_parametro [EXTRACTED 1.00]
- **2025-2026 LLM vs market forecasting benchmarks** — research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_kellybench, research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_wc2026_agents, research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_llm_soccerarena, research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_kalshibench, research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_belief_to_trade_layer, research_notes_melhorias_do_agente_de_apostas_llm_e_praticas_prophet_arena [INFERRED 0.85]

## Communities (35 total, 4 thin omitted)

### Community 0 - "Regras e agentes"
Cohesion: 0.09
Nodes (58): Subagente analista-basebol, Troca de lançador titular (action vs listed pitchers), Subagente analista-futebol, Liquidação aos 90 minutos e linhas asiáticas, Subagente analista-nba (NBA/WNBA), Relatório de lesões e gestão de esforço tardia, Subagente analista-tenis, Alerta ⚠ de movimento ≥5 pp para o azarão (+50 more)

### Community 1 - "Fontes e alvos diários"
Cohesion: 0.05
Nodes (50): collections, dados/consenso.json, aimidas1/pinnacle_bet365_odds_data, Mriganka-codes/tennis_data (tennisexplorer consensus), Formato da resposta por candidata + analise profissional, Niveis de confianca (alta/media/baixa), Erro de fonte: Blanch em Genova e San Diego, Historico 23-25/09/2026 (+42 more)

### Community 2 - "Memória e plano de melhorias"
Cohesion: 0.06
Nodes (51): graphuofm/FIFA2026LLM (LLMs no Mundial 2026), Limitacoes do backtest, Ajuste so para baixo (<=3 pp), Papel do analista: filtro, nao adivinho, Formula p_PT(A) = (p_ref(A) - r_B)/(1 - r_A - r_B), Formulas de EV e odd minima, Tabela de regras de desistencia e adiamento (tenis), Memoria do projeto (+43 more)

### Community 3 - "Backtest histórico"
Cohesion: 0.08
Nodes (38): docs/backtest.md, edouardthom/ATPBetting (ATP 2004-2018 com Pinnacle), Uma so casa mole nao confirma lucro, xgabora/Club-Football-Match-Data-2000-2025, Limiares EV 3% (Pinnacle) / 5% (media), Estrategia: melhor odd acima do preco justo, Modelos proprios (Elo) perdem para o mercado, Fase 5 - Modelos e testes com historico (+30 more)

### Community 4 - "Modelo de pontos (tenis.py)"
Cohesion: 0.09
Nodes (28): functools, cmd_mercados(), Preço justo dos mercados secundários do ténis (sets, total e handicap de…, bissecao(), cobre(), dist_encontro(), ds(), dist_set() (+20 more)

### Community 5 - "Teoria dos mercados secundários"
Cohesion: 0.14
Nodes (26): Tennismylife/TML-Database, Preço justo de mercados secundários de ténis a partir da odd do vencedor, Barnett & Clarke (2005) Combining player statistics, Resolução conjunta (L, d) com a linha de total da Pinnacle, Calibração ao mercado: fixar nível L, resolver diferença d por bisseção, Depken, Gandar & Shapiro (2022) momentum ao nível do set, dist_encontro(), dist_mercado() (implementação de referência stdlib) (+18 more)

### Community 6 - "Fontes de fecho e CLV"
Cohesion: 0.10
Nodes (24): Fontes de dados de ténis e futebol (rede restrita), Verificação de acesso da rede (raw.githubusercontent, PyPI permitidos; Kaggle/HF/football-data bloqueados), aimidas1/pinnacle_bet365_odds_data, Aneeshers/tennis-sackmann-archive, Char2mant/futbol-veri-aynasi (espelho football-data 2026/27), edouardthom/ATPBetting (tennis-data até 2018), Eth91/tennis-odds-collector, Fecho da API pública da Pinnacle (2025) (+16 more)

### Community 7 - "Preço justo sem Pinnacle"
Cohesion: 0.14
Nodes (22): Limiar de EV reforçado sem mercado Pinnacle (≥8% sets, ≥10% 2-1/1-2, ≥6% totais/handicap), Preço justo a partir da média das casas e CLV com snapshots de consenso, arXiv 2604.17194 (2026) OO-EPC, Buchdahl: CLV prevê ROI quase 1:1, Buffer aditivo α em probabilidade (regra Kaunitz), Clarke, Kovalchik & Ingram (2017) Adjusting bookmaker's odds, Fórmula do CLV e do erro-padrão (SE = s/√n, n ≈ (2s/m)²), DataGolf: 95–100% do peso na Pinnacle (+14 more)

### Community 8 - "Fecho e API de odds"
Cohesion: 0.17
Nodes (19): config(), escrever(), pct(), analisar(), cmd_ev(), cmd_fecho(), cmd_odds(), cmd_resultados() (+11 more)

### Community 9 - "LLMs em apostas"
Cohesion: 0.15
Nodes (18): AI World Cup 2026 (arXiv 2608.03416), Beyond Forecasting: The Belief-to-Trade Layer (Raven-Agent), Separar crenca de decisao: stake e risco deterministicos, ForecastBench (FRI), KalshiBench (arXiv 2512.16030) LLM overconfidence, KellyBench (General Reasoning, 2026), LLM como filtro e extrator de factos (nao gera probabilidades), LLMs em apostas desportivas e praticas para banca pequena em Portugal (+10 more)

### Community 10 - "Regras de desistência"
Cohesion: 0.25
Nodes (18): Regras de liquidação no ténis (desistência, walkover, adiamento): casas PT vs internacionais, Ajuste do EV por risco de desistência assimétrico, bet365 — regras de ténis, Betano PT (regras de ténis), Betclic PT (regras de ténis), Betfair Exchange/Sportsbook — regras de ténis, Erro manifesto de odds (palpable error), Kambi / Unibet — regras de ténis (+10 more)

### Community 11 - "Alvos, avaliação e calibração"
Cohesion: 0.15
Nodes (16): calibracao(), cmd_avaliacao(), cmd_stake(), cobertura(), eur(), grupo_fonte(), ler(), (k, a, n): a stake usa o EV calibrado EV_cal = a + k·EV_aparente, não o EV… (+8 more)

### Community 12 - "Testes da banca"
Cohesion: 0.15
Nodes (5): aposta(), Melhorias de 25/09/2026 — ver reports/Melhorias do agente de apostas.md., rec(), TestBanca, TestLimiaresEStakes

### Community 13 - "Núcleo da banca"
Cohesion: 0.22
Nodes (15): csv, ativo(), banca(), carregar(), cmd_registar(), cmd_resultado(), gravar(), hoje() (+7 more)

### Community 14 - "Eficiência do mercado de ténis"
Cohesion: 0.15
Nodes (16): Angelini, Candila & De Angelis (2022) Weighted Elo (WElo), Bet timing rule: bet as soon as soft price >= minimum odds, Buchdahl: How efficient is the tennis betting market (68,361 matches), Fatigue effects on next-match win probability, Tennis market inefficiencies and bet timing (evidence review), Intransitive matchups GNN preprint (arXiv 2510.20454), Koning (2011) home advantage in tennis, Kovalchik (2016) Searching for the GOAT of tennis win prediction (+8 more)

### Community 15 - "Suite de testes"
Cohesion: 0.18
Nodes (11): argparse, contextlib, datetime, io, json, pathlib, shutil, sys (+3 more)

### Community 16 - "Catálogo de APIs"
Cohesion: 0.15
Nodes (14): docs/apis.md, Aneeshers/tennis-sackmann-archive, Char2mant/futbol-veri-aynasi (football-data mirror), ESPN API (nao oficial), Fontes a nao usar (proofodds, Eth91), JeffSackmann/tennis_MatchChartingProject, jriordan55/mlb_pbp_model (stale), MLB Stats API (+6 more)

### Community 17 - "Recomendação e regra de paragem"
Cohesion: 0.19
Nodes (14): ajuste_positivo_permitido(), brier(), cmd_estado(), cmd_recomendar(), em_jogo(), guardar_rec(), limite_stop_loss(), Recomendações que contam para o CLV e para a regra de paragem (sem os registos-… (+6 more)

### Community 18 - "Kelly com incerteza"
Cohesion: 0.17
Nodes (13): Arredondamento para baixo e stake minima de 0,10 EUR, Baker & McHale (2013) Optimal betting under parameter uncertainty, Busseti, Ryu & Boyd, Risk-Constrained Kelly Gambling, Calibracao do EV por regressao CLV ~ EV aparente, Chu, Wu & Swartz (2018) Modified Kelly criteria, Probabilidade de drawdown x^(2/c-1) com Kelly fracionado, Kelly com incerteza no parametro (contracao), MacLean, Thorp & Ziemba, Good and bad properties of the Kelly criterion (+5 more)

### Community 19 - "Testes das fontes GitHub"
Cohesion: 0.20
Nodes (4): Um .xlsx mínimo (strings partilhadas), feito só com a biblioteca padrão., Alvos a partir das fontes no GitHub (ténis do tennisexplorer; futebol com…, TestFontesGithub, xlsx()

### Community 20 - "Viés favorito-azarão"
Cohesion: 0.22
Nodes (10): Abinzano, Muga & Santamaria (2016, 2019) FLB on tennis exchanges, CaSco normalization (Candila & Scognamillo), Data-snooping bias in betting rules, Favourite-longshot bias in tennis, Forrest & McHale (2007) Anyone for tennis betting, Lahvicka (2014) What causes the FLB? tennis, Lyocsa & Vyrost (2018) reality check for tennis betting efficiency, Ramirez, Reade & Singleton (2023) WTA buzz mispricing (overturned) (+2 more)

### Community 21 - "Maldição do vencedor"
Cohesion: 0.24
Nodes (10): Forrest & McHale (2019) Using statistics to detect match fixing, IBIA 2025 annual report (suspicious betting alerts), Higher EV threshold and lower stake for ITF/Challenger, ITIA match alerts / quarterly updates, Match-fixing risk in low tiers, Correcao bayesiana EV_real = mu0 + k(EV_ap - mu0), EV robusto com a 2.a melhor odd (outlier de uma so casa), Maldicao do vencedor / selecao adversa na melhor odd (+2 more)

### Community 22 - "Kelly simultâneo"
Cohesion: 0.31
Nodes (9): Buchdahl, The Real Kelly Criterion (Pinnacle), Grant & Buchen (2013) comparison of simultaneous Kelly strategies, Heuristica de forum: stake x produto(1-kj), Kelly simultaneo (muitas apostas independentes), Algoritmo kelly_simultaneo (descida por coordenadas em grelha), Long (2026) Optimal Parlay Wagering and Whitrow Asymptotics, Tepelyan & Lam (2026) multivariate Kelly in O(N), Thorp (2006) The Kelly Criterion in Blackjack, Sports Betting and the Stock Market (+1 more)

### Community 23 - "Line shopping e limitação"
Cohesion: 0.25
Nodes (8): Line shopping (best odds across bookmakers), Wilkens (2021) ML tennis prediction, market embeds information, Buchdahl, Wisdom of the Crowd (31 247 apostas, ~3,6% ROI), Kaunitz, Zhong & Kreiner (2017) Beating the bookies with their own numbers, Clausula de limitacao da Betclic (odds < 1,40), Kaunitz, Zhong & Kreiner (2017) Beating the bookies, Limitacao de contas em Portugal, Orientacao n.o 1/2017/SRIJ/JO (limites de apostas)

### Community 24 - "Teste do dia completo"
Cohesion: 0.29
Nodes (4): evento(), Varredura → recomendação → aposta → fecho → resultado → avaliação, com uma API…, TestDiaCompleto, pedir()

### Community 26 - "Cálculo e validação da stake"
Cohesion: 0.33
Nodes (7): Stakes com apostas simultaneas, incerteza e maldicao do vencedor, arredondar(), calcular_stake(), Arredonda para baixo ao passo de config; abaixo da stake mínima, 0., Kelly fracionado sobre o EV calibrado, com teto, arredondado para baixo.…, Aplica as regras a uma recomendação. Devolve (stake, motivo da recusa ou None);…, validar()

### Community 27 - "Promoções e fiscalidade PT"
Cohesion: 0.29
Nodes (7): EV de freebet sem hedge (bolsas ilegais em Portugal), IEJO 8% sobre o volume das apostas, Placard (Santa Casa, imposto do selo), Promocoes nas casas portuguesas (SuperOdds, Boost, Power Odds, freebets), Proposta de tributacao IRS de ganhos > 500 EUR (nov/2025), RJO (Decreto-Lei 66/2015), Solverde Power Odds com margem zero no 1X2

### Community 28 - "Estatísticas do CLV"
Cohesion: 0.33
Nodes (7): circuito(), estat(), media_ic(), qualidade_clv(), (média, desvio-padrão, erro-padrão) de uma amostra., +4,2% ± 1,9% em 34' (intervalo de confiança de 95%)., Detalhe do CLV das recomendações com fecho: intervalo de confiança, fonte do…

### Community 29 - "Limiares de EV"
Cohesion: 0.33
Nodes (7): data_utc(), ev_minimo(), idade_horas(), minimo_de(), EV mínimo (fração) para uma seleção. Ver 'Filtros' em CLAUDE.md. - Pinnacle:…, Horas desde a recolha do preço justo (ISO em UTC), ou None se não se souber., EV mínimo de uma recomendação (linha de recomendacoes.csv).

### Community 30 - "Métricas das apostas"
Cohesion: 0.33
Nodes (6): clv(), cmd_metricas(), linha_clv(), Valor da odd apostada face à probabilidade justa no fecho., (n, apostado, lucro, yield, acerto) — nulas não contam para o volume nem para o…, resumo()

### Community 32 - "Taxas de desistência"
Cohesion: 0.40
Nodes (5): Oliver et al. (2024) retirements in ATP/WTA tour events, PLOS One (2024) retirements in Challenger/ITF, Bookmaker retirement settlement rules, Retirement and walkover base rates, Smith et al. (2018) heat and medical events at Australian Open

## Ambiguous Edges - Review These
- `em_jogo()` → `Teto total de exposicao de 25% da banca (1/4 x 100%)`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/kelly_selecao_adversa.md · relation: conceptually_related_to
- `cmd_mercados()` → `dist_mercado() (implementação de referência stdlib)`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/mercados_secundarios.md · relation: semantically_similar_to
- `fecho_github()` → `Char2mant/futbol-veri-aynasi (espelho football-data 2026/27)`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/fontes_dados.md · relation: shares_data_with
- `Regra 'o encontro tem de acabar / nula salvo se determinado'` → `William Hill — regras de ténis`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/regras_desistencia.md · relation: implements
- `Regra '1 set completo + jogador que avança'` → `Kambi / Unibet — regras de ténis`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/regras_desistencia.md · relation: implements
- `Regra '1 set completo + jogador que avança'` → `William Hill — regras de ténis`  [AMBIGUOUS]
  research_notes/Melhorias do agente de apostas/regras_desistencia.md · relation: implements

## Knowledge Gaps
- **72 isolated node(s):** `dados/varredura.json`, `dados/alvos.json`, `Fontes de odds no GitHub (tennisexplorer, Pinnacle futebol)`, `Liquidação aos 90 minutos e linhas asiáticas`, `Varredura de valor (odds.py valor)` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 180 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `em_jogo()` and `Teto total de exposicao de 25% da banca (1/4 x 100%)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `cmd_mercados()` and `dist_mercado() (implementação de referência stdlib)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `fecho_github()` and `Char2mant/futbol-veri-aynasi (espelho football-data 2026/27)`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `Regra 'o encontro tem de acabar / nula salvo se determinado'` and `William Hill — regras de ténis`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **What is the exact relationship between `Regra '1 set completo + jogador que avança'` and `Kambi / Unibet — regras de ténis`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **What is the exact relationship between `Regra '1 set completo + jogador que avança'` and `William Hill — regras de ténis`?**
  _Edge tagged AMBIGUOUS (relation: implements) - confidence is low._
- **Why does `shin()` connect `Backtest histórico` to `Fontes e alvos diários`, `Teoria dos mercados secundários`, `Preço justo sem Pinnacle`, `Fecho e API de odds`, `Regras de desistência`, `Viés favorito-azarão`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._