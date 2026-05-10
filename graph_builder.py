"""
graph_builder.py
----------------
NetworkX yönlü grafı (DiGraph) ile ayçiçeği spiralini modeller.

Düğüm (V) öznitelikleri:
    - tohum_index : int  (i)
    - fibonacci   : int  (F(i))
    - x, y        : float (Vogel konumu)

Kenar (E):
    - v_i  ->  v_{i+1}
    - 'agirlik' özniteliği = F(i+1) / F(i)
"""

from typing import List, Tuple

import networkx as nx

from fibonacci import fibonacci_dizisi
from positioning import tum_konumlar, OLCEK_C
from utils import ardisik_oran, ALTIN_ACI_RADYAN


def grafi_olustur(
    n: int,
    c: float = OLCEK_C,
    aci_radyan: float = ALTIN_ACI_RADYAN,
) -> nx.DiGraph:
    """
    n tohum için yönlü Fibonacci/Vogel grafını üretir.

    Parametreler:
        n (int): Tohum sayısı.
        c (float): Spiral ölçek sabiti.
        aci_radyan (float): Kutupsal açı (varsayılan altın açı).

    Döndürür:
        networkx.DiGraph: Düğüm ve kenar öznitelikleriyle dolu graf.
    """
    if n < 0:
        raise ValueError("n negatif olamaz")

    # Önce gerekli tüm dizileri ve konumları hazırla
    fib: List[int] = fibonacci_dizisi(n)
    konumlar: List[Tuple[float, float]] = tum_konumlar(n, c, aci_radyan)

    G: nx.DiGraph = nx.DiGraph()

    # Düğümleri ekle
    for i in range(n):
        x, y = konumlar[i]
        G.add_node(
            i,
            tohum_index=i,
            fibonacci=fib[i] if i < len(fib) else None,
            x=x,
            y=y,
        )

    # Ardışık kenarları ekle: v_i -> v_{i+1}, ağırlık = F(i+1)/F(i)
    for i in range(n - 1):
        agirlik = ardisik_oran(fib[i], fib[i + 1])
        G.add_edge(i, i + 1, agirlik=agirlik)

    return G


def dugum_konumlari(G: nx.DiGraph) -> dict:
    """
    NetworkX çizim fonksiyonları için {dugum: (x, y)} sözlüğü döndürür.
    """
    return {n: (veri["x"], veri["y"]) for n, veri in G.nodes(data=True)}


def dugum_fibonacci_haritasi(G: nx.DiGraph) -> dict:
    """
    {dugum: F(i)} sözlüğü döndürür — etiketleme ve doğrulama için kullanışlı.
    """
    return {n: veri["fibonacci"] for n, veri in G.nodes(data=True)}


if __name__ == "__main__":
    G = grafi_olustur(10)
    print("Düğüm sayısı:", G.number_of_nodes())
    print("Kenar sayısı:", G.number_of_edges())
    for u, v, d in G.edges(data=True):
        print(f"{u} -> {v}  ağırlık={d['agirlik']:.6f}")
