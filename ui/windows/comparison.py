"""
ui.windows.comparison
---------------------
İki açıyı yan yana spiral olarak karşılaştırma penceresi.

Üst toolbar'da iki açı + n + 3 preset + Çiz. Altta iki matplotlib axes
yan yana. Cross-window sinyal yok — sadece görsel kıyas.
"""

import math

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
)

from positioning import tum_konumlar
from utils import ALTIN_ACI_DERECE
from ui import theme
from ui.windows.base import AnalyticsWindow


class KarsilastirmaPenceresi(AnalyticsWindow):
    BASLIK = "Açı Karşılaştırma — Altın Açı vs Diğeri"

    def __init__(self, mevcut_n: int = 300) -> None:
        super().__init__()
        self.resize(1100, 620)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 8, 8, 8)
        duzen.setSpacing(6)

        ust = QHBoxLayout()

        ust.addWidget(QLabel("Sol açı (°):"))
        self.sol_aci_kutu = QDoubleSpinBox()
        self.sol_aci_kutu.setRange(0.001, 359.999)
        self.sol_aci_kutu.setDecimals(4)
        self.sol_aci_kutu.setSingleStep(0.1)
        self.sol_aci_kutu.setValue(ALTIN_ACI_DERECE)
        self.sol_aci_kutu.setFixedWidth(120)
        ust.addWidget(self.sol_aci_kutu)

        ust.addWidget(QLabel("Sağ açı (°):"))
        self.sag_aci_kutu = QDoubleSpinBox()
        self.sag_aci_kutu.setRange(0.001, 359.999)
        self.sag_aci_kutu.setDecimals(4)
        self.sag_aci_kutu.setSingleStep(0.1)
        self.sag_aci_kutu.setValue(90.0)
        self.sag_aci_kutu.setFixedWidth(120)
        ust.addWidget(self.sag_aci_kutu)

        ust.addWidget(QLabel("n:"))
        self.n_kutu = QSpinBox()
        self.n_kutu.setRange(1, 5000)
        self.n_kutu.setValue(max(int(mevcut_n), 50))
        self.n_kutu.setFixedWidth(80)
        ust.addWidget(self.n_kutu)

        self.preset_90_butonu = QPushButton("137.5° vs 90°")
        self.preset_90_butonu.clicked.connect(lambda: self._preset(ALTIN_ACI_DERECE, 90.0))
        ust.addWidget(self.preset_90_butonu)

        self.preset_137_butonu = QPushButton("137.5° vs 137.0°")
        self.preset_137_butonu.clicked.connect(lambda: self._preset(ALTIN_ACI_DERECE, 137.0))
        ust.addWidget(self.preset_137_butonu)

        self.preset_60_butonu = QPushButton("137.5° vs 60°")
        self.preset_60_butonu.clicked.connect(lambda: self._preset(ALTIN_ACI_DERECE, 60.0))
        ust.addWidget(self.preset_60_butonu)

        self.ciz_butonu = QPushButton("Çiz")
        self.ciz_butonu.setProperty("primary", True)
        self.ciz_butonu.clicked.connect(self._ciz)
        ust.addWidget(self.ciz_butonu)

        ust.addStretch(1)
        duzen.addLayout(ust)

        self._figure = Figure(figsize=(10, 5), facecolor=theme.ARKA_PLAN_KART)
        self._ax_sol = self._figure.add_subplot(1, 2, 1)
        self._ax_sag = self._figure.add_subplot(1, 2, 2)
        for ax in (self._ax_sol, self._ax_sag):
            ax.set_facecolor(theme.ARKA_PLAN_KART)
            ax.set_aspect("equal", adjustable="box")
            ax.axis("off")

        self._canvas = FigureCanvasQTAgg(self._figure)
        duzen.addWidget(self._canvas)

        self._ciz()

    def _preset(self, sol: float, sag: float) -> None:
        self.sol_aci_kutu.setValue(sol)
        self.sag_aci_kutu.setValue(sag)
        self._ciz()

    def _ciz(self) -> None:
        n = self.n_kutu.value()
        sol = self.sol_aci_kutu.value()
        sag = self.sag_aci_kutu.value()
        self._spirali_ciz_axes(self._ax_sol, sol, n)
        self._spirali_ciz_axes(self._ax_sag, sag, n)
        self._figure.tight_layout()
        self._canvas.draw_idle()

    def _spirali_ciz_axes(self, ax, aci_derece: float, n: int) -> None:
        ax.clear()
        ax.set_facecolor(theme.ARKA_PLAN_KART)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        if n <= 0:
            return
        konumlar = tum_konumlar(n, aci_radyan=math.radians(aci_derece))
        xs = [p[0] for p in konumlar]
        ys = [p[1] for p in konumlar]
        ax.scatter(xs, ys, s=12, c=theme.METIN_ANA)
        ax.set_title(f"α = {aci_derece:.4f}°", color=theme.AKSAN, fontsize=11)
