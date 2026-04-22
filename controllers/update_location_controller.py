from __future__ import annotations

from pathlib import Path

import processor
from ui import AppView

_INPUT_DIR = Path(__file__).resolve().parent.parent / "input"
_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def handle(file_stem: str, view: AppView) -> None:
    stem = file_stem.strip()
    if not stem:
        view.set_status("Enter an input file name")
        return

    input_path = _INPUT_DIR / f"{stem}.csv"
    output_path = _OUTPUT_DIR / f"update{stem}.csv"

    view.set_status("Wait...")
    try:
        checked_cells, updated_tokens = processor.fix_status_locations_in_output_csv(input_path, output_path)
        view.set_status(
            f"Wrote {output_path.name} ({updated_tokens} updates in {checked_cells} cells)"
        )
        print(
            f"updateLocation: {input_path.name} -> {output_path.name}, "
            f"updates={updated_tokens}, checked_cells={checked_cells}"
        )
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"updateLocation: {exc.message}")
