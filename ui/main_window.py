"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı + pencere yöneticisi.

Bu görevde sadece üst şerit yerleşti — canvas ve bilgi kartı sonraki
görevlerde eklenecek.
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar


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
        duzen.addStretch(1)  # canvas için yer ayır (Task 8'de doldurulur)
