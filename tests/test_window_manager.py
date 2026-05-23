"""WindowManager tek-instance kuralı."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.base import AnalyticsWindow, WindowManager


class SahteWindow(AnalyticsWindow):
    BASLIK = "Sahte"


def test_window_manager_ayni_kimligi_iki_kere_acmaz(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p1)
    p2 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p2)
    assert p1 is p2


def test_window_manager_kapatilan_pencere_temizlenir(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p1)
    p1.close()
    # Qt'nin destroyed sinyali close() ile senkron gelmeyebilir (Windows quirk).
    # deleteLater() + kısa bekleme ile imhayı zorla.
    p1.deleteLater()
    qtbot.wait(50)
    # Kapatıldıktan sonra yeni açılış yeni instance üretmeli
    p2 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p2)
    assert p1 is not p2


def test_window_manager_farkli_kimlikler_ayri_pencere(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("a", SahteWindow)
    p2 = yonetici.ac_veya_one_getir("b", SahteWindow)
    qtbot.addWidget(p1)
    qtbot.addWidget(p2)
    assert p1 is not p2
