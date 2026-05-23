"""TohumSecimPenceresi — input + sinyaller + bilgi gösterimi."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.seed_select import TohumSecimPenceresi


def test_tohum_secim_acilir(qtbot):
    pencere = TohumSecimPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert "Tohum" in pencere.windowTitle()


def test_gecerli_indeks_tohum_secildi_yayar(qtbot):
    pencere = TohumSecimPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("13")
    with qtbot.waitSignal(pencere.tohum_secildi, timeout=500) as kayit:
        pencere.sec_butonu.click()
    assert kayit.args == [13]
    # 5 bilgi satırı dolu olmalı
    assert "i = 13" in pencere.bilgi_i.text()
    assert "F(13)" in pencere.bilgi_f.text()


def test_aralik_disi_indeks_red(qtbot):
    pencere = TohumSecimPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("200")
    # 200 > n-1=99 → secim_temizle yayılmalı (hata)
    with qtbot.waitSignal(pencere.secim_temizle, timeout=500):
        pencere.sec_butonu.click()
    assert "geçersiz" in pencere.bilgi_i.text().lower() or "hata" in pencere.bilgi_i.text().lower()


def test_kapanma_secimi_temizler(qtbot):
    pencere = TohumSecimPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.secim_temizle, timeout=500):
        pencere.close()


def test_enter_tetikler_sec(qtbot):
    pencere = TohumSecimPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("21")
    with qtbot.waitSignal(pencere.tohum_secildi, timeout=500):
        pencere.giris_kutu.returnPressed.emit()
