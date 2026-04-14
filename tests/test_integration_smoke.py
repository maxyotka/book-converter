"""Fast smoke: both real books parse and render to .typ without error.

Slow mode (pytest -m slow) also compiles PDFs via typst CLI.
"""
import shutil
from pathlib import Path

import pytest

from book_converter.cli import PROJECT_ROOT, convert_single
from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_document
from book_converter.render.typst import render

BOOKS = PROJECT_ROOT / "books"
RUSALKA = BOOKS / "Sotnikov_Venya-Puhov_3_Rusalka-Poisk.PM79RA.456797.fb2.zip"
SMITH = BOOKS / "Smit_Issledovanie-o-prirode-i-prichinah-bogatstva-narodov.i8EvSQ.480216.fb2.zip"


@pytest.mark.parametrize("fb2", [RUSALKA, SMITH])
def test_parse_and_render_to_typ(tmp_path, fb2):
    root = load_fb2(fb2)
    doc = parse_document(root)
    assert doc.meta.title
    assert len(doc.sections) > 0
    result = render(doc, workdir=tmp_path, fonts=["PT Serif", "Times New Roman"])
    content = result.typ_path.read_text(encoding="utf-8")
    assert content.startswith('#import "/templates/classic.typ": *')
    assert "#chapter(" in content or "#part(" in content
    assert len(content) > 1000


@pytest.mark.slow
@pytest.mark.parametrize("fb2", [RUSALKA, SMITH])
def test_full_pdf_compile(fb2):
    if shutil.which("typst") is None:
        pytest.skip("typst CLI not available")
    # workdir must live inside PROJECT_ROOT so typst --root can resolve
    # the absolute /templates/classic.typ import.
    sandbox = PROJECT_ROOT / "build" / "_test_smoke" / fb2.stem
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True)
    out_pdf = sandbox / "out.pdf"
    convert_single(
        input_path=fb2,
        output_path=out_pdf,
        cli_overrides={},
        workdir=sandbox / "work",
    )
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 10_000
