# Create CSV files under the project output/ directory.

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence

from services.paths import output_dir as runtime_output_dir


def output_dir() -> Path:
    """Ensure output/ exists and return its path."""
    out = runtime_output_dir()
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_csv_to_output(
    filename: str,
    rows: Iterable[Sequence[str]],
    *,
    header: Sequence[str] | None = None,
) -> Path:
    """
    Create or overwrite a UTF-8 CSV in output/.

    ``filename`` must be a plain name (e.g. ``cleaned.csv``), not a path.
    """
    name = filename.strip()
    if not name or "/" in name or "\\" in name or ".." in name:
        raise ValueError("filename must be a single file name under output/, no paths")

    dest = output_dir() / name
    row_list = [list(r) for r in rows]

    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header is not None:
            writer.writerow(list(header))
        writer.writerows(row_list)

    return dest
