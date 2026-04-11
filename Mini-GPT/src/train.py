# src/train.py

import os
import torch
from torch.utils.data import DataLoader
from datasets import load_dataset

from tokenizer import Tokenizer
from dataset import TextDataset
from model import MiniGPT
from config import Config
from utils import clean_text


def main():
    # ==============================
    # 1. DEVICE
    # ==============================
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Using device: {device}")

    # ==============================
    # 2. LOAD DATA
    # ==============================
    print("📥 Loading dataset (streaming)...")

    web = load_dataset(
        "Skylion007/openwebtext",
        split="train",
        streaming=True
    )

    wiki = load_dataset(
        "Salesforce/wikitext",
        "wikitext-2-raw-v1",
        split="train"
    )

    MAX_SAMPLES = 20000
    texts = []

    for i, x in enumerate(web):
        if i >= MAX_SAMPLES:
            break
        if x["text"].strip():
            texts.append(clean_text(x["text"]))

    for x in wiki:
        if x["text"].strip():
            texts.append(clean_text(x["text"]))

    print(f"✅ Total samples: {len(texts)}")

    # ==============================
    # 3. TOKENIZER
    # ==============================
    print("🔤 Building tokenizer...")

    tokenizer = Tokenizer()
    tokenizer.build_vocab(texts, vocab_size=Config.vocab_size)

    print(f"Vocab size: {len(tokenizer.stoi)}")

    # Ensure outputs dir exists and save vocab
    os.makedirs("outputs", exist_ok=True)
    tokenizer.save("outputs/vocab.json")
    print("💾 Tokenizer vocab saved in outputs/vocab.json")

    # ==============================
    # 4. DATASET
    # ==============================
    dataset = TextDataset(texts, tokenizer, Config.block_size)

    loader = DataLoader(
        dataset,
        batch_size=Config.batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )

    print(f"📦 Batches: {len(loader)}")

    # ==============================
    # 5. MODEL
    # ==============================
    model = MiniGPT(
        len(tokenizer.stoi),
        Config.embed_size,
        Config.num_heads,
        Config.num_layers
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=Config.lr)
    loss_fn = torch.nn.CrossEntropyLoss()

    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler(device=device.type, enabled=use_amp)

    # ==============================
    # 6. TRAIN LOOP
    # ==============================
    print("🔥 Training started...\n")

    for epoch in range(Config.epochs):
        total_loss = 0

        for step, (x, y) in enumerate(loader):

            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            with torch.amp.autocast(device_type=device.type, enabled=use_amp):
                logits = model(x)
                loss = loss_fn(
                    logits.view(-1, len(tokenizer.stoi)),
                    y.view(-1)
                )

            optimizer.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()

            if step % 100 == 0:
                print(f"Epoch {epoch+1} | Step {step} | Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(loader)
        print(f"\n✅ Epoch {epoch+1} Done | Avg Loss: {avg_loss:.4f}\n")

    # ==============================
    # 7. SAVE
    # ==============================
    torch.save(model.state_dict(), "outputs/model.pt")
    print("💾 Model saved!")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()