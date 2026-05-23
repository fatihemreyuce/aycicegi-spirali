"""AnimasyonKontrolPenceresi — manuel kare kontrolü testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.animation_control import AnimasyonKontrolPenceresi


def test_animasyon_kontrol_acilir(qtbot):
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=99)
    qtbot.addWidget(pencere)
    assert "Animasyon" in pencere.windowTitle()


def test_slider_aralik_ve_baslangic(qtbot):
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=42)
    qtbot.addWidget(pencere)
    assert pencere.kare_kaydirici.minimum() == -1
    assert pencere.kare_kaydirici.maximum() == 99
    assert pencere.kare_kaydirici.value() == 42


def test_ileri_butonu_kareye_atla_yayar(qtbot):
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=20)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.kareye_atla_istendi, timeout=500) as kayit:
        pencere.ileri_butonu.click()
    assert kayit.args == [21]


def test_geri_butonu_kareye_atla_yayar(qtbot):
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=20)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.kareye_atla_istendi, timeout=500) as kayit:
        pencere.geri_butonu.click()
    assert kayit.args == [19]


def test_slider_degisimi_sinyal_yayar(qtbot):
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=0)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.kareye_atla_istendi, timeout=500) as kayit:
        pencere.kare_kaydirici.setValue(55)
    assert kayit.args == [55]


def test_kare_guncelle_slider_ve_etiket(qtbot):
    """canvas.kare_degisti → pencere.kareyi_guncelle sinyalsiz çağrı."""
    pencere = AnimasyonKontrolPenceresi(toplam_n=100, baslangic_kare=0)
    qtbot.addWidget(pencere)
    pencere.kareyi_guncelle(73)
    assert pencere.kare_kaydirici.value() == 73
    # Etiket 1-tabanlı: 73 → "Kare 74 / 100"
    assert "74" in pencere.bilgi_etiketi.text()
