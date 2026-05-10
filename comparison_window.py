"""
comparison_window.py
--------------------
İki farklı açıyla üretilen spiralleri yan yana karşılaştırır.

Eğitsel motivasyon: ayçiçeğindeki sıkı paketleme yalnızca *altın açıda*
ortaya çıkar. 90° / 60° / 137.0° gibi rasyonel/yakın açılarda tohumlar
hizalanıp ışınsal "boşluklar" oluşturur. Bu pencerede iki açı yan yana
çizilerek farkın görsel olarak somut hale gelmesi amaçlanır.
"""

import math
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from positioning import tum_konumlar, OLCEK_C
from utils import ALTIN_ACI_DERECE


PANEL_BG = "#1b1b1b"
PANEL_FG = "#f0f0f0"
EKSEN_BG = "#0b3d2e"
TOHUM_RENGI = "#ffd400"
ACCENT = "#ffd400"


def karsilastirma_penceresi_ac(parent: tk.Misc) -> None:
    """İki açıyı yan yana karşılaştırma penceresi açar."""
    pencere = tk.Toplevel(parent)
    pencere.title("Açı Karşılaştırma — Altın Açı vs Diğeri")
    pencere.configure(bg=PANEL_BG)
    pencere.geometry("1100x620")

    # Üst kontrol şeridi: iki açı entry + n + preset butonlar + Çiz
    ust = ttk.Frame(pencere, style="Panel.TFrame", padding=8)
    ust.pack(fill="x")

    aci_a_var = tk.DoubleVar(value=ALTIN_ACI_DERECE)
    aci_b_var = tk.DoubleVar(value=90.0)
    n_var = tk.IntVar(value=300)

    ttk.Label(ust, text="Sol açı (°):", style="Panel.TLabel").pack(side="left")
    ttk.Entry(ust, textvariable=aci_a_var, width=10, style="Panel.TEntry").pack(side="left", padx=(2, 12))
    ttk.Label(ust, text="Sağ açı (°):", style="Panel.TLabel").pack(side="left")
    ttk.Entry(ust, textvariable=aci_b_var, width=10, style="Panel.TEntry").pack(side="left", padx=(2, 12))
    ttk.Label(ust, text="n:", style="Panel.TLabel").pack(side="left")
    ttk.Entry(ust, textvariable=n_var, width=6, style="Panel.TEntry").pack(side="left", padx=(2, 12))

    # Preset hızlı butonlar — sık kullanılan kıyaslamalar
    def _preset(a: float, b: float):
        aci_a_var.set(a)
        aci_b_var.set(b)
        _ciz()

    ttk.Button(ust, text="137.5° vs 90°", style="Panel.TButton",
               command=lambda: _preset(ALTIN_ACI_DERECE, 90.0)).pack(side="left", padx=2)
    ttk.Button(ust, text="137.5° vs 137.0°", style="Panel.TButton",
               command=lambda: _preset(ALTIN_ACI_DERECE, 137.0)).pack(side="left", padx=2)
    ttk.Button(ust, text="137.5° vs 60°", style="Panel.TButton",
               command=lambda: _preset(ALTIN_ACI_DERECE, 60.0)).pack(side="left", padx=2)

    # İki canvas yan yana
    fig = Figure(figsize=(10, 5), facecolor=PANEL_BG)
    ax_a = fig.add_subplot(1, 2, 1)
    ax_b = fig.add_subplot(1, 2, 2)

    for ax in (ax_a, ax_b):
        ax.set_facecolor(EKSEN_BG)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _spirali_ciz_axes(ax, aci_derece: float, n: int, baslik: str) -> None:
        ax.clear()
        ax.set_facecolor(EKSEN_BG)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        if n <= 0:
            return
        konumlar = tum_konumlar(n, aci_radyan=math.radians(aci_derece))
        xs = [p[0] for p in konumlar]
        ys = [p[1] for p in konumlar]
        ax.scatter(xs, ys, s=20, c=TOHUM_RENGI, edgecolors="black", linewidths=0.2)
        ax.set_title(baslik, color=ACCENT, fontsize=11)

    def _ciz() -> None:
        try:
            n = max(1, min(5000, int(n_var.get())))
            a = float(aci_a_var.get())
            b = float(aci_b_var.get())
        except (ValueError, tk.TclError):
            return
        _spirali_ciz_axes(ax_a, a, n, f"α = {a:.4f}°")
        _spirali_ciz_axes(ax_b, b, n, f"α = {b:.4f}°")
        fig.tight_layout()
        canvas.draw_idle()

    ttk.Button(ust, text="Çiz", style="Panel.TButton", command=_ciz).pack(side="left", padx=(12, 0))

    # İlk çizim
    _ciz()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    karsilastirma_penceresi_ac(root)
    root.mainloop()
