# src/generate.py

import torch
import torch.nn.functional as F


def generate(model, tokenizer, prompt, max_len=100, temperature=0.7, top_k=30, max_token_id=None):
    """
    Autoregressively generate text from a given prompt.

    Args:
        model        : Trained MiniGPT model.
        tokenizer    : Fitted Tokenizer instance.
        prompt       : Seed text string for generation.
        max_len      : Maximum number of NEW tokens to generate.
        temperature  : Controls randomness. Lower = more focused. (default: 0.7)
        top_k        : Keep only the top K most likely tokens. (default: 30)
        max_token_id : Clamp token IDs to this ceiling (for old checkpoints
                       whose embedding table ends before <unk>/<eos>).
    """
    model.eval()

    device      = next(model.parameters()).device
    eos_id      = tokenizer.stoi.get("<eos>", -1)
    pad_id      = tokenizer.stoi.get("<pad>", 0)
    block_size  = 512  # max positional encoding size from model

    tokens = tokenizer.encode(prompt)

    # Clamp encoded tokens if the model was trained on a smaller vocab
    if max_token_id is not None:
        tokens = [min(t, max_token_id) for t in tokens]

    # Guard: drop unknown tokens (all zeros after encode is a bad prompt)
    if not tokens or all(t == 0 for t in tokens):
        return "[No known words in prompt. Try different words from the training data.]"

    for _ in range(max_len):
        # Truncate context to block_size to avoid positional encoding overflow
        context = tokens[-block_size:]
        x = torch.tensor(context, dtype=torch.long, device=device).unsqueeze(0)

        with torch.no_grad():
            logits = model(x)

        # Take logits from the very last position only
        logits = logits[0, -1, :]          # shape: (vocab_size,)

        # Block special tokens from being sampled
        logits[pad_id] = -float("inf")
        if eos_id != -1:
            # Do not block EOS yet — let the stop condition catch it naturally
            pass

        # ── Temperature scaling ──────────────────────────────────────────────
        logits = logits / max(temperature, 1e-8)

        # ── Top-K filtering ──────────────────────────────────────────────────
        if top_k is not None and top_k > 0:
            top_values, top_indices = torch.topk(logits, min(top_k, logits.size(-1)))
            # Zero out everything NOT in top_k
            filtered = torch.full_like(logits, -float("inf"))
            filtered[top_indices] = top_values
            logits = filtered

        probs = F.softmax(logits, dim=-1)

        # ── Sample next token ────────────────────────────────────────────────
        next_token = torch.multinomial(probs, num_samples=1).item()
        tokens.append(next_token)

        # ── EOS stopping condition ───────────────────────────────────────────
        if eos_id != -1 and next_token == eos_id:
            break

    return tokenizer.decode(tokens)