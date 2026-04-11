# 🏗️ Mini-GPT Architecture Deep Dive

This document provides an in-depth technical explanation of every component in the Mini-GPT system.

---

## Table of Contents

- [High-Level Architecture](#1-high-level-architecture)
- [Tokenizer](#2-tokenizer--srctokenizerpy)
- [Dataset](#3-dataset--srcdatasetpy)
- [Model Architecture](#4-model-architecture--srcmodelpy)
  - [Token Embedding](#41-token-embedding)
  - [Positional Embedding](#42-positional-embedding)
  - [Transformer Encoder Layers](#43-transformer-encoder-layers)
  - [Causal Mask — The Critical Feature](#44-causal-mask--the-critical-feature)
  - [Output Linear Layer](#45-output-linear-layer)
- [Training Pipeline](#5-training-pipeline--srctrainpy)
  - [Mixed Precision AMP](#51-mixed-precision-amp)
  - [Loss Function](#52-loss-function)
  - [Optimizer](#53-optimizer)
- [Generation Engine](#6-generation-engine--srcgeneratepy)
  - [Temperature Scaling](#61-temperature-scaling)
  - [Top-K Filtering](#62-top-k-filtering)
  - [Sampling vs Argmax](#63-sampling-vs-argmax)
- [Parameter Count](#7-parameter-count)
- [Memory Layout](#8-memory-layout)

---

## 1. High-Level Architecture

```
                         ┌─────────────────────────────────────┐
                         │            MiniGPT                  │
                         │                                     │
  Input:                 │  [12, 45, 0, 98, 3]                │
  token IDs  ──────────► │       │         │                   │
                         │  Token Embed  Pos Embed             │
                         │       │         │                   │
                         │       └────+────┘                   │
                         │            │                        │
                         │    ┌───────▼────────┐              │
                         │    │ Causal Mask (T×T)│             │
                         │    │  0  -∞  -∞  -∞ │             │
                         │    │  0   0  -∞  -∞ │             │
                         │    │  0   0   0  -∞ │             │
                         │    │  0   0   0   0 │             │
                         │    └───────┬────────┘              │
                         │            │                        │
                         │    ┌───────▼────────┐              │
                         │    │ TransformerEncoder│            │
                         │    │  Layer 1         │            │
                         │    │  Layer 2         │            │
                         │    │  Layer 3         │            │
                         │    │  Layer 4         │            │
                         │    └───────┬────────┘              │
                         │            │                        │
                         │    ┌───────▼────────┐              │
                         │    │ Linear (embed   │             │
                         │    │   → vocab_size) │             │
                         │    └───────┬────────┘              │
                         │            │                        │
                         │    Logits [B × T × V]               │
                         └─────────────────────────────────────┘
```

---

## 2. Tokenizer — `src/tokenizer.py`

### How It Works

The tokenizer converts raw text into integer sequences and back.

**Vocabulary construction:**

```
Step 1: Join all text → ["the cat sat on the mat", ...]
Step 2: Count word frequencies → {"the": 94821, "of": 81234, ...}
Step 3: Take top-N most frequent → most_common(20000)
Step 4: Assign indices
         <pad> = 0
         "the" = 1  (most frequent)
         "of"  = 2
         ...
         <unk> = 20001
         <eos> = 20002
Step 5: Save to outputs/vocab.json
```

**Encoding example:**
```python
text   = "the cat sat on the mat"
tokens = [1, 384, 912, 87, 1, 2041]
         ↑                  ↑
      known word         known word
```

**Decoding example:**
```python
tokens  = [0, 1, 384, 20001, 87, 20002]  # has <pad>, <unk>, <eos>
output  = "the cat on"                    # specials stripped cleanly
```

### Special Token Design Philosophy

Placing `<unk>` and `<eos>` **after** all word tokens (not at indices 2,3) ensures the existing trained model's embedding matrix is never invalidated. Only the embedding rows for the two new tokens would be random-initialized — but since they were never emitted during training, they won't be sampled.

---

## 3. Dataset — `src/dataset.py`

The `TextDataset` class wraps raw text for use with PyTorch's `DataLoader`.

### Sliding Window Strategy

```
Full token sequence (length L):
[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9 ...]

Random start index s = 2:
  x = [t2, t3, t4, t5, t6]    ← input   (block_size = 5)
  y = [t3, t4, t5, t6, t7]    ← target  (shifted by 1)
```

The model learns: *given position k, what token follows?*

### Oversampling Design

`__len__` returns `len(texts) × 10` so each epoch sees each text in **10 different random slices**, maximizing exposure to all sub-sequences without duplicating data.

**Short Text Padding:**
```
tokens = [12, 45, 7]   # shorter than block_size + 1
padded = [12, 45, 7, 0, 0, 0, ..., 0]   # pad with <pad>=0
```

---

## 4. Model Architecture — `src/model.py`

### 4.1 Token Embedding

```python
self.embed = nn.Embedding(vocab_size, embed_size)
```

Maps each integer token ID into a trainable `embed_size`-dimensional vector.

```
vocab_size = 20001
embed_size = 256
Matrix shape: [20001, 256]  ← 5.12M parameters
```

The model **learns** what each token means by gradient updates. Initially random, over training the vectors cluster semantically similar words together in the 256-dimensional space.

### 4.2 Positional Embedding

```python
self.pos = nn.Embedding(512, embed_size)
```

Self-attention has no inherent sense of order. We fix this by adding a learnable position vector to each token embedding:

```
Final input to transformer = token_embed[token_id] + pos_embed[position]
```

This allows position 0 to "feel" different from position 10, even for the same token.

### 4.3 Transformer Encoder Layers

Each `TransformerEncoderLayer` consists of:

```
┌─────────────────────────────────────┐
│  1. Multi-Head Self-Attention       │
│     Q, K, V projections             │
│     num_heads = 4 (default)         │
│     head_dim  = 256 / 4 = 64        │
│                                     │
│  2. Add & Layer Norm                │
│     residual connection             │
│                                     │
│  3. Feed-Forward Network            │
│     Linear(256 → 1024)             │
│     ReLU activation                 │
│     Linear(1024 → 256)             │
│                                     │
│  4. Add & Layer Norm                │
└─────────────────────────────────────┘
```

Stack 4 of these = `num_layers = 4`.

### 4.4 Causal Mask — The Critical Feature

Without a causal mask, the attention mechanism at position `i` can "see" all other positions including future ones. This lets the model **cheat** during training (it reads the answer before predicting it), leading to near-zero loss but **zero generalization**.

```python
mask = nn.Transformer.generate_square_subsequent_mask(T).to(x.device)
```

For sequence length T=5:
```
Position:  0    1    2    3    4
           ┌────────────────────┐
  0        │  0  -∞  -∞  -∞  -∞│  ← only attends to itself
  1        │  0   0  -∞  -∞  -∞│  ← attends 0,1
  2        │  0   0   0  -∞  -∞│  ← attends 0,1,2
  3        │  0   0   0   0  -∞│  ← attends 0,1,2,3
  4        │  0   0   0   0   0│  ← attends all
           └────────────────────┘
```

`-∞` values become `0` after softmax → zero attention weight → no information flows backward from the future.

### 4.5 Output Linear Layer

```python
self.fc = nn.Linear(embed_size, vocab_size)
# [256 → 20001]
```

Projects each position's embed vector to a raw score (logit) over the entire vocabulary. The highest logit = the model's "most confident" next word.

---

## 5. Training Pipeline — `src/train.py`

### 5.1 Mixed Precision AMP

```python
use_amp = device.type == "cuda"
scaler  = torch.amp.GradScaler(device=device.type, enabled=use_amp)

with torch.amp.autocast(device_type=device.type, enabled=use_amp):
    logits = model(x)
    loss   = loss_fn(...)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

**Why AMP works:**
- Forward pass in `float16` → half the GPU memory, 2× faster math
- Gradients scaled up before `backward()` to prevent float16 underflow
- `GradScaler` dynamically adjusts the scaling factor each step

On CPU, `use_amp=False` disables this entirely to avoid CPU errors.

### 5.2 Loss Function

```python
loss_fn = nn.CrossEntropyLoss()
loss = loss_fn(
    logits.view(-1, vocab_size),   # shape: [B*T, V]
    y.view(-1)                     # shape: [B*T]
)
```

Cross-entropy measures how much probability mass the model placed on the correct next token. Perfect prediction = `0.0`. Random prediction over 20K vocab ≈ `ln(20000) ≈ 9.9`.

**Loss progression typically looks like:**
```
Epoch 1 step 0:   Loss ~10.4  (almost random)
Epoch 1 step 500: Loss ~7.2   (learning basic word co-occurrence)
Epoch 3 final:    Loss ~5.5   (learning phrases and structure)
```

### 5.3 Optimizer

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
```

**AdamW** is Adam with decoupled weight decay. It:
- Adapts learning rate per parameter
- Decays large weights to prevent overfitting
- `lr=3e-4` is the standard GPT pre-training rate

---

## 6. Generation Engine — `src/generate.py`

### 6.1 Temperature Scaling

```python
logits = logits / temperature
```

| temperature | Effect |
|-------------|--------|
| `0.1` | Almost deterministic, picks top-1 always |
| `0.7` | **Sweet spot** — varied but coherent |
| `1.0` | Raw model distribution |
| `1.5` | Very noisy, chaotic output |

Dividing by a number < 1 **sharpens** the distribution (bigger differences between high/low logits).
Dividing by a number > 1 **flattens** it (tokens become more equally likely).

### 6.2 Top-K Filtering

```python
top_values, top_indices = torch.topk(logits, k=30)
filtered = torch.full_like(logits, -float("inf"))
filtered[top_indices] = top_values
```

Sets all tokens outside the top-30 to `-inf`. After softmax these become `0` probability — they **cannot be sampled**.

This prevents the model from generating extremely rare or incoherent tokens even with high temperature.

### 6.3 Sampling vs Argmax

```
# Old (greedy argmax) → always same output, no variation:
next_token = torch.argmax(logits).item()

# New (multinomial sampling) → varied natural output:
probs      = F.softmax(logits, dim=-1)
next_token = torch.multinomial(probs, num_samples=1).item()
```

`multinomial` randomly draws from the probability distribution. If the model says `["the"=40%, "a"=30%, "this"=15% ...]`, then 40% of the time it picks "the", 30% of the time "a", etc.

---

## 7. Parameter Count

For default config (`embed_size=256, num_heads=4, num_layers=4, vocab=20001`):

| Component | Parameters |
|-----------|-----------|
| Token Embedding `[20001, 256]` | 5,120,256 |
| Position Embedding `[512, 256]` | 131,072 |
| Transformer Layers × 4 | ~10,000,000 |
| Output Linear `[256, 20001]` | 5,120,257 |
| **Total** | **~15.7M** |

---

## 8. Memory Layout

**Training (GPU, batch=32, block=128):**

| Tensor | Shape | Memory (fp32) |
|--------|-------|--------------|
| Input `x` | `[32, 128]` | 16 KB |
| Embeddings | `[32, 128, 256]` | 4 MB |
| Attention QKV per layer | `[32, 128, 256]×3` | 12 MB |
| Logits | `[32, 128, 20001]` | 327 MB |
| Model weights | — | ~63 MB |

> The logit tensor is the largest memory consumer. With AMP (fp16) this halves to ~163 MB.
