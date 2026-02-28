# Build — VSCode MultiData (v1.0.0)

Build produces **two artifacts** in `output/`: **portable ZIP** and **installer** (Setup.exe).

---

## One-command build

From the **project root**:

```bash
python build.py
```

Steps run in order:

1. **Icon** — `build/build_icon.py` → `app.ico` (from `assets/app_icon.png`)
2. **EXE** — PyInstaller on `src/launcher.py` → `dist/VSCode MultiData by Adam Natad.exe`
3. **Portable ZIP** → `output/VSCodeMultiData-Portable.zip`
4. **Installer** — Inno Setup 6 (`build/installer.iss`) → `output/VSCodeMultiData-Setup.exe`

---

## Prerequisites

- **Python 3.x** and `pip install pyinstaller`
- **Inno Setup 6** — [Download](https://jrsoftware.org/isinfo.php), e.g. `C:\Program Files (x86)\Inno Setup 6`
- **Logo** — 512×512 px PNG at `assets/app_icon.png` (optional; script will warn if missing)

---

## Step-by-step (manual)

**1. Icon**

```bash
python build/build_icon.py
```

Custom logo:

```bash
python build/build_icon.py path/to/logo.png
```

**2. EXE**

```bash
pyinstaller --onefile --noconsole --icon=app.ico --add-data "app.ico;." --name "VSCode MultiData by Adam Natad" src/launcher.py
```

**3. Portable ZIP**

Create `output/` and zip the EXE (e.g. with PowerShell `Compress-Archive` or 7-Zip).  
`build.py` does this automatically using the standard library.

**4. Installer**

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build/installer.iss
```

Or open `build/installer.iss` in Inno Setup 6 and use **Build → Compile**.

---

## Installer behaviour

- **Install path:** `C:\Program Files\VSMultiData\`
- **Permissions:** Write access for Users on the install folder (so config/crash can be written beside the EXE).
- **Shortcuts:** Start Menu + optional Desktop.
- **Uninstall:** Add or remove programs.

---

## Folder layout

- **Root:** `build.py` (single entry point), `src/launcher.py` (app), `assets/`, docs.
- **build/** — Build tools only: `build_icon.py`, `installer.iss`.
- **output/** — Generated: `VSCodeMultiData-Portable.zip`, `VSCodeMultiData-Setup.exe`.
