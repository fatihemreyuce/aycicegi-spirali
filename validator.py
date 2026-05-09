"""
validator.py
------------
Kullanıcının girdiği bir tam sayının Fibonacci dizisinde yer alıp almadığını
kontrol eder ve "Accept" / "Reject" sonucunu döndürür.

İki yaklaşım sağlanır:
    1. dogrula_dizide(...)        : Hazır bir Fibonacci listesinde aramak için.
    2. dogrula_matematiksel(...)  : Liste olmadan da çalışan matematiksel test.
       (Bir x sayısı Fibonacci ise 5x^2 ± 4 tam karedir.)
"""

import math
from typing import Iterable, Optional, Tuple


SONUC_ACCEPT = "Accept"
SONUC_REJECT = "Reject"


def _tam_kare_mi(n: int) -> bool:
    """n negatif değilse tam kare mi diye kontrol eder."""
    if n < 0:
        return False
    k = math.isqrt(n)
    return k * k == n


def dogrula_matematiksel(deger: int) -> str:
    """
    Bir tam sayının Fibonacci olup olmadığını matematiksel olarak kontrol eder.

    Bir x ≥ 0 sayısı Fibonacci ise (5*x^2 + 4) veya (5*x^2 - 4) tam karedir.

    Döndürür:
        "Accept" ya da "Reject".
    """
    if deger < 0:
        return SONUC_REJECT
    kare = 5 * deger * deger
    if _tam_kare_mi(kare + 4) or _tam_kare_mi(kare - 4):
        return SONUC_ACCEPT
    return SONUC_REJECT


def dogrula_dizide(deger: int, dizi: Iterable[int]) -> str:
    """
    Verilen iterable içinde değer var mı kontrol eder.

    Döndürür:
        "Accept" ya da "Reject".
    """
    return SONUC_ACCEPT if deger in set(dizi) else SONUC_REJECT


def dogrula_ve_index(deger: int, dizi: Iterable[int]) -> Tuple[str, Optional[int]]:
    """
    Hem sonucu hem de bulunduğu indeksi döndürür.

    Döndürür:
        ("Accept", index) veya ("Reject", None).
    """
    for i, f in enumerate(dizi):
        if f == deger:
            return SONUC_ACCEPT, i
    return SONUC_REJECT, None


def en_yakin_iki_fibonacci(deger: int, dizi: Iterable[int]) -> Tuple[Optional[int], Optional[int]]:
    """
    Verilen değere en yakın iki Fibonacci sayısını döndürür.

    Strateji: Diziyi sıralı olarak tarar; değerden küçük en büyük Fibonacci
    (alt) ve değerden büyük en küçük Fibonacci (üst) bulunur.

    Döndürür:
        (alt, ust)  — herhangi biri bulunamazsa None olabilir.
    """
    alt: Optional[int] = None
    ust: Optional[int] = None

    for f in dizi:
        if f <= deger:
            # Mevcut alt sınırdan büyük ama değerden küçük/eşit olanı tercih et
            if alt is None or f > alt:
                alt = f
        else:
            # Değerden büyük ilk Fibonacci'yi yakaladığımızda dur
            if ust is None or f < ust:
                ust = f
            # Dizi artan sıralı olduğu için ilk büyük yeterli
            if ust is not None:
                break

    return alt, ust


def en_yakin_iki_fibonacci_indeksli(
    deger: int, dizi: Iterable[int]
) -> Tuple[Tuple[Optional[int], Optional[int]], Tuple[Optional[int], Optional[int]]]:
    """
    Aynı en_yakin_iki_fibonacci ama indeks bilgisini de döndürür.

    Döndürür:
        ((alt_idx, alt_val), (ust_idx, ust_val))
        — herhangi biri yoksa o tarafın hem indeks hem değeri None olur.

    Örnek (deger=7, fib=[0,1,1,2,3,5,8,13,...]):
        ((5, 5), (6, 8))   # F(5)=5  ve  F(6)=8
    """
    alt_idx: Optional[int] = None
    alt_val: Optional[int] = None
    ust_idx: Optional[int] = None
    ust_val: Optional[int] = None

    for i, f in enumerate(dizi):
        if f <= deger:
            if alt_val is None or f > alt_val:
                alt_val = f
                alt_idx = i
        else:
            ust_val = f
            ust_idx = i
            break  # ilk büyük olan, en küçük "üst" demektir

    return (alt_idx, alt_val), (ust_idx, ust_val)


if __name__ == "__main__":
    # Hızlı test
    for x in [0, 1, 2, 3, 4, 5, 6, 8, 13, 21, 22, 144, 145]:
        print(f"{x:>4} -> {dogrula_matematiksel(x)}")
