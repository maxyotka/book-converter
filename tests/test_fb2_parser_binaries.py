from pathlib import Path

from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_document

FIXTURES = Path(__file__).parent / "fixtures"


def test_binaries_decoded():
    root = load_fb2(FIXTURES / "images.fb2")
    doc = parse_document(root)
    assert "img_1" in doc.binaries
    b = doc.binaries["img_1"]
    assert b.content_type == "image/png"
    assert b.data == b"hi"  # base64 "aGk=" → b"hi"
    assert b.filename == "img_1.png"


def test_cover_binary_and_meta_link():
    root = load_fb2(FIXTURES / "metadata_full.fb2")
    doc = parse_document(root)
    assert doc.meta.cover_binary_id == "cover.jpg"
    cover = doc.binaries["cover.jpg"]
    assert cover.content_type == "image/jpeg"
    assert cover.filename == "cover_jpg.jpg"  # dots in id sanitized to _
