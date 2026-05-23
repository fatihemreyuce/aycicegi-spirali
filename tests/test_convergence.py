"""YakinsamaPenceresi — açılış + 2 alt-grafik smoke testleri."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.convergence import YakinsamaPenceresi


def test_yakinsama_penceresi_acilir(qtbot):
    pencere = YakinsamaPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    assert pencere.windowTitle().startswith("Yakınsama")


def test_yakinsama_iki_alt_grafik(qtbot):
    pencere = YakinsamaPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    # Figure içinde 2 axes olmalı (oran + |fark|)
    assert len(pencere._figure.axes) == 2


def test_yakinsama_kucuk_n_crash_yok(qtbot):
    """n=10 küçük bir n; pencere açıklığında crash etmemeli."""
    pencere = YakinsamaPenceresi(mevcut_n=10)
    qtbot.addWidget(pencere)
    assert len(pencere._figure.axes) == 2


def test_yakinsama_minimum_n_korumasi(qtbot):
    """n < 3 olduğunda bile crash etmemeli (gizli minimum uygulanır)."""
    pencere = YakinsamaPenceresi(mevcut_n=1)
    qtbot.addWidget(pencere)
    assert len(pencere._figure.axes) == 2
