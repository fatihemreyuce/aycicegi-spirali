# Fibonacci Doğrulayıcı Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PySide6'da Fibonacci Doğrulayıcı penceresini gerçek içeriğe port et; SpiralCanvas'a cross-window mavi vurgu API'si ekle; MainWindow `graf.validator` menü öğesini placeholder yerine gerçek pencereye bağla.

**Architecture:** `ui/theme.py` MAVI_VURGU rengi ekler. `ui/spiral_canvas.py` `vurgu_ekle/temizle` API'si + öncelik listesinde 3. sıra. `ui/windows/fibonacci_validator.py` yeni AnalyticsWindow alt sınıfı, `tohum_vurgula(int)` ve `vurgu_temizle()` sinyalleri yayar. `ui/main_window.py` placeholder yerine fabrika kullanır + sinyalleri canvas API'sine bağlar.

**Tech Stack:** PySide6 (`QLineEdit`, `QIntValidator`, `QPushButton`, `QLabel`, `Signal`), domain modülleri (`validator.py`, `fibonacci.py`), pytest-qt.

---

## Task 1: Tema MAVI_VURGU rengi

**Files:**
- Modify: `ui/theme.py`
- Modify: `tests/test_theme.py`

- [ ] **Step 1: Test'e MAVI_VURGU ekle**

`tests/test_theme.py` içindeki `test_renk_sabitleri_hex_formatinda` renk listesinin sonuna `"MAVI_VURGU"` ekle.

- [ ] **Step 2: Testi koş → FAIL**

```bash
python -m pytest tests/test_theme.py::test_renk_sabitleri_hex_formatinda -v
```

Beklenen: `AttributeError: module 'ui.theme' has no attribute 'MAVI_VURGU'`.

- [ ] **Step 3: `ui/theme.py`'a sabit ekle**

`BEKLEME` satırının altına:

```python
MAVI_VURGU: str = "#1f8bff"          # Validator doğrulanan tohum vurgusu
```

- [ ] **Step 4: Testleri koş → PASS**

```bash
python -m pytest tests/test_theme.py -v
```

Beklenen: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/theme.py tests/test_theme.py
git commit -m "ui: MAVI_VURGU rengi (validator vurgu)"
```

---

## Task 2: SpiralCanvas — vurgu_ekle/temizle API

**Files:**
- Modify: `ui/spiral_canvas.py`
- Modify: `tests/test_spiral_canvas.py`

- [ ] **Step 1: Başarısız testler yaz**

`tests/test_spiral_canvas.py` sonuna ekle:

```python
def test_vurgu_ekle_mavi_renk(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)
    canvas.vurgu_ekle(5)  # 5. tohum mavi olmalı
    renkler = _renk_listesi(canvas)
    assert renkler[5].lower() == theme.MAVI_VURGU.lower()


def test_vurgu_temizle_eski_vurguyu_kaldirir(qtbot):
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)
    canvas.vurgu_ekle(5)
    canvas.vurgu_temizle()
    renkler = _renk_listesi(canvas)
    # 5. tohum artık mavi değil (Fibonacci olmadığı için lacivert olmalı)
    assert renkler[5].lower() != theme.MAVI_VURGU.lower()


def test_vurgu_oncelik_fibonacci_uzerine_yazar(qtbot):
    """Vurgu ile Fibonacci aynı indeksteyse → mavi gözüksün."""
    canvas = SpiralCanvas()
    qtbot.addWidget(canvas)
    canvas.spirali_ciz(10, 137.5)  # 0,1,2,3,5,8 Fibonacci
    canvas.vurgu_ekle(8)  # 8 hem Fibonacci hem vurgu — mavi öncelikli
    renkler = _renk_listesi(canvas)
    assert renkler[8].lower() == theme.MAVI_VURGU.lower()
```

- [ ] **Step 2: Testi koş → FAIL**

```bash
python -m pytest tests/test_spiral_canvas.py::test_vurgu_ekle_mavi_renk -v
```

Beklenen: `AttributeError: 'SpiralCanvas' object has no attribute 'vurgu_ekle'`.

- [ ] **Step 3: `ui/spiral_canvas.py`'a vurgu state ve API ekle**

`__init__` "Mevcut durum" bloğunda animasyon state'inden sonra ekle (`self._timer = QTimer(self)` satırlarından önce):

Mevcut:
```python
        # Animasyon state
        self._anim_kare: int = -1
        self._anim_toplam: int = 0
        self._timer = QTimer(self)
```

Şununla değiştir:
```python
        # Validator vurgu state — cross-window'den gelen tohum indeksleri
        self._vurgu_indeksleri: set[int] = set()
        # Animasyon state
        self._anim_kare: int = -1
        self._anim_toplam: int = 0
        self._timer = QTimer(self)
```

`_kare_ciz` içindeki renk hesaplama döngüsünü güncelle:

Mevcut:
```python
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
```

Şununla değiştir:
```python
        renkler: list[str] = []
        for i in range(toplam):
            if i > kare_no:
                renkler.append(theme.BEKLEME)
            elif i == kare_no:
                renkler.append(theme.VURGU)
            elif i in self._vurgu_indeksleri:
                renkler.append(theme.MAVI_VURGU)
            elif i in fib_indeksleri:
                renkler.append(theme.VURGU)
            else:
                renkler.append(theme.METIN_ANA)
```

Sınıfın sonuna `vurgu_ekle` / `vurgu_temizle` metodlarını ekle (`_animasyon_tick`'in altı):

```python
    # ---- Validator vurgu (cross-window) ----

    def vurgu_ekle(self, idx: int) -> None:
        """Verilen tohum indeksini mavi vurgu kümesine ekle ve yeniden çiz."""
        self._vurgu_indeksleri.add(idx)
        if self._konumlar:
            self._yeniden_ciz()

    def vurgu_temizle(self) -> None:
        """Tüm validator vurgularını temizle ve yeniden çiz."""
        if not self._vurgu_indeksleri:
            return
        self._vurgu_indeksleri.clear()
        if self._konumlar:
            self._yeniden_ciz()
```

**NOT:** Mevcut `_kare_ciz`'in aktif tohum kontrolünü (`elif i == kare_no`) güncellersek aktif tohum mavi vurgu görür duruma gelir. Sıralama: aktif > mavi > fib > lacivert. Mavi vurgu sadece **ziyaret edilmiş** tohumlar için anlamlı; bekleyen tohum mavi olamaz çünkü `i > kare_no` zaten önce alıyor.

- [ ] **Step 4: Testleri koş → PASS**

```bash
python -m pytest tests/test_spiral_canvas.py -v
```

Beklenen: 13 PASS (10 mevcut + 3 yeni).

- [ ] **Step 5: Commit**

```bash
git add ui/spiral_canvas.py tests/test_spiral_canvas.py
git commit -m "ui: SpiralCanvas — vurgu_ekle/temizle API (validator için)"
```

---

## Task 3: FibonacciValidatorPenceresi

**Files:**
- Create: `ui/windows/fibonacci_validator.py`
- Create: `tests/test_fibonacci_validator.py`

- [ ] **Step 1: Test dosyasını yaz**

`tests/test_fibonacci_validator.py`:

```python
"""FibonacciValidatorPenceresi — sinyaller + sonuç gösterimi."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi


def test_accept_sinyali_dogru_indeksi_yayar(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("21")
    with qtbot.waitSignal(pencere.tohum_vurgula, timeout=500) as kayit:
        pencere.dogrula_butonu.click()
    assert kayit.args == [8]  # F(8) = 21
    assert "Accept" in pencere.sonuc_etiketi.text()


def test_reject_vurgu_temizle_yayar(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("22")
    with qtbot.waitSignal(pencere.vurgu_temizle, timeout=500):
        pencere.dogrula_butonu.click()
    assert "Reject" in pencere.sonuc_etiketi.text()
    # Alt etiket en yakın 2 Fibonacci'yi göstermeli
    alt = pencere.alt_etiketi.text()
    assert "21" in alt and "34" in alt


def test_enter_tetikler_dogrula(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    pencere.giris_kutu.setText("89")
    with qtbot.waitSignal(pencere.tohum_vurgula, timeout=500):
        # QLineEdit returnPressed
        pencere.giris_kutu.returnPressed.emit()


def test_kapanma_vurguyu_temizler(qtbot):
    pencere = FibonacciValidatorPenceresi(mevcut_n=100)
    qtbot.addWidget(pencere)
    with qtbot.waitSignal(pencere.vurgu_temizle, timeout=500):
        pencere.close()
```

- [ ] **Step 2: Testi koş → FAIL**

```bash
python -m pytest tests/test_fibonacci_validator.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'ui.windows.fibonacci_validator'`.

- [ ] **Step 3: `ui/windows/fibonacci_validator.py`'i yaz**

```python
"""
ui.windows.fibonacci_validator
------------------------------
Bir tam sayı için Fibonacci doğrulaması. Accept ise tohum_vurgula(idx)
sinyali ile ana SpiralCanvas'a mavi vurgu yansıtılır; Reject veya
pencere kapanışında vurgu_temizle() yayılır.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from fibonacci import fibonacci_dizisi
from validator import (
    dogrula_ve_index,
    en_yakin_iki_fibonacci_indeksli,
    SONUC_ACCEPT,
)
from ui import theme
from ui.windows.base import AnalyticsWindow


class FibonacciValidatorPenceresi(AnalyticsWindow):
    BASLIK = "Fibonacci Doğrulayıcı"

    tohum_vurgula = Signal(int)
    vurgu_temizle = Signal()

    def __init__(self, mevcut_n: int = 100) -> None:
        super().__init__()
        self._mevcut_n = max(int(mevcut_n), 2)
        self.resize(420, 220)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(16, 16, 16, 16)
        duzen.setSpacing(10)

        baslik = QLabel("Bir tam sayı yazıp Fibonacci dizisinde olup\nolmadığını kontrol edin.")
        baslik.setWordWrap(True)
        duzen.addWidget(baslik)

        giris_satiri = QHBoxLayout()
        giris_satiri.addWidget(QLabel("Sayı:"))
        self.giris_kutu = QLineEdit()
        self.giris_kutu.setValidator(QIntValidator(0, 10**12, self))
        self.giris_kutu.setPlaceholderText("örn. 21, 89, 144")
        giris_satiri.addWidget(self.giris_kutu, 1)

        self.dogrula_butonu = QPushButton("Doğrula")
        self.dogrula_butonu.setProperty("primary", True)
        self.dogrula_butonu.clicked.connect(self._dogrula)
        self.giris_kutu.returnPressed.connect(self._dogrula)
        giris_satiri.addWidget(self.dogrula_butonu)

        duzen.addLayout(giris_satiri)

        self.sonuc_etiketi = QLabel("")
        self.sonuc_etiketi.setWordWrap(True)
        f = self.sonuc_etiketi.font()
        f.setPointSize(13)
        f.setBold(True)
        self.sonuc_etiketi.setFont(f)
        duzen.addWidget(self.sonuc_etiketi)

        self.alt_etiketi = QLabel("")
        self.alt_etiketi.setWordWrap(True)
        duzen.addWidget(self.alt_etiketi)

        duzen.addStretch(1)

    def _dogrula(self) -> None:
        metin = self.giris_kutu.text().strip()
        if not metin:
            return
        try:
            sayi = int(metin)
        except ValueError:
            return

        graf_dizi = fibonacci_dizisi(self._mevcut_n + 1)[: self._mevcut_n]
        sonuc, idx = dogrula_ve_index(sayi, graf_dizi)
        if sonuc == SONUC_ACCEPT and idx is not None:
            f_val = graf_dizi[idx]
            self.sonuc_etiketi.setText(f"✅ Accept: v{idx} düğümü (F={f_val})")
            self.sonuc_etiketi.setStyleSheet(f"color: {theme.AKSAN};")
            self.alt_etiketi.setText("")
            self.tohum_vurgula.emit(idx)
        else:
            (alt_idx, alt_val), (ust_idx, ust_val) = en_yakin_iki_fibonacci_indeksli(
                sayi, graf_dizi
            )
            self.sonuc_etiketi.setText(f"❌ Reject: {sayi} Fibonacci değil")
            self.sonuc_etiketi.setStyleSheet(f"color: {theme.VURGU};")
            parcalar = []
            if alt_idx is not None and alt_val is not None:
                parcalar.append(f"F({alt_idx})={alt_val}")
            if ust_idx is not None and ust_val is not None:
                parcalar.append(f"F({ust_idx})={ust_val}")
            self.alt_etiketi.setText("En yakın: " + ", ".join(parcalar) if parcalar else "")
            self.vurgu_temizle.emit()

    def closeEvent(self, event):  # noqa: N802 (Qt API)
        self.vurgu_temizle.emit()
        super().closeEvent(event)
```

- [ ] **Step 4: Testleri koş → PASS**

```bash
python -m pytest tests/test_fibonacci_validator.py -v
```

Beklenen: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/windows/fibonacci_validator.py tests/test_fibonacci_validator.py
git commit -m "ui: FibonacciValidatorPenceresi — Accept/Reject + tohum_vurgula sinyali"
```

---

## Task 4: MainWindow — placeholder yerine gerçek pencereye yönlendir

**Files:**
- Modify: `ui/main_window.py`
- Modify: `tests/test_main_window.py`

- [ ] **Step 1: Başarısız test yaz**

`tests/test_main_window.py` sonuna ekle:

```python
def test_main_window_graf_validator_acinca_gercek_pencere(qtbot):
    from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.validator")
    yonetici = pencere._pencere_yoneticisi
    p = yonetici._pencereler["graf.validator"]
    qtbot.addWidget(p)
    assert isinstance(p, FibonacciValidatorPenceresi)


def test_main_window_validator_accept_canvas_vurgu_ekler(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.validator")
    p = pencere._pencere_yoneticisi._pencereler["graf.validator"]
    qtbot.addWidget(p)
    p.giris_kutu.setText("21")
    p.dogrula_butonu.click()
    assert 8 in pencere.canvas._vurgu_indeksleri  # F(8) = 21
```

- [ ] **Step 2: Testi koş → FAIL**

```bash
python -m pytest tests/test_main_window.py::test_main_window_graf_validator_acinca_gercek_pencere -v
```

Beklenen: `assert isinstance(p, FibonacciValidatorPenceresi)` FAIL — şu an `PlaceholderWindow` üretiyor.

- [ ] **Step 3: `ui/main_window.py` import + `_menu_eylemi_geldi`**

Mevcut import:
```python
from ui.windows.placeholder import PlaceholderWindow
```

Şununla değiştir:
```python
from ui.windows.placeholder import PlaceholderWindow
from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi
```

`_menu_eylemi_geldi` metodunu güncelle:

Mevcut:
```python
    def _menu_eylemi_geldi(self, eylem_id: str) -> None:
        baslik = MENU_BASLIKLARI.get(eylem_id, eylem_id)
        self._pencere_yoneticisi.ac_veya_one_getir(
            eylem_id,
            lambda: PlaceholderWindow(eylem_id, baslik),
        )
```

Şununla değiştir:
```python
    def _menu_eylemi_geldi(self, eylem_id: str) -> None:
        baslik = MENU_BASLIKLARI.get(eylem_id, eylem_id)
        if eylem_id == "graf.validator":
            pencere = self._pencere_yoneticisi.ac_veya_one_getir(
                eylem_id,
                lambda: self._fibonacci_validator_yarat(),
            )
            return
        self._pencere_yoneticisi.ac_veya_one_getir(
            eylem_id,
            lambda: PlaceholderWindow(eylem_id, baslik),
        )

    def _fibonacci_validator_yarat(self) -> FibonacciValidatorPenceresi:
        """FibonacciValidatorPenceresi'ni mevcut n ile kur ve sinyalleri bağla."""
        p = FibonacciValidatorPenceresi(mevcut_n=self.top_bar.n_kutu.value())
        p.tohum_vurgula.connect(self.canvas.vurgu_ekle)
        p.vurgu_temizle.connect(self.canvas.vurgu_temizle)
        return p
```

- [ ] **Step 4: Testleri koş → PASS**

```bash
python -m pytest tests/test_main_window.py -v
```

Beklenen: 13 PASS (11 mevcut + 2 yeni).

- [ ] **Step 5: Tam regresyon**

```bash
python -m pytest tests/ -v
```

Beklenen: ~88 PASS.

- [ ] **Step 6: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "ui: graf.validator → FibonacciValidatorPenceresi + canvas vurgu bağlantısı"
```

---

## Task 5: Manuel görsel doğrulama

**Files:** (sadece çalıştırma)

- [ ] **Step 1: Uygulamayı başlat**

```bash
python main.py
```

- [ ] **Step 2: Senaryolar**

1. n=100, default açılış → spiral statik.
2. **Graf ▾ → Fibonacci Doğrulayıcı** → küçük pencere açılır.
3. Pencerede "21" yaz, **Doğrula** → "✅ Accept: v8 düğümü (F=21)" yeşilimsi. Ana spiralde **8 indeksli tohum mavi vurgu** alır.
4. "89" yaz, **Enter** → "✅ Accept: v11 düğümü (F=89)". Ana spiralde 11 mavi olur, eski 8 lacivert/kırmızı'ya döner (tek vurgu kuralı).
5. "22" yaz, **Doğrula** → "❌ Reject: 22 Fibonacci değil" kırmızı, alt: "En yakın: F(8)=21, F(9)=34". Ana spiraldeki mavi vurgu kaybolur.
6. Pencereyi kapat → mavi vurgu temizlenir.
7. Tekrar Graf ▾ → Fibonacci Doğrulayıcı → yeni instance (tek-instance kuralı: önceki kapandığı için yeni açılır).
8. n=300, Çiz → spirali yenile. Doğrulayıcı pencereyi tekrar aç → büyük Fibonacci'ler (F(11)=89, F(12)=144, F(13)=233) accept eder.

- [ ] **Step 3: Sorun varsa raporla, yoksa plan biter**
