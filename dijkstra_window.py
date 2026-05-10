"""
dijkstra_window.py
------------------
İki tohum arası en kısa yolu Dijkstra ile hesaplar ve görselleştirir.

Spiral grafı yönlü ve doğrusal (v_i → v_{i+1}); dolayısıyla kaynak < hedef
olmalıdır, aksi halde yol yoktur. Daha zengin bir örnek için kullanıcı
*Delaunay komşuluk grafını* (kenar ağırlığı = Öklid mesafesi) seçebilir.
"""

import math
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx

from utils import mesafe


PANEL_BG = "#1b1b1b"
PANEL_FG = "#f0f0f0"
EKSEN_BG = "#0b3d2e"

RENK_TOHUM = "#7d7d7d"
RENK_KAYNAK = "#1f8bff"
RENK_HEDEF = "#ff7070"
RENK_YOL = "#ffd400"
RENK_KENAR_YOL = "#ff3b3b"


def _delaunay_grafi_agirlikli(konumlar: dict) -> nx.Graph:
    """Delaunay komşuluğundan, kenar ağırlığı Öklid mesafesi olan graf üretir."""
    from scipy.spatial import Delaunay

    sirali = sorted(konumlar.keys())
    pts = [konumlar[i] for i in sirali]
    if len(pts) < 3:
        return nx.Graph()
    tri = Delaunay(pts)
    G = nx.Graph()
    G.add_nodes_from(sirali)
    eklenen = set()
    for simplex in tri.simplices:
        a, b, c = sirali[int(simplex[0])], sirali[int(simplex[1])], sirali[int(simplex[2])]
        for u, v in ((a, b), (b, c), (c, a)):
            anahtar = (u, v) if u < v else (v, u)
            if anahtar in eklenen:
                continue
            eklenen.add(anahtar)
            d = mesafe(konumlar[u], konumlar[v])
            G.add_edge(u, v, agirlik=d)
    return G


def dijkstra_penceresi_ac(parent: tk.Misc, G_spiral: nx.DiGraph) -> None:
    """Dijkstra en kısa yol görselleştirme penceresi."""
    if G_spiral is None or G_spiral.number_of_nodes() < 2:
        return

    pencere = tk.Toplevel(parent)
    pencere.title("En Kısa Yol — Dijkstra")
    pencere.configure(bg=PANEL_BG)
    pencere.geometry("840x680")

    konumlar = {n: (d.get("x", 0.0), d.get("y", 0.0)) for n, d in G_spiral.nodes(data=True)}
    sirali = sorted(konumlar.keys())
    n_total = len(sirali)

    ust = ttk.Frame(pencere, style="Panel.TFrame", padding=8)
    ust.pack(fill="x")

    kaynak_var = tk.IntVar(value=0)
    hedef_var = tk.IntVar(value=min(n_total - 1, 50))
    graf_secim_var = tk.StringVar(value="Spiral")

    ttk.Label(ust, text="Kaynak (i):", style="Panel.TLabel").pack(side="left")
    tk.Spinbox(
        ust, from_=0, to=n_total - 1, textvariable=kaynak_var, width=6,
        bg="#2a2a2a", fg=PANEL_FG, insertbackground=PANEL_FG,
        buttonbackground=PANEL_BG,
    ).pack(side="left", padx=(2, 12))

    ttk.Label(ust, text="Hedef (j):", style="Panel.TLabel").pack(side="left")
    tk.Spinbox(
        ust, from_=0, to=n_total - 1, textvariable=hedef_var, width=6,
        bg="#2a2a2a", fg=PANEL_FG, insertbackground=PANEL_FG,
        buttonbackground=PANEL_BG,
    ).pack(side="left", padx=(2, 12))

    ttk.Label(ust, text="Graf:", style="Panel.TLabel").pack(side="left")
    ttk.Combobox(
        ust, textvariable=graf_secim_var,
        values=["Spiral", "Delaunay"], width=10, state="readonly",
    ).pack(side="left", padx=(2, 12))

    durum_var = tk.StringVar(value="Hazır")
    ttk.Label(ust, textvariable=durum_var, style="Panel.TLabel").pack(side="right")

    fig = Figure(figsize=(8, 6), facecolor=PANEL_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(EKSEN_BG)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

    xs = [konumlar[i][0] for i in sirali]
    ys = [konumlar[i][1] for i in sirali]

    def _hesapla() -> None:
        ax.clear()
        ax.set_facecolor(EKSEN_BG)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")

        try:
            kaynak = int(kaynak_var.get())
            hedef = int(hedef_var.get())
        except (ValueError, tk.TclError):
            durum_var.set("Geçersiz indeks")
            return
        kaynak = max(0, min(n_total - 1, kaynak))
        hedef = max(0, min(n_total - 1, hedef))

        graf_tipi = graf_secim_var.get()
        if graf_tipi == "Delaunay":
            try:
                G_used = _delaunay_grafi_agirlikli(konumlar)
            except ImportError:
                durum_var.set("scipy gerekli — pip install scipy")
                return
            agirlik_anahtar = "agirlik"
        else:
            G_used = G_spiral
            agirlik_anahtar = "agirlik"

        # Tüm tohumları gri çiz; sonra yolu üzerine bas
        ax.scatter(xs, ys, s=30, c=RENK_TOHUM, edgecolors="black",
                   linewidths=0.2, zorder=2)

        try:
            yol = nx.dijkstra_path(G_used, kaynak, hedef, weight=agirlik_anahtar)
            uzunluk = nx.dijkstra_path_length(G_used, kaynak, hedef, weight=agirlik_anahtar)
        except nx.NetworkXNoPath:
            durum_var.set(f"{kaynak} → {hedef}: yol yok (yönlü graf?)")
            canvas.draw_idle()
            return
        except nx.NodeNotFound:
            durum_var.set("Düğüm bulunamadı")
            canvas.draw_idle()
            return

        # Yol kenarları kırmızı kalın çizgi
        for u, v in zip(yol[:-1], yol[1:]):
            x0, y0 = konumlar[u]
            x1, y1 = konumlar[v]
            ax.plot([x0, x1], [y0, y1], color=RENK_KENAR_YOL,
                    linewidth=2.0, alpha=0.95, zorder=3)

        # Yol düğümleri sarı
        yol_xs = [konumlar[i][0] for i in yol]
        yol_ys = [konumlar[i][1] for i in yol]
        ax.scatter(yol_xs, yol_ys, s=50, c=RENK_YOL, edgecolors="black",
                   linewidths=0.4, zorder=4)

        # Kaynak ve hedef ayrı renk
        ax.scatter([konumlar[kaynak][0]], [konumlar[kaynak][1]],
                   s=120, c=RENK_KAYNAK, edgecolors="white",
                   linewidths=1.5, zorder=5)
        ax.scatter([konumlar[hedef][0]], [konumlar[hedef][1]],
                   s=120, c=RENK_HEDEF, edgecolors="white",
                   linewidths=1.5, zorder=5)

        durum_var.set(
            f"{graf_tipi}: {kaynak} → {hedef}  |  {len(yol) - 1} kenar  |  "
            f"toplam ağırlık: {uzunluk:.4f}"
        )
        canvas.draw_idle()

    ttk.Button(ust, text="Hesapla", style="Panel.TButton",
               command=_hesapla).pack(side="left", padx=(6, 0))

    _hesapla()
