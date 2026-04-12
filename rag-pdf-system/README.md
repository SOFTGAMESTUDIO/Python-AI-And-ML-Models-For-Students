<div align="center">

# 📄 RAG PDF System
### Developed by Soft Game Studio

A modern PDF retrieval-augmented generation system for uploading PDF documents, extracting context, and answering questions with semantic search.

</div>

---

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-ready-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PyPDF2](https://img.shields.io/badge/PyPDF2-required-5b83f2?logo=python&logoColor=white)](https://pypi.org/project/PyPDF2/)
[![Studio](https://img.shields.io/badge/By-Soft_Game_Studio-6366f1)](https://github.com/SOFTGAMESTUDIO)

---

## 🚀 Overview

The **RAG PDF System** is designed to convert PDF documents into a searchable knowledge base and answer user questions with high relevance.
The pipeline performs PDF text extraction, document chunking, embedding generation, vector search, and extractive answer assembly.

## ✨ Features

- **PDF upload and preview** using Streamlit.
- **Document chunking** that preserves page context.
- **Sparse TF-IDF embeddings** for similarity search.
- **Cosine similarity retrieval** for top-matching passages.
- **Page-aware results** with page number references.
- **Lightweight and easy to extend** for custom PDF QA workflows.

## 📁 Project structure

- `app.py` – Streamlit web UI for file upload and question answering.
- `main.py` – Main pipeline orchestration and result assembly.
- `requirements.txt` – Python dependencies.
- `data/` – Local storage for uploaded PDF files.
- `embeddings/` – Generated embedding metadata and stored vectors.
- `docs/` – Supporting project documentation.
- `src/loader.py` – PDF text extraction and page parsing.
- `src/splitter.py` – Chunking logic for long documents.
- `src/embedder.py` – TF-IDF embedder implementation.
- `src/vector_store.py` – Vector search and scoring engine.
- `src/rag_pipeline.py` – Query-answer assembly and snippet selection.
- `src/utils.py` – Helper utilities for directories and file handling.

## 🛠️ Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Run the app

```bash
streamlit run app.py
```

Open the local Streamlit URL and upload a PDF to ask questions.

## 📘 Documentation

For architecture details and usage examples, see the docs:

- `docs/README.md`
- `docs/architecture.md`

## 💡 Notes

- Place PDFs in the `data/` folder or upload them directly in the UI.
- The system does not require external API keys to run.
- This repository is built and maintained by **Soft Game Studio**.
