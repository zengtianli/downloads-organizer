"""Core file classification and organization logic."""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from pathlib import Path


def get_file_ext(filename: str) -> str:
    """Return file extension, handling compound extensions like .tar.gz."""
    lower = filename.lower()
    for compound in (".tar.gz", ".tar.bz2", ".tar.xz"):
        if lower.endswith(compound):
            return compound
    _, ext = os.path.splitext(lower)
    return ext


def build_ext_map(categories: dict[str, list[str]]) -> dict[str, str]:
    """Build extension -> category name lookup table."""
    ext_map: dict[str, str] = {}
    for category, extensions in categories.items():
        for ext in extensions:
            ext_map[ext.lower()] = category
    return ext_map


def classify(filename: str, ext_map: dict[str, str], fallback: str) -> str:
    """Return the target category name for a file."""
    ext = get_file_ext(filename)
    return ext_map.get(ext, fallback)


def should_ignore(filename: str, ignore_prefixes: list[str]) -> bool:
    """Return True if the file should be skipped."""
    return any(filename.startswith(prefix) for prefix in ignore_prefixes)


def safe_move(
    src: Path,
    dest_dir: Path,
    dry_run: bool,
    callback: Callable[[str, str], None] | None = None,
) -> bool:
    """Move src to dest_dir, auto-numbering on name collision.

    Returns True on success (or dry-run intent).
    """
    dest = dest_dir / src.name

    if dest.exists():
        # Handle compound extensions when building numbered names
        if src.name.lower().endswith(".tar.gz"):
            stem = src.name[: -len(".tar.gz")]
            ext = ".tar.gz"
        else:
            stem = src.stem
            ext = src.suffix
        counter = 1
        while dest.exists():
            dest = dest_dir / f"{stem} ({counter}){ext}"
            counter += 1

    if dry_run:
        if callback:
            callback("DRY", f"{src.name}  →  {dest_dir.name}/{dest.name}")
        return True

    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dest))
        if callback:
            callback("INFO", f"{src.name}  →  {dest.parent.name}/{dest.name}")
        return True
    except Exception as e:
        if callback:
            callback("ERROR", f"Failed to move {src.name}: {e}")
        return False


def scan_directory(
    scan_dir: Path,
    target_dir: Path,
    ext_map: dict[str, str],
    fallback: str,
    ignore_prefixes: list[str],
    dry_run: bool,
    callback: Callable[[str, str], None] | None = None,
) -> tuple[int, int]:
    """Scan one directory and move/classify files.

    Returns (moved_count, skipped_count).
    """
    moved = 0
    skipped = 0

    if not scan_dir.exists():
        if callback:
            callback("WARN", f"Directory not found, skipping: {scan_dir}")
        return moved, skipped

    for item in sorted(scan_dir.iterdir()):
        if not item.is_file():
            continue
        if should_ignore(item.name, ignore_prefixes):
            skipped += 1
            continue

        category = classify(item.name, ext_map, fallback)
        dest_dir = target_dir / category

        if item.parent == dest_dir:
            skipped += 1
            continue

        if safe_move(item, dest_dir, dry_run, callback):
            moved += 1

    return moved, skipped
