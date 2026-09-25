# Dimensionamento de stakes com muitas apostas simultâneas, incerteza no preço justo e maldição do vencedor (seleção adversa)

> **Contexto:** banca de 20 €, stop-loss aos 10 €, 5 a 30 apostas independentes abertas por dia (ténis, vencedor do encontro, uma por encontro). A regra atual é 1/4 de Kelly por aposta, com teto de 10 % e stake mínima de 0,10 €. O código atual (`scripts/banca.py`, `calcular_stake`) faz `fracao = 0.25 * ev / (odd - 1)` sobre a banca liquidada (não desconta as apostas pendentes), arredonda **para baixo** em passos de 0,10 € (`arredondamento: 0.1`) e devolve 0 se a stake ficar abaixo de 0,10 €.
>
> **Nota de método (importante para quem escrever o relatório):** nesta sessão, o proxy bloqueou o WebFetch em quase todos os domínios (arxiv.org, researchgate, sfu.ca, pinnacle.com, football-data.co.uk, dartmouth.edu, vegapit.com, github.io…). As citações abaixo baseiam-se nos resumos e excertos devolvidos pelo motor de pesquisa, não no texto integral. Onde uso uma fórmula que conheço do artigo mas que não consegui reler, está assinalado como **[não verificado nesta sessão]**. Os números marcados como **(cálculo próprio)** vêm de cálculos e simulações em Python stdlib feitos para esta nota. São inferências, não evidência publicada, e os pressupostos estão indicados.

---

## 1. Kelly simultâneo: frações ótimas para muitas apostas independentes ao mesmo tempo

### Takeaway
Com vantagens pequenas (EV de 3 a 10 %), o Kelly simultâneo exato de apostas independentes é quase igual ao Kelly isolado aplicado a cada aposta. A diferença é de ordem cúbica na vantagem e fica abaixo de 5 % enquanto a soma das frações de Kelly completo não passar de cerca de 0,8. Só diverge a sério quando essa soma se aproxima de 100 % da banca, porque o ótimo exato nunca arrisca a banca inteira. Para 1/4 de Kelly, isto dá uma regra simples e justificável: manter a fórmula por aposta e **escalar proporcionalmente as stakes do dia se o total em jogo passar de ~25 % da banca** (= 1/4 × 100 %). A heurística popular de multiplicar cada stake por Π(1−kⱼ) é demasiado conservadora.

### Cited Findings
- Whitrow (2007) trata a otimização de muitas apostas simultâneas com utilidade logarítmica. Desenvolve algoritmos de gradiente estocástico, compara-os com o método simplex e apresenta as soluções como uma generalização do Kelly para muitas apostas simultâneas, testada com odds reais de casas de apostas. Publicado no *Journal of the Royal Statistical Society, Series C*, 56(5), 607–. — [Wiley](https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9876.2007.00594.x); [Oxford Academic](https://academic.oup.com/jrsssc/article-abstract/56/5/607/7113514); [Semantic Scholar](https://www.semanticscholar.org/paper/Algorithms-for-optimal-allocation-of-bets-on-many-Whitrow/051166ffdf745d709dcf174da3e878e7d36f70f8)
- Long (2026, arXiv 2603.26620), "Optimal Parlay Wagering and Whitrow Asymptotics", dá três resultados para eventos independentes com múltiplas a preço multiplicativo:
  - Com singles, duplas, triplas e acima, o ótimo simultâneo é o produto externo das estratégias de Kelly de cada evento, e a riqueza final fatoriza-se por eventos.
  - Só com simples, o ótimo simultâneo obtém-se do ótimo isolado de cada evento por uma **contração cúbica**. As carteiras coincidem até à segunda ordem.
  - A perda de crescimento por proibir as múltiplas é **O(ε⁴)**, e as stakes simples ótimas só se afastam das de Kelly isolado na ordem cúbica.
  
  — [arXiv abs](https://arxiv.org/abs/2603.26620); [HTML](https://arxiv.org/html/2603.26620)
- Grant & Buchen (2013, *Journal of Gambling Business and Economics*, 6, 1–28) simularam (distribuição de Dirichlet, odds da Premier League 2007-08) três estratégias de Kelly simultâneo. **Kelly com múltiplas de todos os níveis superou a otimização de carteira só com simples.** — [EconPapers](https://econpapers.repec.org/article/bucjgbeco/v_3a6_3ay_3a2012_3ai_3a2_3ap_3a1-28.htm); [Semantic Scholar](https://www.semanticscholar.org/paper/A-Comparison-of-Simultaneous-Kelly-Betting-Grant-Buchen/426a552dc5c982df625fbd2e61a9e5aa895d442b). É uma tensão aparente com Long (2026): o ganho existe, mas é de 4.ª ordem para vantagens pequenas.
- Tepelyan & Lam (Bloomberg, 2026, arXiv 2604.24723):
  - A formulação ingénua do Kelly multivariado custa O(2^N) em tempo e memória.
  - Uma transformada integral para apostas independentes reduz o custo a O(N), resolvendo problemas com centenas de apostas.
  - Um método de decomposição dá limites inferior e superior para o crescimento ótimo.
  
  — [arXiv](https://arxiv.org/abs/2604.24723)
- Thorp (2006), "The Kelly Criterion in Blackjack, Sports Betting and the Stock Market", inclui um exemplo de apostas simultâneas em duas moedas favoráveis independentes, com frações f1 e f2 (o texto não foi lido nesta sessão). — [gwern mirror](https://gwern.net/doc/statistics/decision/2006-thorp.pdf); [Semantic Scholar](https://www.semanticscholar.org/paper/The-Kelly-Criterion-in-Blackjack-Sports-Betting,-Thorp/be7bf0c837214dabd650f98b52902ad7f92c06d4)
- Buchdahl escreveu "The Real Kelly Criterion" (Pinnacle, set/2017), com a forma generalizada do Kelly e aplicações a apostas simultâneas e a hedging. Não foi lido nesta sessão. — [Índice de artigos Buchdahl/Pinnacle](https://www.football-data.co.uk/blog/pinnaclesports_articles.php); [autor na Pinnacle](https://www.pinnacle.com/betting-resources/en/author/joseph-buchdahl)
- Em fóruns circula a heurística "Kelly simultâneo = cada Kelly × Π(1 − kⱼ) sobre todas as apostas". É opinião de fórum, sem derivação. — resumo da pesquisa com [2+2 forum](https://forumserver.twoplustwo.com/25/probability/kelly-criterion-simultaneous-bets-math-1644034/) e [SBR forum](https://www.sportsbookreview.com/forum/newbie-forum/1390215-placing-several-bets-once-using-kelly-criterion.html)
- Há soluções numéricas públicas do Kelly simultâneo (otimização numérica sobre o espaço conjunto de resultados). — [Vegapit](https://vegapit.com/article/numerically_solve_kelly_criterion_multiple_simultaneous_bets/)

### Inferences
**Porque é que a diferença é pequena (derivação própria, coerente com Long 2026).** Seja W = 1 + Σ fᵢXᵢ, com Xᵢ = bᵢ = oᵢ−1 com probabilidade pᵢ e −1 com probabilidade 1−pᵢ, μᵢ = pᵢoᵢ−1 e sᵢ = E[Xᵢ²] ≈ bᵢ. Até à 2.ª ordem, G ≈ Σfᵢμᵢ − ½Σfᵢ²sᵢ − ½Σ_{i≠j} fᵢfⱼμᵢμⱼ. Os termos cruzados são O(ε⁴), por isso o ótimo por aposta só muda na 3.ª ordem. Com N grande, porém, a soma dos termos cruzados cresce com N. A restrição de sobrevivência (W > 0 em todos os cenários, logo Σfᵢ < 1) passa a mandar quando Σ f_isolado → 1.

**Cálculo exato, N apostas idênticas (cálculo próprio).** O número de vitórias segue uma binomial, por isso a otimização é exata e unidimensional:

| odd | EV | N | f isolado | f simultâneo exato | razão | total simultâneo |
|---|---|---|---|---|---|---|
| 2,0 | 3 % | 10 | 3,00 % | 2,98 % | 0,992 | 29,8 % |
| 2,0 | 3 % | 30 | 3,00 % | 2,92 % | 0,973 | 87,6 % |
| 2,0 | 5 % | 10 | 5,00 % | 4,89 % | 0,977 | 48,9 % |
| 2,0 | 5 % | 20 | 5,00 % | 4,75 % | 0,949 | 95 % |
| 2,0 | 5 % | 30 | 5,00 % | ≤3,33 % | ≤0,666 | → ~100 % (restrição ativa) |
| 3,0 | 5 % | 30 | 2,50 % | 2,41 % | 0,964 | 72 % |
| 1,6 | 5 % | 10 | 8,33 % | 7,98 % | 0,958 | 80 % |
| 1,6 | 5 % | 20 | 8,33 % | ≤4,99 % | ≤0,60 | → ~100 % |
| 2,0 | 10 % | 10 | 10,0 % | 8,97 % | 0,897 | 90 % |

(Quando a restrição está ativa, o otimizador parou no limite de pesquisa de 99,9 % de exposição total: o ótimo exato fica muito perto de apostar quase toda a banca, repartida por N apostas quase sem correlação.)

**Cálculo exato, carteiras heterogéneas realistas (cálculo próprio).** Pressupostos: odds U(1,5; 3,5) e EV aparente = 3 % + Exp(média 2,5 %), com teto de 15 %. Solver exato em grelha (abaixo).
- N=10: Σf_isolado = 0,437 e Σf_simultâneo = 0,427. Razão por aposta de 0,974 a 0,984. Com 1/4 de Kelly, o total em jogo seria 10,9 % (ingénuo) contra 10,7 % (1/4 do simultâneo).
- N=20: 0,806 contra 0,767, razão de 0,948 a 0,957. Com 1/4 de Kelly, 20,2 % contra 19,2 %.
- N=30: 1,438 contra 0,998, razão de 0,62 a 0,97 (contração não uniforme). Com 1/4 de Kelly, **35,9 % contra 25,0 %**.
- Para a carteira de N=20, a heurística Π(1−kⱼ) daria um multiplicador de **0,435**, contra ~0,95 do ótimo exato. É demasiado conservadora.
- Um primeiro solver Monte Carlo (6000 cenários, gradiente estocástico ao estilo Whitrow) acertou no total (0,733 contra 0,767) mas deu frações por aposta muito ruidosas (razões de 0,34 a 2,6). Em Python puro, o Monte Carlo não serve para stakes individuais. Usar o método em grelha abaixo.

**Regra prática recomendada (inferência):**
1. Manter a fórmula por aposta, `f_i = c · EV_i/(o_i−1)` com c = 1/4.
2. Somar as stakes de **todas as apostas pendentes mais as novas**. Se o total passar de `c × 100 % = 25 %` da banca, multiplicar todas as novas stakes por `(25 % − pendente)/novas` e arredondar para baixo. Justificação: o total do Kelly simultâneo completo é sempre < 100 %, logo 1/4 dele é < 25 %. Abaixo de ~20 % de total em 1/4 de Kelly (Σf_iso ≤ 0,8), a fórmula ingénua erra menos de 5 %. Uma alternativa mais conservadora é um teto de 20 %.
3. Na simulação do sistema atual (secção 4), a exposição média por dia foi ~15 % da banca, por isso o teto de 25 % só atua em dias com 25 a 30 apostas.

**Algoritmo exato implementável em Python stdlib (cálculo próprio, testado).** É uma descida por coordenadas com a distribuição do "resto" numa grelha:
```
def dist_resto(bets, f, i, passo=0.0005):
    d = {0: 1.0}                                  # distribuição de R = Σ_{j≠i} f_j X_j em múltiplos de 'passo'
    for j,(p,o) in enumerate(bets):
        if j == i or f[j] == 0: continue
        up, dn = round(f[j]*(o-1)/passo), round(f[j]/passo)
        nd = {}
        for k, pr in d.items():
            nd[k+up] = nd.get(k+up, 0) + pr*p
            nd[k-dn] = nd.get(k-dn, 0) + pr*(1-p)
        d = {k: v for k, v in nd.items() if v > 1e-13}
    return d

def resolver_i(p, o, d, passo):                   # resolve E[X_i / W] = 0 por bisseção
    b = o - 1; itens = [(1 + k*passo, pr) for k, pr in d.items()]
    umin = min(u for u, _ in itens)
    g = lambda f: sum(pr*(p*b/(u+f*b) - (1-p)/(u-f)) for u, pr in itens)
    if g(0) <= 0: return 0.0
    lo, hi = 0.0, 0.999*umin
    for _ in range(50):
        m = (lo+hi)/2; lo, hi = (m, hi) if g(m) > 0 else (lo, m)
    return (lo+hi)/2

def kelly_simultaneo(bets, varrimentos=6, passo=0.0005):
    f = [max(0, (p*o-1)/(o-1)) for p, o in bets]; s = sum(f)
    if s > 0.9: f = [x*0.9/s for x in f]
    for _ in range(varrimentos):
        for i,(p,o) in enumerate(bets):
            f[i] = resolver_i(p, o, dist_resto(bets, f, i, passo), passo)
    return f          # stake_i = c * f[i] * banca (c = 1/4), depois teto de 10 % e arredondamento
```
O custo é O(varrimentos × N² × tamanho da grelha). Para N=30 correu em poucos segundos a minutos. Dado o ponto 2, o teto proporcional de 25 % aproxima isto bem e é trivial de implementar.

**Múltiplas.** Pelo resultado O(ε⁴) de Long (2026), o ganho teórico de acrescentar múltiplas é desprezável com EV de 3 a 10 %. A regra atual (no máximo uma múltipla por dia, teto de 5 %) não custa crescimento relevante. O resultado de Grant & Buchen, favorável às múltiplas, não contradiz isto, porque o ganho existe mas é pequeno.

### Gaps
- Não consegui ler o texto integral de Whitrow (2007), Thorp (2006), Buchdahl ("The Real Kelly Criterion") nem Tepelyan & Lam (2026). Faltam os números exatos dos exemplos deles, por exemplo quanto encolhem as stakes nos casos reais de Whitrow.
- Não encontrei nenhuma fonte com uma tabela publicada de "stake simultâneo vs isolado para 10–30 apostas". Os números acima são cálculo próprio.

---

## 2. Kelly com incerteza no parâmetro (probabilidade justa estimada com erro)

### Takeaway
Substituir p pela sua estimativa piora o desempenho fora da amostra. Baker & McHale (2013) mostram que a aposta deve ser contraída, e tanto mais quanto maior a incerteza em p, e que isso melhora os resultados em dados de ténis. Uma aproximação simples (derivação própria, na linha deles) é multiplicar o Kelly por **k ≈ EV²/(EV² + τ²)**, sendo τ o desvio-padrão do erro do EV (≈ odd × erro de p). Com τ ≈ EV, a contração é ~1/2. Para escolher a fração, o mais sólido é **calibrar com os próprios dados de fecho** (regressão do CLV sobre o EV aparente) e depois aplicar 1/4 de Kelly ao EV calibrado.

### Cited Findings
- Baker & McHale (2013, *Decision Analysis* 10(3):189–199):
  - O critério de Kelly ignora a incerteza na probabilidade de ganhar e usa uma estimativa, o que dá pior desempenho fora da amostra do que dentro dela.
  - Para melhorar o desempenho fora da amostra, a aposta deve ser contraída na presença dessa incerteza. Os autores comparam várias estimativas do fator de contração.
  - Numa simulação e em **dados de apostas de ténis**, o Kelly contraído melhora o Kelly "cru".
  - Uma das estimativas aproximadas dá uma correção "back of envelope" fácil de usar.
  - A contração ótima aumenta com a incerteza sobre a probabilidade estimada.
  - Estudam também contração e "inchaço" para utilidades avessas ao risco em geral.
  
  — [INFORMS](https://pubsonline.informs.org/doi/abs/10.1287/deca.2013.0271); [RePEc](https://ideas.repec.org/a/inm/ordeca/v10y2013i3p189-199.html); [Semantic Scholar](https://www.semanticscholar.org/paper/Optimal-Betting-Under-Parameter-Uncertainty:-the-Baker-McHale/d03cda6e9aec9a6674047b1c093780fdc2bf2d56); [ResearchGate](https://www.researchgate.net/publication/262425087_Optimal_Betting_Under_Parameter_Uncertainty_Improving_the_Kelly_Criterion)
- Chu, Wu & Swartz (2018), "Modified Kelly criteria", *Journal of Quantitative Analysis in Sports* 14(1):1–11, doi 10.1515/jqas-2017-0122: reconhecendo que p é desconhecido, obtêm critérios de Kelly modificados que têm em conta essa incerteza. — [De Gruyter](https://www.degruyter.com/view/journals/jqas/14/1/article-p1.xml); [PDF SFU](https://www.sfu.ca/~tswartz/papers/kelly.pdf); [Semantic Scholar](https://www.semanticscholar.org/paper/Modified-Kelly-criteria-Chu-Wu/e870c7a42018eba1c078b1efeb7061aa0ae4a977)
- Uhrín, Šourek, Hubáček & Železný (2021, *IMA Journal of Management Mathematics* 32(4):465–):
  - Testaram estratégias de carteira e de Kelly num protocolo comum, em corridas de cavalos, basquetebol e futebol.
  - Os resultados mostram a **necessidade prática de métodos adicionais de controlo de risco**.
  - Uma **variante adaptativa do Kelly fracionado** é "uma escolha muito adequada numa vasta gama de situações".
  
  — [arXiv 2107.08827](https://arxiv.org/abs/2107.08827); [Oxford Academic](https://academic.oup.com/imaman/article-abstract/32/4/465/6128334)
- Kelly generalizado para apostas não mutuamente exclusivas, com Kelly fracionado (JQAS 2021). — [De Gruyter](https://www.degruyterbrill.com/document/doi/10.1515/jqas-2020-0122/html?lang=en)

### Inferences
**Derivação própria do fator de contração** (coerente com a descrição de Baker & McHale; **a expressão exata deles não foi verificada nesta sessão**):
- Para uma aposta com odd o (b = o−1) e vantagem pequena, G(f) ≈ f·μ − ½f²·b, logo f* = μ/b.
- Se se usa f = k·μ̂/b, com μ̂ = μ + η, E[η] = 0 e Var(η) = τ², então E[G] = kμ²/b − ½k²(μ²+τ²)/b.
- Donde **k* = μ²/(μ² + τ²) = 1/(1 + (τ/μ)²)**. É um encolhimento "James-Stein" do EV para zero.
- Exemplos com o = 2:

| erro de p (dp) | τ (EV) | EV 3 % | EV 5 % | EV 8 % |
|---|---|---|---|---|
| 1 pp | 2 % | k = 0,69 | 0,86 | 0,94 |
| 1,5 pp | 3 % | 0,50 | 0,74 | 0,88 |
| 2,5 pp | 5 % | 0,26 | 0,50 | 0,72 |

- Consequência: as apostas no limiar (EV 3–4 %) são as mais afetadas. O 1/4 de Kelly fixo cobre esta contração quando τ ≤ ~EV, mas já não quando τ ≫ EV.

**Distinção importante (inferência):** com utilidade logarítmica, E_p[p·log(1+fb) + (1−p)·log(1−f)] é linear em p. Por isso, se p já for a **média a posteriori** (já encolhida para o mercado e corrigida do viés de seleção da secção 3), o Kelly ótimo é simplesmente Kelly com essa média. A contração de Baker & McHale é, na prática, a forma frequentista de fazer esse encolhimento. Daí duas correções separadas:
1. corrigir o **viés** do EV (seleção, secção 3);
2. contrair pela **variância** restante e pela aversão ao risco (fração de Kelly).

A regra atual (1/4 fixo) mistura as duas.

**Como escolher a fração a partir dos dados do utilizador (algoritmo proposto, inferência):**
```
# recomendacoes.csv: odd, prob_justa (no momento da recomendação), prob_fecho
pares = [(odd*pj - 1, odd*pf - 1) for (odd, pj, pf) in recs if pf]      # (EV aparente, CLV)
n = len(pares)
# Regressão OLS: CLV = a + k_hat * EV_aparente
k_hat = cov(EV, CLV)/var(EV); a_hat = mean(CLV) - k_hat*mean(EV)
# Encolher a própria estimativa enquanto n é pequeno (prior k0 = 0,5 e peso n0 = 50: valores de opinião)
w = n/(n + 50); k = w*k_hat + (1-w)*0.5;  a = w*a_hat
EV_calibrado = a + k*EV_aparente
stake = banca * 0.25 * max(0, EV_calibrado)/(odd - 1)                      # e depois teto de 10 %, teto total de 25 % e arredondamento
# Estimativa do ruído do preço justo: sd(prob_justa - prob_fecho) é um limite inferior de sigma_p
```
- Implicação para o risco: se o EV real for θ × EV aparente, apostar 1/4 do Kelly **aparente** equivale a apostar 0,25/θ do Kelly **real**. Com θ = 0,5 isso é 1/2 Kelly real; com θ = 0,25, Kelly completo; com θ < 0,125, mais do dobro de Kelly, e o crescimento esperado passa a ser negativo. Ver a tabela de drawdowns na secção 4.
- Erros comuns a todas as apostas (por exemplo, um viés sistemático do método de Shin nos favoritos ou nos outsiders de Challengers) **não se diversificam** com 30 apostas. É mais um argumento para o teto total de exposição (secção 1) e para calibrar k por segmento (ATP/WTA contra Challenger/ITF, favorito contra outsider) quando houver dados.

### Gaps
- Não consegui aceder à fórmula "back of envelope" exata de Baker & McHale nem aos valores de k que obtiveram nos dados de ténis. Os PDF (ResearchGate, academia.edu) estavam bloqueados.
- Também não consegui aceder às fórmulas de Chu, Wu & Swartz (prior Beta? critério de quantil?). O PDF da SFU estava bloqueado.
- Não encontrei nenhuma estimativa publicada do erro-padrão da probabilidade justa da Pinnacle para ténis antes do fecho, em particular nos Challengers. Tem de ser medida com os dados de `recomendacoes.csv`.

---

## 3. Maldição do vencedor / seleção adversa ao escolher a melhor odd

### Takeaway
Escolher a aposta com maior EV aparente, a melhor odd entre várias casas, ou a única casa fora da linha garante que, em média, o EV real é **menor** do que o estimado, mesmo com estimativas não enviesadas. É o "optimizer's curse" de Smith & Winkler (2006). A correção recomendada é bayesiana: **EV_real ≈ μ₀ + k·(EV_aparente − μ₀)**, com μ₀ ≈ −margem (a expectativa a priori de uma odd de casa "soft") e k = σ²_casas/(σ²_casas + σ²_preço justo). Numa simulação própria, com um erro do preço justo de ~2 pp, só ~35 % do EV aparente é real, e no limiar de 3–5 % o EV real é ~1 %. Acrescem os riscos de odd desatualizada e de "palpable error": a casa pode anular apostas ganhas em odds claramente fora do mercado.

### Cited Findings
- Smith & Winkler (2006, *Management Science* 52(3)), "The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis":
  - Se as estimativas de valor forem tomadas à letra e usadas para escolher, o valor real da alternativa escolhida deve ser, em média, inferior à estimativa, **mesmo que as estimativas sejam não enviesadas**.
  - A desilusão média resulta do processo de seleção.
  - Os autores propõem métodos bayesianos para ajustar as estimativas ("ceticismo disciplinado").
  
  — [INFORMS](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0451); [PDF Dartmouth](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Optimizers_Curse.pdf); [JSTOR](https://www.jstor.org/stable/20110511)
- Winner's curse (leilões): para o licitante vencedor, o valor esperado é negativo, ou seja, em média paga demais. — [Wikipedia](https://en.wikipedia.org/wiki/Winner%27s_curse)
- Kaunitz, Zhong & Kreiner (2017, arXiv 1710.02824), "Beating the bookies with their own numbers":
  - Estratégia: usar a probabilidade implícita no consenso das odds para encontrar odds mal cotadas.
  - Lucrativa em 10 anos de simulação com odds de fecho, em 6 meses com odds minuto a minuto e em 5 meses com dinheiro real.
  - Com dinheiro real fizeram **256 apostas de 50 $, taxa de acerto de 47,2 %, lucro de 957,50 $ (retorno de 8,5 %)**.
  - As casas limitaram as contas, nalguns casos a stakes de 1,25 $.
  
  — [arXiv](https://arxiv.org/abs/1710.02824); [Digital Trends](https://www.digitaltrends.com/cool-tech/scientists-beat-the-bookies-sports-gambling/); [MIT Technology Review](https://www.technologyreview.com/2017/10/19/67760/the-secret-betting-strategy-that-beats-online-bookmakers/); [código e dados (GitHub)](https://github.com/Lisandro79/BeatTheBookie). O README do GitHub confirma que as casas bloquearam as contas.
- Buchdahl, "Wisdom of the Crowd": apostar nas casas "soft" quando a odd era superior à odd "verdadeira" da Pinnacle deu ~**3,6 % de ROI** em **31 247 apostas** ao longo de 14 temporadas (fonte secundária). — [pinnacleoddsdropper (resumo)](https://www.pinnacleoddsdropper.com/blog/joseph-buchdahl's-betting-strategy); [PDF original](https://www.football-data.co.uk/The_Wisdom_of_the_Crowd_updated.pdf) (não consegui abri-lo)
- "Palpable error":
  - A casa pode anular uma aposta aceite com um erro óbvio de preço, muitas vezes mesmo quando é vencedora. Algumas pagam à odd "correta".
  - O critério é, na prática, o resto do mercado: "se dez casas oferecem 2/7 e uma oferece 7/2, a outlier é um palpable error". É a própria casa que decide, e os T&C são vagos.
  
  — [Betting Offers UK](https://www.bettingoffers.uk/articles/palpable-error-can-the-bookie-refuse-refuse-to-pay-out-on-a-winning-bet/); [Caanberry](https://caanberry.com/warning-palpable-errors-in-betting/); [RulesofSport](https://www.rulesofsport.com/betting/articles/palpable-error-can-a-bookie-refuse-to-pay-out/)
- Fontes da indústria (qualidade média-baixa, opinião):
  - Tratar a melhor odd como prova de valor é um erro, porque a melhor odd pode continuar abaixo do justo.
  - Um comparador lento mostra odds que a casa já mexeu (odds desatualizadas).
  - Quando várias casas "soft" erram da mesma forma (os mesmos fornecedores de dados), a outlier pode não ter valor face à probabilidade real.
  
  — [Outlier.bet](https://help.outlier.bet/en/articles/8269410-positive-ev-101-what-is-expected-value); [OddsPapi](https://oddspapi.io/blog/player-props-value-scanner-python/); [ValueBetFactory](https://valuebetfactory.com/betting-education/best-odds-comparison-sites)

### Inferences
**Simulação própria da maldição do vencedor** (pressupostos: p real ~ U(0,25; 0,75); a "Pinnacle sem margem" tem um erro normal σ_pin em logit; K casas "soft" com erro σ_soft = 0,10 logit (≈ 2,5 pp em p = 0,5) e margem de 3 pp por lado (≈ 6 % de overround, EV a priori ≈ −5,7 %); escolhe-se a melhor odd e o lado com maior EV aparente; aposta-se se o EV aparente ≥ 3 %; 60 000 encontros por linha):

| σ_pin (≈ pp em p=0,5) | K casas | ρ (a soft copia o erro da Pinnacle) | % encontros com aposta | EV aparente médio | EV real médio | real/aparente | EV real se aparente 3–5 % / 5–8 % / 8–12 % / >12 % |
|---|---|---|---|---|---|---|---|
| 0 (0 pp) | 5 | 0 | 24 % | +5,4 % | +5,4 % | 1,00 | +3,9 / +6,2 / +9,4 / +14,0 |
| 0,04 (1 pp) | 5 | 0 | 31 % | +5,7 % | +4,0 % | 0,71 | +2,6 / +4,5 / +7,1 / +10,7 |
| 0,04 (1 pp) | 1 | 0 | 7 % | +5,4 % | +3,7 % | 0,68 | +2,4 / +4,4 / +7,0 / +11,1 |
| 0,08 (2 pp) | 5 | 0 | 43 % | +6,6 % | +2,3 % | 0,35 | **+1,0** / +2,2 / +3,8 / +6,2 |
| 0,08 (2 pp) | 5 | 0,5 | 19 % | +5,1 % | +1,2 % | 0,24 | +0,5 / +1,8 / +3,6 / +6,1 |
| 0,08 (2 pp) | 1 | 0 | 13 % | +6,1 % | +1,1 % | 0,18 | −0,2 / +1,3 / +2,8 / +5,4 |
| 0,12 (3 pp) | 5 | 0 | 55 % | +7,8 % | +1,3 % | 0,17 | +0,2 / +1,0 / +1,8 / +3,5 |
| 0,12 (3 pp) | 1 | 0 | 21 % | +7,1 % | −1,0 % | <0 | −2,1 / −1,2 / −0,2 / +1,7 |

Leituras (inferências):
1. A maldição depende sobretudo do **ruído do preço justo** (σ_pin), não do número de casas.
2. Com um preço justo nítido (≤ 1 pp de erro, típico do fecho em mercados líquidos), ~70 % do EV aparente é real.
3. Com um preço justo pouco nítido (≥ 2 pp, plausível em Challengers ou em linhas de abertura com limites baixos), o limiar de 3 % deixa passar apostas com EV real ~0–1 %. O limiar efetivo tem de subir.
4. Quando a casa "soft" copia o erro da própria referência (ρ > 0), é pior.
5. A fórmula bayesiana `EV_real ≈ μ₀ + k(EV_ap − μ₀)`, com `k = σ_soft²/(σ_soft² + σ_pin²)` e μ₀ ≈ −5,7 %, reproduz razoavelmente a simulação. Com σ_pin = 0,04, k = 0,86 e o previsto é +4,1 % (simulado: +4,0 %). Com σ_pin = 0,08, k = 0,61 e o previsto é +1,8 % (simulado: +2,3 %). É uma aproximação, não exata.

**Regras propostas (inferência / opinião fundamentada):**
- **Calibrar em vez de adivinhar:** usar a regressão CLV ~ EV aparente da secção 2. É a medida direta da maldição com os dados do utilizador, porque o fecho da Pinnacle serve de "verdade" aproximada. Com a amostra atual pequena, usar k0 = 0,5 como prior.
- **Outlier de uma só casa:** se a odd só tem valor numa casa, e essa casa está > 5–8 % acima da 2.ª melhor, calcular também o "EV robusto" com a 2.ª melhor odd. Se o EV robusto for < limiar, exigir EV ≥ 2× o limiar (por exemplo, ≥ 6 % contra a Pinnacle) **e** confirmação manual da odd (a regra dos 60 minutos já existe).
- Um EV aparente muito alto (por exemplo, > 15 % contra a Pinnacle num vencedor de encontro de ténis) deve ser tratado como suspeito (odd desatualizada, palpable error, lesão ou desistência conhecida) antes de ser tratado como oportunidade. Isto é coerente com o papel dos subagentes como filtros.
- **Assimetria do palpable error:** se a casa anula as ganhas e mantém as perdidas, o EV de uma odd claramente fora do mercado pode ser negativo, seja qual for o EV aparente.
- A limitação de contas (Kaunitz) é seleção adversa do lado da casa. Não altera a stake ótima, mas reduz a capacidade e reforça a regra de distribuir as apostas pelas várias casas.

### Gaps
- Não encontrei um estudo publicado que meça diretamente "EV aparente contra rendimento realizado, por escalão de EV" para odds máximas contra a Pinnacle. Não consegui abrir o PDF "Wisdom of the Crowd" de Buchdahl, que provavelmente tem esses dados.
- Não encontrei dados sobre a frequência de palpable errors ou de anulações nas casas licenciadas em Portugal (SRIJ).
- Os parâmetros da simulação (σ_pin, σ_soft, margem) são pressupostos. O utilizador deve estimá-los com `recomendacoes.csv` e `varredura.json`.

---

## 4. Tetos de exposição diária/total e matemática de drawdowns com 1/4 de Kelly (stop-loss de 50 %)

### Takeaway
Na aproximação de difusão, com vantagem conhecida, a probabilidade de a banca **alguma vez** cair para uma fração x do valor atual, apostando a fração c do Kelly, é **x^(2/c − 1)**. Com c = 1/4, a probabilidade de alguma vez perder 50 % é 0,5⁷ ≈ **0,8 %**. Com 1/2 Kelly é 12,5 %, com Kelly completo 50 %, e com 2× Kelly há ruína de crescimento. Esta probabilidade é praticamente independente do número de apostas simultâneas, desde que sejam independentes e a fração seja medida face ao ótimo da carteira. O risco real vem do **erro na vantagem**: com EV real = metade do aparente, 1/4 "aparente" é 1/2 real (12,5 %). Na simulação Monte Carlo do sistema atual, atingir o stop-loss em ~1000 candidatas é raro se houver vantagem (0,1–1,4 %) e mais provável se o EV real for −2 % (~10 %). **Atingir o stop-loss é sobretudo sinal de ausência de vantagem, não de azar.**

### Cited Findings
- Um apostador em Kelly completo tem 1/3 de probabilidade de reduzir a banca a metade antes de a duplicar, e 1/n de a reduzir alguma vez a 1/n. Com meio Kelly, a probabilidade de a reduzir a metade antes de a duplicar é 1/9. — [Wikipedia, Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion) (via resumo de pesquisa)
- Thorp obteve fórmulas analíticas para a probabilidade de um drawdown de X % com Kelly completo e fracionado. Kelly completo tem 50 % de probabilidade de um drawdown de 50 %; com meio Kelly essa probabilidade cai para 12,5 %, e a taxa de crescimento só cai 25 %. — [PMC, "A Rational Risk Policy? Why Path Dependence Matters"](https://pmc.ncbi.nlm.nih.gov/articles/PMC9955835/); [MacLean, Thorp & Ziemba, "Good and bad properties of the Kelly criterion"](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf); [MacLean, Thorp & Ziemba (eds.), The Kelly Capital Growth Investment Criterion (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1797366)
- Busseti, Ryu & Boyd, "Risk-Constrained Kelly Gambling" (Stanford), formulam o Kelly com uma restrição de drawdown. **[Não verificado nesta sessão, fórmula que conheço do artigo]:** com λ = log β / log α, a restrição E[(rᵀb)^(−λ)] ≤ 1 garante Prob(riqueza mínima < α) < β. — [PDF Stanford](https://web.stanford.edu/~boyd/papers/pdf/kelly.pdf)
- Uhrín et al. (2021) concluem que, na prática, é necessário controlo de risco adicional ao Kelly, e que o Kelly fracionado adaptativo funciona bem numa vasta gama de situações. — [arXiv 2107.08827](https://arxiv.org/abs/2107.08827)
- Opinião de blogs (qualidade baixa, não verificável): "1/4 de Kelly é a configuração profissional mais comum"; "a maioria dos operadores aposta 1/4 ou 1/2 de Kelly para amortecer os drawdowns". — resumo de pesquisa com [WagerBird](https://wagerbird.com/learn/kelly-criterion), [Sportstrade](https://www.sportstrade.io/blog-detail/141/the-fractional-kelly-bankroll-management-system.html) e [Quant Matter](https://quantmatter.com/kelly-criterion-formula/). A atribuição exata a cada site é incerta.

### Inferences
**Tabela de drawdowns (cálculo próprio com a fórmula x^(2/c−1); confere com os valores publicados 1/2, 1/3, 1/9 e 12,5 %):**

| fração do Kelly **real** (c) | P(banca alguma vez ≤ 50 %) | P(−50 % antes de +100 %) | crescimento relativo ao Kelly completo (c − c²/2)/0,5 |
|---|---|---|---|
| 0,25 | **0,78 %** | 0,78 % | 44 % |
| 0,33 | 3,1 % | 3,0 % | 56 % |
| 0,50 | 12,5 % | 11,1 % | 75 % |
| 0,75 | 31,5 % | 24,0 % | 94 % |
| 1,00 | 50 % | 33,3 % | 100 % |
| 1,50 | 79 % | 44 % | 75 % |
| 2,00 | 100 % | – | 0 % |

- **Ligação ao Kelly com restrição de risco:** P ≤ β com α = 0,5 exige 2/c − 1 ≥ λ = log β/log 0,5, ou seja **c ≤ 2/(1 + λ)**. Com β = 5 %, c ≤ 0,38. Com β = 1 %, c ≤ 0,26. Por isso, 1/4 de Kelly corresponde a ~1 % de risco de tocar no stop-loss, *se* o EV estiver certo.
- **Efeito do erro no EV:** c_real = 0,25/θ, sendo θ = EV real/EV aparente. Com θ = 0,5, P ≈ 12,5 %. Com θ = 0,33, c_real = 0,75 e P ≈ 31 %. Com θ ≤ 0,125 o crescimento é negativo. Se o EV real for ≤ 0, a banca acaba por tocar no stop-loss com probabilidade que tende para 1, à medida que o volume cresce.
- **Monte Carlo do sistema atual (cálculo próprio).** Pressupostos:
  - banca de 20 €, paragem quando ≤ 10 €;
  - 5 a 30 apostas por dia (uniforme), odds U(1,5; 3,5), EV aparente 3 % + Exp(2,5 %) com teto de 15 %;
  - stakes calculadas no início do dia sobre a banca liquidada, com a regra exata de `calcular_stake` (1/4 de Kelly, teto de 10 %, arredondamento para baixo a 0,10 € e zero se < 0,10 €);
  - horizonte de ~1000 apostas candidatas (~57 dias) e 800 trajetórias por linha.

| EV real | política | P(stop-loss) | banca mediana final | apostas feitas / 1000 | stake real / alvo 1/4 Kelly | exposição média por dia |
|---|---|---|---|---|---|---|
| = aparente | atual (passos de 0,10) | 0,1 % | 34,92 € | 932 | 0,84 | 15,8 % |
| = aparente | cêntimos (passos de 0,01) | 0,4 % | 36,88 € | 932 | 0,97 | 18,4 % |
| = aparente | atual + teto total de 25 % | 0,0 % | 32,59 € | 870 | 0,83 | 14,4 % |
| = aparente | EV × 0,5 (≈ 1/8 Kelly) | 0,0 % | 25,26 € | 492 | 0,28 | 5,4 % |
| = 1/2 do aparente | atual | 0,9 % | 24,93 € | 880 | 0,80 | 15,2 % |
| = 1/2 do aparente | cêntimos | 3,0 % | 25,58 € | 873 | 0,94 | 17,9 % |
| = 1/4 do aparente | atual | 1,4 % | 21,51 € | 853 | 0,79 | 14,9 % |
| = 0 | atual | 2,8 % | 18,99 € | 822 | 0,77 | 14,6 % |
| = 0 | cêntimos | 9,5 % | 18,11 € | 801 | 0,92 | 17,4 % |
| = −2 % | atual | 9,8 % | 15,27 € | 767 | 0,75 | 14,1 % |
| = −2 % | cêntimos | 18,9 % | 15,01 € | 742 | 0,90 | 17,0 % |
| = −2 % | EV × 0,5 | 0,0 % | 18,56 € | 404 | 0,25 | 4,8 % |

- Leituras:
  1. Com a banca pequena e os passos de 0,10 €, o sistema atual aposta na prática ~0,8 × 1/4 de Kelly, ou seja **≈ 1/5 de Kelly aparente**.
  2. A probabilidade de stop-loss num horizonte de ~2 meses é baixa em todos os cenários com vantagem. Passa a ser relevante (~10 %) quando o EV real é negativo.
  3. A **razão de verosimilhança** "stop-loss | EV −2 %" contra "stop-loss | EV real" é ~10 a 100×. Tocar no stop-loss é forte evidência contra a vantagem, o que é coerente com as regras 5 e 6 do CLAUDE.md.
  4. A regra de CLV (100 recomendações) deve disparar antes do stop-loss na maioria dos cenários sem vantagem.
- **Teto de exposição total:** não encontrei fontes fiáveis sobre tetos diários de profissionais. A recomendação de **≤ 25 % da banca em jogo em simultâneo** (com 1/4 de Kelly) vem da matemática da secção 1, não de prática documentada. O CLAUDE.md diz "sem limite diário de exposição" por decisão do utilizador. Este teto é um limite **matemático** do Kelly simultâneo, que raramente atua (em média ~15 % em jogo), e não um limite discricionário. Cabe ao utilizador decidir.

### Gaps
- Não encontrei dados publicados e fiáveis sobre tetos de exposição diária usados por apostadores profissionais. As fontes disponíveis são blogs.
- A fórmula x^(2/c−1) assume difusão contínua, vantagem conhecida e horizonte infinito. Com apostas discretas, um horizonte finito e o piso da stake mínima (que corta as apostas quando a banca desce), a probabilidade real é menor, como mostra o Monte Carlo.
- Não consegui verificar no PDF a formulação exata do Kelly com restrição de risco (Busseti, Ryu & Boyd).

---

## 5. Efeitos do arredondamento e da stake mínima numa banca muito pequena

### Takeaway
Com 20 € e passos de 0,10 €, o arredondamento para baixo corta em média ~16–25 % da stake de 1/4 de Kelly e elimina as apostas cujo 1/4 de Kelly fica abaixo de 0,10 €. Isso acontece sobretudo com os outsiders de EV baixo: com odd 3,5 e EV 3 %, 1/4 de Kelly dá 0,06 €. Funciona como uma contração extra (~1/5 de Kelly efetivo), útil enquanto a vantagem não está provada. **Arredondar para cima até ao mínimo, ou passar a cêntimos, aumenta o risco.** Com EV real 0, a probabilidade de stop-loss sobe de 2,8 % para 9,5 % na simulação.

### Cited Findings
- Não encontrei literatura específica sobre stake mínima e arredondamento em bancas muito pequenas. O efeito geral de a stake ficar acima ou abaixo de Kelly segue da mesma matemática: apostar mais do que Kelly aumenta a variância e acima de 2× Kelly o crescimento fica negativo. — [Wikipedia, Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion); [MacLean, Thorp & Ziemba](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)
- Uhrín et al. (2021) apontam o Kelly fracionado adaptativo como a variante robusta. — [arXiv 2107.08827](https://arxiv.org/abs/2107.08827)

### Inferences
**Exemplos com o código atual (banca de 20 €; cálculo próprio):**

| odd | EV aparente | 1/4 de Kelly (%) | alvo (€) | stake após arredondamento | fração efetiva do Kelly |
|---|---|---|---|---|---|
| 2,0 | 5 % | 1,25 % | 0,25 | 0,20 | 0,20 |
| 2,0 | 3 % | 0,75 % | 0,15 | 0,10 | 0,17 |
| 1,6 | 5 % | 2,08 % | 0,42 | 0,40 | 0,24 |
| 3,5 | 5 % | 0,50 % | 0,10 | 0,10 | 0,25 |
| 3,5 | 3 % | 0,30 % | 0,06 | **0 (recusada)** | 0 |
| 2,0 | 3 % (banca 12 €) | 0,75 % | 0,09 | **0 (recusada)** | 0 |

- À medida que a banca desce para os 10–13 €, cada vez mais candidatas caem abaixo dos 0,10 € e são recusadas. É um travão automático (anti-ruína) que reduz o risco perto do stop-loss, mas também reduz a amostra de apostas.
- Regras propostas:
  1. **Arredondar sempre para baixo, nunca para cima até ao mínimo**, como o código já faz.
  2. Se se quiser incluir apostas cujo 1/4 de Kelly fica entre 0,05 € e 0,10 €, arredondar para cima só se 0,10 € ≤ 1/2 Kelly, ou seja, se o alvo de 1/4 for ≥ 0,05 €, e só depois de o CLV estar provado (por exemplo, ≥ 100 fechos com CLV médio > 0 e IC95 acima de 0).
  3. Manter os passos de 0,10 € enquanto a vantagem não está provada. Passar a cêntimos (se as casas o permitirem) só depois de o CLV estar provado.
  4. **Não misturar a recusa por stake mínima com a amostra de CLV:** para medir o agente, registar em `recomendacoes.csv` também as candidatas com valor cuja stake ficou abaixo do mínimo, assinaladas como "stake 0". Assim a regra de paragem (100 fechos) acumula amostra mais depressa, sem risco de dinheiro. Esta é uma sugestão de desenho, não uma evidência.
- **Ordem de aplicação** recomendada para `calcular_stake`:
  1. EV calibrado (secção 2 e 3);
  2. 1/4 de Kelly;
  3. teto de 10 % por aposta;
  4. teto total de 25 % em jogo (secção 1), com escala proporcional;
  5. arredondamento para baixo a 0,10 €;
  6. recusa se < 0,10 €.

### Gaps
- Não verifiquei as stakes mínimas reais nem os incrementos das casas do utilizador (`casas` em `config.json`). O valor de 0,10 € vem do `config.json`, não de uma verificação das casas.
- Não encontrei estudos publicados sobre o efeito da granularidade da stake no crescimento ou na ruína de bancas muito pequenas. Os resultados acima são só simulação própria.
