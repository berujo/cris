import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
try:
    import backtest
except ImportError:  # pandas não instalado
    backtest = None


@unittest.skipUnless(backtest, "precisa de pandas (requirements-backtest.txt)")
class TestBacktest(unittest.TestCase):
    def test_apostas_e_resumo(self):
        jogos = [{"y": 0, "justa": [0.5, 0.5], "odds": {"Max": [2.2, 1.7]}, "fecho": None},
                 {"y": 1, "justa": [0.5, 0.5], "odds": {"Max": [2.2, 1.7]}, "fecho": None}]
        feitas = backtest.apostas(jogos, "justa", "Max", 0.03)  # só 2,20 × 0,5 − 1 = +10%
        self.assertEqual([(o, g) for o, g, _ in feitas], [(2.2, True), (2.2, False)])
        n, acerto, roi, _, clv = backtest.resumo(feitas)
        self.assertEqual((n, acerto, clv), (2, 0.5, None))
        self.assertAlmostEqual(roi, 0.1)

    def test_formato_football_data_com_fecho_da_pinnacle(self):
        csv = ("Date,HomeTeam,AwayTeam,FTR,B365H,B365D,B365A,PSH,PSD,PSA,MaxH,MaxD,MaxA,PSCH,PSCD,PSCA\n"
               "10/08/2025,A,B,H,2.10,3.40,3.60,2.00,3.60,3.90,2.25,3.70,4.00,1.90,3.70,4.20\n"
               "11/08/2025,C,D,A,1.50,4.20,6.50,1.52,4.40,6.80,1.55,4.50,7.00,1.55,4.40,6.60\n")
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(csv)
        jogos, com_pinnacle = backtest.jogos_futebol([f.name])
        Path(f.name).unlink()
        self.assertTrue(com_pinnacle)
        self.assertEqual([j["y"] for j in jogos], [0, 2])
        feitas = backtest.apostas(jogos, "justa", "Max", 0.03)
        # A @ 2,25 contra a Pinnacle 2,00: ganha, e a linha fechou a 1,90 (CLV positivo)
        self.assertEqual(feitas[0][:2], (2.25, True))
        self.assertGreater(feitas[0][2], 0)


if __name__ == "__main__":
    unittest.main()
