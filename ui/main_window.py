"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı + pencere yöneticisi.

Bu görevde canvas yerleşti — bilgi kartı (InfoCard) Task 9'da eklenecek.
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas


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

        # Çiz butonuna bağlan
        self.top_bar.cizim_istendi.connect(self.canvas.spirali_ciz)

        # İlk çizim
        self.canvas.spirali_ciz(self.top_bar.n_kutu.value(), self.top_bar.aci_kutu.value())
