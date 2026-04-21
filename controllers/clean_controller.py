# clean_controller — CSV clean action (wired from main.py).

from __future__ import annotations

from pathlib import Path

from ui import AppView

_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = _ROOT / "input" / "raw.csv"
OUTPUT_CSV = _ROOT / "output" / "cleaned.csv"


def handle(search_text: str, view: AppView) -> None:
    view.set_status("Processing...")
    print(f"{INPUT_CSV} -> {OUTPUT_CSV}, search={search_text!r}")
