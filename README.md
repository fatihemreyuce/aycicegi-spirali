# 🌻 Ayçiçeği Spirali — Fibonacci, Altın Oran ve Graflarla Bir Matematiksel İnceleme

> Doğanın en zarif geometrik desenlerinden birini — ayçiçeği başındaki tohum dizilimini — Fibonacci dizisi, altın açı (Vogel formülü) ve yönlü graflar üzerinden modelleyen, PySide6 tabanlı etkileşimli bir Python uygulaması.

![Python](https://img.shields.io/badge/python-3.13%2B-blue) ![Qt](https://img.shields.io/badge/Qt-PySide6-success) ![License](https://img.shields.io/badge/license-Eğitim-yellow) ![Status](https://img.shields.io/badge/proje-Dönem%20Projesi-blue)

---

## 📌 Bu Proje Nedir?

Bu, **ayçiçeği başındaki tohum dizilimini matematiksel olarak modelleyip görselleştiren** bir masaüstü uygulamadır. Tohumlar **Vogel formülü** ile yerleştirilir; ardışık tohumlar arasındaki açı sabit (altın açı ≈ 137.5077°) tutulduğunda, doğada gördüğümüz ile birebir aynı sıkı paketlenmiş spiral desen ortaya çıkar. Bu desen Fibonacci dizisinin altın orana yakınsamasıyla doğrudan ilişkilidir; uygulama bu ilişkiyi hem görsel hem de yapısal (graf modeli, yakınsama grafiği, komşuluk matrisi) olarak inceler.

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

## 🎯 Neden Bu Proje?

Çoğu kişi "altın oran" ile "Fibonacci dizisi"ni duymuştur ama bunların **neden** bir ayçiçeğinin başında karşımıza çıktığını sezgisel olarak görmek zordur. Bu projenin amacı:

1. **Soyut matematiği elle tutulur hâle getirmek.** Bir kaydırıcıyı oynatınca altın açının neden 137° değil de **tam olarak 137.5077°** olması gerektiği görsel olarak anlaşılır: 0.1°'lik bir sapma bile spiralin "bozulmasına" yol açar.
2. **Süreksiz matematiğin (Ayrık Matematik) gerçek hayata bağlanışını göstermek.** Tohumlar düğüm, komşuluklar yönlü kenar, kenar ağırlığı Fibonacci oranı olarak modellenir — yani fizikteki ve doğadaki bir desen tamamen bir grafa indirgenir. Komşuluk Matrisi ekranı bu eşlemeyi sayısal olarak da görünür kılar.
3. **Bir matematik teoreminin doğa ile tutarlılığını test etmek.** F(n+1) / F(n) → φ yakınsamasını canlı bir grafikte görmek; sonra aynı oranın spiraldeki kenarları nasıl φ'ye yakınlaştırdığını fark etmek — bunlar tek bir uygulama içinde birleşince eğitsel etkisi büyür.

---

## 🧮 Matematiksel Arka Plan (Özet)

### Altın Oran (φ)

```
       1 + √5
φ  =  ────────  ≈  1.6180339887498949...
          2
```

### Fibonacci Dizisi ve φ'ye Yakınsama

```
F(0)=0,  F(1)=1,  F(n) = F(n−1) + F(n−2)
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, ...

lim  F(n+1)/F(n)  =  φ        (n → ∞)
```

### Altın Açı (137.5077°)

```
α  =  360°  ×  (1 − 1/φ)  ≈  137.5077640500378°
```

Bu açı **irrasyoneldir** — peş peşe yerleştirilen tohumlar hiçbir zaman aynı doğrultuya hizalanmaz. Sonuç: hiçbir yönde "ışınsal boşluk" oluşmadan, alan başına maksimum tohum sıkışıklığı. Doğanın bu açıyı seçmesi tesadüf değil — milyonlarca yıllık evrimsel optimizasyondur.

### Vogel Formülü — Tohum Yerleşimi

```
xᵢ  =  c · √i · cos(i · α)
yᵢ  =  c · √i · sin(i · α)
```

`√i` ile büyüyen yarıçap, **alan başına düşen tohum yoğunluğunu** sabit tutar (eşit-alan kuralı).

### Graf Modeli  G = (V, E, f, w)

| Bileşen | Anlamı |
|---|---|
| `V` | Düğüm (tohum) kümesi: `{v₀, v₁, ..., v_{n−1}}` |
| `E` | Yönlü kenar kümesi: `{(vᵢ, vᵢ₊₁) \| 0 ≤ i < n−1}` |
| `f: V → ℝ⁴` | Düğüm özniteliği: `f(vᵢ) = (i, F(i), xᵢ, yᵢ)` |
| `w: E → ℝ` | Kenar ağırlığı: `w(vᵢ, vᵢ₊₁) = F(i+1) / F(i)`  → φ |

Tüm bu yapı NetworkX'in `DiGraph` sınıfı üzerine inşa edilmiştir; dolayısıyla projenin matematiksel modeli aynı zamanda **çalıştırılabilir bir veri yapısıdır**.

---

## 🌍 Günümüzde Nerede İşimize Yarar?

"Bir öğrenci projesi" olarak basit görünebilir; ama altın açıya dayalı paketleme ve Fibonacci tabanlı modelleme bugün **gerçek üretim mühendisliğinde** kullanılan tekniklerdir:

### 🌱 Biyomimikri & Tarım

- **Güneş tarlalarında panel dizilimi:** MIT'de 2011'de Aidan Dwyer'ın yaptığı ünlü deney, ayçiçeği spirali deseninde dizilmiş güneş panellerinin geleneksel dikey dizilime göre daha az alanda daha yüksek verim verdiğini gösterdi. Geometrik prensip bu uygulamadakiyle aynıdır.
- **Tohum-ekim planlaması:** Hassas tarım sistemlerinde fide aralıklarını ışık ve su rekabetini en aza indirecek şekilde belirlerken Vogel-tipi dağılım baz alınır.

### 🏛️ Mimari & Tasarım

- **Cephe panel düzenleri:** Frank Lloyd Wright'tan modern parametrik mimariye (Zaha Hadid, Foster + Partners) kadar altın oran tabanlı modüler cephe paneli yerleşimi, hem estetik hem de strüktürel yük dağılımı için kullanılır.
- **Endüstriyel ürün tasarımı:** Kamera lens diyafram bıçakları, türbin kanat yerleşimi, mikrofon dizi düzeni — hepsi optimum açısal aralık için Fibonacci/golden-angle yaklaşımlarından yararlanır.

### 💻 Bilgisayar Bilimi

- **Veri görselleştirme:** Veri noktalarının çakışmadan görüntülendiği "sunflower plots" (R, ggplot2, Bokeh içinde bulunur) doğrudan bu desenden gelir.
- **Pseudo-random sampling:** Monte Carlo simülasyonlarında ve render motorlarında (örn. Cycles, Arnold) gürültü dağılımı için altın açı sampling'i tercih edilir — düzenli ızgaradan daha iyi kapsama sağlar.
- **Graf algoritmaları için referans yapı:** Bu projenin kendisi (spiral graf + Dijkstra ağırlıkları φ'ye yakınsar) algoritma derslerinde "deterministik ama önemsiz olmayan" bir test grafı olarak kullanılabilir.

### 🧬 Biyoloji & Tıp

- **Phyllotaxis modelleme:** Bitki dallanma desenlerini tahmin eden modeller (Mitchison 1977, Jean 1994) bu projedeki Vogel formülünün doğrudan türevidir. İlaç keşfinde bitkilerin yaprak rozet yapısını analiz ederken kullanılır.
- **Tıbbi görüntüleme:** Retina'daki koni hücreleri ve fundus damar dağılımı analizi sunflower deseni referansına dayanır.

### 🎨 Yaratıcı Endüstri

- **Generative art / NFT projeleri:** Phi-tabanlı kompozisyon kuralı modern jeneratif sanat eserlerinde temel bir yapıtaşıdır.
- **Oyun haritası prosedürel üretimi:** Düz ızgara yerine altın açı dağılımı ile yerleştirilen kaynaklar/düşmanlar oyunculara daha "organik" hissettirir.

> 💡 **Özetle:** Bu proje, "matematik niye okuyoruz?" sorusunun somut bir cevabı. Bir öğrencinin kavradığı altın açı, on yıl sonra bir güneş tarlasının verimliliğini, bir mimari cephenin dağılımını ya da bir bilimsel görselleştirmenin okunabilirliğini doğrudan etkileyebilir.

---

## ⚙️ Kurulum

### 🐍 1. Önkoşul: Python 3.13+

```bash
python --version
# Python 3.13.x bekleniyor
```

Yoksa: <https://www.python.org/downloads/>

### 📦 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

İçinde: `matplotlib`, `networkx`, `numpy`, `scipy`, `PySide6`, `pytest`, `pytest-qt`.

### ▶️ 3. Çalıştır

```bash
python main.py
```

Açılışta 1280×800 pencerede 100 tohumlu altın açı spirali görünür; Fibonacci indeksli tohumlar (1, 2, 3, 5, 8, 13, 21, 34, 55, 89) **kırmızı vurgu** alır.

### 🧪 4. Testler (opsiyonel)

```bash
pytest -v
```

> Beklenen: 100+ test, hepsi yeşil.

> **Eski Tkinter arayüzü** (yedek): `python main_legacy.py`. PySide6 portu öncesi kapsamlı versiyondur; bazı eski analiz pencereleri (Algoritma menüsü) burada hâlâ mevcuttur.

---

## 🖱️ Arayüz Rehberi

### Üst Şerit (TopBar)

```
[ n ][ α ][ Çiz ] | [ ▶ Animasyon ][ Hız: Normal ▾ ] | [ Graf ▾ ][ Görselleştir ▾ ]
```

| Kontrol | İşlevi |
|---|---|
| **n** | Çizilecek tohum sayısı (50 – 2000). |
| **α** | Açı (°). Varsayılan 137.5077° (altın açı). 30°–180° arası kabul edilir. |
| **Çiz** | Mevcut n + α ile spirali yeniden çizer. Animasyon çalışıyorsa iptal edip anında tam spirali gösterir. |
| **▶ Animasyon** | Tohumları tek tek yerleştirerek spirali kurar. Hız combo ile canlı ayarlanır. |
| **Hız** | Yavaş (500ms) / Normal (200ms) / Hızlı (50ms) / Anında (tek karede). Animasyon sırasında bile canlı değişir. |

### Sağ-üst Bilgi Kartı (InfoCard)

Krem bir overlay olarak spiralin sağ-üst köşesinde durur. Her zaman:
- En son çizilen n için **F(k)** değeri
- **F(k) / F(k-1)** oranı ve bu oranın φ'den **|Δ|** sapması
- Mouse'un üzerinde olduğu **seçili tohum** indeksi

### Etkileşim (Spiral Üzerinde)

| Eylem | Sonuç |
|---|---|
| **Mouse scroll** | İmleç-merkezli zoom in / out |
| **Sol-tık + sürükle (boş alan)** | Pan — görünümü kaydır |
| **Sol-tık (tohum üstü, kısa)** | InfoCard'ta o tohumun indeksini göster |
| **Hover** | Aynı şekilde InfoCard'ı canlı günceller |

### Graf Menüsü

| Öğe | Ne Yapar |
|---|---|
| 🕸️ **Graf Görünümü** | Ana spirali **toggle ile** graf moduna çevirir: Fibonacci tohumları büyük + lacivert disk, diğerleri küçük + soluk gri. Yönlü kenarlar (v₀ → v₁ → ...) φ'ye yakınlığa göre **renk gradyanı** ile çizilir (yakın olanlar koyu lacivert, uzak olanlar soluk). Mouse hover ile düğüm/kenar tooltip'i (`v8 \| F = 21 \| konum`, `v7 → v8 \| w = 1.6250`). Menüye tekrar tıklamak modu kapatır. |
| 📊 **Komşuluk Matrisi** | Aᵢⱼ = w(vᵢ,vⱼ) — boyut 2–50 ayarlanabilir, scroll'lu QTableWidget. Spiral graf yönlü ve doğrusal olduğu için matris çoğunlukla seyrek; sadece diyagonalın hemen üstündeki köşede φ'ye yakın değerler. |
| ✅ **Fibonacci Doğrulayıcı** | Bir tam sayı yaz, "Doğrula" → Accept ise ilgili tohum ana spiralde **mavi vurgu** alır; Reject ise alt satırda en yakın iki Fibonacci verilir. |

### Görselleştir Menüsü

| Öğe | Ne Yapar |
|---|---|
| 📈 **Yakınsama Grafiği** | Ayrı pencerede iki alt-grafik: üstte F(i+1)/F(i) lacivert eğri + kesikli φ referansı; altta \|fark\| log-skala kırmızı eğri. Yakınsamanın üstel hızı somut olarak görünür. |
| ⚖️ **Açı Karşılaştırma** | İki açıyı yan yana çizer. 3 hazır preset: `137.5° vs 90°`, `137.5° vs 137.0°`, `137.5° vs 60°`. Altın açıdan en ufak sapmanın bile spirali nasıl bozduğunu görsel olarak kanıtlar. |

---

## 📁 Proje Yapısı

### Domain (matematiksel çekirdek)

| Dosya | Sorumluluk |
|---|---|
| `fibonacci.py` | İteratif Fibonacci üretimi + tek değer hesabı + büyük sayı bilimsel notasyon |
| `utils.py` | φ ve altın açı sabitleri, ardışık oran, \|oran−φ\| farkı, Öklid mesafesi |
| `positioning.py` | Vogel formülünü uygulayıp tohum koordinatlarını üretir (`c=4` ölçek) |
| `graph_builder.py` | NetworkX `DiGraph` inşası — düğüm öznitelikleri + `agirlik = F(i+1)/F(i)` |
| `validator.py` | Bir sayının Fibonacci olup olmadığını test eder (`5x²±4` tam kare yöntemi + dizide arama), en yakın iki Fibonacci'yi bulur |
| `graph_traversal.py` | BFS / DFS — undirected, kararlı sıralama (yedek `main_legacy.py` için) |

### Sunum (PySide6 UI)

| Dosya | Sorumluluk |
|---|---|
| `ui/app.py` | `QApplication` kurulumu + `main()` giriş noktası |
| `ui/theme.py` | Akademik aydınlık tema — renk paleti + global Qt stylesheet |
| `ui/main_window.py` | Ana pencere — TopBar + SpiralCanvas + InfoCard + menü yönetimi |
| `ui/top_bar.py` | n / α / Çiz / Animasyon / Hız + 2 menü düğmesi (Graf, Görselleştir) |
| `ui/spiral_canvas.py` | matplotlib qtagg canvas — spiral çizim, animasyon (QTimer), graf modu, zoom/pan, validator vurgu |
| `ui/info_card.py` | Sağ-üst overlay kart — F oranı, tohum bilgisi |
| `ui/windows/base.py` | `AnalyticsWindow` taban + `WindowManager` (tek-instance) |
| `ui/windows/fibonacci_validator.py` | Sayı doğrulayıcı + cross-window mavi vurgu sinyali |
| `ui/windows/convergence.py` | F(n+1)/F(n) → φ yakınsama grafiği |
| `ui/windows/comparison.py` | İki açıyı yan yana karşılaştırma |
| `ui/windows/adjacency_matrix.py` | QTableWidget tabanlı komşuluk matrisi |

### Test

| Dosya | Sorumluluk |
|---|---|
| `tests/test_fibonacci.py`, `test_utils.py`, `test_validator.py`, vb. | Domain birim testleri (unittest + pytest) |
| `tests/test_*_window.py`, `test_*.py` | UI testleri (pytest-qt) |
| `tests/conftest.py` | `QT_QPA_PLATFORM=offscreen` ayarı, qtbot fixture |

### Yedek

| Dosya | Sorumluluk |
|---|---|
| `main_legacy.py` | Eski Tkinter arayüzünü başlatır (BFS/DFS, Dijkstra, Tohum Seçimi gibi PySide6'da kaldırılan pencereler bunda hâlâ var) |
| `gui.py`, `animator.py`, `*_window.py` (eski) | Tkinter çağındaki kod — silinmedi, geri-dönüş yolu olarak korunuyor |

---

## 📊 Bazı Sayısal Olgular

### Yakınsama Tablosu (F(n+1)/F(n) → φ)

`φ ≈ 1.6180339887498949`

| n | F(n) | F(n+1) | F(n+1) / F(n) | \|oran − φ\| |
|---:|---:|---:|---:|---:|
| 5 | 5 | 8 | 1.6000000000000000 | **1.803 × 10⁻²** |
| 10 | 55 | 89 | 1.6181818181818182 | **1.478 × 10⁻⁴** |
| 15 | 610 | 987 | 1.6180327868852460 | **1.202 × 10⁻⁶** |
| 20 | 6 765 | 10 946 | 1.6180339985218033 | **9.772 × 10⁻⁹** |
| 30 | 832 040 | 1 346 269 | 1.6180339887505408 | **6.459 × 10⁻¹³** |

Her yeni terimde fark yaklaşık `1/φ²` katı küçülür — **üstel yakınsama**.

### Görünür Spiral Kol Sayıları

Ayçiçeğindeki spiral kollar (saat yönü / saat tersi) **her zaman ardışık iki Fibonacci sayısıdır**:

| n aralığı | Saat yönü | Saat tersi |
|---|---|---|
| ~50 – 120 | **13** | **21** |
| ~120 – 250 | **21** | **34** |
| ~250 – 500 | **34** | **55** |
| ~500 – 1000 | **55** | **89** |
| 1000+ | **89** | **144** |

### Algoritma Karmaşıklığı

| İşlem | Karmaşıklık | Not |
|---|---|---|
| Fibonacci dizisi üretimi | **O(n)** | İteratif, sabit ek bellek |
| Vogel tohum konumları | **O(n)** | Her i için sabit zamanlı cos/sin |
| Graf inşası (V, E) | **O(n)** | NetworkX hash-tabanlı |
| Validator (Fibonacci testi) | **O(log n)** | `5x²±4` tam kare testi |
| En yakın iki Fibonacci | **O(n)** | Sıralı dizide tek tarama |

---

## 📚 Kaynakça

1. **Vogel, H.** (1979). *A better way to construct the sunflower head.* Mathematical Biosciences, **44**(3-4), 179–189.
2. **Rosen, K. H.** (2019). *Discrete Mathematics and Its Applications* (8th ed.). McGraw-Hill Education.
3. **Knuth, D. E.** (1997). *The Art of Computer Programming, Volume 1.* Addison-Wesley.
4. **Livio, M.** (2002). *The Golden Ratio: The Story of Phi.* Broadway Books.
5. **Hagberg, A. A., Schult, D. A., & Swart, P. J.** (2008). *Exploring network structure with NetworkX.* SciPy2008 Proceedings, 11–15.
6. **Hunter, J. D.** (2007). *Matplotlib: A 2D graphics environment.* Computing in Science & Engineering, **9**(3), 90–95.
7. **Mitchison, G. J.** (1977). *Phyllotaxis and the Fibonacci series.* Science, **196**(4287), 270–275.
8. **Jean, R. V.** (1994). *Phyllotaxis: A Systemic Study in Plant Morphogenesis.* Cambridge University Press.
9. **Adam, J. A.** (2011). *Mathematics in Nature.* Princeton University Press.
10. **Dwyer, A.** (2011). *The Secret of the Fibonacci Sequence in Trees.* American Museum of Natural History — Young Naturalist Awards.

---

<p align="center">
  🌻 <b>İstanbul Gedik Üniversitesi — Ayrık Matematik Dönem Projesi</b> 🌻<br>
  <i>"Doğa'nın matematiksel şiirini koddan okuyabilmek..."</i>
</p>
