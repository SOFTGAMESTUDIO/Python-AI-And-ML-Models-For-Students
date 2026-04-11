# src/tokenizer.py

import json
from collections import Counter


class Tokenizer:
    """
    Word-level tokenizer with special tokens: <pad>, <unk>, <eos>.

    Special token layout (backward compatible):
        <pad> = 0            (padding / unknown fallback - always index 0)
        Words start at 1     (matching trained model embedding layout)
        <unk> = vocab_size   (appended after all word tokens)
        <eos> = vocab_size+1 (appended after <unk>)
    """

    def __init__(self):
        self.stoi = {}   # string -> index
        self.itos = {}   # index  -> string

    def build_vocab(self, texts, vocab_size=20000):
        """
        Build vocabulary from a list of text strings.

        Index layout:
          - 0         : <pad>
          - 1 .. N    : top N most frequent words
          - N+1       : <unk>
          - N+2       : <eos>

        Args:
            texts     : List of raw text strings.
            vocab_size: Max number of WORD tokens (excl. special tokens).
        """
        # Count word frequencies across all texts
        all_words = " ".join(texts).split()
        freq = Counter(all_words).most_common(vocab_size)

        # Assign <pad> = 0, words start from 1
        self.stoi = {"<pad>": 0}
        for i, (word, _) in enumerate(freq):
            self.stoi[word] = i + 1

        # Append <unk> and <eos> at the end (beyond all word indices)
        next_idx = len(self.stoi)
        self.stoi["<unk>"] = next_idx
        self.stoi["<eos>"] = next_idx + 1

        # Build reverse lookup
        self.itos = {idx: word for word, idx in self.stoi.items()}

    def encode(self, text):
        """
        Encode a string into a list of integer token IDs.
        Unknown words map to <unk>.
        """
        unk_id = self.stoi.get("<unk>", 0)
        return [self.stoi.get(w, unk_id) for w in text.split()]

    def decode(self, tokens):
        """
        Decode a list of token IDs back to a human-readable string.
        Skips <pad>, <unk>, and <eos> special tokens from the output.
        """
        skip = {self.stoi.get(t, -1) for t in ("<pad>", "<unk>", "<eos>")}
        words = [self.itos[t] for t in tokens if t in self.itos and t not in skip]
        return " ".join(words)

    def patch_special_tokens(self):
        """
        Inject <unk> and <eos> into an already-loaded vocab (e.g. from old saved
        vocab.json that only had <pad>). Places them after the last word token.
        Safe to call multiple times.
        """
        if "<unk>" not in self.stoi:
            next_idx = max(self.itos.keys()) + 1
            self.stoi["<unk>"] = next_idx
            self.itos[next_idx] = "<unk>"
            next_idx += 1
            self.stoi["<eos>"] = next_idx
            self.itos[next_idx] = "<eos>"

    def save(self, path):
        """Save vocabulary mapping to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"stoi": self.stoi}, f, ensure_ascii=False, indent=2)

    def load(self, path):
        """Load vocabulary mapping from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.stoi = data["stoi"]
        # JSON keys are always strings; convert int-valued indices correctly
        self.itos = {int(v): str(k) for k, v in self.stoi.items()}
        # Always ensure special tokens exist without breaking old vocab
        self.patch_special_tokens()