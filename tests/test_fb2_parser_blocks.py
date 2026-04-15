from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_section, NS

FIXTURES = Path(__file__).parent / "fixtures"


def test_simple_block_sequence():
    root = load_fb2(FIXTURES / "images.fb2")
    section_el = root.find(".//f:body/f:section", NS)
    section = parse_section(section_el, level=1)
    kinds = [b.kind for b in section.blocks]
    assert kinds == ["p", "scene", "p", "subtitle", "image", "p"]
    assert section.blocks[0].inlines[0].text == "first"
    assert section.blocks[2].inlines[0].text == "after break"
    assert section.blocks[3].inlines[0].text == "Sub heading"
    assert section.blocks[4].binary_id == "img_1"
    assert section.blocks[5].inlines[0].text == "last"
