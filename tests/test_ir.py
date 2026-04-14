from book_converter.ir import (
    BookMeta,
    Document,
    Footnote,
    InlineEmphasis,
    InlineLink,
    InlineStrong,
    InlineText,
    Paragraph,
    Section,
)


def test_inline_text_roundtrip():
    t = InlineText(text="hello")
    assert t.kind == "text"
    assert t.text == "hello"


def test_inline_emphasis_nests_inlines():
    em = InlineEmphasis(children=[InlineText(text="bold"), InlineStrong(children=[InlineText(text="deep")])])
    assert em.kind == "em"
    assert em.children[1].kind == "strong"
    assert em.children[1].children[0].text == "deep"


def test_inline_link_has_url():
    link = InlineLink(url="https://example.com", children=[InlineText(text="site")])
    assert link.url == "https://example.com"


def test_paragraph_contains_inlines():
    p = Paragraph(inlines=[InlineText(text="abc")])
    assert p.kind == "p"
    assert p.inlines[0].text == "abc"


def test_section_title_is_list_of_lines():
    s = Section(
        level=2,
        title=[[InlineText(text="Глава 1")], [InlineText(text="Name")]],
        blocks=[Paragraph(inlines=[InlineText(text="body")])],
    )
    assert len(s.title) == 2
    assert s.title[0][0].text == "Глава 1"


def test_section_blocks_allow_nested_sections():
    inner = Section(level=3, title=[[InlineText(text="sub")]], blocks=[])
    outer = Section(level=2, title=[[InlineText(text="outer")]], blocks=[inner])
    assert outer.blocks[0].kind == "section"
    assert outer.blocks[0].level == 3


def test_document_has_meta_sections_footnotes_binaries():
    meta = BookMeta(title="T", author="A", lang="ru")
    doc = Document(meta=meta, sections=[], footnotes={}, binaries={})
    assert doc.meta.title == "T"
    assert doc.footnotes == {}


def test_footnote_stores_blocks():
    fn = Footnote(id="n1", blocks=[Paragraph(inlines=[InlineText(text="note body")])])
    assert fn.id == "n1"
    assert len(fn.blocks) == 1
