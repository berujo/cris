import argparse
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import banca  # noqa: E402
import odds  # noqa: E402

CFG = {"banca_inicial": 20.0, "fracao_kelly": 0.25, "teto_stake_pct": 10, "teto_multipla_pct": 5,
       "stop_loss_pct": 50, "stake_minima": 0.10, "arredondamento": 0.10, "ev_minimo_pct": 3,
       "ev_minimo_consenso_pct": 5, "odd_minima": 1.40, "odd_maxima": 4.00, "ajuste_max_pp": 3,
       "clv_minimo_amostra": 3}


def aposta(estado, stake, odd, lucro):
    return {"id": "1", "data": "2026-09-24", "estado": estado, "stake": str(stake), "odd": str(odd),
            "lucro": str(lucro)}


def rec(**campos):
    r = {c: "" for c in banca.REC}
    r.update({"tipo": "simples", "fonte_justa": "pinnacle", **campos})
    return r


class TestBanca(unittest.TestCase):
    def test_kelly_fracionado(self):
        # EV 10% a odd 2,00 -> Kelly 10% -> 1/4 = 2,5% de 20 € = 0,50 €
        self.assertEqual(banca.calcular_stake(CFG, 20, 0.55, 2.0)[0], 0.50)

    def test_teto(self):
        self.assertEqual(banca.calcular_stake(CFG, 20, 0.95, 3.0)[0], 2.00)
        self.assertEqual(banca.calcular_stake(CFG, 20, 0.95, 3.0, multipla=True)[0], 1.00)

    def test_sem_valor_e_abaixo_do_minimo(self):
        self.assertEqual(banca.calcular_stake(CFG, 20, 0.45, 2.0)[0], 0.0)
        self.assertEqual(banca.calcular_stake(CFG, 20, 0.505, 2.0)[0], 0.0)  # 0,05 € < mínimo

    def test_liquidar(self):
        a = aposta("pendente", 1.0, 2.5, "")
        banca.liquidar(a, "ganha", None)
        self.assertEqual(a["lucro"], "1.50")
        banca.liquidar(a, "perdida", None)
        self.assertEqual(a["lucro"], "-1.00")

    def test_resumo(self):
        apostas = [aposta("ganha", 1, 2.0, 1.0), aposta("perdida", 1, 2.0, -1.0),
                   aposta("ganha", 2, 1.5, 1.0), aposta("nula", 1, 2.0, 0.0)]
        n, apostado, lucro, yld, acerto = banca.resumo(apostas)
        self.assertEqual((n, apostado, lucro), (4, 4.0, 1.0))
        self.assertAlmostEqual(yld, 0.25)
        self.assertAlmostEqual(acerto, 2 / 3)

    def test_validar_aplica_as_regras(self):
        ok = rec(odd="2.10", prob_justa="0.49", prob_final="0.50")  # EV +5%, ajuste +1 pp
        self.assertEqual(banca.validar(CFG, 20, ok), (0.20, None))
        casos = {"ajuste": rec(odd="2.10", prob_justa="0.45", prob_final="0.50"),
                 "fora do intervalo": rec(odd="4.50", prob_justa="0.24", prob_final="0.25"),
                 "abaixo do mínimo de 3": rec(odd="2.00", prob_justa="0.51", prob_final="0.51"),
                 "abaixo do mínimo de 5": rec(odd="2.10", prob_justa="0.49", prob_final="0.49",
                                             fonte_justa="consenso")}
        for motivo, r in casos.items():
            self.assertIn(motivo, banca.validar(CFG, 20, r)[1])

    def test_regra_de_paragem(self):
        maus = [rec(odd="2.0", prob_fecho="0.49") for _ in range(3)]
        self.assertTrue(banca.regra_paragem(CFG, maus))
        self.assertFalse(banca.regra_paragem(CFG, maus[:2]))  # amostra ainda curta
        self.assertFalse(banca.regra_paragem(CFG, [rec(odd="2.0", prob_fecho="0.52") for _ in range(3)]))


class TestOdds(unittest.TestCase):
    def test_shin_igual_a_biblioteca_de_referencia(self):
        # valores da biblioteca 'shin' (PyPI), calculados à parte
        for cotacoes, esperado in (([2.6, 2.4, 4.3], [0.372994, 0.404779, 0.222227]),
                                   ([1.22, 6.5, 13.0], [0.797081, 0.139194, 0.063725]),
                                   ([1.25, 4.2], [0.780952, 0.219048])):
            for p, e in zip(odds.shin(cotacoes), esperado):
                self.assertAlmostEqual(p, e, places=5)

    def test_shin_favorece_o_favorito(self):
        cotacoes = [1.22, 6.5, 13.0]
        proporcional = [(1 / o) / sum(1 / x for x in cotacoes) for o in cotacoes]
        self.assertGreater(odds.shin(cotacoes)[0], proporcional[0])

    def test_valor_contra_pinnacle_sem_exchanges(self):
        agora = datetime(2026, 9, 25, 12, tzinfo=timezone.utc)
        evento = {"bookmakers": [
            {"key": "pinnacle", "title": "Pinnacle", "last_update": "2026-09-25T11:58:00Z",
             "markets": [{"key": "h2h", "outcomes": [{"name": "A", "price": 1.95}, {"name": "B", "price": 1.95}]}]},
            {"key": "unibet_eu", "title": "Unibet", "last_update": "2026-09-25T11:50:00Z",
             "markets": [{"key": "h2h", "outcomes": [{"name": "A", "price": 2.10}, {"name": "B", "price": 1.75}]}]},
            {"key": "betfair_ex_eu", "title": "Betfair", "last_update": "2026-09-25T11:59:00Z",
             "markets": [{"key": "h2h", "outcomes": [{"name": "A", "price": 2.30}, {"name": "B", "price": 1.80}]}]},
        ]}
        valor = {s["selecao"]: s for s in odds.analisar(evento, excluir=["betfair_ex_eu"], agora=agora)}
        self.assertEqual((valor["A"]["casa"], valor["A"]["idade_min"], valor["A"]["fonte"]), ("Unibet", 10, "pinnacle"))
        self.assertAlmostEqual(valor["A"]["valor"], 0.05)

    def test_totais_sem_pinnacle(self):
        evento = {"bookmakers": [
            {"key": k, "title": k, "markets": [{"key": "totals", "outcomes": [
                {"name": "Over", "price": o, "point": 2.5}, {"name": "Under", "price": u, "point": 2.5}]}]}
            for k, o, u in (("x", 1.80, 2.00), ("y", 1.90, 1.90))
        ]}
        r = odds.analisar(evento)
        self.assertEqual({s["selecao"] for s in r}, {"Over 2.5", "Under 2.5"})
        self.assertTrue(all(s["fonte"] == "média de 2 casas" and s["ponto"] == 2.5 for s in r))

    def test_resultado_selecao(self):
        jogo = {"home_team": "A", "away_team": "B", "scores": [{"name": "A", "score": "2"},
                                                                {"name": "B", "score": "1"}]}
        casos = [("h2h", "A", "", "ganha"), ("h2h", "Draw", "", "perdida"),
                 ("totals", "Over 2.5", "2.5", "ganha"), ("totals", "Under 3", "3", "nula"),
                 ("spreads", "B 1.5", "1.5", "ganha"), ("spreads", "A -1", "-1", "nula")]
        for mercado, selecao, ponto, esperado in casos:
            r = rec(mercado=mercado, selecao=selecao, ponto=ponto)
            self.assertEqual(odds.resultado_selecao(r, jogo), esperado, selecao)


def evento(inicio, pinnacle, unibet):
    return {"id": "ev1", "sport_title": "EPL", "home_team": "A", "away_team": "B", "commence_time": inicio,
            "bookmakers": [
                {"key": "pinnacle", "title": "Pinnacle", "markets": [{"key": "h2h", "outcomes": [
                    {"name": "A", "price": pinnacle[0]}, {"name": "Draw", "price": pinnacle[1]},
                    {"name": "B", "price": pinnacle[2]}]}]},
                {"key": "unibet_eu", "title": "Unibet", "markets": [{"key": "h2h", "outcomes": [
                    {"name": "A", "price": unibet[0]}, {"name": "Draw", "price": unibet[1]},
                    {"name": "B", "price": unibet[2]}]}]}]}


class TestDiaCompleto(unittest.TestCase):
    """Varredura → recomendação → aposta → fecho → resultado → avaliação, com uma API falsa."""

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        cfg = json.loads((RAIZ / "dados" / "config.json").read_text())
        cfg["desportos"]["futebol"] = "2000-01-01"  # este teste é sobre o fluxo, não sobre o foco
        (self.pasta / "config.json").write_text(json.dumps(cfg))
        self.dados_originais, banca.DADOS = banca.DADOS, self.pasta
        self.pedir_original = odds.pedir
        self.inicio = (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime(odds.FMT)
        self.pinnacle = (2.00, 3.60, 3.90)

        def pedir(caminho, **params):
            if caminho == "sports":
                return [{"key": "soccer_epl", "active": True, "group": "Soccer", "title": "EPL"},
                        {"key": "tennis_atp_tokyo", "active": True, "group": "Tennis", "title": "ATP Tóquio"}]
            if caminho.endswith("/events"):
                return [{"id": "ev1"}] if "soccer_epl" in caminho else []
            if caminho == "sports/soccer_epl/odds":
                return [evento(self.inicio, self.pinnacle, (2.20, 3.40, 3.50))]
            if caminho == "sports/soccer_epl/scores":
                return [{"id": "ev1", "completed": True, "home_team": "A", "away_team": "B",
                         "scores": [{"name": "A", "score": "1"}, {"name": "B", "score": "0"}]}]
            raise AssertionError(f"pedido inesperado: {caminho}")

        odds.pedir = pedir

    def tearDown(self):
        banca.DADOS, odds.pedir = self.dados_originais, self.pedir_original
        shutil.rmtree(self.pasta)

    def correr(self, funcao, *args):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            funcao(*args)
        return saida.getvalue()

    def test_dia_completo(self):
        saida = self.correr(odds.cmd_valor, argparse.Namespace(horas=36, limiar=None))
        self.assertIn("1 com valor", saida)  # só A @ 2,20 na Unibet bate a Pinnacle por ≥ 3%
        item = json.loads((self.pasta / "varredura.json").read_text())["itens"]
        a = next(s for s in item if s["selecao"] == "A")

        cfg, apostas = banca.carregar()
        campos = {c: None for c in banca.REC}
        campos.update(item=a["id"], prob_final=f"{a['justa']:.4f}", confianca="média")
        ns = argparse.Namespace(**campos)
        saida = self.correr(banca.cmd_recomendar, cfg, apostas, ns)
        ref = saida.split(":")[0]
        self.assertTrue(ref.endswith("#1"))

        ns = argparse.Namespace(ref=ref, odd=2.20, stake=0.20, casa="Betano", estado="pendente", lucro=None,
                                **{c: None for c in ("desporto", "competicao", "evento", "mercado", "selecao",
                                                     "prob", "confianca", "data", "notas", "tipo")})
        self.correr(banca.cmd_registar, cfg, apostas, ns)

        self.pinnacle = (1.90, 3.70, 4.20)  # a linha mexeu a favor da aposta: CLV positivo
        saida = self.correr(odds.cmd_fecho, argparse.Namespace(minutos=90, ref=None))
        self.assertIn("CLV +", saida)
        self.assertTrue(banca.ler("apostas.csv")[0]["prob_fecho"])

        recs = banca.ler("recomendacoes.csv")
        recs[0]["inicio"] = "2026-01-01T12:00:00Z"  # o jogo já acabou
        banca.escrever("recomendacoes.csv", recs, banca.REC)
        self.correr(odds.cmd_resultados, None)
        self.assertEqual(banca.ler("recomendacoes.csv")[0]["resultado"], "ganha")

        saida = self.correr(banca.cmd_avaliacao, banca.config(), [], None)
        self.assertIn("CLV médio: +", saida)
        self.assertIn("ROI em papel", saida)
        saida = self.correr(banca.cmd_metricas, *banca.carregar(), None)
        self.assertIn("CLV médio: +", saida)


if __name__ == "__main__":
    unittest.main()


def xlsx(linhas):
    """Um .xlsx mínimo (strings partilhadas), feito só com a biblioteca padrão."""
    import zipfile
    textos, celulas = [], []
    for i, linha in enumerate(linhas, 1):
        cs = []
        for j, v in enumerate(linha):
            ref = f"{chr(65 + j)}{i}"
            if isinstance(v, str):
                textos.append(v)
                cs.append(f'<c r="{ref}" t="s"><v>{len(textos) - 1}</v></c>')
            elif v is not None:
                cs.append(f'<c r="{ref}"><v>{v}</v></c>')
        celulas.append(f'<row r="{i}">{"".join(cs)}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml", f'<worksheet {ns}><sheetData>{"".join(celulas)}</sheetData></worksheet>')
        z.writestr("xl/sharedStrings.xml", f"<sst {ns}>" + "".join(f"<si><t>{t}</t></si>" for t in textos) + "</sst>")
    return b.getvalue()


class TestFontesGithub(unittest.TestCase):
    """Alvos a partir das fontes no GitHub (ténis do tennisexplorer; futebol com Pinnacle e Bet365)."""

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        shutil.copy(RAIZ / "dados" / "config.json", self.pasta)
        self.dados_originais, banca.DADOS = banca.DADOS, self.pasta
        self.baixar_original = odds.baixar
        amanha = datetime.now(timezone.utc) + timedelta(days=1)
        self.tenis = {"last_updated": amanha.strftime("%Y-%m-%dT00:05:00"), "count": 2, "matches": [
            {"tournament": "Chengdu", "time": "12:00", "player1": "Shapovalov D. (7)", "player2": "Griekspoor T.",
             "odds1": 1.67, "odds2": 2.19, "tour": "ATP"},
            {"tournament": "Genoa challenger", "time": "12:00", "player1": "A", "player2": "B",
             "odds1": 1.80, "odds2": 1.95, "tour": "ATP"}]}
        cab = ["league_info", "fixture_name", "starting_at", "Bet365_Match_Odds_Away", "Bet365_Match_Odds_Draw",
               "Bet365_Match_Odds_Home", "Pinnacle_Match_Odds_Away", "Pinnacle_Match_Odds_Draw",
               "Pinnacle_Match_Odds_Home"]
        self.futebol = xlsx([cab, ["La Liga 2", "Girona vs Albacete", amanha.strftime("%Y-%m-%d 18:30:00"),
                                   1.50, 4.2, 5.75, 1.52, 4.47, 5.70]])
        odds.baixar = lambda url: json.dumps(self.tenis).encode() if url == odds.FONTES["tenis"] else self.futebol

    def tearDown(self):
        banca.DADOS, odds.baixar = self.dados_originais, self.baixar_original
        shutil.rmtree(self.pasta)

    def test_futebol_com_rotulos_trocados_na_fonte(self):
        itens, _ = odds.alvos_futebol()
        girona = next(s for s in itens if s["selecao"] == "Girona")  # a coluna "Away" é a equipa da casa
        self.assertAlmostEqual(girona["justa"], odds.shin([1.52, 4.47, 5.70])[0])
        self.assertEqual((girona["odd_fonte"], girona["fonte"]), (1.50, "pinnacle"))
        self.assertEqual({s["selecao"] for s in itens}, {"Girona", "Empate", "Albacete"})

    def test_tenis_hora_da_europa_central_e_sem_cabeca_de_serie(self):
        itens, _ = odds.alvos_tenis()
        s = itens[0]
        self.assertEqual((s["selecao"], s["evento"]), ("Shapovalov D.", "Shapovalov D. vs Griekspoor T."))
        self.assertEqual(datetime.fromisoformat(s["inicio"]).astimezone(odds.HORA_TENNISEXPLORER).hour, 12)

    def test_alvos_e_recomendacao_com_a_odd_da_casa(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            odds.cmd_alvos(argparse.Namespace(horas=72, desporto=None, challengers=False))
        itens = json.loads((self.pasta / "alvos.json").read_text())["itens"]
        self.assertTrue(any("challenger" in s["competicao"] for s in itens))  # incluir_challengers
        self.assertFalse(any(s["desporto"] == "Futebol" for s in itens))  # futebol só a partir de 09/10
        alvo = next(s for s in itens if s["selecao"] == "Griekspoor T.")
        self.assertAlmostEqual(alvo["minima"], 1.05 / alvo["justa"])  # sem Pinnacle, exige 5%

        campos = {c: None for c in banca.REC}
        campos.update(alvo=alvo["id"], confianca="média")
        with self.assertRaises(SystemExit):  # falta a odd encontrada na casa
            banca.cmd_recomendar(banca.config(), [], argparse.Namespace(**campos))
        campos.update(odd=round(alvo["minima"] + 0.05, 2), casa="Betano")
        with contextlib.redirect_stdout(io.StringIO()):
            banca.cmd_recomendar(banca.config(), [], argparse.Namespace(**campos))
        r = banca.ler("recomendacoes.csv")[0]
        self.assertEqual((r["casa"], r["sport_key"], r["fonte_justa"]), ("Betano", "github", "consenso"))
        self.assertEqual(r["prob_final"], r["prob_justa"])  # sem ajuste por defeito

    def test_futebol_so_ligas_europeias_quando_ativo(self):
        cfg = json.loads((self.pasta / "config.json").read_text())
        cfg["desportos"]["futebol"] = "2000-01-01"
        (self.pasta / "config.json").write_text(json.dumps(cfg))
        self.futebol = xlsx([["league_info", "fixture_name", "starting_at", "Pinnacle_Match_Odds_Away",
                              "Pinnacle_Match_Odds_Draw", "Pinnacle_Match_Odds_Home"],
                             ["La Liga 2 - ESP S", "Girona vs Albacete", self.tenis["last_updated"][:10] + " 18:30:00",
                              1.52, 4.47, 5.70],
                             ["Liga BetPlay - COL PA", "Nacional vs Millonarios",
                              self.tenis["last_updated"][:10] + " 23:30:00", 1.81, 3.69, 4.13]])
        with contextlib.redirect_stdout(io.StringIO()):
            odds.cmd_alvos(argparse.Namespace(horas=72, desporto=None, challengers=False))
        itens = json.loads((self.pasta / "alvos.json").read_text())["itens"]
        futebol = [s for s in itens if s["desporto"] == "Futebol"]
        self.assertTrue(futebol)
        self.assertTrue(all("ESP" in s["competicao"] for s in futebol))

    def test_numeros_estaveis_entre_leituras(self):
        ns = argparse.Namespace(horas=72, desporto=["tenis"], challengers=True)
        with contextlib.redirect_stdout(io.StringIO()):
            odds.cmd_alvos(ns)
        primeiro = {s["selecao"]: s["id"] for s in json.loads((self.pasta / "alvos.json").read_text())["itens"]}
        self.tenis["matches"].insert(0, {"tournament": "Chengdu", "time": "11:00", "player1": "Novo A.",
                                         "player2": "Novo B.", "odds1": 1.9, "odds2": 1.9, "tour": "ATP"})
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            odds.cmd_alvos(ns)
        segundo = {s["selecao"]: s["id"] for s in json.loads((self.pasta / "alvos.json").read_text())["itens"]}
        self.assertTrue(all(segundo[k] == v for k, v in primeiro.items()))
        self.assertEqual(segundo["Novo A."], max(primeiro.values()) + 1)
        self.assertIn("2 novos", saida.getvalue())

    def test_ler_xlsx(self):
        self.assertEqual(odds.ler_xlsx(xlsx([["a", "b"], ["x", 1.5]])), [{"a": "x", "b": "1.5"}])


import tenis  # noqa: E402

CFG_NOVO = dict(CFG, consenso_alpha=0.02, recolha_velha_h=3, recolha_longe_h=12, recolha_extra_pct=2,
                ev_extra_pct={r"\bitf\b": 3}, ev_extra_azarao_pct={"challenger": 1}, ev_suspeito_pct=15,
                ev_secundarios_pct={"sets": 8, "sets_3": 10, "jogos": 6, "handicap": 6},
                calibracao_ev={"k_prior": {"pinnacle": 0.7, "consenso": 0.5, "modelo": 0.5}, "n_prior": 50})


class TestLimiaresEStakes(unittest.TestCase):
    """Melhorias de 25/09/2026 — ver reports/Melhorias do agente de apostas.md."""

    def test_limiar_contra_consenso(self):
        c = CFG_NOVO
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.60), 0.05)  # piso de 5% nos favoritos
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.25), 0.02 / 0.23)  # Kaunitz nos azarões
        self.assertAlmostEqual(banca.ev_minimo(c, "pinnacle", 0.25), 0.03)
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.60, idade_h=4), 0.07)  # recolha velha
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.60, antecedencia_h=13), 0.07)  # longe do início
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.45, "ATP Genoa challenger"), 0.06)
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.60, "ATP Genoa challenger"), 0.05)
        self.assertAlmostEqual(banca.ev_minimo(c, "consenso", 0.60, "ITF M25 Porto"), 0.08)
        self.assertAlmostEqual(banca.ev_minimo(c, "modelo", 0.4, mercado="sets", selecao="A 2-0"), 0.08)
        self.assertAlmostEqual(banca.ev_minimo(c, "modelo", 0.2, mercado="sets", selecao="B 2-1"), 0.10)
        self.assertAlmostEqual(banca.ev_minimo(c, "modelo", 0.5, mercado="jogos"), 0.06)
        self.assertAlmostEqual(banca.ev_minimo(CFG, "consenso", 0.25), 0.05)  # sem as chaves novas: como antes

    def test_stake_sobre_o_ev_calibrado(self):
        self.assertEqual(banca.calibracao(CFG_NOVO, "consenso", []), (0.5, 0.0, 0))
        self.assertEqual(banca.calibracao(CFG_NOVO, "pinnacle", [])[:2], (0.7, 0.0))
        self.assertEqual(banca.calibracao(CFG, "consenso", []), (1.0, 0.0, 0))
        # EV 10% a odd 2,00 com metade do EV: 1/4 de Kelly = 1,25% de 20 € = 0,25 € → 0,20 €
        self.assertEqual(banca.calcular_stake(CFG_NOVO, 20, 0.55, 2.0, calib=(0.5, 0.0))[0], 0.20)
        # O fecho confirma todo o EV: k sobe do prior (0,5) em direção a 1, com peso n/(n + 50)
        recs = [rec(odd=f"{o:.2f}", prob_justa="0.5", prob_fecho="0.5", fonte_justa="consenso")
                for o in (2.1, 2.2, 2.3, 2.4) * 25]
        k, a, n = banca.calibracao(CFG_NOVO, "consenso", recs)
        self.assertEqual(n, 100)
        self.assertAlmostEqual(k, (100 / 150) * 1.0 + (50 / 150) * 0.5)
        self.assertAlmostEqual(a, 0.0)

    def test_filtros_de_armadilha_na_validacao(self):
        c = dict(CFG_NOVO, teto_exposicao_pct=25)
        base = {"prob_justa": "0.50", "prob_final": "0.50"}
        suspeita = rec(odd="2.40", **base)  # EV +20%
        self.assertIn("suspeito", banca.validar(c, 20, suspeita)[1])
        self.assertIsNone(banca.validar(c, 20, suspeita, confirmado=True)[1])
        so_uma = rec(odd="2.08", **base)  # EV +4%
        self.assertIn("só esta casa", banca.validar(c, 20, so_uma, segunda_odd=2.00)[1])
        self.assertIsNone(banca.validar(c, 20, so_uma, segunda_odd=2.07)[1])
        subida = rec(odd="2.10", prob_justa="0.49", prob_final="0.50")
        self.assertIn("ajuste positivo", banca.validar(c, 20, subida, ajuste_positivo=False)[1])
        normal = rec(odd="2.20", **base)  # EV +10%: 0,40 € sem teto
        self.assertEqual(banca.validar(c, 20, normal, exposicao=4.8), (0.20, None))
        self.assertEqual(banca.validar(c, 20, normal, exposicao=5.0), (0.0, None))  # sem margem: stake 0

    def test_freebet(self):
        a = aposta("pendente", 1.0, 3.0, "")
        a["tipo"] = "freebet"
        banca.liquidar(a, "perdida", None)
        self.assertEqual(a["lucro"], "0.00")
        banca.liquidar(a, "ganha", None)
        self.assertEqual(a["lucro"], "2.00")
        self.assertEqual(banca.resumo([a])[1], 0.0)  # a stake da freebet não conta como dinheiro apostado

    def test_preco_justo_conservador(self):
        cotacoes = [1.67, 2.19]
        potencia = odds.potencia(cotacoes)
        self.assertAlmostEqual(sum(potencia), 1.0)
        for c, s, p in zip(odds.justas_consenso(cotacoes), odds.shin(cotacoes), potencia):
            self.assertEqual(c, min(s, p))


class TestMercadosTenis(unittest.TestCase):
    def test_modelo_de_pontos(self):
        self.assertAlmostEqual(tenis.p_jogo(0.64), 0.8126, places=4)
        iguais = tenis.mercados(tenis.distribuicao(0.5, 1.28, sigma=0))  # pA = pB = 0,64
        self.assertAlmostEqual(iguais["media_jogos"], 25.683, places=2)
        m = tenis.mercados(tenis.distribuicao(0.60, 1.22))
        self.assertAlmostEqual(m["vence"], 0.60, places=3)
        self.assertAlmostEqual(m["sets"]["2-0"], 0.369, places=2)
        self.assertAlmostEqual(sum(m["sets"].values()), 1.0)
        puro = tenis.mercados(tenis.distribuicao(0.60, 1.22, sigma=0))
        self.assertLess(puro["sets"]["2-0"], m["sets"]["2-0"])  # o modelo puro subestima os 2-0
        self.assertGreater(puro["media_jogos"], m["media_jogos"])  # e sobrestima os jogos
        self.assertAlmostEqual(tenis.over(m, 0.5), 1.0)
        self.assertAlmostEqual(tenis.cobre(m, 0.5) - tenis.cobre(m, -0.5), m["diferenca"].get(0, 0.0))

    def test_nivel_por_circuito(self):
        self.assertEqual(tenis.nivel(CFG, "WTA Seoul WTA")[1], "wta")
        self.assertEqual(tenis.nivel(CFG, "ATP Genoa 2 challenger")[1], "challenger")
        self.assertEqual(tenis.nivel(CFG, "ATP ITF M25")[1], "challenger")
        self.assertEqual(tenis.nivel(CFG, "ATP Hangzhou"), (1.28, "atp"))


class TestConsensoRecomendacoes(unittest.TestCase):
    """Fecho pelo consenso (CLV sem Pinnacle), uma aposta por jogo, registos-sombra e avaliação."""

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        shutil.copy(RAIZ / "dados" / "config.json", self.pasta)
        self.dados_originais, banca.DADOS = banca.DADOS, self.pasta
        self.alvos_original = odds.alvos_tenis
        agora = datetime.now(timezone.utc)
        self.inicio = (agora + timedelta(hours=5)).strftime(odds.FMT)
        self.recolha = agora.strftime(odds.FMT)
        itens = [{"id": i, "desporto": "Ténis", "competicao": "ATP Hangzhou", "evento": "Faria J. vs Gaston H.",
                  "inicio": self.inicio, "mercado": "h2h", "selecao": nome, "ponto": None, "justa": p,
                  "fonte": "consenso", "recolha": self.recolha}
                 for i, nome, p in ((1, "Faria J.", 0.645), (2, "Gaston H.", 0.355))]
        (self.pasta / "alvos.json").write_text(json.dumps({"hora": self.recolha, "itens": itens}))

    def tearDown(self):
        banca.DADOS, odds.alvos_tenis = self.dados_originais, self.alvos_original
        shutil.rmtree(self.pasta)

    def recomendar(self, **campos):
        ns = {c: None for c in banca.REC}
        ns.update({"confianca": "média", "confirmado": False, "segunda_odd": None, "sombra": False})
        ns.update(campos)
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            banca.cmd_recomendar(banca.config(), [], argparse.Namespace(**ns))
        return saida.getvalue()

    def test_um_por_jogo_sombra_e_cobertura(self):
        self.assertIn("abaixo da mínima", self.recomendar(alvo=2, odd=2.70, casa="Betano", sombra=True))
        saida = self.recomendar(alvo=1, odd=1.75, casa="Betano")  # EV +12,9%, calibrado +6,5%
        self.assertIn("stake 0,40 €", saida)
        with self.assertRaises(SystemExit) as erro:
            self.recomendar(alvo=2, odd=3.20, casa="Solverde")
        self.assertIn("uma aposta por jogo", str(erro.exception))
        recs = banca.ler("recomendacoes.csv")
        self.assertEqual([r["tipo"] for r in recs], ["sombra", "simples"])
        self.assertEqual(recs[1]["recolha"], self.recolha)
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            banca.cmd_avaliacao(banca.config(), [], None)
        self.assertIn("Betano 1/2", saida.getvalue())
        self.assertIn("mais 1 registos-sombra", saida.getvalue())

    def test_fecho_pelo_consenso(self):
        agora = datetime(2026, 9, 25, 12, tzinfo=timezone.utc)
        s = {"evento": "A vs B", "selecao": "A", "inicio": "2026-09-25T13:00:00Z", "justa": 0.60,
             "recolha": "2026-09-25T03:50:00Z"}
        self.assertEqual(odds.guardar_consenso([s], agora), {})
        depois = dict(s, justa=0.63, recolha="2026-09-25T09:50:00Z")
        self.assertEqual(odds.guardar_consenso([depois], agora), {odds.chave_consenso(s): 0.60})
        hist = json.loads((self.pasta / "consenso.json").read_text())
        r = rec(evento="A vs B", selecao="A", inicio=s["inicio"], recolha=s["recolha"], odd="1.80",
                prob_justa="0.6000", sport_key="github")
        p, t, antecedencia = odds.fecho_consenso(r, hist)
        self.assertEqual((p, t), (0.63, depois["recolha"]))
        self.assertAlmostEqual(antecedencia, 3 + 10 / 60)
        self.assertIsNone(odds.fecho_consenso(dict(r, recolha=depois["recolha"]), hist))  # nunca a própria recolha
        longe = dict(s, inicio="2026-09-25T17:00:00Z")  # a última recolha fica a mais de 6 h do início
        odds.guardar_consenso([longe, dict(longe, recolha=depois["recolha"])], agora)
        hist = json.loads((self.pasta / "consenso.json").read_text())
        self.assertIsNone(odds.fecho_consenso(dict(r, inicio=longe["inicio"]), hist))

        def sem_rede():
            raise OSError("sem rede")
        odds.alvos_tenis = sem_rede
        sem_recolha = rec(ref="R2", evento="C vs D", selecao="C", inicio=s["inicio"], recolha=s["recolha"],
                          odd="1.90", prob_justa="0.5500", sport_key="github")
        banca.escrever("recomendacoes.csv", [dict(r, ref="R1"), sem_recolha], banca.REC)
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            odds.cmd_fecho(argparse.Namespace(minutos=90, ref=None))
        self.assertIn("CLV +13,4%", saida.getvalue())  # 1,80 × 0,63 − 1
        gravada, nao_medida = banca.ler("recomendacoes.csv")
        self.assertEqual((gravada["prob_fecho"], gravada["fecho_fonte"]), ("0.6300", "consenso"))
        self.assertEqual((nao_medida["prob_fecho"], nao_medida["fecho_fonte"]), ("", "não medido"))
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            odds.cmd_fecho(argparse.Namespace(minutos=90, ref=None))
        self.assertNotIn("R2", saida.getvalue())  # não volta a ser processada
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            banca.cmd_avaliacao(banca.config(), [], None)
        self.assertIn("CLV médio (IC 95%)", saida.getvalue())
        self.assertIn("mercado a favor depois da recomendação (M) +5,0%", saida.getvalue())


class TestAlvosNovos(unittest.TestCase):
    setUp, tearDown = TestFontesGithub.setUp, TestFontesGithub.tearDown

    def test_itf_e_exibicoes_de_fora_alerta_e_odd_minima_tardia(self):
        self.tenis["matches"] += [
            {"tournament": "ITF M25 Porto", "time": "12:00", "player1": "C", "player2": "D", "odds1": 1.5,
             "odds2": 2.5, "tour": "ATP"},
            {"tournament": "Laver Cup", "time": "13:00", "player1": "E", "player2": "F", "odds1": 1.8,
             "odds2": 1.95, "tour": "ATP"}]
        ns = argparse.Namespace(horas=72, desporto=["tenis"], challengers=True, itf=False)
        with contextlib.redirect_stdout(io.StringIO()):
            odds.cmd_alvos(ns)
        itens = json.loads((self.pasta / "alvos.json").read_text())["itens"]
        self.assertFalse(any("ITF" in s["competicao"] or "Laver" in s["competicao"] for s in itens))
        self.assertTrue(all(s["minima_tarde"] > s["minima"] for s in itens))  # a mínima sobe com a idade
        self.tenis["last_updated"] = self.tenis["last_updated"][:11] + "01:05:00"  # nova recolha, mesmo dia
        self.tenis["matches"][0].update(odds1=1.95, odds2=1.88)  # Griekspoor (azarão) sobe ~6 pp
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            odds.cmd_alvos(ns)
        self.assertIn("⚠ mov. para o azarão", saida.getvalue())
