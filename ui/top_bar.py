"""
ui.top_bar
----------
Ana pencerenin üst şeridi: n / α / Çiz / Animasyon / Yakınlaştır kontrolleri
ve sağda 3 ana menü (Graf / Algoritma / Görselleştir).

Bu modülde menülerin içeriği henüz bağlanmadı — Task 11'de bağlanacak.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QToolButton,
    QMenu,
    QFrame,
    QComboBox,
    QAbstractSpinBox,
)

from utils import ALTIN_ACI_DERECE


class TopBar(QWidget):
    """
    Her zaman görünür kontrol şeridi.

    Sinyaller:
        cizim_istendi(int, float) — n ve α(derece) ile Çiz'e basıldı.
        animasyon_toggled(bool)   — Animasyon butonu durum değiştirdi.
        yakinlastir_toggled(bool) — Yakınlaştır toggle durum değiştirdi.
        menu_eylemi(str)          — Bir menü öğesi tıklandı; argüman eylem kimliği.
    """

    cizim_istendi = Signal(int, float)
    animasyon_toggled = Signal(bool)
    hiz_degisti = Signal(str)
    menu_eylemi = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(14, 8, 14, 8)
        duzen.setSpacing(10)

        # Sol: Başlık
        baslik = QLabel("🌻 Ayçiçeği Spirali")
        baslik.setProperty("role", "title")
        duzen.addWidget(baslik)
        duzen.addWidget(self._dikey_cizgi())

        # n
        duzen.addWidget(QLabel("n"))
        self.n_kutu = QSpinBox()
        self.n_kutu.setRange(50, 5000)
        self.n_kutu.setValue(100)
        self.n_kutu.setFixedWidth(80)
        self.n_kutu.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.n_kutu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duzen.addWidget(self.n_kutu)

        # α
        duzen.addWidget(QLabel("α"))
        self.aci_kutu = QDoubleSpinBox()
        self.aci_kutu.setRange(30.0, 180.0)
        self.aci_kutu.setDecimals(2)
        self.aci_kutu.setSingleStep(0.1)
        self.aci_kutu.setValue(ALTIN_ACI_DERECE)
        self.aci_kutu.setSuffix("°")
        self.aci_kutu.setFixedWidth(100)
        self.aci_kutu.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.aci_kutu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duzen.addWidget(self.aci_kutu)

        # Çiz
        self.ciz_butonu = QPushButton("Çiz")
        self.ciz_butonu.setProperty("primary", True)
        self.ciz_butonu.clicked.connect(self._ciz_tiklandi)
        duzen.addWidget(self.ciz_butonu)

        duzen.addWidget(self._dikey_cizgi())

        # Animasyon
        self.animasyon_butonu = QPushButton("▶ Animasyon")
        self.animasyon_butonu.setCheckable(True)
        self.animasyon_butonu.toggled.connect(self.animasyon_toggled)
        duzen.addWidget(self.animasyon_butonu)

        # Hız
        duzen.addWidget(QLabel("Hız"))
        self.hiz_kutu = QComboBox()
        self.hiz_kutu.addItems(["Yavaş", "Normal", "Hızlı", "Anında"])
        self.hiz_kutu.setCurrentText("Normal")
        self.hiz_kutu.setFixedWidth(100)
        self.hiz_kutu.currentTextChanged.connect(self.hiz_degisti)
        duzen.addWidget(self.hiz_kutu)

        # Sağa it
        duzen.addStretch(1)

        # 2 menü (Algoritma menüsü ve Görselleştir > Animasyon Kontrol kaldırıldı)
        self.graf_butonu = self._menu_butonu_yarat("Graf ▾", [
            ("graf.gorunum", "Graf Görünümü"),
            ("graf.matris", "Komşuluk Matrisi"),
            ("graf.validator", "Fibonacci Doğrulayıcı"),
        ])
        duzen.addWidget(self.graf_butonu)

        self.gorsel_butonu = self._menu_butonu_yarat("Görselleştir ▾", [
            ("gor.yakinsama", "Yakınsama Grafiği"),
            ("gor.karsilastirma", "Açı Karşılaştırma"),
            ("gor.ayciegi", "Ayçiçeği Görünümü"),
        ])
        duzen.addWidget(self.gorsel_butonu)

    # ---- iç yardımcılar ----

    def _dikey_cizgi(self) -> QFrame:
        c = QFrame()
        c.setFrameShape(QFrame.Shape.VLine)
        c.setFrameShadow(QFrame.Shadow.Plain)
        return c

    def _menu_butonu_yarat(self, etiket: str, ogeler: list[tuple[str, str]]) -> QToolButton:
        buton = QToolButton()
        buton.setText(etiket)
        buton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(buton)
        for eylem_id, baslik in ogeler:
            eylem = menu.addAction(baslik)
            eylem.triggered.connect(lambda _checked=False, eid=eylem_id: self.menu_eylemi.emit(eid))
        buton.setMenu(menu)
        return buton

    def _ciz_tiklandi(self) -> None:
        self.cizim_istendi.emit(self.n_kutu.value(), self.aci_kutu.value())
