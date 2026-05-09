"""
utils.py
--------
Ayçiçeği spirali projesi için yardımcı matematik fonksiyonları:

- Altın oran (phi) sabitleri
- Fibonacci ardışık oran F(i+1)/F(i)
- |oran - phi| farkı
- İki nokta arası Öklid mesafesi
"""

import math
from typing import Tuple

# Altın oran sabitleri (modülün her yerinde tek doğrulukta kullanılsın)
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0  # ~1.6180339887...
ALTIN_ACI_DERECE: float = 137.5077640500378  # Phyllotaxis altın açısı (derece)
ALTIN_ACI_RADYAN: float = math.radians(ALTIN_ACI_DERECE)


def ardisik_oran(f_i: float, f_iplus1: float) -> float:
    """
    İki ardışık Fibonacci elemanının oranını verir: F(i+1) / F(i).

    F(i) = 0 olduğunda 0 döndürür (sıfıra bölme önlenir).
    """
    if f_i == 0:
        return 0.0
    return f_iplus1 / f_i


def phi_farki(oran: float) -> float:
    """
    Verilen oranın altın orana mutlak uzaklığını döndürür: |oran - phi|.
    """
    return abs(oran - PHI)


def mesafe(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    İki 2B nokta arasındaki Öklid mesafesini döndürür.

    Parametreler:
        p1, p2: (x, y) demetleri.

    Döndürür:
        float: Mesafe.
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.hypot(dx, dy)


def oran_ve_fark(f_i: float, f_iplus1: float) -> Tuple[float, float]:
    """
    Tek çağrıda hem oranı hem de phi'ye olan farkı döndüren kısayol.

    Döndürür:
        (oran, |oran - phi|)
    """
    oran = ardisik_oran(f_i, f_iplus1)
    return oran, phi_farki(oran)


# Modül doğrudan çalıştırılırsa kısa bir doğrulama
if __name__ == "__main__":
    print(f"PHI = {PHI:.10f}")
    print(f"Altın açı (derece) = {ALTIN_ACI_DERECE}")
    print("F(13)/F(12) oranı ve phi farkı:", oran_ve_fark(144, 233))
