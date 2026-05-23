"""
ui.windows.seed_select
----------------------
Tohum indeksi seçimi. Geçerli bir indeks girilince ana SpiralCanvas'ta
mor vurgu eklenir ve pencerede tohum detayları gösterilir:
i, F(i), açı (i·α mod 360°), yarıçap, konum (x, y).
"""

import math

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from fibonacci import fibonacci_n
from positioning import tum_konumlar
from ui import theme
from ui.windows.base import AnalyticsWindow


class TohumSecimPenceresi(AnalyticsWindow):
    BASLIK = "Tohum Seçimi"

    tohum_secildi = Signal(int)
    secim_temizle = Signal()

    def __init__(self, mevcut_n: int = 100, aci_derece: float = 137.5077) -> None:
        super().__init__()
        self._mevcut_n = max(int(mevcut_n), 1)
        self._aci_derece = float(aci_derece)
        self.resize(420, 280)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(16, 16, 16, 16)
        duzen.setSpacing(8)

        ust = QLabel(
            f"Spiraldeki bir tohumun indeksini gir (0 ≤ i < {self._mevcut_n})."
        )
        ust.setWordWrap(True)
        duzen.addWidget(ust)

        giris_satiri = QHBoxLayout()
        giris_satiri.addWidget(QLabel("İndeks (i):"))
        self.giris_kutu = QLineEdit()
        self.giris_kutu.setValidator(QIntValidator(0, self._mevcut_n - 1, self))
        self.giris_kutu.setPlaceholderText(f"0 — {self._mevcut_n - 1}")
        giris_satiri.addWidget(self.giris_kutu, 1)

        self.sec_butonu = QPushButton("Seç")
        self.sec_butonu.setProperty("primary", True)
        self.sec_butonu.clicked.connect(self._sec)
        self.giris_kutu.returnPressed.connect(self._sec)
        giris_satiri.addWidget(self.sec_butonu)
        duzen.addLayout(giris_satiri)

        # 5 satır bilgi
        self.bilgi_i = QLabel("")
        self.bilgi_f = QLabel("")
        self.bilgi_aci = QLabel("")
        self.bilgi_yaricap = QLabel("")
        self.bilgi_konum = QLabel("")
        for e in (
            self.bilgi_i,
            self.bilgi_f,
            self.bilgi_aci,
            self.bilgi_yaricap,
            self.bilgi_konum,
        ):
            e.setWordWrap(True)
            duzen.addWidget(e)

        duzen.addStretch(1)

    def _sec(self) -> None:
        metin = self.giris_kutu.text().strip()
        if not metin:
            return
        try:
            idx = int(metin)
        except ValueError:
            return

        if idx < 0 or idx >= self._mevcut_n:
            self._bilgileri_temizle()
            self.bilgi_i.setText(
                f"❌ Geçersiz indeks: {idx} (aralık 0 — {self._mevcut_n - 1})"
            )
            self.bilgi_i.setStyleSheet(f"color: {theme.VURGU};")
            self.secim_temizle.emit()
            return

        # Hesapla
        konumlar = tum_konumlar(self._mevcut_n, aci_radyan=math.radians(self._aci_derece))
        x, y = konumlar[idx]
        f_val = fibonacci_n(idx)
        aci_mod = (idx * self._aci_derece) % 360.0
        yaricap = math.hypot(x, y)

        self.bilgi_i.setText(f"i = {idx}")
        self.bilgi_i.setStyleSheet(f"color: {theme.AKSAN};")
        self.bilgi_f.setText(f"F({idx}) = {f_val}")
        self.bilgi_aci.setText(f"Açı (i·α mod 360°) = {aci_mod:.4f}°")
        self.bilgi_yaricap.setText(f"Yarıçap = {yaricap:.4f}")
        self.bilgi_konum.setText(f"Konum = ({x:.4f}, {y:.4f})")
        self.tohum_secildi.emit(idx)

    def _bilgileri_temizle(self) -> None:
        for e in (
            self.bilgi_f,
            self.bilgi_aci,
            self.bilgi_yaricap,
            self.bilgi_konum,
        ):
            e.setText("")

    def closeEvent(self, event):  # noqa: N802 (Qt API)
        self.secim_temizle.emit()
        super().closeEvent(event)
