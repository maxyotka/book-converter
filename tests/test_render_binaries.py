from pathlib import Path

from book_converter.ir import (
    Binary,
    BookMeta,
    Document,
    InlineText,
    Paragraph,
    Section,
)
from book_converter.render.typst import render


def _make_doc():
    meta = BookMeta(
        title="T",
        author="A",
        lang="ru",
        cover_binary_id="cover_id",
    )
    return Document(
        meta=meta,
        sections=[
            Section(
                level=2,
                title=[[InlineText(text="Глава 1")]],
                blocks=[Paragraph(inlines=[InlineText(text="короткий")])],
            )
        ],
        footnotes={},
        binaries={
            "cover_id": Binary(id="cover_id", content_type="image/jpeg", data=b"fake"),
            "img_1": Binary(id="img_1", content_type="image/png", data=b"fake"),
        },
    )


def test_render_writes_typ_and_assets(tmp_path):
    doc = _make_doc()
    result = render(doc, workdir=tmp_path, fonts=["PT Serif", "Times New Roman"])
    typ_path = result.typ_path
    assert typ_path.exists()
    assert typ_path.name.endswith(".typ")

    assets = tmp_path / "assets"
    assert (assets / "cover_id.jpg").read_bytes() == b"fake"
    assert (assets / "img_1.png").read_bytes() == b"fake"


def test_render_typ_content_has_book_header(tmp_path):
    doc = _make_doc()
    result = render(doc, workdir=tmp_path, fonts=["PT Serif"])
    src = result.typ_path.read_text(encoding="utf-8")
    assert '#import "/templates/classic.typ": *' in src
    assert "#show: book.with(" in src
    assert '"T"' in src
    assert 'lang: "ru"' in src
    assert 'cover_id.jpg' in src
    assert "#chapter(" in src
