---
name: pre-jogo
description: Verificação final de uma recomendação cerca de 40 minutos antes do jogo — guarda a odd de fecho (CLV), confirma onzes, lesões e meteorologia e diz ao utilizador se mantém ou cancela. Usar quando dispara uma verificação agendada pelo plano ("Pré-jogo: ... REF") ou quando o utilizador pede para confirmar uma aposta antes do jogo.
---

# Verificação pré-jogo

Recebes uma ou mais referências (ex.: `2026-09-25#1`), de `dados/recomendacoes.csv`.

1. **Fecho:** `python3 scripts/odds.py fecho --ref REF`.
   - Com a The Odds API: guarda a probabilidade justa atual da Pinnacle (a odd de fecho) e mostra o CLV.
   - Alvos do GitHub: mostra o fecho **provisório** pela última recolha do consenso e quanto o consenso mexeu desde a recomendação. Só fica gravado depois do início (na manutenção seguinte), para apanhar uma recolha que ainda chegue.
2. **Notícias:** `noticias-lesoes` em modo pré-jogo, para esta recomendação. Mostra o que mudou desde o plano: onzes e alinhamentos, lesões de última hora, lançador, meteorologia; no ténis, sinais de desistência.
3. **Veredicto:**
   - **MANTER** se não houve notícias contra e a odd na casa do utilizador ainda é ≥ à odd mínima com o preço justo mais recente (a que o `odds.py alvos` ou o `banca.py` mostram; não a calcules à mão).
   - **CANCELAR** se houve notícias contra, se o lançador mudou (basebol), se a odd mínima já não está disponível, ou se o consenso andou mais de 2 pp contra a seleção (o `fecho` avisa com ⚠).
4. **Registo:** acrescenta ao plano do dia uma linha "Pré-jogo REF HH:MM: MANTER/CANCELAR — motivo · CLV x%". Faz commit e push.
5. **Aviso:** se existir a ferramenta PushNotification, envia uma linha (ex.: "2026-09-25#1 Arsenal: MANTER, odd mínima 2,11" ou "2026-09-25#1: CANCELAR — motivo").

Se o utilizador já apostou, não há nada a cancelar: diz só como ficou o CLV.
