# Testes com histórico

Gerado com `scripts/backtest.py`, com stake fixa de 1 unidade e odds entre 1,40 e 4,00. O "IC 95%" é a margem de erro do ROI. Um resultado só é fiável quando o ROI, descontada essa margem, continua do mesmo lado do zero.

## Conclusões (o que muda no agente)
1. **Os modelos próprios perdem para o mercado.**
   - O Elo (por superfície no ténis, o do clubelo no futebol) prevê pior do que as odds, nos dois desportos.
   - Misturá-lo com o mercado também piora.
   - No futebol, apostar com o Elo deu −1,9% a −2,8% de ROI, um resultado significativo.
   - Por isso nenhum modelo próprio entra no cálculo das probabilidades. É a mesma conclusão do teste aos LLMs (ver abaixo).
2. **Comparar odds entre casas é o que elimina a margem.**
   - Apostar em tudo na Bet365 deu −8,6%.
   - Apostar em tudo à melhor odd do mercado deu +0,4%.
3. **Apostar quando a melhor odd está acima do preço justo dá lucro, e significativo.**
   - Futebol: +2,4% com EV ≥ 3% e +5,1% com EV ≥ 5%, em dezenas de milhares de apostas.
   - Ténis: +4,1% com EV ≥ 3% e +16,4% com EV ≥ 8%.
   - É a estratégia que o agente passa a usar.
4. **Com uma só casa "mole", o resultado não se confirmou.** A Bet365 acima da Pinnacle, no ténis, deu −2% a −5%, com poucas apostas e uma margem de erro grande. O lucro histórico vem de haver muitas casas por onde escolher.
   - Com 3 ou 4 contas em casas portuguesas vai haver menos oportunidades, e mais fracas.
   - Ter mais contas licenciadas ajuda.
   - O CLV vai dizer ao fim de cerca de 100 recomendações se chega.
5. **Limiares mantidos:** EV ≥ 3% contra a Pinnacle e ≥ 5% contra a média. Revêem-se com o CLV medido: sobem se o CLV sair negativo.

## Ténis ATP 2004–2018: 25 226 encontros com odds da Pinnacle
Dados: tennis-data.co.uk, via [edouardthom/ATPBetting](https://github.com/edouardthom/ATPBetting). Preço justo: Pinnacle sem margem (Shin). Só encontros terminados, e só jogadores com pelo menos 20 encontros.

| Probabilidades | Log-loss | Brier |
|---|---|---|
| Pinnacle (Shin) | **0,5652** | **0,3851** |
| Elo por superfície | 0,5917 | 0,4067 |
| 80% Pinnacle + 20% Elo | 0,5667 | 0,3861 |

| Estratégia | EV mínimo | Apostas | Acerto | ROI | IC 95% |
|---|---|---|---|---|---|
| Bet365, todas as seleções | — | 30 888 | 44,8% | −8,6% | ±1,2% |
| Bet365 acima da Pinnacle | 3% | 645 | 39,5% | −5,0% | ±9,7% |
| Bet365 acima da Pinnacle | 5% | 310 | 39,0% | −2,3% | ±14,5% |
| Melhor odd, todas as seleções | — | 17 504 | 48,6% | +0,4% | ±1,7% |
| Melhor odd acima da Pinnacle | 2% | 4 677 | 48,2% | +2,8% | ±3,3% |
| Melhor odd acima da Pinnacle | 3% | 3 511 | 47,7% | **+4,1%** | ±3,9% |
| Melhor odd acima da Pinnacle | 5% | 1 984 | 46,0% | +5,6% | ±5,4% |
| Melhor odd acima da Pinnacle | 8% | 899 | 47,7% | **+16,4%** | ±8,5% |
| Elo contra a melhor odd | 5% | 7 319 | 46,6% | +1,7% | ±2,7% |

Por ano (melhor odd, EV ≥ 3%): positivo em 7 de 8 anos. 2011 deu +0,1% e 2017 deu −0,5%.

## Futebol 2005–2026: 211 056 jogos de 38 divisões
Dados: [xgabora/Club-Football-Match-Data-2000-2025](https://github.com/xgabora/Club-Football-Match-Data-2000-2025), com a Bet365 e a máxima de cerca de 17 casas europeias. Este conjunto não tem a Pinnacle, por isso o preço justo aqui é a Bet365 sem margem (Shin).

| Probabilidades (2016/17 em diante, Elo treinado antes) | Log-loss | Brier |
|---|---|---|
| Bet365 (Shin) | **0,9908** | **0,5915** |
| Elo (clubelo) | 1,0103 | 0,6046 |
| 80% Bet365 + 20% Elo | 0,9918 | 0,5922 |

| Estratégia | EV mínimo | Apostas | Acerto | ROI | IC 95% |
|---|---|---|---|---|---|
| Melhor odd acima do justo | 2% | 54 227 | 38,6% | +1,5% | ±1,1% |
| Melhor odd acima do justo | 3% | 33 808 | 38,3% | **+2,4%** | ±1,5% |
| Melhor odd acima do justo | 5% | 13 440 | 38,3% | **+5,1%** | ±2,4% |
| Melhor odd acima do justo | 8% | 4 102 | 37,3% | +4,8% | ±4,4% |
| Elo contra a melhor odd (2016+) | 5% | 41 180 | 34,7% | −1,9% | ±1,4% |
| Mistura contra a melhor odd (2016+) | 5% | 6 191 | 34,4% | −2,4% | ±3,5% |

Por ano (EV ≥ 5%): positivo em 18 de 22 anos.

## LLMs no Mundial 2026 (a nossa regra aplicada às previsões deles)
Dados: [graphuofm/FIFA2026LLM](https://github.com/graphuofm/FIFA2026LLM), com 104 jogos e odds reais. Apliquei a nossa regra anterior (EV ≥ 4%, odds de 1,40 a 4,00) às probabilidades de cada LLM:

| LLM | Apostas | ROI |
|---|---|---|
| ChatGPT | 12 | −20,9% |
| Claude | 13 | −8,5% |
| Gemini | 34 | +13,2% |
| Grok | 32 | +0,2% |

No total dá cerca de +1% em 91 apostas, indistinguível do acaso. Nenhum LLM previu melhor do que o mercado. Por isso, o LLM passou de gerar as probabilidades a filtrar as candidatas.

## Limitações
- As odds históricas não dizem a que hora foram recolhidas. Uma parte das "melhores odds" pode estar desatualizada ou ser de casas que não existem em Portugal.
- Estes dados não permitem medir o CLV: o futebol não tem a odd de fecho da Pinnacle neste conjunto.
- Resultados passados não garantem resultados futuros. Quem ganha de forma consistente acaba com a conta limitada (Kaunitz et al., 2017).

## Reproduzir
```
pip install -r requirements-backtest.txt
git clone --depth 1 https://github.com/edouardthom/ATPBetting /tmp/atp
git clone --depth 1 https://github.com/xgabora/Club-Football-Match-Data-2000-2025 /tmp/futebol
python3 scripts/backtest.py tenis /tmp/atp/Data
python3 scripts/backtest.py futebol /tmp/futebol/data/Matches.csv
```
**Com a rede aberta, o próximo passo** é repetir com os CSV do football-data.co.uk, que têm a Pinnacle e o fecho (`PSH`, `PSCH`, etc.). É o teste mais próximo das casas portuguesas: Bet365 acima da Pinnacle, com o CLV medido. O script já lê esse formato.
