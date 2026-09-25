# Memória do projeto

O que foi decidido, aprendido e deixado em aberto nas conversas com o utilizador. Serve de memória entre sessões
(e de fonte para o grafo do graphify em `graphify-out/`). As regras em vigor estão em `CLAUDE.md`; aqui fica o
porquê e a história.

## O utilizador e as decisões dele
- Fala português de Portugal. Aposta em Portugal, só em casas licenciadas: Betclic, Betano, Placard, Solverde.
- **Banca:** 20 € de início (23/09/2026). A 25/09 disse ter 25 €: a banca registada continua a 20 € — pela regra 11 não se reforça antes de 200 apostas com CLV positivo. Ficou por esclarecer se era engano ou reforço.
- **Regras que escolheu:** teto de 10% da banca por aposta; stakes por 1/4 de Kelly com teto; sem limite diário de exposição (só por aposta); pausa (stop-loss) se a banca cair 50%.
- **Tipos de aposta:** simples pré-jogo, live e múltiplas (2–3 pernas), à escolha do agente. Fontes: The Odds API mais pesquisa web (a chave nunca foi dada).
- **Entrega:** plano automático todos os dias; pediu que começasse à meia-noite (ficou às 00:30 UTC, mais atualizações às 06:30, 12:30 e 18:30 UTC).
- **Foco:** ténis agora (digressão asiática e Challengers); futebol só com as ligas europeias e a Champions, a partir de 09/10/2026; Liga das Nações de fora; NBA e basebol em pausa.
- **Pedidos permanentes:**
  - "Procura sempre jogos a que tenhas acesso por API; procura no public-apis ou na net."
  - Análise profissional completa em todas as apostas (confronto direto, forma, estatísticas, mercados secundários como vencedor, jogos, sets, handicap) — sempre sem inventar odds.
- **25/09:** "hoje só quero arriscar 5 €" — limite desse dia. Perguntou pelo Faria a ganhar 2-0. Pediu a pesquisa de melhorias e depois esta memória no graphify.
- **Por decidir:** ligar o teto de exposição de 25% da banca (= 5 € em 20 €; `teto_exposicao_pct`); a faixa de odds para usar freebets.

## Ferramentas pedidas pelo utilizador
O contentor da sessão é descartado; numa sessão nova, reinstalar:
- **graphify** (memória em grafo): `pip install graphifyy && graphify install --platform claude`.
- **caveman** (respostas curtas), a 25/09: `claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman`. Os outros pedidos da altura (ponytail, headroom, token-optimizer) ficaram por instalar.

## Arquitetura
- Orquestrador (`CLAUDE.md`) com 8 subagentes em `.claude/agents/` (4 analistas por desporto, notícias, estatística, risco e banca) e 3 skills (`plano-diario`, `pre-jogo`, `resultado`).
- Código só com biblioteca padrão: `scripts/odds.py` (preço justo, varredura, alvos do GitHub, fecho, resultados, mercados do ténis, EV de promoções), `scripts/banca.py` (stakes, validação, registos, métricas, avaliação), `scripts/tenis.py` (modelo de pontos), `scripts/backtest.py`.
- Dados: `dados/config.json` (parâmetros), `dados/recomendacoes.csv` (tudo o que o agente recomenda), `dados/apostas.csv` (só o que o utilizador diz que apostou), `dados/alvos.json` e `dados/consenso.json` (leituras da fonte do ténis).
- Rede do ambiente: só GitHub, GitLab, storage.googleapis.com e PyPI. The Odds API, ESPN, MLB Stats e as casas estão bloqueados.

## Método e porquê
- **Preço primeiro:** só se aposta quando uma casa paga acima do preço justo. O backtest mostrou que o Elo e os LLMs perdem para o mercado e que a melhor odd acima do preço justo dá lucro (`docs/backtest.md`).
- **Pesquisa de 25/09** (`reports/Melhorias do agente de apostas.md`, notas em `research_notes/`): o caminho do consenso não media o CLV; só ~56% da vantagem contra a média das casas é real; 1/4 de Kelly sobre o EV aparente levava o risco de stop-loss a ~9%. Daí: odd mínima de Kaunitz com margem por idade, stake sobre o EV calibrado, CLV pelo consenso, filtros determinísticos e o modelo dos mercados secundários (`docs/plano-melhorias.md`, Fase 7).

## Lições aprendidas
- **A fonte do ténis** (Mriganka-codes/tennis_data) chega 3 a 5 h depois do horário e só muda de dia depois da meia-noite de Praga: à noite é preciso repetir a leitura (cadeia de `send_later` até às 06:00 UTC).
- **Rótulos trocados** na fonte de futebol (aimidas1): "Away" é a equipa da casa. Atualiza de 2 em 2 dias.
- **Erros da fonte existem:** a 25/09 o Blanch aparecia em Génova horas depois de jogar em San Diego; dois agentes confirmaram o erro e o jogo saiu.
- **O analista aprovava quase tudo, dos dois lados do jogo:** agora é um lado por jogo (o código recusa o segundo) e perguntas fechadas.
- **Opinião contra modelo:** a 25/09 disse que o 2-1 do Faria era "pelo menos tão plausível" como o 2-0; o modelo dá ~41% ao 2-0 e ~24% ao 2-1. Para mercados secundários, usar sempre `odds.py mercados`.
- **Jogos a começar:** quando a fonte publica tarde, os primeiros jogos da Ásia já começaram; não entram na lista acionável.
- **Limites da sessão:** um subagente pode morrer pelo limite de uso; guardar o trabalho (commit) antes das tarefas longas.

## Histórico
- 23/09/2026: sistema criado (regras, subagentes, skills, `odds.py`, `banca.py`, backtest).
- 24/09: primeiro dia com alvos do GitHub (89 alvos de ténis), sugestão de 1 múltipla e 4 simples, análise profissional de Blanch e Prado Angelo (`planos/2026-09-24.md`).
- 25/09: fonte publicou às 03:50 UTC; 31 jogos com alvo (análise profissional completa); lista de 11 jogos dentro dos 5 € do utilizador; pesquisa de melhorias em 7 frentes e aplicação no código (`planos/2026-09-25.md`).
- Nenhuma aposta registada até 25/09: banca 20,00 €, 0 recomendações com fecho.
