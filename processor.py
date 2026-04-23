# ==========================================
# processor.py - THE MODEL (Data Engine)
# ==========================================
# Pandas logic for SCADA CSVs. No Tkinter.

from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple

import pandas as pd

_TAB_TITLE_RE = re.compile(r"^Tab_v(\d+)_h(\d+)_Title$", re.IGNORECASE)
_STATUS_CELL_RE = re.compile(
    r"^Status_v(\d+)_h(\d+)_r(\d+)_c(\d+)_(.+)$",
    re.IGNORECASE,
)
_STATUS_TOKEN_RE = re.compile(
    r"(Status_v(\d+)_h(\d+)_r)(\d+)(_c)(\d+)(_.+)",
    re.IGNORECASE,
)
_TAG_COMMENT_PAIR_RE = re.compile(
    r"^(?P<prefix>.*?::\s*)?(?P<tag>[^=|]+?)\s*(?P<fault>\*\*FAULT\*\*\s*)?==\s*(?P<comment>.*)$"
)
_WIN_INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')
_FAULT_MARKER = "**FAULT**"
_TABVIEWR_SEP = " :: "
_TAG_VALUE_SEP = " == "


class EqparamProcessingError(Exception):
    """Raised when EQPARAM.csv cannot be read or required columns are missing."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _read_csv_with_encodings(path: Path) -> pd.DataFrame:
    last_err: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_err = exc
        except pd.errors.ParserError as exc:
            raise EqparamProcessingError(f"Invalid CSV: {exc}") from exc
    raise EqparamProcessingError(f"Could not decode CSV (tried utf-8-sig, utf-8, latin-1): {last_err}")


def _read_eqparam_csv(path: Path) -> pd.DataFrame:
    return _read_csv_with_encodings(path)


def _resolve_column_ci(columns: pd.Index, logical_name: str) -> str:
    want = logical_name.lower()
    for col in columns:
        if str(col).strip().lower() == want:
            return str(col)
    raise EqparamProcessingError(f'Missing required column "{logical_name}" (case-insensitive match).')


def _parse_is_tag(value: object) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        pass
    if isinstance(value, bool):
        return value
    s = str(value).strip().upper()
    return s in ("TRUE", "1", "YES", "Y", "T")


def _resolve_variable_tag_column(columns: pd.Index) -> str:
    for logical in ("Tag Name", "Tagname"):
        try:
            return _resolve_column_ci(columns, logical)
        except EqparamProcessingError:
            continue
    raise EqparamProcessingError('VARIABLE.csv: missing "Tag Name" or "Tagname" column.')


def _load_tag_comment_map(variable_path: Path) -> Dict[str, str]:
    """First Tag Name wins. Returns empty dict if VARIABLE.csv is absent."""
    if not variable_path.is_file():
        return {}
    df = _read_csv_with_encodings(variable_path)
    if df.empty:
        return {}
    tag_col = _resolve_variable_tag_column(df.columns)
    comment_col = _resolve_column_ci(df.columns, "Comment")
    out: Dict[str, str] = {}
    for _, row in df.iterrows():
        tag = _cell_str(row[tag_col]).strip()
        if not tag or tag in out:
            continue
        out[tag] = _cell_str(row[comment_col]).strip()
    return out


def _tabviewr_status_cell_text(
    row: pd.Series,
    *,
    name_col: str,
    value_col: str,
    is_tag_col: str,
    tag_to_comment: Dict[str, str],
) -> str:
    name = _cell_str(row[name_col]).strip()
    value = _cell_str(row[value_col]).strip()
    if _parse_is_tag(row[is_tag_col]):
        if not value:
            return ""
        resolved = tag_to_comment.get(value, value)
        return f"{name} :: {value} == {resolved}"
    return f"{name} :: {value}" if (name or value) else ""


def _cell_str(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (ValueError, TypeError):
        pass
    return str(value)


def process_eqparam_equipment_filter(path: Path, needle: str) -> Tuple[List[str], List[List[str]]]:
    """
    Read EQPARAM-style CSV. Output **only** rows whose ``Equipment`` column contains
    ``needle`` (substring, case-insensitive). All original columns are preserved; no
    deduplication.
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
    mask = df[equip_col].astype(str).str.contains(needle, case=False, na=False, regex=False)
    out = df.loc[mask]

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


def process_eqparam_tabviewr(
    path: Path,
    needle: str,
    variable_path: Optional[Path] = None,
) -> List[Tuple[str, List[List[str]]]]:
    """
    Filter EQPARAM rows by Equipment substring; for each (v, h) with Tab_v{v}_h{h}_Title
    (sheet name from Value) and Status_v{v}_h{h}_r*c* cells, build a dense grid. Multiple
    values for the same (r, c) are joined with ``||``.

    Status cell text: if ``Is Tag`` is true, output ``Name :: Value == resolved`` where
    ``resolved`` is VARIABLE.csv ``Comment`` for ``Value`` as Tag Name (else ``Value``);
    if false, output ``Name :: Value``.

    Returns list of (filename_stem_without_csv, rows) — no column header row; data only.
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
    is_tag_col = _resolve_column_ci(df.columns, "Is Tag")

    var_path = variable_path if variable_path is not None else path.parent / "VARIABLE.csv"
    tag_to_comment = _load_tag_comment_map(var_path)

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
            text = _tabviewr_status_cell_text(
                row,
                name_col=name_col,
                value_col=value_col,
                is_tag_col=is_tag_col,
                tag_to_comment=tag_to_comment,
            )
            cell_lists[(v, h)][(r, c)].append(text)

    sheets: List[Tuple[str, List[List[str]]]] = []
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

        rows: List[List[str]] = []
        for r in range(min_r, max_r + 1):
            row_out: List[str] = []
            for c in range(min_c, max_c + 1):
                parts = grid.get((r, c), [])
                row_out.append("||".join(parts) if parts else "")
            rows.append(row_out)

        sheets.append((stem, rows))

    return sheets


def _mark_fault_for_invalid_tag_comment(
    cell_text: str, tag_to_comment: Dict[str, str]
) -> Tuple[str, int]:
    parts = cell_text.split("||")
    updated_parts: List[str] = []
    faults_added = 0

    for part in parts:
        piece = part
        m = _TAG_COMMENT_PAIR_RE.match(piece)
        if not m:
            updated_parts.append(piece)
            continue

        tag = m.group("tag").strip()
        comment = m.group("comment").strip()
        has_fault = m.group("fault") is not None
        expected_comment = tag_to_comment.get(tag)
        is_valid = expected_comment is not None and expected_comment.strip() == comment

        if is_valid or has_fault:
            updated_parts.append(piece)
            continue

        prefix = m.group("prefix") or ""
        updated_parts.append(f"{prefix}{tag} **FAULT** == {comment}")
        faults_added += 1

    return "||".join(updated_parts), faults_added


def fix_status_locations_in_output_csv(
    input_path: Path, output_path: Path, variable_path: Optional[Path] = None
) -> Tuple[int, int, int]:
    """
    Rewrite embedded Status_v..._rX_cY_... tokens in each cell so r/c match the
    cell's 1-based row/column position in the CSV.

    Returns (checked_cells, updated_tokens, fault_pairs).
    """
    if not input_path.is_file():
        raise EqparamProcessingError(f"Missing file: {input_path}")
    var_path = variable_path if variable_path is not None else input_path.parent / "VARIABLE.csv"
    tag_to_comment = _load_tag_comment_map(var_path)

    last_err: Exception | None = None
    df: Optional[pd.DataFrame] = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(input_path, encoding=encoding, header=None, dtype=str, keep_default_na=False)
            break
        except UnicodeDecodeError as exc:
            last_err = exc
        except pd.errors.ParserError as exc:
            raise EqparamProcessingError(f"Invalid CSV: {exc}") from exc
    if df is None:
        raise EqparamProcessingError(
            f"Could not decode CSV (tried utf-8-sig, utf-8, latin-1): {last_err}"
        )
    if df.empty:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, header=False, encoding="utf-8")
        return 0, 0, 0

    checked_cells = 0
    updated_tokens = 0
    fault_pairs = 0

    for row_index in range(len(df.index)):
        for col_index in range(len(df.columns)):
            value = _cell_str(df.iat[row_index, col_index])
            if not value:
                continue
            checked_cells += 1

            actual_r = row_index + 1
            actual_c = col_index + 1

            def _replace(match: re.Match[str]) -> str:
                nonlocal updated_tokens
                existing_r = int(match.group(4))
                existing_c = int(match.group(6))
                if existing_r == actual_r and existing_c == actual_c:
                    return match.group(0)
                updated_tokens += 1
                return f"{match.group(1)}{actual_r}{match.group(5)}{actual_c}{match.group(7)}"

            rewritten = _STATUS_TOKEN_RE.sub(_replace, value)
            rewritten, faults_added = _mark_fault_for_invalid_tag_comment(rewritten, tag_to_comment)
            fault_pairs += faults_added
            if rewritten != value:
                df.iat[row_index, col_index] = rewritten

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, header=False, encoding="utf-8")
    return checked_cells, updated_tokens, fault_pairs


def _read_first_csv_line_as_row(path: Path) -> List[str]:
    """Read the first physical line of a CSV file and parse it as one row (for EQPARAM header)."""
    if not path.is_file():
        raise EqparamProcessingError(f"Missing file: {path}")
    last_err: Exception | None = None
    first_line: str | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with path.open(encoding=encoding, newline="") as f:
                first_line = f.readline()
            break
        except UnicodeDecodeError as exc:
            last_err = exc
    if first_line is None:
        raise EqparamProcessingError(
            f"Could not decode header file (tried utf-8-sig, utf-8, latin-1): {last_err}"
        )
    if not first_line.strip():
        raise EqparamProcessingError(f"Empty or whitespace-only file: {path}")
    reader = csv.reader(io.StringIO(first_line))
    try:
        row = next(reader)
    except StopIteration as exc:
        raise EqparamProcessingError(f"Could not read CSV header from {path}") from exc
    return [str(c).strip() for c in row]


def _read_grid_dataframe(path: Path) -> pd.DataFrame:
    last_err: Exception | None = None
    df: pd.DataFrame | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=encoding, header=None, dtype=str, keep_default_na=False)
            break
        except UnicodeDecodeError as exc:
            last_err = exc
        except pd.errors.ParserError as exc:
            raise EqparamProcessingError(f"Invalid CSV: {exc}") from exc
    if df is None:
        raise EqparamProcessingError(
            f"Could not decode CSV (tried utf-8-sig, utf-8, latin-1): {last_err}"
        )
    return df


def _parse_tabviewr_fragment_to_fields(fragment: str) -> Tuple[str, str, str, str, str, str, str]:
    """
    Inverse of TabViewr cell text: ``Name :: Value`` or ``Name :: Value == resolved``.

    Returns ``(cluster, equipment, name, value, is_tag, comment, project)`` with cluster,
    equipment, project always empty (caller maps to header order).
    """
    piece = fragment.strip()
    if not piece:
        raise EqparamProcessingError("Internal error: empty fragment")
    if _TABVIEWR_SEP not in piece:
        raise EqparamProcessingError(
            f"Expected {_TABVIEWR_SEP!r} in cell text: {piece[:120]!r}"
            + ("…" if len(piece) > 120 else "")
        )
    name, remainder = piece.split(_TABVIEWR_SEP, 1)
    name = name.strip()
    remainder = remainder.strip()
    sep_idx = remainder.find(_TAG_VALUE_SEP)
    if sep_idx != -1:
        value = remainder[:sep_idx].strip()
        comment = remainder[sep_idx + len(_TAG_VALUE_SEP) :].strip()
        is_tag = "TRUE"
    else:
        value = remainder
        comment = ""
        is_tag = "FALSE"
    return "", "", name, value, is_tag, comment, ""


def _equip_row_from_header(
    header: List[str],
    *,
    cluster: str,
    equipment: str,
    name: str,
    value: str,
    is_tag: str,
    comment: str,
    project: str,
) -> List[str]:
    """Map logical fields to one output row following ``header`` column names (case-insensitive)."""
    logical: Dict[str, str] = {
        "cluster": cluster,
        "equipment": equipment,
        "name": name,
        "value": value,
        "is tag": is_tag,
        "comment": comment,
        "project": project,
    }
    out: List[str] = []
    for col in header:
        key = str(col).strip().lower()
        out.append(logical.get(key, ""))
    return out


def process_grid_to_equip_rows(
    grid_path: Path,
    eqparam_header_source: Path,
) -> Tuple[List[str], List[List[str]]]:
    """
    Read a headerless grid (e.g. ``input/<stem>.csv``), convert TabViewr-style cell text
    into EQPARAM-shaped rows. Header columns are taken from the first line of
    ``eqparam_header_source`` (read-only).

    - Any cell containing ``**FAULT**`` raises ``EqparamProcessingError`` (no output).
    - ``||`` in a cell splits into multiple fragments → one row per fragment.
    """
    header = _read_first_csv_line_as_row(eqparam_header_source)
    if not header:
        raise EqparamProcessingError(f"No columns in header file: {eqparam_header_source}")

    if not grid_path.is_file():
        raise EqparamProcessingError(f"Missing file: {grid_path}")

    df = _read_grid_dataframe(grid_path)
    if df.empty:
        return header, []

    for ri in range(len(df.index)):
        for ci in range(len(df.columns)):
            raw = _cell_str(df.iat[ri, ci])
            if not raw:
                continue
            if _FAULT_MARKER in raw:
                raise EqparamProcessingError(
                    "Input contains **FAULT** markers; fix the grid before Equip Create."
                )

    rows: List[List[str]] = []
    for ri in range(len(df.index)):
        for ci in range(len(df.columns)):
            raw = _cell_str(df.iat[ri, ci])
            if not raw:
                continue
            for segment in raw.split("||"):
                seg = segment.strip()
                if not seg:
                    continue
                cluster, equipment, name, value, is_tag, comment, project = _parse_tabviewr_fragment_to_fields(
                    seg
                )
                rows.append(
                    _equip_row_from_header(
                        header,
                        cluster=cluster,
                        equipment=equipment,
                        name=name,
                        value=value,
                        is_tag=is_tag,
                        comment=comment,
                        project=project,
                    )
                )

    return header, rows
