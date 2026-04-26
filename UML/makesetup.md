# Make Setup Workflow

This document explains how the PLANTSCADA setup build works, both for developers (technical flow) and for users (install/run commands).

## What `make setup` Means in This Project

There is no Linux-style `make` file. In this project, "make setup" means running the PowerShell build script:

`scripts/build.ps1`

That script builds:

- A portable app folder at `dist/PLANTSCADA/`
- A single installer at `dist/PLANTSCADA-Setup.exe`

## Technical Flow (Developer View)

When you run the build script, this happens:

1. Python dependencies are resolved from `requirements.txt` (including PyInstaller).
2. PyInstaller uses `PLANTSCADA.spec` to freeze the app into a portable executable layout.
3. The installer packaging step uses `PLANTSCADA-Setup.spec` to produce one self-contained setup executable.
4. The generated setup exe includes the app payload and install logic.
5. During installation on a target machine, the installer asks for install/input/output paths and writes `paths.json` next to `PLANTSCADA.exe`.

`paths.json` stores user-selected folders so runtime processing uses those locations instead of defaults.

## Developer Commands (Build Setup EXE)

Run these commands from the project root in PowerShell:

```powershell
# 1) Create virtual environment
python -m venv venv

# 2) Activate environment
.\venv\Scripts\activate

# 3) Install dependencies
python -m pip install -r requirements.txt

# 4) Build portable app + setup installer
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

After success, distribute:

`dist/PLANTSCADA-Setup.exe`

## User Commands (Run Installed App)

### Option A: Install via setup file (recommended)

1. Double-click `PLANTSCADA-Setup.exe`.
2. Select:
   - Install location
   - Input folder
   - Output folder
3. Finish installation and launch `PLANTSCADA.exe`.

### Option B: Run portable build directly

If you are testing without installer:

```powershell
.\dist\PLANTSCADA\PLANTSCADA.exe
```

If `paths.json` does not exist, the app uses local `input/` and `output/` folders beside the exe.

## Quick Verification

After build, confirm these files exist:

- `dist/PLANTSCADA/PLANTSCADA.exe`
- `dist/PLANTSCADA-Setup.exe`

After install, confirm:

- `PLANTSCADA.exe` launches
- `paths.json` exists next to the exe
- CSV outputs are generated in the selected output folder
