from __future__ import annotations

from pathlib import Path

import processor
from services.csv_output_service import write_csv_to_output
from services.paths import input_dir
from ui import AppView

_INPUT_DIR = input_dir()
_TAGGED_INPUT_HINT = "Supports tagged cells with == and !!"


def _eqparam_header_source() -> Path:
    """Prefer ``input/Eqparam.csv``; fall back to ``input/EQPARAM.csv`` for the header row only."""
    for name in ("Eqparam.csv", "EQPARAM.csv"):
        p = input_dir() / name
        if p.is_file():
            return p
    return input_dir() / "Eqparam.csv"


def handle(file_stem: str, view: AppView) -> None:
    stem = file_stem.strip()
    if not stem:
        view.set_status("Enter an input file name")
        return

    grid_path = _INPUT_DIR / f"{stem}.csv"
    out_name = f"outputEquipImport{stem}.csv"

    view.set_status("Wait...")
    try:
        header, rows = processor.process_grid_to_equip_rows(grid_path, _eqparam_header_source())
        written = write_csv_to_output(out_name, rows, header=header)
        view.set_status(f"Wrote {written.name} ({len(rows)} row(s))")
        print(
            f"Equip Create: {grid_path.name} -> {written.name}, rows={len(rows)}. "
            f"{_TAGGED_INPUT_HINT} (Is Tag=TRUE)."
        )
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"Equip Create: {exc.message}")
    except PermissionError:
        msg = f"Cannot write {out_name} (file is open or locked)"
        view.set_status(msg)
        print(f"Equip Create: {msg}")
    except OSError as exc:
        msg = f"File error for {out_name}: {exc}"
        view.set_status(msg)
        print(f"Equip Create: {msg}")
