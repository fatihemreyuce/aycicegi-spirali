"""GezintiPenceresi — BFS/DFS animasyon testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.traversal import GezintiPenceresi


def test_gezinti_acilir(qtbot):
    pencere = GezintiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert "Gezinti" in pencere.windowTitle() or "BFS" in pencere.windowTitle()


def test_gezinti_default_kontroller(qtbot):
    pencere = GezintiPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert pencere.algo_kutu.currentText() == "BFS"
    assert pencere.graf_kutu.currentText() == "Spiral"
    assert pencere.kok_kutu.value() == 0
    assert pencere.kok_kutu.maximum() == 19  # n-1


def test_gezinti_baslat_bfs_spiral_tum_dugumleri_ziyaret_eder(qtbot):
    """Spiral graf üzerinde BFS = DFS = [0..n-1] sırası — bitiş sinyali yayılır."""
    pencere = GezintiPenceresi(mevcut_n=5, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.hiz_kutu.setValue(10)
    with qtbot.waitSignal(pencere.bitti, timeout=2000):
        pencere.baslat_butonu.click()
    assert pencere.durum_etiketi.text().startswith("Bitti")


def test_gezinti_sifirla_durur(qtbot):
    pencere = GezintiPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.hiz_kutu.setValue(100)
    pencere.baslat_butonu.click()
    qtbot.wait(50)
    pencere.sifirla_butonu.click()
    # Timer durdu, k sıfırlandı
    assert pencere._timer.isActive() is False
    assert pencere._k == 0


def test_gezinti_delaunay_scipy_yoksa_hata(qtbot, monkeypatch):
    """Delaunay seçili + scipy yoksa hata mesajı."""
    pencere = GezintiPenceresi(mevcut_n=10, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.graf_kutu.setCurrentText("Delaunay")
    # scipy.spatial Delaunay import'unu mocklamak için sys.modules trick
    import sys
    # scipy varsa atla
    try:
        import scipy.spatial  # noqa: F401
        pytest.skip("scipy mevcut — hata yolunu test edemiyoruz")
    except ImportError:
        pass
    pencere.baslat_butonu.click()
    assert "scipy" in pencere.durum_etiketi.text().lower()
