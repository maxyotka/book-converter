"""FB2 -> Typst converter for one specific book."""
import base64
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"f": "http://www.gribuser.ru/xml/fictionbook/2.0"}

NBSP = "\u00a0"
SHORT_WORDS = {
    "в", "на", "к", "с", "и", "а", "но", "о", "об",
    "за", "под", "над", "от", "до", "из", "у", "по", "во", "со",
    "не", "ни", "же", "ли", "бы", "то", "что", "как",
    "В", "На", "К", "С", "И", "А", "Но", "О", "Об",
    "За", "Под", "Над", "От", "До", "Из", "У", "По", "Во", "Со",
    "Не", "Ни", "Же", "Ли", "Бы", "То", "Что", "Как",
}


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


def _replace_quotes(text: str) -> str:
    """Turn straight double quotes into «ёлочки»."""
    result = []
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


def apply_russian_typography(text: str) -> str:
    """Apply Russian book typography: quotes, em dashes, non-breaking spaces."""
    text = _replace_quotes(text)

    text = text.replace(" -- ", f"{NBSP}— ")
    text = text.replace("--", "—")

    text = re.sub(r"(^|\n)—\s+", lambda m: f"{m.group(1)}—{NBSP}", text)
    text = re.sub(
        r"([,.!?])\s+—\s+",
        lambda m: f"{m.group(1)}{NBSP}—{NBSP}",
        text,
    )

    def _short_word_nbsp(match: re.Match) -> str:
        word = match.group(1)
        return f"{word}{NBSP}" if word in SHORT_WORDS else match.group(0)

    text = re.sub(
        r"(?<![а-яА-ЯёЁa-zA-Z])([а-яА-ЯёЁa-zA-Z]{1,3}) (?=[а-яА-ЯёЁa-zA-Z])",
        _short_word_nbsp,
        text,
    )

    return text


def extract_cover(root: ET.Element, out_path: Path) -> None:
    """Decode <binary id="cover.jpg"> and write JPEG to out_path."""
    for binary in root.findall("f:binary", NS):
        if binary.get("id") == "cover.jpg":
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(base64.b64decode(binary.text or ""))
            return
    raise ValueError("cover.jpg not found in FB2 binaries")
