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


def test_main_window_graf_validator_acinca_gercek_pencere(qtbot):
    from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.validator")
    yonetici = pencere._pencere_yoneticisi
    p = yonetici._pencereler["graf.validator"]
    qtbot.addWidget(p)
    assert isinstance(p, FibonacciValidatorPenceresi)


def test_main_window_validator_accept_canvas_vurgu_ekler(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.validator")
    p = pencere._pencere_yoneticisi._pencereler["graf.validator"]
    qtbot.addWidget(p)
    p.giris_kutu.setText("21")
    p.dogrula_butonu.click()
    assert 8 in pencere.canvas._vurgu_indeksleri  # F(8) = 21


def test_main_window_gor_yakinsama_acinca_gercek_pencere(qtbot):
    from ui.windows.convergence import YakinsamaPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("gor.yakinsama")
    p = pencere._pencere_yoneticisi._pencereler["gor.yakinsama"]
    qtbot.addWidget(p)
    assert isinstance(p, YakinsamaPenceresi)


def test_main_window_gor_karsilastirma_acinca_gercek_pencere(qtbot):
    from ui.windows.comparison import KarsilastirmaPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("gor.karsilastirma")
    p = pencere._pencere_yoneticisi._pencereler["gor.karsilastirma"]
    qtbot.addWidget(p)
    assert isinstance(p, KarsilastirmaPenceresi)


def test_main_window_alg_tohum_acinca_gercek_pencere(qtbot):
    from ui.windows.seed_select import TohumSecimPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("alg.tohum")
    p = pencere._pencere_yoneticisi._pencereler["alg.tohum"]
    qtbot.addWidget(p)
    assert isinstance(p, TohumSecimPenceresi)


def test_main_window_tohum_secildi_canvas_secim_ekler(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("alg.tohum")
    p = pencere._pencere_yoneticisi._pencereler["alg.tohum"]
    qtbot.addWidget(p)
    p.giris_kutu.setText("21")
    p.sec_butonu.click()
    assert 21 in pencere.canvas._secim_indeksleri


def test_main_window_graf_matris_acinca_gercek_pencere(qtbot):
    from ui.windows.adjacency_matrix import KomsulukMatrisiPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.matris")
    p = pencere._pencere_yoneticisi._pencereler["graf.matris"]
    qtbot.addWidget(p)
    assert isinstance(p, KomsulukMatrisiPenceresi)


def test_main_window_alg_bfs_dfs_acinca_gercek_pencere(qtbot):
    from ui.windows.traversal import GezintiPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("alg.bfs_dfs")
    p = pencere._pencere_yoneticisi._pencereler["alg.bfs_dfs"]
    qtbot.addWidget(p)
    assert isinstance(p, GezintiPenceresi)


def test_main_window_alg_dijkstra_acinca_gercek_pencere(qtbot):
    from ui.windows.dijkstra import DijkstraPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("alg.dijkstra")
    p = pencere._pencere_yoneticisi._pencereler["alg.dijkstra"]
    qtbot.addWidget(p)
    assert isinstance(p, DijkstraPenceresi)


def test_main_window_gor_animasyon_acinca_gercek_pencere(qtbot):
    from ui.windows.animation_control import AnimasyonKontrolPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("gor.animasyon")
    p = pencere._pencere_yoneticisi._pencereler["gor.animasyon"]
    qtbot.addWidget(p)
    assert isinstance(p, AnimasyonKontrolPenceresi)


def test_main_window_animasyon_kontrol_canvas_kareye_atlatir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("gor.animasyon")
    p = pencere._pencere_yoneticisi._pencereler["gor.animasyon"]
    qtbot.addWidget(p)
    p.kare_kaydirici.setValue(42)
    assert pencere.canvas.mevcut_kare() == 42


def test_main_window_graf_gorunum_toggles_canvas(qtbot):
    """graf.gorunum menü öğesi ana canvas'ı toggle eder; ayrı pencere açmaz."""
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    assert pencere.canvas.graf_modu_acik_mi() is False
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    assert pencere.canvas.graf_modu_acik_mi() is True
    # WindowManager'da pencere yok (toggle, ayrı pencere yok)
    assert "graf.gorunum" not in pencere._pencere_yoneticisi._pencereler
    # İkinci tıklama → kapat
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    assert pencere.canvas.graf_modu_acik_mi() is False
