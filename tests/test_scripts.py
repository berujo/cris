import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import banca  # noqa: E402
import odds  # noqa: E402

CFG = {"banca_inicial": 20.0, "fracao_kelly": 0.25, "teto_stake_pct": 10, "teto_multipla_pct": 5,
       "stop_loss_pct": 50, "stake_minima": 0.10, "arredondamento": 0.10}


def aposta(estado, stake, odd, lucro):
    return {"id": "1", "data": "2026-09-24", "estado": estado, "stake": str(stake), "odd": str(odd),
            "lucro": str(lucro)}


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


class TestOdds(unittest.TestCase):
    def test_sem_margem(self):
        self.assertEqual(odds.sem_margem([1.90, 1.90]), [0.5, 0.5])

    def test_valor_contra_pinnacle(self):
        evento = {"bookmakers": [
            {"key": "pinnacle", "title": "Pinnacle", "markets": [{"key": "h2h", "outcomes": [
                {"name": "A", "price": 1.95}, {"name": "B", "price": 1.95}]}]},
            {"key": "betclic", "title": "Betclic", "markets": [{"key": "h2h", "outcomes": [
                {"name": "A", "price": 2.10}, {"name": "B", "price": 1.75}]}]},
        ]}
        valor = {s: (casa, v) for _, s, _, _, _, casa, v in odds.analisar(evento)}
        self.assertEqual(valor["A"][0], "Betclic")
        self.assertAlmostEqual(valor["A"][1], 0.05)

    def test_totais_sem_pinnacle(self):
        evento = {"bookmakers": [
            {"key": k, "title": k, "markets": [{"key": "totals", "outcomes": [
                {"name": "Over", "price": o, "point": 2.5}, {"name": "Under", "price": u, "point": 2.5}]}]}
            for k, o, u in (("x", 1.80, 2.00), ("y", 1.90, 1.90))
        ]}
        r = odds.analisar(evento)
        self.assertEqual({s for _, s, *_ in r}, {"Over 2.5", "Under 2.5"})
        self.assertTrue(all(fonte == "média de 2 casas" for _, _, _, fonte, *_ in r))


if __name__ == "__main__":
    unittest.main()
