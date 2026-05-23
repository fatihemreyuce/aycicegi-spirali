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


def test_sigdir_xlim_ylim_yeniden_ayarlar(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(100, 137.5)
    # Manuel olarak xlim/ylim'i bozulmuş bir aralığa ayarla
    canvas._axes.set_xlim(-1000, 1000)
    canvas._axes.set_ylim(-1000, 1000)
    canvas.sigdir()
    xmin, xmax = canvas._axes.get_xlim()
    ymin, ymax = canvas._axes.get_ylim()
    assert (xmax - xmin) < 200
    assert (ymax - ymin) < 200


def test_scroll_event_xlim_daraltir(qtbot):
    """Scroll-in (zoom in) xlim aralığını daraltır, imleç-merkezli."""
    from unittest.mock import MagicMock
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(100, 137.5)
    canvas.sigdir()
    xmin0, xmax0 = canvas._axes.get_xlim()
    aralik0 = xmax0 - xmin0
    event = MagicMock()
    event.inaxes = canvas._axes
    event.xdata = (xmin0 + xmax0) / 2
    event.ydata = 0
    event.button = "up"
    event.step = 1
    canvas._scroll_handler(event)
    xmin1, xmax1 = canvas._axes.get_xlim()
    aralik1 = xmax1 - xmin1
    assert aralik1 < aralik0


def test_pan_press_motion_release_xlim_kaydirir(qtbot):
    from unittest.mock import MagicMock
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(100, 137.5)
    canvas.sigdir()
    xmin0, xmax0 = canvas._axes.get_xlim()

    press = MagicMock()
    press.inaxes = canvas._axes
    press.button = 1
    press.x = 100
    press.y = 100
    press.xdata = (xmin0 + xmax0) / 2
    press.ydata = 0
    canvas._press_handler(press)

    motion = MagicMock()
    motion.inaxes = canvas._axes
    motion.x = 150
    motion.y = 100
    motion.xdata = press.xdata + 5.0
    motion.ydata = 0
    canvas._motion_pan_handler(motion)

    release = MagicMock()
    release.button = 1
    canvas._release_handler(release)

    xmin1, xmax1 = canvas._axes.get_xlim()
    assert xmin1 != xmin0


def test_vurgu_ekle_mavi_renk(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)
    canvas.vurgu_ekle(5)
    renkler = _renk_listesi(canvas)
    assert renkler[5].lower() == theme.MAVI_VURGU.lower()


def test_vurgu_temizle_eski_vurguyu_kaldirir(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)
    canvas.vurgu_ekle(5)
    canvas.vurgu_temizle()
    renkler = _renk_listesi(canvas)
    assert renkler[5].lower() != theme.MAVI_VURGU.lower()


def test_vurgu_oncelik_fibonacci_uzerine_yazar(qtbot):
    """Vurgu ile Fibonacci aynı indeksteyse → mavi gözüksün."""
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)  # 0,1,2,3,5,8 Fibonacci
    canvas.vurgu_ekle(8)
    renkler = _renk_listesi(canvas)
    assert renkler[8].lower() == theme.MAVI_VURGU.lower()
