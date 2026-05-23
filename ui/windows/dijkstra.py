"""
ui.windows.dijkstra
-------------------
İki tohum arası en kısa yol — Dijkstra ile.

Spiral grafı yönlü ve doğrusal (v_i → v_{i+1}); kaynak < hedef olmalı,
aksi halde yol yoktur. Delaunay komşuluk grafında (scipy gerektirir)
kenar ağırlığı = Öklid mesafesi.
"""

import math

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
)

from graph_builder import grafi_olustur
from utils import mesafe
from ui import theme
from ui.windows.base import AnalyticsWindow


# Yol görselleştirme renkleri
RENK_TOHUM = "#7d7d7d"
RENK_KAYNAK = "#1f8bff"   # Mavi
RENK_HEDEF = "#ff7070"    # Kırmızı
RENK_YOL = "#ffd400"      # Sarı
RENK_KENAR_YOL = "#ff3b3b"  # Kırmızı


def _delaunay_grafi_agirlikli(konumlar: dict) -> nx.Graph:
    """Delaunay komşuluğundan, kenar ağırlığı Öklid mesafesi olan graf üretir."""
    from scipy.spatial import Delaunay

    sirali = sorted(konumlar.keys())
    pts = [konumlar[i] for i in sirali]
    if len(pts) < 3:
        return nx.Graph()
    tri = Delaunay(pts)
    G = nx.Graph()
    G.add_nodes_from(sirali)
    eklenen = set()
    for simplex in tri.simplices:
        a, b, c = sirali[int(simplex[0])], sirali[int(simplex[1])], sirali[int(simplex[2])]
        for u, v in ((a, b), (b, c), (c, a)):
            anahtar = (u, v) if u < v else (v, u)
            if anahtar in eklenen:
                continue
            eklenen.add(anahtar)
            d = mesafe(konumlar[u], konumlar[v])
            G.add_edge(u, v, agirlik=d)
    return G


class DijkstraPenceresi(AnalyticsWindow):
    BASLIK = "En Kısa Yol — Dijkstra"

    def __init__(self, mevcut_n: int = 100, aci_derece: float = 137.5077) -> None:
        super().__init__()
        self._n = max(int(mevcut_n), 2)
        self._aci_derece = float(aci_derece)
        self.resize(840, 680)

        self._G_spiral = grafi_olustur(self._n, aci_radyan=math.radians(self._aci_derece))
        self._konumlar = {
            i: (d.get("x", 0.0), d.get("y", 0.0))
            for i, d in self._G_spiral.nodes(data=True)
        }
        self._sirali = sorted(self._konumlar.keys())

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 8, 8, 8)
        duzen.setSpacing(6)

        # Üst toolbar
        ust = QHBoxLayout()

        ust.addWidget(QLabel("Kaynak (i):"))
        self.kaynak_kutu = QSpinBox()
        self.kaynak_kutu.setRange(0, self._n - 1)
        self.kaynak_kutu.setValue(0)
        self.kaynak_kutu.setFixedWidth(80)
        ust.addWidget(self.kaynak_kutu)

        ust.addWidget(QLabel("Hedef (j):"))
        self.hedef_kutu = QSpinBox()
        self.hedef_kutu.setRange(0, self._n - 1)
        self.hedef_kutu.setValue(min(self._n - 1, 50))
        self.hedef_kutu.setFixedWidth(80)
        ust.addWidget(self.hedef_kutu)

        ust.addWidget(QLabel("Graf:"))
        self.graf_kutu = QComboBox()
        self.graf_kutu.addItems(["Spiral", "Delaunay"])
        self.graf_kutu.setFixedWidth(100)
        ust.addWidget(self.graf_kutu)

        self.hesapla_butonu = QPushButton("Hesapla")
        self.hesapla_butonu.setProperty("primary", True)
        self.hesapla_butonu.clicked.connect(self._hesapla)
        ust.addWidget(self.hesapla_butonu)

        ust.addStretch(1)

        self.durum_etiketi = QLabel("Hazır")
        ust.addWidget(self.durum_etiketi)

        duzen.addLayout(ust)

        # Canvas
        self._figure = Figure(figsize=(8, 6), facecolor=theme.ARKA_PLAN_KART)
        self._axes = self._figure.add_subplot(111)
        self._eksenleri_hazirla()
        self._canvas = FigureCanvasQTAgg(self._figure)
        duzen.addWidget(self._canvas)

        # İlk hesap
        self._hesapla()

    def _eksenleri_hazirla(self) -> None:
        self._axes.set_aspect("equal")
        self._axes.set_xticks([])
        self._axes.set_yticks([])
        for s in self._axes.spines.values():
            s.set_visible(False)
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)

    def _hesapla(self) -> None:
        self._axes.clear()
        self._eksenleri_hazirla()

        kaynak = self.kaynak_kutu.value()
        hedef = self.hedef_kutu.value()
        graf_tipi = self.graf_kutu.currentText()

        if graf_tipi == "Delaunay":
            try:
                G_used = _delaunay_grafi_agirlikli(self._konumlar)
            except ImportError:
                self.durum_etiketi.setText("scipy gerekli — pip install scipy")
                self._canvas.draw_idle()
                return
        else:
            G_used = self._G_spiral

        xs = [self._konumlar[i][0] for i in self._sirali]
        ys = [self._konumlar[i][1] for i in self._sirali]

        # Tüm tohumlar gri
        self._axes.scatter(xs, ys, s=20, c=RENK_TOHUM, zorder=2)

        try:
            yol = nx.dijkstra_path(G_used, kaynak, hedef, weight="agirlik")
            uzunluk = nx.dijkstra_path_length(G_used, kaynak, hedef, weight="agirlik")
        except nx.NetworkXNoPath:
            self.durum_etiketi.setText(f"{kaynak} → {hedef}: yol yok (yönlü graf?)")
            self._canvas.draw_idle()
            return
        except nx.NodeNotFound:
            self.durum_etiketi.setText("Düğüm bulunamadı")
            self._canvas.draw_idle()
            return

        # Yol kenarları kırmızı çizgi
        for u, v in zip(yol[:-1], yol[1:]):
            x0, y0 = self._konumlar[u]
            x1, y1 = self._konumlar[v]
            self._axes.plot(
                [x0, x1], [y0, y1],
                color=RENK_KENAR_YOL, linewidth=2.0, alpha=0.95, zorder=3,
            )

        # Yol düğümleri sarı
        yol_xs = [self._konumlar[i][0] for i in yol]
        yol_ys = [self._konumlar[i][1] for i in yol]
        self._axes.scatter(yol_xs, yol_ys, s=50, c=RENK_YOL, edgecolors=theme.METIN_ANA,
                           linewidths=0.4, zorder=4)

        # Kaynak ve hedef vurgu
        self._axes.scatter(
            [self._konumlar[kaynak][0]], [self._konumlar[kaynak][1]],
            s=120, c=RENK_KAYNAK, edgecolors=theme.METIN_ANA, linewidths=1.0, zorder=5,
        )
        self._axes.scatter(
            [self._konumlar[hedef][0]], [self._konumlar[hedef][1]],
            s=120, c=RENK_HEDEF, edgecolors=theme.METIN_ANA, linewidths=1.0, zorder=5,
        )

        self.durum_etiketi.setText(
            f"{graf_tipi}: {kaynak} → {hedef}  |  {len(yol) - 1} kenar  |  "
            f"toplam ağırlık: {uzunluk:.4f}"
        )
        self._canvas.draw_idle()
