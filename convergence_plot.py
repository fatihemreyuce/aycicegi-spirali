"""
convergence_plot.py
-------------------
Fibonacci ardışık oranlarının altın orana yakınsamasını grafikler.

İki eğri:
    1. F(i+1)/F(i)  ile φ — doğrusal eksen
    2. |F(i+1)/F(i) − φ|  — log skala (yakınsamanın üstel hızı görünür)
"""

import tkinter as tk
from typing import List

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utils import PHI, ardisik_oran, phi_farki


PANEL_BG = "#1b1b1b"
EKSEN_BG = "#0b3d2e"
CIZGI_RENGI_ORAN = "#ffd400"   # Sarı — F(i+1)/F(i)
CIZGI_RENGI_PHI = "#5cff7a"    # Yeşil — φ referansı
CIZGI_RENGI_FARK = "#ff7070"   # Kırmızımsı — |oran - φ|


def yakinsama_penceresi_ac(parent: tk.Misc, fib: List[int]) -> None:
    """
    Yeni bir Toplevel penceresinde iki alt-grafik çizer:
        - Üstte: F(i+1)/F(i) ve φ referans çizgisi
        - Altta: |F(i+1)/F(i) − φ|  (log y ekseni)

    Parametreler:
        parent : Üst pencere (genellikle ana Tk root).
        fib    : İlk en az 3 elemanı içeren Fibonacci listesi.
    """
    pencere = tk.Toplevel(parent)
    pencere.title("Yakınsama Grafiği — F(i+1)/F(i) → φ")
    pencere.configure(bg=PANEL_BG)
    pencere.geometry("720x520")

    # F(0)=0 olduğu için i=1'den başlat — F(1)/F(0) tanımsız
    indeksler: List[int] = []
    oranlar: List[float] = []
    farklar: List[float] = []
    for i in range(1, len(fib) - 1):
        f_i = fib[i]
        f_iplus1 = fib[i + 1]
        if f_i == 0:
            continue
        oran = ardisik_oran(f_i, f_iplus1)
        fark = phi_farki(oran)
        indeksler.append(i)
        oranlar.append(oran)
        # Log skalada 0 görünmez — minik epsilon ile koru
        farklar.append(fark if fark > 0 else 1e-20)

    fig = Figure(figsize=(7, 5), facecolor=PANEL_BG)

    # Üst grafik: oran ve φ
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_facecolor(EKSEN_BG)
    ax1.plot(indeksler, oranlar, color=CIZGI_RENGI_ORAN, linewidth=1.5,
             marker="o", markersize=3, label="F(i+1)/F(i)")
    ax1.axhline(PHI, color=CIZGI_RENGI_PHI, linestyle="--", linewidth=1.0,
                label=f"φ ≈ {PHI:.10f}")
    ax1.set_ylabel("Oran", color="#f0f0f0")
    ax1.tick_params(colors="#f0f0f0")
    for sk in ax1.spines.values():
        sk.set_color("#888888")
    ax1.legend(facecolor=PANEL_BG, edgecolor="#888888", labelcolor="#f0f0f0",
               loc="lower right", fontsize=9)
    ax1.set_title("Ardışık Fibonacci Oranlarının Altın Orana Yakınsaması",
                  color="#ffd400", fontsize=11)

    # Alt grafik: |oran - φ|, log skala
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.set_facecolor(EKSEN_BG)
    ax2.semilogy(indeksler, farklar, color=CIZGI_RENGI_FARK, linewidth=1.5,
                 marker="s", markersize=3, label="|F(i+1)/F(i) − φ|")
    ax2.set_xlabel("i", color="#f0f0f0")
    ax2.set_ylabel("|fark|  (log)", color="#f0f0f0")
    ax2.tick_params(colors="#f0f0f0")
    for sk in ax2.spines.values():
        sk.set_color("#888888")
    ax2.grid(True, which="both", color="#444444", linewidth=0.4, alpha=0.6)
    ax2.legend(facecolor=PANEL_BG, edgecolor="#888888", labelcolor="#f0f0f0",
               loc="upper right", fontsize=9)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    canvas.draw()


if __name__ == "__main__":
    from fibonacci import fibonacci_dizisi
    root = tk.Tk()
    root.withdraw()
    yakinsama_penceresi_ac(root, fibonacci_dizisi(40))
    root.mainloop()
