# src/model.py

import torch
import torch.nn as nn

class MiniGPT(nn.Module):
    def __init__(self, vocab_size, embed_size, heads, layers):
        super().__init__()

        self.embed = nn.Embedding(vocab_size, embed_size)
        self.pos = nn.Embedding(512, embed_size)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_size,
            nhead=heads,
            batch_first=True
        )

        self.transformer = nn.TransformerEncoder(encoder_layer, layers)
        self.fc = nn.Linear(embed_size, vocab_size)

    def forward(self, x):
        B, T = x.shape
        positions = torch.arange(0, T, device=x.device).unsqueeze(0).expand(B, T)
        
        # Causal mask ensures the model only looks at past and current tokens, not future
        mask = nn.Transformer.generate_square_subsequent_mask(T).to(x.device)

        x = self.embed(x) + self.pos(positions)
        x = self.transformer(x, mask=mask, is_causal=True)
        return self.fc(x)