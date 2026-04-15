from book_converter.ir import (
    Footnote,
    InlineFootnoteRef,
    InlineText,
    Paragraph,
)
from book_converter.render.typst import make_footnote_resolver


def test_resolver_returns_escaped_body():
    footnotes = {
        "n1": Footnote(id="n1", blocks=[Paragraph(inlines=[InlineText(text="hello")])])
    }
    resolver = make_footnote_resolver(footnotes)
    body = resolver("n1")
    assert body == "hello"


def test_resolver_flattens_nested_fnref(capsys):
    footnotes = {
        "n1": Footnote(
            id="n1",
            blocks=[Paragraph(inlines=[InlineText(text="see "), InlineFootnoteRef(note_id="n2")])],
        ),
        "n2": Footnote(id="n2", blocks=[Paragraph(inlines=[InlineText(text="target")])]),
    }
    resolver = make_footnote_resolver(footnotes)
    body = resolver("n1")
    assert "see" in body
    assert "target" not in body
    err = capsys.readouterr().err
    assert "nested footnote" in err.lower()


def test_resolver_returns_none_for_missing():
    resolver = make_footnote_resolver({})
    assert resolver("missing") is None
