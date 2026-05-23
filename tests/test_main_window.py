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


def test_main_window_animasyon_butonu_canvas_animasyonu_baslatir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    with patch.object(pencere.canvas, "animasyonu_basla") as mock:
        pencere.top_bar.animasyon_butonu.setChecked(True)
        mock.assert_called_once()
        kwargs = mock.call_args.kwargs
        assert kwargs.get("toplam_n") == 100
        assert kwargs.get("interval_ms") == 200


def test_main_window_animasyon_butonu_kapatma_durdurur(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    with patch.object(pencere.canvas, "animasyonu_durdur") as mock:
        pencere.top_bar.animasyon_butonu.setChecked(False)
        mock.assert_called_once()


def test_main_window_hiz_degisimi_canli_guncellenir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    with patch.object(pencere.canvas, "hiz_guncelle") as mock:
        pencere.top_bar.hiz_kutu.setCurrentText("Hızlı")
        mock.assert_called_once_with(interval_ms=50)


def test_main_window_animasyon_bitti_butonu_off_yapar(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    assert pencere.top_bar.animasyon_butonu.isChecked() is True
    pencere.canvas.animasyon_bitti.emit()
    assert pencere.top_bar.animasyon_butonu.isChecked() is False


def test_main_window_ciz_animasyonu_iptal_eder(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    assert pencere.top_bar.animasyon_butonu.isChecked() is True
    with patch.object(pencere.canvas, "animasyonu_durdur") as mock:
        pencere.top_bar.ciz_butonu.click()
        mock.assert_called_once()
    assert pencere.top_bar.animasyon_butonu.isChecked() is False


def test_main_window_sigdir_butonu_canvas_sigdir_cagirir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    with patch.object(pencere.canvas, "sigdir") as mock:
        pencere.top_bar.sigdir_butonu.click()
        mock.assert_called_once()
