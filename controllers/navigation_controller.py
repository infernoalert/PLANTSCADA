# navigation_controller — open auxiliary windows (Readme, etc.).

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext

from controllers.readme import load_asset
from ui import AppView


def open_content(view: AppView, asset_filename: str) -> None:
    """One-line hook from other controllers: show a page loaded from controllers/Readme/<file>."""
    body = load_asset(asset_filename)
    _open_readme_window(view.root, body, title="Readme")


def handle_readme(view: AppView) -> None:
    view.set_status("Readme…")
    open_content(view, "clean.txt")


def _open_readme_window(parent: tk.Misc, body: str, title: str = "Readme") -> None:
    win = tk.Toplevel(parent)
    win.title(title)
    win.minsize(400, 240)

    text = scrolledtext.ScrolledText(win, wrap="word", width=72, height=18)
    text.pack(fill="both", expand=True, padx=8, pady=8)
    text.insert("1.0", body)
    text.configure(state="disabled")
