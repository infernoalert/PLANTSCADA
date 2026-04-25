# SCADA CSV Processor App

A lightweight, local desktop utility designed to parse, filter, and process very large CSV exports from SCADA systems without overwhelming system memory.

## Architecture: Lightweight MVC
This application intentionally avoids heavy frameworks to remain fast, maintainable, and easy for other Python developers to understand. It is built using a strict **Model-View-Controller (MVC)** design pattern with these layers:

1. **processor.py (The Model)**
   - The data processing engine powered by Pandas.
   - Strictly handles reading, filtering, mathematical operations, and writing CSVs.
   - Completely isolated from any UI logic.

2. **ui.py (The View)**
   - The graphical user interface built with Tkinter / CustomTkinter.
   - Handles window drawing, buttons, file selection dialogs, and gathering user parameters.
   - Completely isolated from data manipulation logic.

3. **main.py (Router)** — Wires `ui.py` to **controllers/** (one module per toolbar action).

4. **services/** — Shared helpers (for example writing UTF-8 CSVs under `output/`).

**Equip Create:** Row 4: reads **`input/<stem>.csv`** (headerless grid; input is never written), converts TabViewr-style cells to EQPARAM-shaped rows, writes **`output/outputEquipImport<stem>.csv`** only (header from `input/Eqparam.csv`). Stops if any cell contains `**FAULT**`.

## Folder Structure
- /input/ - Place raw SCADA .csv files here. (Ignored by Git)
- /output/ - Processed .csv files are generated here. (Ignored by Git)
- main.py, ui.py, processor.py - Core application logic.
- controllers/, services/ - Per-action handlers and CSV output helpers.
- requirements.txt - Python package dependencies.

## Setup Instructions
1. Create a virtual environment: python -m venv venv
2. Activate it: .\venv\Scripts\activate
3. Install dependencies: pip install -r requirements.txt
4. Run the app: python main.py

## Windows Build and Single Setup.exe

The release flow uses **PyInstaller only** (no Inno Setup). One command builds the portable app folder and **`dist/PLANTSCADA-Setup.exe`**, which asks for install location, input folder, and output folder, then unpacks the app and writes `paths.json` next to `PLANTSCADA.exe`.

### Prerequisites
- Python 3.12+
- PowerShell

### PowerShell Commands (copy/paste)
Run from the project root:

```powershell
# 1) Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2) Install dependencies (includes pyinstaller)
python -m pip install -r requirements.txt

# 3) Build portable app + single-file installer
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

### Outputs
- Portable app folder: `dist/PLANTSCADA/`
- App executable: `dist/PLANTSCADA/PLANTSCADA.exe`
- **Single installer:** `dist/PLANTSCADA-Setup.exe` (copy this to other PCs)

### Installed layout
- After running `PLANTSCADA-Setup.exe`, the chosen **input** and **output** folders are stored in `paths.json` beside `PLANTSCADA.exe`. The app creates those folders if they are missing.
- If `paths.json` is absent, the app uses `input/` and `output/` next to the executable (same as portable run from `dist/PLANTSCADA`).

### Notes
- `controllers/Readme/*.txt` are bundled in the portable build.
- `PLANTSCADA-Setup.exe` is large because it embeds the zipped portable folder.
- Unsigned installers may trigger Windows SmartScreen; users can choose **More info** then **Run anyway** if needed.
