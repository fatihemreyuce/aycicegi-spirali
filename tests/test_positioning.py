"""positioning.py için birim testler."""

import math
import unittest

from positioning import OLCEK_C, tohum_konumu, tum_konumlar
from utils import ALTIN_ACI_RADYAN


class TestTohumKonumu(unittest.TestCase):

    def test_sifirinci_tohum_merkezde(self):
        x, y = tohum_konumu(0)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

    def test_yaricap_kareko_kuralina_uyar(self):
        # |(x,y)| = c * sqrt(i) — açıdan bağımsız
        for i in [1, 4, 9, 25, 100]:
            x, y = tohum_konumu(i)
            uzaklik = math.hypot(x, y)
            self.assertAlmostEqual(uzaklik, OLCEK_C * math.sqrt(i), places=8)

    def test_negatif_indeks_hatasi(self):
        with self.assertRaises(ValueError):
            tohum_konumu(-1)

    def test_aci_parametresi_calisir(self):
        # 0 radyan açı → tüm tohumlar pozitif x ekseninde olmalı (y ≈ 0)
        for i in range(1, 5):
            x, y = tohum_konumu(i, aci_radyan=0.0)
            self.assertAlmostEqual(y, 0.0, places=8)
            self.assertGreater(x, 0)


class TestTumKonumlar(unittest.TestCase):

    def test_n_kadar_eleman(self):
        konumlar = tum_konumlar(50)
        self.assertEqual(len(konumlar), 50)

    def test_bos_dizi(self):
        self.assertEqual(tum_konumlar(0), [])

    def test_tutarli_aci(self):
        # Slider'dan gelen açı, tek tohumla aynı olmalı
        n = 20
        a_rad = math.radians(120.0)
        toplu = tum_konumlar(n, aci_radyan=a_rad)
        for i in range(n):
            beklenen = tohum_konumu(i, aci_radyan=a_rad)
            self.assertAlmostEqual(toplu[i][0], beklenen[0])
            self.assertAlmostEqual(toplu[i][1], beklenen[1])


if __name__ == "__main__":
    unittest.main()
