from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Tuple

_NOT_LOADED = object()
_override_cache: Any = _NOT_LOADED


def app_root() -> Path:
    """
    Return the runtime app root.

    - Source mode: repository root.
    - Frozen mode: directory containing the executable.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _paths_config_file() -> Path:
    return app_root() / "paths.json"


def _load_paths_override() -> Optional[Tuple[Path, Path]]:
    path = _paths_config_file()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    inp = raw.get("input_dir")
    out = raw.get("output_dir")
    if not isinstance(inp, str) or not isinstance(out, str):
        return None
    inp = inp.strip()
    out = out.strip()
    if not inp or not out:
        return None
    in_path = Path(inp).expanduser()
    out_path = Path(out).expanduser()
    if not in_path.is_absolute() or not out_path.is_absolute():
        return None
    return (in_path.resolve(), out_path.resolve())


def _effective_io() -> Tuple[Path, Path]:
    global _override_cache
    if _override_cache is _NOT_LOADED:
        _override_cache = _load_paths_override()
    if _override_cache is not None:
        return _override_cache  # type: ignore[return-value]
    root = app_root()
    return (root / "input", root / "output")


def input_dir() -> Path:
    return _effective_io()[0]


def output_dir() -> Path:
    return _effective_io()[1]


def readme_dir() -> Path:
    return app_root() / "controllers" / "Readme"


def ensure_runtime_dirs() -> None:
    input_dir().mkdir(parents=True, exist_ok=True)
    output_dir().mkdir(parents=True, exist_ok=True)
