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
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DADOS = Path(__file__).resolve().parent.parent / "dados"
CAMPOS = ["id", "data", "desporto", "competicao", "evento", "mercado", "selecao", "tipo", "odd", "prob",
          "confianca", "stake", "estado", "lucro", "casa", "ref", "prob_fecho", "notas"]
REC = ["ref", "data", "desporto", "competicao", "evento", "sport_key", "evento_id", "inicio", "mercado",
       "selecao", "ponto", "tipo", "odd", "casa", "prob_justa", "fonte_justa", "prob_final", "confianca",
       "stake", "prob_fecho", "resultado", "notas"]
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


def ev_minimo(cfg, fonte):
    return cfg["ev_minimo_pct" if fonte == "pinnacle" else "ev_minimo_consenso_pct"] / 100


def clv(odd, prob_fecho):
    """Valor da odd apostada face à probabilidade justa no fecho."""
    return float(odd) * float(prob_fecho) - 1


def regra_paragem(cfg, recs):
    """Verdadeira se o CLV médio for ≤ 0 ao fim da amostra mínima de recomendações com fecho."""
    valores = [clv(r["odd"], r["prob_fecho"]) for r in recs if r["prob_fecho"]]
    return len(valores) >= cfg["clv_minimo_amostra"] and sum(valores) / len(valores) <= 0


def calcular_stake(cfg, banca_atual, prob, odd, multipla=False):
    """Kelly fracionado com teto, arredondado para baixo. Devolve (euros, ev)."""
    ev = prob * odd - 1
    teto = cfg["teto_multipla_pct" if multipla else "teto_stake_pct"] / 100
    fracao = max(0.0, min(cfg["fracao_kelly"] * ev / (odd - 1), teto))
    passo = round(cfg["arredondamento"] * 100)
    cents = math.floor(banca_atual * fracao * 100 + 1e-6)
    euros = (cents - cents % passo) / 100
    return (euros if euros >= cfg["stake_minima"] else 0.0), ev


def validar(cfg, banca_atual, r):
    """Aplica as regras a uma recomendação. Devolve (stake, motivo da recusa ou None)."""
    odd, justa, final = float(r["odd"]), float(r["prob_justa"]), float(r["prob_final"])
    multipla, minimo = r["tipo"] == "multipla", ev_minimo(cfg, r["fonte_justa"])
    if abs(final - justa) * 100 > cfg["ajuste_max_pp"] + 1e-9:
        ajuste = f"{(final - justa) * 100:+.1f}".replace(".", ",")
        return 0.0, f"ajuste de {ajuste} pp acima do máximo de {cfg['ajuste_max_pp']} pp"
    if not multipla and not cfg["odd_minima"] <= odd <= cfg["odd_maxima"]:
        return 0.0, f"odd {odd:.2f} fora do intervalo {cfg['odd_minima']:.2f}–{cfg['odd_maxima']:.2f}"
    if odd * final - 1 < minimo:
        return 0.0, f"EV {pct(odd * final - 1, True)} abaixo do mínimo de {pct(minimo)}"
    stake, _ = calcular_stake(cfg, banca_atual, final, odd, multipla)
    return (stake, None) if stake else (0.0, "stake abaixo do mínimo")


def liquidar(a, estado, lucro):
    if estado == "cashout" and lucro is None:
        sys.exit("cashout exige --lucro")
    if lucro is None and estado != "pendente":
        stake, odd = float(a["stake"]), float(a["odd"])
        lucro = {"ganha": stake * (odd - 1), "perdida": -stake, "nula": 0.0}[estado]
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
    euros, ev = calcular_stake(cfg, b, args.prob, args.odd, args.multipla)
    if ev <= 0:
        print(f"Sem valor (EV {pct(ev, True)}): não apostar.")
    elif not euros:
        print(f"EV {pct(ev, True)}, mas a stake fica abaixo do mínimo: não apostar.")
    else:
        print(f"Stake: {eur(euros)} ({pct(euros / b)} da banca de {eur(b)}) | EV {pct(ev, True)} | "
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
                 prob_justa=f"{s['justa']:.4f}", fonte_justa=s["fonte"])
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
    r["data"], r["tipo"] = r["data"] or hoje(), r["tipo"] or "simples"
    stake, motivo = validar(cfg, b, r)
    if motivo:
        sys.exit(f"Recusada: {motivo}.")
    r["stake"] = f"{stake:.2f}"
    r["ref"] = f"{r['data']}#{sum(x['data'] == r['data'] for x in recs) + 1}"
    recs.append(r)
    escrever("recomendacoes.csv", recs, REC)
    final = float(r["prob_final"])
    casa = r["casa"] or "casa por indicar"
    print(f"{r['ref']}: {r['evento']} — {r['selecao']} @ {float(r['odd']):.2f} ({casa}) · "
          f"EV {pct(float(r['odd']) * final - 1, True)} · odd mínima "
          f"{(1 + ev_minimo(cfg, r['fonte_justa'])) / final:.2f} · stake {eur(stake)} ({pct(stake / b)} da banca)")


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
    apostado = sum(float(a["stake"]) for a in validas)
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


def brier(linhas, campo):
    """Brier médio (menor é melhor) de uma coluna de probabilidades face ao resultado."""
    return sum((float(r[campo]) - (r["resultado"] == "ganha")) ** 2 for r in linhas) / len(linhas)


def cmd_avaliacao(cfg, _apostas, _):
    recs = ler("recomendacoes.csv")
    if not recs:
        print("Ainda sem recomendações registadas.")
        return
    print(f"Recomendações registadas: {len(recs)}")
    print(linha_clv(recs) or "CLV: ainda sem odds de fecho (corre 'odds.py fecho' antes dos jogos).")
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
    rec = sub.add_parser("recomendar")
    rec.add_argument("--item", type=int, help="número do item na última 'odds.py valor'")
    rec.add_argument("--alvo", type=int, help="número do alvo no último 'odds.py alvos' (exige --odd e --casa)")
    for campo in ("data", "desporto", "competicao", "evento", "sport-key", "evento-id", "inicio", "mercado",
                  "selecao", "ponto", "casa", "prob-justa", "prob-final", "confianca", "notas"):
        rec.add_argument(f"--{campo}")
    rec.add_argument("--fonte-justa", default=None, help="pinnacle ou consenso")
    rec.add_argument("--odd", type=float)
    rec.add_argument("--tipo", choices=["simples", "multipla", "live"])
    r = sub.add_parser("registar")
    r.add_argument("--ref", help="recomendação do plano (preenche os restantes campos)")
    for campo in ("desporto", "competicao", "evento", "mercado", "selecao", "prob", "confianca", "data",
                  "casa", "notas"):
        r.add_argument(f"--{campo}")
    r.add_argument("--odd", type=float, required=True)
    r.add_argument("--stake", type=float, required=True)
    r.add_argument("--tipo", choices=["simples", "multipla", "live"])
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
