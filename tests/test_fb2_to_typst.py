from pathlib import Path

from src.fb2_to_typst import load_fb2, parse_chapters, parse_metadata

FB2_ZIP = Path(__file__).parent.parent / "Sotnikov_Venya-Puhov_3_Rusalka-Poisk.PM79RA.456797.fb2.zip"


def test_load_fb2_returns_element_tree():
    root = load_fb2(FB2_ZIP)
    assert root.tag.endswith("FictionBook")


def test_parse_metadata_extracts_core_fields():
    root = load_fb2(FB2_ZIP)
    meta = parse_metadata(root)
    assert meta["title"] == "Русалка. Поиск"
    assert "Владимир" in meta["author"]
    assert "Сотников" in meta["author"]
    assert meta["series_name"] == "Веня Пухов"
    assert meta["series_number"] == 3
    assert meta["publisher"] == "Эксмо"
    assert meta["year"] == "2008"
    assert meta["isbn"] == "978-5-699-28243-2"
    assert "русалки" in meta["annotation"].lower()


def test_parse_chapters_returns_21_items():
    root = load_fb2(FB2_ZIP)
    chapters = parse_chapters(root)
    assert len(chapters) == 21


def test_first_chapter_structure():
    root = load_fb2(FB2_ZIP)
    ch = parse_chapters(root)[0]
    assert ch["number_label"] == "Глава 1"
    assert ch["title"]
    assert len(ch["paragraphs"]) > 5


def test_last_chapter_is_epilogue():
    root = load_fb2(FB2_ZIP)
    ch = parse_chapters(root)[-1]
    assert ch["number_label"] == ""
    assert ch["title"] == "ЭПИЛОГ"
