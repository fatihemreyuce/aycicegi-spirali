"""KomsulukMatrisiPenceresi — açılış + boyut + içerik testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.adjacency_matrix import KomsulukMatrisiPenceresi


def test_matris_penceresi_acilir(qtbot):
    pencere = KomsulukMatrisiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert "Matris" in pencere.windowTitle()


def test_matris_default_boyut_uygulanir(qtbot):
    pencere = KomsulukMatrisiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    # Default boyut 6 (veya n_total küçükse min(6, n_total))
    assert pencere.boyut_kutu.value() == 6
    # Tablo (boyut)×(boyut+1) olmalı
    assert pencere.tablo.rowCount() == 6
    assert pencere.tablo.columnCount() == 7


def test_matris_max_boyut_50_ile_sinirli(qtbot):
    pencere = KomsulukMatrisiPenceresi(mevcut_n=200, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert pencere.boyut_kutu.maximum() == 50


def test_matris_kenar_yoksa_sifir(qtbot):
    """Spiral graf yalnızca i → i+1 yönlü kenarlara sahip; A[0][3] = 0 olmalı."""
    pencere = KomsulukMatrisiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    # Hücre 0,3 (v0 satır, v3 sütun) → kenar yok
    item = pencere.tablo.item(0, 3)
    assert item is not None
    assert item.text() == "0"


def test_matris_boyut_degistirince_yenilenir(qtbot):
    pencere = KomsulukMatrisiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.boyut_kutu.setValue(10)
    pencere.yenile_butonu.click()
    assert pencere.tablo.rowCount() == 10
    assert pencere.tablo.columnCount() == 11
