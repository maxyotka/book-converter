"""Render Document IR → Typst source."""
from __future__ import annotations

import sys
from typing import Callable

from book_converter.ir import (
    Inline,
    InlineEmphasis,
    InlineFootnoteRef,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
)
from book_converter.render.escape import typst_escape, typst_string

FootnoteResolver = Callable[[str], object]


def render_inlines(inlines: list[Inline], footnote_resolver: FootnoteResolver) -> str:
    parts: list[str] = []
    for node in inlines:
        parts.append(_render_one(node, footnote_resolver))
    return "".join(parts)


def _render_one(node: Inline, fn_resolver: FootnoteResolver) -> str:
    if isinstance(node, InlineText):
        return typst_escape(node.text)
    if isinstance(node, InlineEmphasis):
        return f"#emph[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineStrong):
        return f"#strong[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineSub):
        return f"#sub[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineSup):
        return f"#super[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineLink):
        return f"#link({typst_string(node.url)})[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineFootnoteRef):
        body = fn_resolver(node.note_id)
        if body is None:
            print(f"warning: unresolved footnote ref '{node.note_id}'", file=sys.stderr)
            return "#super[?]"
        return f"#footnote[{body}]"
    return ""
