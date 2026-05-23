"""
ui.windows.fibonacci_validator
------------------------------
Bir tam sayı için Fibonacci doğrulaması. Accept ise tohum_vurgula(idx)
sinyali ile ana SpiralCanvas'a mavi vurgu yansıtılır; Reject veya
pencere kapanışında vurgu_temizle() yayılır.
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from fibonacci import fibonacci_dizisi
from validator import (
    dogrula_ve_index,
    en_yakin_iki_fibonacci_indeksli,
    SONUC_ACCEPT,
)
from ui import theme
from ui.windows.base import AnalyticsWindow


class FibonacciValidatorPenceresi(AnalyticsWindow):
    BASLIK = "Fibonacci Doğrulayıcı"

    tohum_vurgula = Signal(int)
    vurgu_temizle = Signal()

    def __init__(self, mevcut_n: int = 100) -> None:
        super().__init__()
        self._mevcut_n = max(int(mevcut_n), 2)
        self.resize(420, 220)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(16, 16, 16, 16)
        duzen.setSpacing(10)

        baslik = QLabel("Bir tam sayı yazıp Fibonacci dizisinde olup\nolmadığını kontrol edin.")
        baslik.setWordWrap(True)
        duzen.addWidget(baslik)

        giris_satiri = QHBoxLayout()
        giris_satiri.addWidget(QLabel("Sayı:"))
        self.giris_kutu = QLineEdit()
        # QIntValidator 32-bit imzalı; F(46) ≈ 1.8e9 zaten kapsam içinde
        self.giris_kutu.setValidator(QIntValidator(0, 2**31 - 1, self))
        self.giris_kutu.setPlaceholderText("örn. 21, 89, 144")
        giris_satiri.addWidget(self.giris_kutu, 1)

        self.dogrula_butonu = QPushButton("Doğrula")
        self.dogrula_butonu.setProperty("primary", True)
        self.dogrula_butonu.clicked.connect(self._dogrula)
        self.giris_kutu.returnPressed.connect(self._dogrula)
        giris_satiri.addWidget(self.dogrula_butonu)

        duzen.addLayout(giris_satiri)

        self.sonuc_etiketi = QLabel("")
        self.sonuc_etiketi.setWordWrap(True)
        f = self.sonuc_etiketi.font()
        f.setPointSize(13)
        f.setBold(True)
        self.sonuc_etiketi.setFont(f)
        duzen.addWidget(self.sonuc_etiketi)

        self.alt_etiketi = QLabel("")
        self.alt_etiketi.setWordWrap(True)
        duzen.addWidget(self.alt_etiketi)

        duzen.addStretch(1)

    def _dogrula(self) -> None:
        metin = self.giris_kutu.text().strip()
        if not metin:
            return
        try:
            sayi = int(metin)
        except ValueError:
            return

        graf_dizi = fibonacci_dizisi(self._mevcut_n + 1)[: self._mevcut_n]
        sonuc, idx = dogrula_ve_index(sayi, graf_dizi)
        if sonuc == SONUC_ACCEPT and idx is not None:
            f_val = graf_dizi[idx]
            self.sonuc_etiketi.setText(f"✅ Accept: v{idx} düğümü (F={f_val})")
            self.sonuc_etiketi.setStyleSheet(f"color: {theme.AKSAN};")
            self.alt_etiketi.setText("")
            self.tohum_vurgula.emit(idx)
        else:
            (alt_idx, alt_val), (ust_idx, ust_val) = en_yakin_iki_fibonacci_indeksli(
                sayi, graf_dizi
            )
            self.sonuc_etiketi.setText(f"❌ Reject: {sayi} Fibonacci değil")
            self.sonuc_etiketi.setStyleSheet(f"color: {theme.VURGU};")
            parcalar = []
            if alt_idx is not None and alt_val is not None:
                parcalar.append(f"F({alt_idx})={alt_val}")
            if ust_idx is not None and ust_val is not None:
                parcalar.append(f"F({ust_idx})={ust_val}")
            self.alt_etiketi.setText("En yakın: " + ", ".join(parcalar) if parcalar else "")
            self.vurgu_temizle.emit()

    def closeEvent(self, event):  # noqa: N802 (Qt API)
        self.vurgu_temizle.emit()
        super().closeEvent(event)
