"""GrafGorunumPenceresi — ok başlı kenarlar + tooltip + zoom testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.graph_view import GrafGorunumPenceresi


def test_graf_gorunum_acilir(qtbot):
    pencere = GrafGorunumPenceresi(mevcut_n=20, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    assert "Graf" in pencere.windowTitle()


def test_graf_gorunum_dugum_ve_kenar_sayisi(qtbot):
    """n=10 → 10 düğüm, 9 kenar (spiral graf: i → i+1)."""
    pencere = GrafGorunumPenceresi(mevcut_n=10, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    # Scatter koleksiyonu = düğümler
    scatters = [c for c in pencere._axes.collections]
    assert len(scatters) >= 1
    # FancyArrowPatch sayısı = kenar sayısı
    from matplotlib.patches import FancyArrowPatch
    oklar = [p for p in pencere._axes.patches if isinstance(p, FancyArrowPatch)]
    assert len(oklar) == 9


def test_graf_gorunum_sigdir_xlim_daraltir(qtbot):
    pencere = GrafGorunumPenceresi(mevcut_n=100, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere._axes.set_xlim(-1000, 1000)
    pencere.sigdir()
    xmin, xmax = pencere._axes.get_xlim()
    assert (xmax - xmin) < 200


def test_graf_gorunum_scroll_zoom(qtbot):
    """Scroll event xlim aralığını daraltır."""
    from unittest.mock import MagicMock
    pencere = GrafGorunumPenceresi(mevcut_n=50, aci_derece=137.5077)
    qtbot.addWidget(pencere)
    pencere.sigdir()
    xmin0, xmax0 = pencere._axes.get_xlim()
    event = MagicMock()
    event.inaxes = pencere._axes
    event.xdata = (xmin0 + xmax0) / 2
    event.ydata = 0
    event.button = "up"
    event.step = 1
    pencere._scroll_handler(event)
    xmin1, xmax1 = pencere._axes.get_xlim()
    assert (xmax1 - xmin1) < (xmax0 - xmin0)
