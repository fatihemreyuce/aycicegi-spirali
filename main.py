"""
main.py
-------
PySide6 tabanlı yeni arayüzü başlatır.

Çalıştırma:
    python main.py

Eski Tkinter arayüzüne dönmek için: python main_legacy.py
"""

import sys

from ui.app import main as _ui_main


def main() -> None:
    sys.exit(_ui_main())


if __name__ == "__main__":
    main()
