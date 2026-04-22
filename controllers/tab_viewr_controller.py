# tab_viewr_controller — TabViewr: EQPARAM grid export to output/*.csv

from __future__ import annotations

from pathlib import Path

import processor
from services.csv_output_service import write_csv_to_output
from ui import AppView

_EQPARAM = Path(__file__).resolve().parent.parent / "input" / "EQPARAM.csv"


def handle(search_text: str, view: AppView) -> None:
    if not search_text.strip():
        view.set_status("Enter a search tag")
        return

    view.set_status("Processing...")
    try:
        sheets = processor.process_eqparam_tabviewr(_EQPARAM, search_text)
        if not sheets:
            view.set_status("No Tab/Status sheets to export")
            return
        for stem, header, rows in sheets:
            write_csv_to_output(f"{stem}.csv", rows, header=header)
        view.set_status(f"Wrote {len(sheets)} sheet(s)")
        print(f"TabViewr: wrote {len(sheets)} file(s) for search={search_text!r}")
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"TabViewr: {exc.message}")
