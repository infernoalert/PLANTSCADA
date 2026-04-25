# tab_viewr_controller — TabViewr: EQPARAM grid export to output/*.csv

from __future__ import annotations

import processor
from controllers import alarm_controller
from services.csv_output_service import write_csv_to_output
from services.paths import input_dir
from ui import AppView

_EQPARAM = input_dir() / "EQPARAM.csv"
_VARIABLE = input_dir() / "VARIABLE.csv"


def handle(search_text: str, view: AppView) -> None:
    if not search_text.strip():
        view.set_status("Enter a search tag")
        return

    view.set_status("Wait...")
    try:
        alarm_tag_to_comment = alarm_controller.load_alarm_tag_comment_map()
        sheets = processor.process_eqparam_tabviewr(
            _EQPARAM, search_text, _VARIABLE, alarm_tag_to_comment
        )
        if not sheets:
            view.set_status("No Tab/Status sheets to export")
            return
        for stem, rows in sheets:
            write_csv_to_output(f"{stem}.csv", rows, header=None)
        view.set_status(f"Wrote {len(sheets)} file(s)")
        print(f"TabViewr: wrote {len(sheets)} file(s) for search={search_text!r}")
    except processor.EqparamProcessingError as exc:
        view.set_status(exc.message)
        print(f"TabViewr: {exc.message}")
