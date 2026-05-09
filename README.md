# 🌻 Ayçiçeği Spirali: Altın Oran ve Graflar Üzerine Matematiksel Bir İnceleme

> Doğanın en zarif geometrik desenlerinden birini — ayçiçeği başındaki tohum dizilimini — Fibonacci dizisi, altın oran ve yönlü graflar üzerinden modelleyen bir Python simülasyonu.

![Python](https://img.shields.io/badge/python-3.13%2B-blue) ![License](https://img.shields.io/badge/license-Eğitim-yellow) ![Status](https://img.shields.io/badge/proje-Dönem%20Projesi-success)

---

## 📖 Proje Hakkında

Bu proje, **ayçiçeği başındaki tohum dizilimini** matematiksel olarak modelleyip görselleştiren etkileşimli bir simülasyondur. Tohumların **Vogel formülü** ile yerleştirildiği konumlarda **altın açı (≈ 137.5°)** kullanılarak ortaya çıkan spiral desen, **Fibonacci dizisinin ardışık oranlarının altın orana yakınsamasıyla** doğrudan ilişkilidir. Tüm yapı — tohumlar, komşuluk ilişkileri ve geometrik kenar ağırlıkları — bir **yönlü graf (DiGraph)** olarak modellenmiştir.

🎓 **İstanbul Gedik Üniversitesi — Ayrık Matematik Dersi Dönem Projesi**

### 👥 Grup Üyeleri

| 👤 Ad Soyad | 🆔 Numara |
|---|---|
| Fatih Emre Yüce | 241046016 |
| Ramazan Türkyılmaz | 241041094 |
| Kaan Sarı | 241046012 |
| Talha Akarçeşme | 241046005 |

🧑‍🏫 **Danışman:** Dr. Öğr. Üyesi Fatma Zehra Uzemek

---

## 🧮 Matematiksel Temel

### ✨ Altın Oran (φ)

Altın oran, kendisiyle bir uzunluk arasındaki oranın, o uzunlukla farkları arasındaki orana eşit olduğu eşsiz pozitif sayıdır:

```
       1 + √5
φ  =  ────────  ≈  1.6180339887498949...
          2
```

Doğada salyangoz kabuklarından galaksilere, sanat eserlerinden mimari tasarımlara kadar tekrar eden bu oran, projemizin merkezinde durur.

### 🔢 Fibonacci Dizisi ve Binet Formülü

Klasik özyineli tanım:

```
F(0) = 0,   F(1) = 1,   F(n) = F(n−1) + F(n−2)
```

İlk birkaç terim: `0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, ...`

Kapalı form (Binet formülü):

```
                φⁿ − ψⁿ                         1 − √5
F(n)  =  ─────────────── ,         ψ  =  ───────────  ≈ −0.6180...
                  √5                              2
```

Önemli özellik: ardışık iki Fibonacci'nin oranı altın orana yakınsar:

```
       F(n+1)
lim   ────────  =  φ
n→∞    F(n)
```

### 📐 Altın Açı (137.5077°)

Bir tam çemberi altın orana göre bölersek:

```
α  =  360°  ×  (1 − 1/φ)  ≈  137.5077640500378°
```

Bu açı **irrasyoneldir**; dolayısıyla peş peşe yerleştirilen tohumlar **hiçbir zaman aynı doğrultuya hizalanmaz**. Sonuç: optimum sıkışıklığa sahip, eşsiz bir spiral.

### 🕸️ Graf Modeli  G = (V, E, f, w)

| Bileşen | Anlamı |
|---|---|
| `V` | Düğüm (tohum) kümesi: `{v₀, v₁, ..., v_{n−1}}` |
| `E` | Yönlü kenar kümesi: `{(vᵢ, vᵢ₊₁) \| 0 ≤ i < n−1}` |
| `f: V → ℝ³` | Düğüm öznitelik fonksiyonu: `f(vᵢ) = (i, F(i), xᵢ, yᵢ)` |
| `w: E → ℝ` | Kenar ağırlığı: `w(vᵢ, vᵢ₊₁) = F(i+1) / F(i)` → φ |

### 🌀 Vogel Formülü (Tohum Yerleşimi)

Helmut Vogel (1979), ayçiçeği desenini şu basit kutupsal denklemle modelledi:

```
xᵢ  =  c · √i · cos(i · α)
yᵢ  =  c · √i · sin(i · α)
```

Burada `c` ölçek sabiti (projemizde `c = 4`), `α` altın açıdır. Yarıçapın √i ile büyümesi, **alan başına düşen tohum yoğunluğunu** sabit tutar.

---

## 📁 Proje Yapısı

Proje **9 ayrı modül** halinde, sorumlulukları net ayrılmış biçimde organize edilmiştir:

| 📄 Dosya | 🎯 Sorumluluk |
|---|---|
| `fibonacci.py` | İteratif Fibonacci dizisi üretimi, tek değer hesabı, büyük sayı bilimsel notasyon biçimleyici |
| `utils.py` | Altın oran/açı sabitleri, ardışık oran, \|oran−φ\| farkı, Öklid mesafesi |
| `positioning.py` | Vogel formülünü uygulayıp tohum koordinatlarını üretir (`c=4` ölçek) |
| `graph_builder.py` | NetworkX `DiGraph` inşası — düğüm öznitelikleri ve `agirlik = F(i+1)/F(i)` kenarları |
| `validator.py` | Bir sayının Fibonacci olup olmadığını test eder (matematiksel + dizide arama), en yakın iki Fibonacci'yi bulur |
| `visualizer.py` | matplotlib ile statik spiral çizimi (koyu yeşil arka plan, sarı tohumlar) |
| `animator.py` | `FuncAnimation` ile tohum-tohum yerleştirme; aktif/ziyaret/bekleme renk durumları |
| `gui.py` | tkinter arayüzü: kontroller, canvas, canlı bilgi paneli |
| `main.py` | Tüm modülleri birleştiren giriş noktası |
| `requirements.txt` | Bağımlılık listesi |

---

## ⚙️ Kurulum

### 🐍 1. Önkoşul: Python 3.13+

Sisteminizde Python 3.13 veya üzeri kurulu olmalıdır:

```bash
python --version
# Python 3.13.x bekleniyor
```

Yoksa: <https://www.python.org/downloads/> adresinden indirin.

### 📦 2. Bağımlılıkların Kurulumu

```bash
pip install matplotlib networkx numpy pillow
```

ya da `requirements.txt` üzerinden:

```bash
pip install -r requirements.txt
```

> 💡 `tkinter` Windows ve macOS için Python ile birlikte gelir. Linux'ta gerekirse: `sudo apt install python3-tk`.

### ▶️ 3. Çalıştırma

```bash
python main.py
```

GUI penceresi açılınca **Çiz** butonuna basarak spirali izleyebilirsiniz.

---

## 🎮 Kullanım

### 🎚️ n Kaydırıcısı

Çizilecek tohum sayısını belirler. Aralık: **50 – 2000**. Yanındaki **Entry kutusuna** elle de değer girilebilir (örneğin `1000` yazıp Enter'a basın); kaydırıcı ile çift yönlü senkronize olur.

| n değeri | Beklenen görünüm |
|---|---|
| 50–100 | Genç ayçiçeği — belirgin 13 ↔ 21 spiraller |
| 100–300 | Olgun ayçiçeği — 21 ↔ 34 / 34 ↔ 55 |
| 500+ | Yoğun, gerçekçi ayçiçeği başı |

### 🔄 Açı (Altın Açı: 137.5077°)

Spiralin sırrı **tek bir sayıda**: altın açı. Mevcut sürümde değer **sabit** tutulmuştur (`utils.ALTIN_ACI_DERECE = 137.5077640500378`) çünkü bu açıdan **en ufak sapma bile** spiraldeki sıkı paketlemeyi bozar:

| Açı | Sonuç |
|---|---|
| 137.5° (irrasyonel) | ✅ Optimum spiral, çakışma yok |
| 137.0° / 138.0° | ❌ Gözle görülür "boşluklar" oluşur |
| 90° / 60° / 45° | ❌ Hizalı ışınlar, spiral kaybolur |

> 💡 Açının önemini denemek için `utils.py` içindeki `ALTIN_ACI_DERECE` değerini geçici olarak değiştirip yeniden çalıştırabilirsiniz.

### 🔎 Validator

Sol paneldeki **Validator** kutusuna bir tam sayı girip **Doğrula**'ya basın:

| Giriş | Sonuç | Etki |
|---|---|---|
| `21` | `Accept: v8 düğümü` | İlgili tohum **mavi** vurgulanır |
| `34` | `Accept: v9 düğümü` | İlgili tohum **mavi** vurgulanır |
| `89` | `Accept: v11 düğümü` | İlgili tohum **mavi** vurgulanır |
| `22` | `Reject — en yakın: 21, 34` | Vurgu yok, en yakın iki Fibonacci yazılır |
| `100` | `Reject — en yakın: 89, 144` | Vurgu yok |

### ⚡ Animasyon Hızı

| Seçenek | Aralık |
|---|---|
| 🐢 **Yavaş** | 500 ms / kare |
| 🚶 **Normal** | 200 ms / kare |
| 🏃 **Hızlı** | 50 ms / kare |
| ⚡ **Anında** | Tüm tohumları tek karede çiz |

---

## 📊 Simülasyon Özellikleri

### 🌀 Spiral Kol Sayıları

Ayçiçeğindeki **görünür spiral kollar** (saat yönünde ve tersi) her zaman **ardışık iki Fibonacci sayısıdır**:

| n aralığı | Saat yönü | Saat tersi |
|---|---|---|
| ~50 – 120 | **13** | **21** |
| ~120 – 250 | **21** | **34** |
| ~250 – 500 | **34** | **55** |
| ~500 – 1000 | **55** | **89** |
| 1000+ | **89** | **144** |

### 📈 Yakınsama Tablosu  (F(n+1)/F(n) → φ)

`φ ≈ 1.6180339887498949`

| n | F(n) | F(n+1) | F(n+1) / F(n) | \|oran − φ\| |
|---:|---:|---:|---:|---:|
| 5 | 5 | 8 | 1.6000000000000000 | **1.803 × 10⁻²** |
| 10 | 55 | 89 | 1.6181818181818182 | **1.478 × 10⁻⁴** |
| 15 | 610 | 987 | 1.6180327868852460 | **1.202 × 10⁻⁶** |
| 20 | 6 765 | 10 946 | 1.6180339985218033 | **9.772 × 10⁻⁹** |
| 30 | 832 040 | 1 346 269 | 1.6180339887505408 | **6.459 × 10⁻¹³** |

> Yakınsama hızı **üstel**: her yeni terimde fark yaklaşık `1/φ²` katı küçülür.

### ⏱️ Performans Tablosu

(Intel/AMD masaüstü, Python 3.13.x — `fibonacci_dizisi` + `grafi_olustur` + `tum_konumlar` toplam süresi)

| n | Süre (ms) | Düğüm | Kenar |
|---:|---:|---:|---:|
| 100 | 0.45 | 100 | 99 |
| 200 | 0.54 | 200 | 199 |
| 500 | 1.06 | 500 | 499 |
| 1000 | 2.17 | 1000 | 999 |
| 2000 | 4.51 | 2000 | 1999 |

> Çizim/animasyon süresine matplotlib yeniden çizim maliyeti eklenir; n=2000'de bile tamamlama 1 saniyenin altındadır.

---

## 🔬 Algoritma Karmaşıklığı

| 🧩 İşlem | ⏱️ Karmaşıklık | 📝 Not |
|---|---|---|
| Fibonacci dizisi üretimi | **O(n)** | İteratif, sabit ek bellek |
| Tohum konum hesabı (Vogel) | **O(n)** | Her i için sabit zamanlı `cos`, `sin` |
| Graf inşası (V, E ekleme) | **O(n)** | NetworkX hash-tabanlı sözlük |
| Animasyon (yeniden çizim) | **O(n²)** | Her karede biriken tohumlar yeniden boyanır |
| Validator (Fibonacci testi) | **O(log n)** | `5x²±4` tam kare testi (`isqrt`) |
| En yakın iki Fibonacci | **O(n)** | Sıralı dizide tek taramayla |

---

## 📚 Kaynakça

1. **Vogel, H.** (1979). *A better way to construct the sunflower head.* Mathematical Biosciences, **44**(3-4), 179–189.
2. **Rosen, K. H.** (2019). *Discrete Mathematics and Its Applications* (8th ed.). McGraw-Hill Education.
3. **Knuth, D. E.** (1997). *The Art of Computer Programming, Volume 1: Fundamental Algorithms* (3rd ed.). Addison-Wesley.
4. **Livio, M.** (2002). *The Golden Ratio: The Story of Phi, the World's Most Astonishing Number.* Broadway Books.
5. **Hagberg, A. A., Schult, D. A., & Swart, P. J.** (2008). *Exploring network structure, dynamics, and function using NetworkX.* Proceedings of the 7th Python in Science Conference (SciPy2008), 11–15.
6. **Hunter, J. D.** (2007). *Matplotlib: A 2D graphics environment.* Computing in Science & Engineering, **9**(3), 90–95.
7. **Mitchison, G. J.** (1977). *Phyllotaxis and the Fibonacci series.* Science, **196**(4287), 270–275.
8. **Jean, R. V.** (1994). *Phyllotaxis: A Systemic Study in Plant Morphogenesis.* Cambridge University Press.
9. **Stewart, I.** (1995). *Nature's Numbers: The Unreal Reality of Mathematics.* Basic Books.
10. **Adam, J. A.** (2011). *Mathematics in Nature: Modeling Patterns in the Natural World.* Princeton University Press.

---

<p align="center">
  🌻 <b>İstanbul Gedik Üniversitesi — Ayrık Matematik Dönem Projesi</b> 🌻<br>
  <i>"Doğa'nın matematiksel şiirini koddan okuyabilmek..."</i>
</p>
