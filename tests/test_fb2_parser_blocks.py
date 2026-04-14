from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_section_blocks, NS

FIXTURES = Path(__file__).parent / "fixtures"


def test_simple_block_sequence():
    root = load_fb2(FIXTURES / "images.fb2")
    section = root.find(".//f:body/f:section", NS)
    blocks = parse_section_blocks(section)
    kinds = [b.kind for b in blocks]
    assert kinds == ["p", "scene", "p", "subtitle", "image", "p"]
    assert blocks[0].inlines[0].text == "first"
    assert blocks[2].inlines[0].text == "after break"
    assert blocks[3].inlines[0].text == "Sub heading"
    assert blocks[4].binary_id == "img_1"
    assert blocks[5].inlines[0].text == "last"
