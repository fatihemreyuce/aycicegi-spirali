"""
ui.windows.adjacency_matrix
---------------------------
Komşuluk matrisi A — Aᵢⱼ = w(vᵢ, vⱼ) eğer (vᵢ, vⱼ) ∈ E, aksi halde 0.

Boyut ayarlanabilir (2 — 50). QTableWidget built-in scrollbar'larla
büyük matrisleri rahat gösterir.
"""

import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from graph_builder import grafi_olustur
from ui import theme
from ui.windows.base import AnalyticsWindow


class KomsulukMatrisiPenceresi(AnalyticsWindow):
    BASLIK = "Komşuluk Matrisi A"

    def __init__(self, mevcut_n: int = 100, aci_derece: float = 137.5077) -> None:
        super().__init__()
        self._n_total = max(int(mevcut_n), 2)
        self._aci_derece = float(aci_derece)
        self.resize(760, 560)

        # Grafı bir kez oluştur
        self._G = grafi_olustur(self._n_total, aci_radyan=math.radians(self._aci_derece))

        max_boyut = min(50, self._n_total)
        baslangic_boyut = min(6, max_boyut)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 8, 8, 8)
        duzen.setSpacing(6)

        # Üst toolbar
        ust = QHBoxLayout()
        ust.addWidget(QLabel("Aᵢⱼ = w(vᵢ, vⱼ) eğer (vᵢ, vⱼ) ∈ E, aksi halde 0"))
        ust.addStretch(1)

        ust.addWidget(QLabel("Boyut:"))
        self.boyut_kutu = QSpinBox()
        self.boyut_kutu.setRange(2, max_boyut)
        self.boyut_kutu.setValue(baslangic_boyut)
        self.boyut_kutu.setFixedWidth(80)
        ust.addWidget(self.boyut_kutu)

        ust.addWidget(QLabel(f"× (boyut+1) — max {max_boyut}"))

        self.yenile_butonu = QPushButton("Yenile")
        self.yenile_butonu.setProperty("primary", True)
        self.yenile_butonu.clicked.connect(self._tabloyu_kur)
        ust.addWidget(self.yenile_butonu)

        duzen.addLayout(ust)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tablo.horizontalHeader().setStretchLastSection(False)
        duzen.addWidget(self.tablo)

        # Spinbox değişiminde de otomatik yenile
        self.boyut_kutu.valueChanged.connect(lambda _: self._tabloyu_kur())

        self._tabloyu_kur()

    def _tabloyu_kur(self) -> None:
        boyut = self.boyut_kutu.value()
        satir_sayisi = boyut
        sutun_sayisi = min(boyut + 1, self._n_total)

        self.setWindowTitle(
            f"Komşuluk Matrisi A ({satir_sayisi}×{sutun_sayisi}) — n={self._n_total}"
        )

        self.tablo.clear()
        self.tablo.setRowCount(satir_sayisi)
        self.tablo.setColumnCount(sutun_sayisi)

        # Header'lar
        self.tablo.setHorizontalHeaderLabels([f"v{j}" for j in range(sutun_sayisi)])
        self.tablo.setVerticalHeaderLabels([f"v{i}" for i in range(satir_sayisi)])

        # Hücreler
        for i in range(satir_sayisi):
            for j in range(sutun_sayisi):
                if self._G.has_edge(i, j):
                    if i == 0 and j == 1:
                        # F(0)=0, F(1)/F(0) tanımsız → eski Tk gibi "—"
                        metin = "—"
                    else:
                        w = float(self._G[i][j].get("agirlik", 0.0))
                        metin = f"{w:.4f}"
                else:
                    metin = "0"
                item = QTableWidgetItem(metin)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tablo.setItem(i, j, item)

        self.tablo.resizeColumnsToContents()
