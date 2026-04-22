# clean_controller — CSV clean action (wired from main.py).

from __future__ import annotations

from pathlib import Path

import processor
from services.csv_output_service import write_csv_to_output
from ui import AppView

_ROOT = Path(__file__).resolve().parent.parent
EQPARAM_CSV = _ROOT / "input" / "EQPARAM.csv"


def handle(search_text: str, view: AppView) -> None:
    if not search_text.strip():
        view.set_status("Enter a search tag")
        return

    view.set_status("Wait...")
    try:
        header, rows = processor.process_eqparam_equipment_filter(EQPARAM_CSV, search_text)
        written = write_csv_to_output("cleanEqparam.csv", rows, header=header)
        view.set_status("Wrote cleanEqparam.csv")
        print(f"{EQPARAM_CSV} -> {written}, rows={len(rows)}")
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"EQPARAM clean: {exc.message}")
