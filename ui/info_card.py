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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

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
