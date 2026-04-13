from pathlib import Path

from src.fb2_to_typst import (
    apply_russian_typography,
    extract_cover,
    load_fb2,
    parse_chapters,
    parse_metadata,
    render_typst,
)

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


def test_extract_cover_writes_jpeg(tmp_path):
    root = load_fb2(FB2_ZIP)
    out = tmp_path / "cover.jpg"
    extract_cover(root, out)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert out.read_bytes()[:3] == b"\xff\xd8\xff"


def test_typography_straight_quotes_become_guillemets():
    assert apply_russian_typography('Он сказал "привет" ей.') == 'Он сказал «привет» ей.'


def test_typography_double_hyphen_becomes_em_dash():
    result = apply_russian_typography("слово -- слово")
    assert "—" in result


def test_typography_dash_at_line_start_gets_nbsp():
    result = apply_russian_typography("— Как тебя зовут?")
    assert result.startswith("—\u00a0Как")


def test_typography_short_word_nbsp():
    result = apply_russian_typography("Он пошёл в лес и на реку.")
    assert "в\u00a0лес" in result
    assert "на\u00a0реку" in result


def test_typography_idempotent():
    once = apply_russian_typography("Он сказал в лес.")
    twice = apply_russian_typography(once)
    assert once == twice


def test_render_typst_produces_valid_content():
    root = load_fb2(FB2_ZIP)
    output = render_typst(root, cover_path="cover.jpg")
    assert '#import "../src/template.typ"' in output
    assert "Русалка. Поиск" in output
    assert "Сотников" in output
    assert "cover.jpg" in output
    assert output.count("#chapter(") == 21


def test_first_paragraph_uses_dropcap():
    root = load_fb2(FB2_ZIP)
    output = render_typst(root, cover_path="cover.jpg")
    assert "#dropcap(" in output
