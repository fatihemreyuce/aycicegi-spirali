"""utils.py için birim testler."""

import math
import unittest

from utils import ALTIN_ACI_DERECE, PHI, ardisik_oran, mesafe, oran_ve_fark, phi_farki


class TestAltinOranSabitleri(unittest.TestCase):

    def test_phi_kapali_form(self):
        self.assertAlmostEqual(PHI, (1 + math.sqrt(5)) / 2, places=15)

    def test_altin_aci_yaklasik(self):
        # 360 * (1 - 1/φ) ≈ 137.5077640500378
        beklenen = 360 * (1 - 1 / PHI)
        self.assertAlmostEqual(ALTIN_ACI_DERECE, beklenen, places=10)


class TestArdisikOran(unittest.TestCase):

    def test_normal(self):
        self.assertAlmostEqual(ardisik_oran(13, 21), 21 / 13)

    def test_sifira_bolme_korumasi(self):
        # F(0) = 0 olduğu için 1. tohumda sıfıra bölme olmamalı
        self.assertEqual(ardisik_oran(0, 1), 0.0)


class TestPhiFarki(unittest.TestCase):

    def test_phi_kendisi_sifir(self):
        self.assertAlmostEqual(phi_farki(PHI), 0.0)

    def test_uzak_deger(self):
        self.assertGreater(phi_farki(1.0), 0.6)


class TestOranVeFark(unittest.TestCase):

    def test_dondurus_yapisi(self):
        oran, fark = oran_ve_fark(8, 13)
        self.assertAlmostEqual(oran, 13 / 8)
        self.assertAlmostEqual(fark, abs(13 / 8 - PHI))


class TestMesafe(unittest.TestCase):

    def test_origin(self):
        self.assertAlmostEqual(mesafe((0, 0), (3, 4)), 5.0)

    def test_simetrik(self):
        self.assertAlmostEqual(
            mesafe((1.5, 2.5), (4.0, 6.0)),
            mesafe((4.0, 6.0), (1.5, 2.5)),
        )


if __name__ == "__main__":
    unittest.main()
