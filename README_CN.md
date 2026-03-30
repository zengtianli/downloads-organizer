# Downloads Organizer — Downloads 自动整理工具

一款整洁的桌面应用，可按文件类型自动整理 **Downloads 文件夹**，支持实时监控和现代化 GUI。

---

## 功能特点

- **实时自动整理** — 使用 watchdog 监控文件夹，新文件落地即分类
- **一键「立即整理」** — 手动扫描并整理所有现有文件
- **预览模式（Dry Run）** — 执行前查看哪些文件将被移动
- **可编辑分类** — 直接在 GUI 中增删改文件夹分类和扩展名
- **自动保存配置** — 每次修改即时持久化至 `~/.config/downloads-organizer/config.yaml`
- **跨平台** — macOS、Windows、Linux
- **安全移动** — 文件不会被覆盖，重名自动编号（`file (1).pdf`）
- **复合扩展名** — 正确处理 `.tar.gz`、`.tar.bz2`、`.tar.xz`

---

## 安装

### pip 安装

```bash
pip install downloads-organizer
downloads-organizer
```

### 源码安装

```bash
git clone https://github.com/zengtianli/downloads-organizer
cd downloads-organizer
pip install -e .
python -m downloads_organizer
```

> **Linux 用户**：若缺少 tkinter，先运行 `sudo apt install python3-tk`（Debian/Ubuntu）。

---

## 使用方法

1. **设置监控文件夹** — 默认 `~/Downloads`，点击 **Browse…** 可更改
2. 点击 **Organize Now** 一次性整理所有现有文件
3. 点击 **Start Watching** 开启实时监控
4. 勾选 **Dry Run** 可仅预览，不实际移动文件

---

## 默认分类

| 文件夹名 | 扩展名 |
|---------|--------|
| Images（图片） | `.png` `.jpg` `.jpeg` `.gif` `.svg` `.webp` `.heic` `.bmp` `.tiff` |
| Documents（文档） | `.docx` `.doc` `.pdf` `.xlsx` `.xls` `.pptx` `.ppt` `.csv` `.txt` `.md` `.html` |
| Archives（压缩包） | `.zip` `.rar` `.7z` `.tar.gz` `.tar` `.tar.bz2` `.tar.xz` |
| Installers（安装包） | `.dmg` `.pkg` `.iso` `.app` `.exe` `.msi` `.deb` `.rpm` |
| Media（视频音频） | `.mp4` `.mov` `.mp3` `.wav` `.avi` `.mkv` `.flac` `.aac` `.m4a` |
| Mail（邮件） | `.eml` `.msg` |
| Config（配置文件） | `.plist` `.json` `.yaml` `.yml` `.toml` `.conf` `.ini` `.cfg` |
| Others（其他） | *未匹配的扩展名* |

> **提示**：配置文件中的文件夹名称支持中文，可将 `Images` 改为 `图片`，`Documents` 改为 `文档` 等。

---

## 配置文件

路径：`~/.config/downloads-organizer/config.yaml`

```yaml
target_dir: ~/Downloads
scan_dirs:
  - ~/Downloads
categories:
  图片:
    - .png
    - .jpg
  文档:
    - .pdf
    - .docx
  # 按需添加
fallback: 其他
ignore_prefixes:
  - "~$"
  - "."
auto_watch: false
dry_run: false
```

---

## 开发

```bash
git clone https://github.com/zengtianli/downloads-organizer
cd downloads-organizer
pip install -e ".[dev]"
pytest          # 运行测试
ruff check src/ # 代码检查
```

---

## 许可证

MIT © tianli

---

[English →](README.md)
