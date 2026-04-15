"""English book typography: smart quotes, em-dashes, ellipsis, title NBSP."""
from __future__ import annotations

import re

from book_converter.ir import (
    Inline,
    InlineEmphasis,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
)
from book_converter.typography.base import flatten, rebuild, transform_children

NBSP = "\u00a0"


def _smart_double_quotes(text: str) -> str:
    result: list[str] = []
    open_next = True
    for ch in text:
        if ch == '"':
            result.append("\u201c" if open_next else "\u201d")
            open_next = not open_next
        else:
            if ch in " \t\n(":
                open_next = True
            elif open_next and ch.isalpha():
                open_next = False
            result.append(ch)
    return "".join(result)


def _smart_single_quotes(text: str) -> str:
    result: list[str] = []
    open_next = True
    for i, ch in enumerate(text):
        if ch == "'":
            prev = text[i - 1] if i > 0 else " "
            nxt = text[i + 1] if i + 1 < len(text) else " "
            if prev.isalpha() and nxt.isalpha():
                result.append("\u2019")
            else:
                result.append("\u2018" if open_next else "\u2019")
                open_next = not open_next
        else:
            if ch in " \t\n(":
                open_next = True
            result.append(ch)
    return "".join(result)


_TITLE_NBSP = re.compile(r"\b(Mr|Mrs|Ms|Dr|Prof|St)\.\s+(?=[A-Z])")


def _apply_rules(text: str) -> str:
    text = _smart_double_quotes(text)
    text = _smart_single_quotes(text)
    text = text.replace("--", "—")
    text = text.replace("...", "…")
    text = _TITLE_NBSP.sub(lambda m: f"{m.group(1)}.{NBSP}", text)
    return text


class EnglishTypography:
    lang_codes: tuple[str, ...] = ("en",)

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]:
        with_nested = transform_children(inlines)
        flat, nodes = flatten(with_nested)
        transformed = _apply_rules(flat)
        rebuilt = rebuild(transformed, nodes)
        final: list[Inline] = []
        for n in rebuilt:
            if isinstance(n, InlineText):
                final.append(n)
            elif isinstance(n, (InlineEmphasis, InlineStrong, InlineSub, InlineSup)):
                final.append(type(n)(children=self.transform_paragraph(n.children)))
            elif isinstance(n, InlineLink):
                final.append(InlineLink(url=n.url, children=self.transform_paragraph(n.children)))
            else:
                final.append(n)
        return final
