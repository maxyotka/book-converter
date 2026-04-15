"""Typography plugin interface, passthrough fallback, and shared utils."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from book_converter.ir import (
    Inline,
    InlineEmphasis,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
)

SENTINEL = "\ue000"
"""Private-use char used to mark non-text inline nodes during text-level transforms."""


@runtime_checkable
class Typography(Protocol):
    lang_codes: tuple[str, ...]

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]: ...


class PassthroughTypography:
    lang_codes: tuple[str, ...] = ()

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]:
        return inlines


def flatten(inlines: list[Inline]) -> tuple[str, list[Inline]]:
    """Flatten inlines to a string, replacing non-text nodes with SENTINEL."""
    parts: list[str] = []
    nodes: list[Inline] = []
    for node in inlines:
        if isinstance(node, InlineText):
            parts.append(node.text)
        else:
            parts.append(SENTINEL)
            nodes.append(node)
    return "".join(parts), nodes


def rebuild(flat: str, nodes: list[Inline]) -> list[Inline]:
    """Inverse of flatten: splice SENTINEL-separated text back with non-text nodes."""
    out: list[Inline] = []
    idx = 0
    parts = flat.split(SENTINEL)
    for i, part in enumerate(parts):
        if part:
            out.append(InlineText(text=part))
        if i < len(parts) - 1:
            out.append(nodes[idx])
            idx += 1
    return out


def transform_children(inlines: list[Inline]) -> list[Inline]:
    """Recursively copy inline tree, leaving InlineText intact (identity on leaves)."""
    out: list[Inline] = []
    for n in inlines:
        if isinstance(n, InlineText):
            out.append(n)
        elif isinstance(n, InlineLink):
            out.append(InlineLink(url=n.url, children=transform_children(n.children)))
        elif isinstance(n, (InlineEmphasis, InlineStrong, InlineSub, InlineSup)):
            out.append(type(n)(children=transform_children(n.children)))
        else:
            out.append(n)
    return out
