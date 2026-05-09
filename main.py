"""
main.py
-------
Tüm modülleri birleştirip uygulamayı başlatan giriş noktası.

Çalıştırma:
    python main.py
"""

from gui import uygulamayi_baslat


def main() -> None:
    """Uygulamayı başlat."""
    # Tek satırlık bir başlangıç — tüm bileşenler gui.py içinde kuruluyor
    uygulamayi_baslat()


if __name__ == "__main__":
    main()
