from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout


def build_model(vocab_size, seq_length, embed_dim=64, lstm_units=128, dropout_rate=0.2):
    """
    Build and compile a character/word-level LSTM text generation model.

    Args:
        vocab_size  : Total number of unique tokens (len(word_index) + 1).
        seq_length  : Number of input context tokens (X.shape[1]).
        embed_dim   : Embedding vector dimension.
        lstm_units  : Number of hidden units in the LSTM layer.
        dropout_rate: Dropout applied after LSTM for regularisation.

    Returns:
        Compiled Keras Sequential model.
    """
    model = Sequential([
        # input_length is omitted (deprecated in TF >= 2.13) — shape is inferred at runtime
        Embedding(input_dim=vocab_size, output_dim=embed_dim),
        LSTM(lstm_units, return_sequences=False),
        Dropout(dropout_rate),
        Dense(vocab_size, activation='softmax')
    ])
    model.build(input_shape=(None, seq_length))
    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )
    model.summary()
    return model
