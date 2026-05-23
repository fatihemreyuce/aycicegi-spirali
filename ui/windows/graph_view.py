"""
ui.windows.graph_view
---------------------
Spirali graf modunda gösterir: sarı ok başlı yönlü kenarlar
(i → i+1) + lacivert düğümler. Mouse hover ile düğüm/kenar tooltip'i.
"""

import math
import time
from typing import Optional

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton

from graph_builder import grafi_olustur, dugum_konumlari
from ui import theme
from ui.windows.base import AnalyticsWindow


KENAR_RENGI = "#d4b400"           # Daha koyu sarı (aydınlık tema üzerinde okunur)
TOOLTIP_BG = "#1a2238"            # Lacivert tooltip arkaplanı
TOOLTIP_FG = "#fafaf7"            # Krem tooltip yazı rengi


def _kenar_kalinligi(agirlik: float) -> float:
    """Eski animator.py'daki eşikler — w<1.6 ince, w<1.618 orta, ≥1.618 kalın."""
    if agirlik < 1.6:
        return 0.5
    if agirlik < 1.618:
        return 1.5
    return 2.5


class GrafGorunumPenceresi(AnalyticsWindow):
    BASLIK = "Graf Görünümü — Yönlü Kenarlar"

    def __init__(self, mevcut_n: int = 100, aci_derece: float = 137.5077) -> None:
        super().__init__()
        self._n = max(int(mevcut_n), 2)
        self._aci_derece = float(aci_derece)
        self.resize(900, 720)

        self._G = grafi_olustur(self._n, aci_radyan=math.radians(self._aci_derece))
        self._konumlar = dugum_konumlari(self._G)
        self._sirali_dugumler = sorted(self._konumlar.keys())

        # Üst toolbar
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 8, 8, 8)
        duzen.setSpacing(6)

        ust = QHBoxLayout()
        self.sigdir_butonu = QPushButton("↺ Sığdır")
        self.sigdir_butonu.clicked.connect(self.sigdir)
        ust.addWidget(self.sigdir_butonu)
        ust.addStretch(1)
        duzen.addLayout(ust)

        # Canvas
        self._figure = Figure(figsize=(9, 7), facecolor=theme.ARKA_PLAN_KART)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._axes = self._figure.add_subplot(111)
        self._eksenleri_hazirla()
        duzen.addWidget(self._canvas)

        # Pan state
        self._press_pixel: Optional[tuple[float, float]] = None
        self._press_data: Optional[tuple[float, float]] = None
        self._panning: bool = False
        self._pan_esik_px: float = 5.0

        # Tooltip throttling
        self._son_motion_zamani: float = 0.0
        self._motion_throttle_sn: float = 0.03

        # Event bağlantıları
        self._canvas.mpl_connect("scroll_event", self._scroll_handler)
        self._canvas.mpl_connect("button_press_event", self._press_handler)
        self._canvas.mpl_connect("button_release_event", self._release_handler)
        self._canvas.mpl_connect("motion_notify_event", self._motion_handler)

        # Sahneyi kur
        self._sahneyi_kur()
        self.sigdir()

    # ---- Eksen / sahne ----

    def _eksenleri_hazirla(self) -> None:
        self._axes.set_aspect("equal")
        self._axes.set_xticks([])
        self._axes.set_yticks([])
        for s in self._axes.spines.values():
            s.set_visible(False)
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)

    def _sahneyi_kur(self) -> None:
        """Düğümleri scatter, kenarları FancyArrowPatch olarak çizer."""
        xs = [self._konumlar[i][0] for i in self._sirali_dugumler]
        ys = [self._konumlar[i][1] for i in self._sirali_dugumler]

        # Düğümler
        self._scatter = self._axes.scatter(
            xs, ys, s=30, c=theme.METIN_ANA, edgecolors=theme.AKSAN, linewidths=0.4,
            zorder=2,
        )

        # Kenarlar (ok başlı) — i → i+1
        self._oklar: list[tuple[int, int, FancyArrowPatch]] = []
        for u, v, veri in self._G.edges(data=True):
            x0, y0 = self._konumlar[u]
            x1, y1 = self._konumlar[v]
            w = float(veri.get("agirlik", 0.0))
            lw = _kenar_kalinligi(w)
            ok = FancyArrowPatch(
                (x0, y0), (x1, y1),
                arrowstyle="-|>",
                color=KENAR_RENGI,
                linewidth=lw,
                mutation_scale=10,
                alpha=0.9,
                shrinkA=4, shrinkB=4,
                zorder=1,
            )
            self._axes.add_patch(ok)
            self._oklar.append((u, v, ok))

        # Tooltip artefaktı
        self._tooltip = self._axes.text(
            0, 0, "",
            color=TOOLTIP_FG, fontsize=10,
            ha="left", va="bottom",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor=TOOLTIP_BG, edgecolor=TOOLTIP_BG, alpha=0.95,
            ),
            zorder=10,
        )
        self._tooltip.set_visible(False)

        self._canvas.draw_idle()

    # ---- Sığdır ----

    def sigdir(self) -> None:
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

    # ---- Scroll zoom ----

    def _scroll_handler(self, event) -> None:
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            return
        olcek = 1 / 1.2 if (event.button == "up" or event.step > 0) else 1.2
        xmin, xmax = self._axes.get_xlim()
        ymin, ymax = self._axes.get_ylim()
        cx, cy = event.xdata, event.ydata
        self._axes.set_xlim(cx - (cx - xmin) * olcek, cx + (xmax - cx) * olcek)
        self._axes.set_ylim(cy - (cy - ymin) * olcek, cy + (ymax - cy) * olcek)
        self._canvas.draw_idle()

    # ---- Pan ----

    def _press_handler(self, event) -> None:
        if event.button != 1 or event.inaxes != self._axes:
            return
        if event.x is None or event.y is None or event.xdata is None or event.ydata is None:
            return
        self._press_pixel = (event.x, event.y)
        self._press_data = (event.xdata, event.ydata)
        self._panning = False

    def _release_handler(self, event) -> None:
        if event.button != 1:
            return
        self._press_pixel = None
        self._press_data = None
        self._panning = False

    # ---- Motion (pan + tooltip) ----

    def _motion_handler(self, event) -> None:
        # Pan kontrolü öncelikli
        if self._press_pixel is not None:
            if event.x is None or event.y is None or event.inaxes != self._axes:
                return
            dx_px = event.x - self._press_pixel[0]
            dy_px = event.y - self._press_pixel[1]
            if not self._panning:
                if (dx_px * dx_px + dy_px * dy_px) < (self._pan_esik_px * self._pan_esik_px):
                    return
                self._panning = True
            if event.xdata is None or event.ydata is None or self._press_data is None:
                return
            dx_data = event.xdata - self._press_data[0]
            dy_data = event.ydata - self._press_data[1]
            xmin, xmax = self._axes.get_xlim()
            ymin, ymax = self._axes.get_ylim()
            self._axes.set_xlim(xmin - dx_data, xmax - dx_data)
            self._axes.set_ylim(ymin - dy_data, ymax - dy_data)
            self._canvas.draw_idle()
            return

        # Tooltip — throttled hit-test
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self._canvas.draw_idle()
            return

        simdi = time.perf_counter()
        if simdi - self._son_motion_zamani < self._motion_throttle_sn:
            return
        self._son_motion_zamani = simdi

        metin = self._hit_test(event)
        if metin is not None:
            self._tooltip.set_text(metin)
            self._tooltip.set_position((event.xdata, event.ydata))
            if not self._tooltip.get_visible():
                self._tooltip.set_visible(True)
            self._canvas.draw_idle()
        else:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self._canvas.draw_idle()

    def _hit_test(self, event) -> Optional[str]:
        # 1) Düğümler önce
        ic, info = self._scatter.contains(event)
        if ic:
            idx = int(info["ind"][0])
            node = self._sirali_dugumler[idx]
            x, y = self._konumlar[node]
            f_val = self._G.nodes[node].get("fibonacci", 0)
            return f"v{node} | F = {f_val} | konum ({x:.2f}, {y:.2f})"

        # 2) Kenarlar
        for u, v, ok in self._oklar:
            ic, _ = ok.contains(event)
            if ic:
                w = float(self._G[u][v].get("agirlik", 0.0))
                return f"v{u} → v{v} | w = {w:.4f}"

        return None
