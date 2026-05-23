"""SpiralCanvas — kare-kare çizim, animasyon, zoom/pan testleri."""

import math

import pytest

pytest.importorskip("PySide6")

from ui.spiral_canvas import SpiralCanvas, _fibonacci_indeks_kumesi
from ui import theme
from positioning import tum_konumlar


def _renk_listesi(canvas: SpiralCanvas) -> list[str]:
    """Scatter koleksiyonunun mevcut renklerini hex listesi olarak döndürür."""
    import matplotlib.colors as mcolors
    rgba_dizisi = canvas._scatter.get_facecolors()
    return [mcolors.to_hex(rgba) for rgba in rgba_dizisi]


def test_kare_ciz_ilk_kare_sadece_birinci_aktif(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    n = 10
    aci = 137.5
    konumlar = tum_konumlar(n, aci_radyan=math.radians(aci))
    fib = _fibonacci_indeks_kumesi(n)
    canvas._kare_ciz(kare_no=0, toplam=n, konumlar=konumlar, fib_indeksleri=fib)
    renkler = _renk_listesi(canvas)
    assert renkler[0].lower() == theme.VURGU.lower()  # aktif → kırmızı
    for r in renkler[1:]:
        assert r.lower() == theme.BEKLEME.lower()  # diğerleri gri


def test_kare_ciz_orta_kare_karma_renk(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    n = 10
    aci = 137.5
    konumlar = tum_konumlar(n, aci_radyan=math.radians(aci))
    fib = _fibonacci_indeks_kumesi(n)  # 0..10 için {0,1,2,3,5,8}
    canvas._kare_ciz(kare_no=5, toplam=n, konumlar=konumlar, fib_indeksleri=fib)
    renkler = _renk_listesi(canvas)
    # 0,1,2,3 ziyaret edilmiş — Fibonacci olanlar kırmızı, diğerleri lacivert
    assert renkler[0].lower() == theme.VURGU.lower()   # 0 ∈ fib
    assert renkler[1].lower() == theme.VURGU.lower()   # 1 ∈ fib
    assert renkler[2].lower() == theme.VURGU.lower()   # 2 ∈ fib
    assert renkler[3].lower() == theme.VURGU.lower()   # 3 ∈ fib
    assert renkler[4].lower() == theme.METIN_ANA.lower()  # 4 ziyaret, fib değil
    assert renkler[5].lower() == theme.VURGU.lower()   # 5 aktif → kırmızı
    for r in renkler[6:]:
        assert r.lower() == theme.BEKLEME.lower()  # bekleyen → gri


def test_kare_ciz_son_kare_tam_spiral(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    n = 10
    aci = 137.5
    konumlar = tum_konumlar(n, aci_radyan=math.radians(aci))
    fib = _fibonacci_indeks_kumesi(n)
    canvas._kare_ciz(kare_no=n - 1, toplam=n, konumlar=konumlar, fib_indeksleri=fib)
    renkler = _renk_listesi(canvas)
    # Tüm tohumlar yerleşti; son tohum aktif (kırmızı); fib indeksleri kırmızı; diğerleri lacivert
    assert renkler[n - 1].lower() == theme.VURGU.lower()
    for i in range(n):
        if i == n - 1:
            continue
        if i in fib:
            assert renkler[i].lower() == theme.VURGU.lower()
        else:
            assert renkler[i].lower() == theme.METIN_ANA.lower()


def test_animasyonu_basla_aninda_modu_hemen_bitis_sinyali(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    with qtbot.waitSignal(canvas.animasyon_bitti, timeout=500):
        canvas.animasyonu_basla(toplam_n=10, aci_derece=137.5, interval_ms=1)
    # Anında modda tüm tohumlar yerleşmiş olmalı
    assert canvas._anim_kare == 9


def test_animasyonu_basla_kare_kare_ilerler(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    # 5 tohum × 50ms ≈ 250ms; 2 sn timeout yeterli
    with qtbot.waitSignal(canvas.animasyon_bitti, timeout=2000):
        canvas.animasyonu_basla(toplam_n=5, aci_derece=137.5, interval_ms=50)
    assert canvas._anim_kare == 4


def test_animasyonu_durdur_donar(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.animasyonu_basla(toplam_n=100, aci_derece=137.5, interval_ms=50)
    # 1-2 tick işle ki kare ilerlesin
    qtbot.wait(120)
    canvas.animasyonu_durdur()
    son_kare = canvas._anim_kare
    qtbot.wait(200)
    # Durdurduktan sonra kare ilerlememeli
    assert canvas._anim_kare == son_kare


def test_animasyonu_basla_hiz_canli_guncellenir(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.animasyonu_basla(toplam_n=20, aci_derece=137.5, interval_ms=500)
    # Interval güncellenebilir olmalı
    canvas.hiz_guncelle(interval_ms=50)
    assert canvas._timer.interval() == 50
    canvas.animasyonu_durdur()
