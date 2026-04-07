# 🔍 TF-IDF AI Knowledge Search — Technical Manual

> **Developed by Soft Game Studio**

---

## 1. System Overview

The **TF-IDF Search Engine** built by *Soft Game Studio* is a powerful, locally executing Machine Learning Search Tool. Utilizing the Term Frequency-Inverse Document Frequency (TF-IDF) paradigm, the system parses databases of raw knowledge (`data/raw.txt`), constructs multidimensional vector spaces, and instantly processes case-insensitive fuzzy queries returning top-ranked mathematical probabilities.

## 2. Codebase Breakdown & Execution Flow

The architecture operates efficiently utilizing the `scikit-learn` stack alongside a strictly decoupled structure. Below is the full integration and code snippet breakdown detailing every module with block-by-block and line-by-line explanations.

### 2.1 Pre-Processing `build.py`

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\build.py:L1-L7]
- **Line 1 (`from src.cleaner import convert_to_md, convert_to_json`)**: Imports the data normalization pipeline functions from our `src/cleaner.py` utility module.
- **Lines 3-4**: Executes the parser logic taking our messy `data/raw.txt` and dynamically reformatting it into a structured markdown `data/skills.md`, confirming via terminal print.
- **Lines 6-7**: Executes the JSON parsing logic taking the same text and saving it safely as a structured JSON array into `data/skills.json`, outputting validation.

### 2.2 Data Cleaning `src/cleaner.py`

This module is responsible for scrubbing unstructured text and adding structured headers as well as JSON mapping.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\cleaner.py:L1-L20]
- **Lines 1-2**: Imports Python's built-in `re` module tailored for Regular Expression pattern matching and the `json` module for structured dictionary encoding.
- **Lines 4-19**: Function `split_by_heading(text)` defines a RegEx boundary that splits the large input text explicitly whenever it detects predefined title sequences (like "What is Python"). Iterates sequentially through the generated regex matches skipping by 2 (identifying title / content pair). Trims trailing whitespaces with `.strip()` and recombines the strings as an array of discrete document items. 

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\cleaner.py:L22-L36]
- **Lines 22-36**: `get_structured_data(text)` extracts identical Regex patterns but maps the structural data natively into a Python list of dictionaries consisting of `"title"` and `"content"` mapped values.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\cleaner.py:L38-L51]
- **Lines 38-51**: `convert_to_md` reads the absolute text block from the file safely with UTF-8 encoding, passes it to `split_by_heading()`. Opens the destination file in write mode, writes a foundational top-level markdown heading `📘 AI Knowledge Base`, loops through each chunk and generates standardized `##` headers ensuring a Markdown formatted file is generated.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\cleaner.py:L54-L61]
- **Lines 54-61**: `convert_to_json` acts similarly but relies on the `get_structured_data()` returning dictionaries, dropping the entire dictionary array securely into disk using `json.dump(data, f, indent=4)`.

### 2.3 Data Ingestion `src/loader.py`

Once textual data is structured with markdown tags, we load arrays into memory. 

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\loader.py:L1-L14]
- **Lines 1-6**: Function `load_md(path)` targets the cleaned markdown document, safely reads it, and systematically cuts the entire string object open everywhere `## ` is detected natively splitting it into a Python list.
- **Lines 8-14**: Bootstraps the array loop validating size thresholds. Only sections/segments scaling larger than 50 character limits are appended to our internal dataset memory (`docs`) rendering minor fragment errors omitted automatically.

### 2.4 Mathematical Vectorization `src/tfidf.py`

This operates as the neural mathematics kernel converting human strings to vector angles.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\tfidf.py:L1-L9]
- **Line 1 (`from sklearn.feature_extraction.text import TfidfVectorizer`)**: Targets Scikit-Learn pulling the mathematical class required to map English language strings into coordinate grids.
- **Lines 3-7**: `train(docs)` initiates the vectorization processor configuring parameter `stop_words="english"` to exclude vocabulary noise (e.g., 'and', 'the'). We bind `ngram_range=(1, 2)` to allow mathematical connections mapping combination word-pairs natively.
- **Line 8**: Triggers `.fit_transform(docs)` immediately mapping absolute vectors against the input knowledge strings returning the weighted frequency `matrix`.

### 2.5 Query Evaluation `src/search.py`

This function takes our mathematical matrices and resolves dynamic user inputs scoring answers.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\src\search.py:L1-L14]
- **Line 1 (`from sklearn.metrics.pairwise import cosine_similarity`)**: Directly uses Scikit-Learn logic to calculate the geometrical Cosine angle between vectors evaluating similarity boundaries.
- **Line 3 (`def query(q, vectorizer, matrix, docs, top_k=3):`)**: Accepts the question `q`, generated `vectorizer`, the mapped `matrix`, textual dataset `docs`, and establishes a limit retrieving only maximum `top_k=3` responses.
- **Lines 4-5**: Instantly converts the user question string into a vectorized array dimension `q_vec`. The system computes a cosine mathematical equation extracting absolute angle overlaps against the full knowledge matrix. 
- **Line 7**: Runs `argsort()` indexing arrays backwards mapping only the mathematical highs directly bounded within `top_k`.
- **Lines 9-14**: Iterates the returned top indexes with a strict threshold bounding check: if the probabilistic similarity `scores[i]` is strictly above `0.15` (meaning greater than 15% overlap confidence) it binds the source dataset text and floating score appending to memory returning out the finalized list of context strings.

### 2.6 Main Command Loop `main.py`

Tying the mathematical core to terminal IO flow.

@[d:\Pythoon AI & ML Models For Students\TFIDF-Search-Engine\main.py:L1-L31]
- **Lines 1-3**: Binds all local architectural methods extracting them efficiently for runtime execution.
- **Lines 5-9**: Inside `main()`, ingests the cleaned `data/skills.md`, mapping it strictly calling `train(docs)` outputting the mathematical components `vectorizer, matrix`.
- **Line 12**: Establishes an infinite loop `while True:` rendering a continuous IO console terminal state.
- **Lines 13-16**: Prompts the user terminal. If string evaluates exactly as "exit" it systematically kills the loop breaking safely out to terminal OS.
- **Lines 18-22**: Passes queries through `query()` fetching the returned scoring items. If exactly zero results are returned, prints failed outputs restarting the system loop context instantly waiting for new user input.
- **Lines 24-28**: A successful array response triggers an enumerating visual output parsing `scores` converting scientific formats to a readable float `:.2f` and concatenating the exact document string text directly out to the users terminal interface.
- **Lines 30-31**: Classic python namespace enforcement initializing programmatic flow logically triggering `main()`.

---

## 3. Real-World Execution Examples

To test real-world functionality:
1. Process indexing structures: run `python build.py` 
2. Execute Query Interactive Terminal: run `python main.py` 

**CLI Terminal Example Interaction**:
```text
🤖 AI Knowledge Search (type exit)

Ask: can you explain how ai functions with statistical models?

📌 Answers:

1. Confidence: 0.58
Artificial Intelligence
Artificial Intelligence algorithms depend heavily on matrix-oriented statistical mappings ... which allows machines to determine predictive insights structurally.
...

2. Confidence: 0.22
Machine Learning
Machine Learning is a subset that utilizes statistical vectors to map continuous environments...
```

---
*(c) Copyright Soft Game Studio | Engineering state-of-the-art software intelligence utilities.*
