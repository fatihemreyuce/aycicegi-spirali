"""
fibonacci.py
------------
Fibonacci dizisini iteratif yöntemle üreten modül.

F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2)
"""

from typing import List


def fibonacci_dizisi(n: int) -> List[int]:
    """
    İlk n Fibonacci sayısını liste olarak döndürür.

    Parametre:
        n (int): Üretilecek Fibonacci eleman sayısı (>= 0).

    Döndürür:
        List[int]: [F(0), F(1), ..., F(n-1)] biçiminde liste.

    Hata:
        ValueError: n negatif olduğunda fırlatılır.
    """
    # Negatif giriş kabul edilmez
    if n < 0:
        raise ValueError("n negatif olamaz")

    # Sınır durumlar: 0 ve 1 elemanlı diziler
    if n == 0:
        return []
    if n == 1:
        return [0]

    # İteratif hesaplama: önceki iki değeri tutarak ilerle
    dizi: List[int] = [0, 1]
    for _ in range(2, n):
        # Yeni terim = son iki terimin toplamı
        dizi.append(dizi[-1] + dizi[-2])
    return dizi


def fibonacci_n(n: int) -> int:
    """
    Tek bir F(n) değerini döndürür (yardımcı fonksiyon).

    Parametre:
        n (int): İndeks (>= 0).

    Döndürür:
        int: F(n) değeri.
    """
    if n < 0:
        raise ValueError("n negatif olamaz")
    if n == 0:
        return 0
    if n == 1:
        return 1
    # İki değişken ile bellek kullanımını sabit tutalım
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def formatla_buyuk_sayi(deger: int, max_uzunluk: int = 12) -> str:
    """
    Çok büyük tam sayıları sağ panelde okunabilir biçimde kısaltır.

    Kural:
        - |deger| <= 1_000_000  → tam sayı olduğu gibi (en fazla 7 hane).
        - Aksi halde bilimsel notasyona dönüştürülür (örn. "8.62e+20").
        - Çıktı uzunluğu max_uzunluk karakteri aşmaz; aşıyorsa mantis kısaltılır.

    Çok büyük Fibonacci sayıları float aralığını (~1.8e308) aşabilir; bu yüzden
    float()'a düşmeden, dize uzunluğundan üs hesaplanır.
    """
    s = str(deger)
    # Negatif işaret varsa ayrı tut
    isaret = ""
    if s.startswith("-"):
        isaret = "-"
        s = s[1:]

    # Küçükse olduğu gibi göster
    if deger >= 0 and deger <= 1_000_000:
        return s if not isaret else isaret + s
    if deger < 0 and -deger <= 1_000_000:
        return isaret + s

    # Bilimsel notasyon: ilk haneyi mantis tabanı yap
    haneler = len(s)
    us = haneler - 1
    # Hedef format: "X.YYe+ZZZ" — mantis için kalan alanı hesapla
    sabit_kisim = f"e+{us}"
    kalan = max_uzunluk - len(isaret) - len(sabit_kisim) - 2  # "X." için 2 karakter
    if kalan < 0:
        # Hiç ondalık sığmıyorsa sadece ilk hane + üs
        sonuc = f"{isaret}{s[0]}{sabit_kisim}"
    else:
        ondalik = s[1 : 1 + kalan] if kalan > 0 else ""
        if ondalik:
            sonuc = f"{isaret}{s[0]}.{ondalik}{sabit_kisim}"
        else:
            sonuc = f"{isaret}{s[0]}{sabit_kisim}"

    # Güvenlik için sınırla
    return sonuc[:max_uzunluk]


# Modül doğrudan çalıştırılırsa hızlı bir test yap
if __name__ == "__main__":
    print("İlk 10 Fibonacci:", fibonacci_dizisi(10))
    print("F(15) =", fibonacci_n(15))
    print("Format(123):", formatla_buyuk_sayi(123))
    print("Format(F(100)):", formatla_buyuk_sayi(fibonacci_n(100)))
    print("Format(F(500)):", formatla_buyuk_sayi(fibonacci_n(500)))
