---
name: plano-diario
description: Gera ou atualiza o plano diário de apostas (futebol, ténis, NBA/WNBA, basebol) pelo método "preço primeiro" — varredura de valor contra a Pinnacle, filtro dos subagentes, regras de risco e de banca, registo das recomendações e agendamento das verificações pré-jogo. Usar quando o utilizador pede o plano do dia ou quando as Routines diárias disparam (01:30, 07:30, 13:30 e 19:30 de Lisboa).
---

# Plano diário

**Data:** hoje, na hora de Lisboa, ou a data dada como argumento. Depois das 21:00 de Lisboa, o plano é do dia seguinte.

**Modo:**
- Se `planos/AAAA-MM-DD.md` ainda não existe: **plano completo**, com janela de 36 horas.
- Se já existe (atualizações das 07:30, 13:30 e 19:30, ou novo pedido): **atualização**, com janela de 12 horas. Só entram candidatas novas, numa secção "Atualização HH:MM" no fim do plano. O resto não se refaz.

**Desportos:** só entram os ativos em `desportos` no `config.json` (ver "Foco atual" em `CLAUDE.md`). Os comandos `odds.py valor` e `alvos` já filtram por eles.

À 01:30 ainda não há onzes nem relatórios de lesões para os jogos da tarde e da noite. Nesses casos, a confiança máxima é média e é a verificação pré-jogo que decide.

1. **Estado:** `python3 scripts/banca.py estado`. Se aparecer `STOP-LOSS ATINGIDO` ou `REGRA DE PARAGEM ATIVA`, escreve um plano "PAUSA" (banca, motivo, proposta de revisão) e salta para o passo 8.
2. **Fontes, manutenção e varredura:** o subagente `estatistica-dados` corre primeiro `odds.py fontes` e depois:
   - **Manutenção, sempre:** `odds.py resultados`, `odds.py fecho` (grava o fecho do consenso dos jogos que já começaram) e `banca.py avaliacao`.
   - **Com a The Odds API:** varredura de valor (`odds.py valor`) e promoções das casas do utilizador. Devolve as candidatas por desporto.
   - **Sem ela:** `odds.py alvos`, com as fontes do GitHub. Os alvos entram no plano, na secção "Alvos para as tuas casas", depois de passarem pelos analistas e pelas notícias (passos 3 a 6).
     - Um lado por jogo. Dá prioridade aos torneios principais e ao desporto de que o utilizador falou; os jogos com ⚠ (movimento para o azarão) só entram com notícia que o explique.
     - Mostra a odd mínima como o `alvos` a dá, incluindo a que vale depois de a recolha ficar velha ("≥ 1,83 (1,87 depois das 20:44)").
     - Alvos com "stake 0 (0,10 € a partir de X)": diz ao utilizador a odd X a partir da qual vale a pena; abaixo dela é só registo.
     - Jogos que começam antes de o plano chegar ao utilizador (menos de ~45 min) não entram na lista acionável.
   - **Se o ténis ainda vier com a data de ontem:** a fonte está agendada para as 00:00 UTC, mas costuma chegar 3 a 5 horas depois. Agenda com `send_later` uma nova leitura para as 02:30 UTC, com a mensagem "Alvos de ténis: corre odds.py alvos --desporto tenis e acrescenta-os ao plano de hoje". Essa leitura repete-se de hora a hora até às 06:00 UTC.
   - **Sem nenhuma fonte:** o plano é "HOJE: NÃO APOSTAR" e explica que falta a fonte de odds; salta para o passo 8.
3. **Filtro:** em paralelo, um analista por desporto ativo com candidatas: `analista-futebol`, `analista-tenis`, `analista-nba`, `analista-basebol`. Cada um recebe só as candidatas do seu desporto: item, jogo, seleção, odd, casa, idade, preço justo, EV e movimento.
4. **Notícias:** `noticias-lesoes`, com as candidatas aprovadas pelos analistas.
5. **Validação:** `estatistica-dados`, com as aprovadas e os veredictos das notícias. Confirma as contas e os ajustes.
6. **Risco:** `gestao-risco` devolve as aprovadas e as rejeitadas.
7. **Banca:** `gestao-banca` regista as aprovadas com `banca.py recomendar` e devolve as referências. É o código que calcula a stake, e pode recusar.
   Os alvos do GitHub só se registam quando o utilizador disser a odd e a casa onde a encontrou (`banca.py recomendar --alvo N --odd O --casa C [--segunda-odd S]`); as odds que ele viu abaixo da mínima registam-se com `--sombra`.
   Se o utilizador fixou um limite para o dia (ex.: "hoje só 5 €"), a soma das stakes do plano respeita-o.
8. **Gravar:** escreve `planos/AAAA-MM-DD.md` no formato de `CLAUDE.md` (ou acrescenta-lhe a atualização). Inclui a linha "CLV do agente", tirada do `banca.py avaliacao`. Faz commit e push de `planos/` e `dados/`.
9. **Pré-jogo:** para cada recomendação nova, agenda com `send_later` a mensagem "Pré-jogo: corre a skill pre-jogo para REF", para 40 minutos antes do início (em UTC). Se o jogo começa daqui a menos de 45 minutos, corre já a skill `pre-jogo`.
10. **Entregar:** mostra o plano, ou só a atualização, ao utilizador.
    - Se houver recomendações novas e existir a ferramenta PushNotification, envia um resumo de uma linha (ex.: "1 aposta: Arsenal @ ≥ 2,11 · 0,20 €").
    - Numa atualização sem novidades, não envies notificação e responde numa linha.

As sugestões vão para `dados/recomendacoes.csv`, para medir o agente. O `dados/apostas.csv` só recebe as apostas que o utilizador disser que fez.
