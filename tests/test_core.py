"""Tests for core classification and file-move logic."""

import pytest

from downloads_organizer.config import _DEFAULT_CATEGORIES
from downloads_organizer.core import (
    build_ext_map,
    classify,
    get_file_ext,
    safe_move,
    should_ignore,
)


@pytest.fixture()
def ext_map():
    return build_ext_map(_DEFAULT_CATEGORIES)


class TestGetFileExt:
    def test_normal_extension(self):
        assert get_file_ext("photo.jpg") == ".jpg"

    def test_uppercase_normalized(self):
        assert get_file_ext("Report.PDF") == ".pdf"

    def test_tar_gz(self):
        assert get_file_ext("archive.tar.gz") == ".tar.gz"

    def test_tar_bz2(self):
        assert get_file_ext("archive.tar.bz2") == ".tar.bz2"

    def test_tar_xz(self):
        assert get_file_ext("archive.tar.xz") == ".tar.xz"

    def test_no_extension(self):
        assert get_file_ext("Makefile") == ""


class TestClassify:
    def test_image(self, ext_map):
        assert classify("photo.png", ext_map, "Others") == "Images"

    def test_document(self, ext_map):
        assert classify("report.pdf", ext_map, "Others") == "Documents"

    def test_archive_compound(self, ext_map):
        assert classify("src.tar.gz", ext_map, "Others") == "Archives"

    def test_fallback(self, ext_map):
        assert classify("unknown.xyz", ext_map, "Others") == "Others"

    def test_case_insensitive(self, ext_map):
        assert classify("Image.JPG", ext_map, "Others") == "Images"


class TestShouldIgnore:
    def test_dot_prefix(self):
        assert should_ignore(".DS_Store", [".", "~$"]) is True

    def test_temp_prefix(self):
        assert should_ignore("~$document.docx", [".", "~$"]) is True

    def test_normal_file(self):
        assert should_ignore("report.pdf", [".", "~$"]) is False


class TestSafeMove:
    def test_basic_move(self, tmp_path):
        src = tmp_path / "hello.txt"
        src.write_text("hi")
        dest_dir = tmp_path / "Documents"
        logs = []
        result = safe_move(src, dest_dir, dry_run=False, callback=lambda l, m: logs.append((l, m)))
        assert result is True
        assert (dest_dir / "hello.txt").exists()
        assert not src.exists()
        assert any("hello.txt" in m for _, m in logs)

    def test_dry_run_does_not_move(self, tmp_path):
        src = tmp_path / "hello.txt"
        src.write_text("hi")
        dest_dir = tmp_path / "Documents"
        safe_move(src, dest_dir, dry_run=True)
        assert src.exists()
        assert not dest_dir.exists()

    def test_collision_auto_numbered(self, tmp_path):
        dest_dir = tmp_path / "Documents"
        dest_dir.mkdir()
        # Pre-existing file
        (dest_dir / "hello.txt").write_text("old")
        src = tmp_path / "hello.txt"
        src.write_text("new")
        safe_move(src, dest_dir, dry_run=False)
        assert (dest_dir / "hello (1).txt").exists()

    def test_collision_tar_gz(self, tmp_path):
        dest_dir = tmp_path / "Archives"
        dest_dir.mkdir()
        (dest_dir / "archive.tar.gz").write_text("old")
        src = tmp_path / "archive.tar.gz"
        src.write_text("new")
        safe_move(src, dest_dir, dry_run=False)
        assert (dest_dir / "archive (1).tar.gz").exists()
