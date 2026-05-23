"""
ui.windows.animation_control
----------------------------
Manuel animasyon kontrol penceresi: ◀ Geri / ▶ İleri butonları + kare
slider. Ana SpiralCanvas'ı cross-window olarak kontrol eder.

Sinyaller:
  kareye_atla_istendi(int) — kullanıcı bir kareye atlamak istedi.

Slot:
  kareyi_guncelle(int) — canvas tarafından çağrılır, slider + etiket
  güncellenir (sinyal döngüsü olmadan).
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
)

from ui.windows.base import AnalyticsWindow


class AnimasyonKontrolPenceresi(AnalyticsWindow):
    BASLIK = "Animasyon Kontrol"

    kareye_atla_istendi = Signal(int)

    def __init__(self, toplam_n: int = 100, baslangic_kare: int = 0) -> None:
        super().__init__()
        self._toplam = max(int(toplam_n), 1)
        self.resize(560, 160)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(16, 16, 16, 16)
        duzen.setSpacing(10)

        # Bilgi etiketi
        self.bilgi_etiketi = QLabel("")
        duzen.addWidget(self.bilgi_etiketi)

        # Buton + slider satırı
        kontrol_satiri = QHBoxLayout()
        self.geri_butonu = QPushButton("◀ Geri")
        self.geri_butonu.clicked.connect(self._geri)
        kontrol_satiri.addWidget(self.geri_butonu)

        self.kare_kaydirici = QSlider(Qt.Orientation.Horizontal)
        self.kare_kaydirici.setRange(-1, self._toplam - 1)
        self.kare_kaydirici.setValue(int(baslangic_kare))
        self.kare_kaydirici.valueChanged.connect(self._slider_degisti)
        kontrol_satiri.addWidget(self.kare_kaydirici, 1)

        self.ileri_butonu = QPushButton("▶ İleri")
        self.ileri_butonu.clicked.connect(self._ileri)
        kontrol_satiri.addWidget(self.ileri_butonu)

        duzen.addLayout(kontrol_satiri)

        # İlk gösterim
        self._etiket_yenile(int(baslangic_kare))

    def _etiket_yenile(self, k: int) -> None:
        gosterim = max(0, k + 1)  # -1 → 0, 0 → 1, ...
        self.bilgi_etiketi.setText(f"Kare {gosterim} / {self._toplam}")

    def _slider_degisti(self, k: int) -> None:
        self._etiket_yenile(k)
        self.kareye_atla_istendi.emit(k)

    def _geri(self) -> None:
        yeni = max(-1, self.kare_kaydirici.value() - 1)
        # Slider'ı değiştirmek _slider_degisti'yi tetikler — sinyal yayar
        self.kare_kaydirici.setValue(yeni)

    def _ileri(self) -> None:
        yeni = min(self._toplam - 1, self.kare_kaydirici.value() + 1)
        self.kare_kaydirici.setValue(yeni)

    def kareyi_guncelle(self, k: int) -> None:
        """
        Canvas dışarıdan kare değişikliği bildirdi — slider'ı güncelle
        AMA kareye_atla_istendi sinyalini yayma (döngü olmasın diye).
        """
        # blockSignals ile valueChanged'ı bastır
        self.kare_kaydirici.blockSignals(True)
        try:
            self.kare_kaydirici.setValue(k)
        finally:
            self.kare_kaydirici.blockSignals(False)
        self._etiket_yenile(k)
