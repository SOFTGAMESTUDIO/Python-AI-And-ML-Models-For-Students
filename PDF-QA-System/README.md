<div align="center">

# 🧠 PDF Question Answering System
### Developed by Soft Game Studio

*An advanced, context-aware AI engine designed to process, vectorize, and intelligently answer questions from complex PDF documents.*

</div>

---

## 🚀 Overview

The **Soft Game Studio PDF QA System** is a robust, modular pipeline that transforms static PDF documents into an interactive, fully searchable knowledge base. It leverages modern vector embeddings and similarity search to retrieve relevant context and provide accurate answers.

## ✨ Core Features

- **Automated Document Parsing:** Fast, reliable extraction of text from PDF documents using `src/pdf_loader.py`.
- **Intelligent Semantic Chunking:** Splits large documents into manageable, context-preserving segments via `src/chunker.py`.
- **High-Dimensional Vectorization:** Generates state-of-the-art textual embeddings using `src/vectorizer.py`.
- **Lightning-Fast Vector Search:** Retrieves the most topically relevant document sections instantaneously through `src/search.py`.
- **Modular Architecture:** Designed for enterprise scalability, allowing individual components to be upgraded or swapped seamlessly.

## 📦 Architecture & Setup

Please review our comprehensive technical overview in [`docs/system_architecture.md`](docs/system_architecture.md) for a deep dive into the system's logic and data flow.

### Installation

Ensure your Python environment is set up properly, then install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### Usage

1. Place your target `.pdf` files into the `./data/` directory.
2. Run the main processing and QA pipeline:
   ```bash
   python main.py
   ```

---

<div align="center">

**[Soft Game Studio](https://github.com/SoftGameStudio)**
*Engineering state-of-the-art software systems for scalable enterprise ecosystems.*

</div>