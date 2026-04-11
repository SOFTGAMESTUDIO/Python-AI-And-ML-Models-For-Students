# src/chat.py
"""
Interactive terminal chat with Mini-GPT.
Run from the project root:  python src/chat.py

Commands:
  /temp 0.5      — set temperature (0.1 focused → 1.5 creative)
  /topk 50       — change top-k token sampling
  /len  100      — change max generation length
  exit           — quit
"""

import torch
from model    import MiniGPT
from tokenizer import Tokenizer
from generate  import generate
from config    import Config

# ── Device ────────────────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔧 Device: {device}")

# ── Load Tokenizer ─────────────────────────────────────────────────────────────
tokenizer = Tokenizer()
try:
    tokenizer.load("outputs/vocab.json")
    print(f"✅ Vocab loaded  ({len(tokenizer.stoi):,} tokens)")
except FileNotFoundError:
    print("❌  outputs/vocab.json not found — run  python src/train.py  first.")
    exit(1)

# ── Load Model ────────────────────────────────────────────────────────────────
try:
    checkpoint = torch.load("outputs/model.pt", map_location=device, weights_only=True)
    ckpt_vocab_size = checkpoint["embed.weight"].shape[0]  # exact size from training

    model = MiniGPT(
        ckpt_vocab_size,
        Config.embed_size,
        Config.num_heads,
        Config.num_layers,
    ).to(device)
    model.load_state_dict(checkpoint)
    model.eval()
    print(f"✅ Model loaded  ({ckpt_vocab_size:,} embedding slots)")
except FileNotFoundError:
    print("❌  outputs/model.pt not found — run  python src/train.py  first.")
    exit(1)

# ── Safe vocab ceiling (clamp token IDs for current checkpoint) ──────────────
# <unk> / <eos> indices may exceed the trained embedding table size.
# We clamp all tokens to [0, ckpt_vocab_size-1] before passing to model.
MAX_TOKEN_ID = ckpt_vocab_size - 1

# ── Generation settings (adjustable at runtime) ───────────────────────────────
temperature = Config.temperature   # default: 0.7
top_k       = Config.top_k         # default: 30
max_len     = Config.max_gen_len   # default: 80

# ── Chat Loop ─────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  🤖  Mini-GPT  |  type 'exit' to quit")
print(f"      temp={temperature}  top_k={top_k}  max_len={max_len}")
print("="*55 + "\n")

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye! 👋")
        break

    if not user_input:
        continue

    # ── Runtime command parsing ───────────────────────────────────────────────
    if user_input.lower() == "exit":
        print("Goodbye! 👋")
        break

    if user_input.startswith("/temp"):
        try:
            temperature = float(user_input.split()[1])
            print(f"🌡️  Temperature set to {temperature}")
        except (IndexError, ValueError):
            print("Usage: /temp 0.7")
        continue

    if user_input.startswith("/topk"):
        try:
            top_k = int(user_input.split()[1])
            print(f"🎯  Top-K set to {top_k}")
        except (IndexError, ValueError):
            print("Usage: /topk 30")
        continue

    if user_input.startswith("/len"):
        try:
            max_len = int(user_input.split()[1])
            print(f"📏  Max length set to {max_len}")
        except (IndexError, ValueError):
            print("Usage: /len 80")
        continue

    # ── Generate response ─────────────────────────────────────────────────────
    response = generate(
        model,
        tokenizer,
        user_input,
        max_len=max_len,
        temperature=temperature,
        top_k=top_k,
        max_token_id=MAX_TOKEN_ID,
    )
    print(f"\nBot: {response}\n")