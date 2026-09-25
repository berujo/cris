#!/usr/bin/env python3
"""Odds da The Odds API: preço justo (Pinnacle, método de Shin), valor, fecho e resultados. Só biblioteca padrão.

  python3 scripts/odds.py desportos
  python3 scripts/odds.py valor [--horas 36] [--limiar 3]      # varre as competições de config.json com jogos
  python3 scripts/odds.py odds <chave> [--horas 36] [--mercados h2h,totals]
  python3 scripts/odds.py fecho [--minutos 90] [--ref 2026-09-25#1 ...]  # prob. justa perto do início (CLV)
  python3 scripts/odds.py resultados                           # liquida as recomendações já terminadas
  python3 scripts/odds.py fontes                               # que fontes de odds estão acessíveis agora
  python3 scripts/odds.py alvos [--horas 36] [--desporto tenis futebol] [--challengers] [--itf]
                                                               # odds mínimas a partir das fontes no GitHub
  python3 scripts/odds.py mercados --alvo 128                  # sets, total e handicap de jogos (preço de modelo)
  python3 scripts/odds.py ev --odd 2.20 --justa 2.10 [--freebet]  # EV de uma odd aumentada ou de uma freebet

Precisa de ODDS_API_KEY (chave gratuita em https://the-odds-api.com). As listas de desportos e de jogos não
gastam créditos; as odds gastam 1 crédito por mercado e região; os resultados gastam 2 por desporto.
Sem a API (ou com a rede fechada), 'alvos' usa fontes públicas no GitHub, que passam pela rede do ambiente.
"""
import argparse
import io
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

import banca
import tenis

API = "https://api.the-odds-api.com/v4"
LISBOA = ZoneInfo("Europe/Lisbon")
FMT = "%Y-%m-%dT%H:%M:%SZ"
GRUPOS = {"Soccer", "Tennis", "Basketball", "Baseball"}
restantes = None  # créditos da API, atualizados a cada pedido
# Fontes públicas atualizadas por GitHub Actions (o GitHub passa pela rede do ambiente). Ver docs/apis.md.
FONTES = {
    "tenis": "https://raw.githubusercontent.com/Mriganka-codes/tennis_data/main/matches.json",
    "futebol": "https://raw.githubusercontent.com/aimidas1/pinnacle_bet365_odds_data/main/data/season_2026/"
               "next_games/next_games.xlsx",
}
HORA_TENNISEXPLORER = ZoneInfo("Europe/Prague")  # a fonte de ténis dá as horas na hora da Europa Central
DESPORTO = {"soccer": "futebol", "tennis": "tenis", "basketball": "basquetebol", "baseball": "basebol"}


def pedir(caminho, **params):
    global restantes
    chave = os.environ.get("ODDS_API_KEY")
    if not chave:
        sys.exit("Falta ODDS_API_KEY — usa a pesquisa web para as odds.")
    url = f"{API}/{caminho}?{urllib.parse.urlencode({'apiKey': chave, **params})}"
    with urllib.request.urlopen(url, timeout=30) as r:
        if r.headers.get("x-requests-remaining") is not None:
            restantes = int(float(r.headers["x-requests-remaining"]))
            print(f"(créditos restantes: {restantes})", file=sys.stderr)
        return json.load(r)


def shin(odds):
    """Probabilidades justas pelo método de Shin: tira mais margem aos azarões do que aos favoritos."""
    inv = [1 / o for o in odds]
    soma = sum(inv)
    if soma <= 1:  # sem margem: basta normalizar
        return [x / soma for x in inv]

    def probs(z):
        return [(math.sqrt(z * z + 4 * (1 - z) * x * x / soma) - z) / (2 * (1 - z)) for x in inv]

    lo, hi = 0.0, 0.99
    for _ in range(100):
        z = (lo + hi) / 2
        lo, hi = (z, hi) if sum(probs(z)) > 1 else (lo, z)
    p = probs((lo + hi) / 2)
    return [x / sum(p) for x in p]


def potencia(odds):
    """Probabilidades justas pelo método da potência: p_i = (1/o_i)^k, com k tal que somem 1."""
    inv = [1 / o for o in odds]
    if sum(inv) <= 1:
        return [x / sum(inv) for x in inv]
    lo, hi = 1.0, 20.0
    for _ in range(100):
        k = (lo + hi) / 2
        lo, hi = (k, hi) if sum(x ** k for x in inv) > 1 else (lo, k)
    return [x ** ((lo + hi) / 2) for x in inv]


def justas_consenso(odds):
    """Preço justo de uma média de casas: por seleção, o menor entre Shin e potência (o mais conservador).

    Na média de casas do ténis, Shin, potência e odds-ratio empatam em log-loss e o proporcional é o pior;
    a potência está ligeiramente melhor calibrada (teste em 17 274 encontros ATP 2010–2018)."""
    return [min(a, b) for a, b in zip(shin(odds), potencia(odds))]


def minutos(iso, agora):
    return (datetime.fromisoformat(iso) - agora).total_seconds() / 60


def analisar(evento, excluir=(), agora=None):
    """Por mercado e linha: probabilidade justa (Pinnacle, senão média das casas) e melhor odd de cada seleção."""
    agora = agora or datetime.now(timezone.utc)
    linhas = defaultdict(dict)  # (mercado, linha) -> casa -> {titulo, atualizado, precos: {seleção: (odd, ponto)}}
    for casa in evento["bookmakers"]:
        for mercado in casa["markets"]:
            for o in mercado["outcomes"]:
                ponto = o.get("point")
                nome = o["name"] if ponto is None else f"{o['name']} {ponto:g}"
                linha = linhas[(mercado["key"], None if ponto is None else abs(ponto))]
                entrada = linha.setdefault(casa["key"], {
                    "titulo": casa["title"], "precos": {},
                    "atualizado": mercado.get("last_update") or casa.get("last_update")})
                entrada["precos"][nome] = (o["price"], ponto)
    resultado = []
    for (mercado, _), por_casa in linhas.items():
        ref = por_casa.get("pinnacle")
        selecoes = sorted(ref["precos"]) if ref else max((sorted(c["precos"]) for c in por_casa.values()), key=len)
        completas = [c for c in por_casa.values() if sorted(c["precos"]) == selecoes]
        if len(selecoes) < 2 or not completas:
            continue
        if ref:
            justas, fonte = shin([ref["precos"][s][0] for s in selecoes]), "pinnacle"
        else:
            probs = [shin([c["precos"][s][0] for s in selecoes]) for c in completas]
            justas, fonte = [sum(col) / len(probs) for col in zip(*probs)], f"média de {len(probs)} casas"
        for s, justa in zip(selecoes, justas):
            ofertas = [(c["precos"][s][0], c) for k, c in por_casa.items() if s in c["precos"] and k not in excluir]
            if not ofertas:
                continue
            melhor, c = max(ofertas, key=lambda x: x[0])
            idade = -minutos(c["atualizado"], agora) if c["atualizado"] else None
            resultado.append({"mercado": mercado, "selecao": s, "ponto": c["precos"][s][1], "justa": justa,
                              "fonte": fonte, "melhor": melhor, "casa": c["titulo"],
                              "idade_min": None if idade is None else round(idade), "valor": melhor * justa - 1})
    return resultado


def competicoes(cfg):
    """Chaves ativas da API que correspondem a config.json (um '*' no fim é prefixo)."""
    ativas = sorted(d["key"] for d in pedir("sports") if d["active"])
    return [k for padrao in cfg["competicoes"] for k in ativas
            if (k == padrao or (padrao.endswith("*") and k.startswith(padrao[:-1])))
            and banca.ativo(cfg, DESPORTO.get(k.split("_")[0], ""))]


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cris"}), timeout=30) as r:
        return r.read()


def ler_xlsx(dados):
    """Primeira folha de um .xlsx como lista de dicionários, só com a biblioteca padrão."""
    m = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(dados)) as z:
        partilhadas = []
        if "xl/sharedStrings.xml" in z.namelist():
            partilhadas = ["".join(t.text or "" for t in si.iter(f"{m}t"))
                           for si in ElementTree.fromstring(z.read("xl/sharedStrings.xml")).iter(f"{m}si")]
        folha = ElementTree.fromstring(z.read("xl/worksheets/sheet1.xml"))
    linhas = []
    for row in folha.iter(f"{m}row"):
        valores = {}
        for c in row.iter(f"{m}c"):
            v = c.find(f"{m}v")
            if c.get("t") == "s":
                valor = partilhadas[int(v.text)]
            elif c.get("t") == "inlineStr":
                valor = "".join(t.text or "" for t in c.iter(f"{m}t"))
            else:
                valor = None if v is None else v.text
            valores[re.match(r"[A-Z]+", c.get("r")).group()] = valor
        linhas.append(valores)
    cabecalho = linhas[0] if linhas else {}
    return [{cabecalho[k]: v for k, v in linha.items() if k in cabecalho} for linha in linhas[1:]]


def numero(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x > 1 else None


def data_utc(v):
    """Data da folha de cálculo: texto ISO ou número de série do Excel, em UTC."""
    try:
        return datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=float(v))
    except (TypeError, ValueError):
        return datetime.fromisoformat(str(v)).replace(tzinfo=timezone.utc)


def alvos_tenis():
    d = json.loads(baixar(FONTES["tenis"]))
    recolhido = datetime.fromisoformat(d["last_updated"]).replace(tzinfo=timezone.utc)
    dia = recolhido.date()  # dia da recolha = dia da página da fonte
    itens = []
    for jogo in d["matches"]:
        cotacoes = [numero(jogo.get("odds1")), numero(jogo.get("odds2"))]
        if not all(cotacoes) or not re.fullmatch(r"\d{2}:\d{2}", jogo.get("time") or ""):
            continue
        h, mi = map(int, jogo["time"].split(":"))
        inicio = datetime(dia.year, dia.month, dia.day, h, mi, tzinfo=HORA_TENNISEXPLORER).astimezone(timezone.utc)
        nomes = [re.sub(r"\s*\([^)]*\)$", "", jogo[k]) for k in ("player1", "player2")]  # sem cabeças de série
        for nome, odd, justa in zip(nomes, cotacoes, justas_consenso(cotacoes)):
            itens.append({"desporto": "Ténis", "competicao": f"{jogo.get('tour', '')} {jogo['tournament']}".strip(),
                          "evento": f"{nomes[0]} vs {nomes[1]}", "inicio": inicio.strftime(FMT), "mercado": "h2h",
                          "selecao": nome, "ponto": None, "justa": justa, "fonte": "consenso",
                          "odd_fonte": odd, "casa_fonte": "tennisexplorer", "recolha": recolhido.strftime(FMT)})
    return itens, f"tennisexplorer via GitHub, recolhido a {d['last_updated'][:16].replace('T', ' ')} UTC"


def alvos_futebol():
    itens = []
    for linha in ler_xlsx(baixar(FONTES["futebol"])):
        if " vs " not in (linha.get("fixture_name") or "") or not linha.get("starting_at"):
            continue
        casa, fora = [x.strip() for x in linha["fixture_name"].split(" vs ", 1)]
        # Na fonte, os rótulos Home/Away do 1X2 estão trocados: "Away" é a equipa da casa (confirmado a 24/09/2026).
        mercados = [("h2h", None, [casa, "Empate", fora], ("Away", "Draw", "Home"), "Match_Odds_{}")]
        mercados += [("totals", linha_, [f"Over {linha_:g}", f"Under {linha_:g}"], ("Over", "Under"),
                      "Lines_Goals_{}_" + f"{linha_:g}") for linha_ in (2.5, 3.5)]
        for mercado, ponto, selecoes, rotulos, modelo in mercados:
            pin = [numero(linha.get("Pinnacle_" + modelo.format(r))) for r in rotulos]
            b365 = [numero(linha.get("Bet365_" + modelo.format(r))) for r in rotulos]
            if not all(pin):
                continue
            for nome, justa, odd in zip(selecoes, shin(pin), b365):
                itens.append({"desporto": "Futebol", "competicao": linha.get("league_info") or "",
                              "evento": f"{casa} vs {fora}", "inicio": data_utc(linha["starting_at"]).strftime(FMT),
                              "mercado": mercado, "selecao": nome, "ponto": ponto, "justa": justa,
                              "fonte": "pinnacle", "odd_fonte": odd, "casa_fonte": "Bet365"})
    return itens, "Pinnacle e Bet365 via GitHub (atualização diária)"


def cmd_alvos(args):
    """Odd mínima a procurar nas casas do utilizador, a partir do preço justo das fontes no GitHub."""
    cfg, agora = banca.config(), datetime.now(timezone.utc)
    b = banca.banca(cfg, banca.ler("apostas.csv"))
    itens = []
    for nome, funcao in (("tenis", alvos_tenis), ("futebol", alvos_futebol)):
        if nome not in (args.desporto or [d for d in ("tenis", "futebol") if banca.ativo(cfg, d)]):
            continue
        try:
            novos, nota = funcao()
        except Exception as e:  # fonte em baixo, bloqueada ou com formato mudado
            print(f"{nome}: fonte indisponível ({e})")
            continue
        itens += novos
        print(f"{nome}: {nota}")
    anteriores = guardar_consenso(itens, agora)
    limite = agora + timedelta(hours=args.horas)
    challengers = args.challengers or cfg.get("incluir_challengers", False)
    itf = getattr(args, "itf", False) or cfg.get("incluir_itf", False)
    ligas = cfg.get("futebol_ligas", [""])
    excluidas = cfg.get("competicoes_excluidas", [])
    itens = [s for s in itens if agora < datetime.fromisoformat(s["inicio"]) <= limite
             and (challengers or not re.search(r"challenger", s["competicao"], re.I))
             and (itf or not re.search(r"\bitf\b", s["competicao"], re.I))
             and not any(re.search(x, s["competicao"], re.I) for x in excluidas)
             and (s["desporto"] != "Futebol" or any(liga in s["competicao"] for liga in ligas))]
    # Alerta de integridade: o consenso andou ≥ 5 pp para quem era o azarão na recolha anterior, sem explicação
    # à vista (os alertas de apostas suspeitas no ténis disparam com dinheiro grande nos azarões).
    alertas = set()
    for s in itens:
        antes = anteriores.get(chave_consenso(s))
        s["mov_pp"] = None if antes is None else round((s["justa"] - antes) * 100, 1)
        if s["mov_pp"] is not None and antes < 0.5 and s["mov_pp"] >= cfg.get("alerta_mov_azarao_pp", 5):
            alertas.add(s["evento"])
    recs = banca.ler("recomendacoes.csv")
    calibs = {}
    velha_h = cfg.get("recolha_velha_h")
    for s in itens:
        s["alerta"] = s["evento"] in alertas
        antecedencia = None
        if s.get("recolha"):
            ate_inicio = datetime.fromisoformat(s["inicio"]) - datetime.fromisoformat(s["recolha"])
            antecedencia = ate_inicio.total_seconds() / 3600

        def minima(idade):
            ev = banca.ev_minimo(cfg, s["fonte"], s["justa"], s["competicao"], idade, antecedencia_h=antecedencia)
            return (1 + ev) / s["justa"]
        s["minima"] = minima(banca.idade_horas(s.get("recolha"), agora))
        s["minima_tarde"], s["fresco_ate"] = s["minima"], None
        if s.get("recolha") and velha_h is not None:
            fim = datetime.fromisoformat(s["recolha"]) + timedelta(hours=velha_h)
            if fim > agora:  # a odd mínima sobe quando a recolha fica velha
                s["minima_tarde"], s["fresco_ate"] = minima(math.inf), fim.strftime(FMT)
        grupo = banca.grupo_fonte(s["fonte"])
        calibs.setdefault(grupo, banca.calibracao(cfg, s["fonte"], recs)[:2])
        s["stake"] = banca.calcular_stake(cfg, b, s["justa"], s["minima"] + 1e-9, calib=calibs[grupo])[0]
        s["odd_stake"] = None  # com stake 0 à odd mínima: a partir de que odd a stake chega ao mínimo
        if not s["stake"]:
            odd = math.ceil(s["minima"] * 100) / 100
            while odd <= cfg["odd_maxima"] and not banca.calcular_stake(cfg, b, s["justa"], odd,
                                                                         calib=calibs[grupo])[0]:
                odd = round(odd + 0.01, 2)
            s["odd_stake"] = odd if odd <= cfg["odd_maxima"] else None
    itens = sorted((s for s in itens if cfg["odd_minima"] <= s["minima"] <= cfg["odd_maxima"]),
                   key=lambda s: (s["inicio"], s["evento"]))
    # Números estáveis: o mesmo alvo mantém o # que o utilizador viu no plano; os novos continuam a numeração.
    ficheiro = banca.DADOS / "alvos.json"
    antigos = json.loads(ficheiro.read_text())["itens"] if ficheiro.exists() else []
    antigos = [s for s in antigos if datetime.fromisoformat(s["inicio"]) > agora - timedelta(hours=24)]
    vistos = {(s["evento"], s["mercado"], s["selecao"], s["inicio"]): s["id"] for s in antigos}
    proximo = max(vistos.values(), default=0) + 1
    novos = 0
    for s in itens:
        chave = (s["evento"], s["mercado"], s["selecao"], s["inicio"])
        s["novo"] = chave not in vistos
        s["id"], proximo, novos = (vistos[chave], proximo, novos) if chave in vistos else (proximo, proximo + 1,
                                                                                          novos + 1)
    atuais = {s["id"] for s in itens}
    guardar = sorted(itens + [s for s in antigos if s["id"] not in atuais], key=lambda s: s["id"])
    if guardar and (novos or not ficheiro.exists()):  # sem alvos novos, a lista guardada não muda
        ficheiro.write_text(json.dumps({"hora": agora.strftime(FMT), "itens": guardar}, ensure_ascii=False, indent=1))
    print(f"{len(itens)} alvos nas próximas {args.horas} h, {novos} novos ('novo' = não estava na leitura anterior; "
          "★ = a própria fonte já paga acima da odd mínima, só possível no futebol).")
    print("Só um lado por jogo. A odd mínima já inclui a margem de segurança do consenso (mais alta nos azarões, "
          "nos Challengers e quando a recolha fica velha). ⚠ = o consenso andou ≥ 5 pp para o azarão: confirmar a "
          "notícia ou saltar o jogo.")
    for s in itens:
        hora = datetime.fromisoformat(s["inicio"]).astimezone(LISBOA)
        estrela = " ★" if s["fonte"] != "consenso" and s["odd_fonte"] and s["odd_fonte"] >= s["minima"] else ""
        fonte = f"{s['odd_fonte']:.2f} ({s['casa_fonte']})" if s["odd_fonte"] else "—"
        tarde = ""
        if s.get("fresco_ate") and s["minima_tarde"] > s["minima"] + 0.005:
            fim = datetime.fromisoformat(s["fresco_ate"]).astimezone(LISBOA)
            tarde = f" ({s['minima_tarde']:.2f} depois das {fim:%H:%M})"
        mov = "" if not s.get("mov_pp") else f" · mov {s['mov_pp']:+.1f} pp".replace(".", ",")
        alerta = " · ⚠ mov. para o azarão" if s.get("alerta") else ""
        stake = banca.eur(s["stake"])
        if not s["stake"]:
            stake = (f"0 (0,10 € a partir de {s['odd_stake']:.2f})" if s.get("odd_stake")
                     else "0 (não chega à stake mínima: só registo)")
        print(f"[{s['id']}] {hora:%d/%m %H:%M} {s['competicao']} · {s['evento']} · {s['mercado']} {s['selecao']} · "
              f"justa {1 / s['justa']:.2f} ({s['fonte']}) · odd mínima {s['minima']:.2f}{tarde} · "
              f"stake {stake} · fonte {fonte}{estrela}{mov}{alerta}{' · novo' if s['novo'] else ''}")


def chave_consenso(s):
    return f"{s['evento']}|{s['selecao']}|{s['inicio']}"


def guardar_consenso(itens, agora):
    """Guarda cada recolha do preço justo de consenso, para medir o CLV sem Pinnacle (dados/consenso.json).

    Só escreve quando há uma recolha nova; esquece os jogos com mais de 4 dias. Devolve, por seleção, a
    probabilidade da recolha anterior à atual (para o movimento do consenso)."""
    ficheiro = banca.DADOS / "consenso.json"
    hist = json.loads(ficheiro.read_text()) if ficheiro.exists() else {}
    mudou, anteriores = False, {}
    for s in itens:
        if not s.get("recolha"):
            continue
        pontos = hist.setdefault(chave_consenso(s), [])
        antes = [(t, p) for t, p in pontos if t < s["recolha"]]
        if antes:
            anteriores[chave_consenso(s)] = max(antes)[1]
        if all(t != s["recolha"] for t, _ in pontos):
            pontos.append([s["recolha"], round(s["justa"], 4)])
            mudou = True
    for chave in [k for k in hist if datetime.fromisoformat(k.rsplit("|", 1)[1]) < agora - timedelta(days=4)]:
        del hist[chave]
        mudou = True
    if mudou:
        ficheiro.write_text(json.dumps(hist, ensure_ascii=False, sort_keys=True, indent=0))
    return anteriores


def fecho_consenso(r, hist):
    """(prob, recolha, antecedência em h) da última recolha do consenso posterior à que escolheu a recomendação e
    anterior ao início. Sem recolha posterior, ou só com uma a mais de 6 h do início, não há fecho."""
    base = r.get("recolha") or r.get("hora") or ""
    inicio = datetime.fromisoformat(r["inicio"])
    pontos = [(t, p) for t, p in hist.get(chave_consenso(r), [])
              if t > base and datetime.fromisoformat(t) < inicio]
    if not pontos:
        return None
    t, p = max(pontos)
    antecedencia = (inicio - datetime.fromisoformat(t)).total_seconds() / 3600
    return None if antecedencia > 6 else (p, t, antecedencia)


def cmd_mercados(args):
    """Preço justo dos mercados secundários do ténis (sets, total e handicap de jogos), derivado do preço justo do
    vencedor por um modelo de pontos. É preço de modelo, não de mercado: só serve para responder a perguntas como
    'e o 2-0?' e para recusar valor falso; aposta-se só com uma odd real acima da mínima (limiares altos)."""
    cfg = banca.config()
    nomes, competicao, recolha, inicio = ["A", "B"], args.competicao, None, None
    if args.alvo:
        s = next((x for x in json.loads((banca.DADOS / "alvos.json").read_text())["itens"] if x["id"] == args.alvo),
                 None)
        if not s or s["mercado"] != "h2h" or s["desporto"] != "Ténis":
            sys.exit(f"O alvo {args.alvo} não existe em alvos.json ou não é um vencedor de ténis.")
        outro = next(n for n in s["evento"].split(" vs ") if n != s["selecao"])
        nomes, p, competicao = [s["selecao"], outro], s["justa"], s["competicao"]
        recolha, inicio = s.get("recolha"), s["inicio"]
    elif args.odds:
        p = justas_consenso(args.odds)[0]
    elif args.prob:
        p = args.prob
    else:
        sys.exit("Indica --alvo N, --odds A B ou --prob P (probabilidade justa de o 1.º jogador vencer).")
    nivel, circ = (args.nivel, "nível manual") if args.nivel else tenis.nivel(cfg, competicao)
    sigma = cfg.get("tenis_sigma", 0.065)
    m = tenis.mercados(tenis.distribuicao(p, nivel, sigma))
    idade = banca.idade_horas(recolha)
    antecedencia = None
    if recolha and inicio:
        antecedencia = (datetime.fromisoformat(inicio) - datetime.fromisoformat(recolha)).total_seconds() / 3600
    a, b = nomes

    largura = max(len(n) for n in nomes) + 24

    def linha(rotulo, prob, mercado):
        if prob <= 0:
            return f"  {rotulo:{largura}} {banca.pct(prob):>6}"
        ev = banca.ev_minimo(cfg, "modelo", prob, competicao, idade, mercado, rotulo, antecedencia)
        minima = (1 + ev) / prob
        fora = "" if cfg["odd_minima"] <= minima <= cfg["odd_maxima"] else " (fora do intervalo)"
        return f"  {rotulo:{largura}} {banca.pct(prob):>6}  justa {1 / prob:5.2f}  mínima {minima:5.2f}{fora}"

    print(f"{a} vs {b} — {competicao or 'sem competição'} ({circ}, L {nivel:g}, σ {sigma:g}) · {a} vence "
          f"{banca.pct(m['vence'])} (justa {1 / m['vence']:.2f})")
    print("Preço de MODELO calibrado ao vencedor, não de mercado. Se a Pinnacle tiver este mercado, vale a Pinnacle. "
          "Só há aposta com odd real ≥ mínima numa das tuas casas.")
    print("Resultado em sets:")
    for rotulo, chave in ((f"{a} 2-0", "2-0"), (f"{a} 2-1", "2-1"), (f"{b} 2-1", "1-2"), (f"{b} 2-0", "0-2")):
        print(linha(rotulo, m["sets"].get(chave, 0.0), "sets"))
    print(linha(f"{a} ganha pelo menos 1 set", m["a_ganha_set"], "sets"))
    print(linha(f"{b} ganha pelo menos 1 set", m["b_ganha_set"], "sets"))
    print(f"Total de jogos (média prevista {m['media_jogos']:.1f}):".replace(".", ","))
    for d in (-3, -2, -1, 0, 1):
        limite = math.floor(m["media_jogos"]) + d + 0.5
        acima = tenis.over(m, limite)
        print(linha(f"Mais de {limite:g}", acima, "jogos") + "   |" + linha(f"Menos de {limite:g}", 1 - acima, "jogos"))
    fav, azar, sinal = (a, b, 1) if m["vence"] >= 0.5 else (b, a, -1)
    print(f"Handicap de jogos ({fav} favorito):")
    for x in (1.5, 2.5, 3.5, 4.5, 5.5):
        cobre = sum(v for k, v in m["diferenca"].items() if sinal * k > x)
        print(linha(f"{fav} -{x:g}", cobre, "handicap") + "   |" + linha(f"{azar} +{x:g}", 1 - cobre, "handicap"))


def cmd_ev(args):
    """EV de uma odd (normal ou aumentada) contra o preço justo, ou o valor de uma freebet."""
    cfg = banca.config()
    p = args.prob if args.prob else 1 / args.justa
    if args.freebet:
        print(f"Freebet a {args.odd:.2f}: vale {banca.pct(p * (args.odd - 1))} do valor nominal "
              "(p justa × (odd − 1); a stake não volta). Odds mais altas aproveitam melhor a freebet, "
              "mas respeita a faixa de odds que escolheste para freebets.")
        return
    ev, minimo = p * args.odd - 1, banca.ev_minimo(cfg, args.fonte, p)
    print(f"EV {banca.pct(ev, True)} (odd {args.odd:.2f} contra justa {1 / p:.2f}) · mínimo {banca.pct(minimo)} "
          f"({args.fonte}) → odd mínima {(1 + minimo) / p:.2f}: {'passa' if ev >= minimo else 'não passa'}")


def cmd_fontes(_):
    """Diz que fontes de odds e de dados estão acessíveis a partir deste ambiente, agora."""
    if not os.environ.get("ODDS_API_KEY"):
        print("The Odds API: sem ODDS_API_KEY")
    else:
        try:
            pedir("sports")
            print(f"The Odds API: ok ({restantes} créditos)")
        except Exception as e:
            print(f"The Odds API: indisponível ({e})")
    for nome, url in (("ESPN", "https://site.api.espn.com/apis/site/v2/sports/soccer/por.1/scoreboard"),
                      ("MLB Stats", "https://statsapi.mlb.com/api/v1/sports"),
                      ("GitHub ténis (tennisexplorer)", FONTES["tenis"]),
                      ("GitHub futebol (Pinnacle/Bet365)", FONTES["futebol"])):
        try:
            baixar(url)
            print(f"{nome}: ok")
        except Exception as e:
            print(f"{nome}: indisponível ({e})")


def cmd_desportos(_):
    for d in pedir("sports"):
        if d["group"] in GRUPOS and d["active"]:
            print(f"{d['key']:45} {d['title']}")


def cmd_valor(args):
    cfg, agora = banca.config(), datetime.now(timezone.utc)
    janela = {"commenceTimeFrom": agora.strftime(FMT),
              "commenceTimeTo": (agora + timedelta(hours=args.horas)).strftime(FMT)}
    ficheiro = banca.DADOS / "varredura.json"
    anterior = {}
    if ficheiro.exists():
        anterior = {(s["evento_id"], s["mercado"], s["selecao"]): s["justa"]
                    for s in json.loads(ficheiro.read_text())["itens"]}
    itens = []
    for chave in competicoes(cfg):
        if not pedir(f"sports/{chave}/events", **janela):  # grátis: só gasta créditos onde há jogos
            continue
        if restantes is not None and restantes < cfg["creditos_reserva"]:
            print("Créditos abaixo da reserva: varredura interrompida.", file=sys.stderr)
            break
        for e in pedir(f"sports/{chave}/odds", regions=cfg["regioes"], markets=cfg["mercados"],
                       oddsFormat="decimal", **janela):
            for s in analisar(e, cfg["casas_excluidas"], agora):
                antes = anterior.get((e["id"], s["mercado"], s["selecao"]))
                s.update(id=len(itens) + 1, sport_key=chave, evento_id=e["id"], inicio=e["commence_time"],
                         evento=f"{e['home_team']} vs {e['away_team']}", competicao=e["sport_title"],
                         mov_pp=None if antes is None else round((s["justa"] - antes) * 100, 1))
                itens.append(s)
    ficheiro.write_text(json.dumps({"hora": agora.strftime(FMT), "itens": itens}, ensure_ascii=False, indent=1))
    def minimo(s):
        if args.limiar is not None:
            return args.limiar / 100
        return banca.ev_minimo(cfg, s["fonte"], s["justa"], s["competicao"])

    candidatas = sorted((s for s in itens if s["valor"] >= minimo(s)
                         and cfg["odd_minima"] <= s["melhor"] <= cfg["odd_maxima"]), key=lambda s: -s["valor"])
    print(f"{len(itens)} seleções analisadas; {len(candidatas)} com valor.")
    for s in candidatas:
        hora = datetime.fromisoformat(s["inicio"]).astimezone(LISBOA)
        minima = (1 + minimo(s)) / s["justa"]
        mov = "" if s["mov_pp"] is None else f" · mov {s['mov_pp']:+.1f} pp".replace(".", ",")
        idade = "" if s["idade_min"] is None else f" (há {s['idade_min']} min)"
        print(f"[{s['id']}] {hora:%d/%m %H:%M} {s['evento']} ({s['competicao']}) · {s['mercado']} {s['selecao']} · "
              f"justa {1 / s['justa']:.2f} ({banca.pct(s['justa'])}, {s['fonte']}) · melhor {s['melhor']:.2f} @ "
              f"{s['casa']}{idade} · EV {banca.pct(s['valor'], True)} · odd mínima {minima:.2f}{mov}")


def cmd_odds(args):
    cfg, agora = banca.config(), datetime.now(timezone.utc)
    eventos = pedir(f"sports/{args.desporto}/odds", regions=cfg["regioes"], markets=args.mercados,
                    oddsFormat="decimal", commenceTimeFrom=agora.strftime(FMT),
                    commenceTimeTo=(agora + timedelta(hours=args.horas)).strftime(FMT))
    for e in sorted(eventos, key=lambda e: e["commence_time"]):
        hora = datetime.fromisoformat(e["commence_time"]).astimezone(LISBOA)
        print(f"\n{hora:%d/%m %H:%M}  {e['home_team']} vs {e['away_team']}  ({e['sport_title']})")
        for s in analisar(e, cfg["casas_excluidas"], agora):
            print(f"  {s['mercado']:7} {s['selecao']:30} justa {1 / s['justa']:5.2f} ({banca.pct(s['justa']):>6}, "
                  f"{s['fonte']})  melhor {s['melhor']:5.2f} @ {s['casa']:16} valor {banca.pct(s['valor'], True)}")
    if not eventos:
        print(f"Sem eventos de {args.desporto} nas próximas {args.horas} h.")


def por_desporto(recs):
    grupos = defaultdict(list)
    for r in recs:
        grupos[r["sport_key"]].append(r)
    return grupos.items()


def cmd_fecho(args):
    """Guarda a probabilidade justa perto do início: é a referência do CLV."""
    cfg, agora = banca.config(), datetime.now(timezone.utc)
    recs = banca.ler("recomendacoes.csv")
    alvo = [r for r in recs if r["evento_id"] and not r["prob_fecho"]
            and (r["ref"] in args.ref if args.ref else -10 <= minutos(r["inicio"], agora) <= args.minutos)]
    fechos = {}
    for chave, grupo in por_desporto(alvo):
        eventos = {e["id"]: e for e in pedir(
            f"sports/{chave}/odds", regions=cfg["regioes"], oddsFormat="decimal",
            markets=",".join(sorted({r["mercado"] for r in grupo})),
            eventIds=",".join(sorted({r["evento_id"] for r in grupo})))}
        for r in grupo:
            e = eventos.get(r["evento_id"])
            s = next((s for s in analisar(e, cfg["casas_excluidas"], agora)
                      if s["mercado"] == r["mercado"] and s["selecao"] == r["selecao"]), None) if e else None
            if not s:
                print(f"{r['ref']}: sem odds de fecho (jogo já começou ou mercado fechado)")
                continue
            r["prob_fecho"] = fechos[r["ref"]] = f"{s['justa']:.4f}"
            r["fecho_fonte"] = "pinnacle" if s["fonte"] == "pinnacle" else "média das casas"
            print(f"{r['ref']}: fecho {1 / s['justa']:.2f} ({s['fonte']}) · odd {r['odd']} · "
                  f"CLV {banca.pct(banca.clv(r['odd'], s['justa']), True)}")
    fechos.update(fecho_github(recs, args, agora))
    if fechos:
        banca.escrever("recomendacoes.csv", recs, banca.REC)
        _, apostas = banca.carregar()
        for a in apostas:
            if a.get("ref") in fechos and not a.get("prob_fecho"):
                a["prob_fecho"] = fechos[a["ref"]]
        banca.gravar(apostas)
    elif not alvo:
        print("Nenhuma recomendação a começar dentro da janela.")


def fecho_github(recs, args, agora):
    """Fecho das recomendações do GitHub (sem Pinnacle): a última recolha do consenso antes do início.

    Só fica gravado depois de o jogo começar, para não perder uma recolha que ainda chegue antes do início."""
    alvo = [r for r in recs if r.get("sport_key") == "github" and not r["prob_fecho"]
            and r.get("fecho_fonte") != "não medido" and r.get("tipo") != "sombra"
            and (r["ref"] in args.ref if args.ref else minutos(r["inicio"], agora) <= args.minutos)]
    if not alvo:
        return {}
    try:
        itens, _ = alvos_tenis()
        guardar_consenso(itens, agora)
    except Exception as e:  # sem rede: usa só as recolhas já guardadas
        print(f"(fonte de ténis indisponível: {e}; uso as recolhas guardadas)")
    ficheiro = banca.DADOS / "consenso.json"
    hist = json.loads(ficheiro.read_text()) if ficheiro.exists() else {}
    fechos = {}
    for r in alvo:
        f = fecho_consenso(r, hist)
        if not f:
            print(f"{r['ref']}: sem recolha do consenso posterior à recomendação e a menos de 6 h do início")
            if minutos(r["inicio"], agora) <= 0:  # já começou: não aparece outra recolha antes do início
                r["fecho_fonte"] = "não medido"
                fechos[r["ref"]] = ""
            continue
        p, t, antecedencia = f
        mov = (p - float(r["prob_justa"])) * 100
        horas, pp = f"{antecedencia:.1f}".replace(".", ","), f"{mov:+.1f}".replace(".", ",")
        texto = (f"{r['ref']}: fecho {1 / p:.2f} (consenso, {horas} h antes do início) · odd {r['odd']} · "
                 f"CLV {banca.pct(banca.clv(r['odd'], p), True)} · consenso {pp} pp desde a recomendação")
        if minutos(r["inicio"], agora) > 0:
            aviso = " ⚠ andou mais de 2 pp contra a seleção: cancelar se ainda não apostaste" if mov < -2 else ""
            print(texto + " — provisório: grava-se depois do início" + aviso)
            continue
        r.update(prob_fecho=f"{p:.4f}", fecho_fonte="consenso", fecho_antecedencia_h=f"{antecedencia:.1f}")
        fechos[r["ref"]] = r["prob_fecho"]
        print(texto)
    return fechos


def resultado_selecao(r, jogo):
    """ganha, perdida ou nula para uma recomendação h2h, totals ou spreads, a partir do resultado final."""
    pontos = {s["name"]: float(s["score"]) for s in jogo["scores"]}
    casa, fora = pontos[jogo["home_team"]], pontos[jogo["away_team"]]
    ponto = float(r["ponto"]) if r["ponto"] else None
    nome = r["selecao"] if ponto is None else r["selecao"].rsplit(" ", 1)[0]
    if r["mercado"] == "h2h":
        if casa == fora:
            return "ganha" if nome == "Draw" else "perdida"
        return "ganha" if nome == (jogo["home_team"] if casa > fora else jogo["away_team"]) else "perdida"
    if r["mercado"] == "totals":
        diferenca = (casa + fora - ponto) * (1 if nome == "Over" else -1)
    elif r["mercado"] == "spreads":
        proprio, outro = (casa, fora) if nome == jogo["home_team"] else (fora, casa)
        diferenca = proprio + ponto - outro
    else:
        return ""
    return "ganha" if diferenca > 0 else "perdida" if diferenca < 0 else "nula"


def cmd_resultados(_):
    agora = datetime.now(timezone.utc)
    recs = banca.ler("recomendacoes.csv")
    alvo = [r for r in recs if r["evento_id"] and not r["resultado"] and minutos(r["inicio"], agora) < -120]
    mudou = False
    for chave, grupo in por_desporto(alvo):
        jogos = {j["id"]: j for j in pedir(f"sports/{chave}/scores", daysFrom=3,
                                            eventIds=",".join(sorted({r["evento_id"] for r in grupo})))}
        for r in grupo:
            j = jogos.get(r["evento_id"])
            if j and j.get("completed") and j.get("scores"):
                r["resultado"] = resultado_selecao(r, j)
                mudou = mudou or bool(r["resultado"])
                print(f"{r['ref']}: {r['evento']} — {r['selecao']}: {r['resultado'] or 'mercado não suportado'}")
            else:
                print(f"{r['ref']}: sem resultado na API (liquida à mão se já terminou)")
    if mudou:
        banca.escrever("recomendacoes.csv", recs, banca.REC)
    if not alvo:
        print("Nenhuma recomendação por liquidar.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("desportos")
    sub.add_parser("resultados")
    sub.add_parser("fontes")
    a = sub.add_parser("alvos")
    a.add_argument("--horas", type=int, default=36)
    a.add_argument("--desporto", nargs="*", choices=["tenis", "futebol"], help="por omissão, os ativos em config.json")
    a.add_argument("--challengers", action="store_true", help="incluir Challengers (ou incluir_challengers)")
    a.add_argument("--itf", action="store_true", help="incluir ITF (ou incluir_itf; por omissão, de fora)")
    m = sub.add_parser("mercados")
    m.add_argument("--alvo", type=int, help="número de um alvo de vencedor no ténis (último 'alvos')")
    m.add_argument("--odds", type=float, nargs=2, metavar=("ODD_A", "ODD_B"), help="odds médias do vencedor")
    m.add_argument("--prob", type=float, help="probabilidade justa de o 1.º jogador vencer")
    m.add_argument("--competicao", default="", help="ex.: 'ATP Hangzhou', 'WTA Seoul', 'ATP Genoa challenger'")
    m.add_argument("--nivel", type=float, help="soma das probabilidades de ganhar o ponto no serviço (ex.: 1.25)")
    e = sub.add_parser("ev")
    e.add_argument("--odd", type=float, required=True, help="odd da casa (normal, aumentada ou da freebet)")
    justa = e.add_mutually_exclusive_group(required=True)
    justa.add_argument("--justa", type=float, help="odd justa")
    justa.add_argument("--prob", type=float, help="probabilidade justa")
    e.add_argument("--fonte", default="pinnacle", choices=["pinnacle", "consenso"])
    e.add_argument("--freebet", action="store_true", help="valor esperado de uma freebet a esta odd")
    v = sub.add_parser("valor")
    v.add_argument("--horas", type=int, default=36)
    v.add_argument("--limiar", type=float, help="EV mínimo em %% (por omissão, o de config.json)")
    o = sub.add_parser("odds")
    o.add_argument("desporto", help="chave de 'desportos', ex.: basketball_nba")
    o.add_argument("--horas", type=int, default=36)
    o.add_argument("--mercados", default="h2h", help="h2h,spreads,totals")
    f = sub.add_parser("fecho")
    f.add_argument("--minutos", type=int, default=90, help="recomendações que começam dentro deste prazo")
    f.add_argument("--ref", nargs="*", help="só estas recomendações, a qualquer hora")
    args = p.parse_args()
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
