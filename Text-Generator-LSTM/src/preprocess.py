import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical


def load_text(file_path):
    """Load and clean text from file, stripping comment lines starting with '#'."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Strip lines that are comments or blank
    clean_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
    return ' '.join(clean_lines)


def tokenize_text(text, num_words=None):
    """Fit a Keras Tokenizer on the given text and return it."""
    tokenizer = Tokenizer(num_words=num_words, filters='', oov_token='<OOV>')
    tokenizer.fit_on_texts([text])
    return tokenizer


def create_sequences(tokenizer, text, seq_length):
    """
    Convert text to overlapping sequences of length (seq_length + 1).
    Each row is [context tokens... , next_token].
    Returns None if there is not enough text to form even one sequence.
    """
    tokens = tokenizer.texts_to_sequences([text])[0]
    if len(tokens) <= 1:
        raise ValueError("Text is too short to build sequences.")
        
    sequences = []
    # Start from 1 so we learn to predict the very first words given 0s
    for i in range(1, len(tokens)):
        # Extract up to seq_length prior tokens, plus the very next token
        start_idx = max(0, i - seq_length)
        seq = tokens[start_idx: i + 1]
        
        # Pad left with 0s if we don't have a full seq_length context yet
        if len(seq) < seq_length + 1:
            seq = [0] * (seq_length + 1 - len(seq)) + seq
            
        sequences.append(seq)
    return np.array(sequences)


def split_input_target(sequences, vocab_size):
    """
    Split sequences into (X, y).
    X : all tokens except the last  → shape (N, seq_length)
    y : last token, one-hot encoded  → shape (N, vocab_size)
    vocab_size must be supplied explicitly (len(tokenizer.word_index) + 1).
    """
    X = sequences[:, :-1]
    y = to_categorical(sequences[:, -1], num_classes=vocab_size)
    return X, y
