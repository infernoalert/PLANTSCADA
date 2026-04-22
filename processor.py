# ==========================================
# processor.py - THE MODEL (Data Engine)
# ==========================================
# Pandas logic for SCADA CSVs. No Tkinter.

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

_TAB_TITLE_RE = re.compile(r"^Tab_v(\d+)_h(\d+)_Title$", re.IGNORECASE)
_STATUS_CELL_RE = re.compile(
    r"^Status_v(\d+)_h(\d+)_r(\d+)_c(\d+)_(.+)$",
    re.IGNORECASE,
)
_WIN_INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')


class EqparamProcessingError(Exception):
    """Raised when EQPARAM.csv cannot be read or required columns are missing."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _read_eqparam_csv(path: Path) -> pd.DataFrame:
    last_err: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_err = exc
        except pd.errors.ParserError as exc:
            raise EqparamProcessingError(f"Invalid CSV: {exc}") from exc
    raise EqparamProcessingError(f"Could not decode CSV (tried utf-8-sig, utf-8, latin-1): {last_err}")


def _resolve_column_ci(columns: pd.Index, logical_name: str) -> str:
    want = logical_name.lower()
    for col in columns:
        if str(col).strip().lower() == want:
            return str(col)
    raise EqparamProcessingError(f'Missing required column "{logical_name}" (case-insensitive match).')


def _cell_str(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (ValueError, TypeError):
        pass
    return str(value)


def process_eqparam_dedupe(path: Path, needle: str) -> Tuple[List[str], List[List[str]]]:
    """
    Read EQPARAM-style CSV. Output **only** rows where both ``Equipment`` and ``Name``
    contain ``needle`` (substring, case-insensitive); among those, drop duplicate
    ``(Equipment, Name)`` pairs keeping the first. Rows that do not match both are
    omitted from the output (not written).
    """
    needle = needle.strip()
    if not needle:
        raise EqparamProcessingError("Search text is empty.")

    if not path.is_file():
        raise EqparamProcessingError(f"Missing file: {path}")

    df = _read_eqparam_csv(path)
    if df.empty:
        return [str(c) for c in df.columns.tolist()], []

    equip_col = _resolve_column_ci(df.columns, "Equipment")
    name_col = _resolve_column_ci(df.columns, "Name")

    eq_mask = df[equip_col].astype(str).str.contains(needle, case=False, na=False, regex=False)
    name_mask = df[name_col].astype(str).str.contains(needle, case=False, na=False, regex=False)
    both_mask = eq_mask & name_mask

    matched = df.loc[both_mask]
    out = matched.drop_duplicates(subset=[equip_col, name_col], keep="first")

    header = [str(c) for c in out.columns.tolist()]
    rows = [[_cell_str(v) for v in row] for row in out.to_numpy()]
    return header, rows


def _slug_sheet_stem(raw_title: str, v: int, h: int) -> str:
    s = _cell_str(raw_title).strip().lower().replace(" ", "_")
    s = _WIN_INVALID_CHARS.sub("", s)
    s = re.sub(r"_+", "_", s).strip("._")
    if not s:
        s = f"sheet_v{v}_h{h}"
    return s[:80]


def process_eqparam_tabviewr(path: Path, needle: str) -> List[Tuple[str, List[str], List[List[str]]]]:
    """
    Filter EQPARAM rows by Equipment substring; for each (v, h) with Tab_v{v}_h{h}_Title
    (sheet name from Value) and Status_v{v}_h{h}_r*c* cells, build a dense grid. Multiple
    values for the same (r, c) are joined with ``||``.
    Returns list of (filename_stem_without_csv, header, rows).
    """
    needle = needle.strip()
    if not needle:
        raise EqparamProcessingError("Search text is empty.")

    if not path.is_file():
        raise EqparamProcessingError(f"Missing file: {path}")

    df = _read_eqparam_csv(path)
    if df.empty:
        return []

    equip_col = _resolve_column_ci(df.columns, "Equipment")
    name_col = _resolve_column_ci(df.columns, "Name")
    value_col = _resolve_column_ci(df.columns, "Value")

    eq_mask = df[equip_col].astype(str).str.contains(needle, case=False, na=False, regex=False)
    filtered = df.loc[eq_mask]
    if filtered.empty:
        return []

    titles: Dict[Tuple[int, int], str] = {}
    for _, row in filtered.iterrows():
        name = str(row[name_col]).strip()
        m = _TAB_TITLE_RE.match(name)
        if m:
            v, h = int(m.group(1)), int(m.group(2))
            key = (v, h)
            if key not in titles:
                titles[key] = _cell_str(row[value_col])

    cell_lists: DefaultDict[Tuple[int, int], DefaultDict[Tuple[int, int], List[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for _, row in filtered.iterrows():
        name = str(row[name_col]).strip()
        m = _STATUS_CELL_RE.match(name)
        if m:
            v, h = int(m.group(1)), int(m.group(2))
            r, c = int(m.group(3)), int(m.group(4))
            cell_lists[(v, h)][(r, c)].append(_cell_str(row[value_col]))

    sheets: List[Tuple[str, List[str], List[List[str]]]] = []
    used_stems: set[str] = set()

    for (v, h), grid in sorted(cell_lists.items()):
        if not grid:
            continue
        if (v, h) not in titles:
            continue

        base_stem = _slug_sheet_stem(titles[(v, h)], v, h)
        stem = base_stem
        if stem in used_stems:
            stem = f"{base_stem}_v{v}_h{h}"[:80]
        used_stems.add(stem)

        rs = [rc[0] for rc in grid.keys()]
        cs = [rc[1] for rc in grid.keys()]
        min_r, max_r = min(rs), max(rs)
        min_c, max_c = min(cs), max(cs)

        header = [f"c{j}" for j in range(min_c, max_c + 1)]
        rows: List[List[str]] = []
        for r in range(min_r, max_r + 1):
            row_out: List[str] = []
            for c in range(min_c, max_c + 1):
                parts = grid.get((r, c), [])
                row_out.append("||".join(parts) if parts else "")
            rows.append(row_out)

        sheets.append((stem, header, rows))

    return sheets
