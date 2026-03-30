"""Real-time folder watcher using watchdog."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .config import AppConfig
from .core import build_ext_map, classify, safe_move


class OrganizerEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        config: AppConfig,
        dry_run: bool,
        callback: Callable[[str, str], None],
    ) -> None:
        super().__init__()
        self._config = config
        self._dry_run = dry_run
        self._callback = callback
        self._ext_map = build_ext_map(config.categories)

    def on_created(self, event: FileCreatedEvent) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        path = Path(event.src_path)
        # Wait briefly for the file to finish writing (e.g. browser downloads)
        time.sleep(0.8)
        if not path.exists() or not path.is_file():
            return
        # Skip files already inside a category subfolder
        target = Path(self._config.target_dir).expanduser()
        if path.parent != target and path.parent.parent != target:
            return
        if path.parent != target:
            return
        category = classify(path.name, self._ext_map, self._config.fallback)
        dest_dir = target / category
        safe_move(path, dest_dir, self._dry_run, self._callback)


class WatcherManager:
    def __init__(self) -> None:
        self._observer: Observer | None = None

    def start(self, watch_dir: str, handler: OrganizerEventHandler) -> None:
        self._observer = Observer()
        self._observer.schedule(handler, str(Path(watch_dir).expanduser()), recursive=False)
        self._observer.start()

    def stop(self) -> None:
        if self._observer is None:
            return

        def _stop() -> None:
            assert self._observer is not None
            self._observer.stop()
            self._observer.join()

        threading.Thread(target=_stop, daemon=True).start()
        self._observer = None

    @property
    def is_running(self) -> bool:
        return self._observer is not None and self._observer.is_alive()
