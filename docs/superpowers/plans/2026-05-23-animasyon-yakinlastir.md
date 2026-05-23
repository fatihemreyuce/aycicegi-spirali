# Animasyon + Yakınlaştır Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PySide6 portunda `▶ Animasyon` butonunu QTimer ile kare-kare çalıştırmak, TopBar'a 4 seviyeli `Hız` combobox eklemek, `⊕ Yakınlaştır` toggle'ını `↺ Sığdır` aksiyon butonuna çevirmek, ve SpiralCanvas'a scroll-wheel zoom + sol-tık-drag pan eklemek.

**Architecture:** `ui/theme.py`'a yeni gri renk sabiti eklenir. `ui/top_bar.py` QComboBox ile `hiz_degisti(str)` ve QPushButton ile `sigdir_istendi()` sinyallerini yayınlar. `ui/spiral_canvas.py` QTimer tabanlı animasyon (kare_no = -1 → toplam-1), `animasyon_bitti` sinyali, matplotlib `mpl_connect` üzerinden scroll/drag handler'ları ve `sigdir()` metodu ekler. `ui/main_window.py` sinyalleri bağlar; Çiz'e basılınca animasyon iptal edilir, doğal bitişte buton OFF'a alınır.

**Tech Stack:** PySide6 6.x (`QComboBox`, `QPushButton`, `QTimer`, `Signal`), matplotlib `qtagg` backend (`mpl_connect` event API), pytest + pytest-qt (`qtbot.waitSignal`, `qtbot.mouseClick`).

---

## File Structure

**Değiştirilen dosyalar:**

| Path | Değişiklik |
|---|---|
| `ui/theme.py` | `BEKLEME` sabiti eklenir (`#7d7d7d`). |
| `ui/top_bar.py` | `yakinlastir_butonu` ve `yakinlastir_toggled` kaldırılır; `hiz_kutu` (QComboBox) ve `sigdir_butonu` (QPushButton) eklenir; yeni sinyaller `hiz_degisti(str)`, `sigdir_istendi()`. |
| `ui/spiral_canvas.py` | Animasyon state (QTimer, `_anim_kare`, `_anim_toplam`), `animasyonu_basla` / `animasyonu_durdur` / `animasyon_bitti`, `_kare_ciz` yardımcısı; scroll/drag handler'ları, `sigdir()` metodu. |
| `ui/main_window.py` | `hiz_degisti` → state, `animasyon_toggled` → canvas, `sigdir_istendi` → canvas; `_cizim_istendi` içinde animasyon iptal; `animasyon_bitti` → buton OFF. |
| `tests/test_top_bar.py` | `hiz_kutu` ve `sigdir_butonu` testleri. |
| `tests/test_main_window.py` | Animasyon toggle, Çiz iptal, animasyon bitiş davranış testleri. |

**Yeni dosyalar:**

| Path | Sorumluluk |
|---|---|
| `tests/test_spiral_canvas.py` | `_kare_ciz`, `animasyonu_basla/durdur`, `animasyon_bitti`, `sigdir` testleri. |

**Dokunulmayan dosyalar:** domain modülleri (`fibonacci.py`, `positioning.py`, `validator.py`, `utils.py`, `graph_builder.py`, `graph_traversal.py`), `ui/info_card.py`, `ui/windows/*`, eski Tk dosyaları.

---

## Task 1: Tema BEKLEME rengi

**Files:**
- Modify: `ui/theme.py`
- Modify: `tests/test_theme.py`

- [ ] **Step 1: Önce başarısız testi yaz**

`tests/test_theme.py` içindeki `test_renk_sabitleri_hex_formatinda` fonksiyonunun renk listesine `"BEKLEME"` ekle. Mevcut:

```python
def test_renk_sabitleri_hex_formatinda():
    for ad in [
        "ARKA_PLAN_ANA",
        "ARKA_PLAN_KART",
        "ARKA_PLAN_OVERLAY",
        "KENAR_INCE",
        "KENAR_KALIN",
        "METIN_ANA",
        "METIN_IKINCIL",
        "METIN_PASIF",
        "AKSAN",
        "AKSAN_KOYU",
        "VURGU",
    ]:
```

Şununla değiştir:

```python
def test_renk_sabitleri_hex_formatinda():
    for ad in [
        "ARKA_PLAN_ANA",
        "ARKA_PLAN_KART",
        "ARKA_PLAN_OVERLAY",
        "KENAR_INCE",
        "KENAR_KALIN",
        "METIN_ANA",
        "METIN_IKINCIL",
        "METIN_PASIF",
        "AKSAN",
        "AKSAN_KOYU",
        "VURGU",
        "BEKLEME",
    ]:
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_theme.py::test_renk_sabitleri_hex_formatinda -v
```

Beklenen: FAIL — `AttributeError: module 'ui.theme' has no attribute 'BEKLEME'`.

- [ ] **Step 3: `ui/theme.py`'ye `BEKLEME` sabitini ekle**

`VURGU: str = "#b8242a"` satırının altına ekle:

```python
BEKLEME: str = "#7d7d7d"          # Animasyon sırasında henüz yerleşmemiş tohum
```

- [ ] **Step 4: Testi tekrar çalıştır**

```bash
python -m pytest tests/test_theme.py -v
```

Beklenen: 3 test PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/theme.py tests/test_theme.py
git commit -m "ui: BEKLEME rengi (animasyon sırasında bekleyen tohum)"
```

---

## Task 2: TopBar — Hız ComboBox

**Files:**
- Modify: `ui/top_bar.py`
- Modify: `tests/test_top_bar.py`

- [ ] **Step 1: Başarısız testleri yaz**

`tests/test_top_bar.py` dosyasının üstündeki import bloğunu güncelle:

```python
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QPushButton, QComboBox
```

Dosyanın sonuna ekle:

```python
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
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_top_bar.py::test_topbar_hiz_kutu_4_oge_default_normal -v
```

Beklenen: FAIL — `AttributeError: 'TopBar' object has no attribute 'hiz_kutu'`.

- [ ] **Step 3: `ui/top_bar.py` import'una `QComboBox` ekle**

Mevcut import:

```python
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QToolButton,
    QMenu,
    QFrame,
)
```

Şununla değiştir:

```python
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QToolButton,
    QMenu,
    QFrame,
    QComboBox,
)
```

- [ ] **Step 4: `TopBar`'a `hiz_degisti` sinyalini ekle**

Mevcut sinyal bloğu:

```python
    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    yakinlastir_toggled = Signal(bool)
    menu_eylemi = Signal(str)
```

Şununla değiştir:

```python
    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    yakinlastir_toggled = Signal(bool)
    hiz_degisti = Signal(str)
    menu_eylemi = Signal(str)
```

- [ ] **Step 5: `hiz_kutu` widget'ını layout'a ekle**

Animasyon butonu eklendikten sonra (`duzen.addWidget(self.animasyon_butonu)` satırının altı), Yakınlaştır butonundan ÖNCE ekle:

Mevcut:

```python
        # Animasyon
        self.animasyon_butonu = QPushButton("▶ Animasyon")
        self.animasyon_butonu.setCheckable(True)
        self.animasyon_butonu.toggled.connect(self.animasyon_toggled)
        duzen.addWidget(self.animasyon_butonu)

        # Yakınlaştır
```

Şununla değiştir:

```python
        # Animasyon
        self.animasyon_butonu = QPushButton("▶ Animasyon")
        self.animasyon_butonu.setCheckable(True)
        self.animasyon_butonu.toggled.connect(self.animasyon_toggled)
        duzen.addWidget(self.animasyon_butonu)

        # Hız
        duzen.addWidget(QLabel("Hız"))
        self.hiz_kutu = QComboBox()
        self.hiz_kutu.addItems(["Yavaş", "Normal", "Hızlı", "Anında"])
        self.hiz_kutu.setCurrentText("Normal")
        self.hiz_kutu.setFixedWidth(100)
        self.hiz_kutu.currentTextChanged.connect(self.hiz_degisti)
        duzen.addWidget(self.hiz_kutu)

        # Yakınlaştır
```

- [ ] **Step 6: Testleri tekrar çalıştır**

```bash
python -m pytest tests/test_top_bar.py -v
```

Beklenen: 6 test PASS (4 mevcut + 2 yeni).

- [ ] **Step 7: Commit**

```bash
git add ui/top_bar.py tests/test_top_bar.py
git commit -m "ui: TopBar — Hız QComboBox (Yavaş/Normal/Hızlı/Anında)"
```

---

## Task 3: TopBar — Yakınlaştır toggle → Sığdır butonu

**Files:**
- Modify: `ui/top_bar.py`
- Modify: `tests/test_top_bar.py`

- [ ] **Step 1: Başarısız test yaz**

`tests/test_top_bar.py` sonuna ekle:

```python
def test_topbar_sigdir_butonu_var_ve_sinyal_yayar(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.sigdir_butonu, QPushButton)
    assert "Sığdır" in bar.sigdir_butonu.text()
    with qtbot.waitSignal(bar.sigdir_istendi, timeout=500):
        bar.sigdir_butonu.click()


def test_topbar_yakinlastir_butonu_kaldirildi(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    # Eski toggle artık yok
    assert not hasattr(bar, "yakinlastir_butonu")
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_top_bar.py::test_topbar_sigdir_butonu_var_ve_sinyal_yayar -v
```

Beklenen: FAIL — `AttributeError: 'TopBar' object has no attribute 'sigdir_butonu'`.

- [ ] **Step 3: `TopBar`'a `sigdir_istendi` sinyalini ekle**

Mevcut sinyal bloğu (Task 2 sonrası):

```python
    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    yakinlastir_toggled = Signal(bool)
    hiz_degisti = Signal(str)
    menu_eylemi = Signal(str)
```

Şununla değiştir (`yakinlastir_toggled` satırını sil, `sigdir_istendi` ekle):

```python
    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    hiz_degisti = Signal(str)
    sigdir_istendi = Signal()
    menu_eylemi = Signal(str)
```

- [ ] **Step 4: Yakınlaştır toggle bloğunu Sığdır butonuyla değiştir**

Mevcut blok (Task 2 sonrası):

```python
        # Yakınlaştır
        self.yakinlastir_butonu = QToolButton()
        self.yakinlastir_butonu.setText("⊕ Yakınlaştır")
        self.yakinlastir_butonu.setCheckable(True)
        self.yakinlastir_butonu.toggled.connect(self.yakinlastir_toggled)
        duzen.addWidget(self.yakinlastir_butonu)
```

Şununla değiştir:

```python
        # Sığdır
        self.sigdir_butonu = QPushButton("↺ Sığdır")
        self.sigdir_butonu.clicked.connect(self.sigdir_istendi)
        duzen.addWidget(self.sigdir_butonu)
```

- [ ] **Step 5: `QToolButton` import'unu kontrol et**

`QToolButton` hâlâ menü butonları için kullanılıyor (`_menu_butonu_yarat`), bu yüzden import'tan ÇIKARMA. Sadece kullanım sayısını azalttık.

- [ ] **Step 6: Testleri tekrar çalıştır**

```bash
python -m pytest tests/test_top_bar.py -v
```

Beklenen: 8 test PASS.

- [ ] **Step 7: Commit**

```bash
git add ui/top_bar.py tests/test_top_bar.py
git commit -m "ui: TopBar — Yakınlaştır toggle yerine ↺ Sığdır aksiyon butonu"
```

---

## Task 4: SpiralCanvas — `_kare_ciz` yardımcısı

**Files:**
- Modify: `ui/spiral_canvas.py`
- Create: `tests/test_spiral_canvas.py`

- [ ] **Step 1: Yeni test dosyası yaz**

`tests/test_spiral_canvas.py` yeni dosya:

```python
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
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_spiral_canvas.py -v
```

Beklenen: FAIL — `AttributeError: 'SpiralCanvas' object has no attribute '_kare_ciz'` veya `_scatter is None`.

- [ ] **Step 3: `ui/spiral_canvas.py`'da `_kare_ciz` yardımcısını ve durum alanlarını ekle**

Mevcut import bloğunun altına ekle (theme import zaten var, sadece `BEKLEME` artık erişilebilir).

Mevcut `__init__` sonundaki:

```python
        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()
```

Şununla değiştir (animasyon state alanları):

```python
        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()
        # Statik scatter referansı — _kare_ciz tarafından kullanılır
        self._scatter = None
```

Mevcut `_yeniden_ciz` metodunu tamamen kaldır ve yerine şu iki metodu yaz (sınıfın sonuna ekle):

```python
    def _yeniden_ciz(self) -> None:
        """Tam spirali tek karede çiz (mevcut davranış)."""
        self._kare_ciz(
            kare_no=len(self._konumlar) - 1,
            toplam=len(self._konumlar),
            konumlar=self._konumlar,
            fib_indeksleri=self._fib_indeksleri,
        )

    def _kare_ciz(
        self,
        kare_no: int,
        toplam: int,
        konumlar: list[tuple[float, float]],
        fib_indeksleri: set[int],
    ) -> None:
        """
        `kare_no` (0-indeksli) son aktif tohum olacak şekilde sahneyi çizer.

        Renk öncelik sırası:
          0) index > kare_no   → BEKLEME (gri)
          1) index == kare_no  → VURGU   (aktif, kırmızı)
          2) index ∈ fib AND index < kare_no → VURGU (Fibonacci ziyaret edilmiş)
          3) index < kare_no   → METIN_ANA (lacivert)
        """
        self._axes.clear()
        self._eksenleri_hazirla()

        if toplam == 0 or not konumlar:
            self._scatter = None
            self._canvas.draw_idle()
            return

        xs = [p[0] for p in konumlar]
        ys = [p[1] for p in konumlar]

        renkler: list[str] = []
        for i in range(toplam):
            if i > kare_no:
                renkler.append(theme.BEKLEME)
            elif i == kare_no:
                renkler.append(theme.VURGU)
            elif i in fib_indeksleri:
                renkler.append(theme.VURGU)
            else:
                renkler.append(theme.METIN_ANA)

        self._scatter = self._axes.scatter(xs, ys, s=10, c=renkler, zorder=1)

        # Fibonacci etiketleri sadece yerleşmiş tohumlara
        for i in fib_indeksleri:
            if i > kare_no:
                continue
            x, y = konumlar[i]
            self._axes.text(
                x + 1.0, y + 1.0, str(i),
                fontsize=8, color="#555555",
                family="Georgia", zorder=3,
            )

        self._canvas.draw_idle()
```

- [ ] **Step 4: Testleri çalıştır**

```bash
python -m pytest tests/test_spiral_canvas.py -v
```

Beklenen: 3 test PASS.

- [ ] **Step 5: Regresyonu doğrula — mevcut testler hâlâ geçiyor mu**

```bash
python -m pytest tests/ -v
```

Beklenen: tüm önceki testler de PASS (MainWindow `info_card.n_degisti` çağrısı için `spirali_ciz` davranışı değişmedi).

- [ ] **Step 6: Commit**

```bash
git add ui/spiral_canvas.py tests/test_spiral_canvas.py
git commit -m "ui: SpiralCanvas — _kare_ciz yardımcısı (renk durumları)"
```

---

## Task 5: SpiralCanvas — QTimer animasyonu

**Files:**
- Modify: `ui/spiral_canvas.py`
- Modify: `tests/test_spiral_canvas.py`

- [ ] **Step 1: Başarısız testleri yaz**

`tests/test_spiral_canvas.py` sonuna ekle:

```python
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
    # 5 tohum × 50ms ≈ 250ms; 1 sn timeout yeterli
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
```

- [ ] **Step 2: Testleri çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_spiral_canvas.py::test_animasyonu_basla_aninda_modu_hemen_bitis_sinyali -v
```

Beklenen: FAIL — `AttributeError: 'SpiralCanvas' object has no attribute 'animasyon_bitti'`.

- [ ] **Step 3: `ui/spiral_canvas.py`'a QTimer ve animasyon API ekle**

Import bloğuna ekle (mevcut `from PySide6.QtCore import Signal` satırını değiştir):

Mevcut:

```python
from PySide6.QtCore import Signal
```

Şununla değiştir:

```python
from PySide6.QtCore import Signal, QTimer
```

Mevcut sinyal bloğu:

```python
    nokta_hover = Signal(int)
    nokta_hover_iptal = Signal()
    nokta_tiklandi = Signal(int)
```

Şununla değiştir:

```python
    nokta_hover = Signal(int)
    nokta_hover_iptal = Signal()
    nokta_tiklandi = Signal(int)
    animasyon_bitti = Signal()
```

`__init__` sonundaki "Mevcut durum" bloğuna animasyon state'i ekle. Task 4 sonrasında bu blok şuna benziyor:

```python
        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()
        # Statik scatter referansı — _kare_ciz tarafından kullanılır
        self._scatter = None
```

Şununla değiştir:

```python
        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()
        # Statik scatter referansı — _kare_ciz tarafından kullanılır
        self._scatter = None
        # Animasyon state
        self._anim_kare: int = -1
        self._anim_toplam: int = 0
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._animasyon_tick)
```

Sınıfın sonuna üç yeni metod ekle:

```python
    def animasyonu_basla(self, toplam_n: int, aci_derece: float, interval_ms: int) -> None:
        """
        Animasyonu başlatır. interval_ms <= 1 ise tek karede tüm tohumları çizer
        ve animasyon_bitti sinyalini hemen yayar.
        """
        # Önceki animasyon varsa durdur
        if self._timer.isActive():
            self._timer.stop()

        self._anim_toplam = toplam_n
        self._aci_derece = aci_derece
        self._anim_kare = -1

        # Konumları ve Fibonacci indekslerini hesapla
        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(toplam_n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(toplam_n)
        self._n = toplam_n

        # Anında modu: tek karede son kareyi çiz
        if interval_ms <= 1:
            self._anim_kare = toplam_n - 1
            self._kare_ciz(
                kare_no=self._anim_kare,
                toplam=toplam_n,
                konumlar=self._konumlar,
                fib_indeksleri=self._fib_indeksleri,
            )
            self.animasyon_bitti.emit()
            return

        # Sahneyi sıfırla (kare_no=-1 → tüm tohumlar gri)
        self._kare_ciz(
            kare_no=-1,
            toplam=toplam_n,
            konumlar=self._konumlar,
            fib_indeksleri=self._fib_indeksleri,
        )

        self._timer.setInterval(interval_ms)
        self._timer.start()

    def animasyonu_durdur(self) -> None:
        """Animasyonu durdurur; sahne mevcut karede donar."""
        if self._timer.isActive():
            self._timer.stop()

    def hiz_guncelle(self, interval_ms: int) -> None:
        """Çalışan animasyonun interval'ını canlı günceller."""
        self._timer.setInterval(interval_ms)

    def _animasyon_tick(self) -> None:
        """QTimer tick — bir sonraki kareyi yerleştir."""
        self._anim_kare += 1
        self._kare_ciz(
            kare_no=self._anim_kare,
            toplam=self._anim_toplam,
            konumlar=self._konumlar,
            fib_indeksleri=self._fib_indeksleri,
        )
        if self._anim_kare >= self._anim_toplam - 1:
            self._timer.stop()
            self.animasyon_bitti.emit()
```

- [ ] **Step 4: Testleri çalıştır**

```bash
python -m pytest tests/test_spiral_canvas.py -v
```

Beklenen: 7 test PASS (3 önceki `_kare_ciz` + 4 yeni animasyon).

- [ ] **Step 5: Regresyon kontrolü**

```bash
python -m pytest tests/ -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 6: Commit**

```bash
git add ui/spiral_canvas.py tests/test_spiral_canvas.py
git commit -m "ui: SpiralCanvas — QTimer animasyonu + animasyon_bitti sinyali"
```

---

## Task 6: SpiralCanvas — scroll zoom + drag pan + `sigdir()`

**Files:**
- Modify: `ui/spiral_canvas.py`
- Modify: `tests/test_spiral_canvas.py`

- [ ] **Step 1: Başarısız testleri yaz**

`tests/test_spiral_canvas.py` sonuna ekle:

```python
def test_sigdir_xlim_ylim_yeniden_ayarlar(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(100, 137.5)
    # Manuel olarak xlim'i bozulmuş bir aralığa ayarla
    canvas._axes.set_xlim(-1000, 1000)
    canvas._axes.set_ylim(-1000, 1000)
    canvas.sigdir()
    xmin, xmax = canvas._axes.get_xlim()
    ymin, ymax = canvas._axes.get_ylim()
    # Sığdırıldıktan sonra çok daha dar bir aralık olmalı
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
    # Scroll event simüle et
    event = MagicMock()
    event.inaxes = canvas._axes
    event.xdata = (xmin0 + xmax0) / 2  # merkez
    event.ydata = 0
    event.button = "up"
    event.step = 1
    canvas._scroll_handler(event)
    xmin1, xmax1 = canvas._axes.get_xlim()
    aralik1 = xmax1 - xmin1
    assert aralik1 < aralik0  # zoom in → aralık daraldı


def test_pan_press_motion_release_xlim_kaydirir(qtbot):
    """Drag press → motion → release xlim'i kaydırır (eşik aşıldıysa)."""
    from unittest.mock import MagicMock
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(100, 137.5)
    canvas.sigdir()
    xmin0, xmax0 = canvas._axes.get_xlim()

    press = MagicMock()
    press.inaxes = canvas._axes
    press.button = 1  # sol-tık
    press.x = 100  # piksel
    press.y = 100
    press.xdata = (xmin0 + xmax0) / 2
    press.ydata = 0
    canvas._press_handler(press)

    motion = MagicMock()
    motion.inaxes = canvas._axes
    motion.x = 150  # 50 piksel sağa hareket (eşiği aşar)
    motion.y = 100
    motion.xdata = press.xdata + 5.0
    motion.ydata = 0
    canvas._motion_pan_handler(motion)

    release = MagicMock()
    release.button = 1
    canvas._release_handler(release)

    xmin1, xmax1 = canvas._axes.get_xlim()
    # Pan → xlim kaydı
    assert xmin1 != xmin0
```

- [ ] **Step 2: Testleri çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_spiral_canvas.py::test_sigdir_xlim_ylim_yeniden_ayarlar -v
```

Beklenen: FAIL — `AttributeError: 'SpiralCanvas' object has no attribute 'sigdir'`.

- [ ] **Step 3: `ui/spiral_canvas.py`'a scroll/pan/sigdir kodlarını ekle**

`__init__` içinde mevcut motion/click bağlantı satırlarını bul:

```python
        # Hover/click bağlantıları
        self._canvas.mpl_connect("motion_notify_event", self._hover_handler)
        self._canvas.mpl_connect("button_press_event", self._click_handler)
```

Şununla değiştir (yeni handler'lar da bağlanır, mevcut handler'lar korunur):

```python
        # Hover/click bağlantıları
        self._canvas.mpl_connect("motion_notify_event", self._hover_handler)
        self._canvas.mpl_connect("motion_notify_event", self._motion_pan_handler)
        self._canvas.mpl_connect("button_press_event", self._press_handler)
        self._canvas.mpl_connect("button_release_event", self._release_handler)
        self._canvas.mpl_connect("scroll_event", self._scroll_handler)

        # Pan state
        self._press_pixel: tuple[float, float] | None = None
        self._press_data: tuple[float, float] | None = None
        self._panning: bool = False
        self._pan_esik_px: float = 5.0
```

Eski `_click_handler`'ı sil (artık `_press_handler` + `_release_handler` kullanılıyor — drag eşiği için).

Sınıfın sonuna yeni metodları ekle:

```python
    # ---- Sığdır ----

    def sigdir(self) -> None:
        """xlim/ylim'i çizilen veri sınırına %5 padding ile yeniden oturt."""
        if not self._konumlar:
            return
        xs = [p[0] for p in self._konumlar]
        ys = [p[1] for p in self._konumlar]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        pad_x = (xmax - xmin) * 0.05 + 1.0
        pad_y = (ymax - ymin) * 0.05 + 1.0
        self._axes.set_xlim(xmin - pad_x, xmax + pad_x)
        self._axes.set_ylim(ymin - pad_y, ymax + pad_y)
        self._canvas.draw_idle()

    # ---- Scroll zoom ----

    def _scroll_handler(self, event) -> None:
        """İmleç-merkezli zoom in/out (scroll wheel)."""
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            return
        # button="up" → zoom in (1.2× yakın), "down" → zoom out (1.2× uzak)
        olcek = 1 / 1.2 if (event.button == "up" or event.step > 0) else 1.2
        xmin, xmax = self._axes.get_xlim()
        ymin, ymax = self._axes.get_ylim()
        cx, cy = event.xdata, event.ydata
        # Yeni aralık imleç sabit kalacak şekilde
        yeni_xmin = cx - (cx - xmin) * olcek
        yeni_xmax = cx + (xmax - cx) * olcek
        yeni_ymin = cy - (cy - ymin) * olcek
        yeni_ymax = cy + (ymax - cy) * olcek
        self._axes.set_xlim(yeni_xmin, yeni_xmax)
        self._axes.set_ylim(yeni_ymin, yeni_ymax)
        self._canvas.draw_idle()

    # ---- Pan (sol-tık + drag) ----

    def _press_handler(self, event) -> None:
        """Sol-tık press: pan anchor'ı kaydet."""
        if event.button != 1 or event.inaxes != self._axes:
            return
        if event.x is None or event.y is None or event.xdata is None or event.ydata is None:
            return
        self._press_pixel = (event.x, event.y)
        self._press_data = (event.xdata, event.ydata)
        self._panning = False

    def _motion_pan_handler(self, event) -> None:
        """Press anchor varsa eşik kontrolüyle pan veya hover-passthrough."""
        if self._press_pixel is None:
            return
        if event.x is None or event.y is None or event.inaxes != self._axes:
            return
        dx_px = event.x - self._press_pixel[0]
        dy_px = event.y - self._press_pixel[1]
        if not self._panning:
            if (dx_px * dx_px + dy_px * dy_px) < (self._pan_esik_px * self._pan_esik_px):
                return
            self._panning = True

        # Pan modunda: xlim/ylim'i veri koordinat farkıyla kaydır
        if event.xdata is None or event.ydata is None:
            return
        dx_data = event.xdata - self._press_data[0]
        dy_data = event.ydata - self._press_data[1]
        xmin, xmax = self._axes.get_xlim()
        ymin, ymax = self._axes.get_ylim()
        self._axes.set_xlim(xmin - dx_data, xmax - dx_data)
        self._axes.set_ylim(ymin - dy_data, ymax - dy_data)
        self._canvas.draw_idle()

    def _release_handler(self, event) -> None:
        """Sol-tık release: pan değilse tıklama olarak yorumla."""
        if event.button != 1 or self._press_pixel is None:
            return
        if not self._panning:
            # Tıklama — en yakın tohumu bul ve sinyal yay
            idx = self._en_yakin_nokta_data(self._press_data[0], self._press_data[1])
            if idx is not None:
                self.nokta_tiklandi.emit(idx)
        self._press_pixel = None
        self._press_data = None
        self._panning = False

    def _en_yakin_nokta_data(self, xd: float, yd: float) -> Optional[int]:
        """Veri koordinatında en yakın tohumu döndürür (esik 3.0)."""
        esik = 3.0
        en_yakin: Optional[int] = None
        en_yakin_mes = float("inf")
        for i, (x, y) in enumerate(self._konumlar):
            d = math.hypot(x - xd, y - yd)
            if d < esik and d < en_yakin_mes:
                en_yakin_mes = d
                en_yakin = i
        return en_yakin
```

- [ ] **Step 4: Testleri çalıştır**

```bash
python -m pytest tests/test_spiral_canvas.py -v
```

Beklenen: 10 test PASS (3 _kare_ciz + 4 animasyon + 3 zoom/pan).

- [ ] **Step 5: Regresyon kontrolü**

```bash
python -m pytest tests/ -v
```

Beklenen: tüm testler PASS. Eğer `tests/test_main_window.py::test_main_window_info_card_n_degistirir` ya da hover testleri kırıldıysa, `_click_handler` kaldırılırken bağlantı kaybedildi demektir — `_press_handler` + `_release_handler` zaten tıklama davranışını koruyor, kontrol et.

- [ ] **Step 6: Commit**

```bash
git add ui/spiral_canvas.py tests/test_spiral_canvas.py
git commit -m "ui: SpiralCanvas — scroll zoom + drag pan + sigdir"
```

---

## Task 7: MainWindow — sinyalleri bağla

**Files:**
- Modify: `ui/main_window.py`
- Modify: `tests/test_main_window.py`

- [ ] **Step 1: Başarısız testleri yaz**

`tests/test_main_window.py` sonuna ekle:

```python
def test_main_window_animasyon_butonu_canvas_animasyonu_baslatir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    with patch.object(pencere.canvas, "animasyonu_basla") as mock:
        pencere.top_bar.animasyon_butonu.setChecked(True)
        # Default n=100, default hız Normal → 200ms
        mock.assert_called_once()
        args, kwargs = mock.call_args
        kw = kwargs or dict(zip(["toplam_n", "aci_derece", "interval_ms"], args))
        assert kw.get("toplam_n", args[0] if args else None) == 100
        assert kw.get("interval_ms", args[2] if len(args) > 2 else None) == 200


def test_main_window_animasyon_butonu_kapatma_durdurur(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    with patch.object(pencere.canvas, "animasyonu_durdur") as mock:
        pencere.top_bar.animasyon_butonu.setChecked(False)
        mock.assert_called_once()


def test_main_window_hiz_degisimi_canli_guncellenir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    with patch.object(pencere.canvas, "hiz_guncelle") as mock:
        pencere.top_bar.hiz_kutu.setCurrentText("Hızlı")
        mock.assert_called_once_with(interval_ms=50)


def test_main_window_animasyon_bitti_butonu_off_yapar(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    assert pencere.top_bar.animasyon_butonu.isChecked() is True
    pencere.canvas.animasyon_bitti.emit()
    assert pencere.top_bar.animasyon_butonu.isChecked() is False


def test_main_window_ciz_animasyonu_iptal_eder(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.animasyon_butonu.setChecked(True)
    assert pencere.top_bar.animasyon_butonu.isChecked() is True
    with patch.object(pencere.canvas, "animasyonu_durdur") as mock:
        pencere.top_bar.ciz_butonu.click()
        mock.assert_called_once()
    assert pencere.top_bar.animasyon_butonu.isChecked() is False


def test_main_window_sigdir_butonu_canvas_sigdir_cagirir(qtbot):
    from unittest.mock import patch
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    with patch.object(pencere.canvas, "sigdir") as mock:
        pencere.top_bar.sigdir_butonu.click()
        mock.assert_called_once()
```

- [ ] **Step 2: Testleri çalıştır, başarısızlığı gör**

```bash
python -m pytest tests/test_main_window.py::test_main_window_animasyon_butonu_canvas_animasyonu_baslatir -v
```

Beklenen: FAIL — animasyon butonu hâlâ bağlı değil, mock çağrılmıyor.

- [ ] **Step 3: `ui/main_window.py`'da sinyalleri bağla ve handler'ları ekle**

Mevcut `__init__` içinde "Pencere yöneticisi + menü bağlantısı" bloğundan ÖNCE şu satırları ekle:

Mevcut:

```python
        # Pencere yöneticisi + menü bağlantısı
        self._pencere_yoneticisi = WindowManager()
        self.top_bar.menu_eylemi.connect(self._menu_eylemi_geldi)
```

Şununla değiştir:

```python
        # Animasyon + sığdır bağlantıları
        self.top_bar.animasyon_toggled.connect(self._animasyon_toggle_geldi)
        self.top_bar.hiz_degisti.connect(self._hiz_degisti)
        self.top_bar.sigdir_istendi.connect(self.canvas.sigdir)
        self.canvas.animasyon_bitti.connect(self._animasyon_bitti)

        # Pencere yöneticisi + menü bağlantısı
        self._pencere_yoneticisi = WindowManager()
        self.top_bar.menu_eylemi.connect(self._menu_eylemi_geldi)
```

Mevcut `_cizim_istendi` metodunu:

```python
    def _cizim_istendi(self, n: int, aci_derece: float) -> None:
        self.canvas.spirali_ciz(n, aci_derece)
        self.info_card.n_degisti(n)
```

Şununla değiştir (animasyon iptal):

```python
    def _cizim_istendi(self, n: int, aci_derece: float) -> None:
        # Çalışan animasyonu iptal
        if self.top_bar.animasyon_butonu.isChecked():
            self.canvas.animasyonu_durdur()
            self.top_bar.animasyon_butonu.setChecked(False)
        self.canvas.spirali_ciz(n, aci_derece)
        self.info_card.n_degisti(n)
```

Sınıfın sonuna (mevcut `_menu_eylemi_geldi`'nin altına) yeni metodlar ekle:

```python
    def _animasyon_toggle_geldi(self, basili: bool) -> None:
        """Animasyon butonu durumu değişti."""
        if basili:
            n = self.top_bar.n_kutu.value()
            aci = self.top_bar.aci_kutu.value()
            interval = self._mevcut_interval_ms()
            self.canvas.animasyonu_basla(toplam_n=n, aci_derece=aci, interval_ms=interval)
        else:
            self.canvas.animasyonu_durdur()

    def _hiz_degisti(self, ad: str) -> None:
        """Hız ComboBox seçimi değişti."""
        interval = self._mevcut_interval_ms()
        # Animasyon çalışıyorsa canlı güncelle
        if self.top_bar.animasyon_butonu.isChecked():
            self.canvas.hiz_guncelle(interval_ms=interval)

    def _mevcut_interval_ms(self) -> int:
        """Seçili Hız adına karşılık gelen ms değerini döndürür."""
        hiz_haritasi = {"Yavaş": 500, "Normal": 200, "Hızlı": 50, "Anında": 1}
        return hiz_haritasi.get(self.top_bar.hiz_kutu.currentText(), 200)

    def _animasyon_bitti(self) -> None:
        """Canvas animasyon_bitti yaydı — buton state'ini OFF yap."""
        if self.top_bar.animasyon_butonu.isChecked():
            self.top_bar.animasyon_butonu.setChecked(False)
```

- [ ] **Step 4: Testleri çalıştır**

```bash
python -m pytest tests/test_main_window.py -v
```

Beklenen: 11 test PASS (5 mevcut + 6 yeni).

- [ ] **Step 5: Regresyon kontrolü**

```bash
python -m pytest tests/ -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 6: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "ui: MainWindow — animasyon, hız, sığdır sinyalleri bağlandı"
```

---

## Task 8: Manuel görsel doğrulama

**Files:** (sadece çalıştırma, dosya değişikliği yok)

- [ ] **Step 1: Uygulamayı başlat**

```bash
python main.py
```

- [ ] **Step 2: Animasyon senaryoları**

1. Default açılış: spiral n=100 ile statik görünür.
2. Hız: **Normal** seçili, **▶ Animasyon**'a bas → 100 tohum 200ms × 100 = ~20 sn içinde tek tek görünür; aktif tohum kırmızı, geçenler kırmızı (Fibonacci) veya lacivert, bekleyenler gri.
3. Animasyon biterken Animasyon butonu otomatik OFF olur, tam spiral kalır.
4. Animasyon çalışırken **Hız: Hızlı** seç → animasyon canlı hızlanır.
5. Animasyon çalışırken **Hız: Anında** seç → bir sonraki tick'te tüm tohumlar dolar, animasyon biter.
6. **Hız: Anında** + Animasyon butonu → anında tam spiral.
7. Animasyon çalışırken **Çiz**'e bas → animasyon iptal, yeni n/α ile anında tam spiral, Animasyon butonu OFF.

- [ ] **Step 3: Zoom/pan senaryoları**

1. Spiral üzerinde mouse scroll ↑ → imleç-merkezli zoom in.
2. Mouse scroll ↓ → zoom out.
3. Boş alanda sol-tık + drag → spiral kayar (pan).
4. Bir tohum üzerine kısa tıkla → seçim çalışır (InfoCard "seçili tohum: N" gösterir, pan başlamaz).
5. **↺ Sığdır** butonuna bas → görünüm spirale otomatik yeniden oturur.

- [ ] **Step 4: Regresyon — diğer davranışlar**

1. Menü öğeleri (Graf/Algoritma/Görselleştir) hâlâ placeholder açar.
2. Tek-instance kuralı hâlâ çalışır (aynı menü iki kez yeni pencere açmaz).
3. Hover ile InfoCard "seçili tohum: N" hâlâ güncellenir.

- [ ] **Step 5: Eski Tk regresyonu**

```bash
python main_legacy.py
```

Eski Tk arayüzü hâlâ açılmalı.

- [ ] **Step 6: Sorun varsa raporla, yoksa plan biter**

Manuel test sırasında bulduğun her sorunu plan'a Task 9 olarak ekle ve düzelt.

---

## Plan tamamlandı — son kontrol

- [ ] **Tüm testler geçiyor**

```bash
python -m pytest -v
```

Beklenen: önceki 59 + yeni testler (~76+) PASS.

- [ ] **Manuel kabul kontrol listesi**

`python main.py` ile:
- [ ] **▶ Animasyon** açılınca tohumlar tek tek yerleşir, biter biter Animasyon butonu kendi OFF olur.
- [ ] **Hız** combobox 4 öğe gösterir; canlı değişim animasyonu yeniden başlatmadan hızlandırır.
- [ ] Animasyon çalışırken **Çiz**'e basınca animasyon iptal, anında spiral, buton OFF.
- [ ] Mouse scroll = zoom, sol-tık drag = pan, kısa tıklama = seçim.
- [ ] **↺ Sığdır** butonu görünümü spirale yeniden oturtur.

`python main_legacy.py` ile:
- [ ] Eski Tk arayüzü hâlâ çalışır (regresyon yok).
