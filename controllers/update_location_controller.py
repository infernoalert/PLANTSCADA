from __future__ import annotations

import processor
from services.paths import input_dir, output_dir
from ui import AppView

_INPUT_DIR = input_dir()
_OUTPUT_DIR = output_dir()
_VARIABLE = _INPUT_DIR / "VARIABLE.csv"


def handle(file_stem: str, view: AppView) -> None:
    stem = file_stem.strip()
    if not stem:
        view.set_status("Enter an input file name")
        return

    input_path = _INPUT_DIR / f"{stem}.csv"
    output_path = _OUTPUT_DIR / f"update{stem}.csv"

    view.set_status("Wait...")
    try:
        checked_cells, updated_tokens, fault_pairs = processor.fix_status_locations_in_output_csv(
            input_path, output_path, _VARIABLE
        )
        view.set_status(
            f"Wrote {output_path.name} ({updated_tokens} updates, {fault_pairs} faults in {checked_cells} cells)"
        )
        print(
            f"updateLocation: {input_path.name} -> {output_path.name}, "
            f"updates={updated_tokens}, faults={fault_pairs}, checked_cells={checked_cells}"
        )
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"updateLocation: {exc.message}")
    except PermissionError:
        msg = f"Cannot write {output_path} (file is open or locked)"
        view.set_status(msg)
        print(f"updateLocation: {msg}")
    except OSError as exc:
        msg = f"File error for {output_path.name}: {exc}"
        view.set_status(msg)
        print(f"updateLocation: {msg}")
