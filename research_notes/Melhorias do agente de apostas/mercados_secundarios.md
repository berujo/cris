# Preço justo de mercados secundários de ténis (sets, handicap de jogos, total de jogos, "ganhar um set") a partir da odd do vencedor

Notas de investigação, 25/09/2026. Âmbito: melhor de 3 (ATP 250/500/1000, WTA, Challengers). Melhor de 5 aparece só em nota.
Condições: muitos PDFs académicos (arXiv, Harvard, Imperial College, janmagnus.nl, tennisabstract.com, atptour.com, vuir.vu.edu.au) estavam **bloqueados pelo proxy**. Para esses usei apenas os excertos devolvidos pela pesquisa, e assinalo-o em cada caso. Para compensar, fiz **um teste empírico próprio** com 8.596 encontros ATP à melhor de 3 com odds da Pinnacle (secção 3) e **uma implementação stdlib verificada** (secção 2). O código de trabalho está em `scratchpad/tenis_mercados.py` e `teste_empirico.py` desta sessão e vai transcrito abaixo.

Legenda: **[forte]** = revisto por pares ou calculado por mim com dados primários; **[médio]** = repositório público com relatórios reprodutíveis; **[fraco]** = blogue ou excerto de pesquisa não verificado.

---

## 1. Modelo mais simples (sets iid): usa-se na prática? Qual a precisão face aos resultados e aos mercados de set betting? (dependência entre sets, "momentum", favoritos a ganhar em 2-0)

### Takeaway
O modelo de sets iid, com s tirado de P(encontro) = s²(3−2s), é a base usada por calculadoras e modelos amadores. Ao fixar pA e pB, o modelo hierárquico de pontos iid dá **exatamente** a mesma distribuição de sets. No teste próprio (ATP, 8.596 encontros, Pinnacle/Shin), o modelo **subestima sistematicamente os 2-0 do favorito** (41,3% previsto contra 45,9% observado) e as vitórias do azarão por 0-2 (14,1% contra 17,2%), e **sobrestima os encontros de 3 sets** (44,6% contra 36,9%). Os sets estão positivamente correlacionados. Uma mistura normal na diferença de serviço (σ ≈ 0,06–0,07) corrige quase todo o desvio.

### Cited Findings
- **Fórmulas do modelo iid de sets** (álgebra elementar; verificadas numericamente por mim [forte]), com s = P(ganhar um set):
  - Melhor de 3: P(encontro) = s²(3−2s); P(2-0) = s²; P(2-1) = 2s²(1−s); P(1-2) = 2s(1−s)²; P(0-2) = (1−s)².
  - Melhor de 5: P(encontro) = s³(10−15s+6s²); P(3-0) = s³; P(3-1) = 3s³(1−s); P(3-2) = 6s³(1−s)².
  - A inversão p → s faz-se por bisseção, porque f(s) é crescente em [0,1]. Exemplo: p = 0,60 dá s = 0,5671, com P(2-0) = 0,322, P(2-1) = 0,278, P(1-2) = 0,213 e P(0-2) = 0,187.
- **Teste próprio [forte, com as ressalvas indicadas em Gaps]:** encontros ATP à melhor de 3 de 2013 e 2015–2018 (o ficheiro de 2014 falta no repositório), só "Completed", com odds Pinnacle (colunas PSW/PSL no formato tennis-data.co.uk). A fonte são os ficheiros em [edouardthom/ATPBetting/Data](https://github.com/edouardthom/ATPBetting), com origem em [tennis-data.co.uk](http://www.tennis-data.co.uk). Tirei a margem com o método de Shin (`scripts/odds.py`) e vi o resultado na perspetiva do favorito. n = 8.596.

  | P(fav) justa | n | Observado 2-0 / 2-1 / 1-2 / 0-2 | iid (sets = pontos iid) | Mistura σ=0,08 |
  |---|---|---|---|---|
  | 0,5–0,6 | 2392 | 0,333 / 0,221 / 0,189 / 0,257 | 0,287 / 0,266 / 0,231 / 0,217 | 0,342 / 0,210 / 0,187 / 0,260 |
  | 0,6–0,7 | 2433 | 0,405 / 0,228 / 0,165 / 0,203 | 0,362 / 0,288 / 0,191 / 0,159 | 0,429 / 0,221 / 0,158 / 0,192 |
  | 0,7–0,8 | 2012 | 0,496 / 0,259 / 0,112 / 0,133 | 0,452 / 0,295 / 0,145 / 0,108 | 0,530 / 0,218 / 0,123 / 0,130 |
  | 0,8–0,9 | 1276 | 0,629 / 0,229 / 0,073 / 0,069 | 0,567 / 0,278 / 0,092 / 0,062 | 0,652 / 0,194 / 0,081 / 0,074 |
  | 0,9–1,0 | 483 | 0,756 / 0,159 / 0,056 / 0,029 | 0,719 / 0,216 / 0,041 / 0,024 | 0,799 / 0,136 / 0,036 / 0,028 |
  | Total | 8596 | **0,459 / 0,230 / 0,139 / 0,172** | 0,413 / 0,278 / 0,168 / 0,141 | 0,483 / 0,208 / 0,140 / 0,170 |

  Varrimento de σ (log-loss sobre os 4 resultados; quanto menor, melhor):

  | σ | log-loss | Médias previstas 2-0 / 2-1 / 1-2 / 0-2 |
  |---|---|---|
  | iid | 1,2401 | 0,413 / 0,278 / 0,168 / 0,141 |
  | 0,05 | 1,2296 | 0,447 / 0,244 / 0,155 / 0,154 |
  | 0,06 | 1,2282 | **0,459 / 0,232 / 0,150 / 0,159** |
  | 0,07 | **1,2280** | 0,471 / 0,220 / 0,145 / 0,164 |
  | 0,08 | 1,2291 | 0,483 / 0,208 / 0,140 / 0,170 |

  O Brier de "favorito ganha 2-0" desce de 0,2343 com o iid para 0,2327 com σ = 0,08.
- **Dependência entre sets na literatura:**
  - Jackson & Mosurski (1997, CHANCE 10(2):27–34) compararam quatro modelos: independência, momentum psicológico (PM), independência com efeito aleatório diário e PM com efeito aleatório. O modelo "success-breeds-success" ajusta-se muito melhor do que a independência, sobretudo nas derrotas pesadas (2-0/3-0). Segundo o resumo citado, o efeito aleatório diário acrescenta pouco [médio; resumo secundário]. — [ResearchGate](https://www.researchgate.net/publication/261581953_Heavy_Defeats_in_Tennis_Psychological_Momentum_or_Random_Effect); [Taylor & Francis](https://www.tandfonline.com/doi/abs/10.1080/09332480.1997.10542019)
  - Depken, Gandar & Shapiro (2022, *Journal of Sports Economics* 23(5):598–623) estudaram 66.262 encontros profissionais à melhor de 3 (2002–2020). O modelo racional de referência acerta no 1.º set, mas nos sets seguintes há **momentum estratégico e psicológico** ao nível do set [forte; só li o resumo]. — [SAGE](https://journals.sagepub.com/doi/abs/10.1177/15270025221085715); [RePEc](https://ideas.repec.org/a/sae/jospec/v23y2022i5p598-623.html)
  - Sports Trading Network: quem ganha o 1.º set ganha o 2.º mais vezes do que as odds pré-jogo preveem, com uma "outperformance" média de 16% nos encontros ATP desde 2010. Ganhar o set anterior teria um efeito "enorme" nos homens e nas mulheres, maior em terra batida [fraco; excerto de pesquisa, página bloqueada, método não verificado]. — [Sports Trading Network](https://www.sportstradingnetwork.com/article/modelling-momentum-in-a-tennis-match/)
  - Jeff Sackmann (Heavy Topspin): o cálculo habitual de "straight sets" assume que as hipóteses não mudam de set para set. Se o 2.º set depender do 1.º, os encontros de 3 sets tornam-se menos prováveis [fraco; excerto]. — [Heavy Topspin, 2014](https://www.tennisabstract.com/blog/2014/08/13/a-quick-look-at-the-odds-of-three-setters/)
  - Klaassen & Magnus (2001, JASA 96(454):500–509) analisaram cerca de 90.000 pontos de Wimbledon entre 1992 e 1995. Os pontos **não** são iid: ganhar o ponto anterior ajuda, e nos pontos importantes o servidor ganha menos. Os desvios são **pequenos**, e o iid continua a ser uma boa aproximação em muitos casos. — [T&F](https://www.tandfonline.com/doi/abs/10.1198/016214501753168217); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=138096)
  - O repositório qitaoshi/tennis-model-v2 mediu o momentum com o Match Charting Project: 5.384 encontros e 876.428 pontos de 2010 a 2025, com correção de Miller–Sanjurjo e efeitos fixos por encontro. [médio]
    - Ao nível do ponto o efeito é de +0,53 pp (IC 95% entre 0,28 e 0,78 pp).
    - Ao nível do jogo, à melhor de 3, é de +0,10 pp e não se distingue de zero (p = 0,78).
    - No total de jogos, o momentum explica no máximo −0,05 jogos.
    - Conclusão do autor: a sobre-previsão de jogos vem sobretudo da **heterogeneidade dentro do encontro** (a diferença de nível varia), não do momentum sequencial ponto a ponto. — [reports/momentum_measurement.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/momentum_measurement.md)
- **Com pA e pB fixos, o modelo de pontos iid reproduz o modelo de sets iid:** a p = 0,55, 0,65, 0,75 e 0,85, a distribuição de sets do modelo de pontos calibrado coincide com a do modelo de sets iid até à 3.ª casa decimal. Isto é cálculo meu [forte]. A pequena dependência criada pela ordem de serviço é desprezável.

### Inferences
- Na prática, **não se deve usar o modelo iid puro** para preços de set betting. O erro sistemático (cerca de 4–6 pp no 2-0 do favorito e cerca de 5 pp no 2-1) é maior do que os limiares de EV do agente (3–5%). Com ele, os 2-1 pareceriam "com valor" e os 2-0 do favorito pareceriam caros. É uma armadilha clássica.
- A correção com melhor ajuste nos dados ATP é a **mistura normal na diferença de serviço**, com σ ≈ 0,065 (secção 2). Ela produz exatamente o padrão observado: mais 2-0 e mais 0-2, menos 2-1 e menos 1-2, sem mexer em P(encontro).
- Os dados não permitem separar "momentum psicológico" de "nível variável dentro do encontro". Para o preço isso é indiferente: ambos criam correlação positiva entre sets e são absorvidos pela mistura.
- Para mercados de "ganhar pelo menos um set" do azarão, P = 1 − P(fav 2-0). O iid **sobrestima** esta probabilidade: prevê 58,7% contra 54,1% observados na média total. Apostar "azarão ganha um set" com base no iid seria sistematicamente mau.

### Gaps
- Não encontrei nenhum estudo publicado que compare as **odds de set betting das casas** com um modelo derivado da odd do vencedor. Só comparei com resultados. O relatório do qitaoshi compara modelo e mercado, mas com o modelo alimentado por estatísticas e não pela odd (secção 3).
- O teste próprio cobre só a ATP de 2013 e 2015–2018. Não testei WTA nem Challengers, por falta de dados de odds acessíveis. A ser verdade o excerto da Sports Trading Network sobre o efeito nas mulheres, o σ para a WTA pode ser maior. Não verificado.
- O σ foi escolhido nos mesmos dados (5 valores testados). O risco de sobreajuste é baixo, mas o teste não é fora da amostra.
- Não verifiquei em que momento a tennis-data regista as odds PSW/PSL (se são de fecho ou não).

---

## 2. Modelos hierárquicos de pontos (Barnett & Clarke, Klaassen & Magnus, O'Malley, Newton & Keller): fórmulas e calibração de pA e pB a partir da odd do encontro

### Takeaway
O padrão consolidado é: pontos iid, jogo, tie-break, set, encontro, com pA e pB = probabilidade de cada jogador ganhar um ponto no seu serviço. Para calibrar ao mercado, **fixa-se o nível L = pA + pB** (média de pontos ganhos no serviço do circuito e da superfície, ×2) e **resolve-se por bisseção a diferença d = pA − pB** que reproduz a probabilidade justa do vencedor. A implementação open-source (tennis-engine) faz o mesmo e diz explicitamente que o nível determina o total de jogos e a diferença determina quem ganha. A distribuição de sets quase não depende de L. O total de jogos e o handicap dependem bastante de L.

### Cited Findings
- **Referências base:**
  - O'Malley (2008, JQAS 4(2)) deduz P(ganhar jogo) com pontos iid e testa-a com Wimbledon 2007. Deduz também P(tie-break), P(set), P(encontro) e P(recuperar de um break). — [De Gruyter](https://www.degruyterbrill.com/document/doi/10.2202/1559-0410.1100/html); [RePEc](https://ideas.repec.org/a/bpj/jqsprt/v4y2008i2n15.html)
  - Newton & Keller (2005), *Probability of winning at tennis I. Theory and data* (Studies in Applied Mathematics). — [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.0022-2526.2005.01547.x)
- **Barnett & Clarke (2005, IMA J. Management Math. 16(2):113–120):** combinam as estatísticas ATP de serviço e de resposta para estimar a probabilidade de cada jogador ganhar um ponto no serviço contra aquele adversário. Depois usam uma folha de cálculo para prever a duração do encontro e a probabilidade de vitória. — [OUP](https://academic.oup.com/imaman/article-abstract/16/2/113/704903); [ResearchGate](https://www.researchgate.net/publication/228614352_Combining_player_statistics_to_predict_outcomes_of_tennis_matches)
  - A forma usual é f_AB = f_t + (f_A − f_av) − (g_B − g_av). Aqui f_t é a percentagem média de pontos ganhos no serviço no torneio; f_A é a de A; g_B é a percentagem de pontos ganhos na resposta por B; e _av indica médias do circuito. A escrita exata da fórmula vem da minha memória da literatura; o excerto confirma apenas o princípio ("ajustar a estatística do torneio pelo desempenho do servidor e do recebedor face ao jogador médio"). — [Gollub 2021, JSA](https://journals.sagepub.com/doi/10.3233/JSA-200345)
  - Gollub (2021) mostra métodos que superam o de Barnett & Clarke na previsão do serviço em 7.622 encontros ATP de 2014 a 2016. — [mesma fonte](https://journals.sagepub.com/doi/10.3233/JSA-200345)
- **Inferir pA e pB das odds:**
  - Huang, Knottenbelt e Bradley (Imperial College, 2011) usam um modelo de Markov hierárquico para espelhar as probabilidades do mercado. Dizem que as previsões pré-jogo tiradas das odds implícitas podem gerar as probabilidades de serviço correspondentes, com parâmetros históricos de serviço [fraco; excerto, PDF bloqueado]. — [PDF](https://www.doc.ic.ac.uk/teaching/distinguished-projects/2011/x.huang.pdf)
  - `engine/markov.py::invert_to_target` do repositório tennis-engine (MIT): "solve for the scalar δ in pa' = pa + δ/2, pb' = pb − δ/2 such that match_distribution(pa', pb') gives exactly the target. The serve level (pa + pb, which drives total games) is preserved; only the serve gap (which drives who wins) moves. Bisection on δ — the match probability is monotone in δ." — [urwishpatel2003/tennis-engine](https://github.com/urwishpatel2003/tennis-engine) [médio]
  - `model/combine.py` do qitaoshi/tennis-model-v2 segue a mesma lógica: "Rates give the level (serve dominance), Elo gives the split". A inversão faz-se sobre uma grelha (nível, diferença) com NÍVEL entre 1,00 e 1,50. — [repo](https://github.com/qitaoshi/tennis-model-v2) [médio]
- **Fórmulas exatas** (padrão O'Malley / Newton & Keller). Implementei-as e verifiquei-as [forte]: p_hold(0,64) = 0,8126, igual ao valor exato publicado no relatório do qitaoshi. Com pA = pB = 0,64, a média de jogos é **25,683** à melhor de 3 e **42,377** à melhor de 5 com TB de 10 pontos no set final, iguais a 25,683 e 42,377 no mesmo relatório ([momentum_measurement.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/momentum_measurement.md)).
  1. **Jogo de serviço:** com q = 1−p, P_hold(p) = p⁴(1 + 4q + 10q²) + 20·p³q³ · p²/(1 − 2pq). O último termo é chegar a 40-40 e depois ganhar a partir do deuce.
  2. **Tie-break a T pontos** (T = 7, ou 10 no super tie-break):
     - A serve o 1.º ponto e a sequência é A, B, B, A, A, B, B… O ponto k (a contar de 0) é servido por A se ⌊(k+1)/2⌋ for par.
     - Programação dinâmica sobre (a, b). Ganha quem chegar a T com 2 de vantagem.
     - Nos empates a partir de (T−1, T−1), cada par de pontos tem um serviço de cada, e fecha-se a conta com P_emp = pA(1−pB) / [pA(1−pB) + (1−pA)pB].
  3. **Set com tie-break a 6-6:**
     - Programação dinâmica sobre (i, j) jogos, com o serviço a alternar.
     - Termina em 6-x (x ≤ 4), 7-5, 5-7 ou 7-6/6-7 pelo tie-break.
     - O tie-break começa com quem serviu o 1.º jogo do set, porque o jogo 13 é ímpar.
  4. **Quem serve primeiro no set seguinte:** o outro jogador se o set teve um número ímpar de jogos (6-3, 7-6 = 13); o mesmo se teve número par (6-4, 7-5). Isto decorre da alternância e da regra "quem serviu primeiro no tie-break recebe no 1.º jogo do set seguinte".
  5. **Encontro:** soma sobre os sets, guardando (sets A, sets B, quem serve a seguir, jogos A, jogos B). O servidor inicial é 50/50 porque o sorteio ainda não é conhecido antes do jogo.
     - A distribuição conjunta (sets, jogos A, jogos B) dá todos os mercados: set betting, total (Σ jogos), handicap (jogos A − jogos B), "ganhar um set" e P(há tie-break).
  6. **Efeito de quem serve primeiro:** vale no máximo 0,4 jogos no total esperado. Com pA − pB = 0,10, isso corresponde a cerca de 9 pp em P(>19,5 jogos); se o mais forte servir primeiro, o total esperado desce. Pré-jogo, faz-se a média dos dois casos. — [Mohammadi, arXiv 2605.04867 (2026)](https://arxiv.org/abs/2605.04867) [médio; resumo]
- **Nível L:** calculei a média de pontos ganhos no serviço (SPW) com os dados TML-Database ([stats.tennismylife.org](https://stats.tennismylife.org), cópia em [qitaoshi/tennis-model-v2/vendor](https://github.com/qitaoshi/tennis-model-v2)) [forte].

  | Circuito e período | Todas | Duro | Terra | Relva |
  |---|---|---|---|---|
  | ATP principal, 2013–2018 | 0,637 | 0,636 | 0,625 | 0,663 |
  | ATP principal, 2023–ago 2026 | 0,639 | 0,643 | 0,624 | 0,657 |
  | Challenger, 2023–ago 2026 | **0,611** | 0,624 | 0,598 | — |

  Logo, L ≈ 1,28 para a ATP em duro, ≈ 1,25 em terra, ≈ 1,31–1,33 em relva, e ≈ 1,22 nos Challengers (≈ 1,25 em duro, ≈ 1,20 em terra).
- **WTA:** "a percentagem de pontos ganhos no serviço num encontro WTA ronda os 57%, variando com a superfície", o que dá L ≈ 1,14 [fraco; excerto de pesquisa que não consegui atribuir a uma página, entre [tennisprofits.com](https://tennisprofits.com/diving-into-wta-game-score-stats/) e [Bleacher Report](https://bleacherreport.com/articles/1733332-the-five-most-important-statistics-in-womens-tennis)].
- **Sensibilidade ao nível, com p = 0,70** (cálculo meu):
  - L de 1,10 a 1,32 muda d = pA − pB apenas de 0,040 para 0,042, e **P(2-0) não muda** (0,405 no iid).
  - A média de jogos passa de 23,78 para 25,58, P(over 22,5) de 0,518 para 0,598, e P(fav −3,5) de 0,501 para 0,409.
  - Conclusão: o nível quase não conta no set betting, mas conta muito nos totais e no handicap.

### Inferences
- **Algoritmo recomendado para o agente** (tudo em stdlib):
  1. Tirar a probabilidade justa p do vencedor pela Pinnacle com Shin (`odds.py`), ou pelo consenso das casas.
  2. Escolher L pelo circuito e pela superfície (tabela acima). Quando houver linha de total de jogos da Pinnacle, é melhor **resolver L também a partir do mercado** (ver Inferences da secção 3).
  3. Resolver d por bisseção para que P_encontro(L/2 + d/2, L/2 − d/2) = p.
  4. Aplicar a **mistura**: d_encontro ~ N(d₀, σ²), com σ ≈ 0,065 no ATP. Usar 5 nós de Gauss–Hermite e **recentrar** d₀ para que a mistura continue a dar P(encontro) = p.
  5. Ler os mercados na distribuição conjunta. Para uma odd com devolução (linha inteira), a odd justa é (P(ganha) + P(perde)) / P(ganha).
- **Resposta-tipo a "e o Faria ganhar 2-0?".** Exemplo com a p justa do Faria = 0,60 num Challenger em duro:
  - O modelo corrigido dá P(2-0) ≈ 0,369, ou seja, odd justa ≈ 2,71.
  - O iid daria 0,322 (odd 3,11). A diferença de 4,7 pp mostra porque é que o iid não serve.
  - Só há valor se a casa pagar ≥ 2,71 × 1,03, ou mais (ver o limiar reforçado na secção 3).
- A tabela de referência abaixo (modelo corrigido, σ = 0,065, calculada por mim) permite respostas rápidas sem correr código. A linha "WTA" é **extrapolada**, porque o σ foi ajustado na ATP.

  **ATP (L = 1,28)**

  | p fav | 2-0 | 2-1 | 1-2 | 0-2 | azarão ganha ≥1 set | média jogos | o21,5 | o22,5 | fav −3,5 | fav −4,5 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 0,50 | 0,286 | 0,214 | 0,214 | 0,286 | 0,714 | 24,53 | 0,614 | 0,533 | 0,303 | 0,205 |
  | 0,55 | 0,325 | 0,225 | 0,200 | 0,250 | 0,675 | 24,50 | 0,611 | 0,530 | 0,345 | 0,239 |
  | 0,60 | 0,367 | 0,233 | 0,185 | 0,215 | 0,633 | 24,38 | 0,602 | 0,522 | 0,390 | 0,275 |
  | 0,65 | 0,411 | 0,239 | 0,168 | 0,182 | 0,589 | 24,19 | 0,588 | 0,508 | 0,439 | 0,315 |
  | 0,70 | 0,459 | 0,241 | 0,149 | 0,151 | 0,541 | 23,91 | 0,567 | 0,488 | 0,490 | 0,360 |
  | 0,75 | 0,512 | 0,238 | 0,128 | 0,122 | 0,488 | 23,53 | 0,538 | 0,460 | 0,546 | 0,411 |
  | 0,80 | 0,570 | 0,230 | 0,106 | 0,094 | 0,430 | 23,02 | 0,499 | 0,424 | 0,608 | 0,468 |
  | 0,85 | 0,635 | 0,215 | 0,082 | 0,068 | 0,365 | 22,35 | 0,449 | 0,377 | 0,675 | 0,536 |
  | 0,90 | 0,711 | 0,189 | 0,057 | 0,043 | 0,289 | 21,43 | 0,380 | 0,314 | 0,752 | 0,618 |

  **Challenger (L = 1,22):** os sets são praticamente iguais aos da ATP.

  | p fav | 2-0 | média jogos | o22,5 | fav −3,5 |
  |---|---|---|---|---|
  | 0,60 | 0,369 | 23,75 | 0,493 | 0,416 |
  | 0,70 | 0,462 | 23,28 | 0,459 | 0,519 |
  | 0,80 | 0,572 | 22,40 | 0,397 | 0,636 |

  **WTA (L = 1,14, extrapolado)**

  | p fav | 2-0 | média jogos | o22,5 | fav −3,5 |
  |---|---|---|---|---|
  | 0,60 | 0,371 | 23,15 | 0,467 | 0,438 |
  | 0,70 | 0,464 | 22,68 | 0,435 | 0,542 |
  | 0,80 | 0,575 | 21,81 | 0,375 | 0,660 |

#### Implementação de referência (Python stdlib, verificada contra os valores exatos acima)
```python
import math
from functools import lru_cache

GH5 = [(0.0, 8/15), (1.3556261799742657, 0.2220759220056126), (-1.3556261799742657, 0.2220759220056126),
       (2.8569700138728056, 0.011257411327720691), (-2.8569700138728056, 0.011257411327720691)]  # Gauss-Hermite (probabilistas), pesos normalizados

def p_hold(p):
    q = 1 - p
    return p**4 * (1 + 4*q + 10*q*q) + 20 * p**3 * q**3 * p*p / (1 - 2*p*q)

def p_tiebreak(pa, pb, alvo=7):          # A serve o 1.o ponto
    empate = pa*(1-pb) / (pa*(1-pb) + (1-pa)*pb)
    @lru_cache(maxsize=None)
    def f(a, b):
        if a >= alvo and a - b >= 2: return 1.0
        if b >= alvo and b - a >= 2: return 0.0
        if a == b and a >= alvo - 1: return empate
        w = pa if ((a + b + 1)//2) % 2 == 0 else 1 - pb
        return w*f(a+1, b) + (1-w)*f(a, b+1)
    return f(0, 0)

def dist_set(pa, pb, a_primeiro, tb_alvo=7):   # {(jogosA, jogosB): prob}, TB a 6-6
    ha, hb = p_hold(pa), p_hold(pb)
    est, fim = {(0, 0): 1.0}, {}
    for _ in range(12):
        novos = {}
        for (i, j), pr in est.items():
            w = ha if (((i+j) % 2 == 0) == a_primeiro) else 1 - hb
            for (ni, nj), pp in (((i+1, j), w), ((i, j+1), 1-w)):
                alvo = fim if (ni >= 6 and ni-nj >= 2) or (nj >= 6 and nj-ni >= 2) else novos
                alvo[(ni, nj)] = alvo.get((ni, nj), 0) + pr*pp
        est = novos
    x = est.get((6, 6), 0.0)
    if x:
        t = p_tiebreak(pa, pb, tb_alvo) if a_primeiro else 1 - p_tiebreak(pb, pa, tb_alvo)
        fim[(7, 6)] = x*t; fim[(6, 7)] = x*(1-t)
    return fim

def dist_encontro(pa, pb, melhor_de=3, tb_final=7):   # {(setsA, setsB, jogosA, jogosB): prob}
    alvo, cache, fim = melhor_de//2 + 1, {}, {}
    est = {(0, 0, True, 0, 0): 0.5, (0, 0, False, 0, 0): 0.5}   # sorteio do servico
    while est:
        novos = {}
        for (sa, sb, a1, ga, gb), pr in est.items():
            final = sa == sb == alvo - 1
            k = (a1, final)
            if k not in cache: cache[k] = dist_set(pa, pb, a1, tb_final if final else 7)
            for (i, j), pp in cache[k].items():
                nsa, nsb = sa + (i > j), sb + (j > i)
                if nsa == alvo or nsb == alvo:
                    kk = (nsa, nsb, ga+i, gb+j); fim[kk] = fim.get(kk, 0) + pr*pp
                else:
                    kk = (nsa, nsb, a1 if (i+j) % 2 == 0 else not a1, ga+i, gb+j)
                    novos[kk] = novos.get(kk, 0) + pr*pp
        est = novos
    return fim

def resolver(f, alvo, lo, hi, it=40):     # bissecao, f crescente
    for _ in range(it):
        m = (lo+hi)/2
        lo, hi = (m, hi) if f(m) < alvo else (lo, m)
    return (lo+hi)/2

def p_ganha(d): return sum(v for (sa, sb, _, _), v in d.items() if sa > sb)

def dist_mercado(p_justa, nivel=1.28, sigma=0.065, melhor_de=3, tb_final=7):
    """Mistura normal no split d=pA-pB, recentrada para P(encontro)=p_justa. sigma=0 -> iid puro."""
    nos = GH5 if sigma > 0 else [(0.0, 1.0)]
    def mist(d0):
        tot = {}
        for z, w in nos:
            d = d0 + sigma*z
            a = min(max(nivel/2 + d/2, 0.05), 0.95); b = min(max(nivel/2 - d/2, 0.05), 0.95)
            for k, v in dist_encontro(a, b, melhor_de, tb_final).items(): tot[k] = tot.get(k, 0) + w*v
        return tot
    return mist(resolver(lambda d: p_ganha(mist(d)), p_justa, -0.6, 0.6, 30))

def mercados(d):
    sets, tot, hcp = {}, {}, {}
    for (sa, sb, ga, gb), v in d.items():
        sets[f"{sa}-{sb}"] = sets.get(f"{sa}-{sb}", 0) + v
        tot[ga+gb] = tot.get(ga+gb, 0) + v
        hcp[ga-gb] = hcp.get(ga-gb, 0) + v
    return {"sets": sets,
            "media_jogos": sum(k*v for k, v in tot.items()),
            "over": lambda l: sum(v for k, v in tot.items() if k > l),
            "push_total": lambda l: tot.get(l, 0.0),
            "cobre": lambda l: sum(v for k, v in hcp.items() if k + l > 0),   # A com handicap l (ex.: -3.5)
            "a_ganha_set": sum(v for (sa, sb, _, _), v in d.items() if sa >= 1),
            "b_ganha_set": sum(v for (sa, sb, _, _), v in d.items() if sb >= 1)}
    # P(ha tie-break) exige guardar no estado se algum set acabou 7-6/6-7 (extensao trivial de dist_encontro)

def odd_justa(p_ganha, p_push=0.0):      # linha inteira com devolucao
    return (1 - p_push) / p_ganha
```
Desempenho: `dist_encontro` corre em cerca de 1 ms. `dist_mercado` com mistura faz cerca de 150 avaliações, o que dá cerca de 0,1–0,2 s por encontro. Para varrer muitos encontros, basta guardar em cache por (p arredondada a 0,01, L).

### Gaps
- Não consegui ler o texto de Klaassen & Magnus (2003), *Forecasting the winner of a tennis match* (EJOR), porque o PDF em [janmagnus.nl](https://www.janmagnus.nl/papers/JRM065.pdf) está bloqueado. É a referência clássica da parametrização por (pA+pB, pA−pB), mas **não verifiquei** o que diz. O facto de P(encontro) depender quase só de pA − pB confirmei-o por cálculo próprio.
- Também não li os pacotes R de Kovalchik. O [skoval/deuce](https://github.com/skoval/deuce) está descrito como "Resources for Analysis of Professional Tennis Data" (dados, mais funções como `elo_prediction`) e não encontrei nele um inversor odds → serviço.
- A média de SPW da WTA não está verificada numa fonte primária. Para a calcular, seria preciso um conjunto de dados WTA com estatísticas de serviço.
- Barnett & Clarke: a forma exata da fórmula f_AB vem de memória e não de leitura do artigo.

---

## 3. Precisão para total de jogos e handicap face aos resultados e às linhas das casas; enviesamentos conhecidos (superfície, WTA vs ATP, desistências, tie-break de 10 pontos)

### Takeaway
O modelo iid calibrado à odd do vencedor **sobrestima o total de jogos em cerca de 1,3 jogos** (ATP, teste próprio): P(over 22,5) prevista a 0,550 contra 0,465 observada. Também **subestima as vitórias folgadas do favorito** (P(fav −5,5) a 0,191 contra 0,258). Com a mistura σ ≈ 0,06–0,07, o viés médio fica abaixo de 0,1–0,3 jogos. Mesmo assim, num repositório público o **preço sem margem do próprio mercado é melhor previsor** do que um modelo de estatísticas em todos os mercados secundários. Apostar pelo modelo contra a Bet365 deu ROI negativo em todos eles. Estes modelos servem para dar preços **onde não há mercado de referência** e para detetar armadilhas, não para bater a Pinnacle nas linhas secundárias.

### Cited Findings
- **Teste próprio** (ATP melhor de 3, n = 8.596, p da Pinnacle/Shin, L por superfície com a SPW de 2013–2018) [forte]:

  | Modelo | Média de jogos | P(over 22,5) | P(over 20,5) | P(fav −3,5) | P(fav −5,5) | log-loss over 22,5 | log-loss fav −3,5 |
  |---|---|---|---|---|---|---|---|
  | **Observado** | **23,41** | **0,465** | **0,592** | **0,497** | **0,258** | — | — |
  | iid | 24,73 | 0,550 | 0,682 | 0,448 | 0,191 | 0,6973 | 0,6628 |
  | σ = 0,05 | 23,95 | 0,494 | — | 0,482 | — | 0,6842 | 0,6582 |
  | σ = 0,06 | 23,67 | 0,474 | — | 0,493 | — | **0,6827** | **0,6578** |
  | σ = 0,07 | 23,37 | 0,453 | — | 0,504 | — | 0,6828 | 0,6580 |
  | σ = 0,08 | 23,06 | 0,433 | 0,558 | 0,515 | 0,287 | 0,6848 | 0,6586 |

  - Por faixa de favorito, o iid sobrestima a média de jogos em +1,1 a +1,5 jogos em todas as faixas. Exemplos: faixa 0,5–0,6, 25,54 previsto contra 24,04 observado; faixa 0,9–1,0, 21,67 contra 20,51.
  - Por superfície (observado / iid / σ = 0,08):

    | Superfície | Observado | iid | σ = 0,08 |
    |---|---|---|---|
    | Duro | 23,46 | 24,74 | 23,07 |
    | Terra | 23,11 | 24,54 | 22,86 |
    | Relva | 24,27 | 25,44 | 23,83 |

    O viés é do mesmo sinal nas três superfícies.
- **qitaoshi/tennis-model-v2** (ATP + Challenger desde 2010; pA e pB vêm de estatísticas e Elo, não da odd) [médio]:
  - Com pontos iid, **o total de jogos é sobrestimado em +2,218** (26,206 previsto contra 23,988 real) no período TUNE (2024-01 a 2025-06). Depois das correções da fase 7, o viés fica em +0,428. O desvio da SPW explica apenas cerca de 6% do que resta. Veredito do autor: "THE ENGINE / IID ASSUMPTION". — [totals_bias_diagnosis.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/totals_bias_diagnosis.md)
  - Viés por segmento (total de jogos): Challenger +0,66; ATP 250 −0,03; ATP 500 −0,77; Masters +0,34; Grand Slam −0,21; terra +0,53; relva −1,41; duro +0,58. — [mesmo relatório](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/totals_bias_diagnosis.md)
  - **Tie-breaks:** houve pelo menos um tie-break em 34,45% dos encontros, contra 42,62% previstos pelo iid (−8,2 pp). A correção (mistura na diferença, σ = 0,08, mais −0,02 na probabilidade de manter o serviço em 5-5/6-6) deixa o erro em −0,06 pp.
  - A cobertura do intervalo central de 80% do total de jogos passa de 0,7325 para 0,807.
  - O comentário no código afirma o contrário ("real sets reach 6-6 more often"), mas os dados do próprio relatório mostram que o iid **sobre**-prevê os tie-breaks. — [stage_7.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/stage_validations/stage_7.md); [corrections.py](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/model/corrections.py)
  - **Mercado vs modelo como previsores** (ATP principal, TUNE, cerca de 1.100 encontros; Brier do mercado sem margem contra Brier do modelo):

    | Mercado | Brier do mercado | Brier do modelo | Correlação |
    |---|---|---|---|
    | Vencedor | 0,1835 | 0,2152 | 0,79 |
    | Total de jogos | 0,2170 | 0,2216 | 0,89 |
    | Handicap de jogos | 0,1987 | 0,2173 | 0,84 |
    | Set betting | 0,1423 | 0,1499 | 0,83 |
    | Total de sets | 0,2112 | 0,2151 | 0,92 |

    Nos 545 encontros em que modelo e mercado divergem mais de 10 pontos, o Brier é 0,165 para o mercado e 0,226 para o modelo. — [model_vs_market.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/model_vs_market.md)
  - **Apostar onde o modelo dizia haver valor, à odd bruta da Bet365:**

    | Mercado | ROI | IC 95% | Apostas |
    |---|---|---|---|
    | Vencedor | −5,15% | −11,7% a +1,7% | 584 |
    | Total de jogos | −2,69% | −7,4% a +1,9% | 1.508 |
    | Handicap de jogos | −10,60% | −18,2% a −3,0% | 555 |
    | Set betting | −16,84% | −28,8% a −3,2% | 2.314 |

    Veredito: "no demonstrated edge" em todos. O HOLDOUT de 2026 dá "All five markets unprofitable against real odds". — [multi_market_clv.md](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/reports/multi_market_clv.md); [README](https://github.com/qitaoshi/tennis-model-v2)
- Kovalchik (2016, JQAS 12(3):127–138) testou 11 modelos em 2.395 encontros ATP de 2014, com as casas como referência. Os modelos de pontos tiveram exatidão comparável à dos de regressão e melhor discriminação, ao nível do Elo e das casas. Os mais exatos foram a regressão por ranking e o Elo da FiveThirtyEight. — [De Gruyter](https://www.degruyterbrill.com/document/doi/10.1515/jqas-2015-0059/html); [RePEc](https://ideas.repec.org/a/bpj/jqsprt/v12y2016i3p127-138n1.html)
- Mohammadi (2026) apresenta uma comparação empírica que ilustra "the adequacy of the constant-probability assumption for modelling the total number of games" [médio; só o resumo]. — [arXiv 2605.04867](https://arxiv.org/abs/2605.04867). **Esta conclusão contraria** o teste próprio e o qitaoshi, que mostram um viés de +1,3 a +2,2 jogos quando p é fixado antes do jogo. Hipótese minha, não verificada: o artigo estimará p com as estatísticas do próprio encontro (dentro da amostra), o que esconde a variação de nível entre encontros.
- **Tie-break de 10 pontos no set final:** só existe nos Grand Slams (secção 5). Com melhor de 3 não se aplica. À melhor de 5, a média de jogos com TB de 10 pontos é 42,377 com pA = pB = 0,64 (exato).

### Inferences
- **Regras para o agente (inferência e opinião):**
  1. Se a Pinnacle tiver o mercado secundário (set betting, total, handicap), o preço justo é **esse mercado sem margem** (Shin sobre os N resultados). O modelo serve só para verificar a coerência.
  2. Sem mercado secundário da Pinnacle, usar o modelo corrigido (σ ≈ 0,065), mas **exigir mais EV**. O erro residual do modelo (±1–3 pp nas probabilidades, cerca de 0,3 jogos no total) tem a mesma ordem de grandeza que o limiar de 3%. Sugestão: pelo menos 8% de EV no set betting (e ≥ 10% nos resultados 2-1 e 1-2, os mais sensíveis a σ), e pelo menos 6% no total e no handicap. O mesmo princípio da regra "sem Pinnacle, exigir mais valor".
  3. **Nunca usar o iid puro.** Faria o agente ver valor falso nos overs, nos 2-1 e 1-2, e no "azarão ganha um set", e ver preços caros nos 2-0 do favorito e nos handicaps grandes do favorito.
  4. Para totais e handicaps, o nível L deve vir de preferência do mercado. Se houver linha de total da Pinnacle (por exemplo over/under 22,5 a 1,90/1,95), **resolver em conjunto (L, d)** para reproduzir P(vencedor) e P(over linha). São 2 equações e 2 incógnitas, resolvidas por bisseção alternada, com σ fixo. Assim entram os perfis específicos (dois grandes servidores, terra lenta), que a média do circuito ignora. Não encontrei este método publicado; é uma proposta minha.
  5. Os Challengers têm L mais baixo (0,611 de SPW contra 0,639 na ATP), logo menos jogos para a mesma p. O qitaoshi encontrou viés residual positivo nos Challengers (+0,66) e negativo na relva e nos ATP 500. O ajuste por superfície e circuito é obrigatório, e a relva é a mais incerta.
- **O que é mais robusto:** o set betting depende quase só de p e σ, não de L. É o mercado secundário em que um preço derivado da odd do vencedor é mais fiável. Totais e handicaps precisam de L, e é aí que o modelo é mais frágil.

### Gaps
- Não testei o modelo contra **linhas reais** de total, handicap ou set betting da Pinnacle, por falta de dados de odds secundárias acessíveis. As comparações com mercados vêm só do qitaoshi, com um modelo baseado em estatísticas.
- **Desistências:** excluí-as, e o qitaoshi também. A liquidação de set betting, totais e handicap quando há desistência varia de casa para casa (outra nota desta pasta: `regras_desistencia.md`). É um risco de liquidação a filtrar, não a modelar.
- Não há evidência sobre a WTA para totais e handicaps. O σ e o L da WTA estão por validar.
- Não encontrei estudos académicos publicados sobre a precisão de totais e handicaps de ténis face às linhas das casas.

---

## 4. Implementações open-source que se podem portar

### Takeaway
Há vários motores de Markov em Python que calculam set score, totais e handicap. O mais completo e documentado é o **qitaoshi/tennis-model-v2**: fórmulas fechadas de Barnett–Clarke, correções ao iid e relatórios de validação. O **urwishpatel2003/tennis-engine** (licença MIT) tem a função `invert_to_target`, que faz exatamente a calibração "manter o nível, mexer na diferença". Para o nosso agente, a implementação stdlib da secção 2 basta: foi verificada contra os valores exatos destes repositórios e não precisa de numpy.

### Cited Findings
- **qitaoshi/tennis-model-v2:** "Pre-match tennis pricer... fair probabilities and decimal prices out for every standard market: match winner, exact set score, total games (full ladder), game handicap, tiebreak occurrence, per-player games".
  - Usa as fórmulas fechadas de Barnett & Clarke, com Monte Carlo apenas para verificar. `rules.py` guarda o formato por torneio e por ano. Correções ao iid em `corrections.py`.
  - HOLDOUT de 2026-01 a 07 (6.202 encontros): Brier 0,183; o vencedor tem ECE de 0,067 e sobrestima os azarões.
  - Depende de numpy, sklearn e parquet. Os dados TML estão em CC BY-NC-SA (uso não comercial).
  - Ramo por omissão: `odds-multi-market-eval`; último commit a 22/09/2026. — [GitHub](https://github.com/qitaoshi/tennis-model-v2) [médio]
- **urwishpatel2003/tennis-engine** (licença MIT, último commit a 31/08/2026): "surface-aware Elo blended with a point-level serve/return model through an exact Barnett-Clarke Markov chain. Win probability, set scores, game handicap and totals". Inclui `engine/markov.py::invert_to_target`. — [GitHub](https://github.com/urwishpatel2003/tennis-engine)
- **kylehawkinsa/sports-betting** (último commit a 24/09/2026): Markov hierárquico de Barnett–Clarke (ponto, jogo, tie-break, set, encontro). As probabilidades de vitória, o spread de jogos e o total saem da distribuição completa de jogos. Aceita SPW e RPW introduzidos à mão e tem teste "Markov vs 100k sim". — [GitHub](https://github.com/kylehawkinsa/sports-betting)
- Outros repositórios [não inspecionados em detalhe]:
  - [Seb943/Markov4Tennis](https://github.com/Seb943/Markov4Tennis): R; jogos, tie-breaks, sets e encontro.
  - [AndreaDesan/Tennis-Statistics](https://github.com/AndreaDesan/Tennis-Statistics)
  - [ishanshah3/markov-chains-tennis-model](https://github.com/ishanshah3/markov-chains-tennis-model): ajusta pela força de resposta do adversário.
  - [DIVAKAR92/Tennis_Match_Simulation](https://github.com/DIVAKAR92/Tennis_Match_Simulation)
  - Gist de probabilidade de set: [gist 776986](https://gist.github.com/776986)
  - [JeffSackmann/tennis_misc/tennisSetProbability.py](https://github.com/JeffSackmann/tennis_misc/blob/master/tennisSetProbability.py): o repositório já não está acessível. O qitaoshi regista que a conta de Sackmann "is down to a single public repository".
- **Dados:**
  - Encontros ATP e Challenger com estatísticas de serviço: TML-Database ([stats.tennismylife.org](https://stats.tennismylife.org)).
  - Odds Pinnacle e sets por encontro no formato tennis-data.co.uk (domínio bloqueado aqui; há uma cópia até 2018 em [edouardthom/ATPBetting](https://github.com/edouardthom/ATPBetting)).
  - Ponto a ponto: Match Charting Project (CC BY-NC-SA).

### Inferences
- Portar a secção 2 para `scripts/tenis.py` (ou para dentro de `odds.py`) com um comando do género `odds.py sets --p 0.60 --nivel 1.22`. É a opção mais simples e fica de acordo com a regra de "só stdlib".
- Convém acrescentar um teste que confirme 25,683 (0,64/0,64, melhor de 3) e 42,377 (melhor de 5, TB final de 10), para apanhar regressões.

### Gaps
- Não inspecionei as licenças de todos os repositórios. O qitaoshi não tem LICENSE visível, apenas os dados em CC BY-NC-SA. Por isso deve reimplementar-se, não copiar-se.
- Não encontrei uma calculadora pública "odds do vencedor → handicap de jogos" com validação publicada.

---

## 5. Formatos de pontuação em 2026 (ATP, WTA, Challenger, Grand Slams) que mudam as fórmulas

### Takeaway
Nos circuitos em foco (ATP 250/500/1000, Challengers e WTA), a melhor de 3 joga-se com **tie-break de 7 pontos a 6-6 em todos os sets, incluindo o 3.º**. O tie-break de 10 pontos a 6-6 no set decisivo **só existe nos Grand Slams**, desde 2022. O motor com `tb_final=7` serve para tudo o que é melhor de 3. Para os Grand Slams usa-se `tb_final=10`, à melhor de 5 nos homens e à melhor de 3 nas mulheres.

### Cited Findings
- **Livro de regras ATP 2026:** a Regra 1.02(B) define os encontros de singulares no ATP Tour e no ATP Challenger Tour como "best of three tie-break sets", com tie-break em todos os sets incluindo o 3.º. As ATP Finals também são à melhor de 3 com tie-break em todos os sets. Fonte: excerto de pesquisa; os PDFs estão bloqueados. — [2026 ATP Official Rulebook](https://www.atptour.com/-/media/files/rulebook/2026/2026-rulebook_19dec25.pdf); [alterações de abril de 2026](https://www.atptour.com/-/media/files/rulebook/2026/26rulebook-changes_apr2026v1.pdf)
- **Grand Slams:** a 16/03/2022 o Grand Slam Board anunciou um tie-break de 10 pontos (com 2 de vantagem) aos 6-6 no set final nos quatro majors. Antes:
  - Open da Austrália: já usava o tie-break de 10 pontos.
  - Roland Garros: não tinha tie-break no set decisivo.
  - Wimbledon: tie-break de 7 pontos a 12-12.
  - US Open: tie-break de 7 pontos a 6-6.
  - Fontes: [Tennis.com](https://www.tennis.com/news/articles/all-grand-slams-to-use-10-point-tiebreaker-in-final-set); [ESPN](https://www.espn.com/tennis/story/_/id/33516267/grand-slams-test-10-point-tiebreak-final-set-all-four-majors)
  - O `rules.py` do qitaoshi tem o mesmo histórico: AO com TB de 10 pontos desde 2019; Wimbledon com TB de 7 pontos a 12-12 entre 2019 e 2021 e de 10 pontos a 6-6 desde 2022; RG com TB de 10 pontos desde 2022; US Open com TB de 10 pontos desde 2022. — [rules.py](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/model/rules.py)
- O `rules.py` avisa que o formato do set decisivo "vary by tournament AND year", e que medir sem condicionar pelo formato cria artefactos. Por exemplo, um set com vantagens não pode acabar num tie-break decisivo. — [corrections.py](https://github.com/qitaoshi/tennis-model-v2/blob/odds-multi-market-eval/model/corrections.py)

### Inferences
- Para o foco atual (digressão asiática ATP/WTA e Challengers): melhor de 3, TB de 7 pontos em todos os sets. As fórmulas da secção 2 aplicam-se sem alterações.
- Formatos a excluir ou a tratar à parte:
  - NextGen Finals (sets curtos).
  - Pares, com super tie-break (match tie-break) de 10 pontos em vez do 3.º set.
  - Exibições.
  - Competições por equipas com formatos especiais.

### Gaps
- Não verifiquei diretamente no livro de regras da WTA de 2026 que o 3.º set termina num tie-break de 7 pontos. É o formato habitual e não encontrei indício de mudança, mas não o confirmei numa fonte primária.
- Não verifiquei se há torneios ATP/WTA de 2026 com formatos experimentais, como o "no-let".
