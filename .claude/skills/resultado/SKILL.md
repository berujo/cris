---
name: resultado
description: Regista uma aposta ou o resultado comunicado pelo utilizador (ganhou, perdeu, nula ou cashout; stake; lucro ou prejuízo), atualiza a banca e mostra as métricas. Usar sempre que o utilizador reporta apostas ou resultados.
---

# Registar resultado

1. **Identifica a aposta:** pela referência do plano (ex.: "24/09 #2", em `planos/`) ou pela descrição. Se for ambígua, pergunta.
2. **Usa os números do utilizador** (stake, odd e lucro reais): são a verdade, mesmo que difiram do plano.
3. **Regista:**
   - Aposta nova: `python3 scripts/banca.py registar --desporto ... --competicao ... --evento ... --mercado ... --selecao ... --odd ... --stake ... [--prob ... --confianca ... --tipo simples|multipla|live --data AAAA-MM-DD] --estado ganha|perdida|nula|cashout|pendente [--lucro X] --notas "plano AAAA-MM-DD #N"`.
   - Aposta pendente já registada: `python3 scripts/banca.py resultado ID estado [--stake X --odd Y --lucro Z]`.
4. **Mostra** `python3 scripts/banca.py metricas`: banca, lucro total, ROI, yield, taxa de acerto e evolução.
5. **Commit e push** de `dados/apostas.csv`.
6. Se o stop-loss foi atingido, diz claramente que é pausa. Se houver sinais de perseguir perdas, lembra as regras com tato.

Com menos de 50 apostas as métricas são sobretudo variância; diz isso sem dramatizar ganhos nem perdas.
