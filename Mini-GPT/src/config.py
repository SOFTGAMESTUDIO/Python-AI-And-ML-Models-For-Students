# src/config.py


class Config:
    # ── Model Architecture ───────────────────────────────────────────────────
    vocab_size  = 20000   # Max word tokens (special tokens added on top)
    block_size  = 128     # Sequence length for training windows
    embed_size  = 256     # Embedding vector dimension
    num_heads   = 4       # Transformer attention heads (embed_size % num_heads == 0)
    num_layers  = 4       # Number of stacked Transformer layers

    # ── Training ─────────────────────────────────────────────────────────────
    batch_size  = 32
    lr          = 3e-4    # AdamW learning rate
    epochs      = 3

    # ── Generation (used in chat.py / generate.py) ───────────────────────────
    temperature = 0.7     # Lower = focused/conservative, Higher = creative/random
    top_k       = 30      # Only sample from top-K most likely next tokens
    max_gen_len = 80      # Max new tokens to generate per response