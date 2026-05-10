"""graph_traversal.py için birim testler."""

import unittest

import networkx as nx

from graph_builder import grafi_olustur
from graph_traversal import bfs_sirasi, dfs_sirasi


class TestSpiralGrafTraversal(unittest.TestCase):
    """Spiral grafı doğrusal yoldur — BFS ve DFS aynı sonucu vermeli."""

    def test_bfs_dfs_dogrusal_grafda_es(self):
        G = grafi_olustur(10)
        bfs = bfs_sirasi(G, kok=0)
        dfs = dfs_sirasi(G, kok=0)
        beklenen = list(range(10))
        self.assertEqual(bfs, beklenen)
        self.assertEqual(dfs, beklenen)


class TestGenelGraf(unittest.TestCase):
    """Daldı bir graf — BFS ve DFS farklı sonuç vermeli."""

    def setUp(self):
        # Basit bir ağaç:
        #       0
        #      / \
        #     1   2
        #    /\    \
        #   3  4    5
        self.G = nx.Graph()
        self.G.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)])

    def test_bfs_seviye_seviye(self):
        # 0'dan başlayan BFS önce 1, 2 sonra 3, 4, 5 ziyaret etmeli
        sira = bfs_sirasi(self.G, kok=0)
        self.assertEqual(sira[0], 0)
        # 1 ve 2, 3-4-5'ten önce ziyaret edilmeli
        idx_1 = sira.index(1)
        idx_2 = sira.index(2)
        idx_3 = sira.index(3)
        self.assertLess(idx_1, idx_3)
        self.assertLess(idx_2, idx_3)

    def test_dfs_derine_iner(self):
        # DFS 0 → 1 → 3 (ya da 4) gibi derine iner
        sira = dfs_sirasi(self.G, kok=0)
        self.assertEqual(sira[0], 0)
        # 1 ziyaret edildikten hemen sonra 3 veya 4 (alt-ağaç) gelmeli
        # 2 ziyaretinden ÖNCE
        idx_1 = sira.index(1)
        idx_2 = sira.index(2)
        idx_3 = sira.index(3)
        idx_4 = sira.index(4)
        # 1'in alt ağacı tamamen tüketildikten sonra 2 gelmeli
        self.assertLess(max(idx_3, idx_4), idx_2)

    def test_kok_olmayan_dugum_bos_dondurur(self):
        self.assertEqual(bfs_sirasi(self.G, kok=999), [])
        self.assertEqual(dfs_sirasi(self.G, kok=999), [])


if __name__ == "__main__":
    unittest.main()
