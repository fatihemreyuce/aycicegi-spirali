"""
ui.main_window
--------------
Ana pencere iskeleti. Bu görevde sadece boş bir QMainWindow oluşturuluyor;
sonraki görevler TopBar, SpiralCanvas, InfoCard ekleyecek.
"""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)
