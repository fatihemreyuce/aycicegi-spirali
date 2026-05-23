# Fibonacci Doğrulayıcı (Plan 3) — Tasarım

> İlk gerçek analitik pencere portu. Plan 1'de placeholder olarak duran "Graf ▾ → Fibonacci Doğrulayıcı" için somut UI. Eski Tk davranışına eş port + ana spirale **mavi vurgu** geri bildirim pattern'i kuruluyor (sonraki pencereler için şablon).

## Goal

`graf.validator` menü öğesi tıklanınca açılan pencerede:

- Bir tam sayı girilir → **Doğrula** butonu → sonuç:
  - **Accept** → "✅ Accept: v₈ düğümü (F=21)" yeşil + ana SpiralCanvas'ta o tohum mavi vurgulanır.
  - **Reject** → "❌ Reject: 22 Fibonacci değil" kırmızı + alt satır "En yakın: F(7)=13, F(8)=21". Mavi vurgu yok.
- Pencere kapanınca veya yeni Reject girilince mavi vurgu **temizlenir**.

## Components

### `ui/windows/fibonacci_validator.py` (yeni)

`FibonacciValidatorPenceresi(AnalyticsWindow)` — `BASLIK = "Fibonacci Doğrulayıcı"`.

**Sinyaller (cross-window):**
- `tohum_vurgula(int)` — Accept'te tohum indeksi.
- `vurgu_temizle()` — Reject veya pencere kapanırken.

**Widget'lar:**
- `QLineEdit` (input — `QIntValidator(0, 10**12)`)
- `QPushButton("Doğrula")` (default button — Enter de tetikler)
- `QLabel` ana sonuç (yeşil/kırmızı, font-size 13pt bold)
- `QLabel` alt sonuç (en yakın iki Fibonacci, küçük metin)

**Sahnenin n'i:** Pencere `mevcut_n: int` parametresi alır (MainWindow ana spiraldeki aktif n'i geçer). Bu n'lik `fibonacci_dizisi(n+1)` ile sınırlı doğrulama (eski Tk davranışı).

### `ui/spiral_canvas.py` — vurgu API'si

Yeni: `vurgu_ekle(idx: int)` / `vurgu_temizle()`. İç state `self._vurgu_indeksleri: set[int]`. `_kare_ciz` renk öncelik sırasına ek satır eklenir:

| Öncelik | Durum | Renk |
|---|---|---|
| 1 | `index > kare_no` | gri (BEKLEME) |
| 2 | `index == kare_no` | kırmızı (VURGU) |
| 3 | **`index in vurgu_indeksleri AND index <= kare_no`** | **mavi (MAVI_VURGU yeni)** |
| 4 | `index in fib AND index < kare_no` | kırmızı (VURGU) |
| 5 | `index < kare_no` | lacivert (METIN_ANA) |

### `ui/theme.py` — yeni renk

`MAVI_VURGU: str = "#1f8bff"` — validator vurgu rengi.

### `ui/main_window.py` — bağlantı

`MENU_BASLIKLARI["graf.validator"]` öğesi `FibonacciValidatorPenceresi(mevcut_n=self.top_bar.n_kutu.value())` fabrikasıyla açılır. Sinyaller bağlanır:
- `pencere.tohum_vurgula` → `self.canvas.vurgu_ekle`
- `pencere.vurgu_temizle` → `self.canvas.vurgu_temizle`

## Testing

- `tests/test_fibonacci_validator.py` (yeni): Accept/Reject sinyalleri, en yakın 2 görünümü, Enter ile tetikleme.
- `tests/test_spiral_canvas.py`: `vurgu_ekle/_temizle` öncelik testi.
- `tests/test_main_window.py`: `graf.validator` menü tıklayınca yeni pencere açılır + sinyal bağlanır.

## Out of Scope

- "Multi-vurgu" (aynı anda birden çok Fibonacci'yi vurgula) — şu an tek vurgu, yeni Accept öncekini değiştirir.
- Klavye kısayolları (Ctrl+L = clear vb.).
- Pencere açıldıktan sonra ana spiralin `n` değişirse vurgunun geçerliliği — pencere kapatıp tekrar açılınca son n okunur, canlı sync yok.
