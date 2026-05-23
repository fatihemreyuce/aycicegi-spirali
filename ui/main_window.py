"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı (overlay).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas
from ui.info_card import InfoCard


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)

        self.canvas = SpiralCanvas()
        duzen.addWidget(self.canvas, 1)

        # InfoCard overlay — canvas'ın çocuğu (Qt parent), free-floating
        self.info_card = InfoCard(self.canvas)
        self.info_card.setParent(self.canvas)

        # Sinyalleri bağla
        self.top_bar.cizim_istendi.connect(self._cizim_istendi)
        self.canvas.nokta_hover.connect(self.info_card.secili_tohum)
        self.canvas.nokta_hover_iptal.connect(lambda: self.info_card.secili_tohum(None))
        self.canvas.nokta_tiklandi.connect(self.info_card.secili_tohum)

        # İlk çizim
        self._cizim_istendi(self.top_bar.n_kutu.value(), self.top_bar.aci_kutu.value())

    def _cizim_istendi(self, n: int, aci_derece: float) -> None:
        self.canvas.spirali_ciz(n, aci_derece)
        self.info_card.n_degisti(n)

    def resizeEvent(self, event):  # noqa: N802 (Qt API)
        super().resizeEvent(event)
        self._info_card_konumla()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._info_card_konumla()

    def _info_card_konumla(self) -> None:
        """InfoCard'ı canvas'ın sağ-üst köşesine yerleştir (10px margin)."""
        if not self.canvas.isVisible():
            return
        self.info_card.adjustSize()
        margin = 12
        x = self.canvas.width() - self.info_card.width() - margin
        y = margin
        self.info_card.move(x, y)
        self.info_card.raise_()
