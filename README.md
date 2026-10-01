# 🌻 Ayçiçeği Spirali

### Fibonacci · Altın Oran · Vogel Modeli · Graf Teorisi

> Ayçiçeği başındaki tohum dizilimini **Fibonacci dizisi, altın açı, Vogel modeli ve yönlü graflar** üzerinden inceleyen; matematiksel kavramları etkileşimli görselleştirmelerle birleştiren PySide6 tabanlı bir masaüstü uygulaması.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph_Theory-4C72B0?style=flat-square)
![NumPy](https://img.shields.io/badge/NumPy-Numerical_Computing-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=flat-square)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

---

## 📌 Proje Hakkında

**Ayçiçeği Spirali**, doğadaki ayçiçeği tohumu dizilimlerini matematiksel ve algoritmik olarak incelemek amacıyla geliştirilmiş etkileşimli bir Python uygulamasıdır.

Tohumların konumları **Vogel formülü** kullanılarak hesaplanır. Altın açı yaklaşık **137.5077°** olarak kullanıldığında karakteristik spiral dağılım ortaya çıkar.

Proje yalnızca bu deseni çizmekle kalmaz; aynı zamanda:

- Fibonacci dizisinin altın orana yakınsamasını,
- altın açının spiral üzerindeki etkisini,
- tohumların yönlü graf olarak modellenmesini,
- Fibonacci oranlarının graf kenar ağırlıkları olarak kullanılmasını,
- ağırlıklı komşuluk matrisini,
- farklı açıların oluşturduğu desenleri,
- matematiksel modelin etkileşimli olarak incelenmesini

tek bir masaüstü uygulamasında bir araya getirir.

---

## ✨ Öne Çıkan Özellikler

- 🌻 **Vogel modeliyle spiral üretimi**
- 🌀 **Altın açı tabanlı tohum yerleşimi**
- 🔢 **Fibonacci dizisi ve sayı doğrulama**
- 📈 **`F(n+1) / F(n) → φ` yakınsama görselleştirmesi**
- 🕸️ **NetworkX ile yönlü graf modeli**
- 🔲 **Ağırlıklı komşuluk matrisi**
- ⚖️ **Farklı açıların yan yana karşılaştırılması**
- 🎞️ **Adım adım spiral animasyonu**
- 🔍 **Zoom, pan, hover ve tohum seçimi**
- 🧪 **pytest ve pytest-qt tabanlı test altyapısı**
- 🖥️ **PySide6 tabanlı etkileşimli masaüstü arayüzü**

---

## 🎯 Neden Bu Proje?

Fibonacci dizisi ve altın oran genellikle formüller ve sayısal örnekler üzerinden anlatılır. Ancak bu matematiksel yapıların geometrik desenlerle ilişkisini yalnızca formüllere bakarak anlamak her zaman kolay değildir.

Bu proje, soyut matematiksel kavramları **görsel, etkileşimli ve algoritmik bir modele** dönüştürmek amacıyla geliştirildi.

Temel hedef yalnızca güzel bir spiral çizmek değil; spiral yapının arkasındaki matematiği farklı açılardan incelemektir.

### 1. Soyut Matematiği Görselleştirmek

Kullanıcı tohum sayısını ve açıyı değiştirerek ortaya çıkan yapıyı doğrudan gözlemleyebilir.

Özellikle altın açıdan yapılan küçük değişikliklerin spiral düzeni üzerindeki etkisi, matematiksel bir parametrenin geometrik sonucu olarak etkileşimli biçimde incelenebilir.

### 2. Fibonacci ve Altın Oran İlişkisini İncelemek

Ardışık Fibonacci sayılarının oranı:

```text
F(n+1) / F(n)
```

terimler büyüdükçe altın orana yaklaşır:

```text
φ ≈ 1.6180339887
```

Uygulamadaki yakınsama grafiği bu davranışın görsel olarak incelenmesini sağlar.

### 3. Geometriyi Graf Teorisiyle Birleştirmek

Projede her tohum aynı zamanda bir **graf düğümü (vertex)** olarak temsil edilir.

Ardışık tohumlar arasında yönlü kenarlar oluşturulur ve Fibonacci oranları bu kenarların ağırlıkları olarak kullanılabilir.

Böylece aynı sistem hem geometrik hem de graf-teorik açıdan incelenebilir.

### 4. Matematiksel Modeli Etkileşimli Hale Getirmek

PySide6 tabanlı masaüstü arayüzü sayesinde kullanıcı:

- tohum sayısını değiştirebilir,
- spiral açısını değiştirebilir,
- spiral oluşumunu animasyon olarak izleyebilir,
- graf görünümüne geçebilir,
- düğümleri inceleyebilir,
- komşuluk matrisini görüntüleyebilir,
- Fibonacci sayılarını doğrulayabilir,
- yakınsama grafiğini inceleyebilir,
- farklı açıları yan yana karşılaştırabilir.

---

# 🧮 Matematiksel Arka Plan

## Altın Oran — φ

Altın oran:

```text
       1 + √5
φ  =  ────────
          2
```

yaklaşık olarak:

```text
φ ≈ 1.6180339887498949
```

değerine sahiptir.

---

## Fibonacci Dizisi

Fibonacci dizisi:

```text
F(0) = 0
F(1) = 1
F(n) = F(n−1) + F(n−2)
```

şeklinde tanımlanır.

İlk terimler:

```text
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...
```

Ardışık Fibonacci sayılarının oranı:

```text
F(n+1)
──────
 F(n)
```

`n` büyüdükçe altın orana yaklaşır:

```text
        F(n+1)
lim     ────── = φ
n → ∞    F(n)
```

---

## 🌀 Altın Açı

Altın açı şu şekilde hesaplanabilir:

```text
α = 360° × (1 − 1/φ)
```

Yaklaşık değeri:

```text
α ≈ 137.507764°
```

Bu açı Vogel modelindeki tohumların açısal dağılımında kullanılır.

---

## 🌻 Vogel Formülü

Her tohumun konumu:

```text
xᵢ = c · √i · cos(i · α)
yᵢ = c · √i · sin(i · α)
```

formülüyle hesaplanır.

Burada:

| Değişken | Açıklama |
|---|---|
| `i` | Tohum indeksi |
| `c` | Ölçekleme sabiti |
| `α` | Tohumlar arasındaki açı |
| `√i` | Merkezden radyal uzaklığın büyümesi |
| `xᵢ, yᵢ` | Tohumun koordinatları |

`√i` kullanımı, noktaların merkezden uzaklaşırken alan üzerinde daha dengeli dağılmasına yardımcı olur.

---

# 🕸️ Graf Teorisi Modeli

Spiral yalnızca geometrik bir şekil olarak değil, aynı zamanda yönlü bir graf olarak modellenir.

```text
G = (V, E)
```

### Düğüm Kümesi

```text
V = {v₀, v₁, ..., vₙ₋₁}
```

Her düğüm bir tohumu temsil eder.

Düğüm üzerinde:

```text
f(vᵢ) = (i, F(i), xᵢ, yᵢ)
```

bilgileri tutulabilir.

Bunlar:

- tohum indeksi,
- Fibonacci değeri,
- x koordinatı,
- y koordinatıdır.

### Kenarlar

Ardışık tohumlar arasında yönlü kenarlar oluşturulur:

```text
E = {(vᵢ, vᵢ₊₁)}
```

Böylece:

```text
v₀ → v₁ → v₂ → v₃ → ... → vₙ
```

şeklinde yönlü bir yapı elde edilir.

### Kenar Ağırlıkları

Kenar ağırlığı:

```text
                F(i+1)
w(vᵢ,vᵢ₊₁) = ─────────
                 F(i)
```

olarak tanımlanır.

`i` büyüdükçe:

```text
w → φ
```

davranışı gözlemlenir.

Graf yapısı **NetworkX `DiGraph`** kullanılarak oluşturulur.

---

# 🖥️ Etkileşimli Arayüz

Uygulamanın güncel arayüzü **PySide6 / Qt6** kullanılarak geliştirilmiştir.

Ana ekran üzerinde:

```text
[ n ] [ α ] [ Çiz ]
        │
        ├── ▶ Animasyon
        ├── Hız
        ├── Graf
        └── Görselleştir
```

kontrolleri bulunur.

---

## 🎛️ Ana Kontroller

| Kontrol | İşlev |
|---|---|
| **n** | Çizilecek tohum sayısını belirler |
| **α** | Spiral oluşturulurken kullanılacak açıyı belirler |
| **Çiz** | Mevcut parametrelerle spirali yeniden oluşturur |
| **Animasyon** | Tohumları sırayla yerleştirir |
| **Hız** | Animasyon hızını değiştirir |
| **Graf** | Graf teorisi araçlarını açar |
| **Görselleştir** | Matematiksel analiz pencerelerini açar |

Tohum sayısı yaklaşık:

```text
50 – 2000
```

arasında ayarlanabilir.

---

# 🎞️ Spiral Animasyonu

Spiral tek seferde çizilmek yerine tohumların sırayla eklenmesiyle animasyon olarak da görüntülenebilir.

Desteklenen hız seçenekleri:

| Mod | Yaklaşık Gecikme |
|---|---:|
| Yavaş | 500 ms |
| Normal | 200 ms |
| Hızlı | 50 ms |
| Anında | Tek kare |

Animasyon sırasında hız değiştirilebilir.

---

# 🔍 Spiral Etkileşimleri

Ana spiral üzerinde çeşitli etkileşimler desteklenir.

| Etkileşim | Sonuç |
|---|---|
| Mouse Scroll | Zoom |
| Sol tık + sürükle | Pan |
| Tohuma tıklama | Tohum bilgilerini görüntüleme |
| Hover | Tohum bilgisini canlı güncelleme |

---

# ℹ️ Bilgi Kartı

Spiral üzerinde seçilen veya üzerine gelinen tohum hakkında bilgiler gösterilir.

Bilgi kartında:

- tohum indeksi,
- Fibonacci değeri,
- Fibonacci oranı,
- altın orandan sapma

gibi bilgiler görüntülenebilir.

---

# 🕸️ Graf Görünümü

Graf görünümü etkinleştirildiğinde spiral aynı zamanda yönlü graf olarak görselleştirilir.

Graf üzerinde:

- düğümler,
- yönlü kenarlar,
- Fibonacci tohumları,
- kenar ağırlıkları

görüntülenebilir.

Fibonacci ile ilişkili düğümler diğer düğümlerden görsel olarak ayrılır.

Düğüm ve kenarlar üzerinde hover ile ek bilgiler görüntülenebilir.

---

# 🔲 Komşuluk Matrisi

Graf yapısı ağırlıklı bir komşuluk matrisi üzerinden de incelenebilir.

Matris:

```text
Aᵢⱼ = w(vᵢ,vⱼ)
```

şeklinde tanımlanır.

Graf yönlü ve ardışık düğümlerden oluştuğu için matris seyrek bir yapı gösterir.

Bu özellik geometrik spiral ile graf teorisi arasındaki ilişkinin sayısal olarak incelenmesini sağlar.

---

# ✅ Fibonacci Doğrulayıcı

Uygulama, girilen bir tam sayının Fibonacci dizisine ait olup olmadığını kontrol edebilir.

Doğrulama sırasında matematiksel Fibonacci testi kullanılabilir:

```text
5x² + 4
```

veya:

```text
5x² - 4
```

ifadelerinden en az biri tam kare ise `x` bir Fibonacci sayısıdır.

Fibonacci olmayan değerler için en yakın Fibonacci değerleri de gösterilebilir.

---

# 📈 Yakınsama Grafiği

Uygulama:

```text
F(n+1) / F(n)
```

oranının `φ` değerine yaklaşmasını ayrı bir grafik üzerinde gösterebilir.

Ayrıca hata:

```text
|F(n+1) / F(n) − φ|
```

şeklinde hesaplanarak yakınsama davranışı incelenebilir.

---

# ⚖️ Açı Karşılaştırma

Farklı açılar kullanıldığında oluşan tohum dağılımları yan yana karşılaştırılabilir.

Örnek karşılaştırmalar:

```text
137.5° vs 90°
137.5° vs 137.0°
137.5° vs 60°
```

Bu özellik açısal parametrenin spiral üzerindeki etkisinin doğrudan gözlemlenmesini sağlar.

---

# 📊 Sayısal Yakınsama

Altın oran:

```text
φ ≈ 1.6180339887498949
```

Bazı Fibonacci oranları:

| n | F(n) | F(n+1) | F(n+1) / F(n) | `|oran − φ|` |
|---:|---:|---:|---:|---:|
| 5 | 5 | 8 | 1.6000000000000000 | 1.803 × 10⁻² |
| 10 | 55 | 89 | 1.6181818181818182 | 1.478 × 10⁻⁴ |
| 15 | 610 | 987 | 1.6180327868852460 | 1.202 × 10⁻⁶ |
| 20 | 6,765 | 10,946 | 1.6180339985218033 | 9.772 × 10⁻⁹ |
| 30 | 832,040 | 1,346,269 | 1.6180339887505408 | 6.459 × 10⁻¹³ |

Bu tablo ardışık Fibonacci oranlarının altın orana hızlı biçimde yakınsadığını gösterir.

---

# ⚙️ Algoritmalar ve Karmaşıklık

Projede kullanılan temel işlemlerin yaklaşık karmaşıklıkları:

| İşlem | Karmaşıklık | Açıklama |
|---|---|---|
| Fibonacci dizisi üretimi | `O(n)` | İteratif üretim |
| Vogel koordinatlarının hesaplanması | `O(n)` | Her tohum için koordinat hesabı |
| Graf oluşturma | `O(n)` | Düğüm ve ardışık kenarların oluşturulması |
| Fibonacci üyelik testi | Sayının büyüklüğüne bağlı | Tam kare kontrolüne dayalı |
| Yakın Fibonacci arama | `O(n)` | Üretilen dizi üzerinde arama |

---

# 🏗️ Yazılım Mimarisi

Proje iki temel katmana ayrılır:

```text
┌─────────────────────────────┐
│       PySide6 UI Layer      │
│                             │
│  Main Window                │
│  Spiral Canvas              │
│  Info Card                  │
│  Analysis Windows           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Mathematical Domain     │
│                             │
│  Fibonacci                  │
│  Vogel Positioning          │
│  Graph Builder              │
│  Validator                  │
│  Graph Traversal            │
└─────────────────────────────┘
```

Bu ayrım matematiksel çekirdeğin kullanıcı arayüzünden bağımsız olarak test edilebilmesini kolaylaştırır.

---

# 📁 Proje Yapısı

## Matematiksel Çekirdek

| Dosya | Sorumluluk |
|---|---|
| `fibonacci.py` | Fibonacci dizisi ve tek değer hesaplamaları |
| `utils.py` | φ, altın açı, oran ve matematiksel yardımcı fonksiyonlar |
| `positioning.py` | Vogel formülü ile koordinat üretimi |
| `graph_builder.py` | NetworkX `DiGraph` oluşturulması |
| `validator.py` | Fibonacci doğrulama işlemleri |
| `graph_traversal.py` | Graf dolaşma algoritmaları |

---

## PySide6 Arayüzü

```text
ui/
├── app.py
├── theme.py
├── main_window.py
├── top_bar.py
├── spiral_canvas.py
├── info_card.py
└── windows/
    ├── base.py
    ├── fibonacci_validator.py
    ├── convergence.py
    ├── comparison.py
    └── adjacency_matrix.py
```

### Temel UI Bileşenleri

| Dosya | Sorumluluk |
|---|---|
| `ui/app.py` | QApplication ve uygulama başlangıcı |
| `ui/theme.py` | Tema ve Qt stylesheet |
| `ui/main_window.py` | Ana pencere |
| `ui/top_bar.py` | Kontrol çubuğu |
| `ui/spiral_canvas.py` | Spiral çizimi ve etkileşim |
| `ui/info_card.py` | Tohum ve oran bilgileri |
| `ui/windows/convergence.py` | Yakınsama grafiği |
| `ui/windows/comparison.py` | Açı karşılaştırması |
| `ui/windows/adjacency_matrix.py` | Komşuluk matrisi |
| `ui/windows/fibonacci_validator.py` | Fibonacci doğrulayıcı |

---

# 🧪 Test Altyapısı

Projede hem matematiksel çekirdek hem de kullanıcı arayüzü için testler bulunmaktadır.

Kullanılan araçlar:

- **pytest**
- **pytest-qt**
- Python `unittest`

Testler arasında:

- Fibonacci hesaplamaları,
- matematiksel yardımcı fonksiyonlar,
- validator,
- graf işlemleri,
- PySide6 pencereleri,
- UI davranışları

yer alır.

Testleri çalıştırmak için:

```bash
pytest -v
```

---

# 🧰 Teknoloji Yığını

| Teknoloji | Kullanım |
|---|---|
| Python | Ana programlama dili |
| PySide6 / Qt6 | Masaüstü kullanıcı arayüzü |
| NetworkX | Graf modelleme |
| NumPy | Sayısal işlemler |
| Matplotlib | Matematiksel görselleştirme |
| SciPy | Ek bilimsel hesaplama desteği |
| pytest | Birim testleri |
| pytest-qt | PySide6 UI testleri |

---

# 🚀 Kurulum

## Gereksinimler

Proje Python **3.13+** ile geliştirilmiştir.

Python sürümünü kontrol etmek için:

```bash
python --version
```

---

## 1. Repoyu Klonlayın

```bash
git clone https://github.com/fatihemreyuce/aycicegi-spirali.git
cd aycicegi-spirali
```

---

## 2. Sanal Ortam Oluşturun

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

Temel bağımlılıklar:

```text
matplotlib
networkx
numpy
scipy
PySide6
pytest
pytest-qt
```

---

## 4. Uygulamayı Çalıştırın

```bash
python main.py
```

Uygulama PySide6 tabanlı masaüstü arayüzüyle açılacaktır.

---

# 🧪 Testleri Çalıştırma

```bash
pytest -v
```

UI testlerinde `pytest-qt` kullanılmaktadır.

---

# 🕰️ Legacy Arayüz

Projenin PySide6 öncesindeki eski Tkinter tabanlı arayüzü de korunmaktadır.

Çalıştırmak için:

```bash
python main_legacy.py
```

Legacy sürüm, projenin geliştirme sürecindeki önceki arayüz yaklaşımını incelemek için kullanılabilir.

---

# 🔬 Projenin İncelediği Temel İlişki

Projenin merkezindeki akış özetle şöyledir:

```text
Fibonacci Dizisi
       │
       ▼
Ardışık Fibonacci Oranları
       │
       ▼
     Altın Oran φ
       │
       ▼
     Altın Açı α
       │
       ▼
    Vogel Modeli
       │
       ▼
  Tohum Koordinatları
       │
       ├───────────────┐
       ▼               ▼
Spiral Görünümü    Graf Modeli
                       │
                       ▼
              NetworkX DiGraph
                       │
                       ▼
              Komşuluk Matrisi
```

Böylece sayı dizileri, geometri, graf teorisi ve yazılım görselleştirmesi tek bir model içerisinde bir araya getirilir.

---

# 🎓 Akademik Bağlam

Bu proje **İstanbul Gedik Üniversitesi Ayrık Matematik dersi dönem projesi** kapsamında geliştirilmiştir.

## 👥 Grup Üyeleri

| Ad Soyad | Öğrenci No |
|---|---:|
| Fatih Emre Yüce | 241046016 |
| Ramazan Türkyılmaz | 241041094 |
| Kaan Sarı | 241046012 |
| Talha Akarçeşme | 241046005 |

**Danışman:** Dr. Öğr. Üyesi Fatma Zehra Uzemek

---

# 📚 Kaynakça

Projenin matematiksel ve teknik temelleri için yararlanılan başlıca kaynaklar:

1. Vogel, H. (1979). *A Better Way to Construct the Sunflower Head*. Mathematical Biosciences, 44(3–4), 179–189.
2. Rosen, K. H. (2019). *Discrete Mathematics and Its Applications* (8th ed.). McGraw-Hill Education.
3. Knuth, D. E. (1997). *The Art of Computer Programming, Volume 1*. Addison-Wesley.
4. Livio, M. (2002). *The Golden Ratio: The Story of Phi*. Broadway Books.
5. Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). *Exploring Network Structure, Dynamics, and Function using NetworkX*. Proceedings of SciPy 2008.

---

# 👤 Contributors

This project was developed collaboratively as an academic course project by:

- **Fatih Emre Yüce**
- **Ramazan Türkyılmaz**
- **Kaan Sarı**
- **Talha Akarçeşme**

---

## 🌻 Final Note

Ayçiçeği Spirali, Fibonacci dizisi, altın oran, Vogel modeli ve graf teorisi arasındaki ilişkileri yalnızca formüller üzerinden değil, **çalıştırılabilir ve etkileşimli bir yazılım modeli** üzerinden incelemeyi amaçlar.

Proje; matematiksel modelleme, algoritmalar, veri yapıları, masaüstü arayüz geliştirme ve bilimsel görselleştirme konularını aynı uygulama içerisinde bir araya getirir.
