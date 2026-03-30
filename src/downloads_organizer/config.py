"""App configuration: load, save, and default generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "downloads-organizer" / "config.yaml"

_DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".heic", ".bmp", ".tiff"],
    "Documents": [".docx", ".doc", ".pdf", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".txt", ".md", ".html"],
    "Archives": [".zip", ".rar", ".7z", ".tar.gz", ".tar", ".tar.bz2", ".tar.xz"],
    "Installers": [".dmg", ".pkg", ".iso", ".app", ".exe", ".msi", ".deb", ".rpm"],
    "Media": [".mp4", ".mov", ".mp3", ".wav", ".avi", ".mkv", ".flac", ".aac", ".m4a"],
    "Mail": [".eml", ".msg"],
    "Config": [".plist", ".json", ".yaml", ".yml", ".toml", ".conf", ".ini", ".cfg"],
}


@dataclass
class AppConfig:
    target_dir: str = "~/Downloads"
    scan_dirs: list[str] = field(default_factory=lambda: ["~/Downloads"])
    categories: dict[str, list[str]] = field(default_factory=lambda: dict(_DEFAULT_CATEGORIES))
    fallback: str = "Others"
    ignore_prefixes: list[str] = field(default_factory=lambda: ["~$", "."])
    log_file: str = "~/.local/log/downloads-organizer.log"
    auto_watch: bool = False
    dry_run: bool = False


def default_config() -> AppConfig:
    return AppConfig()


def load_config() -> AppConfig:
    """Load config from disk, writing defaults if absent."""
    if not CONFIG_PATH.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return AppConfig(
        target_dir=data.get("target_dir", "~/Downloads"),
        scan_dirs=data.get("scan_dirs", ["~/Downloads"]),
        categories=data.get("categories", dict(_DEFAULT_CATEGORIES)),
        fallback=data.get("fallback", "Others"),
        ignore_prefixes=data.get("ignore_prefixes", ["~$", "."]),
        log_file=data.get("log_file", "~/.local/log/downloads-organizer.log"),
        auto_watch=data.get("auto_watch", False),
        dry_run=data.get("dry_run", False),
    )


def save_config(config: AppConfig) -> None:
    """Persist config to disk."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "target_dir": config.target_dir,
        "scan_dirs": config.scan_dirs,
        "categories": config.categories,
        "fallback": config.fallback,
        "ignore_prefixes": config.ignore_prefixes,
        "log_file": config.log_file,
        "auto_watch": config.auto_watch,
        "dry_run": config.dry_run,
    }
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
