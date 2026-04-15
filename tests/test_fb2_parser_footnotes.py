from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_document

FIXTURES = Path(__file__).parent / "fixtures"


def test_footnotes_parsed_from_notes_body():
    root = load_fb2(FIXTURES / "footnotes.fb2")
    doc = parse_document(root)
    assert set(doc.footnotes.keys()) == {"n1", "n2"}
    n1 = doc.footnotes["n1"]
    assert n1.blocks[0].inlines[0].text == "First footnote body."
    assert doc.footnotes["n2"].blocks[0].inlines[0].text == "Second footnote body."


def test_footnote_refs_in_paragraph_are_preserved():
    root = load_fb2(FIXTURES / "footnotes.fb2")
    doc = parse_document(root)
    p = doc.sections[0].blocks[0]
    refs = [i for i in p.inlines if i.kind == "fnref"]
    assert [r.note_id for r in refs] == ["n1", "n2"]
