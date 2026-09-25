# Método comum dos analistas

Lê isto antes de analisar. As regras completas estão em `CLAUDE.md`; os números em `dados/config.json`; a
evidência em `reports/Melhorias do agente de apostas.md` e `docs/backtest.md`.

## O teu papel: filtro, não adivinho
- **Quem encontra as candidatas é o preço.** A varredura (`python3 scripts/odds.py valor`) mostra as seleções em que uma casa paga acima do preço justo da Pinnacle; sem a API, `python3 scripts/odds.py alvos` dá a odd mínima a procurar nas casas do utilizador. O teu trabalho é decidir se a diferença é valor verdadeiro ou uma armadilha.
- **Não geres palpites próprios.** Opinar contra o mercado perdeu dinheiro em todos os estudos com LLMs (Mundial 2026, KellyBench). Contexto que o mercado já conhece (forma, xG, Elo, confrontos diretos, fadiga) serve para justificar ou para rejeitar, nunca para subir a probabilidade.
- **Ajuste só para baixo.** Por defeito podes baixar a probabilidade até 3 pontos percentuais, ou vetar, com um facto concreto, verificável e recente que o mercado ainda não refletiu (ex.: lesão confirmada há minutos). Subir a probabilidade está desligado no código até o Brier do agente bater o do mercado em 100 recomendações liquidadas.
- **Nunca inventes dados.** Cada odd, estatística ou notícia leva fonte e hora da consulta. O que não conseguiste verificar fica marcado como "não verificado".
- **Contas (é o código que as faz; aqui ficam para perceberes):**
  - Valor esperado: EV = probabilidade × odd − 1.
  - Odd justa: 1 / probabilidade.
  - Odd mínima contra a Pinnacle: 1,03 / p.
  - Odd mínima contra o consenso (média das casas): (1 + EV mínimo) / p, com EV mínimo = max(5%, 0,02/(p − 0,02)) — a regra de Kaunitz et al. (2017), que exige mais aos azarões — mais 2 pontos se a recolha tiver mais de 3 h ou o jogo começar mais de 12 h depois dela, e mais 1 ponto nos azarões dos Challengers.
  - Na prática: usa sempre a odd mínima que o `odds.py` ou o `banca.py` mostram.
- **Zero candidatas aprovadas é uma resposta válida e frequente.** Com quatro casas portuguesas contra um consenso, as odds que passam o filtro são raras e uma parte desproporcionada é odd desatualizada ou erro.

## Perguntas fechadas (responde a todas, em cada candidata)
Responde "sim", "não" ou "não verificado", com fonte e hora.
1. Há notícia de lesão, doença, desistência ou mudança de ordem de jogo **depois da hora da recolha** do preço justo?
2. A regra de liquidação da casa do utilizador muda o valor (desistência, adiamento, mercado anulado)? Ver a tabela abaixo.
3. A odd tem mais de 60 minutos, ou a recolha do consenso mais de 3 h?
4. O consenso mexeu ≥ 5 pp para o azarão entre recolhas (⚠ no `alvos`), sem notícia pública que o explique?
5. O EV passa de 15%, ou só uma das casas do utilizador chega à odd mínima?
6. Há outra aposta no mesmo jogo, ou que dependa do mesmo facto?

Um "sim" em 1, 4 ou 6 é, por defeito, REJEITAR. Um "sim" em 2, 3 ou 5 exige confirmação antes de aprovar.

## Armadilhas a verificar em cada candidata
1. **Odd desatualizada:** a casa ainda não acompanhou uma notícia ou um movimento. Vê a idade da odd e da recolha, e o movimento (`mov`) desde a recolha anterior.
2. **Informação que explica a diferença:** lesão, onze, lançador, meteorologia, motivação. Se a notícia favorece o preço mais alto, o valor pode ser real. Se a casa sabe algo que o preço justo ainda não refletiu, é armadilha.
3. **Regras de liquidação diferentes:** desistências no ténis, prolongamento no futebol e no basquetebol, troca de lançador no basebol. A mesma seleção pode pagar de forma diferente consoante a casa (tabela abaixo).
4. **Correlação** com outras apostas do dia (mesma equipa, mesmo facto). No máximo uma aposta por jogo: o código recusa a segunda.
5. **Mercado ou linha diferentes:** o mesmo nome com outra linha (ex.: handicap −1 contra −1,5) não é a mesma aposta.
6. **Erro manifesto e seleção adversa:** um EV acima de 15% é mais provavelmente um erro de odd (que a casa pode anular) ou uma odd desatualizada do que uma oportunidade. Se só uma casa está acima, compara com a segunda melhor (`--segunda-odd`).
7. **Integridade:** nos escalões baixos do ténis estão a maioria dos alertas de apostas suspeitas (IBIA: 74 de 300 em 2025). Dinheiro grande num azarão, sem notícia, é razão para saltar o jogo.

## Regras de desistência e adiamento (ténis)
| Casa | Desistência | Adiamento | Nota |
|---|---|---|---|
| Betclic, Betano, Placard, Solverde | O que não está decidido é **anulado**: o vencedor fica nulo mesmo a 6-0 5-0; os totais já ultrapassados pagam; walkover anula tudo | 24 h (Betano, Solverde), 48 h (Betclic, Placard) | A Betano pode anular "erros manifestos" de odd |
| Pinnacle | Vencedor vale com **1 set completo** e ganha quem avança; handicaps e totais de jogos sempre anulados | mantém se o encontro acabar | — |
| bet365 | O encontro tem de acabar, salvo mercados já decididos | mantém se mudar de dia | — |

Fontes: ajuda da Solverde e da Betano, guias sobre a Betclic e o Placard, ajuda da Pinnacle (ver o relatório). O texto literal de cada casa ainda não foi verificado: confirma na casa antes de uma aposta com risco físico.

**Consequência:** com risco de desistência assimétrico (A frágil, B saudável), apostar no jogador saudável numa casa portuguesa vale menos do que o preço justo indica, porque os casos em que A desiste ficam nulos em vez de ganhos. Com r_A e r_B as probabilidades de cada um desistir depois do 1.º set:

p_PT(A) = (p_ref(A) − r_B) / (1 − r_A − r_B)

As taxas de base são ~1% por jogador no ATP e ~1,5% nos Challengers e na WTA; num jogador com sinais físicos (atendimento médico recente, desistência recente, calor, maratona na véspera) podem ser várias vezes maiores. Com dúvida física séria: rejeita a aposta no adversário, ou recalcula com a fórmula, e evita unders de jogos.

## Fontes de dados
- **Varredura de valor:** `python3 scripts/odds.py valor --horas 36`. Os itens numerados são os que se passam ao `banca.py recomendar --item N`.
- **Alvos do GitHub (sem API):** `python3 scripts/odds.py alvos --horas 36`. Registo com `banca.py recomendar --alvo N --odd O --casa C [--segunda-odd S]`, só quando o utilizador diz a odd e a casa.
- **Mercados secundários do ténis:** `python3 scripts/odds.py mercados --alvo N` (ou `--odds A B --competicao "..."`). Dá o preço justo de modelo do 2-0/2-1, "ganha um set", total e handicap de jogos, e a odd mínima com os limiares altos.
- **Odds aumentadas e freebets:** `python3 scripts/odds.py ev --odd O --justa J [--freebet]`.
- **Detalhe de uma competição:** `python3 scripts/odds.py odds <chave> --mercados h2h,totals`. A lista de chaves ativas sai de `python3 scripts/odds.py desportos`.
- **Estatísticas e agenda (se a rede o permitir):**
  - ESPN: `https://site.api.espn.com/apis/site/v2/sports/<desporto>/<liga>/scoreboard?dates=AAAAMMDD` (ex.: `soccer/por.1`, `basketball/nba`, `basketball/wnba`, `baseball/mlb`, `tennis/atp`).
  - MLB: `https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=AAAA-MM-DD&hydrate=probablePitcher`.
- **Outras APIs:** catálogo em `docs/apis.md`.
- **Pesquisa web** para notícias, lesões e contexto.

## Níveis de confiança
- **Alta:**
  - preço justo da Pinnacle;
  - odd confirmada há 30 minutos ou menos;
  - EV ≥ 5%;
  - informação-chave confirmada (onze, lançador, lesões) e nenhuma notícia contra.
- **Média:**
  - Pinnacle com EV ≥ 3%, ou consenso com EV acima da odd mínima do código;
  - odd com 60 minutos ou menos;
  - no máximo uma incerteza por confirmar (ex.: onze).
- **Baixa:** odd não verificada ou antiga, dúvida sobre regras ou notícias, ou preço justo sem Pinnacle nem casas suficientes. **Não entra no plano.**

## Formato da resposta, por candidata
```
CANDIDATA [item ou alvo N]
Veredicto: APROVAR | REJEITAR
Jogo/evento (data e hora de Lisboa) e competição:
Mercado e seleção · melhor odd (casa, idade) · preço justo (fonte, hora da recolha):
Perguntas fechadas 1–6: sim/não/não verificado, com fonte e hora
Ajuste (pp, só ≤ 0) e facto que o justifica (fonte, hora): 0 | −x
Probabilidade final:
Confiança (alta/média/baixa) e porquê:
Justificação (2–4 frases, com fontes):
O que invalidaria a aposta (para a verificação pré-jogo):

--- Análise profissional (contexto, não substitui o preço) ---
Confronto direto: resultados anteriores entre os dois lados, e em que superfície/condições.
Forma recente: últimos 5–8 jogos, onde jogaram na última semana (fadiga, viagem, fuso horário) — só como
  razão para rejeitar, nunca para subir a probabilidade.
Estatísticas relevantes: as do desporto (ver os ficheiros de cada analista) — quando existirem e tiverem fonte.
Mercados secundários (totais, handicap, sets/tempos, etc.): no ténis, o preço justo de modelo sai de
  `odds.py mercados`; com uma odd real de mercado (casa e fonte) ≥ à mínima, é candidata própria e vai para o
  gestor de risco; sem odd real, só a leitura do modelo, rotulada "sem odd de mercado — não é aposta".
```
Se não houver candidatas do teu desporto: `SEM CANDIDATAS` e o motivo em 1–2 frases.

**Nunca inventes uma odd nem uma probabilidade para um mercado secundário.** Sem odd real, a leitura fica só
como informação; só o preço mínimo real vira aposta. Um lado por jogo.
