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
import time
from typing import Optional

import numpy as np

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.colors as mcolors

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout

from fibonacci import fibonacci_dizisi
from graph_builder import grafi_olustur
from positioning import tum_konumlar
from ui import theme


# Graf modu sabitleri
GRAF_TOOLTIP_BG = "#1a2238"           # Lacivert
GRAF_TOOLTIP_FG = "#fafaf7"           # Krem
PHI = (1 + 5 ** 0.5) / 2              # Altın oran


def _kenar_rengi(agirlik: float) -> tuple[float, float, float, float]:
    """
    Ağırlık φ'ye ne kadar yakınsa o kadar yoğun AKSAN (lacivert);
    uzaklaştıkça soluklaşır. RGBA tuple döndürür.
    """
    fark = abs(agirlik - PHI)
    # 0.2 birim fark = tam soluk (alpha düşer + renk grileşir)
    yakinlik = max(0.0, min(1.0, 1.0 - fark / 0.2))
    # AKSAN = #1a4480 → (0.102, 0.267, 0.502)
    # METIN_PASIF = #888888 → (0.533, 0.533, 0.533)
    r = 0.533 + (0.102 - 0.533) * yakinlik
    g = 0.533 + (0.267 - 0.533) * yakinlik
    b = 0.533 + (0.502 - 0.533) * yakinlik
    alpha = 0.35 + 0.55 * yakinlik  # uzakta soluk, yakında dolu
    return (r, g, b, alpha)


def _fibonacci_indeks_kumesi(n: int) -> set[int]:
    """0..n-1 arasındaki tüm Fibonacci sayılarını küme olarak döndürür."""
    fib = fibonacci_dizisi(20)  # F(0)..F(19) = 4181'e kadar yeter
    return {f for f in fib if 0 <= f < n}


def _nokta_boyutu(n: int) -> float:
    """
    Spiral modunda tohum boyutunu n'e göre adaptif hesapla.

    Vogel modelinde komşular arası mesafe ~sabit (c≈1) ama spiral yarıçapı
    √n ile büyür → autoscale ekranı geriye çekince noktalar küçülür.
    Bunu telafi etmek için scatter `s` (pt²) değerini 1/√n ile ölçekle,
    minimum okunur boyutta tut.
    """
    if n <= 0:
        return 18.0
    return max(8.0, 180.0 / math.sqrt(n))


# Ayçiçeği modu renk gradyanı — merkez koyu kahve → dış olgun amber
_AYCIEGI_C_MERKEZ = (0.165, 0.086, 0.063)
_AYCIEGI_C_DIS = (0.690, 0.439, 0.125)
_AYCIEGI_ZEMIN = "#fcfaf3"


def _ayciegi_renkleri(konumlar: list[tuple[float, float]]) -> list[tuple[float, float, float]]:
    """Her tohum için merkezden uzaklığa göre kahve→amber gradient rengi döndürür."""
    if not konumlar:
        return []
    rs = [math.hypot(x, y) for x, y in konumlar]
    r_max = max(rs) or 1.0
    out: list[tuple[float, float, float]] = []
    for r in rs:
        t = r / r_max
        out.append((
            _AYCIEGI_C_MERKEZ[0] + (_AYCIEGI_C_DIS[0] - _AYCIEGI_C_MERKEZ[0]) * t,
            _AYCIEGI_C_MERKEZ[1] + (_AYCIEGI_C_DIS[1] - _AYCIEGI_C_MERKEZ[1]) * t,
            _AYCIEGI_C_MERKEZ[2] + (_AYCIEGI_C_DIS[2] - _AYCIEGI_C_MERKEZ[2]) * t,
        ))
    return out


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
        # Animasyon state
        self._anim_kare: int = -1
        self._anim_toplam: int = 0
        self._anim_batch: int = 1            # kare başına yerleştirilecek tohum sayısı
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._animasyon_tick)

        # Hızlı animasyon (artımlı + blitting) state — büyük n'de O(n²) ve artist
        # churn kaynaklı donmayı önler. Yalnızca spiral/ayçiçeği modunda kullanılır.
        self._anim_hizli: bool = False
        self._anim_bg = None                 # blit için arka plan snapshot'ı
        self._anim_scatter = None            # tüm tohumları içeren kalıcı scatter
        self._anim_ring = None               # aktif tohum halkası (tek nokta)
        self._anim_labels: dict[int, object] = {}  # idx → Fibonacci etiketi (Text)
        self._anim_base_colors = None        # (n,4) RGBA — yerleşmiş tohum renkleri
        self._anim_aktif_rgba = None         # aktif tohumun vurgu rengi
        self._anim_edges = None              # graf modu: tüm kenarlar tek LineCollection
        self._anim_edge_base = None          # (n-1,4) RGBA — kenar renkleri

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

        # Graf modu state
        self._graf_modu: bool = False
        self._G = None  # graf modunda networkx DiGraph
        self._oklar: list = []  # (u, v, FancyArrowPatch) listesi
        self._tooltip = None  # matplotlib.text.Text (graf modu)
        self._son_motion_zamani: float = 0.0
        self._motion_throttle_sn: float = 0.03

        # Ayçiçeği modu state — kayıt için temiz tohum yatağı görünümü
        self._ayciegi_modu: bool = False

        self._eksenleri_hazirla()

    # ---- Genel API ----

    def spirali_ciz(self, n: int, aci_derece: float) -> None:
        """n tohum ile spirali yeniden çiz."""
        self._n = n
        self._aci_derece = aci_derece
        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(n)
        # Graf modu açıkken grafı yeni n'e göre yeniden kur — aksi halde oklar
        # eski (küçük) n'in kenarlarında kalır, dış düğümlerde ok görünmez.
        if self._graf_modu and n > 0:
            self._G = grafi_olustur(n, aci_radyan=aci_radyan)
        self._yeniden_ciz()

    def hideEvent(self, event):  # noqa: N802 (Qt API)
        """Widget gizlenince/kapanınca çalışan animasyon timer'ını durdur —
        yok edilmiş canvas'a ertelenmiş draw_idle düşmesini engeller."""
        if self._timer.isActive():
            self._timer.stop()
        super().hideEvent(event)

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
        # Hızlı animasyon sürerken dışarıdan tam çizim istendi (graf/ayçiçeği toggle,
        # validator vurgusu, vb.) → animasyonu temiz kes; aksi halde timer dangling
        # artist'lere blit/redraw dener. _hizli_animasyon_sonlandir bu metodu yeniden
        # çağırmadan önce _anim_hizli'yi False yaptığı için sonsuz döngü yok.
        if self._anim_hizli:
            if self._timer.isActive():
                self._timer.stop()
            self._anim_hizli = False
            self._anim_bg = None
            self._anim_scatter = None
            self._anim_ring = None
            self._anim_labels = {}
            self._anim_base_colors = None
            self._anim_aktif_rgba = None
            self._anim_edges = None
            self._anim_edge_base = None

        self._axes.clear()
        self._eksenleri_hazirla()

        if toplam == 0 or not konumlar:
            self._scatter = None
            self._canvas.draw_idle()
            return

        xs = [p[0] for p in konumlar]
        ys = [p[1] for p in konumlar]

        # Animasyon sırasında çerçeveyi tam spiralin kapsamına kilitle: yerleşmemiş
        # tohumlar hiç çizilmediği için autoscale'e bırakılırsa görüş alanı her
        # karede büyüyüp küçülür. Sabit limit → tohumlar merkezden dışa, boş
        # başlayıp dolan, oynamayan bir çerçevede belirir.
        self._axes.set_autoscale_on(False)
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        pad_x = (xmax - xmin) * 0.06 or 1.0
        pad_y = (ymax - ymin) * 0.06 or 1.0
        self._axes.set_xlim(xmin - pad_x, xmax + pad_x)
        self._axes.set_ylim(ymin - pad_y, ymax + pad_y)

        # Ayçiçeği modu — sadece yerleşmiş tohumlar, gradient renk, vurgu yok.
        # Kayıt için temiz görünüm: ne Fibonacci kırmızısı ne aktif halka.
        if self._ayciegi_modu and not self._graf_modu:
            son = max(0, kare_no + 1)
            yer_kon = konumlar[:son]
            if not yer_kon:
                self._scatter = None
                self._canvas.draw_idle()
                return
            taban = _nokta_boyutu(toplam)
            renkler_grad = _ayciegi_renkleri(yer_kon)
            self._axes.set_facecolor(_AYCIEGI_ZEMIN)
            self._scatter = self._axes.scatter(
                [p[0] for p in yer_kon],
                [p[1] for p in yer_kon],
                s=taban * 2.2,
                c=renkler_grad,
                edgecolors="none",
                linewidths=0,
                zorder=2,
            )
            self._tooltip = None
            self._oklar = []
            self._canvas.draw_idle()
            return

        # Spiral modunda n'e bağlı adaptif taban boyut
        taban = _nokta_boyutu(toplam)
        fib_boyut = taban * 1.6  # Fibonacci tohumları %60 daha büyük

        # Sadece yerleşmiş tohumları (0..kare_no) çiz — yerleşmemişler hiç
        # görünmez. Eski "gri bekleme noktası" davranışı kaldırıldı; animasyon
        # tamamen boş sahneden başlayıp tek tek dolar.
        son = max(0, kare_no + 1)
        renkler: list[str] = []
        boyutlar: list[float] = []
        for i in range(son):
            if i == kare_no:
                renkler.append(theme.VURGU)
                boyutlar.append(fib_boyut if not self._graf_modu else (60 if i in fib_indeksleri else 18))
                continue
            if i in self._vurgu_indeksleri:
                renkler.append(theme.MAVI_VURGU)
                boyutlar.append(fib_boyut if not self._graf_modu else (60 if i in fib_indeksleri else 18))
                continue
            # Ziyaret edilmiş düğümler için mod-bağımlı renk + boyut
            if self._graf_modu:
                if i in fib_indeksleri:
                    renkler.append(theme.AKSAN)
                    boyutlar.append(60)
                else:
                    renkler.append(theme.METIN_PASIF)
                    boyutlar.append(12)
            else:
                if i in fib_indeksleri:
                    renkler.append(theme.VURGU)
                    boyutlar.append(fib_boyut)
                else:
                    renkler.append(theme.METIN_ANA)
                    boyutlar.append(taban)

        # Spiral modunda da ince krem halo: küçük noktaların kontrastını arttırır
        if son > 0:
            self._scatter = self._axes.scatter(
                xs[:son], ys[:son], s=boyutlar, c=renkler,
                edgecolors=theme.ARKA_PLAN_KART,
                linewidths=(0.8 if self._graf_modu else 0.4),
                zorder=2,
            )
        else:
            self._scatter = None

        # Aktif tohum (kare_no) için belirgin lacivert halka — "şu an buradayım"
        if 0 <= kare_no < toplam:
            ax_x, ax_y = konumlar[kare_no]
            halka_boyut = max(taban, 12.0) * 5.0
            self._axes.scatter(
                [ax_x], [ax_y],
                s=halka_boyut,
                facecolors="none",
                edgecolors=theme.AKSAN_KOYU,
                linewidths=1.8,
                zorder=5,
            )

        # Fibonacci etiketleri sadece yerleşmiş tohumlara
        for i in fib_indeksleri:
            if i > kare_no:
                continue
            x, y = konumlar[i]
            # Graf modunda etiket biraz daha okunur (büyük düğümün üstüne)
            font_renk = theme.AKSAN_KOYU if self._graf_modu else "#555555"
            font_boyut = 9 if self._graf_modu else 8
            self._axes.text(
                x + 1.5, y + 1.5, str(i),
                fontsize=font_boyut, color=font_renk,
                family="Georgia", zorder=4,
            )

        # Graf modu: yerleşmiş düğümler arasındaki kenarları ok başlı çiz
        self._oklar = []
        if self._graf_modu and self._G is not None:
            for u, v, veri in self._G.edges(data=True):
                if u > kare_no or v > kare_no:
                    continue
                x0, y0 = konumlar[u]
                x1, y1 = konumlar[v]
                w = float(veri.get("agirlik", 0.0))
                ok = FancyArrowPatch(
                    (x0, y0), (x1, y1),
                    arrowstyle="-|>",
                    color=_kenar_rengi(w),
                    linewidth=1.2,
                    mutation_scale=9,
                    shrinkA=6, shrinkB=6,
                    zorder=1,
                )
                self._axes.add_patch(ok)
                self._oklar.append((u, v, ok))

            # Tooltip artefaktı
            self._tooltip = self._axes.text(
                0, 0, "",
                color=GRAF_TOOLTIP_FG, fontsize=10,
                ha="left", va="bottom",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor=GRAF_TOOLTIP_BG, edgecolor=GRAF_TOOLTIP_BG, alpha=0.95,
                ),
                zorder=10,
            )
            self._tooltip.set_visible(False)
        else:
            self._tooltip = None

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
        # Mevcut InfoCard sinyali
        idx = self._en_yakin_nokta(event)
        if idx is None:
            self.nokta_hover_iptal.emit()
        else:
            self.nokta_hover.emit(idx)

        # Graf modunda ek olarak tooltip göster (düğüm + kenar hit-test)
        if self._graf_modu:
            self._tooltip_guncelle(event)

    def _tooltip_guncelle(self, event) -> None:
        """Graf modu tooltip — throttled hit-test (düğüm önce, kenar sonra)."""
        if self._tooltip is None:
            return
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self._canvas.draw_idle()
            return

        simdi = time.perf_counter()
        if simdi - self._son_motion_zamani < self._motion_throttle_sn:
            return
        self._son_motion_zamani = simdi

        metin: Optional[str] = None

        # 1) Düğüm hit-test
        if self._scatter is not None:
            ic, info = self._scatter.contains(event)
            if ic and self._G is not None:
                idx = int(info["ind"][0])
                if idx in self._G.nodes:
                    x, y = self._konumlar[idx]
                    f_val = self._G.nodes[idx].get("fibonacci", 0)
                    metin = f"v{idx} | F = {f_val} | konum ({x:.2f}, {y:.2f})"

        # 2) Kenar hit-test
        if metin is None and self._G is not None:
            for u, v, ok in self._oklar:
                ic, _ = ok.contains(event)
                if ic:
                    w = float(self._G[u][v].get("agirlik", 0.0))
                    metin = f"v{u} → v{v} | w = {w:.4f}"
                    break

        if metin is not None:
            self._tooltip.set_text(metin)
            self._tooltip.set_position((event.xdata, event.ydata))
            if not self._tooltip.get_visible():
                self._tooltip.set_visible(True)
            self._canvas.draw_idle()
        else:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
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
        self._anim_hizli = False  # önceki çalışmadan kalmış olabilir

        self._anim_toplam = toplam_n
        self._aci_derece = aci_derece
        self._anim_kare = -1

        aci_radyan = math.radians(aci_derece)
        self._konumlar = tum_konumlar(toplam_n, aci_radyan=aci_radyan)
        self._fib_indeksleri = _fibonacci_indeks_kumesi(toplam_n)
        self._n = toplam_n
        # Graf modu açıkken animasyon n'ine göre grafı yeniden kur (spirali_ciz ile aynı neden).
        if self._graf_modu and toplam_n > 0:
            self._G = grafi_olustur(toplam_n, aci_radyan=aci_radyan)

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

        # Büyük n'de kare sayısını sınırla: kare başına birden çok tohum yerleştir.
        # ~300 karede tamamlanır → toplam render maliyeti O(n²) yerine sınırlı kalır.
        self._anim_batch = max(1, math.ceil(toplam_n / 300)) if toplam_n > 0 else 1

        # Tüm modlar (spiral / ayçiçeği / graf) hızlı artımlı yolu kullanır.
        self._hizli_animasyon_kur(toplam_n)

        self._timer.setInterval(interval_ms)
        self._timer.start()

    def _hizli_animasyon_kur(self, n: int) -> None:
        """Hızlı (artımlı) animasyon için kalıcı artist'leri bir kez yaratır."""
        self._anim_hizli = True
        self._axes.clear()
        self._eksenleri_hazirla()

        konumlar = self._konumlar
        xs = np.fromiter((p[0] for p in konumlar), dtype=float, count=n)
        ys = np.fromiter((p[1] for p in konumlar), dtype=float, count=n)

        # Çerçeveyi tam spiralin kapsamına sabitle (boş başlar, oynamaz)
        self._axes.set_autoscale_on(False)
        xmin, xmax = float(xs.min()), float(xs.max())
        ymin, ymax = float(ys.min()), float(ys.max())
        pad_x = (xmax - xmin) * 0.06 or 1.0
        pad_y = (ymax - ymin) * 0.06 or 1.0
        self._axes.set_xlim(xmin - pad_x, xmax + pad_x)
        self._axes.set_ylim(ymin - pad_y, ymax + pad_y)

        ayciegi = self._ayciegi_modu and not self._graf_modu
        graf = self._graf_modu and not self._ayciegi_modu
        if ayciegi:
            self._axes.set_facecolor(_AYCIEGI_ZEMIN)

        taban = _nokta_boyutu(n)
        fib_boyut = taban * 1.6

        # Yerleşmiş tohum renkleri (n,4) + boyutlar — bir kez hesapla
        base = np.zeros((n, 4), dtype=float)
        sizes = np.empty(n, dtype=float)
        if ayciegi:
            grad = _ayciegi_renkleri(konumlar)
            for i, (r, g, b) in enumerate(grad):
                base[i, 0], base[i, 1], base[i, 2], base[i, 3] = r, g, b, 1.0
            sizes[:] = taban * 2.2
            self._anim_aktif_rgba = None
        elif graf:
            # Graf modu: _kare_ciz graf dalıyla aynı görsel hiyerarşi
            aksan = mcolors.to_rgba(theme.AKSAN)
            pasif = mcolors.to_rgba(theme.METIN_PASIF)
            mavi = mcolors.to_rgba(theme.MAVI_VURGU)
            for i in range(n):
                fib_mi = i in self._fib_indeksleri
                if i in self._vurgu_indeksleri:
                    base[i] = mavi
                    sizes[i] = 60 if fib_mi else 18
                elif fib_mi:
                    base[i] = aksan
                    sizes[i] = 60
                else:
                    base[i] = pasif
                    sizes[i] = 12
            self._anim_aktif_rgba = np.array(mcolors.to_rgba(theme.VURGU), dtype=float)
        else:
            vurgu = mcolors.to_rgba(theme.VURGU)
            metin = mcolors.to_rgba(theme.METIN_ANA)
            mavi = mcolors.to_rgba(theme.MAVI_VURGU)
            for i in range(n):
                if i in self._vurgu_indeksleri:
                    base[i] = mavi
                    sizes[i] = fib_boyut
                elif i in self._fib_indeksleri:
                    base[i] = vurgu
                    sizes[i] = fib_boyut
                else:
                    base[i] = metin
                    sizes[i] = taban
            self._anim_aktif_rgba = np.array(vurgu, dtype=float)
        self._anim_base_colors = base

        # Graf modu: tüm kenarları (n-1 ardışık) TEK LineCollection olarak yarat —
        # her karede FancyArrowPatch yeniden yaratmak yerine sadece renk/alpha
        # güncellenir (donmanın asıl kaynağı buydu). Ok başları animasyonda yok;
        # animasyon bitince _kare_ciz gerçek okları + tooltip'i çizer.
        self._anim_edges = None
        self._anim_edge_base = None
        if graf and self._G is not None and n >= 2:
            m = n - 1
            seg = np.empty((m, 2, 2), dtype=float)
            ecol = np.empty((m, 4), dtype=float)
            for i in range(m):
                seg[i, 0, 0], seg[i, 0, 1] = xs[i], ys[i]
                seg[i, 1, 0], seg[i, 1, 1] = xs[i + 1], ys[i + 1]
                w = float(self._G[i][i + 1].get("agirlik", 0.0))
                ecol[i] = _kenar_rengi(w)
            self._anim_edge_base = ecol
            ec0 = ecol.copy()
            ec0[:, 3] = 0.0
            self._anim_edges = LineCollection(seg, colors=ec0, linewidths=1.2, zorder=1)
            self._axes.add_collection(self._anim_edges)

        # Kalıcı scatter — başta tüm tohumlar saydam (görünmez). edgecolors="none":
        # aksi halde saydam yüzlerin etrafındaki kenar yine de tüm n konumu belli ederdi.
        ilk = base.copy()
        ilk[:, 3] = 0.0
        self._anim_scatter = self._axes.scatter(
            xs, ys, s=sizes, c=ilk, edgecolors="none", linewidths=0, zorder=2,
        )
        self._scatter = self._anim_scatter  # hover hit-test için referans

        # Aktif tohum halkası (tek nokta) — yalnızca düz spiral modunda
        if not ayciegi and not graf:
            halka_boyut = max(taban, 12.0) * 5.0
            self._anim_ring = self._axes.scatter(
                [xs[0]], [ys[0]], s=halka_boyut,
                facecolors="none", edgecolors=theme.AKSAN_KOYU,
                linewidths=1.8, zorder=5,
            )
            self._anim_ring.set_visible(False)
        else:
            self._anim_ring = None

        # Fibonacci etiketleri — bir kez yarat, görünmez başlat (ayçiçeği hariç)
        self._anim_labels = {}
        if not ayciegi:
            font_renk = theme.AKSAN_KOYU if graf else "#555555"
            font_boyut = 9 if graf else 8
            for idx in self._fib_indeksleri:
                if idx >= n:
                    continue
                x, y = konumlar[idx]
                t = self._axes.text(
                    x + 1.5, y + 1.5, str(idx),
                    fontsize=font_boyut, color=font_renk, family="Georgia", zorder=4,
                )
                t.set_visible(False)
                self._anim_labels[idx] = t

        self._tooltip = None
        self._oklar = []
        self._canvas.draw_idle()

    def _hizli_kare_ciz(self, k: int) -> None:
        """
        Hızlı yol: kalıcı artist'lerin yalnızca renk/görünürlüğünü güncelle, sonra
        draw_idle. axes.clear() + artist yeniden-yaratma yok → kare başına maliyet
        sabit kalır (büyük n'de donma yok). Blitting kullanılmaz (gösterilmemiş
        canvas / detached renderer'a karşı sağlam).
        """
        if self._anim_scatter is None or self._anim_base_colors is None:
            return
        n = self._anim_toplam
        k = max(0, min(k, n - 1))

        fc = self._anim_base_colors.copy()
        if k + 1 < n:
            fc[k + 1:, 3] = 0.0  # yerleşmemiş tohumlar saydam
        if self._anim_aktif_rgba is not None:
            fc[k] = self._anim_aktif_rgba  # aktif tohum vurgulu
        self._anim_scatter.set_facecolors(fc)

        # Graf kenarları: i. kenar (i→i+1) ancak i+1 yerleştiyse görünür → i>=k gizli
        if self._anim_edges is not None and self._anim_edge_base is not None:
            ec = self._anim_edge_base.copy()
            if k < len(ec):
                ec[k:, 3] = 0.0
            self._anim_edges.set_colors(ec)

        if self._anim_ring is not None:
            self._anim_ring.set_offsets([self._konumlar[k]])
            self._anim_ring.set_visible(True)

        for idx, t in self._anim_labels.items():
            if idx <= k and not t.get_visible():
                t.set_visible(True)

        self._canvas.draw_idle()

    def _hizli_animasyon_sonlandir(self) -> None:
        """Hızlı animasyon artist'lerini bırak ve sahneyi standart (statik) çiz."""
        self._anim_hizli = False
        self._anim_bg = None
        self._anim_scatter = None
        self._anim_ring = None
        self._anim_labels = {}
        self._anim_base_colors = None
        self._anim_aktif_rgba = None
        self._anim_edges = None
        self._anim_edge_base = None
        kare = max(0, min(self._anim_kare, self._anim_toplam - 1))
        self._kare_ciz(
            kare_no=kare,
            toplam=self._anim_toplam,
            konumlar=self._konumlar,
            fib_indeksleri=self._fib_indeksleri,
        )

    def animasyonu_durdur(self) -> None:
        """Animasyonu durdurur; sahne mevcut karede donar."""
        calisiyordu = self._timer.isActive()
        if calisiyordu:
            self._timer.stop()
        # Hızlı yol artist'leri 'animated' — normal redraw'da kaybolurlar; mevcut
        # kareyi standart (kalıcı) artist'lerle sabitle ki donmuş görüntü kalıcı olsun.
        if self._anim_hizli:
            self._hizli_animasyon_sonlandir()

    def hiz_guncelle(self, interval_ms: int) -> None:
        """Çalışan animasyonun interval'ını canlı günceller."""
        self._timer.setInterval(interval_ms)

    def _animasyon_tick(self) -> None:
        """QTimer tick — bir sonraki kare(ler)i yerleştir."""
        self._anim_kare = min(self._anim_kare + self._anim_batch, self._anim_toplam - 1)
        if self._anim_hizli:
            self._hizli_kare_ciz(self._anim_kare)
        else:
            self._kare_ciz(
                kare_no=self._anim_kare,
                toplam=self._anim_toplam,
                konumlar=self._konumlar,
                fib_indeksleri=self._fib_indeksleri,
            )
        if self._anim_kare >= self._anim_toplam - 1:
            self._timer.stop()
            if self._anim_hizli:
                self._hizli_animasyon_sonlandir()
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

    # ---- Graf modu (ana canvas üzerinde toggle) ----

    def graf_modu_ac(self) -> None:
        """Spiralin yönlü graf görünümünü aktive et — kenarlar + tooltip."""
        if self._graf_modu:
            return
        self._graf_modu = True
        # Mevcut n + α'dan grafı oluştur
        if self._n > 0:
            self._G = grafi_olustur(self._n, aci_radyan=math.radians(self._aci_derece))
        if self._konumlar:
            self._yeniden_ciz()

    def graf_modu_kapat(self) -> None:
        """Graf modunu kapat — kenarlar ve tooltip kaldırılır."""
        if not self._graf_modu:
            return
        self._graf_modu = False
        self._G = None
        self._oklar = []
        self._tooltip = None
        if self._konumlar:
            self._yeniden_ciz()

    def graf_modu_acik_mi(self) -> bool:
        return self._graf_modu

    # ---- Ayçiçeği modu (kayıt için temiz tohum yatağı görünümü) ----

    def ayciegi_modu_ac(self) -> None:
        """Tüm Fibonacci vurgularını kapat, radial gradient tohum yatağı çiz."""
        if self._ayciegi_modu:
            return
        # Graf modu açıksa kapat — ayçiçeği modu onunla birleşmez
        if self._graf_modu:
            self.graf_modu_kapat()
        self._ayciegi_modu = True
        if self._konumlar:
            self._yeniden_ciz()

    def ayciegi_modu_kapat(self) -> None:
        """Standart akademik spiral görünümüne geri dön."""
        if not self._ayciegi_modu:
            return
        self._ayciegi_modu = False
        # Zemin rengini geri al
        self._axes.set_facecolor(theme.ARKA_PLAN_KART)
        if self._konumlar:
            self._yeniden_ciz()

    def ayciegi_modu_acik_mi(self) -> bool:
        return self._ayciegi_modu
