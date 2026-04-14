from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import _parse_inlines, NS

FIXTURES = Path(__file__).parent / "fixtures"


def _first_paragraph_children(fixture: str, index: int):
    root = load_fb2(FIXTURES / fixture)
    ps = root.findall(".//f:body/f:section/f:p", NS)
    return _parse_inlines(ps[index])


def test_plain_text_run():
    inlines = _first_paragraph_children("inline_formatting.fb2", 0)
    kinds = [i.kind for i in inlines]
    assert kinds == ["text", "em", "text", "strong", "text"]
    assert inlines[0].text == "plain "
    assert inlines[1].children[0].text == "em"
    assert inlines[2].text == " mid "
    assert inlines[3].children[0].text == "str"
    assert inlines[4].text == " end"


def test_nested_emphasis_strong():
    inlines = _first_paragraph_children("inline_formatting.fb2", 1)
    assert inlines[1].kind == "em"
    em = inlines[1]
    assert em.children[0].kind == "text"
    assert em.children[0].text == "out "
    assert em.children[1].kind == "strong"
    assert em.children[1].children[0].text == "in"
    assert em.children[2].text == " back"


def test_sub_sup():
    inlines = _first_paragraph_children("inline_formatting.fb2", 2)
    assert inlines[0].text == "x"
    assert inlines[1].kind == "sub"
    assert inlines[1].children[0].text == "1"
    assert inlines[2].text == "y"
    assert inlines[3].kind == "sup"
    assert inlines[3].children[0].text == "2"
    assert inlines[4].text == "z"


def test_external_link():
    inlines = _first_paragraph_children("inline_formatting.fb2", 3)
    link = next(i for i in inlines if i.kind == "link")
    assert link.url == "https://example.com"
    assert link.children[0].text == "site"


def test_footnote_ref():
    inlines = _first_paragraph_children("inline_formatting.fb2", 4)
    fn = next(i for i in inlines if i.kind == "fnref")
    assert fn.note_id == "n1"


def test_crossref_degrades_to_text():
    inlines = _first_paragraph_children("inline_formatting.fb2", 5)
    kinds = [i.kind for i in inlines]
    assert "link" not in kinds
    assert "fnref" not in kinds
    assert any("text" in i.text for i in inlines if i.kind == "text")
