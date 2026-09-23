#!/usr/bin/env python3
"""Odds da The Odds API com probabilidade justa (sem margem) e valor da melhor odd. Só biblioteca padrão.

  python3 scripts/odds.py desportos
  python3 scripts/odds.py odds soccer_portugal_primeira_liga [--horas 36] [--mercados h2h,totals] [--casas betclic,bwin]

Precisa de ODDS_API_KEY (chave gratuita em https://the-odds-api.com). 'desportos' não gasta créditos;
'odds' gasta 1 crédito por mercado e por região. A probabilidade justa vem da Pinnacle quando existe,
senão da média das casas; "valor" = melhor odd × probabilidade justa − 1.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

API = "https://api.the-odds-api.com/v4"
GRUPOS = {"Soccer", "Tennis", "Basketball", "Baseball"}
LISBOA = ZoneInfo("Europe/Lisbon")


def pedir(caminho, **params):
    chave = os.environ.get("ODDS_API_KEY")
    if not chave:
        sys.exit("Falta ODDS_API_KEY — usa a pesquisa web para as odds.")
    url = f"{API}/{caminho}?{urllib.parse.urlencode({'apiKey': chave, **params})}"
    with urllib.request.urlopen(url, timeout=30) as r:
        print(f"(créditos restantes: {r.headers.get('x-requests-remaining', '?')})", file=sys.stderr)
        return json.load(r)


def sem_margem(odds):
    """Probabilidades justas: inversos das odds normalizados para somar 1."""
    inversos = [1 / o for o in odds]
    return [x / sum(inversos) for x in inversos]


def analisar(evento, casas=None):
    """Lista (mercado, seleção, prob. justa, fonte, melhor odd, casa, valor) por mercado e linha."""
    linhas = defaultdict(dict)  # (mercado, linha) -> casa -> {"titulo", "precos": {seleção: odd}}
    for casa in evento["bookmakers"]:
        for mercado in casa["markets"]:
            for o in mercado["outcomes"]:
                ponto = o.get("point")
                nome = o["name"] if ponto is None else f"{o['name']} {ponto:g}"
                linha = linhas[(mercado["key"], None if ponto is None else abs(ponto))]
                linha.setdefault(casa["key"], {"titulo": casa["title"], "precos": {}})["precos"][nome] = o["price"]
    resultado = []
    for (mercado, _), por_casa in linhas.items():
        ref = por_casa.get("pinnacle")
        selecoes = sorted(ref["precos"]) if ref else max((sorted(c["precos"]) for c in por_casa.values()), key=len)
        completas = [c for c in por_casa.values() if sorted(c["precos"]) == selecoes]
        if len(selecoes) < 2 or not completas:
            continue
        if ref:
            justas, fonte = sem_margem([ref["precos"][s] for s in selecoes]), "pinnacle"
        else:
            probs = [sem_margem([c["precos"][s] for s in selecoes]) for c in completas]
            justas, fonte = [sum(col) / len(probs) for col in zip(*probs)], f"média de {len(probs)} casas"
        for s, justa in zip(selecoes, justas):
            ofertas = [(c["precos"][s], c["titulo"]) for k, c in por_casa.items()
                       if s in c["precos"] and (not casas or k in casas)]
            if ofertas:
                melhor, titulo = max(ofertas)
                resultado.append((mercado, s, justa, fonte, melhor, titulo, melhor * justa - 1))
    return resultado


def cmd_desportos(_):
    for d in pedir("sports"):
        if d["group"] in GRUPOS and d["active"]:
            print(f"{d['key']:45} {d['title']}")


def cmd_odds(args):
    agora, fmt = datetime.now(timezone.utc), "%Y-%m-%dT%H:%M:%SZ"
    eventos = pedir(f"sports/{args.desporto}/odds", regions=args.regioes, markets=args.mercados,
                    oddsFormat="decimal", commenceTimeFrom=agora.strftime(fmt),
                    commenceTimeTo=(agora + timedelta(hours=args.horas)).strftime(fmt))
    casas = set(args.casas.split(",")) if args.casas else None
    for e in sorted(eventos, key=lambda e: e["commence_time"]):
        hora = datetime.fromisoformat(e["commence_time"]).astimezone(LISBOA)
        print(f"\n{hora:%d/%m %H:%M}  {e['home_team']} vs {e['away_team']}  ({e['sport_title']})")
        for mercado, sel, justa, fonte, melhor, casa, valor in analisar(e, casas):
            print(f"  {mercado:7} {sel:30} justa {1 / justa:5.2f} ({justa:5.1%}, {fonte})  "
                  f"melhor {melhor:5.2f} @ {casa:16} valor {valor:+.1%}")
    if not eventos:
        print(f"Sem eventos de {args.desporto} nas próximas {args.horas} h.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("desportos")
    o = sub.add_parser("odds")
    o.add_argument("desporto", help="chave de 'desportos', ex.: basketball_nba")
    o.add_argument("--horas", type=int, default=36)
    o.add_argument("--mercados", default="h2h", help="h2h,spreads,totals")
    o.add_argument("--regioes", default="eu")
    o.add_argument("--casas", help="só procurar a melhor odd nestas casas (chaves da API)")
    args = p.parse_args()
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
