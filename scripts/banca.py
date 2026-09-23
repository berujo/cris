#!/usr/bin/env python3
"""Banca, registo de apostas e métricas. Só biblioteca padrão.

  python3 scripts/banca.py estado
  python3 scripts/banca.py stake --prob 0.55 --odd 2.10 [--multipla]
  python3 scripts/banca.py registar --desporto Futebol --competicao "Liga Portugal" \
      --evento "Benfica vs Porto" --mercado 1X2 --selecao Benfica --odd 2.10 --stake 0.70 \
      [--prob 0.55 --confianca média --tipo simples --data 2026-09-24 \
       --estado ganha --lucro 0.77 --notas "plano 2026-09-24 #1"]
  python3 scripts/banca.py resultado ID ganha|perdida|nula|cashout [--stake X --odd Y --lucro Z]
  python3 scripts/banca.py metricas
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "dados"
CAMPOS = ["id", "data", "desporto", "competicao", "evento", "mercado", "selecao", "tipo",
          "odd", "prob", "confianca", "stake", "estado", "lucro", "notas"]
ESTADOS = ["pendente", "ganha", "perdida", "nula", "cashout"]


def eur(x, sinal=False):
    return f"{x:{'+' if sinal else ''}.2f} €".replace(".", ",")


def pct(x, sinal=False):
    return f"{x * 100:{'+' if sinal else ''}.1f}%".replace(".", ",")


def carregar():
    cfg = json.loads((DADOS / "config.json").read_text())
    with (DADOS / "apostas.csv").open(newline="") as f:
        return cfg, list(csv.DictReader(f))


def gravar(apostas):
    with (DADOS / "apostas.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(apostas)


def liquidadas(apostas):
    return sorted((a for a in apostas if a["estado"] != "pendente"),
                  key=lambda a: (a["data"], int(a["id"])))


def banca(cfg, apostas):
    return cfg["banca_inicial"] + sum(float(a["lucro"]) for a in liquidadas(apostas))


def limite_stop_loss(cfg):
    return cfg["banca_inicial"] * (1 - cfg["stop_loss_pct"] / 100)


def calcular_stake(cfg, banca_atual, prob, odd, multipla=False):
    """Kelly fracionado com teto, arredondado para baixo. Devolve (euros, ev)."""
    ev = prob * odd - 1
    teto = cfg["teto_multipla_pct" if multipla else "teto_stake_pct"] / 100
    fracao = max(0.0, min(cfg["fracao_kelly"] * ev / (odd - 1), teto))
    passo = round(cfg["arredondamento"] * 100)
    cents = math.floor(banca_atual * fracao * 100 + 1e-6)
    euros = (cents - cents % passo) / 100
    return (euros if euros >= cfg["stake_minima"] else 0.0), ev


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


def cmd_registar(cfg, apostas, args):
    a = {c: "" for c in CAMPOS}
    a.update({k: str(v) for k, v in vars(args).items() if k in CAMPOS and v is not None})
    a["id"] = str(max((int(x["id"]) for x in apostas), default=0) + 1)
    a["data"] = args.data or date.today().isoformat()
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


def cmd_metricas(cfg, apostas, _):
    liq, ini = liquidadas(apostas), cfg["banca_inicial"]
    pendentes = len(apostas) - len(liq)
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
    for campo, titulo in (("desporto", "Por desporto"), ("tipo", "Por tipo")):
        grupos = defaultdict(list)
        for a in liq:
            grupos[a[campo] or "—"].append(a)
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
        print(f"\nNota: {n} apostas é uma amostra pequena — estas métricas ainda são sobretudo variância.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("estado")
    sub.add_parser("metricas")
    s = sub.add_parser("stake")
    s.add_argument("--prob", type=float, required=True)
    s.add_argument("--odd", type=float, required=True)
    s.add_argument("--multipla", action="store_true")
    r = sub.add_parser("registar")
    for campo in ("desporto", "competicao", "evento", "mercado", "selecao"):
        r.add_argument(f"--{campo}", required=True)
    r.add_argument("--odd", type=float, required=True)
    r.add_argument("--stake", type=float, required=True)
    for campo in ("prob", "confianca", "data", "notas"):
        r.add_argument(f"--{campo}")
    r.add_argument("--tipo", default="simples", choices=["simples", "multipla", "live"])
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
