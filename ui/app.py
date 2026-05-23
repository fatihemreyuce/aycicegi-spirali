"""
ui.app
------
QApplication kurulumu ve uygulama giriş noktası.
"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import qt_stylesheet


def main() -> int:
    """QApplication başlat, MainWindow göster, event loop'a gir."""
    app = QApplication(sys.argv)
    app.setStyleSheet(qt_stylesheet())
    pencere = MainWindow()
    pencere.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
