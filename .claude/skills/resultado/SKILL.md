---
name: resultado
description: Regista uma aposta ou o resultado comunicado pelo utilizador (ganhou, perdeu, nula ou cashout; stake; lucro ou prejuízo), ligando-a à recomendação do plano para medir o CLV, atualiza a banca e mostra as métricas. Usar sempre que o utilizador reporta apostas ou resultados.
---

# Registar aposta ou resultado

1. **Identifica a aposta:** pela referência do plano (ex.: "25/09 #1" é `2026-09-25#1`, em `dados/recomendacoes.csv`), pelo número do alvo (ex.: "#128" em `dados/alvos.json`) ou pela descrição. Se for ambígua, pergunta.
2. **Usa os números do utilizador** (stake, odd, casa, lucro). São a verdade, mesmo que difiram do plano.
3. **Regista:**
   - **Aposta num alvo do plano, ainda sem referência:** primeiro `python3 scripts/banca.py recomendar --alvo N --odd O --casa C [--segunda-odd S]` (pergunta a melhor odd que ele viu nas outras casas: é o `--segunda-odd`). Se o código recusar, diz-lhe porquê antes de ele apostar. Depois regista a aposta com a referência que sair.
   - **Odds vistas e não apostadas** (abaixo da mínima, ou o outro lado do jogo): `recomendar --alvo N --odd O --casa C --sombra`. Mede se as quatro casas chegam à odd mínima.
   - **Aposta de uma recomendação:** `python3 scripts/banca.py registar --ref REF --odd O --stake S --casa C [--estado ganha|perdida|nula|cashout --lucro X]`.
   - **Freebet:** acrescenta `--tipo freebet` (a stake não sai da banca; se perder, perde 0).
   - **Aposta fora do plano:** `python3 scripts/banca.py registar --desporto ... --competicao ... --evento ... --mercado ... --selecao ... --odd ... --stake ... [--casa ... --estado ... --lucro ...]`. Diz ao utilizador, sem sermões, que o valor das apostas fora do plano não é medido.
   - **Resultado de uma aposta pendente:** `python3 scripts/banca.py resultado ID estado [--stake --odd --lucro]`.
4. **Se o jogo ainda não começou,** a aposta fica pendente. A verificação pré-jogo (ou `odds.py fecho`) junta-lhe depois a odd de fecho, para o CLV. Pede ao utilizador que diga sempre quando aposta, antes do jogo.
5. **Mostra** `python3 scripts/banca.py metricas`: banca, lucro, ROI, yield, taxa de acerto, CLV e evolução.
6. **Faz commit e push** de `dados/`.
7. Se o stop-loss foi atingido, diz claramente que é pausa. Se houver sinais de perseguir perdas, lembra as regras com tato.

Com menos de 50 apostas, as métricas de lucro são sobretudo variância; é o CLV que mostra se o processo funciona. Diz isso sem dramatizar ganhos nem perdas.
