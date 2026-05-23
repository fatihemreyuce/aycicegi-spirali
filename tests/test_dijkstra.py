"""DijkstraPenceresi — kaynak/hedef en kısa yol testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.dijkstra import DijkstraPenceresi


def test_dijkstra_acilir(qtbot):
    pencere = DijkstraPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert "Dijkstra" in pencere.windowTitle() or "Kısa" in pencere.windowTitle()


def test_dijkstra_default_kontroller(qtbot):
    pencere = DijkstraPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert pencere.kaynak_kutu.value() == 0
    # Hedef default min(n-1, 50) = 19 (n=20 için)
    assert pencere.hedef_kutu.value() == 19
    assert pencere.graf_kutu.currentText() == "Spiral"


def test_dijkstra_spiral_dogrusal_yol(qtbot):
    """Spiral graf doğrusal — 0 → 5 yolu 5 kenar, toplam ağırlık ~ 5φ."""
    pencere = DijkstraPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.kaynak_kutu.setValue(0)
    pencere.hedef_kutu.setValue(5)
    pencere.hesapla_butonu.click()
    metin = pencere.durum_etiketi.text()
    assert "0 → 5" in metin
    assert "5 kenar" in metin


def test_dijkstra_geriye_yol_yok(qtbot):
    """Spiral graf yönlü — 5 → 0 yolu yok."""
    pencere = DijkstraPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.kaynak_kutu.setValue(5)
    pencere.hedef_kutu.setValue(0)
    pencere.hesapla_butonu.click()
    assert "yol yok" in pencere.durum_etiketi.text().lower()
