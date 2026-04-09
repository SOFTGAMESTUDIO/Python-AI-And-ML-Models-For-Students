import os
import sys
import pickle
import numpy as np

# Ensure the project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tensorflow.keras.models import load_model
from src.preprocess import load_text, tokenize_text


def load_tokenizer(tokenizer_path):
    """Load a previously saved Keras Tokenizer from a pickle file."""
    with open(tokenizer_path, 'rb') as f:
        return pickle.load(f)


def generate_text(model_path, tokenizer, seed_text, seq_length, num_words, temperature=1.0):
    """
    Generate text word-by-word using the trained LSTM model.

    Args:
        model_path  : Path to saved .keras model file.
        tokenizer   : Fitted Keras Tokenizer (must be the SAME one used during training).
        seed_text   : Starting text string (prompt).
        seq_length  : Context window length used during training.
        num_words   : Number of new words to generate.
        temperature : Sampling temperature (1.0 = argmax, >1.0 = more random).

    Returns:
        Generated text string.
    """
    model = load_model(model_path)
    result = seed_text.strip()

    for _ in range(num_words):
        # ── Build context window ────────────────────────────────────────────
        context_words = result.split()[-seq_length:]
        input_text = ' '.join(context_words)

        sequence = tokenizer.texts_to_sequences([input_text])[0]

        # If every word in the context is OOV, break early
        if not sequence:
            print("[WARN] All context words are out-of-vocabulary. Stopping generation.")
            break

        # Pad (left) or trim (right) to exactly seq_length
        if len(sequence) < seq_length:
            sequence = [0] * (seq_length - len(sequence)) + sequence
        else:
            sequence = sequence[-seq_length:]

        sequence = np.array(sequence).reshape(1, -1)

        # ── Predict next token ─────────────────────────────────────────────
        predictions = model.predict(sequence, verbose=0)[0]   # shape: (vocab_size,)

        if temperature == 1.0:
            predicted_index = np.argmax(predictions)
        else:
            # Apply temperature scaling for diversity
            predictions = np.log(predictions + 1e-8) / temperature
            predictions = np.exp(predictions) / np.sum(np.exp(predictions))
            predicted_index = np.random.choice(len(predictions), p=predictions)

        output_word = tokenizer.index_word.get(predicted_index, '')
        if output_word and output_word != '<OOV>':
            result += ' ' + output_word

    return result


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    tokenizer_path = os.path.join(BASE_DIR, 'models', 'tokenizer.pkl')
    model_path     = os.path.join(BASE_DIR, 'models', 'lstm_model.keras')

    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at: {model_path}")
        print("[INFO]  Please run  'python src/train.py'  from the project root first.")
        raise SystemExit(1)

    if not os.path.exists(tokenizer_path):
        print(f"[ERROR] Tokenizer not found at: {tokenizer_path}")
        print("[INFO]  Run 'python src/train.py' to generate both the model and tokenizer.")
        raise SystemExit(1)

    tokenizer = load_tokenizer(tokenizer_path)

    generated = generate_text(
        model_path=model_path,
        tokenizer=tokenizer,
        seed_text='deep learning is a',
        seq_length=10,
        num_words=40,
        temperature=0.8
    )
    print("\n── Generated Text ──────────────────────────────────────────────────")
    print(generated)
    print("────────────────────────────────────────────────────────────────────")
