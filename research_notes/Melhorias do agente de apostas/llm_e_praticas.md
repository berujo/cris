# LLMs em apostas desportivas (evidência 2025–2026) e práticas para uma banca pequena em Portugal

*Nota de método (Set/2026):* o proxy desta sessão bloqueou arxiv.org, alphaxiv, huggingface, gr.inc, decrypt.co, eco.sapo.pt, betclic.pt, srij.turismodeportugal.pt, pmc.ncbi.nlm.nih.gov e mcml.ai. Só consegui abrir diretamente o GitHub (por exemplo, o repositório do WC2026-Agents). Os números dos papers do arXiv e das páginas bloqueadas vêm dos resumos devolvidos pelo motor de pesquisa, que citam essas páginas; os URLs indicados são as fontes primárias. Os números críticos devem ser confirmados no PDF antes de serem citados como definitivos.

---

## A1. Que estudos de 2025–2026 mediram LLMs a apostar ou a prever contra o mercado, e com que resultados?

### Takeaway
Em todos os testes com dinheiro simulado e com a odd real, os LLMs **não batem o mercado em calibração (Brier)**. Em média, **perdem dinheiro quando decidem sozinhos**: no KellyBench, todos os modelos tiveram ROI negativo, o melhor com −8%. No Mundial 2026, nenhum agente bateu o Brier do mercado, e apostar sempre no favorito do mercado rendeu mais do que qualquer um deles. Os ROI positivos isolados assentam em poucas apostas e são compatíveis com ruído. Os melhores resultados aparecem quando uma camada determinística separa a previsão da decisão de apostar e de dimensionar a stake.

### Cited Findings
**KellyBench (General Reasoning, abr/2026; simulação sequencial da Premier League 2023/24; dados históricos, estatísticas avançadas, onzes e odds públicas; os agentes têm de construir modelos de ML e procurar edge)**
- O resultado é determinístico, calculado a partir dos resultados e das odds, sem juízes LLM. — [arXiv 2604.27865](https://arxiv.org/abs/2604.27865); [General Reasoning blog](https://www.gr.inc/releases/introducing-kellybench)
- "Every model we evaluate on KellyBench loses money on average over the course of the season for five seeds, and several models experience ruin." O melhor, o GPT-5.4, teve um ROI médio de **−8%**. — [arXiv 2604.27865](https://arxiv.org/abs/2604.27865)
- O Claude Opus 4.6 perdeu **−11%** em média. Na versão original, só o Opus 4.6 e o GPT-5.4 evitaram a ruína nas 5 seeds; numa atualização, o GPT-5.5, o Claude Opus 4.7, o GLM-5.2 e o Kimi K2.6 também a evitaram. — resumos da pesquisa sobre [Decrypt](https://decrypt.co/364406/ai-beat-sports-betting-market-top-8-models) e [arXiv](https://arxiv.org/abs/2604.27865)
- Há uma rubrica de "sofisticação" do processo, feita com peritos de fundos de apostas quantitativos. As fontes não batem certo no tamanho: o abstract fala em 52 pontos e o resumo da Decrypt em 44. O melhor foi o Opus 4.6, com 32,6%, menos de um terço dos pontos. Uma sofisticação maior previu menos falências (p = 0,008) e esteve correlacionada com melhores retornos. — [Decrypt](https://decrypt.co/364406/ai-beat-sports-betting-market-top-8-models); [arXiv](https://arxiv.org/abs/2604.27865). *Discrepância 52 vs 44 pontos por resolver.*
- O ambiente está disponível publicamente em [OpenReward](https://openreward.ai/GeneralReasoning/KellyBench).

**WC2026-Agents: "FIFA World Cup 2026 as a Contamination-Free Benchmark for LLM Forecasting Agents" (arXiv 2607.17765, jul/2026; os 104 jogos; ciclo pesquisar–agir–refletir; odds 1X2 reais da DraftKings sem margem). Repositório lido diretamente.**
- Os modelos foram o Claude Opus 4.8, o ChatGPT (GPT-5.5, raciocínio alto), o Gemini 3.1 Pro e o Grok (Expert). Cada um dava probabilidades 1X2 e apostava até 100 $ por jogo, com stake escolhida por ele. — [GitHub graphuofm/FIFA2026LLM](https://github.com/graphuofm/FIFA2026LLM)
- **Brier:** mercado 0,469; Claude 0,4705; Grok 0,4706; ChatGPT 0,4729; Gemini 0,4828. Nenhum agente bateu o mercado. — [GitHub](https://github.com/graphuofm/FIFA2026LLM)
- **ROI:** Grok +10,3% (+650 $, 104 apostas); ChatGPT +8,0% (+118 $, 55 apostas); Gemini +3,7% (+322 $, 103 apostas); Claude −18,1% (−275 $, 73 apostas). — [GitHub](https://github.com/graphuofm/FIFA2026LLM)
- "Backing the market favourite in every match made +$1,041", mais do que qualquer agente. — [GitHub](https://github.com/graphuofm/FIFA2026LLM); [arXiv abstract](https://arxiv.org/abs/2607.17765)
- **Apostar contra o mercado:** estas apostas ganharam 21%–40% das vezes, contra 48%–69% quando seguiam o mercado. Deram prejuízo ao Claude (−167 $), ao Gemini (−112 $) e ao ChatGPT (−38 $); só as 5 apostas contrárias do Grok deram lucro (+64 $). O abstract diz que "fading the market is unprofitable for all four". — [GitHub](https://github.com/graphuofm/FIFA2026LLM); [arXiv](https://arxiv.org/abs/2607.17765)
- **Uso do mercado no raciocínio:** o Claude citou as odds em 100% das previsões, o ChatGPT em 92%, o Grok em 63% e o Gemini em 12%. — [GitHub](https://github.com/graphuofm/FIFA2026LLM)
- **Pontos cegos:** os agentes deram a mesma escolha principal em 92% dos jogos (96 de 104). Nenhum escolheu o empate como favorito mais de 4 vezes, apesar de 24 dos 104 jogos terem acabado empatados aos 90'. Os empates foram 22 dos 32 erros. — [GitHub](https://github.com/graphuofm/FIFA2026LLM)
- **Autoavaliação inconsistente:** perante uma escolha errada, o Gemini admitiu o erro 86% das vezes, o Grok 61%, o Claude 49% e o ChatGPT 36%. — [GitHub](https://github.com/graphuofm/FIFA2026LLM)

**Varghese, Bickmann & Sandmann: "Information Specialization and Constrained Synthesis in Multi-Agent LLM Forecasting" (arXiv 2609.12495, set/2026; estudo prospetivo dos últimos 56 jogos do Mundial)**
- Comparou um especialista quantitativo (estatística estruturada) com um especialista de notícias (conferências de imprensa e lesões recentes), seguidos de um crítico e de um meta-agente. — [arXiv 2609.12495](https://arxiv.org/abs/2609.12495); [Pith](https://pith.science/paper/2609.12495)
- O especialista de notícias teve a melhor utilidade Top-3 ponderada e **empatou com o mercado** na precisão de resultado exato. Mas os dois especialistas coincidiram em pelo menos 2 dos 3 resultados em 50 dos 56 jogos, e o meta-agente nunca gerou mais do que um resultado fora do conjunto dos especialistas. Ou seja, a especialização trouxe pouca diversidade real. — [arXiv 2609.12495](https://arxiv.org/abs/2609.12495)

**LLM-SoccerArena (arXiv 2607.24573; 7 LLMs, 104 jogos; desenho fatorial: modelo × pesquisa web × tipo de prompt × horizonte)**
- "LLMs with web access outperform those without, but only by a small margin", com uma melhoria de 0,023 no Brier. As odds das casas e os modelos de sports analytics servem de referência externa. — [arXiv 2607.24573](https://arxiv.org/abs/2607.24573); [MCML news](https://mcml.ai/news/2026-06-19-feuerriegel-ai-predicts-sports-results/)

**Outros benchmarks do Mundial 2026**
- **AI World Cup 2026** (arXiv 2608.03416): 10 assistentes fizeram uma previsão única antes do torneio. O GPT-5.5 Thinking ficou em 1.º (744 pontos) e foi o único a escolher a Espanha. É um benchmark de pontuação, sem comparação económica com as odds. — [arXiv 2608.03416](https://arxiv.org/abs/2608.03416)
- **MDPI Forecasting 8(5):78:** a pesquisa web aumentou a validade estrutural em 32–44 p.p. e reduziu as alucinações em 75–79%. O raciocínio sem fontes externas melhorou a consistência mas **aumentou as alucinações**. — [MDPI](https://www.mdpi.com/2571-9394/8/5/78)
- **WorldCupArena** (arXiv 2607.18084): as referências são o fecho da Pinnacle, o 538 SPI e o favorito sistemático. Mede ainda o "Research Uplift", isto é, quanto um agente com ferramentas ganha face a um contexto preparado. Não obtive os números finais: o anúncio no GitHub é anterior aos resultados. — [arXiv 2607.18084](https://arxiv.org/abs/2607.18084); [GitHub announcement](https://github.com/wzk1015/WorldCupArena/blob/main/docs/announcement.md)

**NBA e mercados de previsão**
- **"Playing the Odds: Agentic LLMs for Real-Time NBA Forecasting and Market Betting"** (abr/2026): agentes de recolha de informação e vários preditores LLM com papéis diferentes, agregados e depois apostados com Kelly fracionado em mercados binários. Os autores dizem que o LLM "can effectively complement traditional models". Não encontrei números. — [ResearchGate](https://www.researchgate.net/publication/403692431_Playing_the_Odds_Agentic_LLMs_for_Real-Time_NBA_Forecasting_and_Market_Betting)
- **Prophet Arena** (arXiv 2510.17638; 1 367 eventos da Kalshi até 11/10/2025): muitos LLMs têm erros de calibração pequenos e retornos de mercado "promissores". A vantagem do o3 vinha sobretudo das faixas extremas (0–10% e 90–100%). — [arXiv 2510.17638](https://arxiv.org/abs/2510.17638); [prophetarena.co](https://www.prophetarena.co/)
- **KalshiBench** (arXiv 2512.16030; 300 perguntas da Kalshi posteriores ao cutoff): há **sobreconfiança sistemática** em todos os modelos. O mais calibrado foi o Claude Opus 4.5 (ECE 0,120). O GPT-5.2-XHigh, com raciocínio longo, teve ECE 0,395: pôs 35% das previsões na faixa de 90–100% e acertou só 33,7% delas. Os autores concluem que o raciocínio longo reforça a hipótese inicial. — [arXiv 2512.16030](https://arxiv.org/abs/2512.16030)
- **"Beyond Forecasting: The Belief-to-Trade Layer"** (arXiv 2607.03015): há uma diferença grande entre boa calibração e resultado de trading. O Raven-Agent separa a previsão da camada de trading, e a seleção, o dimensionamento e o risco são componentes determinísticos "that the language model cannot override". Foi a única política com retorno positivo e com retorno positivo ajustado ao risco num replay controlado. Com o mesmo previsor, os controlos explícitos de seleção, stake e risco melhoraram os resultados. — [arXiv 2607.03015](https://arxiv.org/abs/2607.03015)
- **ForecastBench (FRI):** em out/2025, os LLMs estavam cerca de 0,017 pontos de Brier atrás dos superprevisores e melhoravam cerca de 0,016 por ano; a paridade foi extrapolada para nov/2026. — [FRI Substack](https://forecastingresearch.substack.com/p/llms-are-closing-the-gap-on-human). Nas perguntas de mercado, a diferença é maior: cerca de 0,039 para os superprevisores contra 0,059 para a melhor IA, segundo um agregador. — [Parallect (agregador)](https://parallect.ai/reports/ai-superforecasters-parity-may-2026-fb32ac); ver também [EA Forum síntese](https://forum.effectivealtruism.org/posts/Spyz3wESZu2eeqhDj/ai-forecasting-in-2026-what-11-analyses-say)
- **Ensembles (Schoenegger et al., Science Advances):** um ensemble de 12 LLMs foi estatisticamente indistinguível de uma multidão de 925 humanos. Mostrar a mediana humana ao LLM melhorou a precisão em 17–28%, mas **fazer simplesmente a média da previsão humana e da máquina foi melhor** do que deixar o LLM atualizar. — [Science Advances](https://www.science.org/doi/10.1126/sciadv.adp1528); [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/125626/)

### Inferences
- A evidência é consistente: **o mercado é o melhor previsor disponível** e o LLM, sozinho, fica abaixo. Isto dá razão ao método "preço primeiro" do agente e à regra de ajuste máximo de 3 p.p.
- Os ROI positivos do WC2026-Agents (+3,7% a +10,3% em 55–104 apostas) são estatisticamente indistinguíveis de zero. O próprio favorito teve +1 041 $, o que mostra quanto pesou a sorte do torneio. Não justificam confiar em probabilidades geradas por LLMs.
- O resultado do Schoenegger sugere que **misturar mecanicamente** o preço justo com um ajuste pequeno e limitado é mais seguro do que deixar o LLM "reescrever" a probabilidade depois de ver o preço. O teto de 3 p.p. aplicado por código segue esta lógica.
- O KellyBench e o Belief-to-Trade apontam para o mesmo: **o que protege a banca é o processo** (stake determinística, regras de risco que o LLM não pode contornar), não a inteligência do LLM. Isto apoia o `banca.py recomendar` como guardião.

### Gaps
- Não consegui abrir os PDFs (arXiv bloqueado). Falta confirmar os ROI por modelo no KellyBench para além do GPT-5.4 e do Opus 4.6, o tamanho da rubrica (44 vs 52 pontos) e os números completos do LLM-SoccerArena e do WorldCupArena (Brier contra o fecho da Pinnacle).
- Não encontrei nenhum estudo de 2025–2026 com LLMs em **ténis**, que é o foco atual do agente, nem na NBA com números públicos.
- O "Playing the Odds" (NBA) não tem métricas acessíveis.

---

## A2. Há evidência de que detetar notícias com um LLM dá edge lucrativo no desporto (a informação chega antes de a odd se mexer)?

### Takeaway
Não encontrei nenhum estudo rigoroso de 2025–2026 que mostre lucro sustentado por usar LLMs para detetar notícias antes das casas. As fontes de praticantes dizem que a janela nos mercados principais é de **segundos a minutos**. A evidência académica mostra ganhos pequenos da pesquisa web no Brier e nenhuma vantagem sobre o mercado. Onde há evidência de lucro, **a vantagem vem da velocidade de execução ou de preços desatualizados nas casas soft**, não da capacidade de prever.

### Cited Findings
- A pesquisa web melhora o Brier dos LLMs em apenas 0,023. — [LLM-SoccerArena, arXiv 2607.24573](https://arxiv.org/abs/2607.24573)
- O especialista de notícias (lesões, conferências de imprensa) só **empatou** com o mercado na precisão de resultado exato. — [arXiv 2609.12495](https://arxiv.org/abs/2609.12495)
- A pesquisa web reduz as alucinações em 75–79%. O raciocínio sem fontes aumenta-as. — [MDPI Forecasting](https://www.mdpi.com/2571-9394/8/5/78)
- **Opinião de praticantes:** as notícias de lesões na NFL são "one of the few moments when a sportsbook can briefly lag the market… for a few minutes the posted lines describe a game that no longer exists". — [OddsShopper](https://www.oddsshopper.com/articles/betting-101/betting-nfl-injury-news). Outra fonte diz que a janela nas casas principais "is measured in seconds, … not minutes". — [AgentBets.ai](https://agentbets.ai/news/nfl-preseason-injury-wave-agent-data-edge/). Sobre o uso de LLMs para ler jornalistas de clube antes da confirmação oficial, há ainda uma fonte comercial. — [Sports Command blog](https://blog.sportscommand.ai/injury-impact-betting-guide-how-the-analytics-team-reads-injury-news-before-the-market-does). *Nenhuma destas fontes é académica e várias vendem produtos.*
- **Polymarket:** segundo um agregador, 14 das 20 carteiras mais lucrativas são bots. Cita também um estudo (Della Vedova, 2026, com 222 milhões de trades) em que os traders com previsão acima do acaso têm retorno **negativo**, porque chegam tarde e pagam preços piores. A vantagem estaria na velocidade: os bots apostam depois de o resultado estar praticamente decidido. — [1023jack.com (agregador)](https://1023jack.com/market/are-polymarket-trading-bots-actually-profitable-the-math-behind-2026-s-predictio/); [NYC Servers blog](https://newyorkcityservers.com/blog/ai-agents-prediction-market-trading); [CoinDesk](https://www.coindesk.com/tech/2026/03/15/ai-agents-are-quietly-rewriting-prediction-market-trading). *Não verifiquei o estudo Della Vedova na fonte primária.*
- **Edge em casas soft com odds de consenso (sem LLM):** o Kaunitz, Zhong & Kreiner (2017) usou a média das odds das casas como probabilidade e apostou onde uma casa pagava bem acima dela. Com dinheiro real, em 5 meses, fez 265 apostas, acertou 47% e ganhou 957,50 $ (**+8,5%**). **As casas limitaram as contas** assim que perceberam. — [arXiv 1710.02824](https://arxiv.org/abs/1710.02824); [MIT Technology Review](https://www.technologyreview.com/2017/10/19/67760/the-secret-betting-strategy-that-beats-online-bookmakers/); [GitHub](https://github.com/Lisandro79/BeatTheBookie)

### Inferences
- Para o agente, a notícia vale mais como **filtro** do que como fonte de edge. Serve para cancelar uma aposta cujo "valor" se explica por uma notícia já no preço da Pinnacle mas ainda não na casa soft. Também serve para marcar como "odd desatualizada" uma candidata cuja odd na Pinnacle mexeu depois da notícia. Dá sinal real sobretudo para confirmar que o valor vem de uma casa atrasada e não de uma lesão que só a Pinnacle já refletiu.
- A cadência do agente (varreduras às 01:30, 07:30, 13:30 e 19:30, com o utilizador a apostar à mão) é incompatível com janelas de segundos ou minutos. Não se deve vender a deteção de notícias como fonte de lucro.
- O Kaunitz mostra que o edge estrutural contra casas soft existe mas tem prazo, por causa das limitações (ver B2).

### Gaps
- Não encontrei nenhum estudo académico de 2025–2026 que meça quanto tempo as odds demoram a reagir a notícias no ténis ou no futebol europeu, nem que teste um LLM como detetor de notícias com CLV medido.

---

## A3. Lições de desenho: como usar bem um LLM num pipeline "preço primeiro"

### Takeaway
O LLM deve ser um **filtro e um extrator** de factos verificáveis: lesões, retiradas, regras de liquidação, odds desatualizadas. Não deve gerar probabilidades. A probabilidade vem do mercado (Pinnacle sem margem), qualquer ajuste é pequeno e limitado por código, e a stake e o risco são determinísticos.

### Cited Findings
- **Não contrariar o mercado:** apostar contra o mercado deu prejuízo a 3 dos 4 agentes, e o favorito do mercado bateu todos. — [WC2026-Agents GitHub](https://github.com/graphuofm/FIFA2026LLM)
- **Evitar a sobreconfiança:** os modelos com raciocínio longo pioraram a calibração (ECE 0,395; 35% das previsões na faixa de 90–100%, com 33,7% de acerto). — [KalshiBench](https://arxiv.org/abs/2512.16030)
- **Separar crença de decisão:** a seleção, a stake e o risco devem ser determinísticos e impossíveis de contornar pelo LLM. — [Belief-to-Trade, arXiv 2607.03015](https://arxiv.org/abs/2607.03015)
- **O processo reduz a ruína:** uma sofisticação maior (features, stake, não-estacionariedade, execução) previu menos falências (p = 0,008). — [KellyBench](https://arxiv.org/abs/2604.27865)
- **Fundamentar a informação:** a pesquisa web reduziu as alucinações em 75–79%. — [MDPI](https://www.mdpi.com/2571-9394/8/5/78)
- **Diversidade limitada:** os agentes coincidiram em 92% das escolhas, e dar papéis diferentes ao mesmo modelo produziu previsões quase iguais. Um ensemble de LLMs parecidos acrescenta pouca informação. — [GitHub WC2026](https://github.com/graphuofm/FIFA2026LLM); [arXiv 2609.12495](https://arxiv.org/abs/2609.12495)
- **Combinar por média, não por "atualização":** a média simples entre o humano e a máquina foi melhor do que o LLM a atualizar depois de ver a mediana humana. — [Schoenegger et al.](https://www.science.org/doi/10.1126/sciadv.adp1528)
- **Viés contra o empate:** os LLMs quase nunca escolhem o empate (≤4 vezes em 104 jogos, com 24 empates). — [GitHub WC2026](https://github.com/graphuofm/FIFA2026LLM)
- **Autoavaliação pouco fiável:** a taxa de admissão do erro variou entre 36% e 86%. — [GitHub WC2026](https://github.com/graphuofm/FIFA2026LLM)

### Inferences
Regras práticas para o agente (derivadas da evidência acima, não testadas diretamente):
1. **A probabilidade vem só do preço.** É a da Pinnacle sem margem pelo método de Shin, ou a do consenso com um limiar maior. O LLM nunca produz uma probabilidade de raiz.
2. **O ajuste do LLM é assimétrico e limitado:** por defeito é 0, no máximo ±3 p.p., com um facto citado e datado. O código deve impor o teto. De preferência o LLM só **reduz** confiança ou **veta** apostas, porque a evidência mostra que as apostas contra o mercado perdem.
3. **O LLM serve para perguntas fechadas e verificáveis:** "Há retirada ou lesão confirmada depois da hora da odd da Pinnacle?", "A regra de liquidação da casa X difere (retirada no ténis, prolongamento)?", "A odd tem mais de 60 minutos?". Não serve para "quem ganha?".
4. **Desconfiar de valor grande.** Um EV muito acima do habitual contra a Pinnacle é mais vezes uma odd desatualizada ou um erro de mercado (e a casa pode anular por erro evidente) do que uma oportunidade.
5. **Não usar raciocínio longo para "confiança".** Os modelos com raciocínio longo tornam-se mais sobreconfiantes. Registar a confiança só como categoria (média ou alta) ligada a critérios objetivos.
6. **Medir pelo CLV e pela calibração (Brier contra a Pinnacle).** O ROI de dezenas de apostas é ruído, como mostra o WC2026, onde os ROI de ±10% em cerca de 100 apostas não eram distinguíveis de zero.
7. **Atenção ao empate:** se o LLM fizer qualquer ajuste em mercados 1X2, é plausível que penalize sistematicamente o empate.

### Gaps
- Não há estudos que testem diretamente um "LLM como filtro de armadilhas" com resultados em CLV. As regras acima são inferências de estudos adjacentes.

---

## B1. Promoções nas casas portuguesas (Betclic, Betano, Placard, Solverde): que tipos existem, que termos têm e como calcular o EV

### Takeaway
Os aumentos de odd (Betano **SuperOdds**, Betclic **Boost/Multi+**, Solverde **Power Odds**) e as freebets podem ter EV positivo, mas cada um tem de ser comparado com o preço justo da Pinnacle. Muitos aumentos só levam a odd para perto do justo. Como as bolsas de apostas são **ilegais em Portugal**, as freebets não podem ser "convertidas" com lay. O valor extrai-se usando a freebet como aposta simples a odds mais altas: com a margem portuguesa, a valor esperado de uma freebet ronda os 70–80% do valor facial a odds de 5–10.

### Cited Findings
**Tipos de promoções e termos (2026)**
- **Betano SuperOdds** (fontes do mercado brasileiro da Betano; os termos em Portugal podem ser diferentes): odds aumentadas no Resultado Final "SO", só pré-jogo, não combináveis com outras promoções nem em múltiplas. O aumento vai tipicamente de **0,05 a 0,20** sobre a odd original. — [Metrópoles](https://www.metropoles.com/apostas/superodds-betano); [Oddspedia BR](https://oddspedia.com/br/blog/guias/superodds-betano). A presença das SuperOdds diárias na Betano Portugal é referida em [Observador – Betano](https://observador.pt/prognosticos/betano-apostas/) e [O Jogo – melhores odds](https://www.ojogo.pt/apostas/artigo/melhores-odds-em-portugal/17861530).
- **Solverde Power Odds:** mostram a odd inicial e a odd aumentada. — [Observador – Solverde](https://observador.pt/prognosticos/solverde-apostas/). Na Liga Portugal há "Power Odds com **margem zero** no 1X2 para os grandes". — [O Jogo – comparador de odds](https://www.ojogo.pt/apostas/artigo/melhores-odds-em-portugal/17861530). A aposta mínima na Solverde é 0,10 €, e o máximo varia por mercado (segundo o resumo da pesquisa sobre páginas de análise da Solverde, como o [Observador](https://observador.pt/prognosticos/solverde-apostas/); confirmar).
- **Betclic:** tem odds Boost e Multi+ (bónus em múltiplas). — [Observador – Betano ou Betclic](https://observador.pt/prognosticos/betano-ou-betclic/). A oferta de boas-vindas é uma "aposta sem risco até 50 €", com reembolso em **freebets** se a primeira aposta perder, e **sem rollover** sobre os ganhos. — [O Jogo – bónus Betclic](https://www.ojogo.pt/apostas/artigo/bonus-betclic/17863355); [casasdeapostasonline.pt](https://casasdeapostasonline.pt/betclic/). Há desafios do tipo "aposta de 5 € a odd ≥ 2,00 certeira dá 20 € em freebets". — [resumo sobre Observador – freebets Betclic](https://observador.pt/prognosticos/freebets-betclic/) *(detalhe e validade por confirmar)*.
- **Placard:** a oferta observada é sobretudo de casino ou de boas-vindas com código (por exemplo 10 € + rodadas). — [resumo sobre Observador – códigos](https://observador.pt/seccao/prognosticos/codigos-promocionais/). Não encontrei aumentos de odd do Placard com termos verificáveis.

**Como calcular o EV**
- EV = odd × p_justa − 1, com p_justa tirada da Pinnacle sem margem. Um aumento vale a pena quando a probabilidade justa é maior do que a probabilidade de break-even da odd aumentada. — [Action Network](https://www.actionnetwork.com/education/how-to-calculate-which-odds-boosts-are-actually-worth-betting); [Pinnacle Odds Dropper – EV calculator](https://www.pinnacleoddsdropper.com/blog/expected-value-calculator)
- **Freebet sem devolução da stake (SNR):** o EV cresce com a odd porque a stake não é devolvida. Com hedge numa bolsa, as conversões típicas rondam os 65% a odd 3,0, os 78% a 6,0 e os 85% a 10,0; 70% é "bom" e mais de 80% é raro. — [Extra Place](https://extraplace.co.uk/blog/free-bet-conversion-methods/); [OddsMatched](https://www.oddsmatched.com/matched-betting-guide/free-bet-conversion-how-to-turn-free-bets-into-cash-complete-guide); [TACTIX](https://tactix.football/free-bets)
- **Bolsas de apostas proibidas em Portugal:** o exchange não é regulado pelo SRIJ, e a Betfair saiu em 2016 e não tem licença. — [apostalegal.pt – Betfair](https://apostalegal.pt/betfair-portugal/); [casasdeapostasonline.pt – Betfair](https://casasdeapostasonline.pt/betfair/)

### Inferences
Contas minhas, para ilustrar; verificar com o `odds.py` e o `banca.py` do agente:
- **Aumento de odd:** se o justo pela Pinnacle for 2,10 (47,6%), a Betano pagar 1,95 e a SuperOdd der +0,15, a odd fica em 2,10 e o EV em 0%. Para cumprir o limiar de 3% seria preciso uma odd ≥ 2,10 × 1,03 = **2,163**. Com a margem das casas portuguesas, um aumento de 0,05–0,20 muitas vezes só aproxima a odd do justo. **Cada aumento tem de passar pelo mesmo filtro de EV ≥ 3%** e pelos limites de odd de 1,40–4,00.
- **Power Odds com margem zero (1X2):** se as probabilidades implícitas somarem 100% e a Pinnacle sem margem também, então, a não ser que os preços sejam idênticos, **pelo menos um dos três resultados tem EV > 0** contra a Pinnacle. Vale a pena correr os três resultados de cada Power Odd pelo `odds.py`, embora o EV possa ficar abaixo de 3%.
- **Freebet usada sem hedge, a única opção legal em Portugal:** EV por euro de freebet = p_justa × (odd − 1) ≈ (odd − 1) / odd_justa. Com uma margem de cerca de 7%: a odd 2,0 (justa ≈ 2,14) vale cerca de **47%**; a odd 5,0 (justa ≈ 5,35) cerca de **75%**; a odd 10 (justa ≈ 10,7) cerca de **84%**. Isto é valor esperado, não conversão garantida: com uma banca de 20 €, a variância é grande, mas a freebet não sai da banca em dinheiro. Um hedge entre duas casas portuguesas sem bolsa perde duas margens e tende a render menos.
- **Desafio "5 € a ≥ 2,00 dá 20 € em freebets":** com p ≈ 0,47 (justa 2,14) e uma freebet usada a cerca de 5,0 (valor de 0,75), o EV é aproximadamente 5 × (2,0 × 0,47 − 1) + 0,47 × 20 × 0,75 ≈ −0,30 + 7,05 ≈ **+6,7 €**. Numa banca de 20 € é muito, se os termos se confirmarem. Mas uma stake de 5 € ultrapassa o teto de 10% da banca (2 €). O agente tem de tratar estas promoções à parte e respeitar a Regra 3: se a stake mínima exigida exceder o teto, não se entra.
- **Aposta "sem risco" com reembolso em freebet:** EV = p·S·(O − 1) − (1 − p)·S + (1 − p)·S·c, em que c é o valor da freebet. É provável que o utilizador já tenha usado as boas-vindas nas 4 casas. Se sim, o foco deve ser as promoções recorrentes: aumentos de odd, Power Odds, missões e cashback.
- **Regras do agente:** as promoções não podem servir de pretexto para quebrar os tetos de stake. As freebets devem ser registadas à parte em `apostas.csv`, porque a stake não sai da banca, para não distorcer o CLV e as métricas.

### Gaps
- Não consegui abrir as páginas de promoções nem os termos da Betclic, Betano, Placard e Solverde (proxy). Os limites de stake das SuperOdds e das Power Odds em Portugal, o rollover dos bónus da Betano e da Solverde e a existência de cashback ou "aposta sem risco" recorrente em 2026 **ficam por confirmar** nas próprias casas.
- As regras das SuperOdds vêm de fontes brasileiras e podem diferir em Portugal.
- Não encontrei as stakes mínimas da Betclic, da Betano e do Placard. Interessam porque, com a banca de 20 €, as stakes de 1/4 de Kelly ficam muitas vezes entre 0,10 € e 0,40 €.

---

## B2. Limitação de contas em Portugal: as casas limitam quem ganha, e como adiar isso de forma ética?

### Takeaway
Limitar contas é prática comum no setor e há queixas em Portugal. A Betclic tem até uma cláusula pública de limitação para quem aposta muito em odds abaixo de 1,40. Segundo o resumo da pesquisa, a orientação do SRIJ de 2017 diz que os limites de stake devem ser gerais e não uma forma de punir jogadores, mas isto precisa de confirmação no PDF. Com stakes de cêntimos, o risco é baixo mas não nulo. As táticas de "camuflagem" podem adiar a limitação, mas algumas levantam questões éticas ou de termos de utilização.

### Cited Findings
- **Cláusula da Betclic:** limita quem, num ano civil, apostar mais de 10 000 € com mais de metade em odds inferiores a 1,40, ou mais de 5 000 € em 3 meses nas mesmas condições. Nesse caso, no ano seguinte o jogador fica com um máximo de 500 € apostados e 25 € por aposta. — resumo da pesquisa sobre os [Termos e Condições da Betclic](https://www.betclic.pt/termsandconditions); há queixas com a mensagem "O limite legal periódico de aposta foi excedido" no [Portal da Queixa](https://portaldaqueixa.com/brands/betclic-betclick-limited/complaints/betclic-o-limite-legal-periodico-de-aposta-foi-excedido-36751920)
- **Betano:** um guia português diz que a Betano pode limitar contas com padrão "profissional", como apostar sempre em mercados de valor. — [apostalegal.com – Betano](https://apostalegal.com/betano/como-nao-ser-limitado). Há relatos de contas limitadas a 5–6 R$ por aposta depois de ganhos, mas são **do Brasil**, outra jurisdição. — [Reclame AQUI](https://www.reclameaqui.com.br/betano/limitacao-para-no-maximo-5-ou-6-reais-por-aposta_nzUSm5RVOsCtSs0B/). Existe pelo menos uma queixa portuguesa por "incumprimento da lei do SRIJ" contra a Betano.pt. — [Portal da Queixa](https://portaldaqueixa.com/brands/betano/complaints/betanopt-incumprimento-da-lei-do-srij-41212820)
- **Orientação n.º 1/2017/SRIJ/JO (limites de apostas):** segundo o resumo da pesquisa sobre o PDF, os operadores podem definir mínimos e máximos, divulgados no site, **aplicáveis a todos os jogadores sem exceção**, e a limitação "não pode ser usada como instrumento de prevenção ou punição de comportamentos irregulares". As irregularidades devem ser comunicadas às autoridades. — [SRIJ – Orientação 1/2017 (PDF)](https://www.srij.turismodeportugal.pt/sites/default/files/2022-08/Orientacao_n_1_2017_SRIJ_JO_limites_apostas.pdf) *(não aberto; confirmar a redação exata)*. O SRIJ recebe e analisa queixas contra operadores licenciados. — [SRIJ – Proteção legal ao jogador](https://www.srij.turismodeportugal.pt/pt/jogo-responsavel/protecao-legal-ao-jogador)
- **Evidência histórica:** as casas limitaram quem explorava preços desalinhados face ao consenso, com máximos como 1,25 $ na Sportingbet, 11,11 $ na Interwetten e 10,45 $ na Betway. — [Kaunitz et al. (ResearchGate)](https://www.researchgate.net/publication/320296375_Beating_the_bookies_with_their_own_numbers_-_and_how_the_online_sports_betting_market_is_rigged); [arXiv 1710.02824](https://arxiv.org/abs/1710.02824)
- **Táticas de praticantes para adiar a limitação (opinião):** stakes redondas; variar um pouco as stakes; apostas "de adepto" em eventos populares; apostar ao fim do dia e ao fim de semana; não entrar em todas as promoções; exigir mais edge antes de apostar; limitar o número de apostas por casa e por hora. — [Claw Arbs](https://clawarbs.com/blog/avoid-sportsbook-limits/); [Outplayed](https://outplayed.com/blog/top-tips-to-avoid-being-gubbed); [RebelBetting](https://www.rebelbetting.com/blog/how-to-avoid-bookmaker-limitations); [Pinnacle Odds Dropper](https://www.pinnacleoddsdropper.com/guides/8-tactics-to-avoid-accounts-limits)
- **Casas sharp como âncora:** a Pinnacle e as bolsas não limitam quem ganha. — [Claw Arbs](https://clawarbs.com/blog/avoid-sportsbook-limits/). Em Portugal, nem a Pinnacle nem as bolsas estão licenciadas (ver B1 e B4).

### Inferences
- **Para esta banca:** com stakes de 0,10–2 €, o impacto financeiro de uma limitação é pequeno para a casa. Ainda assim, os perfis de risco costumam olhar para o padrão (apostar logo em odds desatualizadas, só aumentos de odd, CLV sistematicamente positivo) e não só para o montante. É plausível ser limitado com stakes pequenas, mas não encontrei dados portugueses que o quantifiquem.
- **Aceitáveis e éticas** (não enganam ninguém nem violam termos): stakes redondas, que o `banca.py` pode arredondar para 0,10 € desde que abaixo do teto; distribuir as apostas pelas 4 casas; não apostar sempre segundos depois de uma odd aparecer; incluir mercados principais (1X2, vencedor do jogo) e não só mercados de nicho; não pegar em todos os aumentos de odd.
- **A evitar ou sinalizar:** apostas "de adepto" sem valor têm EV negativo, custam dinheiro e contrariam a Regra 8 do agente. Se se fizerem, têm de ser tratadas como custo e com stake mínima, e o agente não as deve recomendar. Contas múltiplas, contas de terceiros, VPN ou dados falsos **violam os termos e a lei** (RJO, identificação obrigatória) e nunca devem ser sugeridos.
- **Se houver limitação:** o CLAUDE.md já prevê distribuir as apostas pelas outras casas. Se a limitação parecer discriminatória, o utilizador pode reclamar ao SRIJ, com base na Orientação 1/2017, a confirmar. O resultado não é garantido.
- A regra da Betclic sobre odds < 1,40 não afeta o agente, porque a odd mínima é 1,40 e o volume é baixo.

### Gaps
- Não encontrei dados sistemáticos sobre com que frequência a Betclic, a Betano, a Solverde e o Placard limitam contas em Portugal, nem a partir de que volume ou CLV. As queixas públicas são anedóticas e muitas são do Brasil.
- O texto exato da Orientação 1/2017 e se continua em vigor em 2026 ficam por confirmar.
- O Placard, que não é licenciado pelo SRIJ (ver B4), pode ter regras próprias de limites. Não encontrei informação.

---

## B3. Comparar odds entre apenas 4 casas portuguesas

### Takeaway
As casas portuguesas pagam o IEJO sobre o **volume** das apostas desportivas (8% do turnover, segundo várias fontes). Por isso têm margens estruturalmente maiores e odds menos competitivas do que a Pinnacle. Com 4 casas, encontrar valor contra a Pinnacle será raro: aparecerá sobretudo em aumentos de odd e Power Odds, em odds desatualizadas e em mercados onde uma casa discorda do consenso.

### Cited Findings
- O IEJO é de 8% sobre o volume total das apostas desportivas à cota. Esta base tributária pressiona as margens e é "uma das razões pelas quais as cotações em Portugal são frequentemente menos competitivas" do que em mercados tributados pela receita bruta, como Malta ou o Reino Unido. — [apostaslegais-pt.com](https://apostaslegais-pt.com/articles/imposto-apostas-desportivas-portugal/); [Jornal de Leiria](https://www.jornaldeleiria.pt/noticia/portugal-e-a-evolucao-do-imposto-sobre-o-jogo-de-vilao-do-mercado-a-modelo-sustentavel)
- **Conflito entre fontes:** outros guias dizem que as apostas desportivas pagam "entre 8% e 16% da receita bruta". — [apostalegal.pt](https://apostalegal.pt/impostos-apostas-portugal/). Segundo o resumo da pesquisa, a progressividade até 16% terá sido eliminada pela Lei do OE 2020, ficando uma taxa fixa de 8% sobre o volume. — [apostaslegais-pt.com](https://apostaslegais-pt.com/articles/imposto-apostas-desportivas-portugal/). *A versão "8% sobre o volume" é a mais consistente com as outras fontes, mas deve ser confirmada no RJO (DL 66/2015, art. 90.º–91.º) em versão consolidada.*
- A Solverde oferece Power Odds com margem zero no 1X2 dos grandes da Liga Portugal. — [O Jogo](https://www.ojogo.pt/apostas/artigo/melhores-odds-em-portugal/17861530)
- O Placard é um produto de apostas desportivas à cota da Santa Casa, em regime de exclusividade, sob o Departamento de Jogos da SCML e não sob o SRIJ. — [Jogos Santa Casa – Regulamento do Placard](https://www.jogossantacasa.pt/web/SCInstitucional/verDetalhe?contentId=13525); [PokerNews PT](https://pt.pokernews.com/noticias/2015/09/placard-as-apostas-desportivas-da-dos-jogos-santa-casa-22018.htm)
- Nos jogos sociais, incluindo o Placard segundo a DECO e o Polígrafo, há um imposto do selo de 4,5% já incluído no preço da aposta (Lei 42/2016). — [DECO Proteste](https://www.deco.proteste.pt/familia-consumo/ferias-lazer/dicas/euromilhoes-placard-lotaria-saiba-quanto-paga-imposto-ganhar); [Polígrafo](https://poligrafo.sapo.pt/fact-check/se-ganhar-um-premio-superior-a-cinco-mil-euros-tera-que-pagar-20-em-imposto-do-selo/)

### Inferences
- Um imposto sobre o volume funciona como uma margem mínima embutida: a casa precisa de uma margem acima de cerca de 8% das apostas para ter lucro. É de esperar que as odds portuguesas fiquem quase sempre abaixo do preço justo da Pinnacle. O valor tende a aparecer em **promoções** e **desalinhamentos pontuais**, não na odd normal. Isto explica provavelmente porque é que o `odds.py alvos` dá poucos alvos cumpríveis.
- O **Placard** tem imposto do selo sobre a aposta e sobre os prémios acima de 5 000 € (ver B4). É estruturalmente a pior das 4 para odds normais. Deve ficar em último na comparação, exceto em promoções específicas. *(Inferência; não encontrei comparações de margens por casa.)*
- **Na prática, para o agente:** (1) correr todos os aumentos de odd e Power Odds do dia pelo filtro de EV contra a Pinnacle; (2) no plano, mostrar a odd mínima por casa; (3) registar em que casa se apostou, para ver onde aparece o valor e quem limita.

### Gaps
- Não encontrei medições publicadas de margens médias por casa (Betclic, Betano, Solverde, Placard) no ténis ou no futebol em 2026.
- A aplicação do imposto do selo de 4,5% ao Placard online vem de fontes de consumidores (DECO e Polígrafo) e não da lei. Fica por confirmar.

---

## B4. Impostos e regulação: os ganhos do apostador são tributados em Portugal? Houve mudanças em 2025–2026?

### Takeaway
Nas casas **licenciadas pelo SRIJ** (Betclic, Betano, Solverde), os prémios **não pagam IRS** nem são declarados: o imposto é o IEJO, pago pelo operador. No **Placard** (Santa Casa), os prémios acima de 5 000 € pagam 20% de imposto do selo sobre o excedente, retido na fonte. Em nov/2025 houve uma proposta para tributar em IRS os ganhos líquidos anuais acima de 500 €. A UTAO criticou-a por falta de dados, e não encontrei confirmação de que tenha sido aprovada.

### Cited Findings
- O apostador está isento nas casas com licença do SRIJ e não declara os ganhos no IRS. O imposto é o IEJO, suportado pelo operador. — [apostalegal.pt](https://apostalegal.pt/impostos-apostas-portugal/); [Portal da Queixa – impostos](https://portaldaqueixa.com/news/impostos-nas-apostas-online-portugal); [casasonlinept.com](https://casasonlinept.com/articles/impostos-ganhos-apostas/)
- A base legal é o RJO, aprovado pelo Decreto-Lei n.º 66/2015. — [apostalegal.pt](https://apostalegal.pt/impostos-apostas-portugal/)
- **Proposta de nov/2025:** tributar em IRS, às taxas progressivas e englobados, os ganhos líquidos anuais de jogo online acima de 500 €. A UTAO disse não ter dados de ganhos por jogador para quantificar o impacto e alertou para o risco de desvio para sites ilegais. Neste momento, os ganhos dos jogadores não são tributados nem declarados. — [ECO, 20/11/2025](https://eco.sapo.pt/2025/11/20/utao-trava-imposto-sobre-ganhos-nas-apostas-online/) *(via resumo da pesquisa)*
- Em 2024, o IEJO rendeu 335 M€. — [ECO](https://eco.sapo.pt/2025/11/20/utao-trava-imposto-sobre-ganhos-nas-apostas-online/). No 2.º trimestre de 2026, a receita bruta foi de 338,2 M€ (+12,8% em termos homólogos) e o IEJO de 101,4 M€, um recorde trimestral, segundo o relatório do SRIJ. — resumo da pesquisa, com referência à [ECO – reforma fiscal 2026](https://eco.sapo.pt/2026/02/13/reforma-fiscal-do-setor-do-jogo-em-portugal-em-2026-e-impacto-na-receita-publica/) e a [apostaslegais-pt.com](https://apostaslegais-pt.com/articles/imposto-apostas-desportivas-portugal/) *(atribuição exata por confirmar)*
- **Placard e jogos sociais:** os prémios até 5 000 € estão isentos; acima disso paga-se 20% de imposto do selo sobre o excedente, retido na fonte (por exemplo, num prémio de 5 100 €, 20 € de imposto). Há ainda 4,5% de imposto do selo incluído no preço da aposta. — [DECO Proteste](https://www.deco.proteste.pt/familia-consumo/ferias-lazer/dicas/euromilhoes-placard-lotaria-saiba-quanto-paga-imposto-ganhar); [Polígrafo](https://poligrafo.sapo.pt/fact-check/se-ganhar-um-premio-superior-a-cinco-mil-euros-tera-que-pagar-20-em-imposto-do-selo/); [Executive Digest](https://executivedigest.sapo.pt/joga-no-euromilhoes-placard-ou-lotaria-saiba-quanto-paga-de-imposto-se-ganhar/)
- **Bolsas e sites sem licença:** as bolsas de apostas não são reguladas pelo SRIJ e estão proibidas. A Betfair não tem licença. — [apostalegal.pt – Betfair](https://apostalegal.pt/betfair-portugal/)
- **SRIJ:** licencia (apostas desportivas à cota, fortuna ou azar, póquer), inspeciona, cobra o IEJO e protege o jogador, com limites de depósito e aposta, autoexclusão e tratamento de queixas. — [Portal da Queixa – o que é o SRIJ](https://portaldaqueixa.com/news/o-que-e-o-srij-e-que-funcoes-desempenha); [SRIJ – Autoexclusão](https://www.srij.turismodeportugal.pt/pt/sos-jogadores/autoexclusao-e-proibicao); [SRIJ – Estratégias de controlo](https://www.srij.turismodeportugal.pt/pt/jogo-responsavel/estrategias-de-controlo-do-jogo)

### Inferences
- Com uma banca de 20 €, os impostos são irrelevantes na prática. Nas 3 casas SRIJ não há imposto para o apostador, e o limiar de 5 000 € do Placard está muito longe. O agente pode dizer ao utilizador que os ganhos em casas licenciadas pelo SRIJ não são tributados em IRS. Deve acrescentar que houve uma proposta em 2025 para mudar isso e que convém confirmar se entrou em vigor.
- O agente só deve sugerir casas licenciadas pelo SRIJ ou o Placard. Isto exclui as bolsas e a Pinnacle, que só serve de **referência de preço**, não para apostar.

### Gaps
- Não consegui confirmar o destino da proposta de tributação em IRS acima de 500 € (aprovada, rejeitada ou retirada no OE 2026). Os guias de 2026 continuam a dizer que o apostador está isento, o que sugere que não foi aprovada, mas não é prova.
- Não consegui confirmar na lei consolidada a taxa e a base atuais do IEJO para apostas desportivas (8% do volume ou 8–16% da receita bruta).
- Não li diretamente o relatório trimestral do SRIJ do 2.º trimestre de 2026 (site bloqueado).
