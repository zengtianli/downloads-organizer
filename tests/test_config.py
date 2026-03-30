"""Tests for config load/save round-trip."""

from pathlib import Path

from downloads_organizer.config import AppConfig, default_config, load_config, save_config


def test_default_config_has_seven_categories():
    cfg = default_config()
    assert len(cfg.categories) == 7


def test_default_config_images_has_png():
    cfg = default_config()
    assert ".png" in cfg.categories["Images"]


def test_round_trip(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    monkeypatch.setattr("downloads_organizer.config.CONFIG_PATH", config_file)

    original = default_config()
    original.categories["TestCat"] = [".xyz"]
    save_config(original)

    loaded = load_config()
    assert loaded.categories.get("TestCat") == [".xyz"]
    assert loaded.fallback == "Others"


def test_load_creates_default_on_missing_file(tmp_path, monkeypatch):
    config_file = tmp_path / "subdir" / "config.yaml"
    monkeypatch.setattr("downloads_organizer.config.CONFIG_PATH", config_file)

    cfg = load_config()
    assert config_file.exists()
    assert isinstance(cfg, AppConfig)
    assert len(cfg.categories) == 7
