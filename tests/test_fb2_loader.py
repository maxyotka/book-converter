from pathlib import Path
import zipfile

import pytest

from book_converter.fb2.loader import load_fb2

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_fb2_plain(tmp_path):
    root = load_fb2(FIXTURES / "flat_minimal.fb2")
    assert root.tag.endswith("FictionBook")


def test_load_fb2_from_zip(tmp_path):
    src = FIXTURES / "flat_minimal.fb2"
    zip_path = tmp_path / "book.fb2.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(src, arcname="flat_minimal.fb2")
    root = load_fb2(zip_path)
    assert root.tag.endswith("FictionBook")


def test_load_fb2_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_fb2(tmp_path / "nope.fb2")


def test_load_fb2_zip_without_fb2_raises(tmp_path):
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("readme.txt", "no fb2 here")
    with pytest.raises(ValueError, match="no .fb2 entry"):
        load_fb2(zip_path)
