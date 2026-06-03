"""
ui.main_window
--------------
Ana pencere: üst şerit + spiral canvas + bilgi kartı (overlay).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ui.top_bar import TopBar
from ui.spiral_canvas import SpiralCanvas
from ui.info_card import InfoCard
from ui.windows.base import WindowManager
from ui.windows.placeholder import PlaceholderWindow
from ui.windows.fibonacci_validator import FibonacciValidatorPenceresi
from ui.windows.convergence import YakinsamaPenceresi
from ui.windows.comparison import KarsilastirmaPenceresi
from ui.windows.adjacency_matrix import KomsulukMatrisiPenceresi


# Menü eylem kimliği → kullanıcıya gösterilecek başlık
MENU_BASLIKLARI: dict[str, str] = {
    "graf.gorunum": "Graf Görünümü",
    "graf.matris": "Komşuluk Matrisi",
    "graf.validator": "Fibonacci Doğrulayıcı",
    "gor.yakinsama": "Yakınsama Grafiği",
    "gor.karsilastirma": "Açı Karşılaştırma",
    "gor.ayciegi": "Ayçiçeği Görünümü",
}


class MainWindow(QMainWindow):
    """Ayçiçeği Spirali uygulamasının ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ayçiçeği Spirali — Fibonacci & Vogel")
        self.resize(1280, 800)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        duzen = QVBoxLayout(merkez)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.setSpacing(0)

        self.top_bar = TopBar()
        duzen.addWidget(self.top_bar)

        self.canvas = SpiralCanvas()
        duzen.addWidget(self.canvas, 1)

        # InfoCard overlay — canvas'ın çocuğu (Qt parent), free-floating
        self.info_card = InfoCard(self.canvas)
        self.info_card.setParent(self.canvas)

        # Sinyalleri bağla
        self.top_bar.cizim_istendi.connect(self._cizim_istendi)
        self.canvas.nokta_hover.connect(self.info_card.secili_tohum)
        self.canvas.nokta_hover_iptal.connect(lambda: self.info_card.secili_tohum(None))
        self.canvas.nokta_tiklandi.connect(self.info_card.secili_tohum)

        # Animasyon bağlantıları
        self.top_bar.animasyon_toggled.connect(self._animasyon_toggle_geldi)
        self.top_bar.hiz_degisti.connect(self._hiz_degisti)
        self.canvas.animasyon_bitti.connect(self._animasyon_bitti)

        # Pencere yöneticisi + menü bağlantısı
        self._pencere_yoneticisi = WindowManager()
        self.top_bar.menu_eylemi.connect(self._menu_eylemi_geldi)

        # İlk çizim — açılışta spiral anında görünür (animasyon yalnızca Çiz'e basınca).
        self.canvas.spirali_ciz(self.top_bar.n_kutu.value(), self.top_bar.aci_kutu.value())
        self.info_card.n_degisti(self.top_bar.n_kutu.value())

    def _cizim_istendi(self, n: int, aci_derece: float) -> None:
        # Çalışan animasyonu iptal — setChecked(False) toggle sinyali üzerinden
        # _animasyon_toggle_geldi'yi tetikler ve animasyonu_durdur çağrılır.
        if self.top_bar.animasyon_butonu.isChecked():
            self.top_bar.animasyon_butonu.setChecked(False)
        # Çiz: tüm noktaları tek karede değil, tohumları tek tek sırayla yerleştir
        # (başta boş sahne → sonda tam spiral). Hız seçicisi pace'i belirler;
        # "Anında" seçiliyse animasyonu_basla zaten tek karede çizer.
        interval = self._mevcut_interval_ms()
        self.canvas.animasyonu_basla(toplam_n=n, aci_derece=aci_derece, interval_ms=interval)
        self.info_card.n_degisti(n)

    def resizeEvent(self, event):  # noqa: N802 (Qt API)
        super().resizeEvent(event)
        self._info_card_konumla()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._info_card_konumla()

    def _info_card_konumla(self) -> None:
        """InfoCard'ı canvas'ın sağ-üst köşesine yerleştir (10px margin)."""
        if not self.canvas.isVisible():
            return
        self.info_card.adjustSize()
        margin = 12
        x = self.canvas.width() - self.info_card.width() - margin
        y = margin
        self.info_card.move(x, y)
        self.info_card.raise_()

    def _menu_eylemi_geldi(self, eylem_id: str) -> None:
        baslik = MENU_BASLIKLARI.get(eylem_id, eylem_id)
        if eylem_id == "graf.validator":
            self._pencere_yoneticisi.ac_veya_one_getir(
                eylem_id,
                self._fibonacci_validator_yarat,
            )
            return
        if eylem_id == "gor.yakinsama":
            self._pencere_yoneticisi.ac_veya_one_getir(
                eylem_id,
                lambda: YakinsamaPenceresi(mevcut_n=self.top_bar.n_kutu.value()),
            )
            return
        if eylem_id == "gor.karsilastirma":
            self._pencere_yoneticisi.ac_veya_one_getir(
                eylem_id,
                lambda: KarsilastirmaPenceresi(mevcut_n=self.top_bar.n_kutu.value()),
            )
            return
        if eylem_id == "graf.matris":
            self._pencere_yoneticisi.ac_veya_one_getir(
                eylem_id,
                lambda: KomsulukMatrisiPenceresi(
                    mevcut_n=self.top_bar.n_kutu.value(),
                    aci_derece=self.top_bar.aci_kutu.value(),
                ),
            )
            return
        if eylem_id == "graf.gorunum":
            # Ayrı pencere değil — ana canvas'ı toggle et
            if self.canvas.graf_modu_acik_mi():
                self.canvas.graf_modu_kapat()
            else:
                self.canvas.graf_modu_ac()
            return
        if eylem_id == "gor.ayciegi":
            # Kayıt için temiz tohum yatağı görünümü — toggle
            if self.canvas.ayciegi_modu_acik_mi():
                self.canvas.ayciegi_modu_kapat()
            else:
                self.canvas.ayciegi_modu_ac()
            return
        self._pencere_yoneticisi.ac_veya_one_getir(
            eylem_id,
            lambda: PlaceholderWindow(eylem_id, baslik),
        )

    def _fibonacci_validator_yarat(self) -> FibonacciValidatorPenceresi:
        """FibonacciValidatorPenceresi'ni mevcut n ile kur ve sinyalleri bağla."""
        p = FibonacciValidatorPenceresi(mevcut_n=self.top_bar.n_kutu.value())
        p.tohum_vurgula.connect(self.canvas.vurgu_ekle)
        p.vurgu_temizle.connect(self.canvas.vurgu_temizle)
        return p

    def _animasyon_toggle_geldi(self, basili: bool) -> None:
        """Animasyon butonu durumu değişti."""
        if basili:
            n = self.top_bar.n_kutu.value()
            aci = self.top_bar.aci_kutu.value()
            interval = self._mevcut_interval_ms()
            self.canvas.animasyonu_basla(toplam_n=n, aci_derece=aci, interval_ms=interval)
        else:
            self.canvas.animasyonu_durdur()

    def _hiz_degisti(self, ad: str) -> None:
        """Hız ComboBox seçimi değişti."""
        interval = self._mevcut_interval_ms()
        if self.top_bar.animasyon_butonu.isChecked():
            self.canvas.hiz_guncelle(interval_ms=interval)

    def _mevcut_interval_ms(self) -> int:
        """Seçili Hız adına karşılık gelen ms değerini döndürür."""
        hiz_haritasi = {"Yavaş": 500, "Normal": 200, "Hızlı": 50, "Anında": 1}
        return hiz_haritasi.get(self.top_bar.hiz_kutu.currentText(), 200)

    def _animasyon_bitti(self) -> None:
        """Canvas animasyon_bitti yaydı — buton state'ini OFF yap."""
        if self.top_bar.animasyon_butonu.isChecked():
            self.top_bar.animasyon_butonu.setChecked(False)
