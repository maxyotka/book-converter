"""Russian book typography: guillemets, em-dashes, NBSP."""
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
from book_converter.typography.base import (
    SENTINEL,
    flatten,
    rebuild,
    transform_children,
)

NBSP = "\u00a0"

SHORT_WORDS = {
    "в", "на", "к", "с", "и", "а", "но", "о", "об",
    "за", "под", "над", "от", "до", "из", "у", "по", "во", "со",
    "не", "ни", "же", "ли", "бы", "то", "что", "как",
    "В", "На", "К", "С", "И", "А", "Но", "О", "Об",
    "За", "Под", "Над", "От", "До", "Из", "У", "По", "Во", "Со",
    "Не", "Ни", "Же", "Ли", "Бы", "То", "Что", "Как",
}


def _replace_quotes(text: str) -> str:
    result: list[str] = []
    open_next = True
    for ch in text:
        if ch == '"':
            result.append("«" if open_next else "»")
            open_next = not open_next
        else:
            if ch in " \t\n(":
                open_next = True
            elif open_next and ch.isalpha():
                open_next = False
            result.append(ch)
    return "".join(result)


def _apply_dashes_and_nbsp(text: str) -> str:
    text = _replace_quotes(text)
    text = text.replace(" -- ", f"{NBSP}— ")
    text = text.replace("--", "—")
    text = re.sub(r"(^|\n)—\s+", lambda m: f"{m.group(1)}—{NBSP}", text)
    text = re.sub(
        r"([,.!?])\s+—\s+",
        lambda m: f"{m.group(1)}{NBSP}—{NBSP}",
        text,
    )

    def _short_nbsp(match: re.Match) -> str:
        word = match.group(1)
        return f"{word}{NBSP}" if word in SHORT_WORDS else match.group(0)

    # Match short words followed by space and either a letter or a sentinel (structural boundary)
    text = re.sub(
        r"(?<![а-яА-ЯёЁa-zA-Z])([а-яА-ЯёЁa-zA-Z]{1,3}) (?=[а-яА-ЯёЁa-zA-Z]|"
        + re.escape(SENTINEL)
        + r")",
        _short_nbsp,
        text,
    )
    return text


class RussianTypography:
    lang_codes: tuple[str, ...] = ("ru",)

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]:
        with_nested = transform_children(inlines)
        flat, nodes = flatten(with_nested)
        transformed = _apply_dashes_and_nbsp(flat)
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
