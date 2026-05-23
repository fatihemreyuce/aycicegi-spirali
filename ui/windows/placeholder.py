"""
ui.windows.placeholder
----------------------
Sonraki planlarda port edilecek analitik pencereler için ortak yer-tutucu.
"Yapım aşamasında" mesajı gösterir; menüden tıklanınca açılır.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel

from ui.windows.base import AnalyticsWindow


class PlaceholderWindow(AnalyticsWindow):
    BASLIK = "Yapım aşamasında"

    def __init__(self, eylem_id: str, baslik: str) -> None:
        super().__init__()
        self.setWindowTitle(f"{baslik} — yapım aşamasında")
        duzen = QVBoxLayout(self)
        etiket = QLabel(
            f"Bu pencere ('{eylem_id}') sonraki planda port edilecek.\n\n"
            f"Şimdilik yer tutuyor — kapatabilirsin."
        )
        etiket.setWordWrap(True)
        duzen.addWidget(etiket)
