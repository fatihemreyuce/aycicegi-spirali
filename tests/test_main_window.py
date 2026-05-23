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


def test_main_window_menu_tiklayinca_placeholder_acilir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    # WindowManager iç sözlüğünde olmalı
    yonetici = pencere._pencere_yoneticisi
    assert "graf.gorunum" in yonetici._pencereler
    p1 = yonetici._pencereler["graf.gorunum"]
    qtbot.addWidget(p1)
    # İkinci kez tıkla — aynı instance olmalı
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    p2 = yonetici._pencereler["graf.gorunum"]
    assert p1 is p2
