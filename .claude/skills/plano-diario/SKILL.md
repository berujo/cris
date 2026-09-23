---
name: plano-diario
description: Gera ou atualiza o plano diário de apostas (futebol, ténis, NBA/WNBA, basebol) pelo método "preço primeiro" — varredura de valor contra a Pinnacle, filtro dos subagentes, regras de risco e de banca, registo das recomendações e agendamento das verificações pré-jogo. Usar quando o utilizador pede o plano do dia ou quando as Routines diárias disparam (00:00, 12:00, 18:00).
---

# Plano diário

**Data:** hoje, na hora de Lisboa, ou a data dada como argumento. Depois das 21:00 de Lisboa, o plano é do dia seguinte.

**Modo:**
- Se `planos/AAAA-MM-DD.md` ainda não existe: **plano completo**, com janela de 36 horas.
- Se já existe (atualizações das 12:00 e das 18:00, ou novo pedido): **atualização**, com janela de 12 horas. Só entram candidatas novas, numa secção "Atualização HH:MM" no fim do plano. O resto não se refaz.

Às 00:00 ainda não há onzes nem relatórios de lesões para os jogos da tarde e da noite. Nesses casos, a confiança máxima é média e é a verificação pré-jogo que decide.

1. **Estado:** `python3 scripts/banca.py estado`. Se aparecer `STOP-LOSS ATINGIDO` ou `REGRA DE PARAGEM ATIVA`, escreve um plano "PAUSA" (banca, motivo, proposta de revisão) e salta para o passo 8.
2. **Manutenção e varredura:** o subagente `estatistica-dados` trata dos resultados, do fecho, da avaliação, da varredura de valor (`odds.py valor`) e das promoções das casas do utilizador. Devolve as candidatas por desporto e o estado das fontes. Sem API, o plano é "HOJE: NÃO APOSTAR" porque falta a fonte de odds; salta para o passo 8.
3. **Filtro:** em paralelo, um analista por desporto com candidatas: `analista-futebol`, `analista-tenis`, `analista-nba`, `analista-basebol`. Cada um recebe só as candidatas do seu desporto: item, jogo, seleção, odd, casa, idade, preço justo, EV e movimento.
4. **Notícias:** `noticias-lesoes`, com as candidatas aprovadas pelos analistas.
5. **Validação:** `estatistica-dados`, com as aprovadas e os veredictos das notícias. Confirma as contas e os ajustes.
6. **Risco:** `gestao-risco` devolve as aprovadas e as rejeitadas.
7. **Banca:** `gestao-banca` regista as aprovadas com `banca.py recomendar` e devolve as referências. É o código que calcula a stake, e pode recusar.
8. **Gravar:** escreve `planos/AAAA-MM-DD.md` no formato de `CLAUDE.md` (ou acrescenta-lhe a atualização). Inclui a linha "CLV do agente", tirada do `banca.py avaliacao`. Faz commit e push de `planos/` e `dados/`.
9. **Pré-jogo:** para cada recomendação nova, agenda com `send_later` a mensagem "Pré-jogo: corre a skill pre-jogo para REF", para 40 minutos antes do início (em UTC). Se o jogo começa daqui a menos de 45 minutos, corre já a skill `pre-jogo`.
10. **Entregar:** mostra o plano, ou só a atualização, ao utilizador.
    - Se houver recomendações novas e existir a ferramenta PushNotification, envia um resumo de uma linha (ex.: "1 aposta: Arsenal @ ≥ 2,11 · 0,20 €").
    - Numa atualização sem novidades, não envies notificação e responde numa linha.

As sugestões vão para `dados/recomendacoes.csv`, para medir o agente. O `dados/apostas.csv` só recebe as apostas que o utilizador disser que fez.
