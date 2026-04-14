"""FB2 ElementTree → Document IR."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from book_converter.ir import (
    BookMeta,
    InlineText,
    Paragraph,
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
