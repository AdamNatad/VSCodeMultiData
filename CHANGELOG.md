# Changelog

Notable changes. Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-03-01

First release.

### Added

- Windows launcher for multiple VS Code instances; each profile has its own user-data and extensions folders.
- Profile management: add, edit, delete; launch via button or double-click; optional new-window and extra CLI args.
- Dark / Light theme and UI scale (Auto, 100%–300%); scale applies after save + relaunch.
- Config and crash log next to the EXE (no AppData); save is explicit (no auto-save).
- Themed modals for remove profile, save config, UI scale, and report bugs; Copy Url in report-bugs dialog; footer “Report Bugs?” (red on hover).
- Min window size 1024×620; right rail always visible.
- App icon (PNG → app.ico); all windows use it.
- Build: `python build.py` → portable ZIP and Inno Setup installer. Install path: `C:\Program Files\VSCodeMD\`; Users get write so config/crash work. Support URL: natadtech.com; Help: natadtech.com/adam-natad.
- Global excepthook: uncaught errors go to crash.log and open report-bugs modal when possible.

### Fixed

- ConfigParser crash when `ui_scale` contained `%` (interpolation disabled).
- Combobox text turning white on Light theme when focused (state mappings for TCombobox).

---

[1.0.0]: https://github.com/AdamNatad/VSCodeMultiData/releases/tag/v1.0.0
