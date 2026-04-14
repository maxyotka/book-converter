"""Test Russian typography rules."""
from book_converter.ir import InlineEmphasis, InlineText
from book_converter.typography.russian import RussianTypography


NBSP = "\u00a0"


def test_quotes_become_yolochki():
    typo = RussianTypography()
    out = typo.transform_paragraph([InlineText(text='Он сказал "привет" ей.')])
    assert out[0].text == "Он сказал «привет» ей."


def test_double_dash_becomes_em_dash():
    typo = RussianTypography()
    out = typo.transform_paragraph([InlineText(text="так -- вот")])
    assert "—" in out[0].text
    assert "-- " not in out[0].text


def test_leading_dialogue_dash_gets_nbsp():
    typo = RussianTypography()
    out = typo.transform_paragraph([InlineText(text="— Привет,")])
    assert out[0].text.startswith(f"—{NBSP}")


def test_short_word_gets_nbsp_before_next_word():
    typo = RussianTypography()
    out = typo.transform_paragraph([InlineText(text="Он и она")])
    assert f"и{NBSP}она" in out[0].text


def test_short_word_nbsp_across_emphasis_boundary():
    typo = RussianTypography()
    inlines = [InlineText(text="Он и "), InlineEmphasis(children=[InlineText(text="она")])]
    out = typo.transform_paragraph(inlines)
    assert out[0].text == f"Он и{NBSP}"
    assert out[1].kind == "em"
    assert out[1].children[0].text == "она"
