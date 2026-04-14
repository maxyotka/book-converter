"""Typography plugin interface and passthrough fallback."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from book_converter.ir import Inline


@runtime_checkable
class Typography(Protocol):
    lang_codes: tuple[str, ...]

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]: ...


class PassthroughTypography:
    lang_codes: tuple[str, ...] = ()

    def transform_paragraph(self, inlines: list[Inline]) -> list[Inline]:
        return inlines
