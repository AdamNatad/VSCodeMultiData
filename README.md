# VSCode MultiData by [Adam Natad](https://natadtech.com/adam-natad)

![VSCode MultiData Banner](assets/VSCodeMultiDataBanner.png)

---

## What it does

Easily launch VS Code with **separate user-data and extension data** per profile. Use different profiles to sign in to different accounts in extensions (e.g. multiple GitHub accounts, different marketplace logins) without switching Windows users. Manage profiles and launch per profile with one click.

---

## Requirements

- **Windows** 10 or 11
- **VS Code** (standard or Insiders)
- **Python 3.x** only if you run or build from source

---

## Installation

### Option A — Installer (recommended)

1. Download **VSCodeMultiData-Setup.exe** from [Releases](https://github.com/AdamNatad/VSCodeMultiData/releases).
2. Run the installer (admin required).
3. Install path: `C:\Program Files\VSMultiData\`.
4. Launch from the Start Menu (or Desktop) shortcut.

Config and crash log are created in the install folder on first run.

### Option B — Portable (ZIP)

1. Download **VSCodeMultiData-Portable.zip** from [Releases](https://github.com/AdamNatad/VSCodeMultiData/releases).
2. Extract anywhere (e.g. `D:\Tools\VSCodeMultiData`).
3. Run **VSCodeMD.exe**.

Config and crash log are created in the same folder as the EXE.

### Option C — Run from source

```bash
git clone https://github.com/AdamNatad/VSCodeMultiData.git
cd VSCodeMultiData
python src/launcher.py
```

---

## Usage

1. **Paths** — Use **Browse** / **Detect** for the VS Code executable and a base directory for profile data.
2. **Profiles** — Add profiles (name + user-data and extensions folders). Use **Auto-Fill from Base** for a quick layout.
3. **Launch** — Select a profile and click **Launch**, or double-click a row.
4. **Save** — Click **Save Config** to write `config.ini` (changes are not auto-saved).

Theme and UI scale apply after you save config and restart the app.

---

## Building from source

Build produces **two outputs** in `output/`: **portable ZIP** and **installer**.

### Prerequisites

- **Python 3.x** and `pip install pyinstaller`
- **Inno Setup 6** — [Download](https://jrsoftware.org/isinfo.php) (e.g. `C:\Program Files (x86)\Inno Setup 6`)
- **Logo** — 512×512 px PNG in `assets/app_icon.png` (optional; run `python build/build_icon.py` to generate `app.ico`)

### One-command build

From the **project root**:

```bash
python build.py
```

**Output:**

| Artifact      | Path |
|---------------|------|
| Portable ZIP  | `output/VSCodeMultiData-Portable.zip` |
| Installer     | `output/VSCodeMultiData-Setup.exe`   |

See **[BUILD.md](BUILD.md)** for step-by-step and folder layout.

---

## Project structure

```
VSCodeMultiData/
├── build.py
├── README.md
├── BUILD.md
├── CHANGELOG.md
├── src/
│   └── launcher.py
├── assets/
│   ├── app_icon.png
│   └── VSCodeMultiDataBanner.png
├── build/
│   ├── build_icon.py
│   └── installer.iss
├── dist/                    (generated)
│   └── VSCodeMD.exe
└── output/                  (generated)
    ├── VSCodeMultiData-Portable.zip
    └── VSCodeMultiData-Setup.exe
```

| Path | Purpose |
|------|---------|
| `build.py` | Full build → ZIP + installer |
| `src/launcher.py` | Main app |
| `assets/app_icon.png` | 512×512 logo for `app.ico` |
| `assets/VSCodeMultiDataBanner.png` | README banner, social preview |
| `build/build_icon.py` | PNG → app.ico |
| `build/installer.iss` | Inno Setup script |
| `dist/`, `output/` | Build output (generated) |

---

## Changelog

[CHANGELOG.md](CHANGELOG.md) — all notable changes per release.

---

## Support / Help

- **Support:** [natadtech.com](https://natadtech.com)
- **Help / About:** [natadtech.com/adam-natad](https://natadtech.com/adam-natad)
- **Bugs / issues:** [GitHub Issues](https://github.com/AdamNatad/VSCodeMultiData/issues)

---

## License

[LICENSE](LICENSE) in this repo.

---

**VSCode MultiData** by [Adam Natad](https://natadtech.com/adam-natad) — VS Code multiple user-data launcher.
