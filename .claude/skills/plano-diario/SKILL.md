---
name: plano-diario
description: Gera o plano diário de apostas (futebol, ténis, NBA/WNBA, basebol) com os subagentes especializados, aplica as regras de risco e banca e grava o plano em planos/. Usar quando o utilizador pede o plano do dia ou quando a Routine diária dispara.
---

# Plano diário

Data: hoje, na hora de Lisboa, ou a data dada como argumento. Depois das 21:00 de Lisboa, faz o plano para o dia seguinte.

- A Routine corre às 00:00 de Lisboa (23:00 no horário de inverno, que pela regra acima dá o plano do dia seguinte), para cobrir os jogos da madrugada (ex.: ténis na Ásia).
- A essa hora ainda não há onzes nem relatórios de lesões para os jogos da tarde e da noite: nesses casos a confiança máxima é média, e o plano diz o que confirmar antes do jogo.
- Se `planos/AAAA-MM-DD.md` já existir, não refaças tudo: verifica notícias e odds das apostas do plano (`noticias-lesoes` e `estatistica-dados`), atualiza ou cancela as que mudaram e acrescenta uma secção "Atualização HH:MM".

1. **Banca:** `python3 scripts/banca.py estado`. Se aparecer `STOP-LOSS ATINGIDO`, escreve um plano "PAUSA" (banca, motivo, proposta de revisão) e salta para o passo 8.
2. **Mapa do dia:** subagente `estatistica-dados`, que devolve os eventos das próximas 36 h por desporto e o estado das fontes (API e rede).
3. **Análise:** em paralelo, um subagente por desporto com jogos: `analista-futebol`, `analista-tenis`, `analista-nba`, `analista-basebol`. Passa a cada um a data, a parte do mapa do seu desporto e as fontes disponíveis.
4. **Notícias:** `noticias-lesoes` com todas as candidatas.
5. **Validação:** `estatistica-dados` com as candidatas e os veredictos das notícias.
6. **Risco:** `gestao-risco` com tudo, que devolve as aprovadas e as rejeitadas.
7. **Stakes:** `gestao-banca` calcula as stakes das aprovadas com `banca.py`.
8. **Gravar:** escreve `planos/AAAA-MM-DD.md` no formato de `CLAUDE.md`; faz commit e push.
9. **Entregar:** mostra o plano ao utilizador. Se a ferramenta PushNotification existir, envia um resumo de uma linha (ex.: "2 apostas, 1,10 € em jogo" ou "Hoje: não apostar").

Não registes as sugestões em `dados/apostas.csv`: só entram quando o utilizador disser que apostou.
