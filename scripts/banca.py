#!/usr/bin/env python3
"""Banca, registo de apostas e de recomendações, CLV e métricas. Só biblioteca padrão.

  python3 scripts/banca.py estado
  python3 scripts/banca.py stake --prob 0.55 --odd 2.10 [--multipla]
  python3 scripts/banca.py recomendar --item 3 --prob-final 0.47 --confianca média    # item de 'odds.py valor'
  python3 scripts/banca.py recomendar --alvo 5 --odd 1.98 --casa Betano --confianca média  # alvo de 'odds.py alvos'
  python3 scripts/banca.py recomendar --desporto Ténis --competicao "ATP Tóquio" --evento "A vs B" \
      --mercado h2h --selecao A --odd 2.10 --casa Betano --prob-justa 0.45 --fonte-justa pinnacle \
      --prob-final 0.46 --confianca média
  python3 scripts/banca.py registar --ref 2026-09-25#1 --odd 2.12 --stake 0.30 --casa Betano [--estado ganha]
  python3 scripts/banca.py registar --desporto Futebol --competicao "Liga Portugal" --evento "Benfica vs Porto" \
      --mercado 1X2 --selecao Benfica --odd 2.10 --stake 0.70 [--estado perdida --lucro -0.70 --data 2026-09-24]
  python3 scripts/banca.py resultado ID ganha|perdida|nula|cashout [--stake X --odd Y --lucro Z]
  python3 scripts/banca.py metricas     # as tuas apostas: lucro, ROI, yield, acerto, CLV, evolução
  python3 scripts/banca.py avaliacao    # o agente: CLV das recomendações, calibração, regra de paragem
"""
import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DADOS = Path(__file__).resolve().parent.parent / "dados"
CAMPOS = ["id", "data", "desporto", "competicao", "evento", "mercado", "selecao", "tipo", "odd", "prob",
          "confianca", "stake", "estado", "lucro", "casa", "ref", "prob_fecho", "notas"]
REC = ["ref", "data", "desporto", "competicao", "evento", "sport_key", "evento_id", "inicio", "mercado",
       "selecao", "ponto", "tipo", "odd", "casa", "prob_justa", "fonte_justa", "prob_final", "confianca",
       "stake", "prob_fecho", "resultado", "notas", "hora", "recolha", "odd_minima", "fecho_fonte",
       "fecho_antecedencia_h"]
ESTADOS = ["pendente", "ganha", "perdida", "nula", "cashout"]
DESPORTOS = {"soccer": "Futebol", "tennis": "Ténis", "basketball": "Basquetebol", "baseball": "Basebol"}
MERCADOS = {"h2h": "Vencedor/1X2", "totals": "Totais", "spreads": "Handicap"}


def eur(x, sinal=False):
    return f"{x:{'+' if sinal else ''}.2f} €".replace(".", ",")


def pct(x, sinal=False):
    return f"{x * 100:{'+' if sinal else ''}.1f}%".replace(".", ",")


def hoje():
    return datetime.now(ZoneInfo("Europe/Lisbon")).date().isoformat()


def config():
    return json.loads((DADOS / "config.json").read_text())


def ler(nome):
    ficheiro = DADOS / nome
    if not ficheiro.exists():
        return []
    with ficheiro.open(newline="") as f:
        return list(csv.DictReader(f))


def escrever(nome, linhas, campos):
    with (DADOS / nome).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def carregar():
    return config(), ler("apostas.csv")


def gravar(apostas):
    escrever("apostas.csv", apostas, CAMPOS)


def liquidadas(apostas):
    return sorted((a for a in apostas if a["estado"] != "pendente"),
                  key=lambda a: (a["data"], int(a["id"])))


def banca(cfg, apostas):
    return cfg["banca_inicial"] + sum(float(a["lucro"]) for a in liquidadas(apostas))


def limite_stop_loss(cfg):
    return cfg["banca_inicial"] * (1 - cfg["stop_loss_pct"] / 100)


def ativo(cfg, desporto, dia=None):
    """Se o desporto está no foco: 'desportos' em config.json dá a data a partir da qual entra (null = pausa)."""
    inicio = cfg.get("desportos", {}).get(desporto, "2000-01-01")
    return inicio is not None and (dia or hoje()) >= inicio


def ev_minimo(cfg, fonte, prob=None, competicao="", idade_h=None, mercado="h2h", selecao="", antecedencia_h=None):
    """EV mínimo (fração) para uma seleção. Ver 'Filtros' em CLAUDE.md.

    - Pinnacle: ev_minimo_pct.
    - Consenso (média das casas): o maior entre ev_minimo_consenso_pct e α/(p − α), a regra de Kaunitz et al.
      (2017) — exige mais aos azarões, onde o consenso erra mais (viés favorito–azarão).
    - Modelo (mercados secundários do ténis): ev_secundarios_pct; o 2-1 e o 1-2 exigem mais.
    - Recolha do preço justo velha (> recolha_velha_h) ou longe do início (> recolha_longe_h): + recolha_extra_pct.
    - Competição com uma palavra de ev_extra_pct (ex.: itf) ou, nos azarões, de ev_extra_azarao_pct
      (ex.: challenger): + esse valor.
    """
    if fonte == "modelo":
        chave = "sets_3" if mercado == "sets" and re.search(r"2-1|1-2", selecao) else mercado
        base = cfg.get("ev_secundarios_pct", {}).get(chave, 8) / 100
    elif fonte == "pinnacle":
        base = cfg["ev_minimo_pct"] / 100
    else:
        base = cfg["ev_minimo_consenso_pct"] / 100
        alfa = cfg.get("consenso_alpha", 0)
        if alfa and prob:
            base = max(base, alfa / (prob - alfa) if prob > alfa else math.inf)
    velha = idade_h is not None and idade_h > cfg.get("recolha_velha_h", math.inf)
    longe = antecedencia_h is not None and antecedencia_h > cfg.get("recolha_longe_h", math.inf)
    if velha or longe:
        base += cfg.get("recolha_extra_pct", 0) / 100
    extras = list(cfg.get("ev_extra_pct", {}).items())
    if prob is not None and prob < 0.5:
        extras += list(cfg.get("ev_extra_azarao_pct", {}).items())
    for palavra, extra in extras:
        if re.search(palavra, competicao or "", re.I):
            base += extra / 100
    return base


def data_utc(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def idade_horas(recolha, agora=None):
    """Horas desde a recolha do preço justo (ISO em UTC), ou None se não se souber."""
    if not recolha:
        return None
    return ((agora or datetime.now(timezone.utc)) - data_utc(recolha)).total_seconds() / 3600


def minimo_de(cfg, r, agora=None):
    """EV mínimo de uma recomendação (linha de recomendacoes.csv)."""
    recolha, antecedencia = r.get("recolha"), None
    if recolha and r.get("inicio"):
        antecedencia = (data_utc(r["inicio"]) - data_utc(recolha)).total_seconds() / 3600
    return ev_minimo(cfg, r["fonte_justa"], float(r["prob_justa"]), r.get("competicao", ""),
                     idade_horas(recolha, agora), r.get("mercado", "h2h"), r.get("selecao", ""), antecedencia)


def clv(odd, prob_fecho):
    """Valor da odd apostada face à probabilidade justa no fecho."""
    return float(odd) * float(prob_fecho) - 1


def reais(recs):
    """Recomendações que contam para o CLV e para a regra de paragem (sem os registos-sombra)."""
    return [r for r in recs if r.get("tipo") != "sombra"]


def regra_paragem(cfg, recs):
    """Verdadeira se o CLV médio for ≤ 0 ao fim da amostra mínima de recomendações com fecho."""
    valores = [clv(r["odd"], r["prob_fecho"]) for r in reais(recs) if r["prob_fecho"]]
    return len(valores) >= cfg["clv_minimo_amostra"] and sum(valores) / len(valores) <= 0


def arredondar(cfg, euros):
    """Arredonda para baixo ao passo de config; abaixo da stake mínima, 0."""
    passo = round(cfg["arredondamento"] * 100)
    cents = math.floor(euros * 100 + 1e-6)
    euros = (cents - cents % passo) / 100
    return euros if euros >= cfg["stake_minima"] else 0.0


def grupo_fonte(fonte):
    return fonte if fonte in ("pinnacle", "modelo") else "consenso"


def calibracao(cfg, fonte, recs):
    """(k, a, n): a stake usa o EV calibrado EV_cal = a + k·EV_aparente, não o EV aparente.

    Escolher a maior diferença de preço sobrestima o EV (maldição do otimizador; Smith & Winkler 2006), e
    encolher a aposta melhora o Kelly fora da amostra (Baker & McHale 2013). Sem dados usa-se o prior k_prior da
    fonte; com n recomendações com fecho da mesma fonte, mistura-se com a regressão do CLV sobre o EV aparente,
    com peso w = n/(n + n_prior)."""
    cal = cfg.get("calibracao_ev")
    if not cal:
        return 1.0, 0.0, 0
    grupo = grupo_fonte(fonte)
    k0 = cal.get("k_prior", {}).get(grupo, 0.5)
    pontos = [(float(r["odd"]) * float(r["prob_justa"]) - 1, clv(r["odd"], r["prob_fecho"]))
              for r in reais(recs) if r.get("prob_fecho") and grupo_fonte(r["fonte_justa"]) == grupo]
    n = len(pontos)
    if n < 3:
        return k0, 0.0, n
    mx, my = sum(x for x, _ in pontos) / n, sum(y for _, y in pontos) / n
    var = sum((x - mx) ** 2 for x, _ in pontos)
    if var <= 0:
        return k0, 0.0, n
    k_hat = sum((x - mx) * (y - my) for x, y in pontos) / var
    w = n / (n + cal.get("n_prior", 50))
    return min(max(w * k_hat + (1 - w) * k0, 0.0), 1.0), w * (my - k_hat * mx), n


def calcular_stake(cfg, banca_atual, prob, odd, multipla=False, calib=(1.0, 0.0)):
    """Kelly fracionado sobre o EV calibrado, com teto, arredondado para baixo. Devolve (euros, ev aparente)."""
    ev = prob * odd - 1
    ev_cal = calib[1] + calib[0] * ev
    teto = cfg["teto_multipla_pct" if multipla else "teto_stake_pct"] / 100
    fracao = max(0.0, min(cfg["fracao_kelly"] * ev_cal / (odd - 1), teto))
    return arredondar(cfg, banca_atual * fracao), ev


def em_jogo(apostas, recs, agora=None):
    """Euros em jogo: apostas pendentes mais recomendações por liquidar que ainda não foram apostadas."""
    agora = agora or datetime.now(timezone.utc)
    apostadas = {a.get("ref") for a in apostas if a.get("ref")}
    total = sum(float(a["stake"]) for a in apostas if a["estado"] == "pendente")
    for r in recs:
        if r["resultado"] or r["ref"] in apostadas or not r["stake"] or not r["inicio"]:
            continue
        if (agora - datetime.fromisoformat(r["inicio"].replace("Z", "+00:00"))).total_seconds() < 12 * 3600:
            total += float(r["stake"])
    return total


def ajuste_positivo_permitido(cfg, recs):
    """Os subagentes só podem subir a probabilidade se ajuste_positivo estiver ligado ou se, em pelo menos 100
    recomendações liquidadas, as probabilidades deles tiverem Brier melhor do que o preço justo."""
    decididas = [r for r in reais(recs) if r["resultado"] in ("ganha", "perdida")]
    return bool(cfg.get("ajuste_positivo")) or (
        len(decididas) >= 100 and brier(decididas, "prob_final") < brier(decididas, "prob_justa"))


def validar(cfg, banca_atual, r, agora=None, confirmado=False, segunda_odd=None, exposicao=0.0, calib=(1.0, 0.0),
            ajuste_positivo=True):
    """Aplica as regras a uma recomendação. Devolve (stake, motivo da recusa ou None); a stake pode ser 0 (tem valor
    mas fica abaixo da stake mínima ou do teto de exposição: regista-se para medir o CLV, não se aposta).

    segunda_odd: a melhor odd da mesma seleção nas outras casas. Se só uma casa passa o mínimo, pode ser um erro
    de odd ou uma odd desatualizada (seleção adversa): exige-se o dobro do EV mínimo e confirmação.
    exposicao: euros já em jogo, para o teto de exposição (teto_exposicao_pct; null = sem teto).
    calib: (k, a) de calibracao(). ajuste_positivo: se o agente pode subir a probabilidade.
    """
    odd, justa, final = float(r["odd"]), float(r["prob_justa"]), float(r["prob_final"])
    multipla, minimo = r["tipo"] == "multipla", minimo_de(cfg, r, agora)
    if abs(final - justa) * 100 > cfg["ajuste_max_pp"] + 1e-9:
        ajuste = f"{(final - justa) * 100:+.1f}".replace(".", ",")
        return 0.0, f"ajuste de {ajuste} pp acima do máximo de {cfg['ajuste_max_pp']} pp"
    if final > justa + 1e-9 and not ajuste_positivo:
        return 0.0, ("ajuste positivo desligado: os subagentes só podem baixar a probabilidade ou vetar, até terem "
                     "Brier melhor do que o mercado em 100 recomendações liquidadas")
    if not multipla and not cfg["odd_minima"] <= odd <= cfg["odd_maxima"]:
        return 0.0, f"odd {odd:.2f} fora do intervalo {cfg['odd_minima']:.2f}–{cfg['odd_maxima']:.2f}"
    ev = odd * final - 1
    if ev < minimo:
        return 0.0, f"EV {pct(ev, True)} abaixo do mínimo de {pct(minimo)}"
    suspeito = cfg.get("ev_suspeito_pct")
    if suspeito is not None and ev * 100 > suspeito and not confirmado:
        return 0.0, (f"EV {pct(ev, True)} acima de {suspeito}% é suspeito (odd errada, desatualizada ou notícia "
                     "que o consenso ainda não tem) — confirma a odd e as notícias e repete com --confirmado")
    if segunda_odd is not None and segunda_odd * final - 1 < minimo:
        if ev < 2 * minimo:
            return 0.0, (f"só esta casa passa o mínimo (a 2.ª melhor, {segunda_odd:.2f}, não chega) e o EV não "
                         f"chega ao dobro do mínimo ({pct(2 * minimo)})")
        if not confirmado:
            return 0.0, "só esta casa passa o mínimo: confirma a odd e repete com --confirmado"
    stake, _ = calcular_stake(cfg, banca_atual, final, odd, multipla, calib)
    teto = cfg.get("teto_exposicao_pct")
    if stake and teto is not None:
        stake = arredondar(cfg, min(stake, banca_atual * teto / 100 - exposicao))
    return stake, None


def liquidar(a, estado, lucro):
    """Lucro de uma aposta. Numa freebet a stake não é do utilizador: ganha só o lucro, perde 0."""
    if estado == "cashout" and lucro is None:
        sys.exit("cashout exige --lucro")
    if lucro is None and estado != "pendente":
        stake, odd = float(a["stake"]), float(a["odd"])
        perda = 0.0 if a.get("tipo") == "freebet" else -stake
        lucro = {"ganha": stake * (odd - 1), "perdida": perda, "nula": 0.0}[estado]
    a["estado"] = estado
    a["lucro"] = "" if estado == "pendente" else f"{lucro:.2f}"


def mostrar(cfg, apostas, a):
    lucro = "" if a["estado"] == "pendente" else f", lucro {eur(float(a['lucro']), True)}"
    print(f"#{a['id']} {a['evento']} — {a['selecao']} @ {a['odd']}, stake {eur(float(a['stake']))}: "
          f"{a['estado']}{lucro}")
    print(f"Banca atual: {eur(banca(cfg, apostas))}")


def cmd_estado(cfg, apostas, _):
    b, limite = banca(cfg, apostas), limite_stop_loss(cfg)
    pendentes = [a for a in apostas if a["estado"] == "pendente"]
    print(f"Banca atual: {eur(b)} (inicial {eur(cfg['banca_inicial'])}, "
          f"lucro {eur(b - cfg['banca_inicial'], True)})")
    print(f"Pendentes: {len(pendentes)} aposta(s), "
          f"{eur(sum(float(a['stake']) for a in pendentes))} em jogo")
    teto = cfg.get("teto_exposicao_pct")
    if teto is not None:
        print(f"Em jogo com recomendações abertas: {eur(em_jogo(apostas, ler('recomendacoes.csv')))} "
              f"(teto de exposição: {eur(b * teto / 100)}, {teto}% da banca)")
    if b <= limite:
        print(f"STOP-LOSS ATINGIDO: banca ≤ {eur(limite)}. Pausa — não sugerir apostas.")
    else:
        print(f"Stop-loss: pausa se a banca chegar a {eur(limite)}")
    if regra_paragem(cfg, ler("recomendacoes.csv")):
        print(f"REGRA DE PARAGEM ATIVA: CLV médio ≤ 0 ao fim de {cfg['clv_minimo_amostra']} recomendações "
              "com fecho. Não recomendar; rever o método.")


def cmd_stake(cfg, apostas, args):
    b = banca(cfg, apostas)
    if b <= limite_stop_loss(cfg):
        sys.exit("STOP-LOSS ATINGIDO: não apostar.")
    k, a, n = calibracao(cfg, args.fonte, ler("recomendacoes.csv"))
    euros, ev = calcular_stake(cfg, b, args.prob, args.odd, args.multipla, (k, a))
    calibrado = f"calibrado {pct(a + k * ev, True)} (k {k:.2f}, {n} com fecho)".replace(".", ",", 1)
    if ev <= 0:
        print(f"Sem valor (EV {pct(ev, True)}): não apostar.")
    elif not euros:
        print(f"EV {pct(ev, True)}, {calibrado}, mas a stake fica abaixo do mínimo: não apostar.")
    else:
        print(f"Stake: {eur(euros)} ({pct(euros / b)} da banca de {eur(b)}) | EV {pct(ev, True)}, {calibrado} | "
              f"odd justa {1 / args.prob:.2f}")


def cmd_recomendar(cfg, apostas, args):
    recs, b = ler("recomendacoes.csv"), banca(cfg, apostas)
    if b <= limite_stop_loss(cfg):
        sys.exit("STOP-LOSS ATINGIDO: não recomendar.")
    if regra_paragem(cfg, recs):
        sys.exit("REGRA DE PARAGEM ATIVA: não recomendar; rever o método.")
    r = {c: "" for c in REC}
    for opcao, ficheiro in (("item", "varredura.json"), ("alvo", "alvos.json")):
        numero = getattr(args, opcao, None)
        if not numero:
            continue
        s = next((x for x in json.loads((DADOS / ficheiro).read_text())["itens"] if x["id"] == numero), None)
        if not s:
            sys.exit(f"O {opcao} {numero} não existe em {ficheiro}")
        r.update(competicao=s["competicao"], evento=s["evento"], inicio=s["inicio"], mercado=s["mercado"],
                 selecao=s["selecao"], ponto="" if s["ponto"] is None else s["ponto"],
                 prob_justa=f"{s['justa']:.4f}", fonte_justa=s["fonte"], recolha=s.get("recolha", ""))
        if opcao == "item":
            r.update(desporto=DESPORTOS.get(s["sport_key"].split("_")[0], ""), sport_key=s["sport_key"],
                     evento_id=s["evento_id"], odd=s["melhor"], casa=s["casa"])
        elif args.odd is None or not args.casa:
            sys.exit("Com --alvo, indica a odd e a casa onde a encontraste (--odd e --casa).")
        else:
            r.update(desporto=s["desporto"], sport_key="github")
    r.update({k: str(v) for k, v in vars(args).items() if k in REC and v is not None})
    r["prob_final"] = r["prob_final"] or r["prob_justa"]  # por defeito, sem ajuste ao preço justo
    for campo in ("evento", "selecao", "odd", "prob_justa"):
        if not r[campo]:
            sys.exit(f"Falta --{campo.replace('_', '-')} (ou usa --item ou --alvo)")
    agora = datetime.now(timezone.utc)
    r["data"], r["hora"] = r["data"] or hoje(), agora.strftime("%Y-%m-%dT%H:%M:%SZ")
    r["tipo"] = "sombra" if getattr(args, "sombra", False) else (r["tipo"] or "simples")
    final = float(r["prob_final"])
    minima = (1 + minimo_de(cfg, r, agora)) / final
    r["odd_minima"] = f"{minima:.3f}"
    if r["tipo"] == "sombra":  # odd vista numa casa, apostável ou não: mede quantas vezes as casas chegam à mínima
        r["stake"], r["prob_final"] = "0.00", r["prob_justa"]
        guardar_rec(recs, r)
        lado, casa = ("acima" if float(r["odd"]) >= minima else "abaixo"), r["casa"] or "—"
        print(f"{r['ref']} (sombra): {r['evento']} — {r['selecao']} @ {float(r['odd']):.2f} ({casa}) · "
              f"odd mínima {minima:.2f} · {lado} da mínima · não apostar")
        return
    repetida = next((x for x in reais(recs) if x["evento"] == r["evento"] and x["inicio"] == r["inicio"]
                     and x["tipo"] != "multipla"), None) if r["tipo"] != "multipla" else None
    if repetida:
        sys.exit(f"Recusada: já há uma recomendação para este jogo ({repetida['ref']}, {repetida['selecao']}) — "
                 "no máximo uma aposta por jogo.")
    exposicao = em_jogo(apostas, recs, agora)
    calib = calibracao(cfg, r["fonte_justa"], recs)
    stake, motivo = validar(cfg, b, r, agora, getattr(args, "confirmado", False), getattr(args, "segunda_odd", None),
                            exposicao, calib[:2], ajuste_positivo_permitido(cfg, recs))
    if motivo:
        sys.exit(f"Recusada: {motivo}.")
    r["stake"] = f"{stake:.2f}"
    guardar_rec(recs, r)
    casa = r["casa"] or "casa por indicar"
    teto = cfg.get("teto_exposicao_pct")
    exp = f" · em jogo {eur(exposicao + stake)}" + (f" (teto {eur(b * teto / 100)})" if teto is not None else "")
    ev = float(r["odd"]) * final - 1
    print(f"{r['ref']}: {r['evento']} — {r['selecao']} @ {float(r['odd']):.2f} ({casa}) · EV {pct(ev, True)} "
          f"(calibrado {pct(calib[1] + calib[0] * ev, True)}) · odd mínima {minima:.2f} · "
          f"stake {eur(stake)} ({pct(stake / b)} da banca){exp}")
    if not stake:
        print("Stake 0: tem valor, mas a stake fica abaixo do mínimo (ou do teto de exposição). Não se aposta; "
              "fica registada para medir o CLV.")


def guardar_rec(recs, r):
    r["ref"] = f"{r['data']}#{sum(x['data'] == r['data'] for x in recs) + 1}"
    recs.append(r)
    escrever("recomendacoes.csv", recs, REC)


def cmd_registar(cfg, apostas, args):
    a = {c: "" for c in CAMPOS}
    if args.ref:
        r = next((x for x in ler("recomendacoes.csv") if x["ref"] == args.ref), None)
        if not r:
            sys.exit(f"A recomendação {args.ref} não existe")
        a.update(data=r["data"], desporto=r["desporto"], competicao=r["competicao"], evento=r["evento"],
                 mercado=MERCADOS.get(r["mercado"], r["mercado"]), selecao=r["selecao"], tipo=r["tipo"],
                 prob=r["prob_final"], confianca=r["confianca"], casa=r["casa"], prob_fecho=r["prob_fecho"])
    a.update({k: str(v) for k, v in vars(args).items() if k in CAMPOS and v is not None})
    for campo in ("desporto", "evento", "mercado", "selecao"):
        if not a[campo]:
            sys.exit(f"Falta --{campo} (ou usa --ref)")
    a["id"] = str(max((int(x["id"]) for x in apostas), default=0) + 1)
    a["data"], a["tipo"] = a["data"] or hoje(), a["tipo"] or "simples"
    liquidar(a, args.estado, args.lucro)
    apostas.append(a)
    gravar(apostas)
    mostrar(cfg, apostas, a)


def cmd_resultado(cfg, apostas, args):
    a = next((x for x in apostas if x["id"] == str(args.id)), None)
    if not a:
        sys.exit(f"Aposta #{args.id} não existe")
    for campo in ("stake", "odd"):
        if getattr(args, campo) is not None:
            a[campo] = str(getattr(args, campo))
    liquidar(a, args.estado, args.lucro)
    gravar(apostas)
    mostrar(cfg, apostas, a)


def resumo(apostas):
    """(n, apostado, lucro, yield, acerto) — nulas não contam para o volume nem para o acerto."""
    validas = [a for a in apostas if a["estado"] != "nula"]
    apostado = sum(float(a["stake"]) for a in validas if a.get("tipo") != "freebet")  # a freebet não é dinheiro teu
    lucro = sum(float(a["lucro"]) for a in apostas)
    decididas = [float(a["lucro"]) for a in validas if float(a["lucro"])]
    acerto = sum(x > 0 for x in decididas) / len(decididas) if decididas else 0.0
    return len(apostas), apostado, lucro, (lucro / apostado if apostado else 0.0), acerto


def linha_clv(linhas):
    valores = [clv(x["odd"], x["prob_fecho"]) for x in linhas if x.get("prob_fecho")]
    if not valores:
        return None
    return (f"CLV médio: {pct(sum(valores) / len(valores), True)} em {len(valores)} com odd de fecho "
            f"({pct(sum(v > 0 for v in valores) / len(valores))} positivas)")


def cmd_metricas(cfg, apostas, _):
    liq, ini = liquidadas(apostas), cfg["banca_inicial"]
    pendentes = len(apostas) - len(liq)
    print(linha_clv(apostas) or "CLV: ainda sem odds de fecho (regista as apostas antes do jogo).")
    if not liq:
        print(f"Ainda sem apostas liquidadas ({pendentes} pendentes). Banca: {eur(ini)}")
        return
    n, apostado, lucro, yld, acerto = resumo(liq)
    serie, pico, drawdown = [ini], ini, 0.0
    for a in liq:
        serie.append(serie[-1] + float(a["lucro"]))
        pico = max(pico, serie[-1])
        drawdown = min(drawdown, (serie[-1] - pico) / pico)
    odds = [float(a["odd"]) for a in liq if a["estado"] != "nula"]
    print(f"Apostas liquidadas: {n} ({pendentes} pendentes)")
    print(f"Banca: {eur(ini)} → {eur(serie[-1])}")
    print(f"Lucro total: {eur(lucro, True)}")
    print(f"ROI (sobre a banca inicial): {pct(lucro / ini, True)}")
    print(f"Yield (sobre {eur(apostado)} apostados): {pct(yld, True)}")
    print(f"Taxa de acerto: {pct(acerto)}")
    print(f"Odd média: {sum(odds) / len(odds):.2f}" if odds else "Odd média: —")
    print(f"Maior queda desde um máximo (drawdown): {pct(drawdown)}")
    for campo, titulo in (("desporto", "Por desporto"), ("tipo", "Por tipo"), ("casa", "Por casa")):
        grupos = defaultdict(list)
        for a in liq:
            grupos[a.get(campo) or "—"].append(a)
        print(f"\n{titulo}:")
        for nome, grupo in sorted(grupos.items()):
            n, _, lucro, yld, acerto = resumo(grupo)
            print(f"  {nome:12} {n:3} apostas  lucro {eur(lucro, True):>9}  yield {pct(yld, True):>7}  "
                  f"acerto {pct(acerto)}")
    print("\nEvolução da banca (por dia):")
    por_dia = defaultdict(float)
    for a in liq:
        por_dia[a["data"]] += float(a["lucro"])
    total = ini
    for dia, lucro in sorted(por_dia.items()):
        total += lucro
        print(f"  {dia}  {eur(lucro, True):>9}  →  {eur(total)}")
    blocos, lo, hi = "▁▂▃▄▅▆▇█", min(serie), max(serie)
    print("  " + "".join(blocos[round((v - lo) / (hi - lo) * 7)] if hi > lo else blocos[3] for v in serie))
    if n < 50:
        print(f"\nNota: {n} apostas é uma amostra pequena — estas métricas ainda são sobretudo variância. "
              "O CLV dá sinal mais cedo.")


def estat(valores):
    """(média, desvio-padrão, erro-padrão) de uma amostra."""
    n = len(valores)
    m = sum(valores) / n
    s = math.sqrt(sum((v - m) ** 2 for v in valores) / (n - 1)) if n > 1 else 0.0
    return m, s, s / math.sqrt(n)


def media_ic(valores):
    """'+4,2% ± 1,9% em 34' (intervalo de confiança de 95%)."""
    m, _, se = estat(valores)
    return f"{pct(m, True)} ± {pct(1.96 * se)} em {len(valores)}"


def circuito(r):
    texto = f"{r.get('desporto', '')} {r.get('competicao', '')}".lower()
    if "futebol" in texto:
        return "Futebol"
    for chave, nome in (("itf", "ITF"), ("challenger", "Challenger"), ("wta", "WTA")):
        if chave in texto:
            return nome
    return "ATP" if "ténis" in texto or "atp" in texto else (r.get("desporto") or "—")


def qualidade_clv(recs):
    """Detalhe do CLV das recomendações com fecho: intervalo de confiança, fonte do fecho, movimento do mercado
    depois da recomendação (M), segmentos e parte do EV aparente confirmada.

    1 + CLV = (1 + EV na recomendação) × (1 + M), com M = p_fecho / p_justa − 1: só M traz informação nova.
    """
    com = [r for r in reais(recs) if r.get("prob_fecho")]
    if not com:
        return []
    valores = [clv(r["odd"], r["prob_fecho"]) for r in com]
    m, s, _ = estat(valores)
    precisas = f" · para distinguir de 0 (t = 2) são precisas ~{math.ceil((2 * s / m) ** 2)}" if m > 0 and s else ""
    linhas = [f"CLV médio (IC 95%): {media_ic(valores)}{precisas}"]
    grupos = defaultdict(list)
    for r in com:
        grupos[r.get("fecho_fonte") or r["fonte_justa"]].append(r)
    for fonte, grupo in sorted(grupos.items()):
        mov = [float(r["prob_fecho"]) / float(r["prob_justa"]) - 1 for r in grupo]
        fracas = sum(float(r.get("fecho_antecedencia_h") or 0) > 2 for r in grupo)
        nota = f"; {fracas} com a última recolha a mais de 2 h do início (sinal fraco)" if fracas else ""
        linhas.append(f"  fecho {fonte}: CLV {media_ic([clv(r['odd'], r['prob_fecho']) for r in grupo])} · "
                      f"mercado a favor depois da recomendação (M) {pct(sum(mov) / len(mov), True)}{nota}")
    for titulo, chave in (("circuito", circuito),
                          ("lado", lambda r: "favorito" if float(r["prob_justa"]) >= 0.5 else "azarão"),
                          ("casa", lambda r: r.get("casa") or "—")):
        segmentos = defaultdict(list)
        for r in com:
            segmentos[chave(r)].append(clv(r["odd"], r["prob_fecho"]))
        if len(segmentos) > 1:
            linhas.append(f"  por {titulo}: " + " · ".join(f"{k} {media_ic(v)}" for k, v in sorted(segmentos.items())))
    ev = [float(r["odd"]) * float(r["prob_justa"]) - 1 for r in com]
    if len(com) >= 20 and sum(ev) > 0:
        linhas.append(f"Parte do EV aparente confirmada no fecho: {pct(sum(valores) / sum(ev))} em {len(com)} "
                      "(abaixo de 50% com 50+ recomendações: subir os limiares)")
    return linhas


def cobertura(recs):
    """Quantas das odds vistas nas casas do utilizador (registos-sombra e recomendações) chegam à odd mínima."""
    vistas = [r for r in recs if r.get("odd_minima") and r.get("casa") and r.get("sport_key") == "github"]
    if not vistas:
        return None
    por_casa = defaultdict(list)
    for r in vistas:
        por_casa[r["casa"]].append(float(r["odd"]) >= float(r["odd_minima"]) - 1e-9)
    return "Odds vistas nas tuas casas que chegam à mínima: " + " · ".join(
        f"{casa} {sum(v)}/{len(v)}" for casa, v in sorted(por_casa.items()))


def brier(linhas, campo):
    """Brier médio (menor é melhor) de uma coluna de probabilidades face ao resultado."""
    return sum((float(r[campo]) - (r["resultado"] == "ganha")) ** 2 for r in linhas) / len(linhas)


def cmd_avaliacao(cfg, _apostas, _):
    todas = ler("recomendacoes.csv")
    recs = reais(todas)
    if not todas:
        print("Ainda sem recomendações registadas.")
        return
    sombras = len(todas) - len(recs)
    print(f"Recomendações registadas: {len(recs)}" + (f" (mais {sombras} registos-sombra)" if sombras else ""))
    print(linha_clv(recs) or "CLV: ainda sem odds de fecho (corre 'odds.py fecho' antes dos jogos).")
    for texto in qualidade_clv(recs) + [cobertura(todas) or ""]:
        if texto:
            print(texto)
    for fonte in sorted({grupo_fonte(r["fonte_justa"]) for r in recs}):
        k, a, n = calibracao(cfg, fonte, recs)
        print(f"Calibração do EV ({fonte}): EV usado na stake = {a * 100:+.1f} pp + {k:.2f} × EV aparente "
              f"({n} com fecho)".replace(".", ","))
    decididas = [r for r in recs if r["resultado"] in ("ganha", "perdida")]
    if decididas:
        lucro = sum(float(r["odd"]) - 1 if r["resultado"] == "ganha" else -1 for r in decididas)
        ganhas = sum(r["resultado"] == "ganha" for r in decididas)
        print(f"ROI em papel (1 unidade por recomendação): {pct(lucro / len(decididas), True)} em "
              f"{len(decididas)} liquidadas (acerto {pct(ganhas / len(decididas))})")
        agente, mercado = brier(decididas, "prob_final"), brier(decididas, "prob_justa")
        com_fecho = [r for r in decididas if r["prob_fecho"]]
        def num(x):
            return f"{x:.4f}".replace(".", ",")

        fecho = f" · fecho {num(brier(com_fecho, 'prob_fecho'))} ({len(com_fecho)})" if com_fecho else ""
        print(f"Calibração (Brier, menor é melhor): agente {num(agente)} · mercado na recomendação "
              f"{num(mercado)}{fecho}")
        veredicto = "melhoram" if agente < mercado else "não melhoram — usar só o preço (ajuste 0)"
        aviso = " (amostra pequena)" if len(decididas) < 100 else ""
        print(f"Os ajustes do agente {veredicto}{aviso}.")
    n_fecho = sum(bool(r["prob_fecho"]) for r in recs)
    if regra_paragem(cfg, recs):
        print(f"REGRA DE PARAGEM ATIVA: CLV médio ≤ 0 em {n_fecho} recomendações. Parar e rever o método.")
    elif n_fecho < cfg["clv_minimo_amostra"]:
        print(f"Regra de paragem: faltam {cfg['clv_minimo_amostra'] - n_fecho} recomendações com fecho "
              "para decidir.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("estado", "metricas", "avaliacao"):
        sub.add_parser(nome)
    s = sub.add_parser("stake")
    s.add_argument("--prob", type=float, required=True)
    s.add_argument("--odd", type=float, required=True)
    s.add_argument("--multipla", action="store_true")
    s.add_argument("--fonte", default="consenso", choices=["pinnacle", "consenso", "modelo"],
                   help="de onde vem o preço justo (muda a calibração do EV)")
    rec = sub.add_parser("recomendar")
    rec.add_argument("--sombra", action="store_true",
                     help="só registar a odd vista numa casa (stake 0, fora do CLV): mede se as casas chegam à "
                          "mínima")
    rec.add_argument("--item", type=int, help="número do item na última 'odds.py valor'")
    rec.add_argument("--alvo", type=int, help="número do alvo no último 'odds.py alvos' (exige --odd e --casa)")
    for campo in ("data", "desporto", "competicao", "evento", "sport-key", "evento-id", "inicio", "mercado",
                  "selecao", "ponto", "casa", "prob-justa", "prob-final", "confianca", "notas"):
        rec.add_argument(f"--{campo}")
    rec.add_argument("--fonte-justa", default=None, help="pinnacle, consenso ou modelo (mercados secundários)")
    rec.add_argument("--odd", type=float)
    rec.add_argument("--segunda-odd", type=float, help="melhor odd da mesma seleção nas outras casas")
    rec.add_argument("--confirmado", action="store_true",
                     help="odd e notícias confirmadas (exigido com EV suspeito ou com uma só casa acima do mínimo)")
    rec.add_argument("--tipo", choices=["simples", "multipla", "live"])
    r = sub.add_parser("registar")
    r.add_argument("--ref", help="recomendação do plano (preenche os restantes campos)")
    for campo in ("desporto", "competicao", "evento", "mercado", "selecao", "prob", "confianca", "data",
                  "casa", "notas"):
        r.add_argument(f"--{campo}")
    r.add_argument("--odd", type=float, required=True)
    r.add_argument("--stake", type=float, required=True)
    r.add_argument("--tipo", choices=["simples", "multipla", "live", "freebet"],
                   help="freebet: a stake é da casa (não sai da banca; se perder, perde 0)")
    r.add_argument("--estado", default="pendente", choices=ESTADOS)
    r.add_argument("--lucro", type=float)
    res = sub.add_parser("resultado")
    res.add_argument("id", type=int)
    res.add_argument("estado", choices=ESTADOS[1:])
    for campo in ("stake", "odd", "lucro"):
        res.add_argument(f"--{campo}", type=float)
    args = p.parse_args()
    cfg, apostas = carregar()
    globals()[f"cmd_{args.cmd}"](cfg, apostas, args)


if __name__ == "__main__":
    main()
