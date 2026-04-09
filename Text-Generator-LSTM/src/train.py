import os
import sys
import pickle

# Ensure the project root is on sys.path so `src.*` imports resolve when running
# this script as:  python src/train.py  (from the project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from src.preprocess import load_text, tokenize_text, create_sequences, split_input_target
from src.model import build_model


def train(data_path, model_path, tokenizer_path, seq_length=10, epochs=150, batch_size=32):
    """
    Full training pipeline.

    Args:
        data_path      : Path to raw text file.
        model_path     : Where to save the trained model (.keras format).
        tokenizer_path : Where to save the fitted tokenizer (.pkl).
        seq_length     : Context window size in tokens.
        epochs         : Maximum training epochs.
        batch_size     : Mini-batch size.
    """
    # ── 1. Load & preprocess ────────────────────────────────────────────────
    text = load_text(data_path)
    print(f"[INFO] Loaded text — {len(text.split())} words.")

    tokenizer = tokenize_text(text)
    vocab_size = len(tokenizer.word_index) + 1   # +1 for padding index 0
    print(f"[INFO] Vocabulary size: {vocab_size}")

    sequences = create_sequences(tokenizer, text, seq_length)
    print(f"[INFO] Total sequences: {len(sequences)}")

    X, y = split_input_target(sequences, vocab_size=vocab_size)
    print(f"[INFO] X shape: {X.shape} | y shape: {y.shape}")

    # ── 2. Build model ──────────────────────────────────────────────────────
    model = build_model(vocab_size=vocab_size, seq_length=X.shape[1])

    # ── 3. Save tokenizer alongside the model ──────────────────────────────
    os.makedirs(os.path.dirname(tokenizer_path), exist_ok=True)
    with open(tokenizer_path, 'wb') as f:
        pickle.dump(tokenizer, f)
    print(f"[INFO] Tokenizer saved → {tokenizer_path}")

    # ── 4. Train ────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    callbacks = [
        # Save best model (lowest training loss)
        ModelCheckpoint(model_path, save_best_only=True, monitor='loss', verbose=1),
        # Stop early if loss stops improving
        EarlyStopping(monitor='loss', patience=25, restore_best_weights=True, verbose=1),
    ]
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=callbacks)
    print(f"[INFO] Training complete. Model saved → {model_path}")


if __name__ == '__main__':
    # Build absolute paths relative to this file so the script works regardless
    # of which directory it is invoked from.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    train(
        data_path=os.path.join(BASE_DIR, 'data', 'input.txt'),
        model_path=os.path.join(BASE_DIR, 'models', 'lstm_model.keras'),
        tokenizer_path=os.path.join(BASE_DIR, 'models', 'tokenizer.pkl'),
        seq_length=10,
        epochs=150,
        batch_size=32
    )
