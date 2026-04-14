from book_converter.ir import (
    Cite,
    Epigraph,
    Image,
    InlineText,
    Paragraph,
    Poem,
    PoemStanza,
    SceneBreak,
    Subtitle,
)
from book_converter.render.typst import render_block


def _no_fn(nid):
    return None


def test_paragraph_becomes_para_call():
    out = render_block(Paragraph(inlines=[InlineText(text="hi")]), _no_fn)
    assert out == "#para[hi]"


def test_scene_break():
    assert render_block(SceneBreak(), _no_fn) == "#scene-break"


def test_subtitle():
    out = render_block(Subtitle(inlines=[InlineText(text="Sub")]), _no_fn)
    assert out == "#subtitle[Sub]"


def test_image():
    out = render_block(Image(binary_id="img_1"), _no_fn)
    assert "#book-image[" in out
    assert "#image(" in out
    assert "img_1" in out


def test_epigraph_with_author():
    ep = Epigraph(
        blocks=[Paragraph(inlines=[InlineText(text="wise words")])],
        author=[InlineText(text="Someone")],
    )
    out = render_block(ep, _no_fn)
    assert out.startswith("#epigraph(")
    assert "Someone" in out
    assert "wise words" in out


def test_cite_without_author():
    c = Cite(blocks=[Paragraph(inlines=[InlineText(text="quoted")])], author=None)
    out = render_block(c, _no_fn)
    assert out.startswith("#cite-block(")
    assert "author: none" in out
    assert "quoted" in out


def test_poem_stanzas():
    p = Poem(
        title=[InlineText(text="Title")],
        stanzas=[
            PoemStanza(lines=[[InlineText(text="Line 1")], [InlineText(text="Line 2")]]),
            PoemStanza(lines=[[InlineText(text="Line 3")]]),
        ],
        author=[InlineText(text="Poet")],
    )
    out = render_block(p, _no_fn)
    assert "#poem(" in out
    assert "Line 1" in out
    assert "Line 3" in out
    assert "Poet" in out
