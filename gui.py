"""
gui.py
------
Tkinter tabanlı arayüz.

Düzen:
    - Sol panel  : n kaydırıcısı (50-2000) + senkron Entry, hız seçimi,
                   Çiz/Sıfırla butonları, validator giriş kutusu ve sonucu.
    - Orta panel : matplotlib canvas (ayçiçeği spirali)
    - Sağ panel  : Canlı bilgi — aktif tohum no, F(i+1)/F(i), |oran-phi|.
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
# Tkinter ile uyumlu backend — pencere açılmadan önce ayarlanmalı
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from fibonacci import fibonacci_dizisi, fibonacci_n, formatla_buyuk_sayi
from graph_builder import grafi_olustur
from animator import SpiralAnimator, HIZ_AYARLARI
from utils import oran_ve_fark, PHI, ALTIN_ACI_DERECE
from validator import (
    dogrula_ve_index,
    en_yakin_iki_fibonacci_indeksli,
    SONUC_ACCEPT,
)
from convergence_plot import yakinsama_penceresi_ac
from comparison_window import karsilastirma_penceresi_ac
from traversal_window import traversal_penceresi_ac


# Tema renkleri (arka plan ve panel başlıkları için)
PANEL_BG = "#1b1b1b"
PANEL_FG = "#f0f0f0"
ACCENT = "#ffd400"
ACCEPT_RENGI = "#5cff7a"   # Yeşil — Accept sonucu
REJECT_RENGI = "#ff7070"   # Kırmızımsı — Reject sonucu


def _alt_indis(num: int) -> str:
    """Tam sayıyı Unicode alt-indis basamaklarına çevirir (örn. 45 → '₄₅')."""
    tablo = "₀₁₂₃₄₅₆₇₈₉"
    return "".join(tablo[int(d)] for d in str(abs(num)))


class AyCicegiGUI:
    """
    Ayçiçeği spirali için ana uygulama penceresi.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.root.configure(bg=PANEL_BG)
        self.root.geometry("1200x720")

        # Çekirdek durum değişkenleri
        self.G = None
        self.fib = []
        self.animator: SpiralAnimator | None = None
        self.vurgu_indexleri: set[int] = set()

        # Pan (sol-tık basılı tut + sürükle) için durum
        self._pan_anchor: tuple[float, float] | None = None
        self._pan_ax = None

        # Tkinter değişkenleri
        self.n_var = tk.IntVar(value=100)
        # Entry kutusu için ayrı StringVar — slider ile çift yönlü senkronize edilir
        self.n_text_var = tk.StringVar(value="100")
        # Senkronizasyon sırasında trace döngüsünü engelleyen kilit
        self._n_senk_kilidi = False
        # Açı (derece) — varsayılan altın açı; slider ile 30°-180° aralığında değişir
        self.aci_var = tk.DoubleVar(value=ALTIN_ACI_DERECE)
        self.aci_text_var = tk.StringVar(value=f"{ALTIN_ACI_DERECE:.4f}")
        self._aci_senk_kilidi = False
        self.hiz_var = tk.StringVar(value="Normal")
        self.dogrulanacak_var = tk.StringVar(value="")
        self.dogrulama_sonuc_var = tk.StringVar(value="")
        # Reject durumunda "En yakın: F(5)=5, F(6)=8" alt satırı
        self.dogrulama_alt_var = tk.StringVar(value="")
        # Reject/Accept sonucuna göre etiket rengi değişir
        self._dogrulama_label: ttk.Label | None = None

        # Sağ panel canlı bilgi değişkenleri
        self.bilgi_tohum_no = tk.StringVar(value="—")
        self.bilgi_fib = tk.StringVar(value="—")
        self.bilgi_oran = tk.StringVar(value="—")
        self.bilgi_phi_farki = tk.StringVar(value="—")
        # Animasyon sırasında dinamik aktif kenar bilgisi
        self.bilgi_aktif_kenar = tk.StringVar(value="—")
        self.bilgi_aktif_agirlik = tk.StringVar(value="—")
        # Seçili tohum (mor) bilgi panelleri — kullanıcı bir tohuma tıklayınca dolar
        self.secili_index_var = tk.StringVar(value="—")
        self.secili_fib_var = tk.StringVar(value="—")
        self.secili_aci_var = tk.StringVar(value="—")
        self.secili_yaricap_var = tk.StringVar(value="—")
        self.secili_konum_var = tk.StringVar(value="—")

        # GRAF MODELİ — n ile dinamik |V| ve |E|
        baslangic_n = int(self.n_var.get())
        self.graf_v_var = tk.StringVar(value=f"Düğüm sayısı |V|: {baslangic_n}")
        self.graf_e_var = tk.StringVar(value=f"Kenar sayısı |E|: {max(0, baslangic_n - 1)}")

        # Graf modu durumu ve sağ paneldeki "Graf Bilgisi" değişkenleri
        self.graf_modu = False
        self.graf_dugum_var = tk.StringVar(value="Düğüm sayısı: —")
        self.graf_kenar_var = tk.StringVar(value="Kenar sayısı: —")
        self.graf_yon_var = tk.StringVar(value="Yön: vᵢ → vᵢ₊₁")
        self.graf_min_var = tk.StringVar(value="Min ağırlık: —")
        self.graf_max_var = tk.StringVar(value="Max ağırlık: —")
        self.graf_avg_var = tk.StringVar(value="Ort ağırlık: —")

        self._stil_ayarla()
        self._yerlesimi_kur()

        # Açılışta hazır figürü göster
        self.figure = Figure(figsize=(7, 7), facecolor="#0b3d2e")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#0b3d2e")
        self.ax.set_aspect("equal", adjustable="datalim")
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.orta_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.draw()

        # Mouse scroll / touchpad iki-parmak scroll ile imleç-merkezli zoom
        self.canvas.mpl_connect("scroll_event", self._zoom_olay)
        # Sol-tık basılı tutup sürükleyerek kaydırma (pan)
        self.canvas.mpl_connect("button_press_event", self._pan_basla)
        self.canvas.mpl_connect("motion_notify_event", self._pan_hareket)
        self.canvas.mpl_connect("button_release_event", self._pan_bitir)

    # ------------------------------------------------------------------ #
    # Stil ve yerleşim
    # ------------------------------------------------------------------ #

    def _stil_ayarla(self) -> None:
        """ttk için tutarlı bir koyu tema kur."""
        stil = ttk.Style(self.root)
        try:
            stil.theme_use("clam")
        except tk.TclError:
            pass

        stil.configure("Panel.TFrame", background=PANEL_BG)
        stil.configure("Panel.TLabel", background=PANEL_BG, foreground=PANEL_FG, font=("Segoe UI", 10))
        stil.configure("Baslik.TLabel", background=PANEL_BG, foreground=ACCENT, font=("Segoe UI", 12, "bold"))
        stil.configure("Bilgi.TLabel", background=PANEL_BG, foreground=ACCENT, font=("Consolas", 11, "bold"))
        # Validator sonuç etiketleri — büyük ve belirgin
        stil.configure("Sonuc.TLabel", background=PANEL_BG, foreground=ACCEPT_RENGI, font=("Segoe UI", 13, "bold"))
        stil.configure("SonucAlt.TLabel", background=PANEL_BG, foreground=PANEL_FG, font=("Segoe UI", 10, "italic"))
        # Validator açıklama metni için soluk-küçük italik stil
        stil.configure("Yardim.TLabel", background=PANEL_BG, foreground="#b0b0b0", font=("Segoe UI", 9, "italic"))
        stil.configure("Panel.TButton", font=("Segoe UI", 10, "bold"))
        stil.configure("Panel.TRadiobutton", background=PANEL_BG, foreground=PANEL_FG, font=("Segoe UI", 9))
        stil.configure("Panel.Horizontal.TScale", background=PANEL_BG)
        stil.configure("Panel.TEntry", fieldbackground="#2a2a2a", foreground=PANEL_FG, insertcolor=PANEL_FG)

    def _yerlesimi_kur(self) -> None:
        """Üç sütunlu ana yerleşimi oluştur: sol kontroller, orta canvas, sağ bilgi."""
        self.root.columnconfigure(0, weight=0, minsize=240)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0, minsize=240)
        self.root.rowconfigure(0, weight=1)

        self.sol_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        self.sol_panel.grid(row=0, column=0, sticky="nsw")

        self.orta_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=4)
        self.orta_panel.grid(row=0, column=1, sticky="nsew")

        self.sag_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        # nsew: sütunun tamamını doldur — anchor="w" etiketleri sol kenara hizalansın
        self.sag_panel.grid(row=0, column=2, sticky="nsew")

        self._sol_paneli_kur()
        self._sag_paneli_kur()

    def _sol_paneli_kur(self) -> None:
        """Kontroller: kaydırıcı, hız, butonlar, validator."""
        ttk.Label(self.sol_panel, text="KONTROLLER", style="Baslik.TLabel").pack(anchor="w", pady=(0, 10))

        # n kaydırıcısı
        ttk.Label(self.sol_panel, text="Tohum sayısı (n)", style="Panel.TLabel").pack(anchor="w")

        self.n_label = ttk.Label(self.sol_panel, text=f"n = {self.n_var.get()}", style="Bilgi.TLabel")
        self.n_label.pack(anchor="w")

        # Slider ve elle giriş aynı satırda yan yana — çift yönlü senkronize edilir
        n_satiri = ttk.Frame(self.sol_panel, style="Panel.TFrame")
        n_satiri.pack(fill="x", pady=(2, 12))

        kaydirici = ttk.Scale(
            n_satiri,
            from_=50, to=2000,
            orient="horizontal",
            variable=self.n_var,
            command=self._n_degisti,
            style="Panel.Horizontal.TScale",
        )
        kaydirici.pack(side="left", fill="x", expand=True)

        # Elle sayı girişi (50-2000 aralığında doğrulanır)
        self.n_entry = ttk.Entry(
            n_satiri,
            textvariable=self.n_text_var,
            width=6,
            style="Panel.TEntry",
            justify="center",
        )
        self.n_entry.pack(side="right", padx=(6, 0))
        # Enter veya odak kaybı ile değer onaylansın
        self.n_entry.bind("<Return>", self._n_entry_onayla)
        self.n_entry.bind("<FocusOut>", self._n_entry_onayla)

        # Açı (derece) — altın açı varsayılan, slider ile 30°-180° aralığı
        ttk.Label(self.sol_panel, text="Açı (°)", style="Panel.TLabel").pack(anchor="w", pady=(0, 0))
        self.aci_label = ttk.Label(
            self.sol_panel,
            text=f"α = {self.aci_var.get():.4f}°",
            style="Bilgi.TLabel",
        )
        self.aci_label.pack(anchor="w")

        aci_satiri = ttk.Frame(self.sol_panel, style="Panel.TFrame")
        aci_satiri.pack(fill="x", pady=(2, 4))

        aci_kaydirici = ttk.Scale(
            aci_satiri,
            from_=30.0, to=180.0,
            orient="horizontal",
            variable=self.aci_var,
            command=self._aci_degisti,
            style="Panel.Horizontal.TScale",
        )
        aci_kaydirici.pack(side="left", fill="x", expand=True)

        self.aci_entry = ttk.Entry(
            aci_satiri,
            textvariable=self.aci_text_var,
            width=8,
            style="Panel.TEntry",
            justify="center",
        )
        self.aci_entry.pack(side="right", padx=(6, 0))
        self.aci_entry.bind("<Return>", self._aci_entry_onayla)
        self.aci_entry.bind("<FocusOut>", self._aci_entry_onayla)

        # "Altın açıya dön" hızlı geri çağırma butonu
        ttk.Button(
            self.sol_panel,
            text="🌟 Altın açıya dön (137.5077°)",
            style="Panel.TButton",
            command=self._aciyi_altina_sifirla,
        ).pack(fill="x", pady=(0, 12))

        # Hız seçimi
        ttk.Label(self.sol_panel, text="Animasyon hızı", style="Panel.TLabel").pack(anchor="w")
        hiz_cerc = ttk.Frame(self.sol_panel, style="Panel.TFrame")
        hiz_cerc.pack(anchor="w", pady=(2, 12))
        for label in HIZ_AYARLARI.keys():
            ttk.Radiobutton(
                hiz_cerc,
                text=label,
                value=label,
                variable=self.hiz_var,
                style="Panel.TRadiobutton",
            ).pack(anchor="w")

        # Eylem butonları
        btn_cerc = ttk.Frame(self.sol_panel, style="Panel.TFrame")
        btn_cerc.pack(fill="x", pady=(0, 16))
        ttk.Button(btn_cerc, text="Çiz", style="Panel.TButton",
                   command=self._ciz).pack(fill="x", pady=2)
        # Geri/İleri adım butonları yan yana — medya oynatıcı düzeni
        adim_satiri = ttk.Frame(btn_cerc, style="Panel.TFrame")
        adim_satiri.pack(fill="x", pady=2)
        ttk.Button(adim_satiri, text="◀ Geri", style="Panel.TButton",
                   command=self._geri).pack(side="left", fill="x", expand=True, padx=(0, 1))
        ttk.Button(adim_satiri, text="▶ Adım", style="Panel.TButton",
                   command=self._adim).pack(side="left", fill="x", expand=True, padx=(1, 0))
        ttk.Button(btn_cerc, text="Sıfırla", style="Panel.TButton",
                   command=self._sifirla).pack(fill="x", pady=2)
        # Graf modu toggle butonu — metni mevcut moda göre değişir
        self.graf_modu_btn = ttk.Button(
            btn_cerc,
            text="📊 Graf Modunu Aç",
            style="Panel.TButton",
            command=self._graf_modu_degistir,
        )
        self.graf_modu_btn.pack(fill="x", pady=2)


        # Validator bölümü — açıklayıcı başlık + kullanım ipuçları
        ttk.Label(self.sol_panel, text="FIBONACCI KONTROLÜ", style="Baslik.TLabel").pack(anchor="w", pady=(8, 2))
        ttk.Label(
            self.sol_panel,
            text="Bir tam sayı yazıp Fibonacci dizisinde olup\nolmadığını kontrol edin.",
            style="Yardim.TLabel",
            wraplength=220,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(self.sol_panel, text="Test edilecek sayı:", style="Panel.TLabel").pack(anchor="w")
        ttk.Entry(self.sol_panel, textvariable=self.dogrulanacak_var, style="Panel.TEntry").pack(fill="x", pady=(2, 2))
        ttk.Label(
            self.sol_panel,
            text="örn. 21, 89, 144 (Fibonacci) — 22, 100 (değil)",
            style="Yardim.TLabel",
            wraplength=220,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        ttk.Button(self.sol_panel, text="Doğrula", style="Panel.TButton",
                   command=self._dogrula).pack(fill="x")

        # Ne olacağını önceden açıkla — kullanıcı ilk kez bakanken bile anlasın
        ttk.Label(
            self.sol_panel,
            text="✅ Fibonacci ise: ilgili tohum (vᵢ) mavi vurgulanır\n"
                 "❌ Değilse: en yakın iki Fibonacci listelenir",
            style="Yardim.TLabel",
            wraplength=220,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        # Sonuç satırı (büyük, renkli) — _dogrula ile rengi güncellenir
        self._dogrulama_label = ttk.Label(
            self.sol_panel, textvariable=self.dogrulama_sonuc_var,
            style="Sonuc.TLabel", wraplength=220, justify="left",
        )
        self._dogrulama_label.pack(anchor="w", pady=(8, 0))
        # Reject durumunda en yakın iki Fibonacci'yi gösteren alt satır
        ttk.Label(
            self.sol_panel, textvariable=self.dogrulama_alt_var,
            style="SonucAlt.TLabel", wraplength=220, justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def _sag_paneli_kur(self) -> None:
        """Canlı bilgi paneli."""
        ttk.Label(self.sag_panel, text="CANLI BİLGİ", style="Baslik.TLabel").pack(anchor="w", pady=(0, 10))

        def _ikili(label_text: str, degisken: tk.StringVar):
            ttk.Label(self.sag_panel, text=label_text, style="Panel.TLabel").pack(anchor="w", pady=(8, 0))
            ttk.Label(self.sag_panel, textvariable=degisken, style="Bilgi.TLabel").pack(anchor="w")

        _ikili("Tohum no (i):", self.bilgi_tohum_no)
        _ikili("F(i):", self.bilgi_fib)
        _ikili("F(i+1) / F(i):", self.bilgi_oran)
        _ikili("|oran - phi|:", self.bilgi_phi_farki)
        # Animasyon esnasında dinamik aktif kenar bilgisi
        _ikili("Aktif kenar:", self.bilgi_aktif_kenar)
        _ikili("Ağırlık:", self.bilgi_aktif_agirlik)

        # Seçili tohum bölümü — tohuma tıklayınca dolar
        ttk.Label(self.sag_panel, text="SEÇİLİ TOHUM (tıkla)", style="Baslik.TLabel").pack(anchor="w", pady=(18, 4))
        _ikili("İndeks (i):", self.secili_index_var)
        _ikili("F(i):", self.secili_fib_var)
        _ikili("Açı (i·α mod 360°):", self.secili_aci_var)
        _ikili("Yarıçap (c·√i):", self.secili_yaricap_var)
        _ikili("Konum (x, y):", self.secili_konum_var)

        # GRAF MODELİ — formal tanım, |V|, |E|, kenar yön/ağırlık formülü
        ttk.Label(self.sag_panel, text="GRAF MODELİ", style="Baslik.TLabel").pack(anchor="w", pady=(18, 4))
        ttk.Label(self.sag_panel, text="Graf: G = (V, E, f, w)", style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, textvariable=self.graf_v_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, textvariable=self.graf_e_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, text="Kenar yönü: vᵢ → vᵢ₊₁", style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, text="Kenar ağırlığı: F(i+1)/F(i)", style="Panel.TLabel").pack(anchor="w")
        ttk.Button(
            self.sag_panel,
            text="Komşuluk Matrisi",
            style="Panel.TButton",
            command=self._komsuluk_matrisi_goster,
        ).pack(fill="x", pady=(6, 0))
        ttk.Button(
            self.sag_panel,
            text="📈 Yakınsama Grafiği",
            style="Panel.TButton",
            command=self._yakinsama_grafigini_goster,
        ).pack(fill="x", pady=(4, 0))
        ttk.Button(
            self.sag_panel,
            text="⚖️ Açı Karşılaştırma",
            style="Panel.TButton",
            command=lambda: karsilastirma_penceresi_ac(self.root),
        ).pack(fill="x", pady=(4, 0))
        ttk.Button(
            self.sag_panel,
            text="🔍 BFS / DFS Gezintisi",
            style="Panel.TButton",
            command=self._traversal_goster,
        ).pack(fill="x", pady=(4, 0))
        ttk.Button(
            self.sag_panel,
            text="🛣️ En Kısa Yol (Dijkstra)",
            style="Panel.TButton",
            command=self._dijkstra_goster,
        ).pack(fill="x", pady=(4, 0))

        # Sabit referans değerler — matematiksel formüller + hesaplanmış değerler
        ttk.Label(self.sag_panel, text="REFERANSLAR", style="Baslik.TLabel").pack(anchor="w", pady=(18, 4))

        ttk.Label(self.sag_panel, text="Altın oran:", style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, text="φ = (1 + √5) / 2", style="Bilgi.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, text=f"φ ≈ {PHI:.10f}", style="Bilgi.TLabel").pack(anchor="w")

        ttk.Label(self.sag_panel, text="Altın açı:", style="Panel.TLabel").pack(anchor="w", pady=(6, 0))
        ttk.Label(self.sag_panel, text="α = 360° × (1 − 1/φ)", style="Bilgi.TLabel").pack(anchor="w")
        ttk.Label(self.sag_panel, text=f"α ≈ {ALTIN_ACI_DERECE:.4f}°", style="Bilgi.TLabel").pack(anchor="w")

        # Graf Bilgisi alt paneli — graf modu açıldığında pack ile görünür kılınır
        self.graf_bilgisi_frame = ttk.Frame(self.sag_panel, style="Panel.TFrame")
        ttk.Label(self.graf_bilgisi_frame, text="Graf Bilgisi:", style="Baslik.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_dugum_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_kenar_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_yon_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_min_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_max_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(self.graf_bilgisi_frame, textvariable=self.graf_avg_var, style="Panel.TLabel").pack(anchor="w")
        # Başlangıçta gizli — toggle ile pack edilir

    # ------------------------------------------------------------------ #
    # Olay yöneticileri
    # ------------------------------------------------------------------ #

    def _n_degisti(self, _=None) -> None:
        """Kaydırıcıdan gelen değeri tam sayıya yuvarlayıp etiketi ve Entry'yi güncelle."""
        if self._n_senk_kilidi:
            return
        n = int(round(float(self.n_var.get())))
        self._n_senk_kilidi = True
        try:
            self.n_var.set(n)
            self.n_label.configure(text=f"n = {n}")
            # Entry kutusuyla çift yönlü senkronizasyon
            if self.n_text_var.get() != str(n):
                self.n_text_var.set(str(n))
            # GRAF MODELİ etiketleri n ile dinamik
            self._vE_etiketlerini_guncelle(n)
        finally:
            self._n_senk_kilidi = False

    def _n_entry_onayla(self, _=None) -> None:
        """Entry'ye yazılan değeri 50-2000 aralığında doğrulayıp slider'a yansıt."""
        if self._n_senk_kilidi:
            return
        ham = self.n_text_var.get().strip()
        try:
            n = int(ham)
        except ValueError:
            # Geçersiz girişte slider değerini geri yaz
            self.n_text_var.set(str(int(self.n_var.get())))
            return
        # Aralığa kelepçele
        n = max(50, min(2000, n))
        self._n_senk_kilidi = True
        try:
            self.n_var.set(n)
            self.n_text_var.set(str(n))
            self.n_label.configure(text=f"n = {n}")
            self._vE_etiketlerini_guncelle(n)
        finally:
            self._n_senk_kilidi = False

    def _vE_etiketlerini_guncelle(self, n: int) -> None:
        """GRAF MODELİ panelindeki |V| ve |E| etiketlerini günceller."""
        self.graf_v_var.set(f"Düğüm sayısı |V|: {n}")
        self.graf_e_var.set(f"Kenar sayısı |E|: {max(0, n - 1)}")

    def _grafi_garantile(self) -> bool:
        """Grafa erişim öncesi var olduğundan emin ol — yoksa anlık üret."""
        if self.G is not None and self.G.number_of_nodes() > 0:
            return True
        n = int(self.n_var.get())
        aci_rad = math.radians(float(self.aci_var.get()))
        self.fib = fibonacci_dizisi(n + 1)
        self.G = grafi_olustur(n, aci_radyan=aci_rad)
        return self.G.number_of_nodes() > 0


    def _aci_degisti(self, _=None) -> None:
        """Slider'dan gelen açıyı etiket ve Entry ile senkronize eder."""
        if self._aci_senk_kilidi:
            return
        aci = float(self.aci_var.get())
        self._aci_senk_kilidi = True
        try:
            self.aci_label.configure(text=f"α = {aci:.4f}°")
            if self.aci_text_var.get() != f"{aci:.4f}":
                self.aci_text_var.set(f"{aci:.4f}")
        finally:
            self._aci_senk_kilidi = False

    def _aci_entry_onayla(self, _=None) -> None:
        """Entry'ye yazılan açıyı 30-180 aralığında doğrulayıp slider'a yansıt."""
        if self._aci_senk_kilidi:
            return
        ham = self.aci_text_var.get().strip().replace(",", ".")
        try:
            aci = float(ham)
        except ValueError:
            self.aci_text_var.set(f"{float(self.aci_var.get()):.4f}")
            return
        aci = max(30.0, min(180.0, aci))
        self._aci_senk_kilidi = True
        try:
            self.aci_var.set(aci)
            self.aci_text_var.set(f"{aci:.4f}")
            self.aci_label.configure(text=f"α = {aci:.4f}°")
        finally:
            self._aci_senk_kilidi = False

    def _aciyi_altina_sifirla(self) -> None:
        """Açıyı tek tıkla altın açıya geri getirir."""
        self._aci_senk_kilidi = True
        try:
            self.aci_var.set(ALTIN_ACI_DERECE)
            self.aci_text_var.set(f"{ALTIN_ACI_DERECE:.4f}")
            self.aci_label.configure(text=f"α = {ALTIN_ACI_DERECE:.4f}°")
        finally:
            self._aci_senk_kilidi = False
        self._ciz()

    def _ciz(self) -> None:
        """Mevcut n, açı ve hız ayarlarına göre grafı yeniden inşa edip animasyonu başlat."""
        # Önceki animasyonu temizle
        if self.animator is not None:
            self.animator.durdur()

        n = int(self.n_var.get())
        aci_rad = math.radians(float(self.aci_var.get()))
        # Bir fazla eleman tutalım — son tohumda da F(i+1)/F(i) hesaplanabilsin
        self.fib = fibonacci_dizisi(n + 1)
        self.G = grafi_olustur(n, aci_radyan=aci_rad)

        # Eski figürü temizle ve animatöre teslim et (graf modu animatöre iletilir)
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.animator = SpiralAnimator(
            self.G,
            ax=self.ax,
            vurgu_indexleri=self.vurgu_indexleri,
            graf_modu=self.graf_modu,
        )

        interval = HIZ_AYARLARI.get(self.hiz_var.get(), 200)
        self.animator.basla(interval_ms=interval, on_step=self._adim_bilgisini_guncelle)
        self.canvas.draw_idle()

        # Graf modu açıksa sağ paneldeki istatistikleri yenile
        if self.graf_modu:
            self._graf_bilgisini_guncelle()

    def _adim(self) -> None:
        """
        Manuel adım: tek bir tohum daha yerleştirir.
        - Animatör yoksa veya n değiştiyse sahneyi yeniden kurar (animasyon başlatmadan).
        - Otomatik animasyon çalışıyorsa keser, son durumdan itibaren manuel ilerler.
        """
        n = int(self.n_var.get())

        # Sahneyi yeniden kurma gereksinimi: animatör yok ya da farklı n için kurulmuş
        yeniden_kur = (
            self.animator is None
            or self.G is None
            or self.G.number_of_nodes() != n
        )
        if yeniden_kur:
            if self.animator is not None:
                self.animator.durdur()
            aci_rad = math.radians(float(self.aci_var.get()))
            # Bir fazla eleman tutalım — son tohumda da F(i+1)/F(i) hesaplanabilsin
            self.fib = fibonacci_dizisi(n + 1)
            self.G = grafi_olustur(n, aci_radyan=aci_rad)
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            kol_renk_listesi = (
                kol_renkleri(n, self.parastichy_k) if self.parastichy_k else None
            )
            self.animator = SpiralAnimator(
                self.G,
                ax=self.ax,
                vurgu_indexleri=self.vurgu_indexleri,
                graf_modu=self.graf_modu,
                kol_renkleri=kol_renk_listesi,
            )
            if self.graf_modu:
                self._graf_bilgisini_guncelle()

        # Sağ paneldeki canlı bilgiyi her adımda güncellemek için geri çağrıyı bağla
        self.animator._on_step = self._adim_bilgisini_guncelle
        self.animator.adim_at()
        self.canvas.draw_idle()

    def _geri(self) -> None:
        """Manuel adımda bir geri al — son yerleşen tohumu sahneden kaldırır."""
        if self.animator is None:
            return
        # Sağ paneldeki bilgiyi yeni durumla güncellemek için geri çağrıyı bağla
        self.animator._on_step = self._adim_bilgisini_guncelle
        self.animator.adim_geri()
        self.canvas.draw_idle()

    def _sifirla(self) -> None:
        """Sahneyi temizle, bilgi panelini sıfırla."""
        if self.animator is not None:
            self.animator.temizle()
            self.animator.secili_index = None
        self.vurgu_indexleri.clear()
        self.dogrulama_sonuc_var.set("")
        self.dogrulama_alt_var.set("")
        self.bilgi_tohum_no.set("—")
        self.bilgi_fib.set("—")
        self.bilgi_oran.set("—")
        self.bilgi_phi_farki.set("—")
        self.bilgi_aktif_kenar.set("—")
        self.bilgi_aktif_agirlik.set("—")
        self._secili_tohum_bilgisini_guncelle()
        self.canvas.draw_idle()

    def _dogrula(self) -> None:
        """Validator giriş kutusunu işle ve eşleşen tohumu mavi vurgula."""
        ham = self.dogrulanacak_var.get().strip()
        if not ham:
            self._sonucu_yaz("Lütfen bir sayı girin.", "", PANEL_FG)
            return
        try:
            sayi = int(ham)
        except ValueError:
            self._sonucu_yaz("Geçersiz sayı.", "", PANEL_FG)
            return

        n = int(self.n_var.get())
        # Mevcut grafımız yoksa önce hazırla (bir fazla eleman tutuyoruz)
        if not self.fib:
            aci_rad = math.radians(float(self.aci_var.get()))
            self.fib = fibonacci_dizisi(n + 1)
            self.G = grafi_olustur(n, aci_radyan=aci_rad)

        # Yalnızca grafa karşılık gelen ilk n elemanda ara
        graf_dizi = self.fib[:n]
        sonuc, idx = dogrula_ve_index(sayi, graf_dizi)
        if sonuc == SONUC_ACCEPT and idx is not None:
            self.vurgu_indexleri.add(idx)
            f_val = graf_dizi[idx]
            # ✅ Accept: v₈ düğümü (F=21)
            ana_metin = f"✅ Accept: v{_alt_indis(idx)} düğümü (F={f_val})"
            self._sonucu_yaz(ana_metin, "", ACCEPT_RENGI)
            # Animatör çalışıyorsa renkleri güncel tut
            if self.animator is not None:
                self.animator.vurgu_kumesi = set(self.vurgu_indexleri)
                # Halihazırda görünen sahnede vurguyu hemen yansıt
                self.animator._kareyi_guncelle(self.animator.toplam - 1)
                self.canvas.draw_idle()
        else:
            # Reject — en yakın iki Fibonacci'yi indeksleriyle birlikte göster
            (alt_idx, alt_val), (ust_idx, ust_val) = en_yakin_iki_fibonacci_indeksli(
                sayi, graf_dizi
            )
            ana_metin = f"❌ Reject: {sayi} Fibonacci değil"
            yakin_parcalar = []
            if alt_idx is not None and alt_val is not None:
                yakin_parcalar.append(f"F({alt_idx})={alt_val}")
            if ust_idx is not None and ust_val is not None:
                yakin_parcalar.append(f"F({ust_idx})={ust_val}")
            alt_metin = "En yakın: " + ", ".join(yakin_parcalar) if yakin_parcalar else ""
            self._sonucu_yaz(ana_metin, alt_metin, REJECT_RENGI)

    def _sonucu_yaz(self, ana: str, alt: str, renk: str) -> None:
        """Validator sonuç ana satırı + alt satırı yazar; ana satır rengini ayarlar."""
        self.dogrulama_sonuc_var.set(ana)
        self.dogrulama_alt_var.set(alt)
        if self._dogrulama_label is not None:
            try:
                self._dogrulama_label.configure(foreground=renk)
            except tk.TclError:
                pass

    # ------------------------------------------------------------------ #
    # Zoom (mouse wheel + touchpad iki-parmak scroll)
    # ------------------------------------------------------------------ #

    def _zoom_olay(self, event) -> None:
        """İmleç merkezli zoom — yukarı scroll yakınlaştırır, aşağı uzaklaştırır."""
        ax = event.inaxes
        if ax is None or event.xdata is None or event.ydata is None:
            return

        # Her tıkta %20 — Ctrl basılıysa daha agresif (touchpad pinch için)
        olcek = 1.5 if getattr(event, "key", None) == "control" else 1.2
        if event.button == "up":
            faktor = 1.0 / olcek
        elif event.button == "down":
            faktor = olcek
        else:
            return

        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        # İmlecin görünüm içindeki oransal konumu zoom sonrası korunur
        rel_x = (event.xdata - x0) / (x1 - x0)
        rel_y = (event.ydata - y0) / (y1 - y0)

        yeni_g = (x1 - x0) * faktor
        yeni_y = (y1 - y0) * faktor
        ax.set_xlim(event.xdata - rel_x * yeni_g, event.xdata + (1 - rel_x) * yeni_g)
        ax.set_ylim(event.ydata - rel_y * yeni_y, event.ydata + (1 - rel_y) * yeni_y)
        self.canvas.draw_idle()

    def _pan_basla(self, event) -> None:
        """Sol tık basıldığında pan'i başlat — imleç altındaki noktayı çapa olarak sakla.

        Eğer tıklanan yerde bir tohum varsa pan başlatma, tohumu seç —
        seçili tohum bilgisi sağ panele yansır.
        """
        if event.button != 1 or event.inaxes is None:
            return
        if event.xdata is None or event.ydata is None:
            return

        # Tohum üstüne tıklandı mı? → seçim yap, pan başlatma
        if (
            self.animator is not None
            and self.animator._scatter is not None
        ):
            ic, info = self.animator._scatter.contains(event)
            if ic and len(info.get("ind", [])) > 0:
                idx_dizide = int(info["ind"][0])
                node = self.animator.sirali_dugumler[idx_dizide]
                # Aynı tohuma tekrar tıklanırsa seçimi kaldır (toggle)
                if self.animator.secili_index == node:
                    self.animator.secili_index = None
                else:
                    self.animator.secili_index = node
                self._secili_tohum_bilgisini_guncelle()
                # Renkleri yenile
                self.animator._kareyi_guncelle(
                    max(self.animator._son_kare, self.animator._manuel_kare)
                )
                self.canvas.draw_idle()
                return

        self._pan_anchor = (event.xdata, event.ydata)
        self._pan_ax = event.inaxes
        # Görsel geri bildirim — imleç "el sürükleme" şekline döner
        try:
            self.canvas.get_tk_widget().configure(cursor="fleur")
        except tk.TclError:
            pass

    def _pan_hareket(self, event) -> None:
        """Sol tık basılıyken görünümü çapa noktası imleç altında kalacak şekilde kaydır."""
        if self._pan_anchor is None or self._pan_ax is None:
            return
        if event.inaxes is not self._pan_ax or event.xdata is None or event.ydata is None:
            return
        # Çapa data uzayında sabit; her motion'da aynı noktanın imleç altında kalması için kaydır
        dx = self._pan_anchor[0] - event.xdata
        dy = self._pan_anchor[1] - event.ydata
        x0, x1 = self._pan_ax.get_xlim()
        y0, y1 = self._pan_ax.get_ylim()
        self._pan_ax.set_xlim(x0 + dx, x1 + dx)
        self._pan_ax.set_ylim(y0 + dy, y1 + dy)
        self.canvas.draw_idle()

    def _pan_bitir(self, event) -> None:
        """Sol tık bırakıldığında pan'i sonlandır."""
        if event.button != 1:
            return
        self._pan_anchor = None
        self._pan_ax = None
        try:
            self.canvas.get_tk_widget().configure(cursor="")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ #
    # Graf Modu
    # ------------------------------------------------------------------ #

    def _graf_modu_degistir(self) -> None:
        """Graf modunu açıp kapar — n değerine dokunmaz; sahneyi mevcut n ile yeniden çizer."""
        # Modu tersine çevir
        self.graf_modu = not self.graf_modu

        if self.graf_modu:
            # Açıldı: butonu güncelle ve "Graf Bilgisi" alt panelini görünür kıl
            self.graf_modu_btn.configure(text="🌻 Normal Moda Dön")
            self.graf_bilgisi_frame.pack(fill="x", pady=(20, 0), anchor="w")
        else:
            # Kapatıldı: butonu eski metnine getir, alt paneli gizle
            self.graf_modu_btn.configure(text="📊 Graf Modunu Aç")
            self.graf_bilgisi_frame.pack_forget()

        # Yeni mod altında sahneyi yeniden çiz (mevcut n korunur)
        self._ciz()

    # ------------------------------------------------------------------ #
    # Komşuluk Matrisi
    # ------------------------------------------------------------------ #

    def _komsuluk_matrisi_goster(self) -> None:
        """Komşuluk matrisini ayrı bir Toplevel pencerede gösterir — boyutu
        ayarlanabilir, büyük matrisler için kaydırılabilir.

        Aᵢⱼ = w(vᵢ, vⱼ) eğer (vᵢ, vⱼ) ∈ E, aksi halde 0.
        """
        if not self._grafi_garantile():
            messagebox.showinfo("Boş Graf", "Önce 'Çiz' ile grafı oluşturun.")
            return

        n_total = self.G.number_of_nodes()
        # Üst sınır 50 — daha büyük matris widget bombardımanına sebep olur
        max_boyut = min(50, n_total)
        baslangic_boyut = min(6, max_boyut)

        pencere = tk.Toplevel(self.root)
        pencere.title(f"Komşuluk Matrisi A — n={n_total}")
        pencere.configure(bg=PANEL_BG)
        pencere.geometry("760x560")

        # Üst kontrol şeridi: boyut ayarı + açıklama
        ust = ttk.Frame(pencere, style="Panel.TFrame", padding=8)
        ust.pack(fill="x")
        ttk.Label(
            ust,
            text="Aᵢⱼ = w(vᵢ, vⱼ) eğer (vᵢ, vⱼ) ∈ E, aksi halde 0",
            style="Panel.TLabel",
        ).pack(side="left")

        boyut_var = tk.IntVar(value=baslangic_boyut)
        ttk.Label(ust, text="Boyut:", style="Panel.TLabel").pack(side="left", padx=(20, 4))
        boyut_spin = tk.Spinbox(
            ust,
            from_=2,
            to=max_boyut,
            width=5,
            textvariable=boyut_var,
            bg="#2a2a2a",
            fg=PANEL_FG,
            insertbackground=PANEL_FG,
            buttonbackground=PANEL_BG,
        )
        boyut_spin.pack(side="left")
        ttk.Label(ust, text=f"× (boyut+1) — max {max_boyut}", style="Yardim.TLabel").pack(side="left", padx=4)

        # Kaydırılabilir alan — Canvas + Scrollbar + Frame klasik tkinter pattern
        cerceve = ttk.Frame(pencere, style="Panel.TFrame")
        cerceve.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        canvas = tk.Canvas(cerceve, bg=PANEL_BG, highlightthickness=0)
        v_scroll = ttk.Scrollbar(cerceve, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(cerceve, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        cerceve.rowconfigure(0, weight=1)
        cerceve.columnconfigure(0, weight=1)

        tablo = ttk.Frame(canvas, style="Panel.TFrame", padding=4)
        tablo_id = canvas.create_window((0, 0), window=tablo, anchor="nw")

        def _scroll_alanini_guncelle(_=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        tablo.bind("<Configure>", _scroll_alanini_guncelle)

        def _tabloyu_yeniden_kur(*_):
            # Mevcut hücreleri temizle
            for child in tablo.winfo_children():
                child.destroy()

            try:
                boyut = int(boyut_var.get())
            except (ValueError, tk.TclError):
                boyut = baslangic_boyut
            boyut = max(2, min(max_boyut, boyut))

            satir_sayisi = boyut
            sutun_sayisi = min(boyut + 1, n_total)
            pencere.title(f"Komşuluk Matrisi A ({satir_sayisi}×{sutun_sayisi}) — n={n_total}")

            hucre_genisligi = 10
            ttk.Label(
                tablo, text="A", style="Baslik.TLabel",
                width=hucre_genisligi, anchor="center",
            ).grid(row=0, column=0, padx=2, pady=2)
            for j in range(sutun_sayisi):
                ttk.Label(
                    tablo, text=f"v{_alt_indis(j)}",
                    style="Baslik.TLabel",
                    width=hucre_genisligi, anchor="center",
                ).grid(row=0, column=j + 1, padx=2, pady=2)

            for i in range(satir_sayisi):
                ttk.Label(
                    tablo, text=f"v{_alt_indis(i)}",
                    style="Baslik.TLabel",
                    width=hucre_genisligi, anchor="center",
                ).grid(row=i + 1, column=0, padx=2, pady=2)
                for j in range(sutun_sayisi):
                    if self.G.has_edge(i, j):
                        if i == 0 and j == 1:
                            metin = "—"
                        else:
                            w = float(self.G[i][j].get("agirlik", 0.0))
                            metin = f"{w:.4f}"
                    else:
                        metin = "0"
                    ttk.Label(
                        tablo, text=metin,
                        style="Bilgi.TLabel",
                        width=hucre_genisligi, anchor="center",
                    ).grid(row=i + 1, column=j + 1, padx=2, pady=2)

            tablo.update_idletasks()
            _scroll_alanini_guncelle()

        ttk.Button(
            ust, text="Yenile", style="Panel.TButton",
            command=_tabloyu_yeniden_kur,
        ).pack(side="left", padx=(8, 0))

        # Spinbox değişiminde de otomatik yenile (ok tıklamaları)
        boyut_var.trace_add("write", lambda *_: _tabloyu_yeniden_kur())

        _tabloyu_yeniden_kur()

    def _secili_tohum_bilgisini_guncelle(self) -> None:
        """Seçili tohum (mor) için sağ paneldeki Vogel detaylarını yazar."""
        if self.animator is None or self.animator.secili_index is None:
            self.secili_index_var.set("—")
            self.secili_fib_var.set("—")
            self.secili_aci_var.set("—")
            self.secili_yaricap_var.set("—")
            self.secili_konum_var.set("—")
            return

        idx = self.animator.secili_index
        # Vogel parametreleri — slider'daki açı kullanılır (varsayılan altın açı)
        aci_derece = float(self.aci_var.get())
        # i·α mod 360° — tohumun çevresel konumu (her zaman 0-360 arası)
        toplam_aci = (idx * aci_derece) % 360.0

        from positioning import OLCEK_C  # döngüsel import değil, modül seviyesinde sabit
        yaricap = OLCEK_C * math.sqrt(idx)

        x = self.animator.konumlar[idx][0]
        y = self.animator.konumlar[idx][1]

        f_val = (
            self.G.nodes[idx].get("fibonacci", "—")
            if self.G is not None and idx in self.G.nodes
            else "—"
        )
        f_metni = formatla_buyuk_sayi(f_val) if isinstance(f_val, int) else str(f_val)

        self.secili_index_var.set(str(idx))
        self.secili_fib_var.set(f_metni)
        self.secili_aci_var.set(f"{toplam_aci:.2f}°")
        self.secili_yaricap_var.set(f"{yaricap:.3f}")
        self.secili_konum_var.set(f"({x:.2f}, {y:.2f})")

    def _yakinsama_grafigini_goster(self) -> None:
        """F(i+1)/F(i) → φ yakınsamasını ayrı bir pencerede çizer."""
        n = int(self.n_var.get())
        # En az birkaç eleman yakınsamayı görmek için yeterli — fib yoksa üret
        if not self.fib or len(self.fib) < n + 1:
            self.fib = fibonacci_dizisi(n + 1)
        yakinsama_penceresi_ac(self.root, self.fib)

    def _traversal_goster(self) -> None:
        """BFS/DFS gezinti penceresini açar."""
        if not self._grafi_garantile():
            messagebox.showinfo("Boş Graf", "Önce 'Çiz' ile grafı oluşturun.")
            return
        traversal_penceresi_ac(self.root, self.G)

    def _dijkstra_goster(self) -> None:
        """Dijkstra en kısa yol penceresini açar."""
        if not self._grafi_garantile():
            messagebox.showinfo("Boş Graf", "Önce 'Çiz' ile grafı oluşturun.")
            return
        from dijkstra_window import dijkstra_penceresi_ac
        dijkstra_penceresi_ac(self.root, self.G)

    def _graf_bilgisini_guncelle(self) -> None:
        """Sağ paneldeki Graf Bilgisi etiketlerini grafın istatistikleriyle doldurur."""
        if self.G is None:
            return
        n = self.G.number_of_nodes()
        e = self.G.number_of_edges()

        # Ağırlıkları topla; F(0)=0 sentinel'i (0.0) istatistiklere katma
        agirliklar = [
            float(d.get("agirlik", 0.0))
            for _, _, d in self.G.edges(data=True)
            if float(d.get("agirlik", 0.0)) > 0
        ]

        if agirliklar:
            mn = min(agirliklar)
            mx = max(agirliklar)
            ort = sum(agirliklar) / len(agirliklar)
            self.graf_min_var.set(f"Min ağırlık: {mn:.3f}")
            self.graf_max_var.set(f"Max ağırlık: {mx:.3f}")
            self.graf_avg_var.set(f"Ort ağırlık: {ort:.3f}")
        else:
            self.graf_min_var.set("Min ağırlık: —")
            self.graf_max_var.set("Max ağırlık: —")
            self.graf_avg_var.set("Ort ağırlık: —")

        self.graf_dugum_var.set(f"Düğüm sayısı: {n}")
        self.graf_kenar_var.set(f"Kenar sayısı: {e}")
        self.graf_yon_var.set("Yön: vᵢ → vᵢ₊₁")

    # ------------------------------------------------------------------ #
    # Animator → GUI geri çağırma
    # ------------------------------------------------------------------ #

    def _adim_bilgisini_guncelle(self, kare_no: int) -> None:
        """SpiralAnimator her adımda bu fonksiyonu çağırır."""
        if not self.fib:
            return

        i = kare_no
        # adim_geri boş sahneye dönerse kare_no = -1 gelir — paneli sıfırla
        if i < 0:
            self.bilgi_tohum_no.set("—")
            self.bilgi_fib.set("—")
            self.bilgi_oran.set("—")
            self.bilgi_phi_farki.set("—")
            self.bilgi_aktif_kenar.set("—")
            self.bilgi_aktif_agirlik.set("—")
            return

        self.bilgi_tohum_no.set(str(i))
        # F(i) — büyük sayılar bilimsel notasyonla 12 karakteri aşmasın
        if 0 <= i < len(self.fib):
            self.bilgi_fib.set(formatla_buyuk_sayi(self.fib[i]))
        else:
            self.bilgi_fib.set("—")

        # F(i+1)/F(i) — i = 0 olduğunda F(0)=0 olduğu için bölme yapılmaz.
        # i >= 1 için her karede güncelle; gerekirse F(i+1)'i anlık hesapla.
        if i >= 1:
            f_i = self.fib[i] if i < len(self.fib) else None
            if (i + 1) < len(self.fib):
                f_iplus1 = self.fib[i + 1]
            else:
                # Son tohumda dizide bir sonraki yoksa anlık üret
                f_iplus1 = fibonacci_n(i + 1)
            if f_i is not None and f_i != 0:
                oran, fark = oran_ve_fark(f_i, f_iplus1)
                self.bilgi_oran.set(f"{oran:.10f}")
                self.bilgi_phi_farki.set(f"{fark:.2e}")
            else:
                self.bilgi_oran.set("—")
                self.bilgi_phi_farki.set("—")
        else:
            # i = 0 için bölme tanımsız — kullanıcıya net bir gösterge ver
            self.bilgi_oran.set("—")
            self.bilgi_phi_farki.set("—")

        # Aktif kenar = (i-1) → i  (i. tohum yerleştiğinde tamamlanan kenar)
        if i >= 1 and self.G is not None and self.G.has_edge(i - 1, i):
            kenar_metni = f"v{_alt_indis(i - 1)} → v{_alt_indis(i)}"
            w = float(self.G[i - 1][i].get("agirlik", 0.0))
            agirlik_metni = "—" if w == 0.0 else f"{w:.4f}"
            self.bilgi_aktif_kenar.set(kenar_metni)
            self.bilgi_aktif_agirlik.set(agirlik_metni)
        else:
            self.bilgi_aktif_kenar.set("—")
            self.bilgi_aktif_agirlik.set("—")


def uygulamayi_baslat() -> None:
    """Tkinter ana döngüsünü başlatan kolay erişim fonksiyonu."""
    root = tk.Tk()
    AyCicegiGUI(root)
    root.mainloop()


if __name__ == "__main__":
    uygulamayi_baslat()
