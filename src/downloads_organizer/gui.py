"""customtkinter desktop GUI for Downloads Organizer."""

from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from .config import AppConfig, load_config, save_config
from .core import build_ext_map, scan_directory
from .watcher import OrganizerEventHandler, WatcherManager

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

_TAG_COLORS = {
    "INFO": "#4CAF50",   # green
    "DRY": "#90CAF9",    # blue
    "WARN": "#FFC107",   # amber
    "ERROR": "#F44336",  # red
}


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Downloads Organizer")
        self.geometry("960x640")
        self.minsize(800, 520)

        self._config: AppConfig = load_config()
        self._log_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._watcher = WatcherManager()
        self._move_count = 0
        self._skip_count = 0
        self._debounce_id: str | None = None

        self._build_ui()
        self._configure_log_tags()
        self._poll_log_queue()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if self._config.auto_watch:
            self.after(500, self._start_watching)

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        left = ctk.CTkFrame(self, width=300, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        left.grid_rowconfigure(3, weight=1)
        self._build_left(left)

        # Right panel
        right = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)
        self._build_right(right)

    def _build_left(self, parent: ctk.CTkFrame) -> None:
        # ── Watch folder ──────────────────────────────────────────────
        ctk.CTkLabel(parent, text="Watch Folder", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(14, 2)
        )

        self._folder_var = ctk.StringVar(value=self._config.scan_dirs[0] if self._config.scan_dirs else "~/Downloads")
        folder_entry = ctk.CTkEntry(parent, textvariable=self._folder_var, state="readonly", width=180)
        folder_entry.grid(row=1, column=0, sticky="ew", padx=(12, 4), pady=2)
        ctk.CTkButton(parent, text="Browse…", width=72, command=self._browse_folder).grid(
            row=1, column=1, sticky="w", padx=(0, 12), pady=2
        )
        parent.grid_columnconfigure(0, weight=1)

        # ── Options ───────────────────────────────────────────────────
        ctk.CTkLabel(parent, text="Options", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(14, 2)
        )
        self._dry_run_var = ctk.BooleanVar(value=self._config.dry_run)
        ctk.CTkCheckBox(parent, text="Dry Run (preview only)", variable=self._dry_run_var,
                        command=self._on_option_change).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=12, pady=4
        )
        self._auto_watch_var = ctk.BooleanVar(value=self._config.auto_watch)
        ctk.CTkCheckBox(parent, text="Auto-Watch on Startup", variable=self._auto_watch_var,
                        command=self._on_option_change).grid(
            row=4, column=0, columnspan=2, sticky="w", padx=12, pady=4
        )

        # ── Categories ────────────────────────────────────────────────
        ctk.CTkLabel(parent, text="Categories", font=ctk.CTkFont(weight="bold")).grid(
            row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(14, 2)
        )

        self._cat_scroll = ctk.CTkScrollableFrame(parent, label_text="", height=220)
        self._cat_scroll.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=12, pady=4)
        parent.grid_rowconfigure(6, weight=1)
        self._cat_scroll.grid_columnconfigure(0, weight=1)
        self._render_categories()

        ctk.CTkButton(parent, text="+ Add Category", command=self._add_category).grid(
            row=7, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 2)
        )

        # ── Action buttons ────────────────────────────────────────────
        ctk.CTkButton(parent, text="Organize Now", command=self._run_organize).grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=(14, 2)
        )
        self._start_btn = ctk.CTkButton(parent, text="Start Watching", fg_color="#2e7d32",
                                        hover_color="#1b5e20", command=self._start_watching)
        self._start_btn.grid(row=9, column=0, columnspan=2, sticky="ew", padx=12, pady=2)

        self._stop_btn = ctk.CTkButton(parent, text="Stop Watching", fg_color="#c62828",
                                       hover_color="#8b0000", state="disabled", command=self._stop_watching)
        self._stop_btn.grid(row=10, column=0, columnspan=2, sticky="ew", padx=12, pady=(2, 14))

    def _build_right(self, parent: ctk.CTkFrame) -> None:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        log_frame = ctk.CTkFrame(parent)
        log_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 4))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Activity Log", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 2)
        )

        self._log_box = ctk.CTkTextbox(log_frame, state="disabled", wrap="word",
                                       font=ctk.CTkFont(family="Menlo", size=12))
        self._log_box.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 8))

        # Status bar
        status_frame = ctk.CTkFrame(parent, height=32)
        status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_propagate(False)

        self._status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(status_frame, textvariable=self._status_var, anchor="w").grid(
            row=0, column=0, sticky="w", padx=10
        )
        self._count_var = ctk.StringVar(value="Moved: 0 | Skipped: 0")
        ctk.CTkLabel(status_frame, textvariable=self._count_var, anchor="e").grid(
            row=0, column=1, sticky="e", padx=10
        )

    def _render_categories(self) -> None:
        for w in self._cat_scroll.winfo_children():
            w.destroy()

        for i, (cat_name, exts) in enumerate(self._config.categories.items()):
            row_frame = ctk.CTkFrame(self._cat_scroll, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row_frame, text=cat_name, width=90, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w")

            ext_var = ctk.StringVar(value=", ".join(exts))
            ext_entry = ctk.CTkEntry(row_frame, textvariable=ext_var, height=26)
            ext_entry.grid(row=0, column=1, sticky="ew", padx=(4, 2))

            # Capture cat_name in closure
            def make_trace(name: str, var: ctk.StringVar):
                def _trace(*_):
                    self._schedule_save(name, var)
                return _trace

            ext_var.trace_add("write", make_trace(cat_name, ext_var))

            ctk.CTkButton(row_frame, text="✕", width=26, height=26, fg_color="#c62828",
                          hover_color="#8b0000",
                          command=lambda n=cat_name: self._remove_category(n)).grid(row=0, column=2)

    # ── Log helpers ───────────────────────────────────────────────────────

    def _configure_log_tags(self) -> None:
        tw = self._log_box._textbox
        for level, color in _TAG_COLORS.items():
            tw.tag_configure(level, foreground=color)

    def _log_callback(self, level: str, message: str) -> None:
        """Thread-safe: put message onto queue."""
        self._log_queue.put((level, message))

    def _poll_log_queue(self) -> None:
        while not self._log_queue.empty():
            level, message = self._log_queue.get_nowait()
            if level == "__COUNT__":
                moved, skipped = message.split(",")
                self._move_count += int(moved)
                self._skip_count += int(skipped)
                self._count_var.set(f"Moved: {self._move_count} | Skipped: {self._skip_count}")
            else:
                self._append_log(level, message)
        self.after(100, self._poll_log_queue)

    def _append_log(self, level: str, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        tw = self._log_box._textbox
        tw.configure(state="normal")
        tw.insert("end", f"{ts}  [{level}]  {message}\n", level)
        tw.configure(state="disabled")
        tw.see("end")

    # ── Actions ───────────────────────────────────────────────────────────

    def _browse_folder(self) -> None:
        chosen = filedialog.askdirectory(title="Select folder to watch/organize")
        if chosen:
            self._folder_var.set(chosen)
            self._config.scan_dirs = [chosen]
            self._config.target_dir = chosen
            save_config(self._config)

    def _on_option_change(self) -> None:
        self._config.dry_run = self._dry_run_var.get()
        self._config.auto_watch = self._auto_watch_var.get()
        save_config(self._config)

    def _schedule_save(self, cat_name: str, var: ctk.StringVar) -> None:
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(400, lambda: self._apply_ext_edit(cat_name, var))

    def _apply_ext_edit(self, cat_name: str, var: ctk.StringVar) -> None:
        raw = var.get()
        exts = [e.strip() for e in raw.replace(",", " ").split() if e.strip()]
        # Normalize: ensure leading dot
        exts = [e if e.startswith(".") else f".{e}" for e in exts]
        if cat_name in self._config.categories:
            self._config.categories[cat_name] = exts
            save_config(self._config)

    def _add_category(self) -> None:
        dialog = ctk.CTkInputDialog(text="New category name:", title="Add Category")
        name = dialog.get_input()
        if name and name.strip() and name.strip() not in self._config.categories:
            self._config.categories[name.strip()] = []
            save_config(self._config)
            self._render_categories()

    def _remove_category(self, cat_name: str) -> None:
        self._config.categories.pop(cat_name, None)
        save_config(self._config)
        self._render_categories()

    def _run_organize(self) -> None:
        config = self._config
        dry_run = self._dry_run_var.get()
        ext_map = build_ext_map(config.categories)
        target = Path(config.target_dir).expanduser()
        mode = "Preview" if dry_run else "Organize"

        def worker() -> None:
            self._log_callback("INFO", f"=== {mode} started ===")
            total_moved = total_skipped = 0
            for scan_dir_str in config.scan_dirs:
                m, s = scan_directory(
                    Path(scan_dir_str).expanduser(),
                    target,
                    ext_map,
                    config.fallback,
                    config.ignore_prefixes,
                    dry_run,
                    callback=self._log_callback,
                )
                total_moved += m
                total_skipped += s
            self._log_callback("INFO", f"=== Done: {total_moved} moved, {total_skipped} skipped ===")
            self._log_queue.put(("__COUNT__", f"{total_moved},{total_skipped}"))

        threading.Thread(target=worker, daemon=True).start()

    def _start_watching(self) -> None:
        if self._watcher.is_running:
            return
        folder = self._folder_var.get()
        handler = OrganizerEventHandler(
            config=self._config,
            dry_run=self._dry_run_var.get(),
            callback=self._log_callback,
        )
        self._watcher.start(folder, handler)
        self._status_var.set(f"Watching: {folder}")
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._log_callback("INFO", f"Watcher started on {folder}")

    def _stop_watching(self) -> None:
        self._watcher.stop()
        self._status_var.set("Ready")
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._log_callback("INFO", "Watcher stopped")

    def _on_close(self) -> None:
        if self._watcher.is_running:
            self._watcher.stop()
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()
