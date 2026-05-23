"""
ui.theme
--------
Akademik aydınlık tema — renk paleti, font sabitleri ve global Qt stylesheet.

Tüm widget'lar bu modülden okur; renk veya font değişikliği tek yerden yapılır.
"""

from typing import Tuple


# ---- Renk paleti (Oxford Lacivert) ----

ARKA_PLAN_ANA: str = "#fafaf7"       # Pencere zemini (kağıt rengi)
ARKA_PLAN_KART: str = "#ffffff"      # Beyaz kart/canvas
ARKA_PLAN_OVERLAY: str = "#fcfaf3"   # Bilgi kartı (hafif krem)

KENAR_INCE: str = "#e8e4d8"
KENAR_KALIN: str = "#d8d4c5"

METIN_ANA: str = "#1a2238"           # Gövde — koyu lacivert
METIN_IKINCIL: str = "#666666"
METIN_PASIF: str = "#888888"

AKSAN: str = "#1a4480"               # Oxford lacivert — vurgu, başlık altı
AKSAN_KOYU: str = "#142f5c"          # hover/pressed
VURGU: str = "#b8242a"               # Fibonacci noktaları — uyarı kırmızısı


# ---- Tipografi ----

FONT_GOVDE: Tuple[str, int] = ("Georgia", 11)
FONT_BASLIK: Tuple[str, int, str] = ("Georgia", 13, "bold")
FONT_KUCUK: Tuple[str, int] = ("Georgia", 9)
FONT_MONO: Tuple[str, int] = ("Consolas", 10)


def qt_stylesheet() -> str:
    """Tüm uygulamaya uygulanan global Qt stylesheet'i döndürür."""
    return f"""
        QMainWindow, QWidget {{
            background-color: {ARKA_PLAN_ANA};
            color: {METIN_ANA};
            font-family: "{FONT_GOVDE[0]}";
            font-size: {FONT_GOVDE[1]}pt;
        }}
        QPushButton {{
            background-color: {ARKA_PLAN_KART};
            color: {AKSAN};
            border: 1px solid {KENAR_KALIN};
            padding: 4px 12px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background-color: {ARKA_PLAN_OVERLAY};
        }}
        QPushButton[primary="true"] {{
            background-color: {AKSAN};
            color: {ARKA_PLAN_KART};
            border: 1px solid {AKSAN_KOYU};
        }}
        QPushButton[primary="true"]:hover {{
            background-color: {AKSAN_KOYU};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {ARKA_PLAN_KART};
            color: {AKSAN};
            border: 1px solid {KENAR_KALIN};
            padding: 2px 6px;
            font-weight: bold;
        }}
        QMenu {{
            background-color: {ARKA_PLAN_KART};
            border: 1px solid {KENAR_KALIN};
        }}
        QMenu::item:selected {{
            background-color: {AKSAN};
            color: {ARKA_PLAN_KART};
        }}
        QLabel[role="title"] {{
            font-weight: bold;
            color: {AKSAN};
        }}
    """
