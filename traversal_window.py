"""
traversal_window.py
-------------------
BFS / DFS gezintisi animasyonu — ayrı bir Toplevel pencerede.

Spiral grafı doğrusal olduğundan BFS = DFS = [0..n-1] olur. Eğitsel olarak
gerçek BFS/DFS davranışını görmek için *Delaunay komşuluk grafı* da
seçilebilir (scipy gerektirir). Delaunay'da BFS dalgalar halinde dışa
yayılırken DFS bir spiral kolu sonuna kadar takip eder.
"""

import math
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx

from graph_traversal import bfs_sirasi, dfs_sirasi


PANEL_BG = "#1b1b1b"
PANEL_FG = "#f0f0f0"
EKSEN_BG = "#0b3d2e"

RENK_ZIYARET = "#5cff7a"
RENK_AKTIF = "#ff3b3b"
RENK_BEKLEME = "#7d7d7d"
RENK_KOK = "#1f8bff"


def _delaunay_grafi(konumlar) -> nx.Graph:
    """Verilen konumlardan Delaunay komşuluk grafı üretir (scipy gerektirir)."""
    from scipy.spatial import Delaunay

    pts = list(konumlar)
    if len(pts) < 3:
        return nx.Graph()
    tri = Delaunay(pts)
    G = nx.Graph()
    G.add_nodes_from(range(len(pts)))
    for simplex in tri.simplices:
        a, b, c = int(simplex[0]), int(simplex[1]), int(simplex[2])
        G.add_edge(a, b)
        G.add_edge(b, c)
        G.add_edge(c, a)
    return G


def traversal_penceresi_ac(parent: tk.Misc, G_spiral: nx.DiGraph) -> None:
    """BFS/DFS gezintisini animasyonlu gösteren Toplevel."""
    if G_spiral is None or G_spiral.number_of_nodes() < 2:
        return

    pencere = tk.Toplevel(parent)
    pencere.title("Graf Gezintisi — BFS / DFS")
    pencere.configure(bg=PANEL_BG)
    pencere.geometry("840x680")

    # Konumları sözlük olarak topla
    konumlar = {n: (d.get("x", 0.0), d.get("y", 0.0)) for n, d in G_spiral.nodes(data=True)}
    sirali = sorted(konumlar.keys())

    # Üst kontrol — algoritma + graf seçimi + kök + hız + Başlat
    ust = ttk.Frame(pencere, style="Panel.TFrame", padding=8)
    ust.pack(fill="x")

    algo_var = tk.StringVar(value="BFS")
    graf_secim_var = tk.StringVar(value="Spiral")
    kok_var = tk.IntVar(value=0)
    hiz_var = tk.IntVar(value=80)  # ms

    ttk.Label(ust, text="Algoritma:", style="Panel.TLabel").pack(side="left")
    ttk.Combobox(
        ust, textvariable=algo_var, values=["BFS", "DFS"],
        width=6, state="readonly",
    ).pack(side="left", padx=(2, 12))

    ttk.Label(ust, text="Graf:", style="Panel.TLabel").pack(side="left")
    ttk.Combobox(
        ust, textvariable=graf_secim_var,
        values=["Spiral", "Delaunay"], width=10, state="readonly",
    ).pack(side="left", padx=(2, 12))

    ttk.Label(ust, text="Kök (i):", style="Panel.TLabel").pack(side="left")
    n_total = len(sirali)
    tk.Spinbox(
        ust, from_=0, to=n_total - 1, textvariable=kok_var, width=6,
        bg="#2a2a2a", fg=PANEL_FG, insertbackground=PANEL_FG,
        buttonbackground=PANEL_BG,
    ).pack(side="left", padx=(2, 12))

    ttk.Label(ust, text="Hız (ms):", style="Panel.TLabel").pack(side="left")
    ttk.Entry(ust, textvariable=hiz_var, width=6, style="Panel.TEntry").pack(side="left", padx=(2, 12))

    durum_var = tk.StringVar(value="Hazır")
    ttk.Label(ust, textvariable=durum_var, style="Panel.TLabel").pack(side="right")

    # Canvas
    fig = Figure(figsize=(8, 6), facecolor=PANEL_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(EKSEN_BG)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

    xs = [konumlar[i][0] for i in sirali]
    ys = [konumlar[i][1] for i in sirali]
    scatter = ax.scatter(
        xs, ys, s=40, c=[RENK_BEKLEME] * n_total,
        edgecolors="black", linewidths=0.3, zorder=2,
    )

    # Animasyon kontrolü için referanslar
    durum = {"sira": [], "k": 0, "after_id": None}

    def _renkleri_uygula(k: int) -> None:
        renkler = [RENK_BEKLEME] * n_total
        sira_listesi = durum["sira"]
        # k arası ziyaret edilmiş
        for j in range(k):
            n_id = sira_listesi[j]
            try:
                idx = sirali.index(n_id)
            except ValueError:
                continue
            renkler[idx] = RENK_ZIYARET
        # k. düğüm aktif (bu adımda yerleşen)
        if 0 <= k < len(sira_listesi):
            n_id = sira_listesi[k]
            try:
                idx = sirali.index(n_id)
                renkler[idx] = RENK_AKTIF
            except ValueError:
                pass
        # Kök her zaman mavi (ziyaret renginin üzerine yazma — kök'ün kendisi
        # zaten ziyaret listesinde ama görsel olarak kök ayrılsın)
        if sira_listesi:
            try:
                kok_idx = sirali.index(sira_listesi[0])
                if k > 0:  # animasyon başladıktan sonra kök sabit mavi
                    renkler[kok_idx] = RENK_KOK
            except ValueError:
                pass
        scatter.set_color(renkler)
        canvas.draw_idle()

    def _adim() -> None:
        k = durum["k"]
        if k >= len(durum["sira"]):
            durum_var.set(f"Bitti — {len(durum['sira'])} düğüm ziyaret edildi")
            durum["after_id"] = None
            return
        _renkleri_uygula(k)
        durum["k"] = k + 1
        try:
            ms = max(1, int(hiz_var.get()))
        except (ValueError, tk.TclError):
            ms = 80
        durum["after_id"] = pencere.after(ms, _adim)

    def _baslat() -> None:
        # Önceki animasyonu kes
        if durum["after_id"] is not None:
            pencere.after_cancel(durum["after_id"])
            durum["after_id"] = None

        algo = algo_var.get()
        graf_tipi = graf_secim_var.get()
        try:
            kok = int(kok_var.get())
        except (ValueError, tk.TclError):
            kok = 0
        kok = max(0, min(n_total - 1, kok))

        if graf_tipi == "Delaunay":
            try:
                G_used = _delaunay_grafi([konumlar[i] for i in sirali])
            except ImportError:
                durum_var.set("scipy gerekli — pip install scipy")
                return
        else:
            G_used = G_spiral

        sira = bfs_sirasi(G_used, kok) if algo == "BFS" else dfs_sirasi(G_used, kok)
        durum["sira"] = sira
        durum["k"] = 0
        durum_var.set(f"{algo} ({graf_tipi}) — {len(sira)} düğüm")
        _adim()

    def _sifirla() -> None:
        if durum["after_id"] is not None:
            pencere.after_cancel(durum["after_id"])
            durum["after_id"] = None
        durum["sira"] = []
        durum["k"] = 0
        scatter.set_color([RENK_BEKLEME] * n_total)
        canvas.draw_idle()
        durum_var.set("Hazır")

    btn_satiri = ttk.Frame(ust, style="Panel.TFrame")
    btn_satiri.pack(side="left", padx=(0, 6))
    ttk.Button(btn_satiri, text="▶ Başlat", style="Panel.TButton",
               command=_baslat).pack(side="left", padx=2)
    ttk.Button(btn_satiri, text="↺ Sıfırla", style="Panel.TButton",
               command=_sifirla).pack(side="left", padx=2)

    # Pencere kapanırken zamanlayıcıyı temizle
    def _on_close():
        if durum["after_id"] is not None:
            pencere.after_cancel(durum["after_id"])
        pencere.destroy()
    pencere.protocol("WM_DELETE_WINDOW", _on_close)
