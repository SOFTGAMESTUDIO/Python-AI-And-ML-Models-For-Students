<div align="center">

# 🧠 TF-IDF Semantic Search Engine
### Developed by Soft Game Studio

*A native, highly performant Machine Learning search pipeline driven by Term Frequency-Inverse Document Frequency statistical scaling.*

</div>

---

## 🚀 Overview

The **Soft Game Studio TF-IDF Engine** is an intelligent offline data-retrieval matrix designed to search concepts rather than exact-word matches. Instead of matching literal strings, it scales lexical meaning, ignores noise, and ranks results utilizing linear algebra (Cosine Similarity) ensuring unparalleled search precision without cloud latency.

## ✨ Core Technical Features

- **Automated Structuring Pipeline**: Transforms messy raw text data into uniformly mapped chunks utilizing Regex markers via our modular `cleaner.py`.
- **Intelligent Matrix Vectorization**: Eliminates language 'stop words' and extracts bi-grams natively using `Scikit-Learn` scaling representations in `tfidf.py`.
- **Mathematical Cosine Scoring**: Resolves user inquiries by identifying geometric similarities across high-dimensional vectors, prioritizing top `k` confidence scores in `search.py`.
- **Absolute 100% Offline AI**: An entire query engine decoupled from cloud dependencies. Maximum privacy guarantees for highly sensitive data architectures.

## 📦 Installation

This stack is primarily reliant on `scikit-learn` for its algorithmic math core. To install all necessary dependencies, refer to `requirements.txt`:

```bash
pip install -r requirements.txt
```

*(See `requirements.txt` for details on professional maintenance by Soft Game Studio and specific package rationale.)*

## 🛠️ Usage Flow

1. Review or modify the unstructured textual data inside `data/raw.txt`.
2. Generate the formatted index structures by executing the build module:
   ```bash
   python build.py
   ```
3. Initialize the application query terminal:
   ```bash
   python main.py
   ```
4. Ask dynamic, natural-language questions directly into the terminal interface to retrieve ranked statistical answers!

## 📂 Internal Operations & Code Documentation

We believe in maximum transparency and thorough technical documentation. For a full breakdown exposing exactly how components (`main.py`, `build.py`, `cleaner.py`, `loader.py`, `tfidf.py`, `search.py`) functionally process datasets, including **line-by-line and block-level Python code explanations**, please refer to our comprehensively updated manual:

👉 **[View Technical Manual - Code & Logic Breakdown](docs/TFIDF-Search-Engine.md)**

---

<div align="center">

**[Soft Game Studio](https://github.com/SoftGameStudio)**
*Engineering state-of-the-art software systems for scalable enterprise ecosystems.*

</div>
