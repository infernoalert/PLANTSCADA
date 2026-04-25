# PLANTSCADA-Setup: unpack portable build, choose input/output folders, write paths.json.

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import tkinter as tk


PAYLOAD_ZIP_NAME = "PLANTSCADA-payload.zip"
MAIN_EXE_NAME = "PLANTSCADA.exe"


def _payload_zip_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / PAYLOAD_ZIP_NAME
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "dist" / PAYLOAD_ZIP_NAME


def _create_desktop_shortcut(target_exe: Path) -> None:
    if not target_exe.is_file():
        return
    import subprocess

    target_ps = json.dumps(str(target_exe.resolve()))
    ps = (
        "$s = New-Object -ComObject WScript.Shell; "
        "$desk = Join-Path $env:USERPROFILE 'Desktop'; "
        "if (-not (Test-Path -LiteralPath $desk)) { exit 0 }; "
        f"$l = $s.CreateShortcut((Join-Path $desk 'PLANTSCADA.lnk')); "
        f"$l.TargetPath = {target_ps}; "
        "$l.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        check=False,
        capture_output=True,
        text=True,
    )


class SetupWizard(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PLANTSCADA Setup")
        self.minsize(520, 200)

        self._install = tk.StringVar()
        self._input = tk.StringVar()
        self._output = tk.StringVar()
        self._shortcut = tk.BooleanVar(value=True)

        pad = {"padx": 8, "pady": 4}
        row = 0

        ttk.Label(self, text="Install application to:").grid(row=row, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self._install, width=50).grid(row=row, column=1, sticky="ew", **pad)
        ttk.Button(self, text="Browse…", command=self._browse_install).grid(row=row, column=2, **pad)
        row += 1

        ttk.Label(self, text="Input folder (CSV files):").grid(row=row, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self._input, width=50).grid(row=row, column=1, sticky="ew", **pad)
        ttk.Button(self, text="Browse…", command=self._browse_input).grid(row=row, column=2, **pad)
        row += 1

        ttk.Label(self, text="Output folder (results):").grid(row=row, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self._output, width=50).grid(row=row, column=1, sticky="ew", **pad)
        ttk.Button(self, text="Browse…", command=self._browse_output).grid(row=row, column=2, **pad)
        row += 1

        ttk.Checkbutton(self, text="Create desktop shortcut", variable=self._shortcut).grid(
            row=row, column=1, sticky="w", **pad
        )
        row += 1

        ttk.Button(self, text="Install", command=self._install_clicked).grid(row=row, column=1, sticky="w", **pad)

        self.columnconfigure(1, weight=1)

    def _browse_install(self) -> None:
        d = filedialog.askdirectory(title="Choose install folder")
        if d:
            self._install.set(d)

    def _browse_input(self) -> None:
        d = filedialog.askdirectory(title="Choose input folder")
        if d:
            self._input.set(d)

    def _browse_output(self) -> None:
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self._output.set(d)

    def _install_clicked(self) -> None:
        install = self._install.get().strip()
        inp = self._input.get().strip()
        out = self._output.get().strip()
        if not install or not inp or not out:
            messagebox.showwarning("Setup", "Please choose install, input, and output folders.")
            return

        install_path = Path(install).expanduser().resolve()
        input_path = Path(inp).expanduser().resolve()
        output_path = Path(out).expanduser().resolve()

        payload = _payload_zip_path()
        if not payload.is_file():
            messagebox.showerror(
                "Setup",
                f"Missing payload zip:\n{payload}\n\nRebuild with scripts/build.ps1",
            )
            return

        try:
            install_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Setup", f"Cannot create install folder:\n{exc}")
            return

        main_exe = install_path / MAIN_EXE_NAME
        if main_exe.exists():
            if not messagebox.askyesno(
                "Setup",
                f"{MAIN_EXE_NAME} already exists in this folder.\nOverwrite installed files?",
            ):
                return

        try:
            input_path.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Setup", f"Cannot create input/output folders:\n{exc}")
            return

        tmp_parent = Path(tempfile.mkdtemp(prefix="plantscada_setup_"))
        try:
            with zipfile.ZipFile(payload, "r") as zf:
                zf.extractall(tmp_parent)
            for item in tmp_parent.iterdir():
                dest = install_path / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        except (OSError, zipfile.BadZipFile) as exc:
            messagebox.showerror("Setup", f"Install failed:\n{exc}")
            return
        finally:
            shutil.rmtree(tmp_parent, ignore_errors=True)

        if not main_exe.is_file():
            messagebox.showerror("Setup", f"Install incomplete: {MAIN_EXE_NAME} not found after extract.")
            return

        cfg = {
            "input_dir": str(input_path),
            "output_dir": str(output_path),
        }
        try:
            (install_path / "paths.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Setup", f"Could not write paths.json:\n{exc}")
            return

        if self._shortcut.get():
            _create_desktop_shortcut(main_exe)

        messagebox.showinfo(
            "Setup",
            f"Installation finished.\n\nApplication:\n{main_exe}\n\nInput:\n{input_path}\n\nOutput:\n{output_path}",
        )
        self.destroy()


def main() -> None:
    app = SetupWizard()
    app.mainloop()


if __name__ == "__main__":
    main()
