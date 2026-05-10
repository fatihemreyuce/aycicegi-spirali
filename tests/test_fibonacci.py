"""fibonacci.py için birim testler — unittest hem `python -m unittest` hem
`pytest` ile çalışır."""

import unittest

from fibonacci import fibonacci_dizisi, fibonacci_n, formatla_buyuk_sayi


class TestFibonacciDizisi(unittest.TestCase):

    def test_sifir_eleman(self):
        self.assertEqual(fibonacci_dizisi(0), [])

    def test_tek_eleman(self):
        self.assertEqual(fibonacci_dizisi(1), [0])

    def test_klasik_dizi(self):
        # F(0)..F(9): 0,1,1,2,3,5,8,13,21,34
        self.assertEqual(
            fibonacci_dizisi(10),
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
        )

    def test_negatif_giris_hatasi(self):
        with self.assertRaises(ValueError):
            fibonacci_dizisi(-1)


class TestFibonacciN(unittest.TestCase):

    def test_kucuk_degerler(self):
        beklenen = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        for i, val in enumerate(beklenen):
            self.assertEqual(fibonacci_n(i), val, f"F({i}) yanlış")

    def test_buyuk_deger(self):
        # F(20) = 6765 — sabit, hızlı doğrulama
        self.assertEqual(fibonacci_n(20), 6765)

    def test_negatif(self):
        with self.assertRaises(ValueError):
            fibonacci_n(-5)


class TestFormatlaBuyukSayi(unittest.TestCase):

    def test_kucuk_sayi_oldugu_gibi(self):
        self.assertEqual(formatla_buyuk_sayi(123), "123")

    def test_milyondan_buyuk_bilimsel(self):
        # F(50) = 12586269025 — bilimsel notasyon bekleniyor
        sonuc = formatla_buyuk_sayi(12586269025)
        self.assertIn("e+", sonuc)

    def test_max_uzunluk_asilmaz(self):
        sonuc = formatla_buyuk_sayi(fibonacci_n(500), max_uzunluk=12)
        self.assertLessEqual(len(sonuc), 12)


if __name__ == "__main__":
    unittest.main()
