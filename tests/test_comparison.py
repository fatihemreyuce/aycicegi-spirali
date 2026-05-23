"""KarsilastirmaPenceresi — açılış + preset + çizim testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.comparison import KarsilastirmaPenceresi
from utils import ALTIN_ACI_DERECE


def test_karsilastirma_penceresi_acilir(qtbot):
    pencere = KarsilastirmaPenceresi(mevcut_n=300)
    qtbot.addWidget(pencere)
    assert "Karşılaştırma" in pencere.windowTitle()


def test_karsilastirma_iki_axes(qtbot):
    pencere = KarsilastirmaPenceresi(mevcut_n=300)
    qtbot.addWidget(pencere)
    assert len(pencere._figure.axes) == 2


def test_karsilastirma_default_acilar(qtbot):
    pencere = KarsilastirmaPenceresi(mevcut_n=300)
    qtbot.addWidget(pencere)
    assert pencere.sol_aci_kutu.value() == pytest.approx(ALTIN_ACI_DERECE, abs=0.01)
    assert pencere.sag_aci_kutu.value() == pytest.approx(90.0)


def test_karsilastirma_preset_butonu_aciyi_degistirir(qtbot):
    pencere = KarsilastirmaPenceresi(mevcut_n=300)
    qtbot.addWidget(pencere)
    # 137.5 vs 60 preset'i
    pencere.preset_60_butonu.click()
    assert pencere.sol_aci_kutu.value() == pytest.approx(ALTIN_ACI_DERECE, abs=0.01)
    assert pencere.sag_aci_kutu.value() == pytest.approx(60.0)


def test_karsilastirma_ciz_axes_temizler_ve_yeniden_cizer(qtbot):
    pencere = KarsilastirmaPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    # n=50 yapıp Çiz'e bas → axes'lerde scatter olmalı
    pencere.n_kutu.setValue(50)
    pencere.ciz_butonu.click()
    # Her axes en az 1 collection (scatter) içermeli
    for ax in pencere._figure.axes:
        assert len(ax.collections) >= 1
