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
    """Rows 1–4: Clean, TabViewr, updateLocation, SearchVariable; row 5: Equip Create; status below."""

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("SCADA CSV Processor")
        self._root.minsize(520, 190)

        # Col 0: narrow row numbers; col 1: primary entry (grows).
        self._root.columnconfigure(0, weight=0, minsize=22)
        self._root.columnconfigure(1, weight=1)

        self._line_font = tkfont.Font(self._root, size=8)
        self._line_muted = "#6b6b6b"

        ttk.Label(self._root, text="1", font=self._line_font, foreground=self._line_muted).grid(
            row=0, column=0, sticky="ne", padx=(6, 2), pady=8
        )
        ttk.Label(self._root, text="2", font=self._line_font, foreground=self._line_muted).grid(
            row=1, column=0, sticky="ne", padx=(6, 2), pady=(0, 4)
        )
        ttk.Label(self._root, text="3", font=self._line_font, foreground=self._line_muted).grid(
            row=2, column=0, sticky="ne", padx=(6, 2), pady=(0, 4)
        )
        ttk.Label(self._root, text="4", font=self._line_font, foreground=self._line_muted).grid(
            row=3, column=0, sticky="ne", padx=(6, 2), pady=(0, 4)
        )
        ttk.Label(self._root, text="5", font=self._line_font, foreground=self._line_muted).grid(
            row=4, column=0, sticky="ne", padx=(6, 2), pady=(0, 4)
        )

        self._search_var = tk.StringVar()
        self._entry = ttk.Entry(self._root, textvariable=self._search_var)
        self._entry.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=8)

        self._clean_btn = ttk.Button(self._root, text="Clean", command=self._handle_clean)
        self._clean_btn.grid(row=0, column=2, sticky="w", padx=4, pady=8)

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
        self._readme_label.grid(row=0, column=3, sticky="w", padx=(4, 8), pady=8)
        self._readme_label.bind("<Button-1>", self._handle_readme_click)
        self._readme_label.bind("<Enter>", self._on_readme_enter)
        self._readme_label.bind("<Leave>", self._on_readme_leave)

        self._tabviewr_search_var = tk.StringVar()
        self._tabviewr_entry = ttk.Entry(self._root, textvariable=self._tabviewr_search_var)
        self._tabviewr_entry.grid(row=1, column=1, sticky="ew", padx=(0, 4), pady=(0, 4))

        self._tabviewr_btn = ttk.Button(self._root, text="TabViewr", command=self._handle_tabviewr)
        self._tabviewr_btn.grid(row=1, column=2, sticky="w", padx=4, pady=(0, 4))

        self._tabviewr_readme_label = tk.Label(
            self._root,
            text="Readme",
            fg=self._readme_link_fg,
            cursor="hand2",
            font=self._readme_font,
            bd=0,
            padx=0,
            pady=0,
        )
        self._tabviewr_readme_label.grid(row=1, column=3, sticky="w", padx=(4, 8), pady=(0, 4))
        self._tabviewr_readme_label.bind("<Button-1>", self._handle_tabviewr_readme_click)
        self._tabviewr_readme_label.bind("<Enter>", self._on_tabviewr_readme_enter)
        self._tabviewr_readme_label.bind("<Leave>", self._on_tabviewr_readme_leave)

        self._update_location_search_var = tk.StringVar()
        self._update_location_entry = ttk.Entry(self._root, textvariable=self._update_location_search_var)
        self._update_location_entry.grid(row=2, column=1, sticky="ew", padx=(0, 4), pady=(0, 4))

        self._update_location_btn = ttk.Button(
            self._root, text="updateLocation", command=self._handle_update_location
        )
        self._update_location_btn.grid(row=2, column=2, sticky="w", padx=4, pady=(0, 4))

        self._update_location_readme_label = tk.Label(
            self._root,
            text="Readme",
            fg=self._readme_link_fg,
            cursor="hand2",
            font=self._readme_font,
            bd=0,
            padx=0,
            pady=0,
        )
        self._update_location_readme_label.grid(row=2, column=3, sticky="w", padx=(4, 8), pady=(0, 4))
        self._update_location_readme_label.bind("<Button-1>", self._handle_update_location_readme_click)
        self._update_location_readme_label.bind("<Enter>", self._on_update_location_readme_enter)
        self._update_location_readme_label.bind("<Leave>", self._on_update_location_readme_leave)

        self._equip_create_search_var = tk.StringVar()
        self._equip_create_entry = ttk.Entry(self._root, textvariable=self._equip_create_search_var)
        self._equip_create_entry.grid(row=4, column=1, sticky="ew", padx=(0, 4), pady=(0, 4))

        self._equip_create_btn = ttk.Button(
            self._root, text="Equip Create", command=self._handle_equip_create
        )
        self._equip_create_btn.grid(row=4, column=2, sticky="w", padx=4, pady=(0, 4))

        self._equip_create_readme_label = tk.Label(
            self._root,
            text="Readme",
            fg=self._readme_link_fg,
            cursor="hand2",
            font=self._readme_font,
            bd=0,
            padx=0,
            pady=0,
        )
        self._equip_create_readme_label.grid(row=4, column=3, sticky="w", padx=(4, 8), pady=(0, 4))
        self._equip_create_readme_label.bind("<Button-1>", self._handle_equip_create_readme_click)
        self._equip_create_readme_label.bind("<Enter>", self._on_equip_create_readme_enter)
        self._equip_create_readme_label.bind("<Leave>", self._on_equip_create_readme_leave)

        self._search_variable_group_var = tk.StringVar()
        self._search_variable_entry = ttk.Entry(
            self._root, textvariable=self._search_variable_group_var
        )
        self._search_variable_entry.grid(row=3, column=1, sticky="ew", padx=(0, 4), pady=(0, 4))

        self._search_variable_btn = ttk.Button(
            self._root, text="SearchVariable", command=self._handle_search_variable
        )
        self._search_variable_btn.grid(row=3, column=2, sticky="w", padx=4, pady=(0, 4))

        self._search_variable_readme_label = tk.Label(
            self._root,
            text="Readme",
            fg=self._readme_link_fg,
            cursor="hand2",
            font=self._readme_font,
            bd=0,
            padx=0,
            pady=0,
        )
        self._search_variable_readme_label.grid(row=3, column=3, sticky="w", padx=(4, 8), pady=(0, 4))
        self._search_variable_readme_label.bind("<Button-1>", self._handle_search_variable_readme_click)
        self._search_variable_readme_label.bind("<Enter>", self._on_search_variable_readme_enter)
        self._search_variable_readme_label.bind("<Leave>", self._on_search_variable_readme_leave)

        self._status_var = tk.StringVar(value="Ready")
        self._status = ttk.Label(self._root, textvariable=self._status_var)
        self._status.grid(row=5, column=1, columnspan=3, sticky="ew", padx=(0, 8), pady=(0, 8))

        self._on_clean: Optional[Callable[[], None]] = None
        self._on_readme_click: Optional[Callable[[], None]] = None
        self._on_tabviewr: Optional[Callable[[], None]] = None
        self._on_tabviewr_readme_click: Optional[Callable[[], None]] = None
        self._on_update_location: Optional[Callable[[], None]] = None
        self._on_update_location_readme_click: Optional[Callable[[], None]] = None
        self._on_equip_create: Optional[Callable[[], None]] = None
        self._on_equip_create_readme_click: Optional[Callable[[], None]] = None
        self._on_search_variable: Optional[Callable[[], None]] = None
        self._on_search_variable_readme_click: Optional[Callable[[], None]] = None

    @property
    def root(self) -> tk.Tk:
        return self._root

    def _handle_clean(self) -> None:
        if self._on_clean is not None:
            self._on_clean()

    def _handle_tabviewr(self) -> None:
        if self._on_tabviewr is not None:
            self._on_tabviewr()

    def _handle_update_location(self) -> None:
        if self._on_update_location is not None:
            self._on_update_location()

    def _handle_equip_create(self) -> None:
        if self._on_equip_create is not None:
            self._on_equip_create()

    def _handle_search_variable(self) -> None:
        if self._on_search_variable is not None:
            self._on_search_variable()

    def _handle_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_readme_click is not None:
            self._on_readme_click()

    def _handle_tabviewr_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_tabviewr_readme_click is not None:
            self._on_tabviewr_readme_click()

    def _handle_update_location_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_update_location_readme_click is not None:
            self._on_update_location_readme_click()

    def _handle_equip_create_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_equip_create_readme_click is not None:
            self._on_equip_create_readme_click()

    def _handle_search_variable_readme_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self._on_search_variable_readme_click is not None:
            self._on_search_variable_readme_click()

    def _on_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._readme_label.configure(fg=self._readme_link_fg)

    def _on_tabviewr_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._tabviewr_readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_tabviewr_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._tabviewr_readme_label.configure(fg=self._readme_link_fg)

    def _on_update_location_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._update_location_readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_update_location_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._update_location_readme_label.configure(fg=self._readme_link_fg)

    def _on_equip_create_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._equip_create_readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_equip_create_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._equip_create_readme_label.configure(fg=self._readme_link_fg)

    def _on_search_variable_readme_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._search_variable_readme_label.configure(fg=self._readme_link_fg_hover)

    def _on_search_variable_readme_leave(self, _event: tk.Event[tk.Misc]) -> None:
        self._search_variable_readme_label.configure(fg=self._readme_link_fg)

    def get_search_string(self) -> str:
        return self._search_var.get().strip()

    def get_tabviewr_search_string(self) -> str:
        return self._tabviewr_search_var.get().strip()

    def get_update_location_search_string(self) -> str:
        return self._update_location_search_var.get().strip()

    def get_equip_create_search_string(self) -> str:
        return self._equip_create_search_var.get().strip()

    def get_search_variable_group_string(self) -> str:
        return self._search_variable_group_var.get().strip()

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

    def set_on_clean(self, callback: Callable[[], None]) -> None:
        self._on_clean = callback

    def set_on_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_readme_click = callback

    def set_on_tabviewr(self, callback: Callable[[], None]) -> None:
        self._on_tabviewr = callback

    def set_on_tabviewr_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_tabviewr_readme_click = callback

    def set_on_update_location(self, callback: Callable[[], None]) -> None:
        self._on_update_location = callback

    def set_on_update_location_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_update_location_readme_click = callback

    def set_on_equip_create(self, callback: Callable[[], None]) -> None:
        self._on_equip_create = callback

    def set_on_equip_create_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_equip_create_readme_click = callback

    def set_on_search_variable(self, callback: Callable[[], None]) -> None:
        self._on_search_variable = callback

    def set_on_search_variable_readme_click(self, callback: Callable[[], None]) -> None:
        self._on_search_variable_readme_click = callback

    def run(self) -> None:
        self._root.mainloop()
