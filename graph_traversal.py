"""
graph_traversal.py
------------------
Spiral grafı üzerinde BFS ve DFS gezintisi.

Not: ana grafımız yönlü (v_i → v_{i+1}) ve doğrusal bir yoldur — yönlü hâlinde
BFS/DFS sonucu trivial olarak [0, 1, 2, ..., n-1] olur. Eğitsel açıdan
*Delaunay komşuluk graflarını* da kabul edebilen genel API tasarlandı:
ileride Delaunay graf'ı geçilebilir.

Mevcut spiral grafı (v_i → v_{i+1}) için BFS/DFS yine sıralı çıkar — ancak
yine de algoritmik akışı görsel olarak izlemek öğretici.
"""

from collections import deque
from typing import List

import networkx as nx


def bfs_sirasi(G: nx.Graph, kok: int = 0) -> List[int]:
    """
    Genişlik öncelikli arama (BFS) ziyaret sırasını döndürür.

    Yönlü graf da kabul edilir; predecessor/successor yönü dikkate alınmaz —
    yön bilgisini görmezden gelmek için undirected'a dönüştürülür.
    """
    H = G.to_undirected() if G.is_directed() else G
    if kok not in H.nodes:
        return []

    sira: List[int] = []
    ziyaret = {kok}
    kuyruk: deque = deque([kok])
    while kuyruk:
        dugum = kuyruk.popleft()
        sira.append(dugum)
        # Kararlı bir sıralama için komşuları sıralı ekle — animasyon
        # tekrarlanabilir olsun
        for komsu in sorted(H.neighbors(dugum)):
            if komsu not in ziyaret:
                ziyaret.add(komsu)
                kuyruk.append(komsu)
    return sira


def dfs_sirasi(G: nx.Graph, kok: int = 0) -> List[int]:
    """
    Derinlik öncelikli arama (DFS) ziyaret sırasını döndürür (iteratif yığın).
    """
    H = G.to_undirected() if G.is_directed() else G
    if kok not in H.nodes:
        return []

    sira: List[int] = []
    ziyaret = set()
    yigin: List[int] = [kok]
    while yigin:
        dugum = yigin.pop()
        if dugum in ziyaret:
            continue
        ziyaret.add(dugum)
        sira.append(dugum)
        # Yığında ters sırada eklemek doğal soldan-sağa derinlik için gerekli
        for komsu in sorted(H.neighbors(dugum), reverse=True):
            if komsu not in ziyaret:
                yigin.append(komsu)
    return sira


if __name__ == "__main__":
    from graph_builder import grafi_olustur
    G = grafi_olustur(10)
    print("BFS:", bfs_sirasi(G))
    print("DFS:", dfs_sirasi(G))
