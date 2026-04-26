# search_variable_controller — resolve xx==Comment using VARIABLE.csv

from __future__ import annotations

import processor
from services.csv_output_service import write_csv_to_output
from services.paths import input_dir
from ui import AppView

_SEARCHVAR = input_dir() / "searchvar.csv"
_VARIABLE = input_dir() / "VARIABLE.csv"
_OUTPUT_NAME = "varsearchout.csv"


def handle(group_filter: str, view: AppView) -> None:
    if not group_filter.strip():
        view.set_status("Enter a group filter (substring for Tag Name)")
        return

    view.set_status("Wait...")
    try:
        rows = processor.process_searchvar_substitution(_SEARCHVAR, _VARIABLE, group_filter)
        written = write_csv_to_output(_OUTPUT_NAME, rows, header=None)
        view.set_status(f"Wrote {written.name} ({len(rows)} row(s))")
        print(
            f"SearchVariable: {_SEARCHVAR.name} + {_VARIABLE.name} -> {written.name}, "
            f"rows={len(rows)}, group={group_filter!r}"
        )
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"SearchVariable: {exc.message}")
    except PermissionError:
        msg = f"Cannot write {_OUTPUT_NAME} (file is open or locked)"
        view.set_status(msg)
        print(f"SearchVariable: {msg}")
    except OSError as exc:
        msg = f"File error for {_OUTPUT_NAME}: {exc}"
        view.set_status(msg)
        print(f"SearchVariable: {msg}")
