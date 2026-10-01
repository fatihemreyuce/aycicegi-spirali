# 🌻 Sunflower Spiral

### Fibonacci, Golden Ratio, Vogel's Model & Graph Theory

An interactive mathematical visualization that explores the structure of sunflower seed patterns through **Fibonacci sequences, the golden ratio, the golden angle, Vogel's model, and graph theory**.

Built as a desktop application with **Python and PySide6**, the project transforms mathematical concepts into an interactive visual model where users can explore spiral formation, graph structures, convergence behavior, and the effect of different angular values.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph_Theory-blue?style=flat-square)
![NumPy](https://img.shields.io/badge/NumPy-Numerical_Computing-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

---

## ✨ Highlights

- 🌻 Interactive sunflower seed visualization using **Vogel's model**
- 🌀 Golden-angle based seed distribution
- 🔢 Fibonacci sequence analysis and validation
- 📈 Visualization of `F(n+1) / F(n) → φ` convergence
- 🕸 Directed graph representation with **NetworkX**
- 🔲 Weighted adjacency matrix visualization
- ⚖️ Side-by-side angle comparison
- 🎞 Interactive seed placement animation
- 🔍 Zoom, pan, hover and seed inspection
- 🧪 Automated domain and UI tests with **pytest** and **pytest-qt**

---

## 🧮 Core Mathematical Model

The seed positions are generated using Vogel's model:

```text
xᵢ = c · √i · cos(i · α)
yᵢ = c · √i · sin(i · α)
```

where the golden angle is approximately:

```text
α ≈ 137.507764°
```

The project also investigates the relationship:

```text
F(n+1) / F(n) → φ
```

where:

```text
φ = (1 + √5) / 2 ≈ 1.6180339887
```

These mathematical relationships are explored visually and represented structurally through directed graphs.

---

## 🎓 Academic Context

This project was developed as a **Discrete Mathematics course project at Istanbul Gedik University**.

### Contributors

| Name |
| --- |
| Fatih Emre Yüce |
| Ramazan Türkyılmaz |
| Kaan Sarı |
| Talha Akarçeşme |

**Academic Advisor:** Dr. Öğr. Üyesi Fatma Zehra Uzemek

---

## 📌 Bu Proje Nedir?
