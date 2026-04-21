# ==========================================
# ui.py - THE VIEW (User Interface)
# ==========================================
# Tkinter window, grid layout, and user inputs.
# Collects parameters for the Controller; no data processing or Pandas.

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Callable, Optional


class AppView:
    """Single toolbar row (entry + actions); status below for scalability."""

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("SCADA CSV Processor")
        self._root.minsize(360, 88)

        self._root.columnconfigure(0, weight=1)

        self._search_var = tk.StringVar()
        self._entry = ttk.Entry(self._root, textvariable=self._search_var)
        self._entry.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=8)

        self._clean_btn = ttk.Button(self._root, text="Clean", command=self._handle_clean)
        self._clean_btn.grid(row=0, column=1, sticky="w", padx=4, pady=8)

        self._readme_link_fg = "#0563c1"
        self._readme_link_fg_hover = "#034783"
        self._readme_font = tkfont.Font(self._root, size=9, underline=True)
        self._readme_label = tk.Label(
            self._root,
            text="Readme",
            fg=self._readme_link_fg,
            cursor="hand2",
            font=self._readme_font,
            bd=0,
            padx=0,
            pady=0,
        )
        self._readme_label.grid(row=0, column=2, sticky="w", padx=(4, 8), pady=8)
        self._readme_label.bind("<Button-1>", self._handle_readme_click)
        self._readme_label.bind("<Enter>", self._on_readme_enter)
        self._readme_label.bind("<Leave>", self._on_readme_leave)

        self._status_var = tk.StringVar(value="Ready")
        self._status = ttk.Label(self._root, textvariable=self._status_var)
        self._status.grid(row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=(0, 8))

        self._on_clean: Optional[Callable[[], None]] = None
        self._on_readme_click: Optional[Callable[[], None]] = None

    @property
    def root(self) -> tk.Tk:
        return self._root

    def _handle_clean(self) -> None:
        if self._on_clean is not None:
            self._on_clean()

    def _handle_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_readme_click is not None:
            self._on_readme_click()

    def _on_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._readme_label.configure(fg=self._readme_link_fg)

    def get_search_string(self) -> str:
        return self._search_var.get().strip()

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

    def set_on_clean(self, callback: Callable[[], None]) -> None:
        self._on_clean = callback

    def set_on_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_readme_click = callback

    def run(self) -> None:
        self._root.mainloop()
