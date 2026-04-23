from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """
    Return the runtime app root.

    - Source mode: repository root.
    - Frozen mode: directory containing the executable.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def input_dir() -> Path:
    return app_root() / "input"


def output_dir() -> Path:
    return app_root() / "output"


def readme_dir() -> Path:
    return app_root() / "controllers" / "Readme"


def ensure_runtime_dirs() -> None:
    input_dir().mkdir(parents=True, exist_ok=True)
    output_dir().mkdir(parents=True, exist_ok=True)
