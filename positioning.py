"""
positioning.py
--------------
Vogel formülü ile ayçiçeği spirali üzerindeki tohum konumlarını hesaplar.

Formül (i = 0, 1, 2, ..., n-1):
    x = c * sqrt(i) * cos(i * 137.5°)
    y = c * sqrt(i) * sin(i * 137.5°)

c = 4 (ölçek sabiti) — tohumlar arası uzaklığı belirler.
"""

import math
from typing import List, Tuple

from utils import ALTIN_ACI_RADYAN

# Spiral ölçek sabiti (problem tanımında c = 4 olarak verilmiştir)
OLCEK_C: float = 4.0


def tohum_konumu(i: int, c: float = OLCEK_C) -> Tuple[float, float]:
    """
    i numaralı tohum için (x, y) koordinatını üretir.

    Parametreler:
        i (int): Tohum indeksi (>= 0).
        c (float): Ölçek sabiti (varsayılan 4).

    Döndürür:
        (x, y) demeti.
    """
    if i < 0:
        raise ValueError("Tohum indeksi negatif olamaz")

    # Yarıçap, indeksin kareköküyle orantılıdır → tohumlar dışa doğru seyrelmez
    yaricap = c * math.sqrt(i)
    # Açı, altın açının indeks katıdır → her tohum bir önceki tohumdan ~137.5° döner
    aci = i * ALTIN_ACI_RADYAN

    x = yaricap * math.cos(aci)
    y = yaricap * math.sin(aci)
    return x, y


def tum_konumlar(n: int, c: float = OLCEK_C) -> List[Tuple[float, float]]:
    """
    İlk n tohumun konum listesini döndürür.

    Parametreler:
        n (int): Üretilecek tohum sayısı.
        c (float): Ölçek sabiti.

    Döndürür:
        [(x0, y0), (x1, y1), ...] biçiminde liste.
    """
    if n < 0:
        raise ValueError("n negatif olamaz")

    # Listeyi tek seferde üret — döngüde liste büyütmek hızlıdır
    return [tohum_konumu(i, c) for i in range(n)]


# Hızlı görsel test (modül doğrudan çalıştırılırsa)
if __name__ == "__main__":
    konumlar = tum_konumlar(10)
    for idx, (x, y) in enumerate(konumlar):
        print(f"i={idx:2d}  x={x:8.3f}  y={y:8.3f}")
