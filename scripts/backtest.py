#!/usr/bin/env python3
"""Testes com histórico: a estratégia de preço e um modelo Elo contra o mercado.

  python3 scripts/backtest.py tenis <pasta com ficheiros do tennis-data.co.uk (.xls, .xlsx ou .csv)>
  python3 scripts/backtest.py futebol <Matches.csv do xgabora, ou CSVs do football-data.co.uk>

Precisa de pandas (e de xlrd/openpyxl para Excel): pip install -r requirements-backtest.txt
Imprime tabelas em Markdown, prontas para docs/backtest.md. Stake fixa de 1 unidade por aposta.
"""
import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from odds import shin  # noqa: E402

LIMIARES = (0.0, 0.02, 0.03, 0.05, 0.08)
ODD_MIN, ODD_MAX = 1.40, 4.00


def valido(odds):
    return all(isinstance(o, (int, float)) and not math.isnan(o) and o > 1 for o in odds)


def apostas(jogos, probs, casa, limiar):
    """(odd, ganhou, clv) de cada seleção com odd na casa, dentro do intervalo e com EV ≥ limiar."""
    feitas = []
    for j in jogos:
        p, odds = j[probs], j["odds"].get(casa)
        if p is None or odds is None:
            continue
        for i, (pi, o) in enumerate(zip(p, odds)):
            if ODD_MIN <= o <= ODD_MAX and (limiar is None or o * pi - 1 >= limiar):
                clv = o * j["fecho"][i] - 1 if j.get("fecho") else None
                feitas.append((o, i == j["y"], clv))
    return feitas


def resumo(feitas):
    """n, acerto, ROI, meia-largura do intervalo de confiança a 95% do ROI e CLV médio."""
    n = len(feitas)
    if not n:
        return 0, 0.0, 0.0, 0.0, None
    lucros = [o - 1 if g else -1 for o, g, _ in feitas]
    media = sum(lucros) / n
    var = sum((x - media) ** 2 for x in lucros) / max(n - 1, 1)
    clvs = [c for *_, c in feitas if c is not None]
    return n, sum(g for _, g, _ in feitas) / n, media, 1.96 * math.sqrt(var / n), \
        (sum(clvs) / len(clvs) if clvs else None)


def perda(jogos, probs):
    """Log-loss e Brier médios de uma coluna de probabilidades (menor é melhor)."""
    ll = br = 0.0
    for j in jogos:
        p = j[probs]
        ll -= math.log(max(p[j["y"]], 1e-12))
        br += sum((pi - (i == j["y"])) ** 2 for i, pi in enumerate(p))
    return ll / len(jogos), br / len(jogos)


def pct(x, sinal=False):
    return f"{x * 100:{'+' if sinal else ''}.1f}%".replace(".", ",")


def tabela_estrategias(titulo, linhas):
    print(f"\n### {titulo}\n")
    print("| Estratégia | EV mínimo | Apostas | Acerto | ROI | IC 95% do ROI | CLV médio |")
    print("|---|---|---|---|---|---|---|")
    for nome, limiar, (n, acerto, roi, ic, clv) in linhas:
        lim = "—" if limiar is None else pct(limiar)
        clv = "—" if clv is None else pct(clv, True)
        print(f"| {nome} | {lim} | {n} | {pct(acerto)} | {pct(roi, True)} | ±{pct(ic)} | {clv} |")


def tabela_perdas(titulo, jogos, colunas):
    print(f"\n### {titulo} ({len(jogos)} jogos)\n")
    print("| Probabilidades | Log-loss | Brier |")
    print("|---|---|---|")
    for nome, col in colunas:
        ll, br = perda(jogos, col)
        print(f"| {nome} | {ll:.4f} | {br:.4f} |".replace(".", ","))


def por_ano(titulo, jogos, probs, casa, limiar):
    anos = defaultdict(list)
    for j in jogos:
        anos[j["ano"]].append(j)
    print(f"\n### {titulo}\n")
    print("| Ano | Apostas | ROI |")
    print("|---|---|---|")
    for ano, grupo in sorted(anos.items()):
        n, _, roi, _, _ = resumo(apostas(grupo, probs, casa, limiar))
        print(f"| {ano} | {n} | {pct(roi, True) if n else '—'} |")


def misturar(jogos, peso):
    for j in jogos:
        if j["elo"] is not None:
            j["mistura"] = [(1 - peso) * m + peso * e for m, e in zip(j["justa"], j["elo"])]
        else:
            j["mistura"] = None


# --- Ténis --------------------------------------------------------------------------------------------

def carregar_tenis(pasta):
    ficheiros = sorted(p for p in Path(pasta).iterdir() if p.suffix in (".xls", ".xlsx", ".csv"))
    df = pd.concat([pd.read_csv(f) if f.suffix == ".csv" else pd.read_excel(f) for f in ficheiros],
                   ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[df["Comment"].astype(str).str.startswith(("Completed", "Retired"))]  # walkovers fora
    return df.sort_values("Date", kind="stable").reset_index(drop=True)


def elo_tenis(df):
    """Elo (metade geral, metade por superfície), com K a diminuir com a experiência."""
    geral, superficie, jogos = defaultdict(lambda: 1500.0), defaultdict(lambda: 1500.0), defaultdict(int)
    probs, experiencia = [], []
    for w, l, s in zip(df["Winner"], df["Loser"], df["Surface"]):
        rw, rl = (geral[w] + superficie[w, s]) / 2, (geral[l] + superficie[l, s]) / 2
        probs.append(1 / (1 + 10 ** ((rl - rw) / 400)))
        experiencia.append(min(jogos[w], jogos[l]))
        kw, kl = 250 / (jogos[w] + 5) ** 0.4, 250 / (jogos[l] + 5) ** 0.4
        for tabela, (a, b) in ((geral, (w, l)), (superficie, ((w, s), (l, s)))):
            esperado = 1 / (1 + 10 ** ((tabela[b] - tabela[a]) / 400))
            tabela[a] += kw * (1 - esperado)
            tabela[b] -= kl * (1 - esperado)
        jogos[w] += 1
        jogos[l] += 1
    return probs, experiencia


def jogos_tenis(df):
    df = df.copy()
    df["p_elo"], df["exp"] = elo_tenis(df)
    jogos = []
    for r in df.itertuples(index=False):
        pin = [getattr(r, "PSW", float("nan")), getattr(r, "PSL", float("nan"))]
        if r.Comment != "Completed" or r.exp < 20 or not valido(pin):
            continue
        odds = {}
        for casa in ("B365", "Max", "Avg"):
            cot = [getattr(r, f"{casa}W", float("nan")), getattr(r, f"{casa}L", float("nan"))]
            if valido(cot):
                odds[casa] = cot
        jogos.append({"ano": r.Date.year, "y": 0, "justa": shin(pin), "odds": odds,
                      "elo": [r.p_elo, 1 - r.p_elo], "fecho": None})
    return jogos


def cmd_tenis(args):
    jogos = jogos_tenis(carregar_tenis(args.caminhos[0]))
    misturar(jogos, 0.2)
    anos = f"{min(j['ano'] for j in jogos)}–{max(j['ano'] for j in jogos)}"
    print(f"## Ténis ATP {anos}: {len(jogos)} encontros com odds da Pinnacle\n")
    print("Preço justo = Pinnacle sem margem (Shin). Só encontros terminados e jogadores com ≥ 20 encontros.")
    tabela_perdas("Quem prevê melhor", jogos, [("Pinnacle (Shin)", "justa"), ("Elo por superfície", "elo"),
                                               ("80% Pinnacle + 20% Elo", "mistura")])
    linhas = []
    for casa, nome in (("B365", "Bet365 acima da Pinnacle"),
                       ("Max", "Melhor odd do mercado acima da Pinnacle")):
        linhas.append((f"{casa}: todas as seleções", None, resumo(apostas(jogos, "justa", casa, None))))
        linhas += [(nome, t, resumo(apostas(jogos, "justa", casa, t))) for t in LIMIARES[1:]]
    linhas += [("Elo contra a melhor odd", t, resumo(apostas(jogos, "elo", "Max", t))) for t in LIMIARES[2:]]
    linhas += [("Mistura contra a melhor odd", t, resumo(apostas(jogos, "mistura", "Max", t)))
               for t in LIMIARES[2:]]
    tabela_estrategias("Estratégias (odds entre 1,40 e 4,00)", linhas)
    por_ano("Melhor odd do mercado com EV ≥ 3% contra a Pinnacle, por ano", jogos, "justa", "Max", 0.03)


# --- Futebol ------------------------------------------------------------------------------------------

def elo_futebol(treino, teste, largura=25, limite=500):
    """P(1/X/2 | diferença de Elo), estimada por classes no treino e aplicada ao teste."""
    def classe(d):
        return max(-limite, min(limite, round(d / largura) * largura))
    contagens = defaultdict(lambda: [1, 1, 1])
    for j in treino:
        contagens[classe(j["dif_elo"])][j["y"]] += 1
    for j in teste:
        c = contagens[classe(j["dif_elo"])]
        j["elo"] = [x / sum(c) for x in c]


def jogos_futebol(caminhos):
    df = pd.concat([pd.read_csv(c, low_memory=False, encoding_errors="ignore") for c in caminhos],
                   ignore_index=True)
    xgabora = "OddHome" in df.columns
    if xgabora:
        df["data"] = pd.to_datetime(df["MatchDate"], errors="coerce")
        cols = {"res": "FTResult", "B365": ("OddHome", "OddDraw", "OddAway"),
                "Max": ("MaxHome", "MaxDraw", "MaxAway")}
    else:
        df["data"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        cols = {"res": "FTR", "B365": ("B365H", "B365D", "B365A"), "Max": ("MaxH", "MaxD", "MaxA"),
                "PS": ("PSH", "PSD", "PSA"), "PSC": ("PSCH", "PSCD", "PSCA")}
    jogos = []
    for r in df.to_dict("records"):
        if r[cols["res"]] not in ("H", "D", "A") or pd.isna(r["data"]):
            continue
        odds = {casa: [r.get(c) for c in cols[casa]] for casa in ("B365", "Max", "PS", "PSC") if casa in cols}
        odds = {casa: cot for casa, cot in odds.items() if valido(cot)}
        referencia = odds.get("PS") or odds.get("B365")
        if not referencia or "Max" not in odds:
            continue
        jogos.append({"ano": r["data"].year, "data": r["data"], "y": "HDA".index(r[cols["res"]]),
                      "justa": shin(referencia), "odds": odds, "elo": None,
                      "fecho": shin(odds["PSC"]) if "PSC" in odds else None,
                      "dif_elo": r["HomeElo"] - r["AwayElo"]
                      if xgabora and valido([r["HomeElo"], r["AwayElo"]]) else None})
    return jogos, "PS" in cols


def cmd_futebol(args):
    jogos, com_pinnacle = jogos_futebol(args.caminhos)
    fonte = "Pinnacle" if com_pinnacle else "Bet365"
    anos = f"{min(j['ano'] for j in jogos)}–{max(j['ano'] for j in jogos)}"
    print(f"## Futebol {anos}: {len(jogos)} jogos com odds\n")
    print(f"Preço justo = {fonte} sem margem (Shin). Melhor odd = máxima de ~17 casas europeias.")
    linhas = [(f"Melhor odd acima do justo ({fonte})", t, resumo(apostas(jogos, "justa", "Max", t)))
              for t in LIMIARES[1:]]
    if com_pinnacle:
        linhas += [("Bet365 acima da Pinnacle", t, resumo(apostas(jogos, "justa", "B365", t)))
                   for t in LIMIARES[1:]]
    com_elo = [j for j in jogos if j["dif_elo"] is not None]
    if com_elo:
        corte = pd.Timestamp("2016-07-01")
        treino, teste = [j for j in com_elo if j["data"] < corte], [j for j in com_elo if j["data"] >= corte]
        elo_futebol(treino, teste)
        misturar(teste, 0.2)
        tabela_perdas("Quem prevê melhor (época 2016/17 em diante; Elo treinado antes)", teste,
                      [(f"{fonte} (Shin)", "justa"), ("Elo (clubelo)", "elo"),
                       (f"80% {fonte} + 20% Elo", "mistura")])
        linhas += [("Elo contra a melhor odd (2016+)", t, resumo(apostas(teste, "elo", "Max", t)))
                   for t in LIMIARES[2:]]
        linhas += [("Mistura contra a melhor odd (2016+)", t, resumo(apostas(teste, "mistura", "Max", t)))
                   for t in LIMIARES[2:]]
    tabela_estrategias("Estratégias (odds entre 1,40 e 4,00)", linhas)
    por_ano(f"Melhor odd com EV ≥ 5% contra {fonte}, por ano", jogos, "justa", "Max", 0.05)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("tenis", "futebol"):
        sub.add_parser(nome).add_argument("caminhos", nargs="+")
    args = p.parse_args()
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
