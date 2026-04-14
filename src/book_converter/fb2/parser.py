"""FB2 ElementTree → Document IR."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from book_converter.ir import (
    Block,
    BookMeta,
    Cite,
    Document,
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
    PoemStanza,
    SceneBreak,
    Section,
    Subtitle,
)

NS = {
    "f": "http://www.gribuser.ru/xml/fictionbook/2.0",
    "l": "http://www.w3.org/1999/xlink",
}
L_HREF = f"{{{NS['l']}}}href"


def _text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return (elem.text or "").strip()


def parse_metadata(root: ET.Element) -> BookMeta:
    desc = root.find("f:description", NS)
    if desc is None:
        raise ValueError("FictionBook has no <description>")
    ti = desc.find("f:title-info", NS)
    if ti is None:
        raise ValueError("<description> has no <title-info>")

    author_el = ti.find("f:author", NS)
    author = ""
    if author_el is not None:
        author = " ".join(
            part for part in (
                _text(author_el.find(f"f:{tag}", NS))
                for tag in ("first-name", "middle-name", "last-name")
            ) if part
        )

    seq = ti.find("f:sequence", NS)
    series_name = seq.get("name") if seq is not None else None
    series_number = None
    if seq is not None and seq.get("number"):
        try:
            series_number = int(seq.get("number"))
        except ValueError:
            series_number = None

    lang_el = ti.find("f:lang", NS)
    lang = _text(lang_el) or "ru"

    annotation_blocks: list = []
    ann_el = ti.find("f:annotation", NS)
    if ann_el is not None:
        for p in ann_el.findall("f:p", NS):
            text = (p.text or "").strip()
            if text:
                annotation_blocks.append(Paragraph(inlines=[InlineText(text=text)]))

    cover_id: str | None = None
    cover_el = ti.find("f:coverpage/f:image", NS)
    if cover_el is not None:
        href = cover_el.get(L_HREF, "")
        if href.startswith("#"):
            cover_id = href[1:]

    pi = desc.find("f:publish-info", NS)
    publisher = year = isbn = ""
    if pi is not None:
        publisher = _text(pi.find("f:publisher", NS))
        year = _text(pi.find("f:year", NS))
        isbn = _text(pi.find("f:isbn", NS))

    return BookMeta(
        title=_text(ti.find("f:book-title", NS)),
        author=author,
        lang=lang,
        series_name=series_name,
        series_number=series_number,
        publisher=publisher,
        year=year,
        isbn=isbn,
        annotation=annotation_blocks,
        cover_binary_id=cover_id,
    )


_INLINE_TAGS = {
    "emphasis": ("em", InlineEmphasis),
    "strong": ("strong", InlineStrong),
    "sub": ("sub", InlineSub),
    "sup": ("sup", InlineSup),
}


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _parse_inlines(elem: ET.Element) -> list[Inline]:
    out: list[Inline] = []

    def _push_text(text: str | None) -> None:
        if not text:
            return
        if out and out[-1].kind == "text":
            out[-1] = InlineText(text=out[-1].text + text)
        else:
            out.append(InlineText(text=text))

    _push_text(elem.text)
    for child in elem:
        local = _local(child.tag)
        if local in _INLINE_TAGS:
            _kind, cls = _INLINE_TAGS[local]
            out.append(cls(children=_parse_inlines(child)))
        elif local == "a":
            href = child.get(L_HREF, "")
            a_type = child.get("type", "")
            if href.startswith(("http://", "https://", "mailto:")):
                out.append(InlineLink(url=href, children=_parse_inlines(child)))
            elif a_type == "note" and href.startswith("#"):
                out.append(InlineFootnoteRef(note_id=href[1:]))
            else:
                out.extend(_parse_inlines(child))
        else:
            out.extend(_parse_inlines(child))
        _push_text(child.tail)
    return out


def _parse_title_lines(title_el: ET.Element | None) -> list[list[Inline]]:
    if title_el is None:
        return []
    lines: list[list[Inline]] = []
    for p in title_el.findall("f:p", NS):
        lines.append(_parse_inlines(p))
    return lines


def _parse_text_author(parent: ET.Element) -> list[Inline] | None:
    ta = parent.find("f:text-author", NS)
    if ta is None:
        return None
    return _parse_inlines(ta)


def _parse_nested_blocks(parent: ET.Element) -> list[Block]:
    """Parse child <p>/<empty-line>/<subtitle> of a container like <epigraph>/<cite>."""
    blocks: list[Block] = []
    for child in parent:
        local = _local(child.tag)
        if local == "p":
            blocks.append(Paragraph(inlines=_parse_inlines(child)))
        elif local == "empty-line":
            blocks.append(SceneBreak())
        elif local == "subtitle":
            blocks.append(Subtitle(inlines=_parse_inlines(child)))
    return blocks


def _parse_poem(elem: ET.Element) -> Poem:
    title_el = elem.find("f:title", NS)
    title_inlines: list[Inline] | None = None
    if title_el is not None:
        p = title_el.find("f:p", NS)
        title_inlines = _parse_inlines(p) if p is not None else _parse_inlines(title_el)
    stanzas: list[PoemStanza] = []
    for st in elem.findall("f:stanza", NS):
        lines = [_parse_inlines(v) for v in st.findall("f:v", NS)]
        stanzas.append(PoemStanza(lines=lines))
    return Poem(title=title_inlines, stanzas=stanzas, author=_parse_text_author(elem))


def parse_section(section: ET.Element, level: int) -> Section:
    title_lines = _parse_title_lines(section.find("f:title", NS))
    blocks: list[Block] = []
    for child in section:
        local = _local(child.tag)
        if local == "title":
            continue
        if local == "p":
            blocks.append(Paragraph(inlines=_parse_inlines(child)))
        elif local == "empty-line":
            blocks.append(SceneBreak())
        elif local == "subtitle":
            p = child.find("f:p", NS)
            src = p if p is not None else child
            blocks.append(Subtitle(inlines=_parse_inlines(src)))
        elif local == "image":
            href = child.get(L_HREF, "")
            if href.startswith("#"):
                blocks.append(Image(binary_id=href[1:]))
        elif local == "epigraph":
            blocks.append(Epigraph(
                blocks=_parse_nested_blocks(child),
                author=_parse_text_author(child),
            ))
        elif local == "cite":
            blocks.append(Cite(
                blocks=_parse_nested_blocks(child),
                author=_parse_text_author(child),
            ))
        elif local == "poem":
            blocks.append(_parse_poem(child))
        elif local == "section":
            blocks.append(parse_section(child, level=level + 1))
    return Section(level=level, title=title_lines, blocks=blocks)


def parse_document(root: ET.Element) -> Document:
    meta = parse_metadata(root)
    sections: list[Section] = []
    for body in root.findall("f:body", NS):
        if body.get("name"):
            continue  # handled in task 9 (notes)
        for sec in body.findall("f:section", NS):
            sections.append(parse_section(sec, level=1))
    return Document(meta=meta, sections=sections, footnotes={}, binaries={})
