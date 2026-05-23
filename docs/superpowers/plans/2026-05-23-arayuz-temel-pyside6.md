# Arayüz Temel — PySide6 Geçişi (Plan 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mevcut Tkinter tabanlı `gui.py` yerine, PySide6 + akademik aydınlık tema ile spiral-merkezli ana pencereyi (üst şerit + spiral canvas + sağ-üst bilgi kartı + analitik pencere altyapısı) ayağa kaldırmak. Plan bittiğinde uygulama açılır, n/α değiştirip Çiz'e basılır, spiral Fibonacci vurgularıyla görünür, hover detay verir; menü öğeleri yer-tutucu pencereler açar (içerikleri sonraki planlarda).

**Architecture:** Domain modüllerine (`fibonacci.py`, `graph_builder.py`, `positioning.py`, `utils.py`, `validator.py`, `graph_traversal.py`) dokunulmuyor. Yeni `ui/` paketi PySide6 ile sunum katmanını sağlıyor: `MainWindow` üst şeridi (`TopBar`) + spiral canvas'ı (`SpiralCanvas`, matplotlib `qtagg` backend) + bilgi kartı (`InfoCard`) içerir. Analitik pencereler `AnalyticsWindow` base class'ından türer ve `WindowManager` aracılığıyla tek-instance kuralı uygulanır. Pencereler ana pencereye `graph_updated` Qt sinyaliyle abone olur.

**Tech Stack:** PySide6 6.x, matplotlib (`backend_qtagg`), networkx (mevcut), pytest + pytest-qt.

**Kapsam dışı:** 9 analitik pencerenin gerçek içeriği (sonraki planlar). Eski `gui.py` / `*_window.py` dosyalarının silinmesi (son planda `legacy/`'ye taşınır). Bu plan boyunca eski uygulama hâlâ `python main_legacy.py` ile çalıştırılabilir tutulur.

---

## File Structure

**Yeni dosyalar:**

| Path | Sorumluluk |
|---|---|
| `ui/__init__.py` | Paket markeri. |
| `ui/theme.py` | Renk + font sabitleri ve global Qt stylesheet üreticisi. |
| `ui/app.py` | `QApplication` kurulumu + `main()` giriş noktası. |
| `ui/main_window.py` | `MainWindow` — üst şerit + canvas + bilgi kartı + pencere yöneticisi sahibi. |
| `ui/top_bar.py` | `TopBar` widget'ı — n / α / Çiz / Animasyon / Yakınlaştır + 3 menü. |
| `ui/spiral_canvas.py` | `SpiralCanvas` — matplotlib qtagg canvas; nokta + Fibonacci vurgusu + hover detay. |
| `ui/info_card.py` | `InfoCard` — spiral overlay'i; F oranı, tohum, imleç. |
| `ui/windows/__init__.py` | Alt paket markeri. |
| `ui/windows/base.py` | `AnalyticsWindow` base + `WindowManager` (tek-instance). |
| `ui/windows/placeholder.py` | Geçici yer-tutucu pencere (9 menü öğesi için ortak). |
| `tests/test_theme.py` | Tema sabitlerinin smoke testi. |
| `tests/test_top_bar.py` | TopBar widget'ı testleri (pytest-qt). |
| `tests/test_main_window.py` | MainWindow açılış + sinyal testi. |
| `tests/test_window_manager.py` | Tek-instance kuralı testi. |
| `tests/conftest.py` | `qapp` fixture (pytest-qt zaten sağlar ama açıkça yapılandırılır). |

**Değiştirilen dosyalar:**

| Path | Değişiklik |
|---|---|
| `requirements.txt` | `PySide6` + `pytest-qt` eklenir. |
| `main.py` | İçeriği `ui.app:main()` çağrısına dönüşür; eski Tk başlatma silinir. |
| `main_legacy.py` *(yeni)* | Eski `from gui import uygulamayi_baslat` içeriği buraya taşınır (geri dönüş için). |

**Dokunulmayan dosyalar:** `fibonacci.py`, `validator.py`, `positioning.py`, `graph_builder.py`, `graph_traversal.py`, `utils.py`, `convergence_plot.py`, `comparison_window.py`, `traversal_window.py`, `dijkstra_window.py`, `animator.py`, `visualizer.py`, `gui.py`. (Sonraki planlarda port edilecekler.)

---

## Task 1: Bağımlılıkları ekle ve ortamı doğrula

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: `requirements.txt`'i güncelle**

`requirements.txt` mevcut hâli:
```
matplotlib>=3.6,<4.0
networkx>=3.0,<4.0
numpy>=1.24,<3.0
scipy>=1.10,<2.0
pytest>=7.0,<9.0
```

Şu satırları ekle (mevcut bloğun sonuna):
```
# UI — PySide6 (Qt 6 Python bağlamaları)
PySide6>=6.6,<7.0

# UI testi — pytest fixture'ları (qtbot vb.)
pytest-qt>=4.2,<5.0
```

- [ ] **Step 2: Bağımlılıkları yükle**

Komut:
```bash
pip install -r requirements.txt
```

Beklenen: PySide6 ve pytest-qt başarıyla kurulur. Hata olursa Python sürümünün ≥3.9 olduğundan emin ol.

- [ ] **Step 3: Kurulumu doğrula**

Komut:
```bash
python -c "import PySide6.QtWidgets; import pytestqt; print('ok')"
```

Beklenen çıktı:
```
ok
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: PySide6 ve pytest-qt eklendi"
```

---

## Task 2: `ui/` paket iskeleti

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/windows/__init__.py`

- [ ] **Step 1: Paket dosyalarını oluştur**

`ui/__init__.py`:
```python
"""ui — PySide6 tabanlı sunum katmanı (akademik aydınlık tema)."""
```

`ui/windows/__init__.py`:
```python
"""ui.windows — bağımsız analitik pencereler."""
```

- [ ] **Step 2: Paket Python'dan görünüyor mu doğrula**

Komut:
```bash
python -c "import ui; import ui.windows; print(ui.__doc__)"
```

Beklenen çıktı: paket docstring'i.

- [ ] **Step 3: Commit**

```bash
git add ui/__init__.py ui/windows/__init__.py
git commit -m "ui: paket iskeleti"
```

---

## Task 3: Tema sabitleri (`ui/theme.py`)

**Files:**
- Create: `ui/theme.py`
- Create: `tests/test_theme.py`

- [ ] **Step 1: Önce başarısız testi yaz**

`tests/test_theme.py`:
```python
"""Tema sabitlerinin var ve doğru tipte olduğunu doğrular (smoke)."""

import re

from ui import theme


HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


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
        deger = getattr(theme, ad)
        assert isinstance(deger, str), f"{ad} string olmalı"
        assert HEX_RE.match(deger), f"{ad} '{deger}' hex formatında değil"


def test_font_sabitleri_tup_uc_eleman():
    assert theme.FONT_GOVDE[0] == "Georgia"
    assert isinstance(theme.FONT_GOVDE[1], int)
    assert theme.FONT_BASLIK[0] == "Georgia"


def test_stylesheet_uretir():
    css = theme.qt_stylesheet()
    assert isinstance(css, str)
    assert theme.AKSAN in css
    assert theme.ARKA_PLAN_ANA in css
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

Komut:
```bash
pytest tests/test_theme.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'ui.theme'`

- [ ] **Step 3: `ui/theme.py`'i yaz**

`ui/theme.py`:
```python
"""
ui.theme
--------
Akademik aydınlık tema — renk paleti, font sabitleri ve global Qt stylesheet.

Tüm widget'lar bu modülden okur; renk veya font değişikliği tek yerden yapılır.
"""

from typing import Tuple


# ---- Renk paleti (Oxford Lacivert) ----

ARKA_PLAN_ANA: str = "#fafaf7"       # Pencere zemini (kağıt rengi)
ARKA_PLAN_KART: str = "#ffffff"      # Beyaz kart/canvas
ARKA_PLAN_OVERLAY: str = "#fcfaf3"   # Bilgi kartı (hafif krem)

KENAR_INCE: str = "#e8e4d8"
KENAR_KALIN: str = "#d8d4c5"

METIN_ANA: str = "#1a2238"           # Gövde — koyu lacivert
METIN_IKINCIL: str = "#666666"
METIN_PASIF: str = "#888888"

AKSAN: str = "#1a4480"               # Oxford lacivert — vurgu, başlık altı
AKSAN_KOYU: str = "#142f5c"          # hover/pressed
VURGU: str = "#b8242a"               # Fibonacci noktaları — uyarı kırmızısı


# ---- Tipografi ----

FONT_GOVDE: Tuple[str, int] = ("Georgia", 11)
FONT_BASLIK: Tuple[str, int, str] = ("Georgia", 13, "bold")
FONT_KUCUK: Tuple[str, int] = ("Georgia", 9)
FONT_MONO: Tuple[str, int] = ("Consolas", 10)


def qt_stylesheet() -> str:
    """Tüm uygulamaya uygulanan global Qt stylesheet'i döndürür."""
    return f"""
        QMainWindow, QWidget {{
            background-color: {ARKA_PLAN_ANA};
            color: {METIN_ANA};
            font-family: "{FONT_GOVDE[0]}";
            font-size: {FONT_GOVDE[1]}pt;
        }}
        QPushButton {{
            background-color: {ARKA_PLAN_KART};
            color: {AKSAN};
            border: 1px solid {KENAR_KALIN};
            padding: 4px 12px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background-color: {ARKA_PLAN_OVERLAY};
        }}
        QPushButton[primary="true"] {{
            background-color: {AKSAN};
            color: {ARKA_PLAN_KART};
            border: 1px solid {AKSAN_KOYU};
        }}
        QPushButton[primary="true"]:hover {{
            background-color: {AKSAN_KOYU};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {ARKA_PLAN_KART};
            color: {AKSAN};
            border: 1px solid {KENAR_KALIN};
            padding: 2px 6px;
            font-weight: bold;
        }}
        QMenu {{
            background-color: {ARKA_PLAN_KART};
            border: 1px solid {KENAR_KALIN};
        }}
        QMenu::item:selected {{
            background-color: {AKSAN};
            color: {ARKA_PLAN_KART};
        }}
        QLabel[role="title"] {{
            font-weight: bold;
            color: {AKSAN};
        }}
    """
```

- [ ] **Step 4: Testi tekrar çalıştır, geçer**

Komut:
```bash
pytest tests/test_theme.py -v
```

Beklenen: 3 test PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/theme.py tests/test_theme.py
git commit -m "ui: tema sabitleri ve global Qt stylesheet"
```

---

## Task 4: Boş `MainWindow` + `ui/app.py` giriş noktası

**Files:**
- Create: `ui/main_window.py`
- Create: `ui/app.py`
- Create: `tests/conftest.py`
- Create: `tests/test_main_window.py`

- [ ] **Step 1: `tests/conftest.py` ile qapp fixture'ı garantiye al**

`tests/conftest.py`:
```python
"""pytest-qt için ortak fixture'lar."""

import os

# Headless CI/sandbox ortamlarında ekran olmayabilir — offscreen platform kullan
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

- [ ] **Step 2: Başarısız test yaz — MainWindow açılmalı**

`tests/test_main_window.py`:
```python
"""MainWindow açılış smoke testi."""

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QMainWindow

from ui.main_window import MainWindow


def test_main_window_acilir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    assert isinstance(pencere, QMainWindow)
    assert pencere.windowTitle().startswith("Ayçiçeği Spirali")
```

- [ ] **Step 3: Testi çalıştır, başarısızlığı gör**

Komut:
```bash
pytest tests/test_main_window.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'ui.main_window'`

- [ ] **Step 4: `ui/main_window.py`'i yaz (en küçük gerekli)**

`ui/main_window.py`:
```python
"""
ui.main_window
--------------
Ana pencere iskeleti. Bu görevde sadece boş bir QMainWindow oluşturuluyor;
sonraki görevler TopBar, SpiralCanvas, InfoCard ekleyecek.
"""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)
```

- [ ] **Step 5: `ui/app.py` giriş noktasını yaz**

`ui/app.py`:
```python
"""
ui.app
------
QApplication kurulumu ve uygulama giriş noktası.
"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import qt_stylesheet


def main() -> int:
    """QApplication başlat, MainWindow göster, event loop'a gir."""
    app = QApplication(sys.argv)
    app.setStyleSheet(qt_stylesheet())
    pencere = MainWindow()
    pencere.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Testi tekrar çalıştır**

Komut:
```bash
pytest tests/test_main_window.py -v
```

Beklenen: PASS.

- [ ] **Step 7: Uygulamayı manuel başlat (görsel doğrulama)**

Komut:
```bash
python -m ui.app
```

Beklenen: 1280×800 boyutunda boş krem zeminli bir pencere açılır, başlık "Ayçiçeği Spirali — Fibonacci & Vogel". Kapatınca çıkar.

- [ ] **Step 8: Commit**

```bash
git add ui/main_window.py ui/app.py tests/conftest.py tests/test_main_window.py
git commit -m "ui: boş MainWindow + QApplication giriş noktası"
```

---

## Task 5: Eski `main.py`'ı yedeğe al, yeni giriş noktasına bağla

**Files:**
- Create: `main_legacy.py`
- Modify: `main.py`

- [ ] **Step 1: Eski `main.py` içeriğini `main_legacy.py`'a kopyala**

`main_legacy.py`:
```python
"""
main_legacy.py
--------------
Eski Tkinter tabanlı arayüzü başlatır. Yeni PySide6 arayüzü tamamlanana
kadar geri dönüş yolu olarak tutulur. Çalıştırma:

    python main_legacy.py
"""

from gui import uygulamayi_baslat


def main() -> None:
    uygulamayi_baslat()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: `main.py`'ı yeni giriş noktasıyla değiştir**

Yeni `main.py` (tüm içerik):
```python
"""
main.py
-------
PySide6 tabanlı yeni arayüzü başlatır.

Çalıştırma:
    python main.py

Eski Tkinter arayüzüne dönmek için: python main_legacy.py
"""

import sys

from ui.app import main as _ui_main


def main() -> None:
    sys.exit(_ui_main())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Her iki giriş noktasını da doğrula**

Komut 1 (yeni):
```bash
python main.py
```
Beklenen: PySide6 boş pencere açılır. Kapatınca çıkar.

Komut 2 (eski):
```bash
python main_legacy.py
```
Beklenen: Eski Tkinter arayüzü açılır (önceki davranış).

- [ ] **Step 4: Commit**

```bash
git add main.py main_legacy.py
git commit -m "main: PySide6 giriş noktasına geçildi (Tk yedek main_legacy.py'da)"
```

---

## Task 6: `TopBar` — kontroller (menüler henüz no-op)

**Files:**
- Create: `ui/top_bar.py`
- Create: `tests/test_top_bar.py`

- [ ] **Step 1: Başarısız test yaz**

`tests/test_top_bar.py`:
```python
"""TopBar widget'ı davranış testleri."""

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QPushButton

from ui.top_bar import TopBar
from utils import ALTIN_ACI_DERECE


def test_topbar_n_kutu_50_2000_arasi(qtbot):
    bar = TopBar()
    qtbot.addWidget(bar)
    assert isinstance(bar.n_kutu, QSpinBox)
    assert bar.n_kutu.minimum() == 50
    assert bar.n_kutu.maximum() == 2000
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
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

Komut:
```bash
pytest tests/test_top_bar.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'ui.top_bar'`

- [ ] **Step 3: `ui/top_bar.py`'i yaz**

`ui/top_bar.py`:
```python
"""
ui.top_bar
----------
Ana pencerenin üst şeridi: n / α / Çiz / Animasyon / Yakınlaştır kontrolleri
ve sağda 3 ana menü (Graf / Algoritma / Görselleştir).

Bu modülde menülerin içeriği henüz bağlanmadı — Task 11'de bağlanacak.
"""

from PySide6.QtCore import Signal
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

from utils import ALTIN_ACI_DERECE


class TopBar(QWidget):
    """
    Her zaman görünür kontrol şeridi.

    Sinyaller:
        cizim_istendi(int, float) — n ve α(derece) ile Çiz'e basıldı.
        animasyon_toggled(bool)   — Animasyon butonu durum değiştirdi.
        yakinlastir_toggled(bool) — Yakınlaştır toggle durum değiştirdi.
        menu_eylemi(str)          — Bir menü öğesi tıklandı; argüman eylem kimliği.
    """

    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    yakinlastir_toggled = Signal(bool)
    menu_eylemi = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(14, 8, 14, 8)
        duzen.setSpacing(10)

        # Sol: Başlık
        baslik = QLabel("🌻 Ayçiçeği Spirali")
        baslik.setProperty("role", "title")
        duzen.addWidget(baslik)
        duzen.addWidget(self._dikey_cizgi())

        # n
        duzen.addWidget(QLabel("n"))
        self.n_kutu = QSpinBox()
        self.n_kutu.setRange(50, 2000)
        self.n_kutu.setValue(100)
        self.n_kutu.setFixedWidth(80)
        duzen.addWidget(self.n_kutu)

        # α
        duzen.addWidget(QLabel("α"))
        self.aci_kutu = QDoubleSpinBox()
        self.aci_kutu.setRange(30.0, 180.0)
        self.aci_kutu.setDecimals(2)
        self.aci_kutu.setSingleStep(0.1)
        self.aci_kutu.setValue(ALTIN_ACI_DERECE)
        self.aci_kutu.setSuffix("°")
        self.aci_kutu.setFixedWidth(100)
        duzen.addWidget(self.aci_kutu)

        # Çiz
        self.ciz_butonu = QPushButton("Çiz")
        self.ciz_butonu.setProperty("primary", True)
        self.ciz_butonu.clicked.connect(self._ciz_tiklandi)
        duzen.addWidget(self.ciz_butonu)

        duzen.addWidget(self._dikey_cizgi())

        # Animasyon
        self.animasyon_butonu = QPushButton("▶ Animasyon")
        self.animasyon_butonu.setCheckable(True)
        self.animasyon_butonu.toggled.connect(self.animasyon_toggled)
        duzen.addWidget(self.animasyon_butonu)

        # Yakınlaştır
        self.yakinlastir_butonu = QToolButton()
        self.yakinlastir_butonu.setText("⊕ Yakınlaştır")
        self.yakinlastir_butonu.setCheckable(True)
        self.yakinlastir_butonu.toggled.connect(self.yakinlastir_toggled)
        duzen.addWidget(self.yakinlastir_butonu)

        # Sağ tarafa it
        duzen.addStretch(1)

        # 3 menü
        self.graf_butonu = self._menu_butonu_yarat("Graf ▾", [
            ("graf.gorunum", "Graf Görünümü"),
            ("graf.matris", "Komşuluk Matrisi"),
            ("graf.validator", "Fibonacci Doğrulayıcı"),
        ])
        duzen.addWidget(self.graf_butonu)

        self.algoritma_butonu = self._menu_butonu_yarat("Algoritma ▾", [
            ("alg.bfs_dfs", "BFS / DFS Gezinme"),
            ("alg.dijkstra", "Dijkstra Kısa Yol"),
            ("alg.tohum", "Tohum Seçimi"),
        ])
        duzen.addWidget(self.algoritma_butonu)

        self.gorsel_butonu = self._menu_butonu_yarat("Görselleştir ▾", [
            ("gor.yakinsama", "Yakınsama Grafiği"),
            ("gor.karsilastirma", "Açı Karşılaştırma"),
            ("gor.animasyon", "Animasyon Kontrol"),
        ])
        duzen.addWidget(self.gorsel_butonu)

    # ---- iç yardımcılar ----

    def _dikey_cizgi(self) -> QFrame:
        c = QFrame()
        c.setFrameShape(QFrame.VLine)
        c.setFrameShadow(QFrame.Plain)
        return c

    def _menu_butonu_yarat(self, etiket: str, ogeler: list[tuple[str, str]]) -> QToolButton:
        buton = QToolButton()
        buton.setText(etiket)
        buton.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(buton)
        for eylem_id, baslik in ogeler:
            eylem = menu.addAction(baslik)
            eylem.triggered.connect(lambda _checked=False, eid=eylem_id: self.menu_eylemi.emit(eid))
        buton.setMenu(menu)
        return buton

    def _ciz_tiklandi(self) -> None:
        self.cizim_istendi.emit(self.n_kutu.value(), self.aci_kutu.value())
```

- [ ] **Step 4: Testi tekrar çalıştır**

Komut:
```bash
pytest tests/test_top_bar.py -v
```

Beklenen: 4 test PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/top_bar.py tests/test_top_bar.py
git commit -m "ui: TopBar widget — kontroller + 3 menü (henüz no-op)"
```

---

## Task 7: `TopBar`'ı `MainWindow`'a yerleştir

**Files:**
- Modify: `ui/main_window.py`
- Modify: `tests/test_main_window.py`

- [ ] **Step 1: Testi genişlet — TopBar bağlanmış olmalı**

`tests/test_main_window.py` mevcut içeriğinin sonuna ekle:
```python
def test_main_window_top_bar_iceriyor(qtbot):
    from ui.top_bar import TopBar

    pencere = MainWindow()
    qtbot.addWidget(pencere)
    assert pencere.top_bar is not None
    assert isinstance(pencere.top_bar, TopBar)
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

Komut:
```bash
pytest tests/test_main_window.py::test_main_window_top_bar_iceriyor -v
```

Beklenen: `AttributeError: 'MainWindow' object has no attribute 'top_bar'`

- [ ] **Step 3: `MainWindow`'a TopBar'ı ekle**

`ui/main_window.py` tüm içeriğini şu hâliyle değiştir:
```python
"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı + pencere yöneticisi.

Bu görevde sadece üst şerit yerleşti — canvas ve bilgi kartı sonraki
görevlerde eklenecek.
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)
        duzen.addStretch(1)  # canvas için yer ayır (Task 8'de doldurulur)
```

- [ ] **Step 4: Testleri çalıştır**

Komut:
```bash
pytest tests/test_main_window.py -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 5: Manuel görsel doğrulama**

Komut:
```bash
python main.py
```

Beklenen: Üst şeritte n=100, α=137.50°, Çiz butonu (lacivert dolu), ▶ Animasyon, ⊕ Yakınlaştır, sağda Graf / Algoritma / Görselleştir menüleri. Menüleri aç — öğeler görünür ama tıklayınca henüz bir şey olmaz. Çiz'e bas — henüz bir şey olmaz (bağlanmadı).

- [ ] **Step 6: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "ui: MainWindow'a TopBar yerleştirildi"
```

---

## Task 8: `SpiralCanvas` — temel spiral çizimi

**Files:**
- Create: `ui/spiral_canvas.py`

- [ ] **Step 1: `ui/spiral_canvas.py`'i yaz**

`ui/spiral_canvas.py`:
```python
"""
ui.spiral_canvas
----------------
matplotlib qtagg backend tabanlı Qt widget'ı. Ayçiçeği spiralini çizer;
Fibonacci indeksli noktaları vurgular; hover/click ile sinyal yayar
(InfoCard bu sinyalleri dinleyip detayı sağ-üst kartta gösterir).

NOT: Spec 3.5'teki "noktanın yanında açılan tooltip" davranışı Plan 1'de
sadeleştirildi — aynı bilgi sağ-üst InfoCard'da gösteriliyor. Cursor'ı
takip eden floating tooltip ileride ayrı bir alt-task olarak eklenebilir.
"""

import math
from typing import Optional

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from fibonacci import fibonacci_dizisi
from positioning import tum_konumlar
from ui import theme


def _fibonacci_indeks_kumesi(n: int) -> set[int]:
    """0..n-1 arasındaki tüm Fibonacci sayılarını küme olarak döndürür."""
    fib = fibonacci_dizisi(20)  # F(0)..F(19) = 4181'e kadar yeter
    return {f for f in fib if 0 <= f < n}


class SpiralCanvas(QWidget):
    """
    Spirali çizen ve etkileşim yönetim Qt widget'ı.

    Sinyaller:
        nokta_hover(int)  — fare bir noktanın yakınına geldi (tohum_index).
        nokta_hover_iptal — fare bir noktanın yakınından ayrıldı.
        nokta_tiklandi(int) — bir noktaya tıklandı.
    """

    nokta_hover = Signal(int)
    nokta_hover_iptal = Signal()
    nokta_tiklandi = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._figure = Figure(figsize=(8, 8), facecolor=theme.ARKA_PLAN_KART)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._axes = self._figure.add_subplot(111)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.addWidget(self._canvas)

        # Mevcut durum
        self._n: int = 0
        self._aci_derece: float = 137.5
        self._konumlar: list[tuple[float, float]] = []
        self._fib_indeksleri: set[int] = set()

        # Hover/click bağlantıları
        self._canvas.mpl_connect("motion_notify_event", self._hover_handler)
        self._canvas.mpl_connect("button_press_event", self._click_handler)

        self._eksenleri_hazirla()

    # ---- Genel API ----

    def spirali_ciz(self, n: int, aci_derece: float) -> None:
        """n tohum ile spirali yeniden çiz."""
        self._n = n
        self._aci_derece = aci_derece
        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(n)
        self._yeniden_ciz()

    # ---- İç çizim ----

    def _eksenleri_hazirla(self) -> None:
        self._axes.set_aspect("equal")
        self._axes.set_xticks([])
        self._axes.set_yticks([])
        for spine in self._axes.spines.values():
            spine.set_visible(False)
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)

    def _yeniden_ciz(self) -> None:
        self._axes.clear()
        self._eksenleri_hazirla()

        if not self._konumlar:
            self._canvas.draw_idle()
            return

        xs = [p[0] for p in self._konumlar]
        ys = [p[1] for p in self._konumlar]

        # Tüm noktalar — koyu lacivert
        self._axes.scatter(xs, ys, s=8, c=theme.METIN_ANA, zorder=1)

        # Fibonacci indeksli noktalar — kırmızı + etiket
        for i in self._fib_indeksleri:
            x, y = self._konumlar[i]
            self._axes.scatter([x], [y], s=24, c=theme.VURGU, zorder=2)
            self._axes.text(
                x + 1.0, y + 1.0, str(i),
                fontsize=8, color="#555555",
                family="Georgia", zorder=3,
            )

        self._canvas.draw_idle()

    # ---- Etkileşim — bu Task'ta sinyalleri yayıyor, tooltip Task 9'da ----

    def _en_yakin_nokta(self, event) -> Optional[int]:
        if event.xdata is None or event.ydata is None or not self._konumlar:
            return None
        # Veri koordinatlarında 3.0 birim eşik (~10px düşük zoom'da)
        esik = 3.0
        en_yakin: Optional[int] = None
        en_yakin_mes = float("inf")
        for i, (x, y) in enumerate(self._konumlar):
            d = math.hypot(x - event.xdata, y - event.ydata)
            if d < esik and d < en_yakin_mes:
                en_yakin_mes = d
                en_yakin = i
        return en_yakin

    def _hover_handler(self, event) -> None:
        idx = self._en_yakin_nokta(event)
        if idx is None:
            self.nokta_hover_iptal.emit()
        else:
            self.nokta_hover.emit(idx)

    def _click_handler(self, event) -> None:
        idx = self._en_yakin_nokta(event)
        if idx is not None:
            self.nokta_tiklandi.emit(idx)
```

- [ ] **Step 2: SpiralCanvas'ı MainWindow'a yerleştir**

`ui/main_window.py` içinde:

Mevcut:
```python
from ui.top_bar import TopBar


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)
        duzen.addStretch(1)  # canvas için yer ayır (Task 8'de doldurulur)
```

Şununla değiştir:
```python
from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)

        self.canvas = SpiralCanvas()
        duzen.addWidget(self.canvas, 1)

        # Çiz butonuna bağlan
        self.top_bar.cizim_istendi.connect(self.canvas.spirali_ciz)

        # İlk çizim
        self.canvas.spirali_ciz(self.top_bar.n_kutu.value(), self.top_bar.aci_kutu.value())
```

- [ ] **Step 3: Mevcut MainWindow testlerini çalıştır**

Komut:
```bash
pytest tests/test_main_window.py -v
```

Beklenen: tüm testler PASS (canvas eklenmesi mevcut testleri kırmaz).

- [ ] **Step 4: Manuel görsel doğrulama**

Komut:
```bash
python main.py
```

Beklenen:
- Pencere açıldığında 100 tohumlu spiral hemen görünür (varsayılan değerlerle çizilmiş)
- Kırmızı vurgulu noktalar = Fibonacci indeksli (1, 2, 3, 5, 8, 13, 21, 34, 55, 89 indeksli olanlar)
- Yanlarında küçük rakam etiketleri (Georgia)
- n=200, Çiz → spiral genişler
- α=120, Çiz → açı değişir, farklı desen

- [ ] **Step 5: Commit**

```bash
git add ui/spiral_canvas.py ui/main_window.py
git commit -m "ui: SpiralCanvas — Vogel spirali + Fibonacci noktası vurgusu"
```

---

## Task 9: `InfoCard` — sağ-üst bilgi kartı

**Files:**
- Create: `ui/info_card.py`
- Modify: `ui/main_window.py`

- [ ] **Step 1: `ui/info_card.py`'i yaz**

`ui/info_card.py`:
```python
"""
ui.info_card
------------
Spiral canvas'ın sağ-üstünde duran küçük overlay. F oranı, seçili tohum,
imleç altındaki nokta gibi anlık metrikleri gösterir.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from fibonacci import fibonacci_n, formatla_buyuk_sayi
from utils import oran_ve_fark, PHI
from ui import theme


class InfoCard(QFrame):
    """Spiral overlay kartı — küçük, sade serif metin."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("info_card")
        self.setStyleSheet(
            f"#info_card {{"
            f"  background-color: {theme.ARKA_PLAN_OVERLAY};"
            f"  border: 1px solid {theme.KENAR_KALIN};"
            f"  border-radius: 2px;"
            f"}}"
            f"#info_card QLabel {{"
            f"  background-color: transparent;"
            f"  color: {theme.METIN_ANA};"
            f"  font-family: '{theme.FONT_KUCUK[0]}';"
            f"  font-size: {theme.FONT_KUCUK[1]}pt;"
            f"}}"
        )
        self.setAttribute(Qt.WA_StyledBackground, True)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(12, 10, 12, 10)
        duzen.setSpacing(2)

        self.f_etiketi = QLabel("F(—) = —")
        self.oran_etiketi = QLabel("F(—)/F(—) = —")
        self.tohum_etiketi = QLabel("seçili tohum: —")
        self.imlec_etiketi = QLabel("imleç: —")

        for e in (self.f_etiketi, self.oran_etiketi, self.tohum_etiketi, self.imlec_etiketi):
            duzen.addWidget(e)

    # ---- Genel API ----

    def n_degisti(self, n: int) -> None:
        """En son çizilen n için F(k) ve F(k)/F(k-1) gösterimini güncelle."""
        if n < 2:
            self.f_etiketi.setText("F(—) = —")
            self.oran_etiketi.setText("F(—)/F(—) = —")
            return
        k = self._buyuk_fib_indeksi(n)
        fk = fibonacci_n(k)
        fk1 = fibonacci_n(k - 1)
        oran, fark = oran_ve_fark(fk1, fk)
        self.f_etiketi.setText(f"F({k}) = {formatla_buyuk_sayi(fk)}")
        self.oran_etiketi.setText(
            f"F({k})/F({k-1}) = {oran:.4f}  → φ (Δ={fark:.2e})"
        )

    def imlec_pozisyonu(self, x: Optional[float], y: Optional[float]) -> None:
        if x is None or y is None:
            self.imlec_etiketi.setText("imleç: —")
        else:
            self.imlec_etiketi.setText(f"imleç: ({x:.1f}, {y:.1f})")

    def secili_tohum(self, idx: Optional[int]) -> None:
        if idx is None:
            self.tohum_etiketi.setText("seçili tohum: —")
        else:
            self.tohum_etiketi.setText(f"seçili tohum: {idx}")

    # ---- iç ----

    def _buyuk_fib_indeksi(self, n: int) -> int:
        """n'den küçük en büyük Fibonacci indeksini döndürür."""
        k = 1
        while fibonacci_n(k + 1) < n:
            k += 1
        return k
```

- [ ] **Step 2: MainWindow'a InfoCard'ı overlay olarak yerleştir**

`ui/main_window.py` mevcut içeriğini şu hâliyle değiştir:
```python
"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı (overlay).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas
from ui.info_card import InfoCard


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)

        self.canvas = SpiralCanvas()
        duzen.addWidget(self.canvas, 1)

        # InfoCard overlay — canvas'ın çocuğu (Qt parent), free-floating
        self.info_card = InfoCard(self.canvas)
        self.info_card.setParent(self.canvas)

        # Sinyalleri bağla
        self.top_bar.cizim_istendi.connect(self._cizim_istendi)
        self.canvas.nokta_hover.connect(self.info_card.secili_tohum)
        self.canvas.nokta_hover_iptal.connect(lambda: self.info_card.secili_tohum(None))
        self.canvas.nokta_tiklandi.connect(self.info_card.secili_tohum)

        # İlk çizim
        self._cizim_istendi(self.top_bar.n_kutu.value(), self.top_bar.aci_kutu.value())

    def _cizim_istendi(self, n: int, aci_derece: float) -> None:
        self.canvas.spirali_ciz(n, aci_derece)
        self.info_card.n_degisti(n)

    def resizeEvent(self, event):  # noqa: N802 (Qt API)
        super().resizeEvent(event)
        self._info_card_konumla()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._info_card_konumla()

    def _info_card_konumla(self) -> None:
        """InfoCard'ı canvas'ın sağ-üst köşesine yerleştir (10px margin)."""
        if not self.canvas.isVisible():
            return
        self.info_card.adjustSize()
        margin = 12
        x = self.canvas.width() - self.info_card.width() - margin
        y = margin
        self.info_card.move(x, y)
        self.info_card.raise_()
```

- [ ] **Step 3: `InfoCard.__init__` imza düzeltmesi**

InfoCard yukarıdaki kodda `InfoCard(self.canvas)` ile parent veriliyor ama `__init__` parent almıyor. `ui/info_card.py` `__init__` imzasını güncelle:

Mevcut:
```python
    def __init__(self) -> None:
        super().__init__()
```

Şununla değiştir:
```python
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
```

- [ ] **Step 4: Test ekle — InfoCard güncellemeleri**

`tests/test_main_window.py`'ın sonuna ekle:
```python
def test_main_window_info_card_n_degistirir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.show()
    # n=100 ile başladı; en yakın Fibonacci k bulunmalı → 11 (F(11)=89)
    metin = pencere.info_card.f_etiketi.text()
    assert "F(" in metin and "=" in metin
```

- [ ] **Step 5: Testleri çalıştır**

Komut:
```bash
pytest tests/test_main_window.py -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 6: Manuel görsel doğrulama**

Komut:
```bash
python main.py
```

Beklenen:
- Sağ-üstte küçük krem kart: "F(11) = 89", "F(11)/F(10) = 1.6180 ...", "seçili tohum: —", "imleç: —"
- Bir noktanın üzerine gel → "seçili tohum: 34" gibi değer çıkar
- Fareyi noktadan uzaklaştır → "seçili tohum: —"
- Pencereyi yeniden boyutlandır → kart sağ-üstte kalır

- [ ] **Step 7: Commit**

```bash
git add ui/info_card.py ui/main_window.py tests/test_main_window.py
git commit -m "ui: InfoCard overlay — F oranı, tohum, sinyal bağlantıları"
```

---

## Task 10: `AnalyticsWindow` + `WindowManager` (tek-instance)

**Files:**
- Create: `ui/windows/base.py`
- Create: `ui/windows/placeholder.py`
- Create: `tests/test_window_manager.py`

- [ ] **Step 1: Başarısız test yaz**

`tests/test_window_manager.py`:
```python
"""WindowManager tek-instance kuralı."""

import pytest

pytest.importorskip("PySide6")

from ui.windows.base import AnalyticsWindow, WindowManager


class SahteWindow(AnalyticsWindow):
    BASLIK = "Sahte"


def test_window_manager_ayni_kimligi_iki_kere_acmaz(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p1)
    p2 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p2)
    assert p1 is p2


def test_window_manager_kapatilan_pencere_temizlenir(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p1)
    p1.close()
    # Kapatıldıktan sonra yeni açılış yeni instance üretmeli
    p2 = yonetici.ac_veya_one_getir("test", SahteWindow)
    qtbot.addWidget(p2)
    assert p1 is not p2


def test_window_manager_farkli_kimlikler_ayri_pencere(qtbot):
    yonetici = WindowManager()
    p1 = yonetici.ac_veya_one_getir("a", SahteWindow)
    p2 = yonetici.ac_veya_one_getir("b", SahteWindow)
    qtbot.addWidget(p1)
    qtbot.addWidget(p2)
    assert p1 is not p2
```

- [ ] **Step 2: Testi çalıştır, başarısızlığı gör**

Komut:
```bash
pytest tests/test_window_manager.py -v
```

Beklenen: `ModuleNotFoundError: No module named 'ui.windows.base'`

- [ ] **Step 3: `ui/windows/base.py`'i yaz**

`ui/windows/base.py`:
```python
"""
ui.windows.base
---------------
Analitik pencerelerin base class'ı ve tek-instance yöneticisi.

Kullanım:
    yonetici = WindowManager()
    pencere = yonetici.ac_veya_one_getir("graf.gorunum", GrafGorunumPencere)
"""

from typing import Callable, Optional

from PySide6.QtWidgets import QWidget


class AnalyticsWindow(QWidget):
    """
    Analitik pencerelerin base class'ı. Alt sınıflar BASLIK'ı override eder
    ve gerçek içeriği __init__ içinde kurar.
    """

    BASLIK: str = "Pencere"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        # Üst-seviye pencere — parent verme; sadece referans tutmak için yönetici
        # parent argümanı kullanmaz, top-level QWidget yaratırız
        super().__init__()
        self.setWindowTitle(self.BASLIK)
        self.resize(640, 480)


class WindowManager:
    """
    Tek-instance pencere yönetimi.

    Her kimlik (eylem id'si, örn. "graf.gorunum") için en fazla bir açık
    pencere tutar. ac_veya_one_getir çağrısı:
      - kimliğin penceresi yoksa yeni instance üretip gösterir,
      - varsa onu ön plana getirir.

    Pencere kapanınca destroyed sinyali ile sözlükten temizlenir.
    """

    def __init__(self) -> None:
        self._pencereler: dict[str, AnalyticsWindow] = {}

    def ac_veya_one_getir(
        self,
        kimlik: str,
        fabrika: Callable[[], AnalyticsWindow],
    ) -> AnalyticsWindow:
        """Verilen kimlik için pencereyi üret ya da var olanı ön plana getir."""
        mevcut = self._pencereler.get(kimlik)
        if mevcut is not None:
            mevcut.show()
            mevcut.raise_()
            mevcut.activateWindow()
            return mevcut

        yeni = fabrika()
        self._pencereler[kimlik] = yeni
        # Kapatılınca sözlükten çıkar
        yeni.destroyed.connect(lambda *_: self._pencereler.pop(kimlik, None))
        yeni.show()
        return yeni
```

- [ ] **Step 4: Testleri çalıştır**

Komut:
```bash
pytest tests/test_window_manager.py -v
```

Beklenen: 3 test PASS.

> NOT: Test `WindowManager.ac_veya_one_getir(kimlik, fabrika)` imzasıyla `(kimlik, SahteWindow)` çağırıyor — yani `fabrika()` no-arg çağrı olmalı. `SahteWindow.__init__` no-arg → çalışır. Eğer test başarısız olursa imzayı kontrol et.

- [ ] **Step 5: `ui/windows/placeholder.py`'i yaz**

`ui/windows/placeholder.py`:
```python
"""
ui.windows.placeholder
----------------------
Sonraki planlarda port edilecek analitik pencereler için ortak yer-tutucu.
"Yapım aşamasında" mesajı gösterir; menüden tıklanınca açılır.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel

from ui.windows.base import AnalyticsWindow


class PlaceholderWindow(AnalyticsWindow):
    BASLIK = "Yapım aşamasında"

    def __init__(self, eylem_id: str, baslik: str) -> None:
        super().__init__()
        self.setWindowTitle(f"{baslik} — yapım aşamasında")
        duzen = QVBoxLayout(self)
        etiket = QLabel(
            f"Bu pencere ('{eylem_id}') sonraki planda port edilecek.\n\n"
            f"Şimdilik yer tutuyor — kapatabilirsin."
        )
        etiket.setWordWrap(True)
        duzen.addWidget(etiket)
```

- [ ] **Step 6: Commit**

```bash
git add ui/windows/base.py ui/windows/placeholder.py tests/test_window_manager.py
git commit -m "ui: AnalyticsWindow base + WindowManager tek-instance"
```

---

## Task 11: Menü öğelerini placeholder pencerelere bağla

**Files:**
- Modify: `ui/main_window.py`

- [ ] **Step 1: MainWindow'a WindowManager ekle ve menü sinyalini bağla**

`ui/main_window.py` içinde:

Mevcut import bloğu:
```python
from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas
from ui.info_card import InfoCard
```

Şununla değiştir:
```python
from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas
from ui.info_card import InfoCard
from ui.windows.base import WindowManager
from ui.windows.placeholder import PlaceholderWindow


# Menü eylem kimliği → kullanıcıya gösterilecek başlık
MENU_BASLIKLARI: dict[str, str] = {
    "graf.gorunum": "Graf Görünümü",
    "graf.matris": "Komşuluk Matrisi",
    "graf.validator": "Fibonacci Doğrulayıcı",
    "alg.bfs_dfs": "BFS / DFS Gezinme",
    "alg.dijkstra": "Dijkstra Kısa Yol",
    "alg.tohum": "Tohum Seçimi",
    "gor.yakinsama": "Yakınsama Grafiği",
    "gor.karsilastirma": "Açı Karşılaştırma",
    "gor.animasyon": "Animasyon Kontrol",
}
```

`MainWindow.__init__` içinde, mevcut "Sinyalleri bağla" bloğunun **sonuna** ekle (mevcut bağlantıları silme):
```python
        # Pencere yöneticisi + menü bağlantısı
        self._pencere_yoneticisi = WindowManager()
        self.top_bar.menu_eylemi.connect(self._menu_eylemi_geldi)
```

`MainWindow` sınıfının sonuna yeni method ekle (mevcut method'ların altına):
```python
    def _menu_eylemi_geldi(self, eylem_id: str) -> None:
        baslik = MENU_BASLIKLARI.get(eylem_id, eylem_id)
        self._pencere_yoneticisi.ac_veya_one_getir(
            eylem_id,
            lambda: PlaceholderWindow(eylem_id, baslik),
        )
```

- [ ] **Step 2: Test ekle — menü tıklayınca pencere açılır**

`tests/test_main_window.py`'ın sonuna ekle:
```python
def test_main_window_menu_tiklayinca_placeholder_acilir(qtbot):
    pencere = MainWindow()
    qtbot.addWidget(pencere)
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    # WindowManager iç sözlüğünde olmalı
    yonetici = pencere._pencere_yoneticisi
    assert "graf.gorunum" in yonetici._pencereler
    p1 = yonetici._pencereler["graf.gorunum"]
    qtbot.addWidget(p1)
    # İkinci kez tıkla — aynı instance olmalı
    pencere.top_bar.menu_eylemi.emit("graf.gorunum")
    p2 = yonetici._pencereler["graf.gorunum"]
    assert p1 is p2
```

- [ ] **Step 3: Tüm testleri çalıştır**

Komut:
```bash
pytest tests -v
```

Beklenen: tüm testler PASS.

- [ ] **Step 4: Manuel görsel doğrulama (uçtan uca)**

Komut:
```bash
python main.py
```

Beklenen senaryolar:
1. Pencere açılır, spiral n=100 ile görünür, sağ-üstte info card.
2. n'i 300 yap, Çiz → spiral genişler, info card F(13)=233 gösterir (en yakın Fibonacci).
3. α'yı 90.0 yap, Çiz → spiral dramatik değişir (artık altın açı değil).
4. Bir noktanın üzerine gel → info card "seçili tohum: N" gösterir.
5. Graf ▾ menüsü → Graf Görünümü tıkla → "Graf Görünümü — yapım aşamasında" başlıklı yer-tutucu pencere açılır.
6. Aynı menü öğesine tekrar tıkla → yeni pencere açılmaz, mevcut ön plana gelir.
7. Yer-tutucu pencereyi kapat → tekrar tıkla → yeni instance açılır.
8. Algoritma ▾ ve Görselleştir ▾ menüleri de aynı şekilde çalışır.
9. ▶ Animasyon ve ⊕ Yakınlaştır butonları toggle olur ama henüz işlevsel değil (sonraki planlarda bağlanır).

- [ ] **Step 5: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "ui: menü öğeleri placeholder pencerelere bağlandı"
```

---

## Task 12: README'ye yeni çalıştırma talimatını ekle

**Files:**
- Modify: `README.md` (varsa; yoksa bu task'ı atla)

- [ ] **Step 1: README'nin varlığını kontrol et**

Komut:
```bash
ls README.md
```

Eğer "No such file" derse — bu task'ı atla, sonraki task'a geç.

- [ ] **Step 2: README'yi oku ve "Çalıştırma" / "Usage" / "Kullanım" bölümünü bul**

Komut:
```bash
grep -n -i "çalıştır\|usage\|kullanım\|run\|python main" README.md
```

- [ ] **Step 3: README'ye yeni arayüz notu ekle**

Bulduğun çalıştırma bölümüne şu eki yap (uygun yere):
```markdown
### Arayüz (PySide6 — yeni)

```bash
python main.py
```

### Eski Tkinter arayüzü (yedek)

```bash
python main_legacy.py
```
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README'ye yeni PySide6 arayüzü için çalıştırma talimatı"
```

---

## Plan tamamlandı — son kontrol

- [ ] **Tüm testler geçiyor mu?**

```bash
pytest -v
```

Beklenen: önceki tüm testler + yeni eklenen smoke testler PASS.

- [ ] **Manuel kabul kontrol listesi:**

`python main.py` ile:
- [ ] Pencere 1280×800 boyutunda açılır.
- [ ] Üst şeritte n, α, Çiz, Animasyon, Yakınlaştır + 3 menü görünür.
- [ ] Tema kâğıt renginde (krem), metinler lacivert.
- [ ] Spiral varsayılan değerlerle hemen çizilir.
- [ ] Fibonacci indeksli noktalar kırmızı ve etiketli.
- [ ] Sağ-üstte info card görünür ve F oranı doğru.
- [ ] n/α değişiminden sonra Çiz spiralı yeniler.
- [ ] Hover → info card "seçili tohum" güncellenir.
- [ ] Menü öğeleri placeholder pencereler açar.
- [ ] Aynı menü öğesine 2. tıklama yeni pencere açmaz.

`python main_legacy.py` ile:
- [ ] Eski Tk arayüzü hâlâ çalışır (regresyon yok).

Plan 1 burada biter. Sonraki plan: ilk analitik pencere portu (öneri sırası: en küçük olan Fibonacci Doğrulayıcı'dan başla, sonra Yakınsama Grafiği, sonra büyük olanlar).
