"""
visualizer.py
-------------
matplotlib ile ayçiçeği spiralini statik olarak çizer.

Renk paleti:
    - Arka plan : koyu yeşil
    - Tohumlar  : sarı
    - Vurgu     : mavi (validator tarafından kabul edilen tohum)
"""

from typing import Iterable, Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import networkx as nx

from graph_builder import dugum_konumlari


# Tek noktadan değiştirilebilir renk sabitleri
ARKA_PLAN_RENGI = "#0b3d2e"   # Koyu yeşil
TOHUM_RENGI = "#ffd400"        # Sarı
VURGU_RENGI = "#1f8bff"        # Mavi
KENAR_RENGI = "#5a8a6a"        # Hafif soluk yeşil — kenarlar arka planı bozmasın


def figur_hazirla(figsize=(7, 7)) -> tuple[Figure, Axes]:
    """
    Koyu yeşil arka planlı, eşit ölçekli, eksensiz bir matplotlib figürü hazırlar.
    """
    fig: Figure = plt.figure(figsize=figsize, facecolor=ARKA_PLAN_RENGI)
    ax: Axes = fig.add_subplot(111)
    ax.set_facecolor(ARKA_PLAN_RENGI)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    return fig, ax


def spirali_ciz(
    G: nx.DiGraph,
    ax: Optional[Axes] = None,
    nokta_boyutu: int = 40,
    vurgu_indexleri: Optional[Iterable[int]] = None,
) -> Axes:
    """
    Verilen grafı (tüm tohumlar görünür) tek bir karede çizer.

    Parametreler:
        G               : networkx DiGraph (graph_builder.grafi_olustur ile üretilir)
        ax              : Mevcut bir Axes verilmezse yenisi oluşturulur.
        nokta_boyutu    : Tohum nokta boyutu (matplotlib 's' parametresi).
        vurgu_indexleri : Mavi renkle vurgulanacak düğüm indeksleri.

    Döndürür:
        Çizimin yapıldığı Axes.
    """
    if ax is None:
        _, ax = figur_hazirla()

    konumlar = dugum_konumlari(G)
    if not konumlar:
        return ax

    vurgu_kumesi = set(vurgu_indexleri) if vurgu_indexleri else set()

    # X ve Y koordinatlarını sıralı düğümlere göre topla
    sirali_dugumler = sorted(konumlar.keys())
    xs = [konumlar[i][0] for i in sirali_dugumler]
    ys = [konumlar[i][1] for i in sirali_dugumler]
    renkler = [VURGU_RENGI if i in vurgu_kumesi else TOHUM_RENGI for i in sirali_dugumler]

    # Önce ince kenar çizgileri (spiralin geometrisini öne çıkarır)
    if G.number_of_edges() > 0:
        for u, v in G.edges():
            x0, y0 = konumlar[u]
            x1, y1 = konumlar[v]
            ax.plot([x0, x1], [y0, y1], color=KENAR_RENGI, linewidth=0.4, alpha=0.6, zorder=1)

    # Sonra noktalar — kenar çizgilerinin üstünde kalsın
    ax.scatter(xs, ys, s=nokta_boyutu, c=renkler, edgecolors="black",
               linewidths=0.3, zorder=2)

    return ax


if __name__ == "__main__":
    # Hızlı görsel test (interaktif çalıştırılırsa pencere açılır)
    from graph_builder import grafi_olustur

    G = grafi_olustur(200)
    fig, ax = figur_hazirla()
    spirali_ciz(G, ax)
    plt.show()
