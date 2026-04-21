# Load static page text from controllers/Readme/ (all readme assets live there).

from __future__ import annotations

from pathlib import Path

_CONTROLLERS_DIR = Path(__file__).resolve().parent
_README_DIR = _CONTROLLERS_DIR / "Readme"


def load_asset(filename: str) -> str:
    path = _README_DIR / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return f"(Missing: Readme/{filename})"
