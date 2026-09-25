# Fair price from an average of bookmaker odds (no Pinnacle) and CLV from consensus snapshots

> Research notes, 25/09/2026. Context: the agent's "alvos" path uses tennisexplorer average odds (many books, refreshed ~4x/day, 3–5 h delay), devigged with Shin (`scripts/odds.py`), and recommends a bet when a bookmaker odd ≥ 1.05 / p_fair (EV ≥ 5% vs consensus). No closing odds are stored on this path.
>
> **Access caveat:** this session's network policy blocked arxiv.org, pinnacle.com, football-data.co.uk, substack, technologyreview.com, pinnacleoddsdropper.com, outlier.bet and others. Most external facts below therefore come from search-engine result summaries (not full-text reads), and are marked "(search summary)". GitHub was reachable, so I ran an original check on public tennis data (ATP 2010–2018 from tennis-data.co.uk, via [edouardthom/ATPBetting](https://github.com/edouardthom/ATPBetting)); those results are marked "(own computation)". The script is `devig_avg.py` in the session scratchpad; its method is described inline so it can be rebuilt.

---

## 1. Kaunitz, Zhong & Kreiner (2017): exact consensus formula, alpha, performance, and what it means for our 5% threshold

### Takeaway
Kaunitz et al. did **not** devig. They took p_cons = 1 / (mean decimal odds across bookmakers). They found that true frequency ≈ p_cons − α, with α estimated at 0.034 / 0.057 / 0.037 (home / draw / away). They bet when the **maximum** odds on offer exceeded 1/(p_cons − 0.05). This returned about +3.5% over 56,435 simulated bets and made a real-money profit (265 bets) before bookmakers limited their accounts. Their α = 0.05 is an **additive buffer in probability space**. Because it is additive, it demands a larger EV on longshots than on favourites. A flat "+5% EV" rule does the opposite: it demands the same relative EV at every price.

### Cited Findings
- **Formula (search summary of the paper):** "p_real = p_cons − α", where p_cons is "calculated from bookmakers' average odds". Expected payoff is "E(Π) ≈ (p_cons − α)·ω − 1". The strategy bets "whenever the maximum odds offered … fulfils max(Ω) > 1/(p_cons − 0.05)". — [arXiv 1710.02824](https://arxiv.org/abs/1710.02824); [PDF](https://arxiv.org/pdf/1710.02824)
- **Estimated α:** 0.034 (home win), 0.057 (draw), 0.037 (away win). The consensus probability is "an extremely accurate proxy (up to a constant intercept) of the actual probability". — [arXiv 1710.02824](https://arxiv.org/abs/1710.02824) (search summary)
- **Choice of α = 0.05:** it "produced the optimal payoff with the largest amount of games". An α of 0.06 is reported as equally profitable, and the summary also says it "provided twice as many games to bet on". That is contradictory, because a larger α should select *fewer* games, so the summary probably garbled this; check the PDF. — [arXiv PDF](https://arxiv.org/pdf/1710.02824) (search summary)
- **10-year historical simulation (closing odds):**
  - $98,865 profit over 56,435 bets at $50 each (about 3.5% return), with accuracy of about 44%.
  - Chance of doing this well by random betting: "less than 1 in a billion".
  - Media report the simulation as covering "479,440 soccer games played between 2005 and 2015". The repo says the dataset holds 880,494 matches from 2000–2015, so the simulation was presumably run on a subset.
  - Sources: [Digital Trends](https://www.digitaltrends.com/cool-tech/scientists-beat-the-bookies-sports-gambling/); [digit.fyi](https://www.digit.fyi/boffins-bookies-banhammer/); [GitHub README](https://github.com/Lisandro79/BeatTheBookie)
- **Paper trading:** 407 bets of $50 made $1,128.50, a 5.5% return (1,128.5 / 20,350 = 5.5%, so the figures are consistent). The paper describes this as a "6-month historical simulation using minute-to-minute odds" plus paper trading. — [MIT Technology Review](https://www.technologyreview.com/2017/10/19/67760/the-secret-betting-strategy-that-beats-online-bookmakers/) (search summary)
- **Real money (5 months):** bets won 47.2% of the time, for a profit of $957.50 at a reported "8.5% return".
  - **Conflicting bet count:** MIT Technology Review says 265 bets; digit.fyi and Digital Trends say 256.
  - **Return does not match flat stakes:** at a flat $50, 957.5 / (265 × 50) = 7.2%, or 7.5% with 256 bets, not 8.5%. Stakes may have varied.
  - Sources: [MIT TR](https://www.technologyreview.com/2017/10/19/67760/the-secret-betting-strategy-that-beats-online-bookmakers/); [digit.fyi](https://www.digit.fyi/boffins-bookies-banhammer/)
- **Account limits:** bookmakers "would no longer accept their wagers, or would limit them to amounts as small as $1.25". The repo README concludes that "the effort of deploying such a strategy is completely worthless, considering the time spent on the betting and the monetary reward". — [digit.fyi](https://www.digit.fyi/boffins-bookies-banhammer/); [GitHub README](https://github.com/Lisandro79/BeatTheBookie)
- **Data:** closing odds for 880,494 football matches (2000–2015) across 912 leagues, plus minute-by-minute odds series for 2015–2016. Code is MATLAB, PHP and SQL. — [GitHub BeatTheBookie](https://github.com/Lisandro79/BeatTheBookie)
- **Own computation — Kaunitz rule on tennis:**
  - Data: ATP 2010–2018 (2014 missing), 17,274 completed matches.
  - Rule: Max > 1/(1/Avg − 0.05). Max odds were capped at ≤ 1.25 × Avg to drop outliers, with odds between 1.40 and 4.00.
  - Result: 1,735 bets. Mean edge vs Pinnacle fair odds (Shin) was **+4.1%** (SE 0.15%); 66% of bets had a positive edge vs Pinnacle. Realised ROI was +3.4% (SE 2.8%).
  - With α = 0.02 or 0.03, the edge vs Pinnacle fell to about +0.5% and +1.0%.
  - Source: dataset [edouardthom/ATPBetting](https://github.com/edouardthom/ATPBetting), from [tennis-data.co.uk](http://www.tennis-data.co.uk/notes.txt)

### Inferences
- **What α means.** Using raw 1/avg without devigging, α does two jobs: it removes the average margin per outcome, and it adds a safety buffer. In football 1X2, α ≈ 0.034–0.037 on home and away is basically the per-outcome margin, so the 0.05 used adds a buffer of about **1.3–1.6 percentage points (pp)** on top of it. For draws, 0.05 is actually *below* the estimated α of 0.057.
- **The same rule in our terms.** For tennis the average overround is about 6% (own computation: Avg 1.060, Pinnacle 1.024, Bet365 1.067), so the margin is about 3 pp per side. The Kaunitz rule then becomes: bet when odds ≥ 1/(p_fair − 0.02). As EV vs the consensus fair price, that means:

  | p_fair | 0.70 | 0.50 | 0.40 | 0.33 | 0.25 |
  |---|---|---|---|---|---|
  | EV required | 2.9% | 4.2% | 5.3% | 6.4% | 8.7% |

  Our flat 5% is stricter on favourites and **looser on underdogs** than Kaunitz.
- **Where Kaunitz's edge came from.** They took the **best price across dozens of books**, including outliers and stale lines, measured against a **fresh** consensus. The user bets only at his own licensed Portuguese books, against a consensus that is 3–5 h old. Their returns are therefore an upper bound for us.
- **Account limits.** The paper supports the project's existing rule of spreading bets across books when one of them limits the account.

### Gaps
- I could not read the full PDF to confirm: the number of bookmakers averaged, whether "average" is the arithmetic mean of decimal odds, the exact accuracy figure (44.4%?), and the resolution of 256 vs 265 real-money bets.
- The authors' GitHub is MATLAB code. I could not open the strategy script (the GitHub API was restricted in this session).

---

## 2. Devigging an average: Shin vs power vs multiplicative vs additive vs odds-ratio, especially for tennis two-way markets and the favourite–longshot bias

### Takeaway
- **Shin is the additive method in two-way markets.** For a two-outcome market, Shin's method gives *exactly* the same probabilities as the additive method (verified numerically; maximum difference 3e-16). So `shin()` in `odds.py` is, for tennis, simply p_i = 1/o_i − (1/o_1 + 1/o_2 − 1)/2.
- **Methods compared on the tennis average:** Shin/additive, power and odds-ratio are statistically tied. **Multiplicative is clearly worse** and leaves a large favourite–longshot bias.
- **The literature:**
  - Clarke et al. (2017): power ≥ Shin > multiplicative.
  - Štrumbelj (2014): Shin > normalisation.
  - arXiv 2604.17194 (April 2026): a newer method (OO-EPC) beats all three on football.
  - Maurice Berk (August 2026): argues it is "time to retire Shin's method". I could not read the article's content.

### Cited Findings
- **Formulas**, with r_i = 1/o_i. All are from the `implied` package vignette, [opisthokonta/implied](https://github.com/opisthokonta/implied) ([vignette](https://raw.githubusercontent.com/opisthokonta/implied/master/vignettes/introduction.Rmd)).
  - **Multiplicative (basic):** p_i = r_i / Σr. The vignette says it "tend[s] to be the least accurate of the methods in this package".
  - **Additive:** p_i = r_i − (Σr − 1)/n. It "can produce negative probabilities" for longshots.
  - **Power:** p_i = r_i^(1/k), with k chosen so that Σp_i = 1. Buchdahl calls this the "logarithmic" method.
  - **Odds ratio:** p_i = r_i / (OR + r_i − OR·r_i), with OR chosen so that Σp_i = 1 (Cheung; Buchdahl).
  - **WPO (margin weights proportional to odds, Buchdahl):** p_i = (n − M·O_i) / (n·O_i), where M is the margin.
  - **Other methods in the package:** Shin, balanced books, JSD, and OO-EPC.
- **Shin, as implemented in `odds.py`:** p_i = (√(z² + 4(1−z)·r_i²/Σr) − z) / (2(1−z)), with z solved so that Σp = 1. — `/home/user/cris/scripts/odds.py` (lines 62–78)
- **Clarke, Kovalchik & Ingram (2017):**
  - They propose the power method, which "never produces bookmaker or fair probabilities outside the 0–1 range and allows for the favourite–longshot bias".
  - It "universally outperforms the multiplicative method and outperforms or is comparable to the Shin method".
  - Tested on "three large bookmaker datasets across different sports including tennis".
  - Weaknesses of the others: additive can go negative; normalisation ignores the favourite–longshot bias; normalisation and Shin can give bookmaker probabilities > 1 "when applied in reverse".
  - Sources: [Science Publishing Group](https://www.sciencepublishinggroup.com/article/10.11648/j.ajss.20170506.12); [ResearchGate](https://www.researchgate.net/publication/326510904_Adjusting_Bookmaker's_Odds_to_Allow_for_Overround) (search summary)
- **Štrumbelj (2014), *International Journal of Forecasting*:**
  - Probabilities from Shin's model are "more accurate forecasts than those determined using basic normalization" and than regression models.
  - Some bookmakers are significantly better sources of probabilities than others.
  - "The advantage of using Shin probabilities decreases with an increasing market size."
  - Source: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207014000533) (search summary)
- **arXiv 2604.17194 (April 2026), "Forecast Sports Outcomes under Efficient Market Hypothesis":**
  - Multiplicative, Shin and power "do not adjust for biases found" in 90,014 football matches across five bookmakers.
  - The proposed OO-EPC (odds-only, equal-profitability-confidence) method "outperforms existing odds-only methods" for most bookmakers.
  - A one-parameter model that adjusts for the favourite–longshot bias (FL-GLM) is also proposed.
  - A search summary quoted power-method log losses of about 1.0033–1.0046 per bookmaker (Bet365, Bet&Win, Interwetten, Pinnacle, William Hill, football 1X2).
  - Source: [arXiv 2604.17194](https://arxiv.org/abs/2604.17194) (search summary)
- **Maurice Berk (3 August 2026), "It's Time to Retire Shin's Method":** Berk wrote the Python `shin` package and previously recommended the method. He says that "after running the numbers" his view changed. I could not access the content. — [Substack](https://algorithmicsportsbetting.substack.com/p/its-time-to-retire-shins-method); [mberk/shin](https://github.com/mberk/shin) (search summary)
- **Practitioner guidance (opinion, not evidence):**
  - "Multiplicative on two-way markets, power on three-way" as a starting point.
  - Power "sits between multiplicative and Shin" in how much it corrects the favourite–longshot bias.
  - "Worst case" means taking the most conservative EV across all methods.
  - Sources: [Outlier help](https://help.outlier.bet/en/articles/8208129-how-to-devig-odds-comparing-the-methods); [Bet Hero](https://betherosports.com/blog/devigging-methods-explained) (search summaries)
- **Own computation — accuracy by method.** ATP 2010–2018, 17,274 completed matches; log loss on the probability given to the actual winner (lower is better).

  | Source | mult | additive = Shin | power | odds-ratio |
  |---|---|---|---|---|
  | Pinnacle | 0.55608 | **0.55579** | 0.55585 | 0.55581 |
  | Average (Oddsportal) | 0.55763 | 0.55620 | **0.55612** | **0.55612** |
  | Bet365 | 0.55718 | **0.55638** | 0.55694 | 0.55647 |

  Paired differences on the average:
  - power − Shin = −0.00008 (SE 0.00023): **not significant**.
  - multiplicative − Shin = +0.00143 (SE 0.00027): **significantly worse**.
- **Own computation — favourite–longshot bias.** Mean (observed win rate − predicted probability) for the favourite, by probability band:

  | Method | 0.7–0.8 | 0.8–0.9 | Overall |
  |---|---|---|---|
  | avg / multiplicative | +3.35 pp | +3.55 pp | +1.69 pp (SE 0.33) |
  | avg / Shin (= additive) | +1.70 pp | +1.21 pp | +0.55 pp |
  | avg / power | +1.04 pp | −0.04 pp | −0.14 pp |
  | Pinnacle / Shin | +1.46 pp | +1.17 pp | +0.58 pp |

  Positive values mean favourites win more often than priced, i.e. the underdog's fair probability is overstated.

### Inferences
- **Stop worrying about the method, with one exception.** For tennis two-way markets, Shin (= additive), power and odds-ratio are practically equivalent on the average. The difference, about 0.0001 log loss, is tiny next to the noise from a stale consensus (see Q3 and Q6). The exception is **multiplicative on the average, which must be avoided**: it leaves the underdog's fair probability about 3 pp too high in the 0.7–0.9 favourite band, so underdog EV is overstated.
- **A conservative alternative.** Compute the underdog's fair probability as min(Shin, power), and the favourite's as min as well: a "worst-case" fair price. This protects against the residual favourite–longshot bias Shin leaves in the 0.7–0.9 band (about +1.2 to +1.7 pp, roughly 1.5 SE, so only suggestive).
- **Devigging an average is not the same as devigging one sharp book.**
  - The average carries more margin (6.0% vs 2.4% for Pinnacle in the tennis data).
  - Soft books shade longshots more, so the average carries more favourite–longshot bias to remove.
  - The average of decimal odds is not the reciprocal of the average of probabilities (Jensen's inequality), which slightly inflates longshot odds.
  - The numbers show it: multiplicative loses 0.0003 log loss on Pinnacle but 0.0014 on the average.
  - Where per-book odds are available (The Odds API path), devig each book and then average the probabilities, which `odds.py` already does. Avoid devigging an average of odds when you can.

### Gaps
- I could not read the tables in Clarke et al. (2017) (outlier.bet blocked), so I do not know which tennis dataset and bookmaker they used.
- I could not read the content of Berk's 2026 article.
- I could not confirm that `implied` documents Shin ≡ additive for two outcomes. It is verified numerically here.

---

## 3. Is the market consensus (average of many books) as accurate as Pinnacle?

### Takeaway
- **Accuracy is close, per match:** in tennis ATP at the price-collection timestamp, the devigged average is only marginally less accurate than devigged Pinnacle (Δ log loss +0.0004, not significant).
- **Precision is the problem, per bet.** The two fair prices differ by a standard deviation of about 4% in fair odds. Only about 56% of an "edge" measured against the consensus survives against Pinnacle.
- **Other studies:** in golf, the best combined forecast puts 95–100% of the weight on Pinnacle. Buchdahl and others consider Pinnacle's close the most efficient line.

### Cited Findings
- **DataGolf (golf matchups):** "If you were to optimally predict matchup results using the closing odds from all books, the best predictions would be achieved by putting 95–100% of the weight on Pinnacle." Other books' closing odds "add little predictive value", and Pinnacle's odds "move the most from opening to close". — [DataGolf, "How sharp are bookmakers?"](https://datagolf.com/how-sharp-are-bookmakers) (search summary)
- **Buchdahl, "Wisdom of the Crowd":** removes Pinnacle's margin to get "true" odds and finds that Pinnacle is "relatively more efficient than the rest". — [football-data.co.uk, Pinnacle wisdom](https://www.football-data.co.uk/blog/pinnacle_wisdom.php); [The Wisdom of the Crowd (PDF)](https://www.football-data.co.uk/The_Wisdom_of_the_Crowd_updated.pdf) (search summary)
- **Using Pinnacle pre-closing odds as the truth:** over 14 seasons, betting soft books whenever they beat Pinnacle had an expected profit of $1,176.72 (3.8% ROI) and a realised $1,117.56 (3.6% ROI). This came from a search summary in which Godsofodds and Pinnacle Odds Dropper pages on Buchdahl's method were listed; the exact attribution is uncertain. — [Godsofodds](https://godsofodds.com/en/previews/using-pinnacle-s-odds-to-build-a-profitable-betting-system); [Pinnacle Odds Dropper](https://www.pinnacleoddsdropper.com/blog/joseph-buchdahl's-betting-strategy)
- **Pre-registered football study (GitHub, 2026; unknown author, moderate credibility):**
  - Pinnacle's closing line was well calibrated in 2016/17–2022/23 (logistic slope 1.044, intercept +0.028).
  - It was **not** calibrated in the 2023/24–2025/26 holdout (slope 1.096, intercept +0.062). Longshots "won 372 times against 422.5 expected", about 2.6 SD below.
  - The study used proportional devig and the market-average close.
  - Source: [football-market-efficiency](https://github.com/urajimiruliss-arch/football-market-efficiency)
- **"Forecasting soccer matches with betting odds: A tale of two markets" (*IJF* 2024; authors not verified):** the traditional 1X2 market is "systematically biased" (favourite–longshot bias). Pinnacle's Asian-handicap market "behaves in an efficient manner … shows no pattern of favourite–longshot bias". — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0169207024000670); [MPRA PDF](https://mpra.ub.uni-muenchen.de/116925/1/MPRA_paper_116925.pdf) (search summary)
- **Own computation (tennis ATP 2010–2018, same timestamp):**
  - Log loss: average/Shin 0.55620 vs Pinnacle/Shin 0.55579, a difference of +0.00040 (SE 0.00031).
  - Fair-probability gap |p_avg − p_pin|: mean 1.15 pp, 90th percentile 2.35 pp, 99th percentile 4.3 pp.
  - SD of log(fair odds from average / fair odds from Pinnacle) = **0.040**.
  - Across all sides, regressing the edge vs Pinnacle on the edge vs consensus (both at Max odds) gives **edge_pin = 0.002 + 0.557 × edge_avg** (n = 20,984).
  - Mean edge vs Pinnacle by consensus-edge bucket:

    | Edge vs consensus | Mean edge vs Pinnacle | n |
    |---|---|---|
    | 3–5% | +2.0% | 1,697 |
    | 5–8% | +3.3% | 960 |
    | 8–12% | +6.2% | 374 |
    | ≥ 12% | +11.4% | 136 |

  - Source: [ATPBetting data](https://github.com/edouardthom/ATPBetting)
- **Tennis-data field definitions:** PSW/PSL = Pinnacle odds; MaxW/AvgW = "Maximum / Average odds … as shown by Oddsportal.com". Files are updated weekly. — [tennis-data notes](http://www.tennis-data.co.uk/notes.txt) (search summary)

### Inferences
- **Why the average can be so accurate here.** The Oddsportal average includes Pinnacle and many books that copy it, so in liquid ATP main-tour matches at close it is nearly as informative *on average* as Pinnacle.
- **Why that is not enough.** For **bet selection**, what matters is the per-match error, not average calibration. With an SD of about 4% between the two fair odds, a 5% "edge" is only about 1.25 SD of consensus noise. Selecting on it produces a winner's curse: about 44% of the measured edge is noise.
- **Where it will be worse.** Challengers and WTA 125 events have fewer books, less Pinnacle influence and slower lines, so the consensus will be noisier there than in this ATP sample.
- **Timing.** These numbers compare two prices collected at the *same* time. The user's consensus is 3–5 h stale, which adds line-movement noise on top (see Q6).

### Gaps
- There is no public study comparing average vs Pinnacle accuracy specifically for tennis Challengers.
- I could not read Buchdahl's "Squares & Sharps" or the pinnacle_wisdom figures in full.
- The collection time of tennis-data's odds (closing or not) is not stated in the summary I could access. It is commonly treated as close to closing.

---

## 4. CLV: evidence that beating the close predicts profit, sample sizes, and the standard-error formula

### Takeaway
Buchdahl's analysis of Pinnacle data shows that the ratio of the odds taken to Pinnacle's devigged closing price predicts ROI almost one-to-one. Because the SD of CLV per bet is about 0.07–0.10, against about 1.0–1.2 for profit per unit staked, a 3% edge becomes statistically visible in CLV after roughly **20–50 bets**, but in profit only after roughly **4,000–7,000 bets**.

### Cited Findings
- **Buchdahl's evidence:** "four seasons of Pinnacle closing odds across 87,960 odds pairs" from major European football leagues. The ratio of an earlier price to Pinnacle's closing price "predicts the expected return … with an almost perfect one-to-one relationship". — [Pinnacle Odds Dropper, "CLV demystified by Joseph Buchdahl"](https://www.pinnacleoddsdropper.com/blog/closing-line-value--clv-demystified-by-expert-joseph-buchdahl) (search summary)
- **Variance:** the "typical standard deviation in even-money profits and losses will be about 1.00, while the equivalent for CLV will be about 0.1". Consistently beating the close can reach significance in "perhaps as few as just 50" bets. A system with mean EV of 1.72% needed "many thousands of wagers" on profit, but "as few as 65 bets" using price movement. — [Pinnacle Odds Dropper](https://www.pinnacleoddsdropper.com/blog/closing-line-value--clv-demystified-by-expert-joseph-buchdahl); [howprosbet](https://howprosbet.com/what-is-closing-line-value/) (search summaries)
- **Caveat on the 50-bet figure:** "a sample of around fifty bets can sometimes show an early signal, although it is not enough to prove a durable edge on its own". — [howprosbet](https://howprosbet.com/what-is-closing-line-value/) (search summary)
- **Choice of closing source:** "use one bookmaker or declare a named closing source, as different operators can legitimately close at different prices". Market-average closing odds are "common, but … not always precise; accuracy depends on which bookmakers are used, how margins are removed, and market liquidity". — [Bet-Analytix](https://www.bet-analytix.com/academy/closing-odds-ultimate-indicator) and CLV-calculator pages (search summary)
- **Own computation (tennis):** among bets selected by "Max ≥ 1.05 / p_avg", the per-bet edge vs Pinnacle had SD ≈ 0.07 (0.063–0.075 across odds bands). Mean edge vs Pinnacle was +4.6% and realised ROI was +6.7% (SE 3.5%, n = 1,395). The two agree within noise. — [ATPBetting data](https://github.com/edouardthom/ATPBetting)
- **Timing claim (low quality, unverified):** bets placed more than 24 h out average +1.2% CLV, while final-hour bets average −0.5%. — [Sharp Football Analysis](https://www.sharpfootballanalysis.com/sportsbook/clv-betting/) (search summary; treat as opinion)

### Formulas (standard statistics; my derivation, consistent with Buchdahl's numbers)
- **Per-bet CLV:**
  - CLV_i = o_taken,i × p_close,i − 1, where p_close,i is the **devigged** closing probability of the selection.
  - Log form: c_i = ln(o_taken,i × p_close,i). It is more symmetric and adds up across bets.
- **Mean and standard error:**
  - Unweighted mean: m = (1/n) Σ CLV_i.
  - Sample SD: s = √(Σ(CLV_i − m)² / (n − 1)).
  - **SE = s / √n**, and t = m / SE.
  - Stake-weighted version: m_w = Σw_iCLV_i / Σw_i and SE_w = √(Σw_i²(CLV_i − m_w)²) / Σw_i.
  - If bets can share an event, cluster by event.
- **Profit per unit staked at odds o with EV e:** Var = (1 + e)(o − 1 − e) ≈ o − 1, so SD ≈ √(o − 1). This gives 1.0 at o = 2 (matching Buchdahl) and 1.22 at o = 2.5.
- **Bets needed for t = 2:** n ≈ (2s / m)².
  - CLV, s = 0.07: m = 3% → n ≈ 22; m = 2% → 49.
  - CLV, s = 0.10: m = 3% → 44; m = 2% → 100.
  - Profit at o = 2.5: m = 3% → about 6,700; m = 5% → about 2,400.
- **Checking the project's stop rule** (stop if mean CLV ≤ 0 after 100 recommendations with a close). At n = 100, SE ≈ 0.7–1.0 pp.
  - If the true CLV is +3%, the chance of a false stop is ≤ 0.1%.
  - If the true CLV is +1%, it is 8–16%.
  - So the rule is well calibrated for detecting an edge of 3% or more.

### Inferences
- **Trust the CLV only if the close is sharp.** CLV is the right primary metric, but its link to ROI was demonstrated against **Pinnacle's** close. Against a consensus close, it inherits the consensus noise and bias from Q3.
- **Scale it down when translating.** Expect CLV measured vs the consensus to overstate CLV vs a sharp close. The tennis shrinkage slope is about 0.56, so a +5% consensus CLV is roughly +3% vs sharp.
- **Use the agent's own s.** Compute s from the agent's own CLV records instead of assuming 0.1. With a noisy consensus close, s rises: √(0.07² + 0.04²) ≈ 0.08 from the consensus-noise component alone.

### Gaps
- I could not read Buchdahl's original Pinnacle article or book chapter, so the exact regression slope and intercept are unverified.
- There is no tennis-specific published CLV-vs-ROI study.

---

## 5. Measuring CLV with only periodic snapshots of a consensus (last snapshot before start as the close)

### Takeaway
"Last consensus snapshot before start" is only a **weak proxy**. It can be 3–9 h before the real close (refresh ~4x/day plus a 3–5 h publishing delay). If it is the *same* snapshot that selected the bet, the CLV is mechanically about equal to the selection EV (≥ 5%) and **means nothing**. Measure CLV only against a strictly later snapshot, flag how old it is, report the consensus movement separately, and add an independent sharp close wherever possible (Pinnacle from tennis-data after the fact, The Odds API, or Betfair).

### Cited Findings
- **Why the close matters:** closing lines incorporate "injuries, weather, public betting trends, and wiseguy (sharp) action". Opening and early lines are the least efficient, and limits rise as the close nears. — [Sharp Football Analysis](https://www.sharpfootballanalysis.com/sportsbook/clv-betting/); [Boyd's Bets](https://www.boydsbets.com/opening-vs-closing-line/) (search summaries; practitioner opinion)
- **Earlier vs closing prices:** Buchdahl's Pinnacle series ("How to solve a problem like efficiency", parts 1–2) tests whether earlier prices or the closing price are more efficient, and the effect of anchoring on odds movement. — [Pinnacle Betting Resources](https://www.pinnacle.com/betting-resources/en/educational/how-to-solve-a-problem-like-efficiency-part-two/KS5JTMY67W9XFGGM); [Sports Trading Network mirror](https://www.sportstradingnetwork.com/article/how-to-solve-a-problem-like-efficiency-part-two/) (content not read; search listing only)
- **Independent close for tennis:** tennis-data.co.uk publishes Pinnacle (PSW/PSL), Max and Avg (Oddsportal) odds for ATP/WTA matches, updated weekly after each tournament. This can serve as a retrospective closing price for main-tour matches. — [tennis-data notes](http://www.tennis-data.co.uk/notes.txt); [data page](http://www.tennis-data.co.uk/data.php) (search summary)
- **OddsPortal** archives historical closing odds. — [search summary of CLV-calculator pages](https://www.bet-analytix.com/academy/closing-odds-ultimate-indicator)

### Recommended computation (inference, built on the formulas in Q4)
1. **At recommendation time** (snapshot s0, published at t_pub0), store:
   - the odds taken o and the book;
   - p0 = devig(consensus at s0);
   - the snapshot's publish time and its data age;
   - the match start T.
2. **At every later snapshot s_k** (and at the pre-match check about 40 min before start), store p_k = devig(consensus at s_k) with its timestamp.
3. **Closing proxy:** s\* = the last snapshot with s0 < s\* ≤ T. It must be strictly after s0; if there is none, record `clv = n/a`. Flag the gap g = T − (data time of s\*):
   - g ≤ 2 h: **good**;
   - 2–6 h: **weak**;
   - more than 6 h, or s\* = s0: **not measured**.
4. **Metrics:**
   - CLV_cons = o × p\* − 1, where p\* is the devigged fair probability at s\*.
   - Consensus movement M = p\* / p0 − 1; positive means the market moved toward our pick.
   - The two are linked: **1 + CLV_cons = (1 + EV0)(1 + M)**, where EV0 = o × p0 − 1 ≥ 5% by construction.
   - So CLV_cons can only add information through M. Report M (mean, SE, and the share of M > 0) as the real test of the consensus path.
5. **Independent sharp close** where possible:
   - Pinnacle from tennis-data for ATP/WTA main-tour matches, retrospectively;
   - The Odds API (the source `odds.py valor` already uses when Pinnacle is present);
   - Betfair.
   - CLV_sharp = o × p_Pinnacle,close − 1 is the metric the stop rule (rule 6) should use when available.
6. **Report CLV_sharp and CLV_cons separately,** with coverage (the % of recommendations that have each). Do not pool them.

### Inferences
- **Why a stale close understates true CLV.** If the soft book's high price was *right*, i.e. the consensus lagged and later moved toward that price, then M < 0 and CLV_cons shrinks. Consensus-based CLV therefore penalises exactly the bets where the soft book was stale but correct, and rewards those where the consensus drifted our way. Only M and CLV_sharp can separate these cases.
- **When the proxy becomes meaningless.** For Asian-swing matches (early morning in Lisbon) under a ~4x/day refresh with a 3–5 h delay, the last snapshot will often be the same one used for selection. Those rows should read "CLV not measurable", not "+5%".
- **Rough mapping to a sharp CLV.** Given Q3, a consensus CLV of +5% corresponds to roughly +3% sharp CLV (slope 0.56) *at the same time*. With staleness it will be less.

### Gaps
- I found no published method or study specifically on "CLV from periodic consensus snapshots". The recommendations above are derived, not sourced.
- I could not measure tennis line movement between T−6 h and T (no timestamped series available here), so I cannot quantify the extra noise from staleness.
- I have not verified The Odds API's historical-snapshot granularity or plan requirements in this session.

---

## 6. What EV threshold is appropriate against a consensus average, given its noise and staleness?

### Takeaway
- **5% is the minimum, not a comfortable margin.** At *fresh* (closing-time) consensus, a 5% consensus edge corresponds to about a 3% edge vs Pinnacle, which is the project's sharp threshold. So 5% is the break-even translation.
- **Staleness needs more.** A 3–5 h old consensus warrants a higher bar.
- **Underdogs need more still,** because of the favourite–longshot bias and the higher error there.
- **Suggestion (inference):** require EV ≥ max(5%, 0.02 / (p_fair − 0.02)), i.e. a Kaunitz-style buffer of 2 pp in probability. Add about +2 pp of EV when the snapshot is older than about 3 h.

### Cited Findings
- **Kaunitz:** bet if max odds > 1/(p_cons − 0.05) on raw (non-devigged) 1/avg. This is equivalent to an additive probability buffer of about 1.5 pp beyond the margin in football. — [arXiv 1710.02824](https://arxiv.org/abs/1710.02824) (search summary)
- **Own computation — threshold sweep.** Rule: Max ≥ (1 + T)/p_avg_Shin, with Max ≤ 1.25 × Avg and odds 1.40–4.00, ATP 2010–2018. One side per match, chosen by the larger consensus edge.

  | T | n | Mean edge vs Pinnacle | Median | % of bets with positive edge vs Pinnacle | Realised ROI (SE) |
  |---|---|---|---|---|---|
  | 0% | 7,875 | +1.1% | −0.2% | 49% | +2.2% (1.3) |
  | 3% | 2,864 | +3.1% | +2.1% | 60% | +4.7% (2.4) |
  | **5%** | **1,395** | **+4.6%** | **+4.2%** | **66%** | **+6.7% (3.5)** |
  | 8% | 494 | +7.5% | +8.4% | 75% | +4.5% (6.0) |
  | 10% | 270 | +9.7% | +10.4% | 82% | +7.9% (8.0) |

  Source: [ATPBetting data](https://github.com/edouardthom/ATPBetting)
- **Own computation — how much of the consensus edge survives.** Bets selected at ≥ 5% had a mean edge of 7.8% vs the consensus, but only 4.75% vs Pinnacle.
- **Own computation — 5% rule by odds band** (edge vs Pinnacle):
  - 1.40–2.00: +6.7% (n = 297);
  - 2.00–3.00: +4.5% (n = 636);
  - 3.00–4.00: +3.8% (n = 519).

  The edge that survives falls as the odds rise.
- **Own computation — devig method in the threshold rule:**
  - Multiplicative devig of the average at 5%: edge vs Pinnacle only +2.9% (median +1.4%), n = 2,722, ROI +4.1%.
  - Power at 5%: +5.4% (n = 1,133).
  - Multiplicative lets through many false underdog "values".
- **Own computation — a mainstream soft book (Bet365) against the consensus.** Bet365 ≥ 1.05/p_avg happened only **19 times in 8 years** (odds 1.40–4.00). The edge vs Pinnacle was +0.7% (SE 3.0%) and the median −0.5%: no real value. The Max-odds edge comes mostly from outlier or niche books.
- **Data caveat:** tennis-data Max odds contain outliers. Without the 1.25 × Avg filter, "edges" of +90% or more appear. 12.5% of matches had Max > 1.25 × Avg on at least one side. — [ATPBetting data](https://github.com/edouardthom/ATPBetting)

### Inferences
- **Keep 5% as the floor and scale it.** Keep "EV ≥ 5% vs consensus", but add:
  - (a) **an odds-dependent buffer:** EV ≥ max(5%, 0.02 / (p_fair − 0.02)). This gives 5.3% at p = 0.40, 6.4% at 0.33 and 8.7% at 0.25, and matches Kaunitz in spirit and the band results above.
  - (b) **a staleness surcharge:** +2 pp when the consensus snapshot's data is more than about 3 h old or the match starts more than 12 h after the snapshot. This is a judgement call; the data here cannot quantify it.
  - (c) **the fair price from power or Shin, never multiplicative.** Optionally use the "worst-case" fair price, min(Shin, power), for the side being bet.
- **Expect few qualifying bets.** Portuguese books' margins are similar to or higher than Bet365's (about 6–7%). Qualifying bets at the user's books will therefore be rare, and those that pass may be stale or erroneous prices, which the pre-match check must confirm. "Hoje: não apostar" should be the common outcome on this path.
- **Keep the rules as they are.** None of this changes the project rules: ¼ Kelly via `banca.py`, the 10% cap, and CLV as the main metric. The only change is that the 5% threshold is a floor to scale up.

### Gaps
- No timestamped consensus series was available, so I could not estimate how much the 3–5 h staleness inflates noise in tennis.
- The ATP main tour 2010–2018 may not represent Challengers in 2026 (fewer books, thinner markets), where noise will be larger.
- I could not verify the paper's own threshold sensitivity analysis (α = 0.04–0.06) beyond the search summary.
