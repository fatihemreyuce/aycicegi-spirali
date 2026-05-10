"""validator.py için birim testler."""

import unittest

from fibonacci import fibonacci_dizisi
from validator import (
    SONUC_ACCEPT,
    SONUC_REJECT,
    dogrula_dizide,
    dogrula_matematiksel,
    dogrula_ve_index,
    en_yakin_iki_fibonacci,
    en_yakin_iki_fibonacci_indeksli,
)


class TestDogrulaMatematiksel(unittest.TestCase):

    def test_fibonacci_sayilari_kabul_eder(self):
        for x in [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]:
            self.assertEqual(dogrula_matematiksel(x), SONUC_ACCEPT, f"{x} red edildi")

    def test_fibonacci_olmayanlari_reddeder(self):
        for x in [4, 6, 7, 9, 10, 11, 22, 100, 145]:
            self.assertEqual(dogrula_matematiksel(x), SONUC_REJECT, f"{x} kabul edildi")

    def test_negatif_reddedilir(self):
        self.assertEqual(dogrula_matematiksel(-5), SONUC_REJECT)


class TestDogrulaDizide(unittest.TestCase):

    def setUp(self):
        self.fib = fibonacci_dizisi(15)

    def test_dizide_olan(self):
        self.assertEqual(dogrula_dizide(13, self.fib), SONUC_ACCEPT)

    def test_dizide_olmayan(self):
        self.assertEqual(dogrula_dizide(22, self.fib), SONUC_REJECT)


class TestDogrulaVeIndex(unittest.TestCase):

    def test_index_dogru(self):
        fib = fibonacci_dizisi(15)
        sonuc, idx = dogrula_ve_index(21, fib)
        self.assertEqual(sonuc, SONUC_ACCEPT)
        self.assertEqual(idx, 8)  # F(8) = 21

    def test_reject_index_none(self):
        sonuc, idx = dogrula_ve_index(22, fibonacci_dizisi(15))
        self.assertEqual(sonuc, SONUC_REJECT)
        self.assertIsNone(idx)


class TestEnYakinIkiFibonacci(unittest.TestCase):

    def setUp(self):
        self.fib = fibonacci_dizisi(15)

    def test_arada_kalan_deger(self):
        alt, ust = en_yakin_iki_fibonacci(22, self.fib)
        self.assertEqual(alt, 21)
        self.assertEqual(ust, 34)

    def test_indeksli_versiyon(self):
        (alt_i, alt_v), (ust_i, ust_v) = en_yakin_iki_fibonacci_indeksli(7, self.fib)
        self.assertEqual(alt_v, 5)
        self.assertEqual(ust_v, 8)
        self.assertEqual(alt_i, 5)  # F(5)=5
        self.assertEqual(ust_i, 6)  # F(6)=8


if __name__ == "__main__":
    unittest.main()
