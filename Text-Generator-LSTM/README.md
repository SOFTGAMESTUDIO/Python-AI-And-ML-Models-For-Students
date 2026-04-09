# Text Generation using Long Short-Term Memory (LSTM) Networks

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-orange)
![Keras](https://img.shields.io/badge/Keras-Enabled-red)
![License](https://img.shields.io/badge/License-MIT-green)

A professional, student-friendly implementation of a character/word-level generative language model powered by an LSTM sequence architecture.

This project demonstrates how deep learning models learn patterns from raw textual data and use those learned probabilistic distributions to generate completely new, coherent text sequences iteratively.

---

## 📖 Project Overview

Traditional feed-forward neural networks struggle with text generation because they cannot retain "memory" of previous inputs. This project utilizes Long Short-Term Memory (LSTM) networks—a specialized type of Recurrent Neural Network (RNN)—which maintain an internal hidden state across sequence time-steps. 

By analyzing overlapping contexts, the model learns the syntax, vocabulary, and grammar of the training dataset.

### Key Features
- **Dynamic Preprocessing**: Intelligent left-padded sequence chunking.
- **Robust Training Pipeline**: Includes model checkpointing and EarlyStopping to prevent overfitting.
- **Inference Parameterization**: Exposes a `temperature` variable to scale generation creativity versus strict confidence.
- **Persistence**: Automatically serializes both the Model `.keras` weights and Tokenizer `.pkl` vocabulary definitions.

---

## 🗂️ Directory Structure

```text
Text-Generator-LSTM/
├── data/
│   └── input.txt            # Training text corpus (Drop your dataset here!)
├── docs/
│   └── architecture.md      # Detailed explanation of the LSTM neural design
├── models/                  # Output directory for serialized objects
│   ├── lstm_model.keras     # Trained neural network weights
│   └── tokenizer.pkl        # Pickled vocabulary state
├── src/
│   ├── preprocess.py        # Tokenization, padding, and sequence generation
│   ├── model.py             # Sequential LSTM architecture definition
│   ├── train.py             # End-to-end model training script
│   └── generate.py          # Inference script to predict text
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Setup & Execution

### 1. Environment Configuration
Ensure you have Python installed, then install the deep learning dependencies:
```bash
pip install -r requirements.txt
```

### 2. Supply Training Data
We have provided a default primer on Deep Learning within `data/input.txt`. For superior, production-like results, you should replace this with a massive text file (e.g., a Shakespeare play, Wikipedia dumps, or a book). The more data, the better the LSTM learns grammatical structure.

### 3. Model Training
Run the pipeline to tokenize the data, build overlapping tensors, and train the neural network architecture.
```bash
python src/train.py
```
> **Note:** The training uses EarlyStopping. If validation loss ceases to improve over 25 epochs, training will gracefully halt and revert to the best-performing weights.

### 4. Text Generation (Inference)
Invoke the trained model. The generator script reads the saved tokenizer layout, consumes a "seed" sequence, and outputs the highly probable next tokens sequentially.
```bash
python src/generate.py
```

### 🧠 Tuning Generation Quality
In `src/generate.py`, you can modify the `temperature` parameter:
*   `temperature = 1.0` (Default): Standard probability.
*   `temperature < 1.0` (e.g., 0.6): Safer, highly repetitive, and confident word choices.
*   `temperature > 1.0` (e.g., 1.5): Wild, creative, and risky linguistic jumps.

---

## 👨‍💻 Developed By
**Soft Game Studio** - Part of the *Python AI & ML Models For Students* repository designed for hands-on, educational machine learning engineering.
