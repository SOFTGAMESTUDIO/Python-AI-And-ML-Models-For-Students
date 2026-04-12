from pathlib import Path


def ensure_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
