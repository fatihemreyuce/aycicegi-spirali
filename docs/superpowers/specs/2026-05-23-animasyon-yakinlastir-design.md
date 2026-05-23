# Animasyon + Yakınlaştır — Tasarım

> PySide6 portunda **▶ Animasyon** ve **⊕ Yakınlaştır** butonları görsel olarak duruyor ama henüz işlevsel değildi (Plan 1'in kapsam dışı maddesi). Bu spec, ikisini de çalışır hâle getirir ve eski Tk arayüzündeki davranışı PySide6'ya port eder.

## Goal

`python main.py` ile açılan PySide6 arayüzünde:

- Kullanıcı **Hız** seçer (Yavaş / Normal / Hızlı / Anında), **Animasyon**'a basar → tohumlar tek tek eklenerek spiral oluşur; aktif tohum kırmızı, ziyaret edilenler koyu lacivert, henüz yerleşmemişler gri.
- **Hız=Anında** → tek karede tam spiral (mevcut Çiz davranışı).
- Doğal bitiş → animasyon durur, tam spiral kalır, buton OFF'a döner.
- **Mouse scroll** spiral canvas'ta her zaman zoom; **sol-tık + drag** (boş alanda) pan. **↺ Sığdır** butonu görünümü otomatik yeniden boyutlandırır.

## Context

- Eski Tk arayüzünde animasyon `animator.SpiralAnimator` (matplotlib `FuncAnimation`) ile yapılıyor; hız ön ayarları `HIZ_AYARLARI = {Yavaş: 500, Normal: 200, Hızlı: 50, Anında: 1}` ms.
- Zoom/pan eski Tk'de `gui.py` içinde `mpl_connect("scroll_event", _zoom_olay)` ve sol-tık + drag pan ile yapılıyor.
- Yeni PySide6 `ui/spiral_canvas.py` şu an `spirali_ciz(n, aci)` ile tek karede tüm tohumları çiziyor; animasyon ve zoom/pan mantığı henüz yok.
- `ui/top_bar.py` Animasyon ve Yakınlaştır butonlarını sinyal olarak yayınlıyor (`animasyon_toggled`, `yakinlastir_toggled`) ama `MainWindow` bu sinyalleri bağlamıyor.

## Architecture

### Modül sorumlulukları

- **`ui/top_bar.py`** — UI kontrolleri:
  - `▶ Animasyon` butonu (mevcut, sinyalle kalır)
  - **YENİ:** `Hız: Normal ▾` QComboBox, `hiz_degisti(str)` sinyali ile yayınlar
  - **DEĞİŞTİ:** `⊕ Yakınlaştır` toggle → `↺ Sığdır` QPushButton (toggle değil, anlık aksiyon), `sigdir_istendi()` sinyali

- **`ui/spiral_canvas.py`** — çizim ve etkileşim:
  - **YENİ:** `animasyonu_basla(toplam_n, aci_derece, interval_ms)` — QTimer ile kare-kare çizim
  - **YENİ:** `animasyonu_durdur()` — QTimer'ı kapat, sahneyi mevcut karede dondur
  - **YENİ:** `animasyon_bitti` sinyali — doğal bitişte (kare_no = n-1) yayılır
  - **YENİ:** scroll-wheel zoom (imleç-merkezli), sol-tık-drag pan, `sigdir()` metodu
  - **DEĞİŞTİ:** `spirali_ciz` her zaman tek karede çizmeye devam eder; iç `_kare_ciz(kare_no, toplam, konumlar, fib_indeksleri)` yardımcısı kareye göre kısmen çizer

- **`ui/main_window.py`** — sinyal bağlayıcı:
  - `top_bar.animasyon_toggled` → `_animasyon_toggle_geldi(bool)`
  - `top_bar.hiz_degisti` → mevcut hız adını sakla, `_current_interval_ms` döndüren yardımcı
  - `top_bar.sigdir_istendi` → `canvas.sigdir()`
  - `canvas.animasyon_bitti` → `top_bar.animasyon_butonu.setChecked(False)`

### Renk durumları (sahnedeki tohumlar)

Öncelik sırası (üstte olan kazanır):

1. **Bekleyen** (henüz yerleşmemiş, `index > kare_no`): `#7d7d7d` gri
2. **Aktif** (`index == kare_no`): `theme.VURGU` (kırmızı `#b8242a`)
3. **Fibonacci + ziyaret edilmiş** (`index in fib AND index < kare_no`): `theme.VURGU` (kırmızı kalır)
4. **Ziyaret edilmiş** (`index < kare_no`, Fibonacci değil): `theme.METIN_ANA` (lacivert)

Yani Fibonacci vurgusu sadece tohum yerleştikten sonra görünür; bekleme aşamasında tüm tohumlar (Fibonacci dahil) gridir. Animasyon olmadığında (statik çizim) tüm n yerleşmiş sayılır → mevcut "Fibonacci kırmızı, kalanlar lacivert" görüntüsü değişmez.

### Animasyon mekanizması — QTimer

`matplotlib.animation.FuncAnimation` yerine **`QTimer`** kullanılıyor; gerekçe:

- PySide6 ekosistemine native, Qt event loop ile çatışmaz.
- Test edilebilir (`qtbot.waitSignal`, fake clock).
- Interval anlık güncellenebilir (`timer.setInterval`) — kullanıcı hız değiştirince animasyon kesilmeden devam eder.
- `repeat=False` davranışı doğal: son karede `timer.stop()` çağrılır.

Kare akışı:

```
animasyonu_basla(n, α, interval_ms)
    self._anim_toplam = n
    self._anim_kare = -1
    if interval_ms <= 1:
        _kare_ciz(n-1, ...)                # anında modu
        emit animasyon_bitti
        return
    self._timer.setInterval(interval_ms)
    self._timer.start()

QTimer.timeout
    self._anim_kare += 1
    _kare_ciz(self._anim_kare, ...)
    if self._anim_kare >= self._anim_toplam - 1:
        self._timer.stop()
        emit animasyon_bitti
```

### Zoom + pan

- **Scroll wheel** (`matplotlib.backend_bases.MouseEvent` → `scroll_event` mpl_connect): yön=1 zoom in, yön=-1 zoom out. Ölçek faktörü 1.2. İmleç-merkezli — yeni xlim/ylim, fare pozisyonu sabit kalacak şekilde hesaplanır (eski `gui.py:_zoom_olay` formülü).
- **Sol-tık + drag** pan: `button_press_event` → `(x0, y0)` anchor kaydet (matplotlib piksel koordinatları, `event.x`/`event.y`); `motion_notify_event` → `(x - x0)² + (y - y0)² > 5²` piksel eşiğini aşarsa pan moduna geç ve xlim/ylim'i veri koordinatlarına çevirip kaydır; `button_release_event` → anchor temizle. **Sol-tık aktif tohum üstündeyse** mevcut `nokta_tiklandi` davranışı bozulmasın diye: press anında piksel konumu kaydet, release'e kadar hareket eşik altında ise tıklama (mevcut `nokta_tiklandi` sinyali), üstünde ise pan (tıklama sinyali yayma).
- **`sigdir()`** metodu: `_axes.relim() + autoscale_view()` + %5 padding, `draw_idle()`.

### Çiz ↔ Animasyon etkileşimi

`MainWindow._cizim_istendi(n, aci)` içinde:

1. Animasyon çalışıyorsa `canvas.animasyonu_durdur()`, `top_bar.animasyon_butonu.setChecked(False)`.
2. `canvas.spirali_ciz(n, aci)` (mevcut anında tam çizim).
3. `info_card.n_degisti(n)`.

Yani Çiz = "şu an gör, animasyon iptal". Yeni animasyon istenirse Animasyon butonuna basılır.

Hız ComboBox değişimi animasyon çalışırken → `QTimer.setInterval` ile interval canlı güncellenir.

## Testing Strategy

### Yeni testler

- **`tests/test_top_bar.py`** ekler:
  - `hiz_kutu` 4 öğeyi içerir; default "Normal".
  - Hız değişimi `hiz_degisti(str)` sinyali yayar; argüman seçili ad.
  - `sigdir_butonu` tıklayınca `sigdir_istendi()` sinyali yayar.
- **`tests/test_spiral_canvas.py`** (yeni dosya):
  - `_kare_ciz(0, 100, ...)` sadece 1. tohumu kırmızı, kalanlar gri.
  - `_kare_ciz(50, 100, ...)` 0–49 lacivert, 50 kırmızı, 51+ gri.
  - `animasyonu_basla(10, α, 50)` → QTimer çalışır; 10 tick sonra `animasyon_bitti` yayılır (qtbot.waitSignal).
  - `animasyonu_basla(10, α, 1)` (anında) → QTimer çalışmaz, `animasyon_bitti` hemen yayılır, tüm tohumlar çizilir.
  - `animasyonu_durdur()` QTimer'ı kapatır ve `animasyon_bitti` yayılmaz.
  - `sigdir()` `_axes.get_xlim()`/`get_ylim()`'i spirale göre yeniden ayarlar.
- **`tests/test_main_window.py`** ekler:
  - `top_bar.animasyon_butonu.click()` → `canvas.animasyonu_basla` çağrılır (mock/spy ile).
  - `top_bar.hiz_kutu.setCurrentText("Hızlı")` → bağlı interval state güncellenir.
  - Animasyon çalışırken `top_bar.ciz_butonu.click()` → animasyon durur, Animasyon butonu OFF olur.
  - `canvas.animasyon_bitti` yayılır → Animasyon butonu otomatik OFF olur.

Mevcut testler kırılmamalı. `tests/conftest.py` `QT_QPA_PLATFORM=offscreen` ayarı QTimer'ı bozmaz (QTimer headless çalışır).

## Out of Scope

- Eski Tk'de bulunan **manuel ◀ Geri / ▶ Adım** butonları — ayrı bir plan.
- Animasyon sırasında **tohum tıklama / hover** — mevcut davranış korunur ama renk durumlarıyla görsel çakışma olabilir; bu spec sadece "seçili tohum mor olarak öncelikli" kuralını korur, Plan 1'deki gibi.
- Animasyon devam ederken n/α SpinBox değişimi → şu an hiçbir şey yapmıyor (sadece Çiz'e basınca etki ediyor); bu davranış aynen korunur.
- **Animasyon sırasında graph_builder** ile DiGraph inşası — şu an SpiralCanvas sadece `tum_konumlar` kullanıyor, graf öznitelikleri animasyona girmiyor.
