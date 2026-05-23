"""
ui.windows.traversal
--------------------
BFS / DFS gezintisi animasyonu — ayrı pencere.

Spiral grafı doğrusal olduğundan BFS = DFS = [0..n-1]. Eğitsel olarak
Delaunay komşuluk grafı da seçilebilir (scipy gerektirir).
"""

import math

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import networkx as nx

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
)

from graph_builder import grafi_olustur
from graph_traversal import bfs_sirasi, dfs_sirasi
from ui import theme
from ui.windows.base import AnalyticsWindow


# Animasyon renkleri (eski Tk'den korunur — eğitimsel netlik)
RENK_ZIYARET = "#5cff7a"   # Yeşil
RENK_AKTIF = "#ff3b3b"     # Kırmızı
RENK_BEKLEME = "#7d7d7d"   # Gri
RENK_KOK = "#1f8bff"       # Mavi


def _delaunay_grafi(konumlar) -> nx.Graph:
    """Verilen konumlardan Delaunay komşuluk grafı üretir (scipy gerektirir)."""
    from scipy.spatial import Delaunay  # local import; ImportError yakalanabilir

    pts = list(konumlar)
    if len(pts) < 3:
        return nx.Graph()
    tri = Delaunay(pts)
    G = nx.Graph()
    G.add_nodes_from(range(len(pts)))
    for simplex in tri.simplices:
        a, b, c = int(simplex[0]), int(simplex[1]), int(simplex[2])
        G.add_edge(a, b)
        G.add_edge(b, c)
        G.add_edge(c, a)
    return G


class GezintiPenceresi(AnalyticsWindow):
    BASLIK = "Graf Gezintisi — BFS / DFS"

    bitti = Signal()  # animasyon bittiğinde

    def __init__(self, mevcut_n: int = 100, aci_derece: float = 137.5077) -> None:
        super().__init__()
        self._n = max(int(mevcut_n), 2)
        self._aci_derece = float(aci_derece)
        self.resize(840, 680)

        # Grafı bir kez oluştur
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

        ust.addWidget(QLabel("Algoritma:"))
        self.algo_kutu = QComboBox()
        self.algo_kutu.addItems(["BFS", "DFS"])
        self.algo_kutu.setFixedWidth(80)
        ust.addWidget(self.algo_kutu)

        ust.addWidget(QLabel("Graf:"))
        self.graf_kutu = QComboBox()
        self.graf_kutu.addItems(["Spiral", "Delaunay"])
        self.graf_kutu.setFixedWidth(100)
        ust.addWidget(self.graf_kutu)

        ust.addWidget(QLabel("Kök (i):"))
        self.kok_kutu = QSpinBox()
        self.kok_kutu.setRange(0, self._n - 1)
        self.kok_kutu.setValue(0)
        self.kok_kutu.setFixedWidth(80)
        ust.addWidget(self.kok_kutu)

        ust.addWidget(QLabel("Hız (ms):"))
        self.hiz_kutu = QSpinBox()
        self.hiz_kutu.setRange(1, 2000)
        self.hiz_kutu.setValue(80)
        self.hiz_kutu.setFixedWidth(80)
        ust.addWidget(self.hiz_kutu)

        self.baslat_butonu = QPushButton("▶ Başlat")
        self.baslat_butonu.setProperty("primary", True)
        self.baslat_butonu.clicked.connect(self._baslat)
        ust.addWidget(self.baslat_butonu)

        self.sifirla_butonu = QPushButton("↺ Sıfırla")
        self.sifirla_butonu.clicked.connect(self._sifirla)
        ust.addWidget(self.sifirla_butonu)

        ust.addStretch(1)

        self.durum_etiketi = QLabel("Hazır")
        ust.addWidget(self.durum_etiketi)

        duzen.addLayout(ust)

        # Canvas
        self._figure = Figure(figsize=(8, 6), facecolor=theme.ARKA_PLAN_KART)
        self._axes = self._figure.add_subplot(111)
        self._eksenleri_hazirla()

        # İlk çizim
        xs = [self._konumlar[i][0] for i in self._sirali]
        ys = [self._konumlar[i][1] for i in self._sirali]
        self._scatter = self._axes.scatter(
            xs, ys, s=40, c=[RENK_BEKLEME] * len(self._sirali),
            edgecolors=theme.METIN_ANA, linewidths=0.4, zorder=2,
        )

        self._canvas = FigureCanvasQTAgg(self._figure)
        duzen.addWidget(self._canvas)

        # Animasyon state
        self._sira: list[int] = []
        self._k: int = 0
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._tick)

        self._sigdir()

    # ---- Eksen kurulumu ----

    def _eksenleri_hazirla(self) -> None:
        self._axes.set_aspect("equal")
        self._axes.set_xticks([])
        self._axes.set_yticks([])
        for s in self._axes.spines.values():
            s.set_visible(False)
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)

    def _sigdir(self) -> None:
        if not self._konumlar:
            return
        xs = [p[0] for p in self._konumlar.values()]
        ys = [p[1] for p in self._konumlar.values()]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        pad_x = (xmax - xmin) * 0.05 + 1.0
        pad_y = (ymax - ymin) * 0.05 + 1.0
        self._axes.set_xlim(xmin - pad_x, xmax + pad_x)
        self._axes.set_ylim(ymin - pad_y, ymax + pad_y)
        self._canvas.draw_idle()

    # ---- Başlat / Sıfırla / Tick ----

    def _baslat(self) -> None:
        if self._timer.isActive():
            self._timer.stop()

        algo = self.algo_kutu.currentText()
        graf_tipi = self.graf_kutu.currentText()
        kok = self.kok_kutu.value()

        if graf_tipi == "Delaunay":
            try:
                G_used = _delaunay_grafi([self._konumlar[i] for i in self._sirali])
            except ImportError:
                self.durum_etiketi.setText("scipy gerekli — pip install scipy")
                return
        else:
            G_used = self._G_spiral

        if algo == "BFS":
            sira = bfs_sirasi(G_used, kok)
        else:
            sira = dfs_sirasi(G_used, kok)

        self._sira = sira
        self._k = 0
        self.durum_etiketi.setText(f"{algo} ({graf_tipi}) — {len(sira)} düğüm")
        self._timer.setInterval(self.hiz_kutu.value())
        self._timer.start()

    def _sifirla(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        self._sira = []
        self._k = 0
        self._renkleri_uygula(-1)
        self.durum_etiketi.setText("Hazır")

    def _tick(self) -> None:
        if self._k >= len(self._sira):
            self._timer.stop()
            self.durum_etiketi.setText(f"Bitti — {len(self._sira)} düğüm ziyaret edildi")
            self.bitti.emit()
            return
        self._renkleri_uygula(self._k)
        self._k += 1

    def _renkleri_uygula(self, k: int) -> None:
        n_total = len(self._sirali)
        renkler = [RENK_BEKLEME] * n_total
        if k < 0:
            self._scatter.set_color(renkler)
            self._canvas.draw_idle()
            return

        for j in range(k):
            n_id = self._sira[j]
            try:
                idx = self._sirali.index(n_id)
            except ValueError:
                continue
            renkler[idx] = RENK_ZIYARET

        if 0 <= k < len(self._sira):
            n_id = self._sira[k]
            try:
                idx = self._sirali.index(n_id)
                renkler[idx] = RENK_AKTIF
            except ValueError:
                pass

        if self._sira and k > 0:
            try:
                kok_idx = self._sirali.index(self._sira[0])
                renkler[kok_idx] = RENK_KOK
            except ValueError:
                pass

        self._scatter.set_color(renkler)
        self._canvas.draw_idle()

    def closeEvent(self, event):  # noqa: N802 (Qt API)
        if self._timer.isActive():
            self._timer.stop()
        super().closeEvent(event)
