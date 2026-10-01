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

Ayçiçeği Spirali, doğadaki **phyllotaxis** düzenini matematiksel ve algoritmik olarak incelemek amacıyla geliştirilmiş etkileşimli bir Python uygulamasıdır.

Tohumların konumları **Vogel formülü** kullanılarak hesaplanır. Altın açı yaklaşık **137.5077°** olarak kullanıldığında karakteristik ayçiçeği spiral yapısı ortaya çıkar.

Proje yalnızca bu deseni çizmekle kalmaz; aynı zamanda:

- Fibonacci dizisinin altın orana yakınsamasını,
- altın açının spiral üzerindeki etkisini,
- tohumların yönlü graf olarak modellenmesini,
- Fibonacci oranlarının kenar ağırlıkları olarak kullanılmasını,
- komşuluk matrisini,
- farklı açıların oluşturduğu desenleri,
- matematiksel modelin etkileşimli olarak incelenmesini

tek bir masaüstü uygulamasında bir araya getirir.

---

## ✨ Öne Çıkan Özellikler

- 🌻 **Vogel modeliyle spiral üretimi**
- 🌀 **Altın açı tabanlı tohum yerleşimi**
- 🔢 **Fibonacci dizisi ve sayı doğrulama**
- 📈 **F(n+1) / F(n) → φ yakınsama görselleştirmesi**
- 🕸️ **NetworkX ile yönlü graf modeli**
- 🔲 **Ağırlıklı komşuluk matrisi**
- ⚖️ **Farklı açıların yan yana karşılaştırılması**
- 🎞️ **Adım adım spiral animasyonu**
- 🔍 **Zoom, pan, hover ve tohum seçimi**
- 🧪 **pytest ve pytest-qt tabanlı test altyapısı**

---

## 🧠 Projenin Temel Fikri

Projenin merkezinde üç matematiksel yapı bulunur:

### 1. Fibonacci Dizisi

```text
F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2)
```

Ardışık Fibonacci sayılarının oranı büyüdükçe altın orana yaklaşır:

```text
F(n+1)
────── → φ
 F(n)
```

### 2. Altın Açı

Altın oran:

```text
        1 + √5
φ = ───────────── ≈ 1.6180339887
           2
```

Altın açı ise:

```text
α = 360° × (1 - 1/φ)

α ≈ 137.507764°
```

### 3. Vogel Modeli

Her tohumun spiral üzerindeki konumu:

```text
xᵢ = c · √i · cos(i · α)
yᵢ = c · √i · sin(i · α)
```

formülüyle hesaplanır.

`√i` terimi tohumların merkezden uzaklaşmasını sağlarken, `i · α` terimi her yeni tohumu belirli bir açısal dönüşle konumlandırır.

Bu yapı sayesinde matematiksel model doğrudan etkileşimli bir görselleştirmeye dönüştürülür.

---

## 🕸️ Graf Teorisi Modeli

Spiral yalnızca geometrik bir şekil olarak değil, aynı zamanda yönlü bir graf olarak modellenir:

```text
G = (V, E)
```

Burada:

| Bileşen | Açıklama |
|---|---|
| `V` | Tohumları temsil eden düğümler |
| `E` | Ardışık tohumlar arasındaki yönlü kenarlar |
| `f(vᵢ)` | Tohumun indeks, Fibonacci değeri ve koordinat bilgileri |
| `w(vᵢ,vᵢ₊₁)` | Ardışık Fibonacci değerlerinin oranı |

Kenar ağırlığı:

```text
                F(i+1)
w(vᵢ,vᵢ₊₁) = ─────────
                 F(i)
```

şeklinde tanımlanır.

`i` büyüdükçe bu ağırlık:

```text
w → φ
```

davranışı gösterir.

Graf yapısı **NetworkX `DiGraph`** kullanılarak oluşturulur. Böylece görsel spiral aynı zamanda üzerinde analiz yapılabilen gerçek bir graf veri yapısına dönüşür.

---

## 🎓 Akademik Bağlam

Bu proje **İstanbul Gedik Üniversitesi Ayrık Matematik dersi dönem projesi** kapsamında geliştirilmiştir.

### 👥 Grup Üyeleri

| Ad Soyad | Öğrenci No |
|---|---:|
| Fatih Emre Yüce | 241046016 |
| Ramazan Türkyılmaz | 241041094 |
| Kaan Sarı | 241046012 |
| Talha Akarçeşme | 241046005 |

**Danışman:** Dr. Öğr. Üyesi Fatma Zehra Uzemek

---

## 🎯 Neden Bu Proje?

Fibonacci dizisi ve altın oran genellikle formüller ve sayısal örnekler üzerinden anlatılır. Ancak bu matematiksel yapıların doğada nasıl ortaya çıktığını yalnızca formüllere bakarak anlamak her zaman kolay değildir.

Bu proje, bu soyut kavramları **görsel, etkileşimli ve algoritmik bir modele** dönüştürmek amacıyla geliştirildi.

Temel hedef, yalnızca güzel bir ayçiçeği spirali çizmek değil; spiral yapının arkasındaki matematiği farklı açılardan incelemektir.

### 1. Soyut Matematiği Görselleştirmek

Kullanıcı tohum sayısını ve açıyı değiştirerek ortaya çıkan yapıyı doğrudan gözlemleyebilir.

Özellikle altın açıdan yapılan küçük değişikliklerin spiral düzeni üzerindeki etkisi, matematiksel bir değerin geometrik sonucu olarak etkileşimli biçimde görülebilir.

### 2. Fibonacci ve Altın Oran İlişkisini İncelemek

Ardışık Fibonacci sayılarının oranı:

```text
F(n+1) / F(n)
