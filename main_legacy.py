"""
main_legacy.py
--------------
Eski Tkinter tabanlı arayüzü başlatır. Yeni PySide6 arayüzü tamamlanana
kadar geri dönüş yolu olarak tutulur. Çalıştırma:

    python main_legacy.py
"""

from gui import uygulamayi_baslat


def main() -> None:
    uygulamayi_baslat()


if __name__ == "__main__":
    main()
