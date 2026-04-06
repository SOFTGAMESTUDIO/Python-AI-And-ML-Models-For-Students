<div align="center">

# 📄 PDF Text Extractor
### Developed by Soft Game Studio

*A high-performance, precision-driven PDF text extraction utility designed to natively handle complex two-column layouts with absolute accuracy.*

</div>

---

## 🚀 Overview

Standard PDF extractors struggle with dual-column layouts, often merging text indiscriminately across the page horizontally. The **Soft Game Studio PDF Text Extractor** resolves this by mathematically determining the geometric layout of text blocks to preserve the true reading order.

## ✨ Core Features

- **Spatial Coordinate Targeting:** Accurately reads PDF spatial geometry rather than raw, unordered text streams.
- **Automatic Column Segmentation:** Intelligently splits the layout into `LEFT` and `RIGHT` columns to maintain logical content flow.
- **Vertical Sorting Engine:** Processes and sorts text blocks top-to-bottom sequentially within their respective columns.
- **Privacy-First & Fully Native:** Operates entirely offline with deterministic results. No API calls, no third-party ML models, and zero data telemetry.
- **High-Performance Architecture:** Optimized for instantaneous execution utilizing lightweight local resources.

## 📦 Installation

Ensure your Python environment is set up properly, then install the necessary dependencies:

```bash
pip install -r requirements.txt
```

## 🛠️ Usage

1. Place your target `.pdf` files into the `./sample/` or working directory.
2. Run the extraction pipeline:
   ```bash
   python src/extractor.py
   ```
3. The tool will parse the layout and output perfectly-structured text reflecting the original column-based format.

---

<div align="center">

**[Soft Game Studio](https://github.com/SoftGameStudio)**
*Engineering state-of-the-art software systems for scalable enterprise ecosystems.*

</div>