"""FibonacciValidatorPenceresi — sinyaller + sonuç gösterimi."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi


def test_accept_sinyali_dogru_indeksi_yayar(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("21")
    with qtbot.waitSignal(pencere.tohum_vurgula, timeout=500) as kayit:
        pencere.dogrula_butonu.click()
    assert kayit.args == [8]  # F(8) = 21
    assert "Accept" in pencere.sonuc_etiketi.text()


def test_reject_vurgu_temizle_yayar(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("22")
    with qtbot.waitSignal(pencere.vurgu_temizle, timeout=500):
        pencere.dogrula_butonu.click()
    assert "Reject" in pencere.sonuc_etiketi.text()
    alt = pencere.alt_etiketi.text()
    assert "21" in alt and "34" in alt


def test_enter_tetikler_dogrula(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("89")
    with qtbot.waitSignal(pencere.tohum_vurgula, timeout=500):
        pencere.giris_kutu.returnPressed.emit()


def test_kapanma_vurguyu_temizler(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.vurgu_temizle, timeout=500):
        pencere.close()
