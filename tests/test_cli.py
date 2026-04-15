from pathlib import Path

import pytest

from book_converter.cli import build_parser, convert_single


FIXTURES = Path(__file__).parent / "fixtures"


def test_parser_single_shot_minimal():
    parser = build_parser()
    args = parser.parse_args(["input.fb2.zip"])
    assert args.command is None
    assert str(args.input) == "input.fb2.zip"


def test_parser_single_shot_options():
    parser = build_parser()
    args = parser.parse_args([
        "input.fb2", "-o", "out.pdf",
        "--title", "Override", "--author", "A",
        "--lang", "en", "--font", "F1", "--font", "F2",
    ])
    assert args.title == "Override"
    assert args.lang == "en"
    assert args.font == ["F1", "F2"]
    assert str(args.output) == "out.pdf"


def test_parser_batch():
    parser = build_parser()
    args = parser.parse_args(["build", "books", "--out-dir", "out"])
    assert args.command == "build"
    assert str(args.books_dir) == "books"
    assert str(args.out_dir) == "out"


def test_convert_single_writes_typ_stops_before_compile(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "book_converter.cli._run_typst",
        lambda typ, pdf, root: pdf.write_bytes(b"%PDF-fake"),
    )
    input_fb2 = FIXTURES / "flat_minimal.fb2"
    out_pdf = tmp_path / "out.pdf"
    exit_code = convert_single(
        input_path=input_fb2,
        output_path=out_pdf,
        cli_overrides={},
        workdir=tmp_path / "work",
    )
    assert exit_code == 0
    assert out_pdf.exists()
    assert (tmp_path / "work" / "book.typ").exists()
