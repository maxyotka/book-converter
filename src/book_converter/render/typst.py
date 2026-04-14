"""Render Document IR → Typst source."""
from __future__ import annotations

import sys
from typing import Callable

from book_converter.ir import (
    Block,
    Cite,
    Epigraph,
    Image,
    Inline,
    InlineEmphasis,
    InlineFootnoteRef,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
    Paragraph,
    Poem,
    SceneBreak,
    Subtitle,
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


def _maybe_author(author) -> str:
    if author is None:
        return "none"
    return f"[{render_inlines(author, lambda _nid: None)}]"


def render_block(
    block,
    footnote_resolver: FootnoteResolver,
    image_path: Callable[[str], str] | None = None,
) -> str:
    if image_path is None:
        image_path = lambda bid: bid

    if isinstance(block, Paragraph):
        return f"#para[{render_inlines(block.inlines, footnote_resolver)}]"
    if isinstance(block, Subtitle):
        return f"#subtitle[{render_inlines(block.inlines, footnote_resolver)}]"
    if isinstance(block, SceneBreak):
        return "#scene-break"
    if isinstance(block, Image):
        return f"#book-image({typst_string(image_path(block.binary_id))})"
    if isinstance(block, Epigraph):
        author = _maybe_author(block.author)
        body = "\n".join(render_block(b, footnote_resolver, image_path) for b in block.blocks)
        return f"#epigraph(author: {author})[\n{body}\n]"
    if isinstance(block, Cite):
        author = _maybe_author(block.author)
        body = "\n".join(render_block(b, footnote_resolver, image_path) for b in block.blocks)
        return f"#cite-block(author: {author})[\n{body}\n]"
    if isinstance(block, Poem):
        title = "none" if block.title is None else f"[{render_inlines(block.title, footnote_resolver)}]"
        author = _maybe_author(block.author)
        stanzas_src = []
        for stanza in block.stanzas:
            lines_src = [f"[{render_inlines(line, footnote_resolver)}]" for line in stanza.lines]
            stanzas_src.append("(" + ", ".join(lines_src) + ",)")
        stanzas_tuple = "(" + ", ".join(stanzas_src) + ",)"
        return f"#poem(title: {title}, author: {author}, stanzas: {stanzas_tuple})"
    raise TypeError(f"render_block does not handle {type(block).__name__}")
