"""Test typography base protocol and registry."""
from book_converter.ir import InlineEmphasis, InlineText
from book_converter.typography.base import PassthroughTypography
from book_converter.typography import registry


def test_passthrough_returns_inlines_unchanged():
    typo = PassthroughTypography()
    inlines = [InlineText(text="abc"), InlineEmphasis(children=[InlineText(text="def")])]
    out = typo.transform_paragraph(inlines)
    assert len(out) == 2
    assert out[0].text == "abc"
    assert out[1].kind == "em"


def test_registry_get_returns_passthrough_when_unknown():
    t = registry.get("xx")
    assert t.__class__.__name__ == "PassthroughTypography"


def test_registry_register_then_get():
    class FakeTypo:
        lang_codes = ("zz",)
        def transform_paragraph(self, inlines):
            return inlines
    registry.register(FakeTypo())
    try:
        assert registry.get("zz").__class__.__name__ == "FakeTypo"
    finally:
        registry._REGISTRY.pop("zz", None)
