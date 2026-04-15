from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_section, NS

FIXTURES = Path(__file__).parent / "fixtures"


def test_epigraph_with_author():
    root = load_fb2(FIXTURES / "epigraph_cite_poem.fb2")
    section_el = root.find(".//f:body/f:section", NS)
    section = parse_section(section_el, level=1)
    epigraphs = [b for b in section.blocks if b.kind == "epigraph"]
    assert len(epigraphs) == 1
    ep = epigraphs[0]
    assert len(ep.blocks) == 2
    assert ep.blocks[0].inlines[0].text == "Эпиграф строка один."
    assert ep.author is not None
    assert ep.author[0].text == "Автор эпиграфа"


def test_cite_with_author():
    root = load_fb2(FIXTURES / "epigraph_cite_poem.fb2")
    section_el = root.find(".//f:body/f:section", NS)
    section = parse_section(section_el, level=1)
    cites = [b for b in section.blocks if b.kind == "cite"]
    assert len(cites) == 1
    c = cites[0]
    assert c.blocks[0].inlines[0].text == "Цитата."
    assert c.author[0].text == "Цитата автор"


def test_poem_structure():
    root = load_fb2(FIXTURES / "epigraph_cite_poem.fb2")
    section_el = root.find(".//f:body/f:section", NS)
    section = parse_section(section_el, level=1)
    poems = [b for b in section.blocks if b.kind == "poem"]
    assert len(poems) == 1
    p = poems[0]
    assert p.title[0].text == "Стихи"
    assert len(p.stanzas) == 2
    assert len(p.stanzas[0].lines) == 2
    assert p.stanzas[0].lines[0][0].text == "Строка первая"
    assert p.stanzas[1].lines[0][0].text == "Вторая строфа"
    assert p.author[0].text == "Поэт"
