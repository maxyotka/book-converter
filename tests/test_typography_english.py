"""Test English typography rules."""
from book_converter.ir import InlineText
from book_converter.typography.english import EnglishTypography

NBSP = "\u00a0"


def test_smart_double_quotes():
    typo = EnglishTypography()
    out = typo.transform_paragraph([InlineText(text='He said "hi" to her.')])
    assert out[0].text == "He said \u201chi\u201d to her."


def test_double_dash_to_em_dash():
    typo = EnglishTypography()
    out = typo.transform_paragraph([InlineText(text="wait -- really?")])
    assert "—" in out[0].text


def test_ellipsis():
    typo = EnglishTypography()
    out = typo.transform_paragraph([InlineText(text="hmm... okay")])
    assert "…" in out[0].text


def test_mr_gets_nbsp():
    typo = EnglishTypography()
    out = typo.transform_paragraph([InlineText(text="Mr. Smith and Dr. Jones")])
    assert f"Mr.{NBSP}Smith" in out[0].text
    assert f"Dr.{NBSP}Jones" in out[0].text
