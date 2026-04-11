# 📖 Mini-GPT Usage Guide

Complete step-by-step guide for training, testing, and chatting with Mini-GPT.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Step 1 — Configure the Model](#step-1--configure-the-model)
- [Step 2 — Train the Model](#step-2--train-the-model)
- [Step 3 — Run Automated Tests](#step-3--run-automated-tests)
- [Step 4 — Chat with the Model](#step-4--chat-with-the-model)
- [Tuning Generation Quality](#tuning-generation-quality)
- [Troubleshooting](#troubleshooting)
- [Common Errors and Fixes](#common-errors-and-fixes)

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | 3.10+ recommended |
| PyTorch | 2.0+ | With CUDA support for GPU |
| RAM | 4 GB min | 8 GB+ recommended |
| VRAM | Optional | 6 GB+ for GPU training |
| Disk Space | ~500 MB | For model + vocab outputs |
| Internet | Required | For HuggingFace dataset streaming |

---

## Installation

```bash
# 1. Navigate to the project
cd Mini-GPT

# 2. (Recommended) Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Install all dependencies
pip install -r requirements.txt
```

**What gets installed:**

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | 2.0+ | Deep learning framework + CUDA |
| `datasets` | latest | HuggingFace streaming datasets |
| `numpy` | latest | Numerical array operations |

---

## Step 1 — Configure the Model

Open `src/config.py` and adjust settings to match your hardware:

```python
class Config:
    # ── Model Architecture ──────────────────────────────────────
    vocab_size  = 20000   # Max word tokens
    block_size  = 128     # Context window (sequence length)
    embed_size  = 256     # Embedding dimensions
    num_heads   = 4       # Attention heads  (embed_size % heads == 0)
    num_layers  = 4       # Transformer layers

    # ── Training ────────────────────────────────────────────────
    batch_size  = 32      # Reduce to 16 if you get OOM errors
    lr          = 3e-4
    epochs      = 3       # Increase for better quality

    # ── Generation defaults ─────────────────────────────────────
    temperature = 0.7
    top_k       = 30
    max_gen_len = 80
```

**Quick config presets:**

| Hardware | `batch_size` | `embed_size` | `num_layers` | `epochs` |
|----------|-------------|-------------|-------------|---------|
| CPU only | 8 | 128 | 2 | 3 |
| 4GB GPU | 16 | 256 | 4 | 5 |
| 8GB GPU | 32 | 256 | 4 | 10 |
| 16GB+ GPU | 64 | 512 | 8 | 20 |

> [!TIP]
> Always ensure `embed_size % num_heads == 0`. For example:
> `embed_size=256, num_heads=4` ✅ → `256 / 4 = 64` per head
> `embed_size=256, num_heads=6` ❌ → `256 / 6 = 42.6` (not divisible)

---

## Step 2 — Train the Model

```bash
python src/train.py
```

**What happens step by step:**

```
1. 🚀 Detects CUDA or falls back to CPU
2. 📥 Streams 20,000 samples from OpenWebText (no local download)
3. 📚 Downloads WikiText-2 (~5,000 samples)
4. 🧹 Cleans all text (strips, removes newlines)
5. 🔤 Builds vocabulary (top 20,000 words + <pad><unk><eos>)
6. 💾 Saves outputs/vocab.json
7. 📦 Creates DataLoader (batches, shuffled)
8. 🏗️ Initializes MiniGPT model
9. 🔥 Trains for N epochs with AMP + AdamW
10. 💾 Saves outputs/model.pt
```

**Expected training time:**

| Hardware | Per Epoch (43K samples) | 3 Epochs |
|----------|------------------------|---------|
| CPU (8-core) | ~25–40 min | ~2 hrs |
| GTX 1660 Ti | ~8–12 min | ~36 min |
| RTX 3080 | ~3–5 min | ~15 min |
| RTX 4090 | ~1–2 min | ~6 min |

**Expected Loss Trajectory:**

```
Epoch 1 Step    0: Loss ~10.5  (random initialization)
Epoch 1 Step  100: Loss ~7.8
Epoch 1 Step  500: Loss ~6.9
Epoch 1 Final:     Loss ~6.2

Epoch 2 Final:     Loss ~5.8
Epoch 3 Final:     Loss ~5.5
```

> [!IMPORTANT]
> Loss below 5.0 = recognizable text patterns.
> Loss below 4.0 = coherent paragraphs (needs more epochs/model size).

---

## Step 3 — Run Automated Tests

```bash
python test_generate.py
```

The test runner:
- Auto-detects model vocab size from checkpoint (no size mismatch errors)
- Runs 7 prompts with different temperature + top_k settings
- Reports per-test pass/fail status
- Prints all generated outputs for inspection

**Sample output:**
```
============================================================
  Mini-GPT Generation Test
  Device : cuda
============================================================

✅ Vocab loaded  — 20,003 tokens
   Checkpoint embed size: 20,001 (auto-detected)
✅ Model loaded  — 15.7M parameters

[1] ✅  temp=0.7  top_k=30  max=50
     Prompt : The future of artificial intelligence is
     Output : The future of artificial intelligence is so rare in the world...

[2] ✅  temp=0.4  top_k=15  max=40
     Prompt : Machine learning is a field of
     Output : Machine learning is a field of a system of interest...
...
============================================================
  ✅  All tests passed!
============================================================
```

---

## Step 4 — Chat with the Model

```bash
python src/chat.py
```

### Startup Sequence

```
🔧 Device: cuda
✅ Vocab loaded  (20,003 tokens)
✅ Model loaded  (20,001 embedding slots)

═══════════════════════════════════════════════════════
  🤖  Mini-GPT  |  type 'exit' to quit
      temp=0.7  top_k=30  max_len=80
═══════════════════════════════════════════════════════
```

### Chat Commands

| Command | Syntax | Example | Description |
|---------|--------|---------|-------------|
| Generate | Just type anything | `The ocean is vast and` | Generates text continuation |
| Set temperature | `/temp <float>` | `/temp 0.5` | Lower = focused, higher = creative |
| Set top-K | `/topk <int>` | `/topk 15` | Smaller = more conservative |
| Set max length | `/len <int>` | `/len 150` | More tokens per response |
| Quit | `exit` | `exit` | Gracefully exits |

### Example Chat Session

```
You: The ocean covers most of our
Bot: The ocean covers most of our territory , and the ocean is a great deal of the world . The first
     time we discovered the ocean was when we were doing the same thing that we did on the ocean .

You: /temp 0.4
🌡️  Temperature set to 0.4

You: The ocean covers most of our
Bot: The ocean covers most of our state , and the size of the state was the first time the state was
     able to maintain the integrity of the state . The researchers have shown that the

You: /temp 1.1
🌡️  Temperature set to 1.1

You: The ocean covers most of our
Bot: The ocean covers most of our stories , floating deep inside everywhere , until we hear something
     surprising that draws us into all the mystery in our world . Nothing to love – no...
```

Notice: **same prompt, 3 different temperatures, 3 very different styles!**

---

## Tuning Generation Quality

### Strategy 1 — Adjust Prompts

The model is a **text completer**, not a question answerer. Give it partial sentences:

| ❌ Bad Prompt | ✅ Better Prompt |
|--------------|-----------------|
| `What is AI?` | `Artificial intelligence is defined as` |
| `Tell me about space` | `The history of space exploration began when` |
| `hello` | `Hello, my name is` |
| `news` | `Today's top news stories include` |

### Strategy 2 — Temperature × Top-K Combinations

| Goal | Temperature | Top-K | Effect |
|------|-------------|-------|--------|
| Maximum coherence | 0.3–0.5 | 10–20 | Repetitive but on-topic |
| Balanced output | 0.6–0.8 | 25–40 | Natural and readable ✅ |
| Creative writing | 0.9–1.1 | 40–70 | Diverse and expressive |
| Brainstorming | 1.1–1.3 | 80+ | Very wild ideas |

### Strategy 3 — Train Longer

Increasing `epochs` in `config.py` and retraining produces dramatically better output. Each extra epoch costs training time but reduces loss meaningfully for the first ~10 epochs.

---

## Troubleshooting

### CUDA Out Of Memory

```
RuntimeError: CUDA out of memory
```

**Fix:** Reduce `batch_size` in `Config`:
```python
batch_size = 16   # or 8
```

---

### Size Mismatch Loading Model

```
RuntimeError: size mismatch for embed.weight
```

**Cause:** Vocab changed after training (old model, new tokenizer).

**Fix 1 (quick):** Retrain the model with `python src/train.py`.

**Fix 2 (no retraining):** The checkpoint auto-detection in `chat.py` and `test_generate.py` already handles this — run them directly.

---

### HuggingFace 401 / Rate Limit Warning

```
Warning: You are sending unauthenticated requests to the HF Hub
```

This is just a **warning**, not an error. Training continues normally. For higher rate limits:
```bash
pip install huggingface_hub
huggingface-cli login   # enter your HF token
```

---

### All Generated Words Are Empty

```
Output: "     "  (all spaces)
```

**Cause:** Prompt contains no words from the vocabulary.

**Fix:** Use more common English words in your prompt. The model knows approximately the top 20,000 most frequent words from OpenWebText + WikiText.

---

### num_workers Error on Windows

```
RuntimeError: An attempt has been made to start a new process before the current process ...
```

**Fix:** Set `num_workers=0` in `train.py` line 78:
```python
loader = DataLoader(dataset, ..., num_workers=0)
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: tokenizer` | Running from wrong directory | Run from `Mini-GPT/` root |
| `FileNotFoundError: outputs/model.pt` | Not trained yet | Run `python src/train.py` first |
| `FileNotFoundError: outputs/vocab.json` | Not trained yet | Run `python src/train.py` first |
| `CUDA error: device-side assert triggered` | Token index > embedding size | Retrain model (will auto-fix) |
| `embed_size % num_heads != 0` | Bad config | Make `embed_size` divisible by `num_heads` |
