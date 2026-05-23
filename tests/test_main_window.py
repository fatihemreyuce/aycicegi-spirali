"""MainWindow açılış smoke testi."""

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QMainWindow

from ui.main_window import MainWindow


def test_main_window_acilir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    assert isinstance(pencere, QMainWindow)
    assert pencere.windowTitle().startswith("Ayçiçeği Spirali")
