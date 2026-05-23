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


def test_main_window_top_bar_iceriyor(qtbot):
    from ui.top_bar import TopBar

    pencere = MainWindow()
    qtbot.addWidget(pencere)
    assert pencere.top_bar is not None
    assert isinstance(pencere.top_bar, TopBar)


def test_main_window_info_card_n_degistirir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.show()
    # n=100 ile başladı; en yakın Fibonacci k bulunmalı → 11 (F(11)=89)
    metin = pencere.info_card.f_etiketi.text()
    assert "F(" in metin and "=" in metin
