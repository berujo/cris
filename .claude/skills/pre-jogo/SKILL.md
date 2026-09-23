---
name: pre-jogo
description: Verificação final de uma recomendação cerca de 40 minutos antes do jogo — guarda a odd de fecho (CLV), confirma onzes, lesões e meteorologia e diz ao utilizador se mantém ou cancela. Usar quando dispara uma verificação agendada pelo plano ("Pré-jogo: ... REF") ou quando o utilizador pede para confirmar uma aposta antes do jogo.
---

# Verificação pré-jogo

Recebes uma ou mais referências (ex.: `2026-09-25#1`), de `dados/recomendacoes.csv`.

1. **Fecho:** `python3 scripts/odds.py fecho --ref REF` guarda a probabilidade justa atual da Pinnacle (a odd de fecho) e mostra o CLV da recomendação.
2. **Notícias:** `noticias-lesoes` em modo pré-jogo, para esta recomendação. Mostra o que mudou desde o plano: onzes e alinhamentos, lesões de última hora, lançador, meteorologia.
3. **Veredicto:**
   - **MANTER** se não houve notícias contra e a odd na casa do utilizador ainda é ≥ à odd mínima. Recalcula a odd mínima com o novo preço justo: 1,03 / probabilidade justa, ou 1,05 / probabilidade sem Pinnacle.
   - **CANCELAR** se houve notícias contra, se o lançador mudou (basebol), ou se a odd mínima já não está disponível.
4. **Registo:** acrescenta ao plano do dia uma linha "Pré-jogo REF HH:MM: MANTER/CANCELAR — motivo · CLV x%". Faz commit e push.
5. **Aviso:** se existir a ferramenta PushNotification, envia uma linha (ex.: "2026-09-25#1 Arsenal: MANTER, odd mínima 2,11" ou "2026-09-25#1: CANCELAR — motivo").

Se o utilizador já apostou, não há nada a cancelar: diz só como ficou o CLV.
