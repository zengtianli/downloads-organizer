# Downloads Organizer

A clean desktop app that automatically sorts your **Downloads folder** by file type — with real-time file watching and a modern GUI.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Platform macOS | Windows | Linux](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)

---

## Features

- **Real-time auto-organization** — watchdog monitors your folder; new files are sorted the moment they arrive
- **One-click "Organize Now"** — manually scan and sort everything at once
- **Dry Run (preview) mode** — see exactly what would move before committing
- **Editable categories** — add, remove, or rename folder categories and their file extensions directly in the GUI
- **Auto-save config** — every change is instantly persisted to `~/.config/downloads-organizer/config.yaml`
- **Cross-platform** — macOS, Windows, Linux
- **Collision-safe moves** — files are never overwritten; duplicates are auto-numbered (`file (1).pdf`)
- **Compound extension support** — `.tar.gz`, `.tar.bz2`, `.tar.xz` handled correctly

---

## Install

### Via pip

```bash
pip install downloads-organizer
downloads-organizer
```

### From source

```bash
git clone https://github.com/zengtianli/downloads-organizer
cd downloads-organizer
pip install -e .
python -m downloads_organizer
```

> **Linux users**: If tkinter is missing, run `sudo apt install python3-tk` (Debian/Ubuntu) first.

---

## Usage

1. **Set your Watch Folder** — defaults to `~/Downloads`. Click **Browse…** to change it.
2. Click **Organize Now** to sort all existing files in one pass.
3. Toggle **Start Watching** to continuously monitor for new files.
4. Enable **Dry Run** to preview moves in the log without actually moving anything.

### Keyboard shortcut

```bash
python -m downloads_organizer   # launch from terminal
```

---

## Default Categories

| Folder | Extensions |
|--------|-----------|
| Images | `.png` `.jpg` `.jpeg` `.gif` `.svg` `.webp` `.heic` `.bmp` `.tiff` |
| Documents | `.docx` `.doc` `.pdf` `.xlsx` `.xls` `.pptx` `.ppt` `.csv` `.txt` `.md` `.html` |
| Archives | `.zip` `.rar` `.7z` `.tar.gz` `.tar` `.tar.bz2` `.tar.xz` |
| Installers | `.dmg` `.pkg` `.iso` `.app` `.exe` `.msi` `.deb` `.rpm` |
| Media | `.mp4` `.mov` `.mp3` `.wav` `.avi` `.mkv` `.flac` `.aac` `.m4a` |
| Mail | `.eml` `.msg` |
| Config | `.plist` `.json` `.yaml` `.yml` `.toml` `.conf` `.ini` `.cfg` |
| Others | *(any unmatched extension)* |

---

## Configuration

Config file: `~/.config/downloads-organizer/config.yaml`

```yaml
target_dir: ~/Downloads
scan_dirs:
  - ~/Downloads
categories:
  Images:
    - .png
    - .jpg
  Documents:
    - .pdf
    - .docx
  # ... add your own
fallback: Others
ignore_prefixes:
  - "~$"
  - "."
auto_watch: false
dry_run: false
```

Category folder names support any language — rename `Images` to `图片` or `Bilder` as needed.

---

## Development

```bash
git clone https://github.com/zengtianli/downloads-organizer
cd downloads-organizer
pip install -e ".[dev]"
pytest          # run tests
ruff check src/ # lint
```

---

## License

MIT © tianli

---

[中文文档 →](README_CN.md)
