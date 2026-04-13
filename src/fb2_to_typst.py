"""FB2 -> Typst converter for one specific book."""
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"f": "http://www.gribuser.ru/xml/fictionbook/2.0"}


def load_fb2(zip_path: Path) -> ET.Element:
    """Open .fb2.zip, find the .fb2 inside, return parsed XML root."""
    with zipfile.ZipFile(zip_path) as z:
        fb2_name = next(n for n in z.namelist() if n.lower().endswith(".fb2"))
        with z.open(fb2_name) as f:
            return ET.parse(f).getroot()


def _text(elem: ET.Element | None) -> str:
    return (elem.text or "").strip() if elem is not None else ""


def parse_metadata(root: ET.Element) -> dict:
    """Extract book metadata from FictionBook/description."""
    desc = root.find("f:description", NS)
    ti = desc.find("f:title-info", NS)
    pi = desc.find("f:publish-info", NS)

    author_el = ti.find("f:author", NS)
    author = " ".join(
        _text(author_el.find(f"f:{tag}", NS))
        for tag in ("first-name", "middle-name", "last-name")
    )
    author = " ".join(author.split())

    seq = ti.find("f:sequence", NS)
    series_name = seq.get("name") if seq is not None else ""
    series_number = int(seq.get("number")) if seq is not None and seq.get("number") else None

    annotation_el = ti.find("f:annotation", NS)
    annotation = " ".join(
        (p.text or "").strip() for p in annotation_el.findall("f:p", NS)
    ) if annotation_el is not None else ""

    return {
        "title": _text(ti.find("f:book-title", NS)),
        "author": author,
        "series_name": series_name,
        "series_number": series_number,
        "annotation": annotation,
        "publisher": _text(pi.find("f:publisher", NS)) if pi is not None else "",
        "year": _text(pi.find("f:year", NS)) if pi is not None else "",
        "isbn": _text(pi.find("f:isbn", NS)) if pi is not None else "",
    }


def parse_chapters(root: ET.Element) -> list[dict]:
    """Extract chapters from the book body.

    Each top-level <section> is one chapter. Title is in <title>/<p> —
    either ["Глава N", "Название"] for regular chapters, or ["Эпилог"] for the epilogue.
    """
    body = root.find("f:body", NS)
    chapters = []
    for section in body.findall("f:section", NS):
        title_el = section.find("f:title", NS)
        title_parts = (
            [(p.text or "").strip() for p in title_el.findall("f:p", NS)]
            if title_el is not None
            else []
        )

        if len(title_parts) >= 2 and title_parts[0].lower().startswith("глава"):
            number_label = title_parts[0]
            title = title_parts[1]
        else:
            number_label = ""
            title = " ".join(title_parts)

        paragraphs = [
            (p.text or "").strip()
            for p in section.findall("f:p", NS)
            if (p.text or "").strip()
        ]

        chapters.append(
            {
                "number_label": number_label,
                "title": title,
                "paragraphs": paragraphs,
            }
        )
    return chapters
