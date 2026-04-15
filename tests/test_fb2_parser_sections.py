from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_document

FIXTURES = Path(__file__).parent / "fixtures"


def test_nested_sections_levels_1_to_5():
    root = load_fb2(FIXTURES / "nested_sections.fb2")
    doc = parse_document(root)
    top = doc.sections
    assert len(top) == 1

    l1 = top[0]
    assert l1.level == 1
    assert l1.title[0][0].text == "Книга первая"
    assert l1.blocks[0].kind == "p"
    assert l1.blocks[0].inlines[0].text == "intro L1"

    l2 = l1.blocks[1]  # second block is nested section
    assert l2.kind == "section"
    assert l2.level == 2
    assert l2.title[0][0].text == "Часть I"

    l3 = l2.blocks[1]
    assert l3.level == 3
    assert len(l3.title) == 2
    assert l3.title[0][0].text == "Глава 1"
    assert l3.title[1][0].text == "Название главы"

    l4 = l3.blocks[1]
    assert l4.level == 4

    l5 = l4.blocks[1]
    assert l5.level == 5
    assert l5.blocks[0].inlines[0].text == "deepest"


def test_flat_minimal_top_level_sections():
    root = load_fb2(FIXTURES / "flat_minimal.fb2")
    doc = parse_document(root)
    assert len(doc.sections) == 2
    assert doc.sections[0].title[0][0].text == "Глава 1"
    assert doc.sections[1].title[0][0].text == "Глава 2"
    assert all(s.level == 1 for s in doc.sections)
