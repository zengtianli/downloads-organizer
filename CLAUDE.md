# downloads-organizer — 按文件类型自动整理 Downloads 文件夹

## Quick Reference

| 项目 | 路径/值 |
|------|---------|
| 项目根 | `/Users/tianli/Dev/downloads-organizer` |
| 源码 | `src/downloads_organizer/` |
| 入口（GUI） | `src/downloads_organizer/gui.py` → `main()` |
| 入口（CLI） | `src/downloads_organizer/__main__.py` |
| 测试 | `tests/` |
| 配置 | `~/.config/downloads-organizer/config.yaml`（运行时生成） |

## 常用命令

```bash
# 开发环境安装（editable mode）
pip install -e ".[dev]"

# 启动 GUI
downloads-organizer
# 或
python -m downloads_organizer

# CLI 整理（dry-run 预览）
downloads-organizer --dry-run

# 实时监控模式
downloads-organizer --watch

# 一次性整理所有文件
downloads-organizer --organize

# 运行测试
pytest tests/
ruff check src/
```

## 项目结构

```
src/downloads_organizer/
├── __main__.py      # CLI 入口
├── gui.py           # customtkinter GUI，main() 在此
├── core.py          # 文件分类 + 移动逻辑
├── config.py        # YAML 配置读写
└── watcher.py       # watchdog 实时监控

tests/
├── test_core.py     # 核心逻辑测试
└── test_config.py   # 配置解析测试
```

## 依赖说明

| 库 | 用途 |
|----|------|
| `customtkinter` | 现代风格 Tkinter GUI |
| `watchdog` | 文件系统事件监听 |
| `PyYAML` | 配置文件读写 |

## 开发注意事项

- Python ≥ 3.11（pyproject.toml 要求，注意不是 3.9）
- 无需外部 API，不依赖 `~/.personal_env`
- 修改分类规则：编辑 `config.py` 中的默认 category 映射或用户 config.yaml
- GUI 与 core 逻辑分离，`core.py` 可独立测试无 GUI 依赖
- Raycast 快捷启动可添加到 `~/Dev/scripts/raycast/commands/`
