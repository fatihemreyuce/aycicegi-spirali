"""graph_builder.py için birim testler."""

import unittest

from graph_builder import dugum_fibonacci_haritasi, dugum_konumlari, grafi_olustur


class TestGrafiOlustur(unittest.TestCase):

    def test_dugum_kenar_sayilari(self):
        G = grafi_olustur(10)
        self.assertEqual(G.number_of_nodes(), 10)
        self.assertEqual(G.number_of_edges(), 9)

    def test_kenarlar_yonlu_ve_ardisik(self):
        G = grafi_olustur(5)
        for i in range(4):
            self.assertTrue(G.has_edge(i, i + 1))
            self.assertFalse(G.has_edge(i + 1, i))  # yön: i → i+1, ters yok

    def test_kenar_agirligi_phi_ye_yakinsar(self):
        G = grafi_olustur(20)
        son_kenar = G[18][19]["agirlik"]  # F(19)/F(18) — phi'ye çok yakın
        self.assertAlmostEqual(son_kenar, 1.6180, places=3)

    def test_dugum_oznitelikleri(self):
        G = grafi_olustur(5)
        for i in range(5):
            n = G.nodes[i]
            self.assertEqual(n["tohum_index"], i)
            self.assertIn("x", n)
            self.assertIn("y", n)
            self.assertIn("fibonacci", n)


class TestYardimcilar(unittest.TestCase):

    def test_dugum_konumlari(self):
        G = grafi_olustur(5)
        konumlar = dugum_konumlari(G)
        self.assertEqual(len(konumlar), 5)
        # Düğüm 0 merkezde olmalı
        self.assertAlmostEqual(konumlar[0][0], 0.0)
        self.assertAlmostEqual(konumlar[0][1], 0.0)

    def test_fibonacci_haritasi(self):
        G = grafi_olustur(10)
        harita = dugum_fibonacci_haritasi(G)
        self.assertEqual(harita[5], 5)   # F(5) = 5
        self.assertEqual(harita[8], 21)  # F(8) = 21


if __name__ == "__main__":
    unittest.main()
