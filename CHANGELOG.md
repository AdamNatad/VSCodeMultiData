# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-03-01

### Added

- **VSCode MultiData** — Windows launcher for multiple VS Code instances with separate user data and extensions.
- Profile management: add, edit, delete profiles; each profile has its own user-data and extensions folders.
- Launch any profile with one click or double-click; optional open-new-window and extra CLI args.
- Theme: Dark / Light (case-sensitive); UI scale: Auto, 100%–300%.
- Config and crash log beside the EXE (no AppData); explicit Save Config (no auto-save).
- Styled confirmation dialogs (remove profile, save config, UI scale info, configuration saved) with Dark/Light theme and modal focus.
- Minimum window size (1024×620) so the right action menu is always visible; enforced on resize.
- App icon support: 512×512 PNG in `assets/` → `app.ico` for EXE and installer.
- **Build:** Single entry point `python build.py` from project root.
  - Output: `output/VSCodeMultiData-Portable.zip` and `output/VSCodeMultiData-Setup.exe`.
- **Installer:** Inno Setup 6 script in `build/installer.iss`; install path `C:\Program Files\VSMultiData\`; grants Users write permission so app can write config/crash in install folder.
- **Project layout:** App in `src/launcher.py`; build script `build.py` and build tools in `build/` (build_icon.py, installer.iss).

### Fixed

- ConfigParser crash with `ui_scale=200%` (interpolation disabled).
- Combobox text turning white on Light theme when dropdown focused/pressed (state mappings for TCombobox).

---

[1.0.0]: https://github.com/AdamNatad/VSCodeMultiData/releases/tag/v1.0.0
