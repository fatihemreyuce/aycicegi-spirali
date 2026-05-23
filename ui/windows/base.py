"""
ui.windows.base
---------------
Analitik pencerelerin base class'ı ve tek-instance yöneticisi.

Kullanım:
    yonetici = WindowManager()
    pencere = yonetici.ac_veya_one_getir("graf.gorunum", GrafGorunumPencere)
"""

from typing import Callable, Optional

from PySide6.QtWidgets import QWidget


class AnalyticsWindow(QWidget):
    """
    Analitik pencerelerin base class'ı. Alt sınıflar BASLIK'ı override eder
    ve gerçek içeriği __init__ içinde kurar.
    """

    BASLIK: str = "Pencere"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        # Üst-seviye pencere — parent verme; sadece referans tutmak için yönetici
        # parent argümanı kullanmaz, top-level QWidget yaratırız
        super().__init__()
        self.setWindowTitle(self.BASLIK)
        self.resize(640, 480)


class WindowManager:
    """
    Tek-instance pencere yönetimi.

    Her kimlik (eylem id'si, örn. "graf.gorunum") için en fazla bir açık
    pencere tutar. ac_veya_one_getir çağrısı:
      - kimliğin penceresi yoksa yeni instance üretip gösterir,
      - varsa onu ön plana getirir.

    Pencere kapanınca destroyed sinyali ile sözlükten temizlenir.
    """

    def __init__(self) -> None:
        self._pencereler: dict[str, AnalyticsWindow] = {}

    def ac_veya_one_getir(
        self,
        kimlik: str,
        fabrika: Callable[[], AnalyticsWindow],
    ) -> AnalyticsWindow:
        """Verilen kimlik için pencereyi üret ya da var olanı ön plana getir."""
        mevcut = self._pencereler.get(kimlik)
        if mevcut is not None:
            mevcut.show()
            mevcut.raise_()
            mevcut.activateWindow()
            return mevcut

        yeni = fabrika()
        self._pencereler[kimlik] = yeni
        # Kapatılınca sözlükten çıkar
        yeni.destroyed.connect(lambda *_: self._pencereler.pop(kimlik, None))
        yeni.show()
        return yeni
