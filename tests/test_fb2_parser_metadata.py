from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_metadata

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_metadata_full_fields():
    root = load_fb2(FIXTURES / "metadata_full.fb2")
    meta = parse_metadata(root)
    assert meta.title == "Полное собрание"
    assert meta.author == "Иван Иванович Иванов"
    assert meta.lang == "ru"
    assert meta.series_name == "Собрание"
    assert meta.series_number == 2
    assert meta.publisher == "Издательство"
    assert meta.year == "2024"
    assert meta.isbn == "978-0-00-000000-0"
    assert meta.cover_binary_id == "cover.jpg"
    assert len(meta.annotation) == 1
    assert meta.annotation[0].kind == "p"


def test_parse_metadata_minimal_defaults():
    root = load_fb2(FIXTURES / "flat_minimal.fb2")
    meta = parse_metadata(root)
    assert meta.title == "Flat Minimal"
    assert meta.author == "Test Author"
    assert meta.lang == "ru"
    assert meta.series_name is None
    assert meta.series_number is None
    assert meta.publisher == ""
    assert meta.year == ""
    assert meta.isbn == ""
    assert meta.annotation == []
    assert meta.cover_binary_id is None
