# Fontes de dados de ténis e futebol acessíveis a partir de uma rede restrita (GitHub, GitLab, storage.googleapis.com, PyPI/npm)

Verificação feita a 25/09/2026 (≈11:00–12:30 UTC) a partir deste ambiente. Método: `curl` a `raw.githubusercontent.com`, `git clone --depth N --filter=blob:none` / `git ls-remote` (git por HTTPS funciona), pesquisa GitHub via ferramenta MCP (a API REST `api.github.com/repos/...` devolve "GitHub access to this repository is not enabled for this session" para repositórios não anexados, por isso as datas de commit vêm do `git log` dos clones). Tudo o que não foi testado daqui está marcado **não verificado**.

## 1. Repositórios de Jeff Sackmann (tennis_atp, tennis_wta, tennis_slam_pointbypoint, tennis_MatchChartingProject): estado, datas, colunas, Challengers

### Takeaway
`tennis_atp`, `tennis_wta` e `tennis_slam_pointbypoint` **já não existem** (404 desde, pelo menos, 20/09/2026); só o `tennis_MatchChartingProject` continua ativo (último commit 18/09/2026). Os dados ATP/WTA 2025–2026 no formato Sackmann (com `w_svpt`, `w_1stWon`, etc., incluindo `atp_matches_qual_chall_2026.csv`) só sobrevivem em espelhos congelados em junho de 2026, sendo o melhor o `Aneeshers/tennis-sackmann-archive` (ATP até torneios de 25/05/2026, Challengers/qualificações até 01/06/2026).

### Cited Findings
- `raw.githubusercontent.com/JeffSackmann/tennis_atp/master/README.md`, `.../atp_matches_2023.csv`, `.../atp_matches_2025.csv`, `.../atp_matches_2026.csv`, `.../atp_matches_qual_chall_2026.csv`, `.../atp_rankings_current.csv`, `tennis_wta/master/README.md`, `wta_matches_2025.csv`, `wta_matches_2026.csv` e `tennis_slam_pointbypoint/master/README.md` devolveram **HTTP 404** (verificado aqui). `git ls-remote https://github.com/JeffSackmann/tennis_atp` pede credenciais (sinal de repositório inexistente) e `add_repo` respondeu "was not found on github.com". — [tennis_atp (morto)](https://github.com/JeffSackmann/tennis_atp)
- A pesquisa GitHub `user:JeffSackmann tennis` devolve **um único** repositório: `tennis_MatchChartingProject` (público, `pushed_at` 2026-09-18T08:36Z, 436 estrelas). — [tennis_MatchChartingProject](https://github.com/JeffSackmann/tennis_MatchChartingProject)
- Issue de 20/09/2026: "Four repositories from Jeff Sackmann's account were deleted — tennis_atp, tennis_wta, tennis_pointbypoint, and tennis_slam_pointbypoint. Only tennis_MatchChartingProject remains". O autor propõe como alternativa um conjunto agregado (não por encontro) em `blog.livetennisapi.com/studies.json` (não verificado). — [MLT-OSS/FirstData #238](https://github.com/MLT-OSS/FirstData/issues/238)
- Outros projetos a reagir à remoção (títulos de resultados de pesquisa, não abertos): [wchatgpt2026/tennis #7 "Resolve unavailable Sackmann upstream and pin historical data snapshot"](https://github.com/wchatgpt2026/tennis/issues/7), [ClickHouse PR #121439 "replace the removed tennis dataset"](https://github.com/ClickHouse/ClickHouse/pull/121439), [awesome-open-data PR #42 "remove two 404 tennis entries"](https://github.com/okhosting/awesome-open-data/pull/42).
- Em abril de 2026 o repositório ainda existia: um projeto de terceiros listava `github.com/JeffSackmann/tennis_atp` / `tennis_wta` como fonte ("Last reviewed: 2026-04-25"). — [thekasser/tennis-wta-atp data/sources.md](https://raw.githubusercontent.com/thekasser/tennis-wta-atp/main/data/sources.md)
- **Espelho recomendado:** `Aneeshers/tennis-sackmann-archive`, commit único de 2026-06-25 ("Archive of Jeff Sackmann tennis datasets"), 473 ficheiros; README: snapshots ATP/WTA "from upstream commits made in June 2026", slam point-by-point de `6febb77` (outubro 2024, 2011–2024); licença CC BY-NC-SA 4.0 (uso não comercial). Espelho também no Hugging Face (bloqueado aqui). — [Aneeshers/tennis-sackmann-archive](https://github.com/Aneeshers/tennis-sackmann-archive)
- Ficheiros verificados com HTTP 200 nesse espelho (contagens calculadas aqui):
  - `atp/atp_matches_2026.csv`: 1.449 encontros, `tourney_date` 20260104–20260525 (Roland Garros), 1.191 com `w_svpt`; níveis A, D, G, M. — [raw](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_2026.csv)
  - `atp/atp_matches_qual_chall_2026.csv`: 5.745 encontros (Challengers + qualificações), até 20260601, 5.735 com estatísticas de serviço; níveis A, C, G, M. — [raw](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_qual_chall_2026.csv)
  - `atp/atp_matches_2025.csv`: 2.944 encontros, 20241227–20251217, 2.685 com estatísticas. — [raw](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_2025.csv)
  - `wta/wta_matches_2026.csv`: 1.295 encontros até 20260525; `wta/wta_matches_qual_itf_2026.csv`: 8.975 encontros até 20260602 (inclui ITF W15–W100). — [raw WTA](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/wta/wta_matches_2026.csv)
  - Existem ainda `atp_matches_futures_2024/2025/2026.csv`, `atp_matches_qual_chall_2024/2025.csv`, `wta_matches_qual_itf_2024/2025.csv` (listados na árvore git; não descarregados).
- Colunas (cabeçalho de `atp_matches_2026.csv`): `tourney_id, tourney_name, surface, draw_size, tourney_level, tourney_date, match_num, winner_id, winner_seed, winner_entry, winner_name, winner_hand, winner_ht, winner_ioc, winner_age, loser_* (idem), score, best_of, round, minutes, w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_SvGms, w_bpSaved, w_bpFaced, l_ace, l_df, l_svpt, l_1stIn, l_1stWon, l_2ndWon, l_SvGms, l_bpSaved, l_bpFaced, winner_rank, winner_rank_points, loser_rank, loser_rank_points`. **Não há odds.** — [raw](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_2026.csv)
- Cópia ligeiramente mais recente encontrada: `davidpiontransactions-eng/pariscore` tem `data/tennis_atp/atp_matches_2026.csv` com 1.458 encontros até 20260614 (Estugarda), 1.447 com `w_svpt`. Outras 7 cópias verificadas (MatchMind-Tennis, PropORACLE, tbt-pro, Market_Betting, Sporty, ATP_Tennis_Project, Omega) param em 20260525 ou antes. — [pariscore raw](https://raw.githubusercontent.com/davidpiontransactions-eng/pariscore/HEAD/data/tennis_atp/atp_matches_2026.csv)
- Match Charting Project: último commit 2026-09-18 ("thru 18 sep 2026"). `charting-m-matches.csv`: 7.566 encontros (579 de 2025, 184 de 2026; o mais recente com id 20260521, qualificação de Roland Garros). `charting-w-matches.csv`: 4.264 encontros (565 de 2025, 355 de 2026; o mais recente 20260909, QF US Open Gauff–Andreeva). Ficheiros de estatísticas: `charting-{m,w}-stats-Overview.csv`, `ServeBasics`, `KeyPointsServe`, `KeyPointsReturn`, `ReturnOutcomes`, `ServeDirection`, `Rally`, `NetPoints`, `SvBreakSplit`, etc., e pontos (`charting-*-points-2020s.csv`). — [README](https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/README.md), [charting-m-matches.csv (HTTP 200, 1,14 MB)](https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-matches.csv)

### Inferences
- Para estatísticas de serviço/resposta por encontro em 2026, o agente só tem dados completos até ~meados de junho de 2026 (antes da relva). Tudo o que aconteceu depois (Wimbledon, US Open, digressão asiática) falta no formato Sackmann.
- O Match Charting Project é útil só como amostra (voluntários, enviesado para encontros mediáticos) e quase não cobre o circuito masculino depois de maio de 2026; não serve como fonte de forma recente para Challengers.
- A licença CC BY-NC-SA 4.0 obriga a uso não comercial e atribuição; convém registar isso se o agente usar o espelho.

### Gaps
- Não se sabe porque é que Sackmann apagou os repositórios nem se voltarão noutro sítio (a issue #238 só confirma a remoção).
- Não encontrei nenhum espelho com dados ATP/WTA no formato Sackmann posteriores a 14/06/2026.
- O espelho do Hugging Face (`huggingface.co/datasets/Aneeshers/tennis-sackmann-archive`) não é acessível daqui (403 no CONNECT a huggingface.co).

## 2. Odds ATUAIS (2026) com Pinnacle ou fecho, para ténis e futebol europeu, publicadas em repositórios GitHub

### Takeaway
Só há uma fonte publicada no GitHub com **odds da Pinnacle para futebol europeu** e acessível daqui: `aimidas1/pinnacle_bet365_odds_data` — mas atualiza **de 2 em 2 dias** (não diariamente) e não tem Champions League; não está confirmado que as odds guardadas sejam de fecho. Para **ténis**, a única fonte pré-jogo aproveitável continua a ser `Mriganka-codes/tennis_data` (odds do tennisexplorer, sem Pinnacle, sem fecho, 4 atualizações/dia). Não encontrei nenhum repositório público com odds de ténis da Pinnacle pré-jogo em formato reutilizável.

### Cited Findings
- **aimidas1/pinnacle_bet365_odds_data** (futebol):
  - Último commit 2026-09-23 21:21 UTC; historial: 51 commits de ficheiros a cada execução nos dias 09, 11, 13, 15, 17, 19, 21 e 23/09/2026 → **cadência de 2 em 2 dias** (verificado com `git log`). — [repo](https://github.com/aimidas1/pinnacle_bet365_odds_data)
  - Ficheiros: `data/season_2026/ligas/<Liga>_2026-2027.csv` para 24 ligas (inclui England_Premier_League, Spain_La_Liga, Italy_Serie_A, Germany_Bundesliga, France_Ligue_1, Liga_Portugal, Portugal_LigaPro, Netherlands_Eredivisie, Belgium, Turkey, Greece, Denmark, Spain_La_Liga_2, Bundesliga_2, Russia, Brasil, Argentina, MLS, etc.), `data/season_2026/ligas_full/ligas_full_2026.csv`, `data/season_2026/next_games/next_games.xlsx`, `stats_teams_*`. **Não há ficheiro de Champions League** na árvore. — [árvore via git clone](https://github.com/aimidas1/pinnacle_bet365_odds_data)
  - Colunas de `England_Premier_League_2026-2027.csv`: resultado e estatísticas (golos, cantos, remates, ataques, posse, cartões…) + `odds_pinnacle_home/draw/away`, `odds_btts_pinnacle_no/yes`, `odds_over/under_pinnacle_2`, `_2_25`, `_2_5`, as mesmas para `bet365`, e `prob_*` (implícitas). Exemplo: Manchester City vs Sunderland, 2026-09-20 13:00, Pinnacle 1,36 / 5,40 / 9,25. O formato de `result_info` ("Manchester City won after full-time.") sugere origem Sportmonks (inferência). — [raw](https://raw.githubusercontent.com/aimidas1/pinnacle_bet365_odds_data/main/data/season_2026/ligas/England_Premier_League_2026-2027.csv)
- **Mriganka-codes/tennis_data** (ténis): `matches.json` = `{last_updated, count, matches[]}`, cada encontro com `tournament, time, player1, player2, odds1, odds2, tour` (sem casa nem Pinnacle). Snapshot de 25/09 03:50 UTC com 50 encontros (ex.: "San Diego 2 challenger"). Commits nos últimos 5 dias por volta das 03, 10–12, 15–16 e 20–21 UTC. Descrição: "Scrapes ATP, WTA, and Challenger matches with odds from tennisexplorer.com every 6 hours via GitHub Actions". — [raw matches.json](https://raw.githubusercontent.com/Mriganka-codes/tennis_data/main/matches.json), [repo](https://github.com/Mriganka-codes/tennis_data)
- **Eth91/tennis-odds-collector**: commits "odds snapshot [skip ci]" de ~10 em ~10 min (último 2026-09-25 10:52 UTC), que alteram só `lines_delta.json`; branch `dk-board` com moneylines da DraftKings recolhidas por um workflow a cada 30 min. O `TENNIS.md` descreve 8.375 fechos pré-jogo da Pinnacle recolhidos pelo autor (margem mediana no moneyline 4,73%; ATP/WTA/ITF) e conclui "MONEYLINE IS DEAD… Betting into Pinnacle runs about -10% ROI" para o modelo Elo dele. `docs/tennis_board.json` (gerado 2026-09-05, desatualizado) tem apostas FanDuel/DraftKings com `pin` (odd Pinnacle) e `fair`. O conteúdo de `lines_delta.json` e do branch `dk-board` **não foi inspecionado** (bloqueado pela política de permissões desta sessão). — [TENNIS.md](https://raw.githubusercontent.com/Eth91/tennis-odds-collector/main/TENNIS.md), [repo](https://github.com/Eth91/tennis-odds-collector)
- **melehovtrigger-dot/live-odds-archive**: arquivo de odds **live** (ténis e basquetebol) de um feed público de uma casa de apostas, nomes em cirílico, uma linha JSON por alteração (`ts, id, sport, t1, t2, k1, k2, score, timer, tb`); ficheiros diários `data/2026-09-13.jsonl.gz` … `data/2026-09-25.jsonl` (1,0 MB, 4.918 linhas às ~04 UTC); 4 janelas de 5,5 h por dia. Sem Pinnacle, sem pré-jogo. — [README](https://raw.githubusercontent.com/melehovtrigger-dot/live-odds-archive/main/README.md)
- **alienorsutinn/tennis-odds-mvp**: usa The Odds API (`regions=eu`, `markets=h2h`) de 12 em 12 h (cron `5 */12 * * *`), mas guarda só a **primeira** casa de cada evento; `data/odds_latest.json` de 2026-09-25T03:49Z tinha 4 eventos (WTA Singapura; Betfair, Unibet FR). — [odds_latest.json](https://raw.githubusercontent.com/alienorsutinn/tennis-odds-mvp/main/data/odds_latest.json)
- **Wheyecologicalwarfare3565/proofodds** (descrição: "scored against Pinnacle's closing line", 8 ligas europeias): o código não muda desde 2026-09-01, só há `predictions/2026-08-26…29.json`, e o README (alterado hoje) tem botões "Download Now" e instruções para ignorar o aviso do Windows ("click More info and then Run anyway") — padrão típico de repositórios-isco com malware. Não tem dados da Pinnacle publicados. **Não usar.** — [repo](https://github.com/Wheyecologicalwarfare3565/proofodds)
- Outros vistos e descartados: `bily1258-design/football-odds-api` (4 ficheiros, quadro da lotaria chinesa 北单, produtos no branch gh-pages, não verificado) — [repo](https://github.com/bily1258-design/football-odds-api); `gehrenberg823/ufc-pinnacle-odds` (só UFC) — [repo](https://github.com/gehrenberg823/ufc-pinnacle-odds); `thekasser/tennis-wta-atp` (rankings e bios; refrescado 3x/dia, `snapshot_summary.txt` de 2026-09-25 01:19 UTC com 16.191 encontros numa BD que **não** está no repositório) — [snapshot_summary](https://raw.githubusercontent.com/thekasser/tennis-wta-atp/main/data/snapshot_summary.txt); `bturkyil/brier-veri` (ficheiros JSON pessoais "hafiza" por liga; formato não documentado) — [repo](https://github.com/bturkyil/brier-veri).
- A API pública da Pinnacle fechou em 2025, segundo a descrição de um SDK comercial: "The Pinnacle API alternative since the public API closed (2025)". — [PinnWire/pinnwire-sdk](https://github.com/PinnWire/pinnwire-sdk)

### Inferences
- A tabela de `docs/apis.md` diz que o `aimidas1` é "Diária": na prática é **de 2 em 2 dias** (dias ímpares de setembro, ~21–22 UTC). O plano das 01:30 pode usar odds com 1–2 dias; a regra "confirmar odds com mais de 60 min" é sempre acionada para futebol.
- Como os jogos já disputados mantêm as odds da Pinnacle no CSV, é possível que sejam a última captura antes do jogo (até ~48 h antes), não o fecho real; usar como "fecho" para CLV seria otimista/pessimista de forma não controlada.
- Nenhum repositório encontrado resolve o problema da falta da Pinnacle em ténis; os coletores que a têm (Eth91) não publicam os dados de forma estável e usam métodos de recolha que contornam proteções dos sites — não devem ser integrados.

### Gaps
- Não foi possível confirmar se as odds do `aimidas1` são de abertura, intermédias ou de fecho (o repositório não tem README; `raw .../README.md` = 404).
- Não verifiquei o conteúdo de `Eth91/.../lines_delta.json` nem do branch `dk-board` (bloqueado pela política desta sessão).
- Não encontrei nenhum repositório com a Champions League 2026/27 com odds da Pinnacle.

## 3. Espelhos de football-data.co.uk e tennis-data.co.uk no GitHub (Pinnacle de fecho PSCH/PSCD/PSCA, PSW/PSL, Max/Avg)

### Takeaway
Existe um espelho **automático e atual** do football-data.co.uk para a época 2026/27 (`Char2mant/futbol-veri-aynasi`), mas os CSV de 2026/27 **já não trazem colunas da Pinnacle** (nem PSH nem PSCH); trazem em vez disso odds de fecho da Betfair Exchange (`BFECH/BFECD/BFECA`), média e máximo de fecho (`AvgCH`, `MaxCH`) e mais 6 casas. O mesmo aconteceu no tennis-data.co.uk: em 2026, `PSW/PSL` só existem até 13/01/2026 e foram substituídas por `BFEW/BFEL` (Betfair Exchange). Os CSV com PSCH (Pinnacle de fecho) cobrem até à época 2025/26 (último jogo 24/05/2026) e estão em `huhao930422-debug/football-odds-mirror`.

### Cited Findings
- **Char2mant/futbol-veri-aynasi**: workflow diário às 05:17 UTC que descarrega `https://www.football-data.co.uk/mmz4281/<época>/<liga>.csv` para `T1 E0 E1 SP1 D1 I1 F1 N1 P1 B1 G1 SC0` e calcula a época corrente sozinho ("a partir de julho, nova época"); só faz commit quando o ficheiro muda. Commits de dados: 10, 11, 15, 18 e 22/09/2026. — [workflow](https://raw.githubusercontent.com/Char2mant/futbol-veri-aynasi/main/.github/workflows/mirror-football-data.yml), [repo](https://github.com/Char2mant/futbol-veri-aynasi)
- Conteúdo de `data/fd/2627/*.csv` (verificado aqui): último jogo 20/09/2026 em todas; linhas: E0 50, SP1 69, I1 50, D1 36, F1 45, P1 62, N1 63, T1 54. Colunas PSH e PSCH: **0 preenchidas (não existem no cabeçalho)**; `AvgCH`, `MaxCH`, `B365CH`: 100% preenchidas. Cabeçalho completo: `Div, Date, Time, HomeTeam, AwayTeam, FTHG, FTAG, FTR, HTHG, HTAG, HTR, HxG, AxG, HS, AS, HST, AST, HF, AF, HC, AC, HY, AY, HR, AR, B365H/D/A, BFDH/D/A, BVH/D/A, BWH/D/A, PPH/D/A, SKBH/D/A, MaxH/D/A, AvgH/D/A, BFEH/D/A, B365>2.5, B365<2.5, Max>2.5, Max<2.5, Avg>2.5, Avg<2.5, BFE>2.5, BFE<2.5, AHh, B365AHH/A, MaxAHH/A, AvgAHH/A, BFEAHH/A, B365CH/D/A, BFDCH/D/A, BVCH/D/A, BWCH/D/A, PPCH/D/A, SKBCH/D/A, MaxCH/D/A, AvgCH/D/A, BFECH/D/A, B365C>2.5, B365C<2.5, MaxC>2.5, MaxC<2.5, AvgC>2.5, AvgC<2.5, BFEC>2.5, BFEC<2.5, AHCh, B365CAHH/A, MaxCAHH/A, AvgCAHH/A, BFECAHH/A` (novidade: xG `HxG/AxG`). — [E0 2026/27 raw](https://raw.githubusercontent.com/Char2mant/futbol-veri-aynasi/main/data/fd/2627/E0.csv), [P1 2026/27 raw](https://raw.githubusercontent.com/Char2mant/futbol-veri-aynasi/main/data/fd/2627/P1.csv)
- **huhao930422-debug/football-odds-mirror**: "Daily mirror of football-data.co.uk", cron `0 5 * * *`, commits 15, 18, 19, 22 e 25/09/2026. O `scripts/fetch.py` tem as épocas fixas "from 9394 to 2526", por isso **não descarrega 2026/27** das ligas europeias; o último commit (25/09) só alterou `data/usa/all-seasons.csv` (ligas extra de `/new/`). — [fetch.py](https://raw.githubusercontent.com/huhao930422-debug/football-odds-mirror/main/scripts/fetch.py), [repo](https://github.com/huhao930422-debug/football-odds-mirror)
- O `data/premier-league/season-2526.csv` desse espelho (HTTP 200, 203 KB, 132 colunas) tem `PSH, PSD, PSA, PSCH, PSCD, PSCA, P>2.5, PC>2.5, AHh, PCAHH, MaxCH, AvgCH, B365CH`; último jogo 24/05/2026. Estrutura: `data/<liga>/season-XXYY.csv` desde 1993/94 para 20+ ligas (premier-league, championship, league-one, la-liga, la-liga-2, serie-a, serie-b, bundesliga, bundesliga-2, ligue-1, ligue-2, eredivisie, primeira-liga, jupiler-league, super-lig, scottish-*…) e `data/<país>/all-seasons.csv` para ligas extra (brazil, usa…). — [PL 2025/26 raw](https://raw.githubusercontent.com/huhao930422-debug/football-odds-mirror/main/data/premier-league/season-2526.csv)
- **xgabora/Club-Football-Match-Data-2000-2025**: `data/Matches.csv` (45,4 MB) + `data/EloRatings.csv`; commit 2026-09-05 "Update dataset through early 2026-27 season"; README: 238.858 jogos de 28/07/2000 a 03/09/2026, dados do football-data.co.uk e Elo do ClubElo. `OddHome/OddDraw/OddAway` = **Bet365**, `MaxHome/…` = máximo de ~17 casas, `Over25/Under25` = Bet365. **Sem Pinnacle e sem fecho.** O autor remete para `odds.adamgabor.eu` (não verificado). — [README](https://raw.githubusercontent.com/xgabora/Club-Football-Match-Data-2000-2025/main/README.md), [Matches.csv](https://raw.githubusercontent.com/xgabora/Club-Football-Match-Data-2000-2025/main/data/Matches.csv)
- **tennis-data.co.uk**: não encontrei espelho automático. Cópias manuais atuais:
  - `GreenAlephSports/Monte-Carlo-Tennis-Simulation`: `data/2026_atp_raw.xlsx.xlsx` (2.150 encontros ATP, 04/01–13/09/2026) e `data/2026_wta_raw.xlsx.xlsx` (2.075 encontros WTA até 12/09/2026); último commit 2026-09-18. — [ATP xlsx](https://raw.githubusercontent.com/GreenAlephSports/Monte-Carlo-Tennis-Simulation/main/data/2026_atp_raw.xlsx.xlsx)
  - `nick-benelli/Tennis-Data-Pipeline`: `data/archive/tennis-data-uk/atp-v2/atp_singles_results_2026.csv` (2.150 encontros até 13/09/2026) e `data/raw/uk/wta/uk_wta_singles_raw_2026.csv` (2.075 até 12/09/2026); commits manuais (o único workflow corre lint/testes em push). — [ATP 2026 CSV](https://raw.githubusercontent.com/nick-benelli/Tennis-Data-Pipeline/HEAD/data/archive/tennis-data-uk/atp-v2/atp_singles_results_2026.csv)
  - `robertssong7/tennis-analytics`: `data/scraped/tennis_data_2026.xlsx` só até 15/03/2026 (desatualizado), apesar de commits diários de outros artefactos. — [xlsx](https://raw.githubusercontent.com/robertssong7/tennis-analytics/main/data/scraped/tennis_data_2026.xlsx)
- Colunas tennis-data 2026: `ATP, Location, Tournament, Date, Series, Court, Surface, Round, Best of, Winner, Loser, WRank, LRank, WPts, LPts, W1…L5, Wsets, Lsets, Comment, B365W, B365L, PSW, PSL, MaxW, MaxL, AvgW, AvgL, BFEW, BFEL`. Preenchimento no ATP 2026 (calculado aqui, por mês jan→set): `PSW` 71/0/0/0/0/0/0/0/0 (último 13/01/2026); `BFEW` 238/292/221/167/269/237/251/283/88 (2.046 de 2.150); `AvgW` 2.150/2.150. WTA 2026: `PSW` 101, `BFEW` 1.960 de 2.075. — [ATP 2026 CSV](https://raw.githubusercontent.com/nick-benelli/Tennis-Data-Pipeline/HEAD/data/archive/tennis-data-uk/atp-v2/atp_singles_results_2026.csv)
- `edouardthom/ATPBetting` (dados tennis-data até 2018): último commit 2018-03-13 — desatualizado. — [repo](https://github.com/edouardthom/ATPBetting)

### Inferences
- A partir de 2026 as duas fontes clássicas deixaram de publicar a Pinnacle (futebol na época 2026/27; ténis desde meados de janeiro de 2026). É coerente com o fecho da API pública da Pinnacle em 2025 (secção 2), mas a causa não está confirmada.
- Para medir o CLV do agente em futebol 2026/27 dá para usar, sem chave, o **fecho da Betfair Exchange** (`BFECH/D/A`, antes da comissão) ou a **média de fecho** (`AvgCH`) do football-data, lidos do espelho Char2mant (atualizado ~2x/semana, depois das jornadas). Não substitui a Pinnacle exatamente: as odds da Betfair Exchange não descontam a comissão da bolsa e a média inclui a margem das casas (valor da comissão não verificado).
- Para backtest com Pinnacle de fecho: futebol até 2025/26 (`PSCH`) no espelho huhao; ténis só até 2025 (`PSW/PSL`; no tennis-data as odds da Pinnacle eram historicamente tratadas como de fecho, mas isso não foi verificado daqui).
- Para ténis 2026, o `BFEW/BFEL` do tennis-data é a melhor referência "afiada" disponível, mas os espelhos são manuais e param no US Open (13/09/2026); a digressão asiática ainda não aparece.

### Gaps
- Não consegui ler as notas oficiais (`notes.txt`) do football-data.co.uk nem do tennis-data.co.uk para confirmar quando a Pinnacle saiu, nem se `BFEW` em ténis é de fecho (ambos os sites bloqueados: CONNECT 403).
- Não verifiquei se o Char2mant cobre também a Champions League (não está na lista de ligas do workflow; o football-data.co.uk historicamente não publica a UCL).

## 4. Estatísticas de encontros de ténis 2025–2026 (serviço/resposta, resultados recentes) além de Sackmann

### Takeaway
Não há, no GitHub, uma fonte atualizada até setembro de 2026 com estatísticas de serviço de todos os encontros ATP/WTA/Challenger. O `Tennismylife/TML-Database` (que o `docs/apis.md` dá como "diária") **parou a 27/01/2026**. Há cobertura parcial: estatísticas estilo Sofascore dos Masters/Slams de 2026 em `LuckyLoser91/TennisCourtLog`, e resultados sem estatísticas até 29/08/2026 em `robertssong7/tennis-analytics`.

### Cited Findings
- `Tennismylife/TML-Database`: HEAD = commit de 2026-01-27 ("Delete index.html"); `2026.csv` com 137 encontros até 20260117 (Adelaide/Auckland); `ongoing_tourneys.csv` com 80 encontros do Australian Open até 20260121. Colunas iguais às de Sackmann + `indoor`, com `w_svpt` etc. preenchidos. — [2026.csv](https://raw.githubusercontent.com/Tennismylife/TML-Database/master/2026.csv), [repo](https://github.com/Tennismylife/TML-Database)
- O site do mesmo autor diz ter uma base "1967–2026" — [stats.tennismylife.org](https://stats.tennismylife.org/tennis-match-database) (não verificado daqui).
- `LuckyLoser91/TennisCourtLog` (último commit 2026-09-22): `api_folder/data/<torneio>_2026/` para australian_open, doha, dubai, indian_wells, miami, madrid, rome, roland_garros, wimbledon, canada, cincinnati e us_open 2026 (+ RG e Wimbledon 2025); no US Open 2026 há 127 `event_statistics_<id>.json` + 127 `event_detail_<id>.json` em formato Sofascore (grupos "Service": aces, double faults, first serve…). Não inclui a digressão asiática nem Challengers. — [exemplo](https://raw.githubusercontent.com/LuckyLoser91/TennisCourtLog/HEAD/api_folder/data/us_open_2026/event_statistics_16901555.json), [repo](https://github.com/LuckyLoser91/TennisCourtLog)
- `robertssong7/tennis-analytics`: commits diários ("Daily downstream artifacts — 2026-09-24"); `data/processed/supplemental_matches_2025_2026.csv` com 9.486 encontros até 20260829, colunas `tourney_name, tourney_date, surface, tourney_level, round, winner_name, loser_name, winner_rank, loser_rank, score, best_of, court, location` (sem estatísticas de serviço). — [CSV](https://raw.githubusercontent.com/robertssong7/tennis-analytics/main/data/processed/supplemental_matches_2025_2026.csv)
- `Mriganka-codes/tennis_data` só tem encontros do dia e odds (secção 2), não resultados nem estatísticas.
- Repositórios recentes com nomes promissores (`acimovicluka/atp-tennis-tracker`: 3 ficheiros, só esquema e fetcher, criado 24/09/2026; `thekasser/tennis-wta-atp`: rankings) não têm dados de encontros publicados. — [atp-tennis-tracker](https://github.com/acimovicluka/atp-tennis-tracker)

### Inferences
- A forma recente (últimos 3 meses) de jogadores, sobretudo em Challengers, não pode ser obtida de fontes GitHub verificadas; o agente teria de a declarar "não verificada" (regra 9) ou usar só o preço de mercado.
- Para modelos de serviço/resposta (ex.: Markov), dá para calibrar com dados até junho de 2026 (espelho Sackmann + qual_chall), aceitando 3 meses de atraso.

### Gaps
- Não encontrei nenhuma fonte GitHub com estatísticas dos torneios de Chengdu, Hangzhou, Pequim, Xangai ou Wuhan 2026.
- Não verifiquei se o `TennisCourtLog` continua a acrescentar torneios automaticamente (os ficheiros parecem ser gerados por scripts em `updates/`, mas não li o workflow).

## 5. Conjuntos de dados públicos em storage.googleapis.com

### Takeaway
`storage.googleapis.com` é acessível (a raiz responde HTTP 400, sinal de que o host passa no proxy), mas não encontrei nenhum bucket público com odds desportivas. Kaggle e Hugging Face, onde estão os grandes conjuntos de odds, estão bloqueados.

### Cited Findings
- `curl https://storage.googleapis.com` → HTTP 400 (acessível); `https://www.kaggle.com` e `https://huggingface.co` → "CONNECT tunnel failed, response 403" (verificado aqui). — [storage.googleapis.com](https://storage.googleapis.com)
- A documentação da Google explica o formato `https://storage.googleapis.com/BUCKET_NAME/OBJECT_NAME` para dados públicos, mas a pesquisa não encontrou nenhum bucket de odds de futebol ou ténis. — [Google Cloud: Access public data](https://docs.cloud.google.com/storage/docs/access-public-data)

### Inferences
- Só valeria a pena se um projeto específico publicasse o URL do bucket; não há nenhum candidato conhecido.

### Gaps
- Não existe forma de listar buckets públicos sem saber o nome; a pesquisa web não devolveu nenhum.

## 6. Pacotes PyPI que trazem ou obtêm dados desportivos e se funcionam atrás deste proxy

### Takeaway
O PyPI é acessível e os pacotes instalam-se, mas os scrapers dos pacotes de futebol (`soccerdata`, `penaltyblog`) vão buscar dados a sites bloqueados, por isso **não funcionam aqui como fontes de dados**. O `penaltyblog` continua útil offline pelos modelos e pela remoção de margem (tem implementação do método de Shin em `penaltyblog/implied`).

### Cited Findings
- `https://pypi.org/pypi/<pkg>/json` → 200 para `soccerdata`, `penaltyblog`, `sportsdataverse`; 404 para `tennisdata` e `worldfootballR` (não existem no PyPI). Versões: soccerdata 1.9.1 (2026-07-24), penaltyblog 1.12.2 (2026-09-13), sportsdataverse 0.1.4 (2026-09-01). `pip download` funcionou. — [soccerdata no PyPI](https://pypi.org/project/soccerdata/), [penaltyblog no PyPI](https://pypi.org/project/penaltyblog/)
- Hosts usados no código do `soccerdata` 1.9.1: `site.api.espn.com`, `understat.com`, `football-data.co.uk`, `whoscored.com`, `sofascore.com`, `sofifa.com`, `fbref.com`, `clubelo.com`. No `penaltyblog` 1.12.2: `fantasy.premierleague.com`, `understat.com`, `football-data.co.uk`. Nenhum dos dois usa `raw.githubusercontent.com` para dados (grep ao código). — [soccerdata (GitHub)](https://github.com/probberechts/soccerdata)
- Testados daqui, todos bloqueados (CONNECT 403 ou 403): understat.com, fbref.com, www.clubelo.com, api.clubelo.com, fantasy.premierleague.com, www.sofascore.com, pena.lt, football-data.co.uk, tennis-data.co.uk.
- `penaltyblog/implied/implied.py` e `models.py` contêm a implementação de Shin (grep "shin" no wheel). — [penaltyblog](https://pypi.org/project/penaltyblog/)

### Inferences
- Nenhum pacote PyPI resolve o acesso a dados neste ambiente; o caminho viável é sempre um repositório GitHub que publique os ficheiros.
- O `penaltyblog` pode servir para validar a implementação de Shin em `scripts/odds.py`, mas não é necessário.

### Gaps
- Não testei pacotes npm nem pacotes de ténis menos conhecidos.

## 7. Resumo da verificação de acesso (URLs testados a 25/09/2026)

### Takeaway
A rede deixa passar `raw.githubusercontent.com` e o git por HTTPS para repositórios públicos, a pesquisa GitHub via ferramenta MCP, `storage.googleapis.com` e o PyPI. Bloqueia github.com (páginas web via curl), os sites de dados (football-data, tennis-data, Kaggle, Hugging Face, FBref, Understat, Sofascore, ClubElo, FPL). A API REST do GitHub para repositórios não anexados à sessão devolve erro de acesso.

### Cited Findings
- **HTTP 200 (fontes com dados úteis):**
  - [Aneeshers/tennis-sackmann-archive atp_matches_2026.csv](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_2026.csv) — dados até 25/05/2026 (snapshot de junho, congelado).
  - [atp_matches_qual_chall_2026.csv](https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_qual_chall_2026.csv) — até 01/06/2026.
  - [MatchCharting charting-m-matches.csv](https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-matches.csv) — commit 18/09/2026.
  - [Mriganka matches.json](https://raw.githubusercontent.com/Mriganka-codes/tennis_data/main/matches.json) — commit 25/09/2026 03:50 UTC.
  - [aimidas1 PL 2026-27](https://raw.githubusercontent.com/aimidas1/pinnacle_bet365_odds_data/main/data/season_2026/ligas/England_Premier_League_2026-2027.csv) — commit 23/09/2026 21:21 UTC.
  - [Char2mant football-data 2026/27 E0](https://raw.githubusercontent.com/Char2mant/futbol-veri-aynasi/main/data/fd/2627/E0.csv) — commit 22/09/2026, jogos até 20/09/2026.
  - [huhao football-data 2025/26 PL (com PSCH)](https://raw.githubusercontent.com/huhao930422-debug/football-odds-mirror/main/data/premier-league/season-2526.csv) — até 24/05/2026.
  - [xgabora Matches.csv](https://raw.githubusercontent.com/xgabora/Club-Football-Match-Data-2000-2025/main/data/Matches.csv) — até 03/09/2026.
  - [nick-benelli tennis-data ATP 2026](https://raw.githubusercontent.com/nick-benelli/Tennis-Data-Pipeline/HEAD/data/archive/tennis-data-uk/atp-v2/atp_singles_results_2026.csv) — até 13/09/2026.
  - [GreenAleph tennis-data WTA 2026](https://raw.githubusercontent.com/GreenAlephSports/Monte-Carlo-Tennis-Simulation/main/data/2026_wta_raw.xlsx.xlsx) — até 12/09/2026.
  - [TML 2026.csv](https://raw.githubusercontent.com/Tennismylife/TML-Database/master/2026.csv) — 200, mas parado em 17/01/2026.
  - [live-odds-archive 2026-09-25.jsonl](https://raw.githubusercontent.com/melehovtrigger-dot/live-odds-archive/main/data/2026-09-25.jsonl) — live, sem Pinnacle.
- **HTTP 404:** todos os ficheiros testados de `JeffSackmann/tennis_atp`, `tennis_wta`, `tennis_slam_pointbypoint`; `aimidas1/.../README.md`.
- **Bloqueados (CONNECT 403):** www.tennis-data.co.uk, www.football-data.co.uk, www.kaggle.com, huggingface.co, understat.com, fbref.com, www.clubelo.com, fantasy.premierleague.com, www.sofascore.com, pena.lt; `github.com/<user>/<repo>` por curl → 403; `api.clubelo.com` → 403.
- **Acessível:** storage.googleapis.com (400 na raiz), pypi.org (200).

### Inferences
- Resumo de prioridades para o agente:
  1. **Odds atuais com Pinnacle:** futebol → `aimidas1` (2 em 2 dias, 24 ligas, sem UCL). Ténis → nenhuma fonte com Pinnacle; `Mriganka` (média do tennisexplorer) continua a ser a única pré-jogo.
  2. **Fecho para CLV em 2026:** futebol → `Char2mant` (fecho Betfair Exchange `BFEC*`, média `AvgC*`, máximo `MaxC*`); ténis → `BFEW/BFEL` do tennis-data, só em cópias manuais (paradas a 13/09/2026).
  3. **Estatísticas de ténis:** espelho Sackmann até junho de 2026; nada completo depois disso.
  4. **Backtest com Pinnacle de fecho:** futebol até 2025/26 (`huhao`, `PSCH/PSCD/PSCA`); ténis até janeiro de 2026 (`PSW/PSL`).
- Correções para `docs/apis.md`: o `aimidas1` não é diário (2 em 2 dias) e o `TML-Database` está parado desde 27/01/2026.

### Gaps
- A abordagem é limitada ao que a pesquisa do GitHub devolve; repositórios sem palavras-chave óbvias podem ter escapado.
- O GitLab foi indicado como acessível mas não foi pesquisado nesta ronda.
