# APIs de dados desportivos

Escolhidas da secção "Sports & Fitness" do repositório [public-apis](https://github.com/public-apis/public-apis). Para procurar outras: `git clone --depth 1 https://github.com/public-apis/public-apis` (o GitHub é acessível) e lê essa secção do `README.md`.

Regras de uso: tenta primeiro as que não pedem chave. As chaves vêm de variáveis de ambiente e nunca se mostram nem se gravam no repositório. Se a rede bloquear um domínio, diz qual foi e passa à pesquisa web. Confirma os endpoints na documentação de cada API antes do primeiro uso.

## Acessíveis a partir deste ambiente, sem mexer na rede
Com a rede atual, só passam os seguintes serviços:
- GitHub: `raw.githubusercontent.com`, `codeload.github.com` e `api.github.com` (parcial);
- `gitlab.com` e `storage.googleapis.com`;
- os registos de pacotes (PyPI, npm e afins).

Estas fontes, publicadas por GitHub Actions, já estão ligadas ao `scripts/odds.py` (`fontes` e `alvos`):

| Fonte | O que dá | Atualização | Estado (25/09/2026) |
|---|---|---|---|
| [Mriganka-codes/tennis_data](https://github.com/Mriganka-codes/tennis_data) | Encontros ATP, WTA e Challengers do dia, com odds médias do tennisexplorer (margem mediana ~7%). O histórico git (785 versões desde 10/03/2026) é uma série de consensos com data e hora | Agendada de 6 em 6 h (00, 06, 12 e 18 UTC), mas chega 3 a 5 h depois; só muda de dia depois da meia-noite de Praga | ✅ ligada; cada leitura fica em `dados/consenso.json` (fecho) |
| [aimidas1/pinnacle_bet365_odds_data](https://github.com/aimidas1/pinnacle_bet365_odds_data) | Próximos jogos de futebol com odds da **Pinnacle** e da Bet365 (1X2, ambas marcam, mais/menos golos), 24 ligas. Os rótulos Home/Away do 1X2 estão trocados na fonte. **Sem Champions** | **De 2 em 2 dias** (não diária); não está confirmado que sejam odds de fecho | ✅ ligada |
| [Char2mant/futbol-veri-aynasi](https://github.com/Char2mant/futbol-veri-aynasi) | Espelho diário dos CSV do football-data.co.uk (12 ligas): fecho da **Betfair Exchange** (`BFECH/D/A`), média e máxima de fecho (`AvgCH`, `MaxCH`), 6 casas e xG. Em 2026/27 **já não tem Pinnacle** (`PSH`/`PSCH`) | Diária | por ligar — fecho fiável para o CLV do futebol a partir de 09/10 |
| [Aneeshers/tennis-sackmann-archive](https://github.com/Aneeshers/tennis-sackmann-archive) | Espelho dos repositórios de Jeff Sackmann (`tennis_atp`/`tennis_wta`, apagados por volta de 20/09/2026): encontros com estatísticas de serviço (`w_svpt`, `w_1stWon`, …), incluindo Challengers e ITF. Licença CC BY-NC-SA | Congelado: ATP até 25/05/2026, Challengers até 01/06/2026 | contexto (histórico) |
| [JeffSackmann/tennis_MatchChartingProject](https://github.com/JeffSackmann/tennis_MatchChartingProject) | Encontros "charted" ponto a ponto (poucos em 2026) | Ativo (18/09/2026) | contexto |
| [jriordan55/mlb_pbp_model](https://github.com/jriordan55/mlb_pbp_model) | Odds da MLB (DraftKings, FanDuel, BetMGM) | Parou a 20/07/2026 | ❌ desatualizada |
| [Tennismylife/TML-Database](https://github.com/Tennismylife/TML-Database) | Resultados ATP (sem odds) | **Parou a 27/01/2026** | ❌ desatualizada |

**A Pinnacle saiu das fontes públicas.** A API pública da Pinnacle fechou em 2025; no tennis-data.co.uk as colunas `PSW`/`PSL` só têm dados até 13/01/2026 (passaram a vir `BFEW`/`BFEL`, da Betfair Exchange); no football-data de 2026/27 também já não há Pinnacle. Para a Champions (13–14/10) não há nenhuma fonte acessível com Pinnacle: fica o consenso, a ≥ 5%, ou de fora.

**Não usar:** o repositório `proofodds` tem sinais de isco de malware ("Download", "Run anyway"); o `Eth91/tennis-odds-collector` contorna as proteções dos sites de apostas. Kaggle e Hugging Face dão 403 neste ambiente; os scrapers do `soccerdata` e do `penaltyblog` usam sites bloqueados.

**Regra:** procura sempre fontes a que o ambiente consiga chegar.
- Começa por `python3 scripts/odds.py fontes`.
- Se um desporto ficar sem cobertura, procura no [public-apis](https://github.com/public-apis/public-apis) e na web por dados publicados num dos serviços acessíveis. Em geral são repositórios do GitHub com GitHub Actions.
- Antes de ler um repositório novo, pede acesso de leitura com `add_repo`. Testa se chega e se está atualizado, e só então acrescenta-o a `FONTES` no `odds.py` e a esta tabela.

## Odds e probabilidades justas
| API | O que dá | Chave | Documentação |
|---|---|---|---|
| The Odds API | Odds de várias casas, incluindo a Pinnacle (região `eu`). Usada por `scripts/odds.py` | `ODDS_API_KEY` (grátis, 500 créditos/mês) | https://the-odds-api.com |
| PinnWire | Odds da Pinnacle em tempo real, 13 desportos | sim | https://pinnwire.com/docs.html |
| FanLine Wire | Odds da FanDuel (EUA), com snapshot público | não | https://fanlinewire.com/docs |
| Odds-API.io | Odds de 265+ casas, 34 desportos | sim | https://docs.odds-api.io |

## Probabilidades de modelos (segunda opinião)
| API | O que dá | Chave | Documentação |
|---|---|---|---|
| Bet Better | Probabilidades e odds justas de modelos, 13 ligas | não | https://betbetter.world/api/ |
| Football Charts | Probabilidades de modelo e projeções, 93 ligas de futebol | sim | https://www.football-charts.com/developers |

## Calendário, resultados e estatísticas
| API | O que dá | Chave | Documentação |
|---|---|---|---|
| SportScore | Jogos, resultados, classificações: futebol, basquetebol, ténis | não | https://sportscore.com/developers/ |
| ESPN (não oficial) | Scoreboards de futebol, NBA, WNBA, MLB e ténis | não | ver `docs/comum.md` |
| MLB Stats API | Jogos e lançadores prováveis | não | ver `docs/comum.md` |
| TheSportsDB | Calendários de muitos desportos | chave de teste gratuita | https://www.thesportsdb.com/api.php |
| API-FOOTBALL | Futebol: jogos, onzes, lesões, estatísticas | sim (plano gratuito) | https://www.api-football.com/documentation-v3 |
| football-data.org | Futebol: jogos e classificações das principais ligas | sim (gratuita) | https://www.football-data.org |
| balldontlie | Estatísticas da NBA | sim (gratuita) | https://www.balldontlie.io |
| OpenLigaDB | Resultados das ligas alemãs | não | https://www.openligadb.de |
