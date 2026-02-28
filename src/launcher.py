# VSCode MultiData by Adam Natad (Compact + Responsive + Stable)
# ------------------------------------------------------------------------------
# Fixes:
# - ConfigParser % crash (ui_scale=200%) by disabling interpolation
# - Compact responsive UI (tree expands, right panel stays narrow)
# - Removed all icons (cleaner look)
#
# Build: from project root run  python build.py  (output: output/VSCodeMultiData-Portable.zip, output/VSCodeMultiData-Setup.exe)
# App lives in src/; build script and installer script in build/.

from __future__ import annotations

import os
import sys
import shutil
import platform
import subprocess
import ctypes
import configparser
import traceback
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

APP_NAME = "VSCode MultiData by Adam Natad"
CONFIG_FILENAME = "config.ini"


# -----------------------------
# Helpers
# -----------------------------

def os_name() -> str:
    return platform.system()

def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def config_path() -> str:
    return os.path.join(app_dir(), CONFIG_FILENAME)

def crash_log_path() -> str:
    return os.path.join(app_dir(), "crash.log")

def norm(p: str) -> str:
    return os.path.normpath(os.path.expandvars(os.path.expanduser((p or "").strip())))

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def open_folder_cross_platform(path: str) -> None:
    path = norm(path)
    ensure_dir(path)
    if os_name() == "Windows":
        os.startfile(path)  # type: ignore[attr-defined]
    elif os_name() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def split_args(extra: str) -> list[str]:
    extra = (extra or "").strip()
    if not extra:
        return []
    try:
        import shlex
        return shlex.split(extra, posix=(os_name() != "Windows"))
    except Exception:
        return extra.split()


# -----------------------------
# VS Code detection
# -----------------------------

def vscode_candidates() -> list[str]:
    cands: list[str] = []

    if os_name() == "Windows":
        # Prefer Code.exe first
        cands += [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ]
        local = os.environ.get("LOCALAPPDATA")
        if local:
            cands += [
                os.path.join(local, r"Programs\Microsoft VS Code\Code.exe"),
                os.path.join(local, r"Programs\Microsoft VS Code Insiders\Code - Insiders.exe"),
            ]

        # CLI fallbacks last
        which_code = shutil.which("code.cmd") or shutil.which("code.exe") or shutil.which("code")
        if which_code:
            cands.append(which_code)

    elif os_name() == "Darwin":
        cands += [
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code",
            os.path.expanduser("~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
        ]
        which_code = shutil.which("code")
        if which_code:
            cands.insert(0, which_code)

    else:
        cands += ["/usr/bin/code", "/usr/local/bin/code", "/snap/bin/code"]
        which_code = shutil.which("code")
        if which_code:
            cands.insert(0, which_code)

    out, seen = [], set()
    for p in cands:
        if not p:
            continue
        p = norm(p)
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def autodetect_vscode_path() -> str:
    for p in vscode_candidates():
        if os.path.isfile(p) or shutil.which(p):
            return p
    return ""

def is_executable_path(p: str) -> bool:
    p = norm(p)
    return bool(p) and (os.path.isfile(p) or shutil.which(p))


# -----------------------------
# Config + Model
# -----------------------------

class Profile:
    def __init__(self, name: str, user_data: str, extensions: str):
        self.name = name
        self.user_data = user_data
        self.extensions = extensions

    def ensure_folders(self) -> None:
        ensure_dir(self.user_data)
        ensure_dir(self.extensions)

class ConfigManager:
    def __init__(self, path: str):
        self.path = path
        # IMPORTANT: disable interpolation so "200%" doesn't crash
        self.cfg = configparser.ConfigParser(interpolation=None)

    def _default_base_dir(self) -> str:
        if os_name() == "Windows":
            return r"D:\VSCode-UData"
        return os.path.expanduser("~/VSCode-UData")

    def load(self) -> None:
        if os.path.isfile(self.path):
            self.cfg.read(self.path, encoding="utf-8")
        else:
            self._create_default()

        if "app" not in self.cfg: self.cfg["app"] = {}
        if "profiles" not in self.cfg: self.cfg["profiles"] = {}

        self.cfg["app"].setdefault("vscode_path", autodetect_vscode_path())
        self.cfg["app"].setdefault("base_dir", self._default_base_dir())
        self.cfg["app"].setdefault("open_new_window", "1")
        self.cfg["app"].setdefault("reuse_existing_window", "0")
        self.cfg["app"].setdefault("extra_args", "")
        self.cfg["app"].setdefault("theme", "Dark")
        self.cfg["app"].setdefault("ui_scale", "Auto")

        if len(self.cfg["profiles"]) == 0:
            base_dir = norm(self.cfg["app"]["base_dir"])
            for i in range(1, 5):
                name = f"code{i}"
                ud = os.path.join(base_dir, f"Code{i}", "user-data")
                ex = os.path.join(base_dir, f"Code{i}", "extensions")
                self.cfg["profiles"][name] = f"{ud}|{ex}"
            self.save()
        else:
            if "ui_scale" not in self.cfg["app"]:
                self.cfg["app"]["ui_scale"] = "Auto"
                self.save()

    def _create_default(self) -> None:
        self.cfg["app"] = {
            "vscode_path": autodetect_vscode_path(),
            "base_dir": self._default_base_dir(),
            "open_new_window": "1",
            "reuse_existing_window": "0",
            "extra_args": "",
            "theme": "Dark",
            "ui_scale": "Auto",
        }
        self.cfg["profiles"] = {}
        ensure_dir(app_dir())
        self.save()

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            self.cfg.write(f)

    def get_app(self) -> dict:
        return dict(self.cfg["app"])

    def set_app(self, key: str, value: str) -> None:
        self.cfg["app"][key] = value

    def get_profiles(self) -> list[Profile]:
        out: list[Profile] = []
        for name, value in self.cfg["profiles"].items():
            parts = value.split("|", 1)
            ud = norm(parts[0]) if parts else ""
            ex = norm(parts[1]) if len(parts) > 1 else ""
            out.append(Profile(name, ud, ex))
        out.sort(key=lambda p: p.name.lower())
        return out

    def upsert_profile(self, p: Profile) -> None:
        self.cfg["profiles"][p.name] = f"{p.user_data}|{p.extensions}"

    def delete_profile(self, name: str) -> None:
        if name in self.cfg["profiles"]:
            del self.cfg["profiles"][name]


# -----------------------------
# Profile editor dialog (compact)
# -----------------------------

class ProfileEditor(tk.Toplevel):
    def __init__(self, master: tk.Tk, title: str, initial: Profile | None, base_dir: str):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result: Profile | None = None
        self._master_app = getattr(master, "palette", None) and master or None

        self.base_dir = norm(base_dir)
        self.var_name = tk.StringVar(value=(initial.name if initial else "codeX"))
        self.var_user_data = tk.StringVar(value=(initial.user_data if initial else ""))
        self.var_extensions = tk.StringVar(value=(initial.extensions if initial else ""))

        if self._master_app:
            self.configure(bg=self._master_app.palette["bg"])
        frm = ttk.Frame(self, style="Card.TFrame" if self._master_app else "TFrame", padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.columnconfigure(1, weight=1)

        lbl_style = "Card.TLabel" if self._master_app else "TLabel"
        ttk.Label(frm, text="Name", style=lbl_style).grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.var_name, width=46).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(frm, text="User Data", style=lbl_style).grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frm, textvariable=self.var_user_data, width=46).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))
        ttk.Button(frm, text="Browse…", command=self.browse_ud, takefocus=False, cursor="hand2").grid(row=1, column=2, padx=(8, 0), pady=(8, 0))

        ttk.Label(frm, text="Extensions", style=lbl_style).grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frm, textvariable=self.var_extensions, width=46).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))
        ttk.Button(frm, text="Browse…", command=self.browse_ex, takefocus=False, cursor="hand2").grid(row=2, column=2, padx=(8, 0), pady=(8, 0))

        ttk.Separator(frm).grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(frm, text="Auto-Fill from Base", command=self.autofill, takefocus=False, cursor="hand2").grid(row=4, column=0, columnspan=3, sticky="ew")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=3, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy, takefocus=False, cursor="hand2").grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Save", command=self.save, takefocus=False, cursor="hand2").grid(row=0, column=1)

        self.bind("<Return>", lambda _e: self.save())
        self.bind("<Escape>", lambda _e: self.destroy())

        self.transient(master)
        self.grab_set()
        self.wait_visibility()
        self._center_on(master)
        self.focus_force()

    def _center_on(self, master: tk.Tk) -> None:
        """Center this window on the master window."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        mx = master.winfo_x()
        my = master.winfo_y()
        mw = master.winfo_width()
        mh = master.winfo_height()
        x = mx + max(0, (mw - w) // 2)
        y = my + max(0, (mh - h) // 2)
        self.geometry(f"+{x}+{y}")

    def autofill(self) -> None:
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning(APP_NAME, "Enter a name first.")
            return
        folder = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
        self.var_user_data.set(norm(os.path.join(self.base_dir, folder, "user-data")))
        self.var_extensions.set(norm(os.path.join(self.base_dir, folder, "extensions")))

    def browse_ud(self) -> None:
        d = filedialog.askdirectory(title="Select User Data Folder")
        if d:
            self.var_user_data.set(norm(d))

    def browse_ex(self) -> None:
        d = filedialog.askdirectory(title="Select Extensions Folder")
        if d:
            self.var_extensions.set(norm(d))

    def save(self) -> None:
        name = self.var_name.get().strip()
        ud = norm(self.var_user_data.get())
        ex = norm(self.var_extensions.get())
        if not name:
            messagebox.showerror(APP_NAME, "Name cannot be empty.")
            return
        if not ud or not ex:
            messagebox.showerror(APP_NAME, "User Data and Extensions are required.")
            return
        self.result = Profile(name, ud, ex)
        self.destroy()


# -----------------------------
# Styled delete confirmation dialog
# -----------------------------

class DeleteConfirmDialog(tk.Toplevel):
    """Themed confirmation dialog so it doesn't look like a default messagebox."""

    def __init__(self, master: "App", profile_name: str):
        super().__init__(master)
        self.master_app = master
        self.profile_name = profile_name
        self.confirmed = False

        self.title("Remove profile")
        self.resizable(False, False)
        self.configure(bg=master.palette["bg"])

        outer = ttk.Frame(self, style="Card.TFrame", padding=16)
        outer.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(
            outer,
            text=f'"{profile_name}" will be removed from the list.',
            style="Card.TLabel",
            font=(master.base_font.cget("family"), master.base_font.cget("size") + 1, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            outer,
            text="Your data folders stay on disk. Use Save Config when you're done to write the change.",
            style="Card.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

        btn_row = ttk.Frame(outer)
        btn_row.grid(row=2, column=0, sticky="e")
        ttk.Button(btn_row, text="Cancel", command=self._cancel, takefocus=False, cursor="hand2").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Remove", style="Danger.TButton", command=self._remove, takefocus=False, cursor="hand2").pack(side="left")

        self.transient(master)
        self.bind("<Escape>", lambda _e: self._cancel())
        self.grab_set()
        self.wait_visibility()
        self._center_on(master)
        self.focus_force()

    def _center_on(self, master: tk.Misc) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        mx = master.winfo_x()
        my = master.winfo_y()
        mw = master.winfo_width()
        mh = master.winfo_height()
        x = mx + max(0, (mw - w) // 2)
        y = my + max(0, (mh - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _cancel(self) -> None:
        self.destroy()

    def _remove(self) -> None:
        self.confirmed = True
        self.destroy()


# -----------------------------
# Styled Save confirmation dialog
# -----------------------------

class SaveConfirmDialog(tk.Toplevel):
    """Themed confirmation for saving configuration; follows app dark/light theme."""

    def __init__(self, master: "App"):
        super().__init__(master)
        self.confirmed = False

        self.title("Save configuration")
        self.resizable(False, False)
        self.configure(bg=master.palette["bg"])

        outer = ttk.Frame(self, style="Card.TFrame", padding=16)
        outer.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(
            outer,
            text="Save configuration to file?",
            style="Card.TLabel",
            font=(master.base_font.cget("family"), master.base_font.cget("size") + 1, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            outer,
            text="Your current settings will be written to the config file.",
            style="Card.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

        btn_row = ttk.Frame(outer)
        btn_row.grid(row=2, column=0, sticky="e")
        ttk.Button(btn_row, text="Cancel", command=self._cancel, takefocus=False, cursor="hand2").pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Save", style="Accent.TButton", command=self._save, takefocus=False, cursor="hand2").pack(side="left")

        self.transient(master)
        self.bind("<Escape>", lambda _e: self._cancel())
        self.grab_set()
        self.wait_visibility()
        self._center_on(master)
        self.focus_force()

    def _center_on(self, master: tk.Misc) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        mx = master.winfo_x()
        my = master.winfo_y()
        mw = master.winfo_width()
        mh = master.winfo_height()
        x = mx + max(0, (mw - w) // 2)
        y = my + max(0, (mh - h) // 2)
        self.geometry(f"+{x}+{y}")

    def _cancel(self) -> None:
        self.destroy()

    def _save(self) -> None:
        self.confirmed = True
        self.destroy()


# -----------------------------
# Styled info dialog (one button)
# -----------------------------

class InfoDialog(tk.Toplevel):
    """Themed info message; follows app dark/light theme."""

    def __init__(self, master: "App", title: str, message: str):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=master.palette["bg"])

        outer = ttk.Frame(self, style="Card.TFrame", padding=16)
        outer.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(outer, text=message, style="Card.TLabel", wraplength=360).grid(row=0, column=0, sticky="w", pady=(0, 16))
        ttk.Button(outer, text="OK", style="Accent.TButton", command=self.destroy, takefocus=False, cursor="hand2").grid(row=1, column=0, sticky="e")

        self.transient(master)
        self.bind("<Return>", lambda _e: self.destroy())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.grab_set()
        self.wait_visibility()
        self._center_on(master)
        self.focus_force()

    def _center_on(self, master: tk.Misc) -> None:
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        mx = master.winfo_x()
        my = master.winfo_y()
        mw = master.winfo_width()
        mh = master.winfo_height()
        x = mx + max(0, (mw - w) // 2)
        y = my + max(0, (mh - h) // 2)
        self.geometry(f"+{x}+{y}")


# -----------------------------
# Main App (compact + responsive)
# -----------------------------

class App(tk.Tk):
    THEME_OPTIONS = ["Dark", "Light"]
    SCALE_OPTIONS = ["Auto", "100%", "125%", "150%", "175%", "200%", "225%", "250%", "300%"]
    # Minimum size so the right action menu is always visible; window cannot be resized smaller
    MIN_WIDTH = 1024
    MIN_HEIGHT = 620

    @staticmethod
    def _normalize_theme(raw: str) -> str:
        v = (raw or "").strip().lower()
        return "Dark" if v == "dark" else "Light"

    def _theme_is_dark(self) -> bool:
        return (self.var_theme.get() or "").strip().lower() == "dark"

    def __init__(self):
        # DPI awareness on Windows can reduce pixelation
        if platform.system() == "Windows":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
        super().__init__()
        self.title(APP_NAME)
        _icon = os.path.join(getattr(sys, "_MEIPASS", app_dir()), "app.ico")
        if os.path.isfile(_icon):
            try:
                self.iconbitmap(_icon)
            except Exception:
                pass
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.bind("<Configure>", self._enforce_min_size)

        self.cm = ConfigManager(config_path())
        self.cm.load()
        app = self.cm.get_app()

        self.var_vscode_path = tk.StringVar(value=norm(app.get("vscode_path", "")))
        self.var_base_dir = tk.StringVar(value=norm(app.get("base_dir", "")))
        self.var_open_new_window = tk.IntVar(value=int(app.get("open_new_window", "1")))
        self.var_reuse_existing_window = tk.IntVar(value=int(app.get("reuse_existing_window", "0")))
        self.var_extra_args = tk.StringVar(value=app.get("extra_args", ""))
        self.var_theme = tk.StringVar(value=self._normalize_theme(app.get("theme", "Dark")))
        self.var_ui_scale = tk.StringVar(value=(app.get("ui_scale", "Auto") or "Auto"))

        self.status = tk.StringVar(value=f"Config: {config_path()}")

        # Fonts
        self.base_font = tkfont.nametofont("TkDefaultFont")
        if os_name() == "Windows":
            try:
                self.base_font.configure(family="Segoe UI")
            except Exception:
                pass

        # Style
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.palette = self._palette_dark() if self._theme_is_dark() else self._palette_light()
        self._apply_style()
        self._apply_scale()  # Apply before building UI so scaling is correct from the start
        self._build_ui()
        self._refresh_list()

        # Start centered on screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"+{x}+{y}")

        # fix “dotted focus” look: prevent focus by default
        self.bind_all("<Button-1>", self._defocus_on_click, add="+")

    def _enforce_min_size(self, event=None):
        """Keep window from being resized smaller than MIN so the right menu stays visible."""
        if event and event.widget != self:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w < self.MIN_WIDTH or h < self.MIN_HEIGHT:
            self.geometry(f"{max(w, self.MIN_WIDTH)}x{max(h, self.MIN_HEIGHT)}")

    def _defocus_on_click(self, e):
        # keep focus from sticking on buttons (less ugly on ttk/clam); skip when clicking a button to avoid extra work
        try:
            if isinstance(e.widget, ttk.Button):
                return
            w = self.focus_get()
            if isinstance(w, ttk.Button):
                self.focus_set()
        except Exception:
            pass

    def _palette_dark(self) -> dict:
        return {
            "bg": "#1E1E1E",
            "panel": "#252526",
            "panel2": "#2D2D2D",
            "border": "#3C3C3C",
            "text": "#D4D4D4",
            "muted": "#9DA2A6",
            "accent": "#007ACC",
            "accent_hover": "#1A8AD4",
            "danger": "#F14C4C",
            "danger_hover": "#FF6B6B",
            "button_hover": "#3C3C3C",
            "warning": "#F14C4C",
            "field": "#1F1F1F",
            "select": "#094771",
            "button_border": "#6C6C6C",
        }

    def _palette_light(self) -> dict:
        return {
            "bg": "#F3F3F3",
            "panel": "#FFFFFF",
            "panel2": "#F6F6F6",
            "border": "#D0D0D0",
            "text": "#1E1E1E",
            "muted": "#5A5A5A",
            "accent": "#007ACC",
            "accent_hover": "#3399DD",
            "danger": "#C62828",
            "danger_hover": "#E53935",
            "button_hover": "#E8E8E8",
            "warning": "#C62828",
            "field": "#FFFFFF",
            "select": "#CFE8FF",
            "button_border": "#5A5A5A",
        }

    def _apply_style(self) -> None:
        p = self.palette
        self.configure(bg=p["bg"])

        self.style.configure(".", background=p["bg"], foreground=p["text"])
        self.style.configure("TFrame", background=p["bg"])
        self.style.configure("TLabel", background=p["bg"], foreground=p["text"])
        self.style.configure("Muted.TLabel", background=p["bg"], foreground=p["muted"])
        # Labels on cards must use panel background so they don't show a different color
        self.style.configure("Card.TLabel", background=p["panel"], foreground=p["text"])
        self.style.configure("Warning.TLabel", background=p["panel"], foreground=p["warning"], font=(self.base_font.cget("family"), self.base_font.cget("size"), "normal"))

        self.style.configure("Card.TFrame", background=p["panel"], relief="flat", borderwidth=1)

        self.style.configure("TEntry", fieldbackground=p["field"], foreground=p["text"])
        # Dropdown (Combobox): theme-matched border and padding so it doesn't look broken
        self.style.configure(
            "TCombobox",
            fieldbackground=p["field"],
            foreground=p["text"],
            background=p["panel2"],
            bordercolor=p["button_border"],
            borderwidth=1,
            padding=(6, 4),
            arrowcolor=p["text"],
        )
        # Keep text and field colors correct when dropdown is pressed/focused (fixes light theme text turning white)
        self.style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", p["field"]),
                ("focus", p["field"]),
                ("pressed", p["field"]),
            ],
            foreground=[
                ("readonly", p["text"]),
                ("focus", p["text"]),
                ("pressed", p["text"]),
            ],
            background=[
                ("readonly", p["panel2"]),
                ("focus", p["panel2"]),
                ("pressed", p["panel2"]),
            ],
            arrowcolor=[
                ("readonly", p["text"]),
                ("focus", p["text"]),
                ("pressed", p["text"]),
            ],
        )

        # Buttons: theme-matched border (dark theme = light border, light theme = dark border)
        self.style.configure(
            "TButton",
            background=p["panel2"],
            foreground=p["text"],
            padding=(6, 4),
            relief="solid",
            borderwidth=1,
            bordercolor=p["button_border"],
        )
        self.style.map("TButton", background=[("active", p["button_hover"]), ("pressed", p["border"])])
        try:
            self.style.configure("TButton", focusthickness=0, focuspadding=0)
        except Exception:
            pass

        self.style.configure(
            "Accent.TButton",
            background=p["accent"],
            foreground="#FFFFFF",
            padding=(6, 5),
            relief="solid",
            borderwidth=1,
            bordercolor=p["button_border"],
        )
        self.style.map("Accent.TButton", background=[("active", p["accent_hover"]), ("pressed", p["accent"])])

        self.style.configure(
            "Danger.TButton",
            background=p["panel2"],
            foreground=p["danger"],
            padding=(6, 4),
            relief="solid",
            borderwidth=1,
            bordercolor=p["button_border"],
        )
        self.style.map("Danger.TButton", background=[("active", p["button_hover"]), ("pressed", p["border"])])

        self.style.configure("Treeview", background=p["field"], fieldbackground=p["field"], foreground=p["text"], relief="flat", borderwidth=0)
        self.style.map("Treeview", background=[("selected", p["select"])], foreground=[("selected", "#FFFFFF" if self._theme_is_dark() else p["text"])])
        self.style.configure("Treeview.Heading", background=p["panel2"], foreground=p["text"], padding=(12, 10), relief="flat")
        if hasattr(self, "body_sep"):
            self.body_sep.configure(bg=p["border"])
        if hasattr(self, "header_sep1"):
            self.header_sep1.configure(bg=p["border"])
        if hasattr(self, "header_sep2"):
            self.header_sep2.configure(bg=p["border"])

    def _parse_ui_scale(self) -> float | None:
        v = (self.var_ui_scale.get() or "").strip()
        if v.lower() == "auto":
            return None
        if v.endswith("%"):
            try:
                pct = float(v[:-1])
                factor = pct / 100.0
                return (96.0 * factor) / 72.0
            except Exception:
                return None
        return None

    def _apply_scale(self) -> None:
        forced = self._parse_ui_scale()
        if forced is not None:
            self.tk.call("tk", "scaling", forced)
        else:
            self.tk.call("tk", "scaling", 96.0 / 72.0)
        self.update_idletasks()
        self._update_tree_rowheight()

    def _update_tree_rowheight(self) -> None:
        linespace = self.base_font.metrics("linespace")
        self.style.configure("Treeview", rowheight=max(int(linespace + 16), 34))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=6)
        root.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        # ---- Top panel (compact)
        top = ttk.Frame(root, style="Card.TFrame", padding=6)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="VS Code Path", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.entry_vscode_path = ttk.Entry(top, textvariable=self.var_vscode_path)
        self.entry_vscode_path.grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(top, text="Browse", command=self._browse_vscode, takefocus=False, cursor="hand2").grid(row=0, column=2, padx=(0, 4))
        ttk.Button(top, text="Detect", command=self._detect_vscode, takefocus=False, cursor="hand2").grid(row=0, column=3)

        ttk.Label(top, text="Base Dir", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.entry_base_dir = ttk.Entry(top, textvariable=self.var_base_dir)
        self.entry_base_dir.grid(row=1, column=1, sticky="ew", padx=(6, 6), pady=(6, 0))
        ttk.Button(top, text="Browse", command=self._browse_base, takefocus=False, cursor="hand2").grid(row=1, column=2, padx=(0, 4), pady=(6, 0))

        # Read-only: change only via Browse/Detect
        self.entry_vscode_path.config(state="disabled")
        self.entry_base_dir.config(state="disabled")

        # Theme + UI Scale aligned right (compact); Theme: Dark / Light (case-sensitive)
        right = ttk.Frame(top, style="Card.TFrame")
        right.grid(row=0, column=4, rowspan=2, sticky="e", padx=(10, 0))
        ttk.Label(right, text="Theme", style="Card.TLabel").grid(row=0, column=0, sticky="e", padx=(0, 4))
        theme = ttk.Combobox(right, textvariable=self.var_theme, values=self.THEME_OPTIONS, state="readonly", width=8)
        theme.grid(row=0, column=1, sticky="e")
        theme.bind("<<ComboboxSelected>>", lambda _e: self._on_theme_change())

        ttk.Label(right, text="UI Scale", style="Card.TLabel").grid(row=1, column=0, sticky="e", padx=(0, 4), pady=(6, 0))
        scale = ttk.Combobox(right, textvariable=self.var_ui_scale, values=self.SCALE_OPTIONS, state="readonly", width=8)
        scale.grid(row=1, column=1, sticky="e", pady=(6, 0))
        scale.bind("<<ComboboxSelected>>", lambda _e: self._on_scale_change())

        # ---- Middle panel
        mid = ttk.Frame(root, style="Card.TFrame", padding=8)
        mid.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        mid.columnconfigure(0, weight=1)
        mid.rowconfigure(0, weight=1)

        # Body: tree + separator + rail
        body = ttk.Frame(mid)
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.columnconfigure(2, weight=0)
        body.rowconfigure(0, weight=1)

        # Left: table (custom header with separators + spacing)
        table = ttk.Frame(body, padding=(0, 4))
        table.grid(row=0, column=0, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=0)
        table.rowconfigure(1, weight=1)
        table.rowconfigure(2, weight=0)

        # Custom header row: titles + vertical separators (title only)
        header_frm = ttk.Frame(table, style="Card.TFrame")
        header_frm.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        header_frm.columnconfigure(0, weight=0, minsize=100)
        header_frm.columnconfigure(1, weight=0, minsize=2)
        header_frm.columnconfigure(2, weight=1, minsize=180)
        header_frm.columnconfigure(3, weight=0, minsize=2)
        header_frm.columnconfigure(4, weight=1, minsize=180)
        ttk.Label(header_frm, text="Profile", style="Card.TLabel", font=(self.base_font.cget("family"), self.base_font.cget("size"), "bold")).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=6)
        self.header_sep1 = tk.Frame(header_frm, width=2, bg=self.palette["border"], highlightthickness=0)
        self.header_sep1.grid(row=0, column=1, sticky="ns")
        self.header_sep1.grid_propagate(False)
        ttk.Label(header_frm, text="User Data Dir", style="Card.TLabel", font=(self.base_font.cget("family"), self.base_font.cget("size"), "bold")).grid(row=0, column=2, sticky="w", padx=(12, 8), pady=6)
        self.header_sep2 = tk.Frame(header_frm, width=2, bg=self.palette["border"], highlightthickness=0)
        self.header_sep2.grid(row=0, column=3, sticky="ns")
        self.header_sep2.grid_propagate(False)
        ttk.Label(header_frm, text="Extensions Dir", style="Card.TLabel", font=(self.base_font.cget("family"), self.base_font.cget("size"), "bold")).grid(row=0, column=4, sticky="w", padx=(12, 8), pady=6)

        cols = ("name", "user_data", "extensions")
        # show="headings" would show a header row; use "" so only our custom header row is visible
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=10, takefocus=False)
        self.tree.grid(row=1, column=0, sticky="nsew")
        # Hide the native heading row (no text + zero height via style not possible, so we use show="" after setting columns)
        self.tree["show"] = ""
        self.tree.column("name", width=100, minwidth=80, stretch=False, anchor="w")
        self.tree.column("user_data", width=280, minwidth=180, stretch=True, anchor="w")
        self.tree.column("extensions", width=280, minwidth=180, stretch=True, anchor="w")

        vsb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns", padx=(6, 0))

        hsb = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        hsb.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        self.tree.bind("<Double-1>", lambda _e: self.launch_selected())

        # Thin divider between tree and rail (tk.Frame is lighter than ttk.Separator on resize)
        self.body_sep = tk.Frame(body, width=2, bg=self.palette["border"], highlightthickness=0)
        self.body_sep.grid(row=0, column=1, sticky="ns", padx=(4, 4))
        self.body_sep.grid_propagate(False)

        # Right: fixed narrow rail
        rail = ttk.Frame(body, width=130)
        rail.grid(row=0, column=2, sticky="ns", padx=(4, 0))
        rail.grid_propagate(False)  # IMPORTANT: enforce width

        def rbtn(text, cmd, style="TButton", pady=(0, 4)):
            b = ttk.Button(rail, text=text, command=cmd, style=style, takefocus=False, cursor="hand2")
            b.pack(fill="x", pady=pady)
            return b

        rbtn("Launch", self.launch_selected, style="Accent.TButton", pady=(0, 4))
        rbtn("Add", self.add_profile)
        rbtn("Edit", self.edit_profile)
        rbtn("Delete", self.delete_profile, style="Danger.TButton", pady=(0, 4))

        ttk.Separator(rail).pack(fill="x", pady=(4, 6))

        rbtn("Open User Data", self.open_user_data)
        rbtn("Open Extensions", self.open_extensions)
        rbtn("Open Base Dir", self.open_base_dir, pady=(0, 4))

        ttk.Separator(rail).pack(fill="x", pady=(4, 6))

        rbtn("Save Config", self.save_config)
        rbtn("Reload", self.reload_config, pady=(0, 0))

        # Status line
        status = ttk.Frame(root, padding=(2, 4, 2, 0))
        status.grid(row=2, column=0, sticky="ew")
        status.columnconfigure(0, weight=1)
        ttk.Label(status, textvariable=self.status, style="Muted.TLabel").grid(row=0, column=0, sticky="w")

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.profiles = self.cm.get_profiles()
        for p in self.profiles:
            self.tree.insert("", "end", values=(p.name, p.user_data, p.extensions))
        kids = self.tree.get_children()
        if kids:
            self.tree.selection_set(kids[0])
            self.tree.focus(kids[0])

    def selected_profile(self) -> Profile | None:
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return None
        name = vals[0]
        for p in self.profiles:
            if p.name == name:
                return p
        return None

    def _browse_vscode(self):
        if os_name() == "Windows":
            fp = filedialog.askopenfilename(
                title="Select VS Code executable (Code.exe)",
                filetypes=[("VS Code", "Code.exe"), ("Executable", "*.exe"), ("All files", "*.*")]
            )
        else:
            fp = filedialog.askopenfilename(title="Select VS Code launcher/binary (code)")
        if fp:
            self.entry_vscode_path.config(state="normal")
            self.var_vscode_path.set(norm(fp))
            self.entry_vscode_path.config(state="disabled")

    def _detect_vscode(self):
        p = autodetect_vscode_path()
        if p:
            self.entry_vscode_path.config(state="normal")
            self.var_vscode_path.set(norm(p))
            self.entry_vscode_path.config(state="disabled")
            self.status.set(f"Detected VS Code: {p}")
        else:
            messagebox.showwarning(APP_NAME, "Could not auto-detect VS Code.")

    def _browse_base(self):
        d = filedialog.askdirectory(title="Select Base Directory")
        if d:
            self.entry_base_dir.config(state="normal")
            self.var_base_dir.set(norm(d))
            self.entry_base_dir.config(state="disabled")

    def _on_theme_change(self):
        self.palette = self._palette_dark() if self._theme_is_dark() else self._palette_light()
        self._apply_style()
        self._apply_scale()

    def _on_scale_change(self):
        InfoDialog(
            self,
            "UI scale",
            "The new UI scale will take effect after you save and restart.\n\n"
            "1. Click Save Config to write your settings.\n\n"
            "2. Close and reopen the app to apply the new scale.",
        )
        self._apply_scale()
        self._apply_style()  # Reapply styles so fonts/row heights reflect new scaling

    def add_profile(self):
        ed = ProfileEditor(self, "Add Profile", None, self.var_base_dir.get())
        if ed.result:
            existing = {p.name.lower() for p in self.cm.get_profiles()}
            if ed.result.name.lower() in existing:
                messagebox.showerror(APP_NAME, "Profile name already exists.")
                return
            self.cm.upsert_profile(ed.result)
            self._refresh_list()

    def edit_profile(self):
        p = self.selected_profile()
        if not p:
            messagebox.showinfo(APP_NAME, "Select a profile first.")
            return
        ed = ProfileEditor(self, "Edit Profile", p, self.var_base_dir.get())
        if ed.result:
            existing = {x.name.lower() for x in self.cm.get_profiles() if x.name.lower() != p.name.lower()}
            if ed.result.name.lower() in existing:
                messagebox.showerror(APP_NAME, "Another profile with that name already exists.")
                return
            if ed.result.name != p.name:
                self.cm.delete_profile(p.name)
            self.cm.upsert_profile(ed.result)
            self._refresh_list()

    def delete_profile(self):
        p = self.selected_profile()
        if not p:
            messagebox.showinfo(APP_NAME, "Select a profile first.")
            return
        d = DeleteConfirmDialog(self, p.name)
        self.wait_window(d)
        if not d.confirmed:
            return
        self.cm.delete_profile(p.name)
        self._refresh_list()

    def open_user_data(self):
        p = self.selected_profile()
        if not p:
            messagebox.showinfo(APP_NAME, "Select a profile first.")
            return
        open_folder_cross_platform(p.user_data)

    def open_extensions(self):
        p = self.selected_profile()
        if not p:
            messagebox.showinfo(APP_NAME, "Select a profile first.")
            return
        open_folder_cross_platform(p.extensions)

    def open_base_dir(self):
        open_folder_cross_platform(self.var_base_dir.get())

    def save_config(self):
        d = SaveConfirmDialog(self)
        self.wait_window(d)
        if not d.confirmed:
            return
        self.cm.set_app("vscode_path", norm(self.var_vscode_path.get()))
        self.cm.set_app("base_dir", norm(self.var_base_dir.get()))
        self.cm.set_app("open_new_window", "1" if self.var_open_new_window.get() else "0")
        self.cm.set_app("reuse_existing_window", "1" if self.var_reuse_existing_window.get() else "0")
        self.cm.set_app("extra_args", (self.var_extra_args.get() or "").strip())
        self.cm.set_app("theme", self.var_theme.get())
        self.cm.set_app("ui_scale", self.var_ui_scale.get())
        self.cm.save()
        self.status.set(f"Saved config: {config_path()}")
        d = InfoDialog(self, "Configuration saved", "Your settings have been written to the config file.")
        self.wait_window(d)

    def reload_config(self):
        self.cm.load()
        app = self.cm.get_app()
        self.var_vscode_path.set(norm(app.get("vscode_path", "")))
        self.var_base_dir.set(norm(app.get("base_dir", "")))
        self.var_open_new_window.set(int(app.get("open_new_window", "1")))
        self.var_reuse_existing_window.set(int(app.get("reuse_existing_window", "0")))
        self.var_extra_args.set(app.get("extra_args", ""))
        self.var_theme.set(self._normalize_theme(app.get("theme", "Dark")))
        self.var_ui_scale.set(app.get("ui_scale", "Auto") or "Auto")

        self.palette = self._palette_dark() if self._theme_is_dark() else self._palette_light()
        self._apply_style()
        self._apply_scale()
        self._refresh_list()
        self.status.set(f"Reloaded config: {config_path()}")

    def launch_selected(self):
        vscode = norm(self.var_vscode_path.get())
        if not is_executable_path(vscode):
            messagebox.showerror(APP_NAME, "VS Code path is invalid. Set it on top.")
            return

        p = self.selected_profile()
        if not p:
            messagebox.showinfo(APP_NAME, "Select a profile first.")
            return

        p.ensure_folders()

        args = [
            vscode,
            "--user-data-dir", p.user_data,
            "--extensions-dir", p.extensions,
        ]
        if self.var_open_new_window.get() and not self.var_reuse_existing_window.get():
            args.append("--new-window")

        args.extend(split_args(self.var_extra_args.get()))

        try:
            subprocess.Popen(args, cwd=os.path.dirname(vscode) if os.path.isfile(vscode) else None)
            self.status.set(f"Launched {p.name}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Launch failed:\n\n{e}")


# -----------------------------
# Crash-safe launcher
# -----------------------------

def run_app():
    app = App()
    app.mainloop()

def crash_safe_main():
    try:
        run_app()
    except Exception:
        err = traceback.format_exc()
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(crash_log_path(), "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"{stamp}\n")
                f.write(err)
        except Exception:
            pass

        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                APP_NAME,
                "App crashed on startup.\n\n"
                "A crash.log file was created beside the EXE.\n\n"
                "Error:\n" + err.splitlines()[-1]
            )
            root.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    crash_safe_main()