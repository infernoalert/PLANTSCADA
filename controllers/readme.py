# Load static page text from controllers/Readme/ (all readme assets live there).

from __future__ import annotations

from services.paths import readme_dir


def load_asset(filename: str) -> str:
    path = readme_dir() / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return f"(Missing: Readme/{filename})"
