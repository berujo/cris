# Medir primeiro, apostar menos e melhor

A melhoria mais importante para este agente não é uma fórmula de preço melhor: é conseguir medir-se. O agente trabalha hoje com o consenso do tennisexplorer publicado no GitHub, que não tem Pinnacle nem odd de fecho, e esse caminho não grava fecho nenhum. Por isso o CLV (a métrica principal) não se calcula, a regra de paragem não pode disparar e o `dados/recomendacoes.csv` continua vazio. A segunda descoberta é que o consenso é uma referência mais ruidosa do que parece. No ténis ATP, só **cerca de 56% da vantagem medida contra a média das casas se mantém contra a Pinnacle**. Uma casa "mole" do tipo da Bet365 ficou 5% ou mais acima do consenso **apenas 19 vezes em oito anos, e sem valor real**. Daqui saem três correções com fórmula:
- um limiar de EV que sobe para os azarões e para as recolhas antigas;
- stakes calculadas sobre um EV "encolhido": com 1/4 de Kelly sobre o EV aparente, a probabilidade de a banca chegar ao stop-loss passa de ~0,8% para ~9%;
- filtros determinísticos para as armadilhas próprias do ténis: desistências liquidadas de forma diferente da Pinnacle, erros manifestos de odd e encontros ITF.

Os subagentes LLM devem ficar como veto. Nenhum estudo de 2025–2026 mostra LLMs a bater o mercado, e os ângulos clássicos do ténis (fadiga, jet lag, motivação) não têm efeito provado sobre as odds. Com quatro casas portuguesas e um imposto sobre o volume apostado, "Hoje: não apostar" deve ser o resultado normal, e as próximas 100 recomendações valem sobretudo como experiência de medição. Duas ressalvas:
- quase toda a literatura externa foi lida em resumos de motores de pesquisa, porque o proxy bloqueou os textos integrais;
- os cálculos próprios usam a ATP de 2010–2018 no circuito principal.

Por isso, os números devem ser confirmados antes de passarem a constantes no código.

## O caminho que o agente usa na prática não produz odd de fecho

**O CLV não chega a ser medido no caminho do consenso.** Uma recomendação desse caminho só é registada quando o utilizador diz a odd e a casa. O `banca.py recomendar` grava-a então com `sport_key = "github"` e sem `evento_id`. O `odds.py fecho` só processa linhas com `evento_id`, e a função `regra_paragem` só conta linhas com `prob_fecho`. Resultado: no caminho que o agente usa todos os dias, **a regra 6 do `CLAUDE.md` nunca pode disparar**. Não é por falta de amostra; é por construção (`scripts/banca.py`, `scripts/odds.py`).

**A ★ da lista de alvos nunca acende no ténis.** A odd da fonte é a mesma que se usou para tirar a margem. No método aditivo (igual ao de Shin a duas vias), odd × p = 1 − o(Σ − 1)/2, que é sempre menor do que 1 quando há margem. No alvo Duckworth a 2,10 dá 0,943, longe dos 1,05 exigidos. A instrução da skill "dá prioridade aos marcados com ★" não tem qualquer efeito no ténis.

A referência que dá nome ao método também desapareceu das fontes públicas:
- **A API pública da Pinnacle fechou em 2025** ([PinnWire](https://github.com/PinnWire/pinnwire-sdk)).
- **No tennis-data, as colunas da Pinnacle (PSW/PSL) só têm dados até 13/01/2026.** Foram substituídas pelas da Betfair Exchange (BFEW/BFEL), preenchidas em 2 046 dos 2 150 encontros ATP de 2026 ([espelho nick-benelli](https://raw.githubusercontent.com/nick-benelli/Tennis-Data-Pipeline/HEAD/data/archive/tennis-data-uk/atp-v2/atp_singles_results_2026.csv)).
- **O football-data da época 2026/27 já não tem PSH nem PSCH.** Traz, em vez disso, o fecho da Betfair Exchange (`BFECH/D/A`) e a média de fecho (`AvgCH`), num espelho atualizado todos os dias ([Char2mant](https://github.com/Char2mant/futbol-veri-aynasi)).
- **A fonte de futebol com Pinnacle atualiza de 2 em 2 dias, não diariamente** como diz o `docs/apis.md`, e não tem ficheiro da Champions ([aimidas1](https://github.com/aimidas1/pinnacle_bet365_odds_data)).
- **Os repositórios `tennis_atp` e `tennis_wta` de Jeff Sackmann foram apagados** por volta de 20/09/2026 ([issue #238](https://github.com/MLT-OSS/FirstData/issues/238)). Resta um espelho congelado em junho de 2026, com licença CC BY-NC-SA ([Aneeshers](https://github.com/Aneeshers/tennis-sackmann-archive)).
- **O TML-Database, que a documentação dá como diário, parou a 27/01/2026** ([TML](https://github.com/Tennismylife/TML-Database)).

**Para a 2.ª jornada da Champions (13–14/10) não há nenhuma fonte acessível com Pinnacle.**

**Vale a pena corrigir isto porque o CLV é, de longe, o sinal mais rápido.** Buchdahl analisou 87 960 pares de odds da Pinnacle em quatro épocas. A razão entre a odd tomada e o fecho sem margem previu o retorno numa relação "quase perfeita de um para um". O desvio-padrão por aposta é de cerca de 0,1 no CLV, contra 1,0 no lucro ([Pinnacle Odds Dropper](https://www.pinnacleoddsdropper.com/blog/closing-line-value--clv-demystified-by-expert-joseph-buchdahl)). As fórmulas são as habituais:
- CLVᵢ = oᵢ · p_fecho,ᵢ − 1;
- erro-padrão SE = s/√n;
- número de apostas para t = 2: **n ≈ (2s/m)²**.

Com s = 0,07, uma vantagem de 3% vê-se em ~22 apostas e uma de 2% em ~49. Pelo lucro, a odd 2,5, seriam precisas ~6 700 ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)). A regra de paragem atual (100 recomendações com fecho) está bem calibrada: se o CLV real for +3%, a hipótese de parar por engano é ≤ 0,1%; se for +1%, sobe para 8–16%.

Há uma ressalva própria do ténis. Um tipster com ~3 000 apostas teve **ROI de +8,9% quando o fecho da Pinnacle previa −0,2%** ([Sports Trading Network](https://www.sportstradingnetwork.com/article/do-pinnacle-closing-prices-in-tennis-tell-the-full-story-can-you-win-in-the-long-run-without-beating-them/)). O fecho é imperfeito em nichos, mas com amostras pequenas continua a ser a melhor métrica.

### A armadilha da recolha: com o fecho errado, o CLV sai igual ao EV

Se o "fecho" for a própria recolha que selecionou a aposta, o CLV é, por construção, igual ao EV de seleção, isto é, ≥ 5%, e não quer dizer nada. A identidade que resolve o problema é:

**1 + CLV_cons = (1 + EV₀)(1 + M)**, com **M = p\*/p₀ − 1**

onde:
- p₀ é a probabilidade justa na recolha da seleção;
- p\* é a probabilidade justa na **última recolha estritamente posterior** e anterior ao início.

Só M, o movimento do consenso na direção da seleção, traz informação. A qualidade do "fecho" depende do intervalo g entre essa última recolha e o início:
- **g ≤ 2 h:** boa;
- **2 h a 6 h:** fraca;
- **mais de 6 h, ou sem recolha posterior:** "não medido".

Onde exista, junta-se um fecho independente e mais fiável, obtido depois do jogo: o BFEW/BFEL da Betfair Exchange no ténis e o BFEC/AvgC no futebol. Os dois fechos reportam-se **separados**, com a percentagem de recomendações que cada um cobre. Nunca se misturam. Para comparar escalas, a inclinação medida na ATP sugere que **+5% de CLV contra o consenso valem ~+3% contra um fecho fiável**, e menos quando o consenso está desatualizado ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)).

### O histórico da própria fonte já é uma série de consensos com data e hora

Nenhuma das notas conseguiu medir quanto se move o consenso do tennisexplorer entre recolhas. Mas o repositório que o agente já lê guarda **785 versões de `matches.json` desde 10/03/2026**. Esse histórico git é, de graça, uma série de consensos com data e hora ([Mriganka-codes/tennis_data](https://github.com/Mriganka-codes/tennis_data)). Num cálculo próprio sobre essa série, foram comparadas a primeira e a última recolha antes do início em **10 536 encontros**. O intervalo mediano entre as duas foi de 7,3 h (percentil 90: 12,5 h).

O movimento típico é pequeno, mas as caudas são largas:

| Medida | Valor |
|---|---|
| Variação mediana da probabilidade justa | **0,8 pp** |
| Encontros com variação > 3 pp | **16,5%** |
| Encontros com variação > 5 pp | **8,6%** |
| Challenger/ITF com variação > 5 pp | **10,9%** |
| ATP / WTA com variação > 5 pp | 6,3% / 6,4% |
| Margem mediana do consenso | **7,0%** (média 8,2%) |

Cerca de 2% dos pares moveram-se mais de 15 pp. Serão erros de dados ou substituições de jogadores, o que não foi verificado.

A seleção do agente escolhe precisamente os casos em que uma casa portuguesa está acima de um consenso desatualizado. Uma cauda do tamanho de toda a margem de 5% é, por isso, o risco central, e não ruído de fundo. Há ainda um problema de horário na digressão asiática. A fonte publica o dia por volta das 03:50 UTC, e muitos encontros começam entre as 04:00 e as 06:00 UTC. Nesses casos não existe recolha posterior e a linha tem de ficar "não medido".

## Contra o consenso, pouco mais de metade da vantagem é real

**O método para tirar a margem quase não importa, desde que não seja o multiplicativo.** Com dois resultados, o método de Shin dá exatamente as mesmas probabilidades que o aditivo: a diferença máxima verificada foi de 3×10⁻¹⁶. Nas odds médias da ATP de 2010–2018:
- Shin, power e odds-ratio ficaram empatados (power − Shin = −0,00008 de log-loss, SE 0,00023).
- O multiplicativo foi significativamente pior (+0,00143, SE 0,00027). Na faixa em que o favorito tem 0,7–0,9, deixa a probabilidade do azarão ~3 pp alta demais ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)).

A literatura vai no mesmo sentido:
- o power iguala ou supera o de Shin e bate o multiplicativo, em dados que incluem ténis ([Clarke, Kovalchik & Ingram 2017](https://www.sciencepublishinggroup.com/article/10.11648/j.ajss.20170506.12));
- as probabilidades de Shin são melhores do que a simples normalização ([Štrumbelj 2014](https://www.sciencedirect.com/science/article/abs/pii/S0169207014000533)).

**O viés favorito–azarão no ténis é forte e bem documentado:**
- é positivo em toda a gama de odds ([Forrest & McHale 2007](https://www.tandfonline.com/doi/abs/10.1080/13518470701705736));
- em ~45 000 encontros, é mais forte entre jogadores de ranking baixo, nas rondas finais e nos torneios mediáticos, o que é coerente com as casas a protegerem-se de apostadores com informação privilegiada ([Lahvička](https://mpra.ub.uni-muenchen.de/47905/1/MPRA_paper_47905.pdf));
- também existe nas bolsas de apostas ([Abinzano et al. 2016](https://www.tandfonline.com/doi/full/10.1080/13504851.2015.1093074));
- num estudo com odds da Bet365, o método de Shin corrige-o pouco nos encontros desequilibrados ([CaSco](https://econpapers.repec.org/paper/sepwpaper/3_5f236.htm)).

Depois do método de Shin sobre a média, ainda sobram +1,2 a +1,7 pp de viés na faixa 0,7–0,9. É só sugestivo (~1,5 erros-padrão), mas justifica uma proteção barata: usar, para o lado apostado, o preço "pior caso" **p = min(p_Shin, p_power)**. Há dois trabalhos de 2026 que não foi possível ler e que merecem ser acompanhados: o artigo de Maurice Berk "It's Time to Retire Shin's Method" ([Substack](https://algorithmicsportsbetting.substack.com/p/its-time-to-retire-shins-method)) e o método OO-EPC ([arXiv 2604.17194](https://arxiv.org/abs/2604.17194)).

**O problema do consenso é a precisão em cada encontro, não a calibração média.** À mesma hora, a média das casas sem margem é quase tão exata como a Pinnacle: log-loss de 0,55620 contra 0,55579, uma diferença não significativa. Mas o desvio-padrão de log(odd justa pela média / odd justa pela Pinnacle) é **0,040**, e a regressão das vantagens dá **vantagem_pin = 0,002 + 0,557 × vantagem_média**. Uma vantagem de 5–8% contra o consenso vale, em média, +3,3% contra a Pinnacle; uma de 3–5% vale só +2,0% ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)). Os 5% atuais são, portanto, apenas o ponto em que se empata com os 3% exigidos contra a Pinnacle. Não deixam margem de segurança.

Com o limiar de 5%, o varrimento deu 1 395 apostas, com +4,6% de vantagem média contra a Pinnacle, 66% delas com vantagem positiva e ROI de +6,7% (SE 3,5%). A vantagem que resta cai com a odd:
- 1,40–2,00: **+6,7%**;
- 2,00–3,00: **+4,5%**;
- 3,00–4,00: **+3,8%**.

O limiar de Kaunitz, Zhong & Kreiner é um desconto somado na probabilidade: aposta-se se odd máxima > 1/(p_consenso − 0,05), com 1/média sem tirar margem. Com ele fizeram +3,5% em 56 435 apostas simuladas. Com dinheiro real, fizeram ~260 apostas antes de as casas limitarem as contas, em alguns casos a **1,25 $** ([arXiv 1710.02824](https://arxiv.org/abs/1710.02824); [BeatTheBookie](https://github.com/Lisandro79/BeatTheBookie)). Traduzido para odds de ténis já sem margem (~3 pp de margem por lado), fica **EV ≥ 0,02/(p_justa − 0,02)**. Um "+5%" fixo é, por isso, mais exigente do que Kaunitz nos favoritos e **mais permissivo nos azarões**.

A proposta junta as duas regras e acrescenta uma sobretaxa quando a recolha é antiga:

**EV_mín,cons = max(5%, 0,02/(p_justa − 0,02)) + 2 pp** se a recolha tiver mais de 3 h ou o jogo começar mais de 12 h depois dela.

O valor dos 2 pp é opinião. As caudas medidas acima apoiam-no, mas não o calibram.

| p justa | 0,70 | 0,60 | 0,50 | 0,40 | 0,33 | 0,25 |
|---|---|---|---|---|---|---|
| EV mínimo | 5,0% | 5,0% | 5,0% | 5,3% | 6,5% | 8,7% |
| Odd mínima (recolha recente) | 1,50 | 1,75 | 2,10 | 2,63 | 3,23 | 4,35 (fora de 1,40–4,00) |
| Odd mínima (+2 pp, recolha antiga) | 1,53 | 1,78 | 2,14 | 2,68 | 3,29 | 4,43 |

**Estes números assumem a melhor odd de dezenas de casas, e o utilizador tem quatro casas "moles".** Nos mesmos dados, a Bet365 ficou ≥ 1,05/p_média **só 19 vezes em oito anos** (odds 1,40–4,00). A vantagem contra a Pinnacle foi de +0,7% (SE 3,0%), com mediana −0,5% ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)). O próprio backtest do repositório deu −5,0% (±9,7%) para "Bet365 acima da Pinnacle a 3%" (`docs/backtest.md`). Em mais de 60 000 encontros ATP e WTA, o **ROI foi negativo apostando numa só casa** e só passou a positivo com a melhor odd de muitas casas ([Angelini, Candila & De Angelis 2022](https://www.sciencedirect.com/science/article/abs/pii/S0377221721003234)). As casas portuguesas pagam ainda um imposto especial de jogo online (IEJO) de 8% sobre o volume apostado. Há fontes que falam antes em 8–16% da receita bruta ([apostaslegais-pt](https://apostaslegais-pt.com/articles/imposto-apostas-desportivas-portugal/)). Seja qual for a base, as odds normais ficam estruturalmente baixas. Conclusão: as odds portuguesas que passarem o filtro serão raras, e uma parte desproporcionada será odd desatualizada ou erro. É o pré-jogo que tem de as confirmar.

**As promoções são a fonte de valor mais realista, e têm de passar pelo mesmo filtro.** Um aumento de odd só vale se a odd aumentada for ≥ (1 + EV_mín)/p_justa. Muitos aumentos de 0,05–0,20 só aproximam a odd do preço justo. As bolsas de apostas são ilegais em Portugal ([apostalegal.pt](https://apostalegal.pt/betfair-portugal/)), por isso uma freebet não pode ser convertida com lay (apostar contra a seleção numa bolsa). O valor esperado por euro de freebet é **p_justa × (odd − 1)**: cerca de 47% à odd 2,0 e 75% à odd 5,0, com ~7% de margem. Isto choca com a faixa de odds 1,40–4,00, e a decisão é do utilizador. Um desafio do tipo "aposta 5 € a ≥ 2,00 e ganha 20 € em freebets" pode ter EV positivo, mas uma stake de 5 € excede o teto de 10% (2 €): pela regra 3, não se entra. Para adiar a limitação da conta, a única tática sem problemas éticos nem legais é repartir as apostas pelas quatro casas. Contas múltiplas, contas de terceiros ou VPN violam os termos e o regime jurídico do jogo online (RJO).

## Um quarto de Kelly sobre o EV aparente pode ser quase meio Kelly real

**Escolher a maior diferença de preço garante que o EV real fica abaixo do estimado, mesmo que as estimativas não tenham viés.** É a "maldição do otimizador" ([Smith & Winkler 2006](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0451)). Numa simulação própria, com a melhor de cinco casas e um limiar de 3%:
- com um erro de ~1 pp no preço justo, **~71% do EV aparente é real**;
- com ~2 pp de erro, só **~35%**, e as apostas com EV aparente de 3–5% têm EV real de **~+1%**;
- com 3 pp de erro e uma só casa, o EV real fica negativo.

Uma aproximação bayesiana reproduz razoavelmente a simulação:

**EV_real ≈ μ₀ + k(EV_ap − μ₀)**, com **k = σ²_casas/(σ²_casas + σ²_preço justo)** e μ₀ ≈ −5,7% (o EV esperado de uma odd de casa "mole" antes de se escolher).

Para σ = 0,04 prevê +4,1%, e a simulação dá +4,0%. Os valores dos parâmetros são pressupostos da simulação.

**Com incerteza na probabilidade, a stake deve encolher.** Baker & McHale mostram que o Kelly "cru" rende pior fora da amostra do que dentro dela, e que contrair a aposta o melhora, **incluindo em dados de ténis**. A contração ótima aumenta com a incerteza ([Baker & McHale 2013](https://pubsonline.informs.org/doi/abs/10.1287/deca.2013.0271)). Uma derivação própria no mesmo espírito dá **k\* = μ²/(μ² + τ²)**, em que τ é o desvio-padrão do erro do EV. Com τ ≈ μ, a contração é para metade. Convém separar duas coisas: corrigir o **viés** de seleção (encolher o EV) e contrair pela **variância** que resta (a fração de Kelly). Hoje, o 1/4 fixo mistura as duas.

O erro no EV transforma-se em risco de drawdown. Com vantagem conhecida, a probabilidade de a banca **alguma vez** cair para a fração x é **x^(2/c − 1)**, em que c é a fração do Kelly real. É coerente com os valores de Thorp: 50% de probabilidade de um drawdown de 50% com Kelly completo, e 12,5% com meio Kelly ([MacLean, Thorp & Ziemba](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)). Se θ = EV real / EV aparente, apostar 1/4 do Kelly aparente é apostar c = 0,25/θ do Kelly real:

| θ (EV real / EV aparente) | 1,00 | 0,70 | 0,56 (consenso, à mesma hora) | 0,50 | 0,40 |
|---|---|---|---|---|---|
| Fração do Kelly real | 0,25 | 0,36 | 0,45 | 0,50 | 0,63 |
| P(banca alguma vez ≤ 50%) | **0,8%** | 4,1% | **9,1%** | 12,5% | 21,8% |

Com θ ≤ 0,125 o crescimento esperado passa a negativo. A proposta é apostar **1/4 de Kelly sobre um EV calibrado com os próprios dados**:
- regressão OLS CLV = â + k̂ · EV_ap;
- peso w = n/(n + 50);
- **k = w·k̂ + (1 − w)·0,5** e **a = w·â**;
- EV_cal = a + k·EV_ap;
- stake = banca × 0,25 × max(0, EV_cal)/(o − 1), seguida dos tetos e do arredondamento para baixo.

O prior k₀ = 0,5 e o peso n₀ = 50 são opinião, escolhidos para ficar perto do 0,557 medido. Na simulação Monte Carlo do sistema atual, encolher o EV para metade:
- leva a probabilidade de stop-loss a ~0% **mesmo com EV real de −2%** (hoje, 9,8%);
- mas reduz para cerca de metade o número de apostas feitas;
- e baixa a banca mediana final de 34,92 € para 25,26 € **se a vantagem for real**.

Enquanto a vantagem não estiver provada, a proteção vale mais do que o crescimento.

**Com muitas apostas em simultâneo, a fórmula por aposta serve; o que falta é um teto total.** Com vantagens pequenas, o Kelly simultâneo exato só se afasta do Kelly isolado na terceira ordem ([Long 2026](https://arxiv.org/abs/2603.26620); [Whitrow 2007](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9876.2007.00594.x)). Só diverge quando a soma das frações de Kelly completo se aproxima de 100% da banca. Um quarto desse total fica sempre abaixo de 25%. Daí a regra: **stakes pendentes + novas ≤ 25% da banca**; se passar, multiplica-se cada nova stake por (25% − pendente)/(soma das novas) e arredonda-se para baixo.

A heurística de fórum Π(1 − kⱼ) é demasiado conservadora: dá 0,435 quando o ótimo exato dá ~0,95. Na simulação, a exposição média foi de 15,8% por dia, por isso o teto só atua em dias de 25–30 apostas. O código atual calcula a stake sobre a banca liquidada e ignora as pendentes. Como a regra 10 diz "sem limite diário de exposição", este teto é uma decisão do utilizador. Pode apresentá-lo como limite matemático, não como limite discricionário.

**O arredondamento para baixo em passos de 0,10 € já funciona como uma contração extra**, equivalente a ~0,8 × 1/4 de Kelly. Uma aposta à odd 3,5 com EV de 3% dá um alvo de 0,06 € e é recusada. Passar a cêntimos aumentaria o risco: com EV real zero, a probabilidade de stop-loss subiria de 2,8% para 9,5%. O arredondamento deve continuar para baixo, e nunca para cima até ao mínimo. Chegar ao stop-loss é sobretudo prova de que não há vantagem: é 10 a 100 vezes mais provável com EV −2% do que com vantagem real. As apostas cuja stake fica abaixo do mínimo devem ir na mesma para o `recomendacoes.csv`, com stake 0, para a amostra de CLV crescer sem arriscar dinheiro. Quanto às múltiplas, o ganho teórico é de quarta ordem na vantagem, por isso a regra atual (uma por dia, teto de 5%) não custa nada de relevante.

## No ténis, a regra da casa e o escalão do torneio mudam o preço justo

**A Pinnacle e as casas portuguesas não liquidam o mesmo acontecimento.**
- **Pinnacle:** as apostas no vencedor mantêm-se se ficou completo pelo menos um set, e quem avança é declarado vencedor ([Pinnacle Help](https://en.help.pinnaclesports.com/en/support/solutions/articles/1000115722-how-is-retirement-or-disqualification-of-tennis-players-treated-)). Handicaps e totais de jogos são sempre anulados quando há desistência.
- **Casas portuguesas:** seguem "o que não está determinado é anulado". Uma desistência anula a aposta no vencedor, mesmo a 6-0 5-0. Os totais já ultrapassados são liquidados. Isto consta da ajuda oficial da [Solverde](https://ajuda.solverde.pt/hc/pt/articles/22119037510161-O-que-acontece-%C3%A0-minha-aposta-se-um-tenista-abandonar-o-jogo) e da [Betano](https://support.betano.pt/hc/pt/articles/16435365475357-O-que-%C3%A9-uma-Aposta-Anulada-e-por-que-raz%C3%B5es-acontece), num guia sobre a [Betclic](https://apostasdescomplicadas.com/handicap-tenis-desistencia-regras/) e no regulamento do [Placard](https://www.bonuseapostas.com/os-motivos-para-a-apostas-ser-cancelada-no-placard/). O texto literal de cada casa não foi verificado.

Seja C o acontecimento "o encontro chega ao fim" e r_B a probabilidade de B desistir depois do 1.º set. Então:
- pela regra da Pinnacle: p_pin(A) = P(A ganha ∧ C) + r_B;
- numa casa portuguesa: **p_PT(A) = (p_pin(A) − r_B)/(1 − r_A − r_B)**.

As taxas de base são conhecidas:
- **1,56 desistências por 1 000 jogos nos homens e 1,36 nas mulheres**, nos Challengers, ITF e WTA 125 ([PLOS One 2024](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0304638));
- 1,03 nos Masters 1000 e 1,65 nos WTA Premier ([Oliver et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1002/ejsc.12177));
- tendência de subida de pelo menos 25% no ATP e 50% no WTA em 25 anos ([UVic](https://www.uvic.cat/en/news/retirements-from-matches-by-professional-tennis-players-have-increased-by-25-on-the-mens)).

Numa estimativa própria, isto dá ~3% dos encontros de Challenger e ~2% do ATP. Com um risco simétrico de 1–1,5% por jogador, a regra da Pinnacle aproxima o preço do favorito de 50%, em 0,4–0,9 pp (com o favorito a 0,70–0,80). O favorito vale assim +0,6% a +1,1% de EV a mais numa casa portuguesa, e o azarão vale menos.

**Com risco assimétrico o efeito é grande.** Se A for frágil (5% de desistência depois do 1.º set) e B saudável (1%), e B ganhar 40% dos encontros que chegam ao fim, a regra da Pinnacle dá a B 42,6%. **O EV de apostar no jogador saudável numa casa portuguesa fica sobrestimado em ~6,5%**, mais do que todo o limiar. O consenso do tennisexplorer mistura casas com as duas regras, o que dilui o efeito, mas o sinal é o mesmo.

Os prazos de adiamento também diferem: 24 h na Betano e na Solverde, 48 h na Betclic e no Placard. Isto só importa nas entradas live. A Betano reserva-se ainda o direito de anular apostas feitas com "erros manifestos" de odd. Um EV aparente acima de ~15% é, por isso, mais provavelmente um erro ou uma odd desatualizada do que uma oportunidade. A correção do estudo da "buzz" da WTA mostra o mesmo padrão: ROIs de 17–29% que se deviam sobretudo **a uma única odd errada** ([arXiv 2306.01740](https://arxiv.org/abs/2306.01740)).

**Os escalões mais baixos juntam preços "moles" e risco de integridade.**
- Em 2025, o ténis gerou **74 dos 300 alertas de apostas suspeitas da IBIA (25%)**, e foram sancionados 10 jogadores e 6 árbitros ([Yogonet](https://www.yogonet.com/international/news/2026/02/04/117454-ibia-reports-300-suspicious-betting-alerts-in-2025-up-29-)).
- No 3.º trimestre de 2025, a maioria dos casos veio de competições de escalão baixo ([Tribuna](https://tribuna.com/en/betting/news/2025-12-05-tennis-overtakes-football-in-suspicious-betting-alerts-ibia-reports/)).
- Os alertas disparam com grandes montantes apostados em azarões ([ITIA](https://www.itia.tennis/news/itia-news/what-is-a-betting-alert/)).
- A divergência entre modelos e odds já foi aceite como prova no Tribunal Arbitral do Desporto ([Forrest & McHale 2019](https://academic.oup.com/imaman/article-abstract/30/4/431/5522261)).

No código, `incluir_challengers: true` deixa entrar também os ITF, porque a expressão regular é a mesma (`challenger|itf`). Para um apostador que parte do preço, a resposta racional é evitar:
- excluir os ITF por omissão;
- exigir mais aos azarões dos Challengers;
- saltar o encontro quando o consenso se mover ≥ 5 pp para o azarão entre recolhas, sem notícia pública.

Pelas medições acima, o último filtro corta perto de 4% dos encontros.

**Os mercados secundários só podem ter preço de modelo, e o modelo perde para o mercado.** O modelo de sets independentes falha de forma sistemática. Num teste próprio com 8 596 encontros ATP à melhor de 3:
- o favorito ganhou 2-0 em **45,9%** dos casos, contra 41,3% previstos;
- houve três sets em 36,9%, contra 44,6% previstos;
- o total de jogos ficou **1,3 jogos abaixo** do previsto.

Uma mistura normal na diferença de serviço, com σ ≈ 0,065, corrige quase tudo ([cálculo próprio sobre ATPBetting](https://github.com/edouardthom/ATPBetting)). É coerente com a dependência entre sets documentada na literatura ([Depken et al. 2022](https://journals.sagepub.com/doi/abs/10.1177/15270025221085715)). Mesmo assim, num projeto público, o preço sem margem do mercado foi **melhor previsor do que o modelo em todos os mercados secundários**. Apostar pelo modelo à odd da Bet365 deu ROI negativo em todos, com −16,8% no set betting ([qitaoshi/tennis-model-v2](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/multi_market_clv.md)).

A implementação stdlib das notas (tie-break de 7 pontos em todos os sets à melhor de 3; o de 10 pontos só nos Grand Slams) serve para responder a "e o Faria ganhar 2-0?" e para recusar valor falso. Não serve para gerar apostas, a não ser com limiares muito mais altos.

## Os subagentes rendem mais como veto do que como previsores

**No ténis, o mercado já contém quase toda a informação disponível.**
- Em 25 204 encontros ATP e 13 755 WTA, nenhum método de machine learning passou dos ~70% de acerto, e juntar dados dos jogadores não acrescentou nada ao que as odds já sabiam ([Wilkens 2021](https://journals.sagepub.com/doi/10.3233/JSA-200463)).
- O consenso das casas foi o mais exato de 11 modelos (72%) ([Kovalchik 2016](https://vuir.vu.edu.au/34652/1/jqas-2015-0059.pdf)).
- Das 40 regras de aposta testadas, os lucros aparentes desaparecem quando se corrige a pesca de dados (testar muitas regras até alguma dar lucro por acaso) ([Lyócsa & Výrost 2018](https://www.tandfonline.com/doi/abs/10.1080/00036846.2017.1394973)).

Os ângulos favoritos dos analistas não resistem:
- a vantagem de apostar no jogador mais fresco nos Grand Slams vem de **76 apostas (+3,7%)** ([Pinnacle](https://www.pinnacle.com/betting-resources/en/tennis/analysing-fatigue-at-grand-slams/m3djq42thz47zk4n));
- o estudo sobre jet lag mediu fisiologia em 52 jogadoras, não odds ([Maynard et al. 2026](https://doi.org/10.1177/19417381251387717));
- para a motivação de fim de época, os pontos a defender, as mudanças de piso e os qualificados, não se encontrou nenhuma medição no mercado de apostas.

O `analista-tenis.md` apresenta hoje o calor, o jet lag, a motivação e os "qualificados cujas odds iniciais demoram a acompanhar" como ângulos. Devem passar a ser apenas razões para rejeitar.

**Os estudos de 2026 com LLMs apontam todos no mesmo sentido.**
- No Mundial 2026, o Brier do mercado foi 0,469 e o melhor agente teve 0,4705. **Apostar sempre no favorito do mercado rendeu +1 041 $, mais do que qualquer agente.** As apostas contra o mercado deram prejuízo a três dos quatro modelos ([FIFA2026LLM](https://github.com/graphuofm/FIFA2026LLM)).
- No KellyBench, todos os modelos perderam dinheiro; o melhor ficou em **−8%** ([arXiv 2604.27865](https://arxiv.org/abs/2604.27865)).
- O raciocínio longo agravou a sobreconfiança (ECE 0,395) ([KalshiBench](https://arxiv.org/abs/2512.16030)).
- A única política com retorno positivo foi a que tornou a seleção e a stake determinísticas, sem que o LLM as pudesse contornar ([Belief-to-Trade](https://arxiv.org/abs/2607.03015)).
- Fazer a média simples entre humano e máquina foi melhor do que deixar o LLM atualizar a sua própria previsão ([Schoenegger et al.](https://www.science.org/doi/10.1126/sciadv.adp1528)).

Daqui resulta um ajuste **assimétrico e imposto pelo código**. Por omissão, o ajuste só pode ser ≤ 0, ou seja, reduzir a probabilidade ou vetar. O ajuste positivo só se liga se o `banca.py avaliacao` mostrar um Brier do agente abaixo do do mercado em pelo menos 100 recomendações liquidadas. Os subagentes passam a responder a perguntas fechadas: há desistência ou lesão depois da hora da recolha? A regra da casa difere? A odd tem mais de 60 minutos?

**O momento da aposta também conta.** A Pinnacle publica as primeiras linhas com limites baixos, os limites sobem até ao início, e as outras casas seguem os seus movimentos ([Pinnacle](https://www.pinnacle.com/betting-resources/en/betting-strategy/market-movement-in-betting/4732xnzxpqpzrff5)). A vantagem de um apostador que compara preços é a casa atrasada. Por isso deve apostar-se **logo** que a odd portuguesa chega à odd mínima. No pré-jogo, recalcula-se a odd mínima com a última recolha e cancela-se se o consenso tiver andado contra a seleção.

## Conclusão

A investigação reforça a arquitetura atual: preço primeiro, stakes determinísticas e LLM como filtro. O que mudou foi o terreno onde ela assenta. O método foi desenhado em torno da Pinnacle, e a Pinnacle desapareceu dos dados públicos de ténis em janeiro de 2026. O agente trabalha, na prática, contra um consenso com 7% de margem, publicado com horas de atraso e sem fecho, e esse caminho está hoje cego para o CLV. O ponto fraco já não é "como tirar a margem" (Shin, power e odds-ratio empatam). É contra que preço se compara e como se mede o resultado.

Tudo depende de uma incógnita que nenhuma fonte pública resolve: com que frequência uma das quatro casas portuguesas fica 5% ou mais acima de um consenso desatualizado **por uma razão que não seja má notícia**. Só os registos do utilizador podem responder. O plano racional é tratar as próximas 100 recomendações como uma experiência com stakes mínimas, medidas por M e pelo fecho da Betfair, com erro-padrão, e deixar a regra de paragem decidir. Se M sair ≤ 0, a conclusão honesta é que o caminho dos alvos não funciona com quatro casas portuguesas. Restariam então duas opções: uma fonte com Pinnacle (a The Odds API) ou jogar só promoções.

## Melhorias por ordem de prioridade

Força da evidência:
- **Forte:** estudo revisto por pares com amostra grande, matemática estabelecida ou verificação direta.
- **Moderada:** cálculo próprio em dados públicos, preprint, ou estudo de praticante com amostra grande.
- **Opinião:** inferência não testada, ou parâmetro escolhido.

| # | Melhoria | Fórmula ou regra | Evidência | Onde mexe |
|---|---|---|---|---|
| 1 | **Medir o CLV no caminho do consenso** | Guardar cada recolha (ou reconstruí-las do histórico git da fonte), com p₀, a hora da recolha e a idade. Fecho = última recolha s\* com s₀ < s\* ≤ início. M = p\*/p₀ − 1; CLV_cons = (1+EV₀)(1+M) − 1. Qualidade: g ≤ 2 h boa, 2–6 h fraca, > 6 h ou s\* = s₀ "não medido". CLV_fiável = o·p_BFE,fecho − 1 obtido depois do jogo (BFEW/BFEL no ténis; BFEC/AvgC no futebol). A regra 6 usa o CLV_fiável e, sem ele, M; nunca os mistura | Moderada (CLV→lucro: Buchdahl); o método das recolhas é inferência | `scripts/odds.py` (alvos, fecho, nova fonte de fecho), `scripts/banca.py` (colunas de REC, `regra_paragem`), skills `pre-jogo` e `resultado`, `CLAUDE.md` regra 6 |
| 2 | **Erro-padrão e segmentos na avaliação** | m, s, SE = s/√n, IC95 = m ± 1,96·SE; n necessário ≈ (2s/m)². Por circuito (ATP/WTA/Challenger), favorito/azarão, casa e fonte do fecho, com a cobertura de cada fecho | Forte (estatística padrão) | `scripts/banca.py avaliacao` |
| 3 | **Registar tudo o que passa no filtro** | Candidatas com stake < 0,10 € gravadas com stake 0. Nos alvos, pedir ao utilizador a odd que encontrou em cada casa, mesmo abaixo da mínima (registo "sombra") | Opinião (desenho) | `banca.py recomendar` (opção `--sombra`), skill `plano-diario`, `CLAUDE.md` (Fluxos) |
| 4 | **Limiar contra o consenso que sobe com a odd e com a idade** | EV_mín = max(5%, 0,02/(p − 0,02)) + 2 pp se a recolha tiver > 3 h ou o jogo começar > 12 h depois dela. Odd mínima = (1 + EV_mín)/p | Moderada (Kaunitz; ATP por faixa de odd; caudas medidas); os 2 pp e as 3 h são opinião | `banca.py ev_minimo` (passa a receber p e a idade), `odds.py alvos`, `config.json` (`buffer_consenso_pp`, `sobretaxa_idade_pp`, `idade_recolha_h`), `docs/comum.md` (fórmula da odd mínima) |
| 5 | **Stake sobre o EV calibrado** | EV_cal = a + k·EV_ap; k̂ e â por OLS de CLV sobre EV_ap; w = n/(n+50); k = w·k̂ + (1−w)·0,5; a = w·â. Stake = banca·0,25·max(0, EV_cal)/(o − 1), depois o teto de 10% e o arredondamento para baixo | Forte no princípio (Baker & McHale; Smith & Winkler); k₀ e n₀ são opinião | `banca.py calcular_stake` e `validar`, `config.json` (`k_prior`, `n0_prior`), `CLAUDE.md` regra 4 ("1/4 de Kelly sobre o EV calibrado") |
| 6 | **Filtros determinísticos de armadilha** | EV_ap > 15% → "suspeito" (só com confirmação manual). Movimento do consenso ≥ 5 pp para o azarão sem notícia → saltar o encontro. `incluir_itf: false`, separado de `incluir_challengers`. +1 pp de exigência nos azarões dos Challengers | Moderada (IBIA/ITIA, correção Ramirez, termos da Betano); os limiares são opinião | `odds.py alvos` (expressão regular), `config.json`, agentes `gestao-risco` e `noticias-lesoes` |
| 7 | **Ajuste por desistência nas casas portuguesas** | p_PT(A) = (p_ref(A) − r_B)/(1 − r_A − r_B), com r por jogador ≈ 1% no ATP e ≈ 1,5% nos Challengers/WTA. Com risco físico assimétrico: rejeitar a aposta no adversário saudável ou recalcular. Sem unders de jogos com dúvida física. Tabela de regras por casa (adiamentos: 24 h na Betano e na Solverde, 48 h na Betclic e no Placard) | Forte nas taxas (PLOS One; Oliver 2024); moderada nas regras (resumos, confirmar à mão); a fórmula é inferência | `docs/comum.md` (tabela de regras), agentes `analista-tenis` e `noticias-lesoes`; opcionalmente `odds.py` |
| 8 | **Subagentes só como veto** | Ajuste ≤ 0 por omissão (`ajuste_positivo: false`). O ajuste positivo só se liga com Brier do agente < mercado em ≥ 100 liquidadas. Fadiga, jet lag, calor, motivação e qualificados passam a ser só razões para rejeitar | Moderada (WC2026, KellyBench, Belief-to-Trade); forte na eficiência do ténis (Wilkens, Kovalchik) | `banca.py validar`, `config.json`, `docs/comum.md`, `.claude/agents/analista-tenis.md`, `CLAUDE.md` (Método) |
| 9 | **Corrigir as fontes e a documentação** | `apis.md`: aimidas1 de 2 em 2 dias e sem Champions; TML parado a 27/01/2026; Sackmann apagado, com espelho Aneeshers (CC BY-NC-SA, até junho); tennis-data sem Pinnacle desde 13/01/2026; football-data 2026/27 sem Pinnacle (fecho no Char2mant); `proofodds` é isco de malware; não integrar `Eth91`. `comum.md`: retirar "sem API… nada entra no plano". `odds.py`: retirar ou redefinir a ★ do ténis. Champions: consenso a 5% ou mais, ou de fora | Forte (verificação direta a 25/09/2026) | `docs/apis.md`, `docs/comum.md`, `odds.py` (`FONTES`, `fontes`, `alvos`), skill `plano-diario` |
| 10 | **Teto de exposição total** | Pendentes + novas ≤ 25% da banca; acima disso, escalar as novas por (25% − pendente)/(soma das novas) e arredondar para baixo | Moderada (Whitrow; Long 2026; cálculo próprio); choca com a regra 10, decide o utilizador | `banca.py calcular_stake` (descontar pendentes), `config.json` (`teto_total_pct`), `CLAUDE.md` regra 10 |
| 11 | **Preço justo "pior caso", nunca multiplicativo** | Para o lado apostado, p = min(p_Shin, p_power), com power pᵢ = rᵢ^(1/k) e Σp = 1 | Moderada (Clarke 2017; Štrumbelj 2014; cálculo próprio) | `odds.py` (nova função `power`), `docs/comum.md` |
| 12 | **Pré-jogo e momento da aposta** | Apostar logo que a odd portuguesa ≥ mínima. No pré-jogo, recalcular a mínima com a última recolha e cancelar se o consenso tiver andado > 2 pp contra a seleção | Moderada (mecânica do mercado da Pinnacle); os 2 pp são opinião | skill `pre-jogo`, `CLAUDE.md` (Fluxos) |
| 13 | **Promoções dentro das regras** | Aumento de odd só se odd ≥ (1 + EV_mín)/p_justa. Freebet sem cobertura: valor ≈ p_justa·(o − 1) por euro. Nunca uma stake acima do teto. Freebets registadas à parte (tipo próprio, fora da banca) | Moderada nas fórmulas; fraca nos termos (por confirmar) | agente `estatistica-dados`, `banca.py` (tipo `freebet`), `CLAUDE.md` |
| 14 | **Preços de mercados secundários só como informação** | p do vencedor → d por bisseção, com L por circuito e piso (ATP em duro 1,28, em terra 1,25; Challenger 1,22; WTA ~1,14, não verificado); mistura σ ≈ 0,065; nunca o modelo iid. Aposta só com EV ≥ 8% (sets), ≥ 10% (2-1 e 1-2), ≥ 6% (totais e handicap). Teste: 25,683 jogos com pA = pB = 0,64 | Moderada (teste próprio com 8 596 encontros; qitaoshi); os limiares são opinião | novo `scripts/tenis.py` ou `odds.py sets`, agente `analista-tenis`, `docs/comum.md` |

## Perguntas em aberto que só os dados do utilizador resolvem

1. Com que frequência a odd de cada uma das quatro casas fica igual ou acima da odd mínima do consenso, e em que casa? Isto exige registar também as odds vistas e não apostadas.
2. Qual é o M médio, e o CLV contra o fecho da Betfair, das primeiras 100 recomendações, com o seu intervalo de confiança? É o que a regra de paragem decide.
3. Qual é o k real, isto é, a inclinação do CLV sobre o EV aparente, por segmento: ATP/WTA contra Challenger, favorito contra azarão? Serve para substituir o prior de 0,5.
4. O valor concentra-se nas recolhas com mais de 3 h? A resposta calibra a sobretaxa de idade, e o histórico git da fonte permite testá-lo já.
5. Quais são as stakes mínimas e os incrementos reais da Betclic, da Betano e do Placard? Para a Solverde, só há um resumo que indica 0,10 €. E qual é o texto literal das regras de desistência e de adiamento das quatro casas?
6. Alguma casa limita a conta, e ao fim de quantas apostas ou com que CLV?
7. Decisões do utilizador: aceita o teto de 25% de exposição (regra 10)? Que faixa de odds admite para usar freebets?
