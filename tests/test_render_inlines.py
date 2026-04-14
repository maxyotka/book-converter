from book_converter.ir import (
    InlineEmphasis,
    InlineFootnoteRef,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
)
from book_converter.render.typst import render_inlines


def _footnote_resolver(note_id):
    return None


def test_plain_text_escaped():
    out = render_inlines([InlineText(text="hello [world]")], _footnote_resolver)
    assert out == "hello \\[world\\]"


def test_emphasis_and_strong():
    inlines = [
        InlineText(text="a "),
        InlineEmphasis(children=[InlineText(text="b")]),
        InlineText(text=" c "),
        InlineStrong(children=[InlineText(text="d")]),
    ]
    out = render_inlines(inlines, _footnote_resolver)
    assert out == "a #emph[b] c #strong[d]"


def test_sub_and_sup():
    inlines = [
        InlineText(text="H"),
        InlineSub(children=[InlineText(text="2")]),
        InlineText(text="O x"),
        InlineSup(children=[InlineText(text="2")]),
    ]
    out = render_inlines(inlines, _footnote_resolver)
    assert out == "H#sub[2]O x#super[2]"


def test_link_rendered():
    inlines = [InlineLink(url="https://a.b", children=[InlineText(text="site")])]
    out = render_inlines(inlines, _footnote_resolver)
    assert out == '#link("https://a.b")[site]'


def test_unresolved_footnote_ref_renders_placeholder(capsys):
    inlines = [InlineText(text="x"), InlineFootnoteRef(note_id="missing")]
    out = render_inlines(inlines, lambda nid: None)
    assert out == "x#super[?]"
    err = capsys.readouterr().err
    assert "missing" in err
