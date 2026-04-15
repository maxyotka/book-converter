"""Document Intermediate Representation for FB2 → PDF pipeline."""
from __future__ import annotations

import re as _re
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- Inline nodes -----------------------------------------------------------

class InlineText(_Base):
    kind: Literal["text"] = "text"
    text: str


class InlineEmphasis(_Base):
    kind: Literal["em"] = "em"
    children: list["Inline"]


class InlineStrong(_Base):
    kind: Literal["strong"] = "strong"
    children: list["Inline"]


class InlineSub(_Base):
    kind: Literal["sub"] = "sub"
    children: list["Inline"]


class InlineSup(_Base):
    kind: Literal["sup"] = "sup"
    children: list["Inline"]


class InlineLink(_Base):
    kind: Literal["link"] = "link"
    url: str
    children: list["Inline"]


class InlineFootnoteRef(_Base):
    kind: Literal["fnref"] = "fnref"
    note_id: str


Inline = Annotated[
    Union[
        InlineText,
        InlineEmphasis,
        InlineStrong,
        InlineSub,
        InlineSup,
        InlineLink,
        InlineFootnoteRef,
    ],
    Field(discriminator="kind"),
]


# --- Block nodes ------------------------------------------------------------

class Paragraph(_Base):
    kind: Literal["p"] = "p"
    inlines: list[Inline]


class Subtitle(_Base):
    kind: Literal["subtitle"] = "subtitle"
    inlines: list[Inline]


class SceneBreak(_Base):
    kind: Literal["scene"] = "scene"


class Image(_Base):
    kind: Literal["image"] = "image"
    binary_id: str


class Cite(_Base):
    kind: Literal["cite"] = "cite"
    blocks: list["Block"]
    author: list[Inline] | None = None


class Epigraph(_Base):
    kind: Literal["epigraph"] = "epigraph"
    blocks: list["Block"]
    author: list[Inline] | None = None


class PoemStanza(_Base):
    lines: list[list[Inline]]


class Poem(_Base):
    kind: Literal["poem"] = "poem"
    title: list[Inline] | None = None
    stanzas: list[PoemStanza]
    author: list[Inline] | None = None


class Section(_Base):
    kind: Literal["section"] = "section"
    level: int
    title: list[list[Inline]]
    blocks: list["Block"]


Block = Annotated[
    Union[
        Paragraph,
        Subtitle,
        SceneBreak,
        Image,
        Cite,
        Epigraph,
        Poem,
        Section,
    ],
    Field(discriminator="kind"),
]


# --- Document -----------------------------------------------------------------

_MIME_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
}

_SAFE_ID = _re.compile(r"[^a-zA-Z0-9_-]+")


class Binary(_Base):
    id: str
    content_type: str
    data: bytes

    @property
    def filename(self) -> str:
        safe = _SAFE_ID.sub("_", self.id) or "binary"
        ext = _MIME_EXT.get(self.content_type.lower(), "bin")
        return f"{safe}.{ext}"


class Footnote(_Base):
    id: str
    blocks: list[Block]


class BookMeta(_Base):
    title: str
    author: str
    lang: str
    series_name: str | None = None
    series_number: int | None = None
    publisher: str = ""
    year: str = ""
    isbn: str = ""
    annotation: list[Block] = Field(default_factory=list)
    cover_binary_id: str | None = None


class Document(_Base):
    meta: BookMeta
    sections: list[Section]
    footnotes: dict[str, Footnote] = Field(default_factory=dict)
    binaries: dict[str, Binary] = Field(default_factory=dict)


# Rebuild models with forward refs
for _cls in (
    InlineEmphasis, InlineStrong, InlineSub, InlineSup, InlineLink,
    Paragraph, Subtitle, Cite, Epigraph, Poem, Section, Footnote, BookMeta, Document,
):
    _cls.model_rebuild()
