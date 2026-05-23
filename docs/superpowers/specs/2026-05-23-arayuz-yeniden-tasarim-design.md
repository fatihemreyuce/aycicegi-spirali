# Arayüz Yeniden Tasarım — Tasarım Dokümanı

**Tarih:** 2026-05-23
**Durum:** Onay bekliyor
**Kapsam:** Mevcut Tkinter/matplotlib tabanlı 3 sütun arayüzünü, akademik aydınlık tarzda PySide6 tabanlı spiral-merkezli bir arayüze taşımak.

---

## 1. Motivasyon

Mevcut arayüz (`gui.py`) Tkinter ile yazılmış, koyu tema, 3 sütunlu yoğun bir panel düzeni:
- Sol: kontrol paneli (n kaydırıcısı, açı, butonlar, validator)
- Orta: matplotlib canvas (spiral)
- Sağ: canlı bilgi paneli (F oranları, tohum bilgisi vb.)
- Ek özellikler (`comparison_window.py`, `traversal_window.py`, `dijkstra_window.py`, `convergence_plot.py`) ayrı Tk pencerelerinde açılıyor.

Sorunlar:
- Kalabalık görünüyor; spirale değil çevre panellere odak kayıyor.
- Koyu tema "data app" hissi veriyor — spiral aslında bir matematik figürü, akademik bir his daha doğal.
- Mevcut özellikler organize değil — her şey aynı menüde / butonda; yenisi eklendikçe karışıyor.

Hedef: spirali ön plana alan, sade, ders-kitabı estetiğinde bir arayüz. Tüm mevcut işlevsellik korunur; sadece sunum değişir.

---

## 2. Karar Özeti

Brainstorm aşamasında alınan kararlar (referans: `.superpowers/brainstorm/`):

| Konu | Karar |
|---|---|
| Görsel yön | **A — Akademik & Aydınlık.** Beyaz/krem zemin, serif tipografi, ders-kitabı estetiği. |
| Layout | **B — Spiral-merkezli + üst şerit.** Spiral neredeyse tüm ekranı kaplar, üstte ince kontrol şeridi. |
| Teknoloji | **PySide6.** Tk yerine native Qt; daha iyi tipografi, taşınabilir alt-pencereler, modern widget'lar. |
| Özellik organizasyonu | **B — Bağımsız Qt pencereleri.** Her analitik özellik kendi penceresinde, yan yana dizilebilir. |
| Spiral annotation | **B + C kombinasyonu.** Varsayılan: Fibonacci indeksli noktalar kırmızı + küçük rakam etiketli; parastichy uçlarında "→13", "→21" ipuçları. Üstüne: hover/tıkla → küçük detay kartı (indeks, F(n), açı, yarıçap). |
| Tipografi + palet | **A — Georgia + Oxford Lacivert.** PySide6'da hazır; Türkçe karakterler temiz. Aksan `#1a4480`, vurgu `#b8242a`. |
| Menü organizasyonu | 3 ana menü: Graf / Algoritma / Görselleştir. Üst şeritte sadece günlük kontroller. |

---

## 3. Mimari

### 3.1 Modül haritası

Mevcut domain modülleri (`fibonacci.py`, `validator.py`, `positioning.py`, `graph_builder.py`, `graph_traversal.py`, `utils.py`, `convergence_plot.py` içindeki saf hesap kısmı) **dokunulmaz**. Yeniden tasarım sadece sunum katmanını değiştirir.

Yeni sunum katmanı:

```
ui/
  __init__.py
  app.py                  # QApplication + ana pencere kurulumu
  main_window.py          # MainWindow (üst şerit + spiral canvas + bilgi kartı)
  theme.py                # Renkler, fontlar, stylesheet
  spiral_canvas.py        # Matplotlib QWidget — spirali çizen ana görsel
  info_card.py            # Sağ-üst overlay (F oranları, tohum, imleç)
  top_bar.py              # n / α / Çiz / Animasyon / Yakınlaştır + 3 menü
  windows/
    __init__.py
    base.py               # AnalyticsWindow (taşıma, "tekil pencere" mantığı)
    graph_view.py         # Graf görünümü (mevcut graph_builder kullanılır)
    adjacency_matrix.py   # Komşuluk matrisi
    validator_window.py   # Fibonacci doğrulayıcı
    bfs_dfs.py            # BFS/DFS gezinme
    dijkstra.py           # Dijkstra (mevcut dijkstra_window.py'den port)
    seed_picker.py        # Tohum seçimi
    convergence.py        # Yakınsama grafiği
    comparison.py         # Açı karşılaştırma
    animation.py          # Animasyon kontrol paneli
main.py                   # ui.app:main fonksiyonunu çağırır
```

**Mevcut dosyaların durumu:**
- `main.py` → tek satır değişir (yeni `ui.app:main` çağrısı).
- `gui.py`, `comparison_window.py`, `traversal_window.py`, `dijkstra_window.py` → arşive (`legacy/` altına) taşınır, içeriği `ui/` altına port edilir. Bir migration faz'ında her birinin Tk → Qt karşılığı yazılır.
- `animator.py`, `visualizer.py` → matplotlib bağımlı kısımları `ui/spiral_canvas.py` içine emilir; saf hesap (frame üretimi) ayrı bir `presentation/` modülüne ayrılır (opsiyonel — ilk fazda mevcut hâliyle kullanılabilir).
- `convergence_plot.py` → hesaplama kısmı kalır; matplotlib figure üretimi `ui/windows/convergence.py` içine taşınır.

### 3.2 Üst şerit içeriği (her zaman görünür)

| Öğe | Tip | Davranış |
|---|---|---|
| `🌻 Ayçiçeği Spirali` | Başlık | statik |
| `n` | `QSpinBox` (50–2000) | yazma + ok tuşları; değişiklik anında değil "Çiz"de uygulanır |
| `α` | `QDoubleSpinBox` (30.0°–180.0°, 0.1° adım) | varsayılan 137.5° |
| `Çiz` | `QPushButton` (primary) | spirali yeniden çizer |
| `▶ Animasyon` | `QPushButton` (toggle) | animasyonu **başlat/durdur** kısayolu (varsayılan hızla). Hız, manuel adım vb. tam kontrol için Görselleştir → Animasyon Kontrol penceresi. |
| `⊕ Yakınlaştır` | `QToolButton` (toggle) | tıklayınca cursor + drag ile zoom moduna geçer |
| **(sağda)** `Graf ▾` `Algoritma ▾` `Görselleştir ▾` | `QMenu` | analitik pencereler |

### 3.3 Menü içerikleri

**Graf ▾**
- Graf Görünümü → `windows/graph_view.py`
- Komşuluk Matrisi → `windows/adjacency_matrix.py`
- Fibonacci Doğrulayıcı → `windows/validator_window.py`

**Algoritma ▾**
- BFS / DFS Gezinme → `windows/bfs_dfs.py`
- Dijkstra Kısa Yol → `windows/dijkstra.py`
- Tohum Seçimi → `windows/seed_picker.py`

**Görselleştir ▾**
- Yakınsama Grafiği → `windows/convergence.py`
- Açı Karşılaştırma → `windows/comparison.py`
- Animasyon Kontrol → `windows/animation.py`

### 3.4 Sağ-üst bilgi kartı (spiral overlay)

Spiral canvas'ın sağ-üst köşesinde kalıcı küçük bir kart:
```
F(11) = 144
F(11)/F(10) = 1.6180 → φ
seçili tohum: 13
imleç: (46, 28)
```
Sade serif, küçük punto. Eski sağ panelin yerine geçer; yer kaplamaz, spirali bozmaz.

### 3.5 Spiral annotation kuralları (canvas içi)

- Tüm noktalar: 2px koyu lacivert (`#1a2238`) daireler.
- Fibonacci indeksli noktalar (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...): 3px kırmızı (`#b8242a`) + yanlarında küçük rakam (Georgia 8pt, `#555`).
- Parastichy uçları: en dış halkada görünür sarmalın yanında "→13", "→21" gibi italik ipuçları (`#1a4480`).
- Hover: cursor bir noktaya 10px yakınsa, küçük tooltip kartı açılır: indeks, F(n) (eğer Fibonacci indeksindeyse), açı, polar yarıçap.
- Tıklama: aynı tooltip kalıcı olur (pin); başka noktaya tıklayınca yer değiştirir.

### 3.6 Pencere yönetimi

Her analitik özellik için tek bir aktif pencere instance'ı:
- Menüden tıklarsan zaten açıksa → ön plana getir.
- Kapatılırsa → instance temizlenir.
- `AnalyticsWindow` base class taşıma, kapama, "tek instance" mantığını yönetir.

---

## 4. Tema — `ui/theme.py`

Tek noktadan tanımlanır, tüm widget'lar buradan okur.

```python
# Renk paleti — Oxford Lacivert akademik
ARKA_PLAN_ANA       = "#fafaf7"   # Pencere zemini (kağıt rengi)
ARKA_PLAN_KART      = "#ffffff"   # Beyaz kart/canvas
ARKA_PLAN_OVERLAY   = "#fcfaf3"   # Bilgi kartı (hafif krem)
KENAR_INCE          = "#e8e4d8"
KENAR_KALIN         = "#d8d4c5"

METIN_ANA           = "#1a2238"   # Gövde metni — koyu lacivert
METIN_IKINCIL       = "#666666"   # İkincil etiketler
METIN_PASIF         = "#888888"

AKSAN               = "#1a4480"   # Oxford lacivert — link, vurgu, başlık altı
AKSAN_KOYU          = "#142f5c"   # hover/pressed
VURGU               = "#b8242a"   # Fibonacci noktaları — uyarı kırmızısı

# Tipografi
FONT_GOVDE          = ("Georgia", 11)
FONT_BASLIK         = ("Georgia", 13, "bold")
FONT_KUCUK          = ("Georgia", 9)
FONT_MONO           = ("Consolas", 10)   # sayı tabloları için
```

`MainWindow.__init__` içinde `QApplication.setStyleSheet(...)` ile global Qt stylesheet'i uygulanır.

---

## 5. Veri akışı

Brainstorm değişmiş bir veri modeli getirmiyor. Mevcut akış korunur:

```
TopBar (n, α, Çiz) ─→ MainWindow.cizimi_yenile() ─→ graph_builder.grafi_olustur(n, α)
                                                  ↓
                              spiral_canvas: çiz + Fibonacci vurgula
                              info_card: F oranlarını güncelle
                              açık analitik pencereler: yeni grafı al → kendi görünümünü yenile
```

Analitik pencereler ana pencereye `graph_updated` Qt sinyaliyle abone olur. Eski Tk'de bu "geri çağırım listesi" ile yapılıyordu; Qt sinyali daha temiz.

---

## 6. Hata yönetimi

- Geçersiz `n` (≤0 ya da >2000) → `QSpinBox` zaten kabul etmez.
- Geçersiz `α` → `QDoubleSpinBox` aralık dışında kalmaz.
- Validator giriş kutusu (Fibonacci Doğrulayıcı penceresinde): sayı değilse → kırmızı kenar + altta "geçerli sayı girin" mesajı; uygulama çökmez.
- Dijkstra: kaynak > hedef (doğrusal grafta yol yok) → pencere üst kısmında uyarı kutusu, butonlar aktif kalır.
- Tek-instance ihlali (örn. eski referans hâlâ var) → mevcut pencere kapatılır, yenisi açılır; sessizce.

---

## 7. Test

Mevcut `tests/` dizinindeki domain testleri etkilenmez (presentation değişiyor). Yeni testler:

- `tests/test_theme.py` — renk/font sabitlerinin var ve dolu olduğunu doğrular (smoke).
- `tests/test_main_window.py` — `QApplication` + `MainWindow` ayağa kalkar, üst şerit widget'ları beklenen sayıda. (pytest-qt ile.)
- `tests/test_window_manager.py` — bir menüden aynı pencereyi iki kez açmanın yeni instance üretmediğini test eder.

UI'nin pixel-perfect testi yok; smoke + davranış yeterli.

**Yeni dev bağımlılığı:** `pytest-qt` (`requirements.txt` veya ayrı bir `requirements-dev.txt` dosyasına eklenir).

---

## 8. Migrasyon planı (özet — detaylar implementation plan'da)

Spec onaylanırsa `writing-plans` skill'i devreye girer ve aşağıdaki dilimleme önerilir:

1. **Bootstrap**: PySide6 bağımlılığı + `ui/` iskeleti + boş `MainWindow`.
2. **Theme & TopBar**: `theme.py`, `top_bar.py`, statik üst şerit (menü tıklama henüz no-op).
3. **SpiralCanvas + InfoCard**: spiral çizimi + hover/click annotation + sağ-üst bilgi kartı.
4. **Window infrastructure**: `AnalyticsWindow` base, tek-instance manager, graph_updated sinyali.
5. **Pencere portları** (her biri ayrı faz): graph_view → adjacency → validator → bfs_dfs → dijkstra → seed_picker → convergence → comparison → animation.
6. **Legacy temizliği**: `gui.py` ve eski `_window.py` dosyalarını `legacy/` altına taşı, `main.py` yeni giriş noktasını kullanır.

Her faz commit-edilebilir, çalıştırılabilir bir ara durum bırakır.

---

## 9. Kapsam dışı

Bu spec **sadece** sunum katmanı değişikliğini kapsar. Şunlar dışındadır:

- Yeni matematiksel özellik (örn. yeni bir spiral tipi).
- Domain modüllerinin (`graph_builder`, `validator`, vb.) refaktörü.
- Performans optimizasyonu (n > 2000 desteği gibi).
- I/O (kayıt/yükleme, export PNG vb.) — sonraki bir milestone.
- Çoklu dil desteği — TR sabit kalır.
- Erişilebilirlik (screen reader, kontrast WCAG) — kapsam dışı; ileride değerlendirilir.

---

## 10. Açık sorular

Yok — tüm büyük kararlar brainstorm aşamasında çözüldü. Implementation plan'da çıkacak küçük kararlar (örn. matplotlib backend seçimi `qtagg` vs `qt5agg`) plan dokümanına bırakıldı.
