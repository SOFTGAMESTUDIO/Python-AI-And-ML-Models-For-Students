# src/dataset.py

import torch
from torch.utils.data import Dataset

class TextDataset(Dataset):
    def __init__(self, texts, tokenizer, block_size):
        self.texts = texts
        self.tokenizer = tokenizer
        self.block_size = block_size

    def __len__(self):
        # Rough estimate (not exact, but works)
        return len(self.texts) * 10

    def __getitem__(self, idx):
        # Pick random text (instead of storing all)
        text = self.texts[idx % len(self.texts)]

        tokens = self.tokenizer.encode(text)

        # Handle short texts
        if len(tokens) < self.block_size + 1:
            tokens = tokens + [0] * (self.block_size + 1 - len(tokens))

        # Random slice
        start = torch.randint(0, max(1, len(tokens) - self.block_size - 1), (1,)).item()

        x = tokens[start:start + self.block_size]
        y = tokens[start + 1:start + self.block_size + 1]

        return torch.tensor(x), torch.tensor(y)