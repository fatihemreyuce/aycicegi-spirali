"""
animator.py
-----------
matplotlib FuncAnimation ile tohumların teker teker eklenmesini canlandırır.

Renkler:
    - Aktif tohum         : kırmızı
    - Ziyaret edilmişler  : yeşil (parlak)
    - Henüz eklenmemişler : gri (mat)
    - Vurgu (validator)   : mavi
"""

import time
from typing import Callable, Iterable, Optional

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
import networkx as nx

from graph_builder import dugum_konumlari
from visualizer import figur_hazirla, KENAR_RENGI


# Animasyona özel renk sabitleri
RENK_AKTIF = "#ff3b3b"        # Kırmızı
RENK_ZIYARET = "#5cff7a"      # Parlak yeşil
RENK_BEKLEME = "#7d7d7d"      # Gri
RENK_VURGU = "#1f8bff"        # Mavi (validator)
RENK_SECILI = "#c389ff"       # Mor (kullanıcının tıklayarak seçtiği tohum)

# Graf modu için renkler
GRAF_OK_RENGI = "#ffd400"      # Sarı (kenar/ok rengi)
TOOLTIP_BG = "#2b2b2b"         # Tooltip arka planı (koyu gri)
TOOLTIP_FG = "#ffffff"         # Tooltip yazı rengi (beyaz)


# Hız ön ayarları (ms cinsinden kare aralığı)
HIZ_AYARLARI = {
    "Yavaş": 500,
    "Normal": 200,
    "Hızlı": 50,
    "Anında": 1,
}


def kenar_kalinligi(agirlik: float) -> float:
    """
    Kenar ağırlığına göre çizgi kalınlığını döndürür (graf modu için).

    Eşikler:
        w < 1.6                 → 0.5
        1.6 <= w < 1.618        → 1.5
        w >= 1.618              → 2.5
    """
    if agirlik < 1.6:
        return 0.5
    if agirlik < 1.618:
        return 1.5
    return 2.5


def _alt_indis(num: int) -> str:
    """Tam sayıyı Unicode alt-indis basamaklarına çevirir (örn. 45 → '₄₅')."""
    tablo = "₀₁₂₃₄₅₆₇₈₉"
    return "".join(tablo[int(d)] for d in str(abs(num)))


class SpiralAnimator:
    """
    Tohumları tek tek ekleyen animasyon yöneticisi.

    Kullanım:
        anim = SpiralAnimator(G, ax)
        anim.basla(interval_ms=200, on_step=lambda i: ...)
    """

    def __init__(
        self,
        G: nx.DiGraph,
        ax: Optional[Axes] = None,
        vurgu_indexleri: Optional[Iterable[int]] = None,
        graf_modu: bool = False,
    ):
        self.G = G
        # Mevcut bir Axes verilmezse yeni bir figür oluştur
        if ax is None:
            self.fig, self.ax = figur_hazirla()
        else:
            self.ax = ax
            self.fig: Figure = ax.figure  # type: ignore[assignment]

        self.vurgu_kumesi = set(vurgu_indexleri) if vurgu_indexleri else set()
        # Kullanıcının tıklayarak seçtiği tohum (mor) — None ise seçili tohum yok
        self.secili_index: Optional[int] = None
        self.konumlar = dugum_konumlari(G)
        self.sirali_dugumler = sorted(self.konumlar.keys())

        # Tohum sayısı 0 ise animasyon yapacak bir şey yok
        self.toplam = len(self.sirali_dugumler)

        # Graf modu açıkken kenarlar ok başlı ve etiketli çizilir
        self.graf_modu = graf_modu

        # Hazırlık: scatter ve kenar çizgileri için tek seferlik ayarlar
        self._scatter = None
        self._cizgiler = []        # Normal modda Line2D listesi
        self._oklar = []           # Graf modunda FancyArrowPatch listesi
        self._anim: Optional[FuncAnimation] = None
        self._on_step: Optional[Callable[[int], None]] = None
        # Manuel adım (Adım butonu) için son yerleşen tohum no — -1 = henüz hiçbiri
        self._manuel_kare: int = -1
        # Tooltip iterasyonunu görünür kenarlarla sınırlamak için son çizilen kare
        self._son_kare: int = -1
        # Mouse motion throttling — saniyede en fazla ~33 hit-test
        self._son_motion_zamani: float = 0.0
        self._motion_throttle_sn: float = 0.030

        # Tooltip artefaktı ve mouse motion bağlantı kimliği — sadece graf modunda
        self._tooltip = None
        self._tooltip_cid: Optional[int] = None

        self._sahneyi_hazirla()

        # Graf modunda tooltip sistemini kur
        if self.graf_modu:
            self._tooltip_olustur()

    # ------------------------------------------------------------------ #
    # Sahne kurulumu
    # ------------------------------------------------------------------ #

    def _sahneyi_hazirla(self) -> None:
        """Tüm tohumları gri, kenarları görünmez başlatır."""
        self.ax.clear()
        # figür_hazirla çağrılmış olabilir ama clear sonrası tekrar düzenleyelim
        self.ax.set_facecolor("#0b3d2e")
        self.ax.set_aspect("equal", adjustable="datalim")
        self.ax.axis("off")

        if self.toplam == 0:
            return

        xs = [self.konumlar[i][0] for i in self.sirali_dugumler]
        ys = [self.konumlar[i][1] for i in self.sirali_dugumler]

        # Tüm noktaları başta gri olarak çiz (scatter tek seferde oluşturulur)
        self._scatter = self.ax.scatter(
            xs, ys,
            s=40,
            c=[RENK_BEKLEME] * self.toplam,
            edgecolors="black",
            linewidths=0.3,
            zorder=2,
        )

        # Kenar artefaktları — graf moduna göre iki farklı yol
        self._cizgiler = []
        self._oklar = []

        if self.graf_modu:
            # Graf modu: ok başlı sarı kenarlar (ağırlık değeri tooltip'te gösterilir)
            for u, v, veri in self.G.edges(data=True):
                x0, y0 = self.konumlar[u]
                x1, y1 = self.konumlar[v]
                w = float(veri.get("agirlik", 0.0))
                lw = kenar_kalinligi(w)

                ok = FancyArrowPatch(
                    (x0, y0), (x1, y1),
                    arrowstyle="-|>",
                    color=GRAF_OK_RENGI,
                    linewidth=lw,
                    mutation_scale=10,
                    alpha=0.85,          # hedef alpha — görünürlük set_visible ile toggle
                    shrinkA=4, shrinkB=4,  # nokta üzerine binmesin
                    zorder=1,
                )
                ok.set_visible(False)    # başlangıçta gizli — render pipeline'ı atlar
                self.ax.add_patch(ok)
                self._oklar.append((u, v, ok))
        else:
            # Normal mod: ince soluk yeşil çizgiler (mevcut davranış aynen korunur)
            for u, v in self.G.edges():
                x0, y0 = self.konumlar[u]
                x1, y1 = self.konumlar[v]
                (line,) = self.ax.plot(
                    [x0, x1], [y0, y1],
                    color=KENAR_RENGI,
                    linewidth=0.4,
                    alpha=0.6,   # hedef alpha — görünürlük set_visible ile toggle
                    zorder=1,
                )
                line.set_visible(False)  # başlangıçta gizli
                self._cizgiler.append((u, v, line))

        # Eksen sınırlarını manuel olarak biraz genişlet — son tohumda crop olmasın
        if xs and ys:
            xmin, xmax = min(xs), max(xs)
            ymin, ymax = min(ys), max(ys)
            pad_x = (xmax - xmin) * 0.05 + 1
            pad_y = (ymax - ymin) * 0.05 + 1
            self.ax.set_xlim(xmin - pad_x, xmax + pad_x)
            self.ax.set_ylim(ymin - pad_y, ymax + pad_y)

    # ------------------------------------------------------------------ #
    # Kare güncellemesi
    # ------------------------------------------------------------------ #

    def _kareyi_guncelle(self, kare_no: int):
        """
        kare_no'ya kadar olan tohumları yerleştirir.
        Aktif (en yeni) tohum kırmızı, öncekiler yeşil, sonrakiler gri olur.
        """
        if self._scatter is None:
            return ()

        # Tooltip hit-test sadece görünür kenarlarda yapsın
        self._son_kare = kare_no
        # Otomatik animasyon ilerlerken manuel sayacı senkron tut — animasyon
        # bittikten sonra "Geri" butonu kaldığı yerden devam edebilsin
        if kare_no > self._manuel_kare:
            self._manuel_kare = kare_no

        renkler = []
        for i in self.sirali_dugumler:
            if i == self.secili_index and i <= kare_no:
                # Kullanıcı tıklamasıyla seçilen tohum — mor, en yüksek öncelik
                renkler.append(RENK_SECILI)
            elif i in self.vurgu_kumesi and i <= kare_no:
                # Validator vurgusu — mavi
                renkler.append(RENK_VURGU)
            elif i < kare_no:
                renkler.append(RENK_ZIYARET)
            elif i == kare_no:
                renkler.append(RENK_AKTIF)
            else:
                renkler.append(RENK_BEKLEME)
        self._scatter.set_color(renkler)

        # Aktif tohuma kadar olan kenarları görünür yap.
        # set_visible: alpha=0'dan farklı olarak görünmez artist'i tüm render
        # pipeline'ı atlar — graf modunda çok daha hızlı.
        if self.graf_modu:
            for u, v, ok in self._oklar:
                ok.set_visible(v <= kare_no)
        else:
            for u, v, line in self._cizgiler:
                line.set_visible(v <= kare_no)

        # Dış dünyaya geri çağır — sağ paneldeki canlı bilgi için
        if self._on_step is not None:
            try:
                self._on_step(kare_no)
            except Exception:
                # GUI tarafındaki bir hata animasyonu durdurmasın
                pass

        return (self._scatter,)

    # ------------------------------------------------------------------ #
    # Tooltip (sadece graf modu)
    # ------------------------------------------------------------------ #

    def _tooltip_olustur(self) -> None:
        """Koyu gri arka planlı, beyaz yazılı tooltip ve mouse hareket bağlantısını kurar."""
        # Tek bir Text artefaktı yeterli; içeriği hover'a göre değiştiririz
        self._tooltip = self.ax.text(
            0, 0, "",
            color=TOOLTIP_FG,
            fontsize=11,               # daha okunaklı boyut
            ha="left", va="bottom",
            bbox=dict(
                boxstyle="round,pad=0.55",
                facecolor=TOOLTIP_BG,   # koyu gri
                edgecolor=TOOLTIP_BG,
                alpha=0.92,
            ),
            zorder=10,
        )
        self._tooltip.set_visible(False)
        # motion_notify_event'e bağlan — kimliği saklayıp temizlerken kopar
        self._tooltip_cid = self.fig.canvas.mpl_connect(
            "motion_notify_event", self._on_motion
        )

    def _on_motion(self, event) -> None:
        """Mouse hareketi — düğüm/kenar üzerinde tooltip göster, yoksa gizle."""
        if self._tooltip is None:
            return
        # Eksen dışındaysa veya koordinat yoksa tooltip'i gizle (throttle UYGULAMAZ —
        # leave olayında gecikmeli kapanma istemiyoruz)
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self.fig.canvas.draw_idle()
            return

        # Throttle: hit-test pahalı (n=2000'de ~2000 contains çağrısı/event).
        # Saniyede ~33 motion event'le sınırla — tooltip görsel olarak hâlâ akıcı.
        simdi = time.perf_counter()
        if simdi - self._son_motion_zamani < self._motion_throttle_sn:
            return
        self._son_motion_zamani = simdi

        metin: Optional[str] = None

        # 1) Önce düğümleri (scatter noktaları) kontrol et — daha öncelikli
        if self._scatter is not None:
            ic, info = self._scatter.contains(event)
            if ic:
                idx_dizide = int(info["ind"][0])
                node = self.sirali_dugumler[idx_dizide]
                x, y = self.konumlar[node]
                f_val = self.G.nodes[node].get("fibonacci", 0)
                metin = (
                    f"v{_alt_indis(node)} | F = {f_val} | "
                    f"Konum: ({x:.2f}, {y:.2f})"
                )

        # 2) Düğüm değilse kenarları (FancyArrowPatch) kontrol et —
        #    YALNIZCA görünür olanlar (animasyonun o anki karesine kadar yerleşmiş)
        if metin is None:
            son = self._son_kare
            for u, v, ok in self._oklar:
                # Henüz görünmeyen kenarı hit-test etme — büyük performans kazancı
                if v > son:
                    continue
                ic, _ = ok.contains(event)
                if ic:
                    w = float(self.G[u][v].get("agirlik", 0.0))
                    metin = (
                        f"v{_alt_indis(u)} → v{_alt_indis(v)} | w = {w:.4f}"
                    )
                    break

        if metin is not None:
            # Tooltip'i imlecin biraz sağ-üstüne yerleştir
            self._tooltip.set_text(metin)
            self._tooltip.set_position((event.xdata, event.ydata))
            if not self._tooltip.get_visible():
                self._tooltip.set_visible(True)
            self.fig.canvas.draw_idle()
        else:
            if self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self.fig.canvas.draw_idle()

    def _tooltip_kapat(self) -> None:
        """Tooltip bağlantısını kopar — animatör değiştirilirken çağrılır."""
        if self._tooltip_cid is not None:
            try:
                self.fig.canvas.mpl_disconnect(self._tooltip_cid)
            except Exception:
                pass
            self._tooltip_cid = None
        self._tooltip = None

    # ------------------------------------------------------------------ #
    # Genel API
    # ------------------------------------------------------------------ #

    def basla(
        self,
        interval_ms: int = 200,
        on_step: Optional[Callable[[int], None]] = None,
        repeat: bool = False,
    ) -> Optional[FuncAnimation]:
        """
        Animasyonu başlatır.

        interval_ms = 1 verilirse "anında" modu olarak değerlendirilir ve
        animasyon yerine tüm tohumlar tek seferde çizilir.
        """
        self._on_step = on_step

        if self.toplam == 0:
            return None

        # Anında çizim modu
        if interval_ms <= 1:
            self._kareyi_guncelle(self.toplam - 1)
            if self._on_step is not None:
                self._on_step(self.toplam - 1)
            self.fig.canvas.draw_idle()
            return None

        self._anim = FuncAnimation(
            self.fig,
            self._kareyi_guncelle,
            frames=range(self.toplam),
            interval=interval_ms,
            blit=False,
            repeat=repeat,
        )
        return self._anim

    def durdur(self) -> None:
        """Animasyonu durdurur ve tooltip bağlantısını koparır (varsa)."""
        if self._anim is not None:
            try:
                self._anim.event_source.stop()
            except Exception:
                pass
            self._anim = None
        # Tooltip event handler'ını sızdırma — yeni animatöre yer açıyoruz
        self._tooltip_kapat()

    def adim_at(self) -> Optional[int]:
        """
        Manuel mod: bir sonraki tohumu yerleştirir, görünüm o haliyle donar.

        Otomatik animasyon çalışıyorsa önce durdurur. Tüm tohumlar yerleştiyse
        None döner, aksi halde yerleştirilen yeni kare numarasını döndürür.
        """
        # Çalışan otomatik animasyonu kes — manuel kontrole geçiyoruz
        if self._anim is not None:
            try:
                self._anim.event_source.stop()
            except Exception:
                pass
            self._anim = None

        if self.toplam == 0 or self._manuel_kare >= self.toplam - 1:
            return None

        self._manuel_kare += 1
        self._kareyi_guncelle(self._manuel_kare)  # _on_step de tetiklenir
        self.fig.canvas.draw_idle()
        return self._manuel_kare

    def adim_geri(self) -> Optional[int]:
        """
        Manuel mod: bir adım geri — son yerleştirilen tohumu kaldırır.

        Sahne boşsa (manuel_kare = -1) None döner.
        Tek tohum kaldıysa onu da kaldırır ve sahne tamamen boşalır.
        Döndürür: yeni manuel_kare (boş sahne için -1).
        """
        # Otomatik animasyon çalışıyorsa önce kes
        if self._anim is not None:
            try:
                self._anim.event_source.stop()
            except Exception:
                pass
            self._anim = None

        if self._manuel_kare < 0:
            return None

        self._manuel_kare -= 1
        # _kareyi_guncelle(-1): tüm renkler "bekleme", tüm kenarlar gizli — temiz sıfır
        self._kareyi_guncelle(self._manuel_kare)
        self.fig.canvas.draw_idle()
        return self._manuel_kare

    def temizle(self) -> None:
        """Sahneyi sıfırlar (Sıfırla butonu için)."""
        self.durdur()
        self._manuel_kare = -1
        self._son_kare = -1
        self._sahneyi_hazirla()
        self.fig.canvas.draw_idle()


if __name__ == "__main__":
    from graph_builder import grafi_olustur

    G = grafi_olustur(150)
    anim = SpiralAnimator(G)
    anim.basla(interval_ms=50)
    plt.show()
