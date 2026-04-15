"""Slow smoke: a synthetic Document compiles via the classic.typ template.

Covers title page, copyright, annotation, TOC, chapter with dropcap, image,
epigraph, cite, poem, subsection, and localized strings for ru and en.
Runs without any external FB2 files so the test survives books/ removal.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

from book_converter.cli import PROJECT_ROOT
from book_converter.ir import (
    Binary,
    BookMeta,
    Cite,
    Document,
    Epigraph,
    Image,
    InlineText,
    Paragraph,
    Poem,
    PoemStanza,
    SceneBreak,
    Section,
    Subtitle,
)
from book_converter.render.typst import render

# Valid 1x1 RGB PNG
_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
    "de0000000c49444154789c63f8ffff3f0005fe02fe0def46b80000000049454e"
    "44ae426082"
)


def _long_text(prefix: str) -> str:
    return prefix + "текст " * 50


def _synthetic_doc(lang: str, *, with_series: bool, with_number: bool) -> Document:
    meta = BookMeta(
        title="Пример книги" if lang == "ru" else "Sample Book",
        author="Автор Авторов" if lang == "ru" else "Jane Doe",
        lang=lang,
        series_name=("Мир" if lang == "ru" else "World") if with_series else None,
        series_number=3 if (with_series and with_number) else None,
        publisher="Изд" if lang == "ru" else "Publisher",
        year="2025",
        isbn="000-0-00-000000-0",
        annotation=[Paragraph(inlines=[InlineText(text="Короткая аннотация.")])],
        cover_binary_id="cover",
    )
    sections = [
        Section(
            level=1,
            title=[[InlineText(text="Часть первая" if lang == "ru" else "Part One")]],
            blocks=[
                Section(
                    level=2,
                    title=[
                        [InlineText(text="Глава 1" if lang == "ru" else "Chapter 1")],
                        [InlineText(text="Начало" if lang == "ru" else "The Beginning")],
                    ],
                    blocks=[
                        Epigraph(
                            blocks=[
                                Paragraph(
                                    inlines=[
                                        InlineText(text="Мудрая мысль в эпиграфе.")
                                    ]
                                )
                            ],
                            author=[InlineText(text="Мудрец")],
                        ),
                        Paragraph(
                            inlines=[InlineText(text=_long_text("К"))]
                        ),
                        Subtitle(inlines=[InlineText(text="Подзаголовок")]),
                        Paragraph(inlines=[InlineText(text="Второй абзац.")]),
                        SceneBreak(),
                        Cite(
                            blocks=[
                                Paragraph(
                                    inlines=[InlineText(text="Цитата внутри главы.")]
                                )
                            ],
                            author=None,
                        ),
                        Image(binary_id="fig1"),
                        Poem(
                            title=[InlineText(text="Песнь")],
                            stanzas=[
                                PoemStanza(
                                    lines=[
                                        [InlineText(text="Первая строка")],
                                        [InlineText(text="Вторая строка")],
                                    ]
                                )
                            ],
                            author=[InlineText(text="Поэт")],
                        ),
                        Section(
                            level=3,
                            title=[[InlineText(text="Подраздел")]],
                            blocks=[
                                Paragraph(
                                    inlines=[InlineText(text="Текст подраздела.")]
                                )
                            ],
                        ),
                    ],
                )
            ],
        )
    ]
    return Document(
        meta=meta,
        sections=sections,
        footnotes={},
        binaries={
            "cover": Binary(id="cover", content_type="image/png", data=_PNG),
            "fig1": Binary(id="fig1", content_type="image/png", data=_PNG),
        },
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "lang,with_series,with_number",
    [
        ("ru", True, True),
        ("ru", True, False),
        ("en", True, True),
        ("en", False, False),
    ],
)
def test_template_compiles(tmp_path_factory, lang, with_series, with_number):
    if shutil.which("typst") is None:
        pytest.skip("typst CLI not available")
    name = f"{lang}_{int(with_series)}{int(with_number)}"
    sandbox = PROJECT_ROOT / "build" / "_template_smoke" / name
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True)

    doc = _synthetic_doc(lang, with_series=with_series, with_number=with_number)
    result = render(doc, workdir=sandbox / "work", fonts=["PT Serif", "Times New Roman"])

    out_pdf = sandbox / "out.pdf"
    proc = subprocess.run(
        [
            "typst",
            "compile",
            "--root",
            str(PROJECT_ROOT),
            str(result.typ_path),
            str(out_pdf),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert out_pdf.exists() and out_pdf.stat().st_size > 1000
