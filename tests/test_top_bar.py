"""TopBar widget'ı davranış testleri."""

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QPushButton, QComboBox

from ui.top_bar import TopBar
from utils import ALTIN_ACI_DERECE


def test_topbar_n_kutu_50_5000_arasi(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.n_kutu, QSpinBox)
    assert bar.n_kutu.minimum() == 50
    assert bar.n_kutu.maximum() == 5000  # ayçiçeği modu için F(19)=4181'i kapsar
    assert bar.n_kutu.value() == 100  # varsayılan


def test_topbar_aci_kutu_varsayilan_altin_aci(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.aci_kutu, QDoubleSpinBox)
    assert bar.aci_kutu.minimum() == pytest.approx(30.0)
    assert bar.aci_kutu.maximum() == pytest.approx(180.0)
    assert bar.aci_kutu.value() == pytest.approx(ALTIN_ACI_DERECE, abs=0.01)


def test_topbar_ciz_butonu_primary_property(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.ciz_butonu, QPushButton)
    assert bar.ciz_butonu.property("primary") is True


def test_topbar_ciz_clicked_sinyali_n_aci_yayar(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    bar.n_kutu.setValue(150)
    bar.aci_kutu.setValue(140.0)
    with qtbot.waitSignal(bar.cizim_istendi, timeout=500) as kayit:
        bar.ciz_butonu.click()
    assert kayit.args == [150, 140.0]


def test_topbar_hiz_kutu_4_oge_default_normal(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.hiz_kutu, QComboBox)
    assert bar.hiz_kutu.count() == 4
    ogeler = [bar.hiz_kutu.itemText(i) for i in range(4)]
    assert ogeler == ["Yavaş", "Normal", "Hızlı", "Anında"]
    assert bar.hiz_kutu.currentText() == "Normal"


def test_topbar_hiz_degisimi_sinyal_yayar(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    with qtbot.waitSignal(bar.hiz_degisti, timeout=500) as kayit:
        bar.hiz_kutu.setCurrentText("Hızlı")
    assert kayit.args == ["Hızlı"]


