"""
ui.spiral_canvas
----------------
matplotlib qtagg backend tabanlı Qt widget'ı. Ayçiçeği spiralini çizer;
Fibonacci indeksli noktaları vurgular; hover/click ile sinyal yayar
(InfoCard bu sinyalleri dinleyip detayı sağ-üst kartta gösterir).

NOT: Spec 3.5'teki "noktanın yanında açılan tooltip" davranışı Plan 1'de
sadeleştirildi — aynı bilgi sağ-üst InfoCard'da gösteriliyor. Cursor'ı
takip eden floating tooltip ileride ayrı bir alt-task olarak eklenebilir.
"""

import math
from typing import Optional

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from fibonacci import fibonacci_dizisi
from positioning import tum_konumlar
from ui import theme


def _fibonacci_indeks_kumesi(n: int) -> set[int]:
    """0..n-1 arasındaki tüm Fibonacci sayılarını küme olarak döndürür."""
    fib = fibonacci_dizisi(20)  # F(0)..F(19) = 4181'e kadar yeter
    return {f for f in fib if 0 <= f < n}


class SpiralCanvas(QWidget):
    """
    Spirali çizen ve etkileşim yönetim Qt widget'ı.

    Sinyaller:
        nokta_hover(int)  — fare bir noktanın yakınına geldi (tohum_index).
        nokta_hover_iptal — fare bir noktanın yakınından ayrıldı.
        nokta_tiklandi(int) — bir noktaya tıklandı.
    """

    nokta_hover = Signal(int)
    nokta_hover_iptal = Signal()
    nokta_tiklandi = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._figure = Figure(figsize=(8, 8), facecolor=theme.ARKA_PLAN_KART)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._axes = self._figure.add_subplot(111)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.addWidget(self._canvas)

        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()

        # Hover/click bağlantıları
        self._canvas.mpl_connect("motion_notify_event", self._hover_handler)
        self._canvas.mpl_connect("button_press_event", self._click_handler)

        self._eksenleri_hazirla()

    # ---- Genel API ----

    def spirali_ciz(self, n: int, aci_derece: float) -> None:
        """n tohum ile spirali yeniden çiz."""
        self._n = n
        self._aci_derece = aci_derece
        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(n)
        self._yeniden_ciz()

    # ---- İç çizim ----

    def _eksenleri_hazirla(self) -> None:
        self._axes.set_aspect("equal")
        self._axes.set_xticks([])
        self._axes.set_yticks([])
        for spine in self._axes.spines.values():
            spine.set_visible(False)
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)

    def _yeniden_ciz(self) -> None:
        self._axes.clear()
        self._eksenleri_hazirla()

        if not self._konumlar:
            self._canvas.draw_idle()
            return

        xs = [p[0] for p in self._konumlar]
        ys = [p[1] for p in self._konumlar]

        # Tüm noktalar — koyu lacivert
        self._axes.scatter(xs, ys, s=8, c=theme.METIN_ANA, zorder=1)

        # Fibonacci indeksli noktalar — kırmızı + etiket
        for i in self._fib_indeksleri:
            x, y = self._konumlar[i]
            self._axes.scatter([x], [y], s=24, c=theme.VURGU, zorder=2)
            self._axes.text(
                x + 1.0, y + 1.0, str(i),
                fontsize=8, color="#555555",
                family="Georgia", zorder=3,
            )

        self._canvas.draw_idle()

    # ---- Etkileşim ----

    def _en_yakin_nokta(self, event) -> Optional[int]:
        if event.xdata is None or event.ydata is None or not self._konumlar:
            return None
        # Veri koordinatlarında 3.0 birim eşik (~10px düşük zoom'da)
        esik = 3.0
        en_yakin: Optional[int] = None
        en_yakin_mes = float("inf")
        for i, (x, y) in enumerate(self._konumlar):
            d = math.hypot(x - event.xdata, y - event.ydata)
            if d < esik and d < en_yakin_mes:
                en_yakin_mes = d
                en_yakin = i
        return en_yakin

    def _hover_handler(self, event) -> None:
        idx = self._en_yakin_nokta(event)
        if idx is None:
            self.nokta_hover_iptal.emit()
        else:
            self.nokta_hover.emit(idx)

    def _click_handler(self, event) -> None:
        idx = self._en_yakin_nokta(event)
        if idx is not None:
            self.nokta_tiklandi.emit(idx)
