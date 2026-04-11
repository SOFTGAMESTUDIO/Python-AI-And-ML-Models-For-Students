# test_generate.py  —  run from Mini-GPT root: python test_generate.py
"""
Smoke test for Mini-GPT generation pipeline.
Detects the EXACT vocab size from the saved model checkpoint so it
always matches, regardless of tokenizer special-token changes.
"""

import sys
sys.path.insert(0, "src")

import torch
from model     import MiniGPT
from tokenizer import Tokenizer
from generate  import generate
from config    import Config

# ── Setup ─────────────────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n{'='*60}")
print(f"  Mini-GPT Generation Test")
print(f"  Device : {device}")
print(f"{'='*60}\n")

# ── Load tokenizer ─────────────────────────────────────────────────────────────
tokenizer = Tokenizer()
tokenizer.load("outputs/vocab.json")
print(f"✅ Vocab loaded  — {len(tokenizer.stoi):,} tokens")
print(f"   <pad>={tokenizer.stoi.get('<pad>')}  "
      f"<unk>={tokenizer.stoi.get('<unk>')}  "
      f"<eos>={tokenizer.stoi.get('<eos>')}")

# ── Detect checkpoint vocab size automatically ──────────────────────────────────
checkpoint = torch.load("outputs/model.pt", map_location=device, weights_only=True)
ckpt_vocab_size = checkpoint["embed.weight"].shape[0]
print(f"   Checkpoint embed size: {ckpt_vocab_size:,} (auto-detected)")

# ── Load model with the checkpoint's exact vocab size ─────────────────────────
model = MiniGPT(ckpt_vocab_size, Config.embed_size, Config.num_heads, Config.num_layers)
model.load_state_dict(checkpoint)
model.to(device).eval()

param_count = sum(p.numel() for p in model.parameters()) / 1e6
print(f"✅ Model loaded  — {param_count:.1f}M parameters")

# Safe token ID ceiling — clamp <unk>/<eos> if they exceed the checkpoint vocab
MAX_TOKEN_ID = ckpt_vocab_size - 1
print(f"   Max token ID  : {MAX_TOKEN_ID}\n")

# ── Test cases ─────────────────────────────────────────────────────────────────
test_cases = [
    # (prompt,                                       temp,  top_k, max_len)
    ("The future of artificial intelligence is",     0.7,   30,    50),
    ("In the beginning, the universe was",           0.7,   30,    50),
    ("Scientists have recently discovered that",     0.7,   30,    50),
    ("The history of the United States shows that",  0.8,   40,    60),
    ("Once upon a time there lived a",               0.9,   50,    60),
    ("Machine learning is a field of",               0.4,   15,    40),  # focused
    ("The stars at night remind me of",              1.1,   60,    50),  # creative
]

print(f"{'─'*60}")
print(f"  Running {len(test_cases)} test prompts...")
print(f"{'─'*60}\n")

all_ok = True
for i, (prompt, temp, topk, maxlen) in enumerate(test_cases, 1):
    try:
        output = generate(
            model, tokenizer, prompt,
            max_len=maxlen, temperature=temp, top_k=topk,
            max_token_id=MAX_TOKEN_ID,
        )
        status = "✅"
    except Exception as e:
        output = f"ERROR: {e}"
        status = "❌"
        all_ok = False

    print(f"[{i}] {status}  temp={temp}  top_k={topk}  max={maxlen}")
    print(f"     Prompt : {prompt}")
    print(f"     Output : {output}")
    print()

print(f"{'='*60}")
print(f"  {'✅  All tests passed!' if all_ok else '❌  Some tests failed!'}")
print(f"{'='*60}\n")
