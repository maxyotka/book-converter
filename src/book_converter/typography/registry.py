"""Lang-code → Typography mapping with passthrough fallback."""
from __future__ import annotations

from book_converter.typography.base import PassthroughTypography, Typography

_REGISTRY: dict[str, Typography] = {}
_PASSTHROUGH = PassthroughTypography()


def register(typo: Typography) -> None:
    for code in typo.lang_codes:
        _REGISTRY[code] = typo


def get(lang: str) -> Typography:
    return _REGISTRY.get(lang, _PASSTHROUGH)
