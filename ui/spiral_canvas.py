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
from PySide6.QtCore import Signal, QTimer
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
    animasyon_bitti = Signal()

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
        # Statik scatter referansı — _kare_ciz tarafından kullanılır
        self._scatter = None
        # Validator vurgu state — cross-window'den gelen tohum indeksleri
        self._vurgu_indeksleri: set[int] = set()
        # Tohum seçimi state — kullanıcının seçtiği indeksler
        self._secim_indeksleri: set[int] = set()
        # Animasyon state
        self._anim_kare: int = -1
        self._anim_toplam: int = 0
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._animasyon_tick)

        # Hover/click bağlantıları
        self._canvas.mpl_connect("motion_notify_event", self._hover_handler)
        self._canvas.mpl_connect("motion_notify_event", self._motion_pan_handler)
        self._canvas.mpl_connect("button_press_event", self._press_handler)
        self._canvas.mpl_connect("button_release_event", self._release_handler)
        self._canvas.mpl_connect("scroll_event", self._scroll_handler)

        # Pan state
        self._press_pixel: Optional[tuple[float, float]] = None
        self._press_data: Optional[tuple[float, float]] = None
        self._panning: bool = False
        self._pan_esik_px: float = 5.0

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
        kare_no (0-indeksli) son aktif tohum olacak şekilde sahneyi çizer.

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
            elif i in self._secim_indeksleri:
                renkler.append(theme.MOR_VURGU)
            elif i in self._vurgu_indeksleri:
                renkler.append(theme.MAVI_VURGU)
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

    # ---- Etkileşim ----

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
        """İmleç-merkezli zoom in/out."""
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            return
        olcek = 1 / 1.2 if (event.button == "up" or event.step > 0) else 1.2
        xmin, xmax = self._axes.get_xlim()
        ymin, ymax = self._axes.get_ylim()
        cx, cy = event.xdata, event.ydata
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
        """Press anchor varsa eşik kontrolüyle pan."""
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

        if event.xdata is None or event.ydata is None or self._press_data is None:
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
        if not self._panning and self._press_data is not None:
            idx = self._en_yakin_nokta_data(self._press_data[0], self._press_data[1])
            if idx is not None:
                self.nokta_tiklandi.emit(idx)
        self._press_pixel = None
        self._press_data = None
        self._panning = False

    def _en_yakin_nokta_data(self, xd: float, yd: float) -> Optional[int]:
        """Veri koordinatında en yakın tohumu döndürür (eşik 3.0)."""
        esik = 3.0
        en_yakin: Optional[int] = None
        en_yakin_mes = float("inf")
        for i, (x, y) in enumerate(self._konumlar):
            d = math.hypot(x - xd, y - yd)
            if d < esik and d < en_yakin_mes:
                en_yakin_mes = d
                en_yakin = i
        return en_yakin

    # ---- Animasyon ----

    def animasyonu_basla(self, toplam_n: int, aci_derece: float, interval_ms: int) -> None:
        """
        Animasyonu başlatır. interval_ms <= 1 ise tek karede tüm tohumları çizer
        ve animasyon_bitti sinyalini hemen yayar.
        """
        if self._timer.isActive():
            self._timer.stop()

        self._anim_toplam = toplam_n
        self._aci_derece = aci_derece
        self._anim_kare = -1

        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(toplam_n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(toplam_n)
        self._n = toplam_n

        # Anında modu
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

        # Sahneyi sıfırla (tüm tohumlar gri)
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

    def secim_ekle(self, idx: int) -> None:
        """Verilen tohum indeksini mor seçim kümesine ekle ve yeniden çiz."""
        self._secim_indeksleri.add(idx)
        if self._konumlar:
            self._yeniden_ciz()

    def secim_temizle(self) -> None:
        """Tüm tohum seçimlerini temizle ve yeniden çiz."""
        if not self._secim_indeksleri:
            return
        self._secim_indeksleri.clear()
        if self._konumlar:
            self._yeniden_ciz()
