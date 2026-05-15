# clean_controller — CSV clean action (wired from main.py).



from __future__ import annotations



import processor

from services.csv_output_service import write_csv_to_output

from services.paths import input_dir

from ui import AppView



_EQPARAM = input_dir() / "EQPARAM.csv"

_VARIABLE = input_dir() / "VARIABLE.csv"

_DIGALM = input_dir() / "DIGALM.csv"

_OUTPUT = "clean.csv"





def handle(search_text: str, view: AppView) -> None:

    if not search_text.strip():

        view.set_status("Enter a search tag")

        return



    view.set_status("Wait...")

    try:

        header, rows = processor.process_clean_combined(

            _EQPARAM, _VARIABLE, _DIGALM, search_text

        )

        written = write_csv_to_output(_OUTPUT, rows, header=header)

        counts = _row_counts_by_table(rows)

        view.set_status(

            f"Wrote {_OUTPUT} (EQPARAM: {counts['EQPARAM']}, "

            f"VARIABLE: {counts['VARIABLE']}, DIGIALARM: {counts['DIGIALARM']})"

        )

        print(f"Clean -> {written}, rows={len(rows)}, counts={counts}")

    except processor.EqparamProcessingError as exc:

        view.set_status(exc.message)

        print(f"Clean: {exc.message}")





def _row_counts_by_table(rows: list[list[str]]) -> dict[str, int]:

    counts = {"EQPARAM": 0, "VARIABLE": 0, "DIGIALARM": 0}

    for row in rows:

        if row and row[0] in counts:

            counts[row[0]] += 1

    return counts

