"""
ui.windows.convergence
----------------------
F(i+1)/F(i) → φ yakınsamasını gösteren ayrı pencere.

İki alt-grafik:
  - Üstte: oran ve φ referans çizgisi
  - Altta: |oran − φ|, log skala
"""

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtWidgets import QVBoxLayout

from fibonacci import fibonacci_dizisi
from utils import PHI, ardisik_oran, phi_farki
from ui import theme
from ui.windows.base import AnalyticsWindow


class YakinsamaPenceresi(AnalyticsWindow):
    BASLIK = "Yakınsama Grafiği — F(i+1)/F(i) → φ"

    def __init__(self, mevcut_n: int = 100) -> None:
        super().__init__()
        n = max(int(mevcut_n), 5)
        self.resize(720, 520)

        self._figure = Figure(figsize=(7, 5), facecolor=theme.ARKA_PLAN_KART)
        self._canvas = FigureCanvasQTAgg(self._figure)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 8, 8, 8)
        duzen.addWidget(self._canvas)

        fib = fibonacci_dizisi(n + 1)
        self._cizimi_yap(fib)

    def _cizimi_yap(self, fib: list[int]) -> None:
        """İki alt-grafiği hesaplayıp çizer."""
        indeksler: list[int] = []
        oranlar: list[float] = []
        farklar: list[float] = []
        for i in range(1, len(fib) - 1):
            f_i = fib[i]
            f_iplus1 = fib[i + 1]
            if f_i == 0:
                continue
            oran = ardisik_oran(f_i, f_iplus1)
            fark = phi_farki(oran)
            indeksler.append(i)
            oranlar.append(oran)
            # log skalada 0 görünmez — epsilon ile koru
            farklar.append(fark if fark > 0 else 1e-20)

        # Üst grafik: oran + φ ref
        ax1 = self._figure.add_subplot(2, 1, 1)
        ax1.set_facecolor(theme.ARKA_PLAN_KART)
        ax1.plot(
            indeksler, oranlar,
            color=theme.AKSAN, linewidth=1.5,
            marker="o", markersize=3, label="F(i+1)/F(i)",
        )
        ax1.axhline(
            PHI,
            color=theme.METIN_PASIF, linestyle="--", linewidth=1.0,
            label=f"φ ≈ {PHI:.10f}",
        )
        ax1.set_ylabel("Oran", color=theme.METIN_ANA)
        ax1.tick_params(colors=theme.METIN_ANA)
        for sk in ax1.spines.values():
            sk.set_color(theme.KENAR_KALIN)
        ax1.legend(
            facecolor=theme.ARKA_PLAN_KART,
            edgecolor=theme.KENAR_KALIN,
            labelcolor=theme.METIN_ANA,
            loc="lower right", fontsize=9,
        )
        ax1.set_title(
            "Ardışık Fibonacci Oranlarının Altın Orana Yakınsaması",
            color=theme.AKSAN, fontsize=11,
        )

        # Alt grafik: |fark| log skala
        ax2 = self._figure.add_subplot(2, 1, 2)
        ax2.set_facecolor(theme.ARKA_PLAN_KART)
        ax2.semilogy(
            indeksler, farklar,
            color=theme.VURGU, linewidth=1.5,
            marker="s", markersize=3, label="|F(i+1)/F(i) − φ|",
        )
        ax2.set_xlabel("i", color=theme.METIN_ANA)
        ax2.set_ylabel("|fark|  (log)", color=theme.METIN_ANA)
        ax2.tick_params(colors=theme.METIN_ANA)
        for sk in ax2.spines.values():
            sk.set_color(theme.KENAR_KALIN)
        ax2.grid(True, which="both", color=theme.KENAR_INCE, linewidth=0.4, alpha=0.8)
        ax2.legend(
            facecolor=theme.ARKA_PLAN_KART,
            edgecolor=theme.KENAR_KALIN,
            labelcolor=theme.METIN_ANA,
            loc="upper right", fontsize=9,
        )

        self._figure.tight_layout()
        self._canvas.draw_idle()
