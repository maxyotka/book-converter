"""Command-line entrypoint: single-shot convert and batch build."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from book_converter.config import apply_config_to_meta, load_book_config
from book_converter.fb2.loader import load_fb2
from book_converter.fb2.parser import parse_document
from book_converter.render.typst import render

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class _Parser:
    """Dispatches between single-shot convert and batch build subcommand.

    argparse cannot cleanly mix an optional top-level positional with
    subparsers, so this class sniffs the first argv element and routes to
    the matching parser.
    """

    def __init__(self) -> None:
        self.convert = argparse.ArgumentParser(prog="book-converter")
        self.convert.add_argument(
            "input", nargs="?", type=Path, help="Input FB2 file"
        )
        self.convert.add_argument("-o", "--output", type=Path)
        self.convert.add_argument("--title")
        self.convert.add_argument("--author")
        self.convert.add_argument("--lang")
        self.convert.add_argument("--publisher")
        self.convert.add_argument("--year")
        self.convert.add_argument("--isbn")
        self.convert.add_argument("--font", action="append", default=[])
        self.convert.add_argument("--config", type=Path)

        self.build = argparse.ArgumentParser(prog="book-converter build")
        self.build.add_argument(
            "books_dir", nargs="?", type=Path, default=Path("books")
        )
        self.build.add_argument("--out-dir", type=Path, default=Path("build"))

    def parse_args(self, argv: list[str] | None = None) -> argparse.Namespace:
        if argv is None:
            argv = sys.argv[1:]
        if argv and argv[0] == "build":
            ns = self.build.parse_args(argv[1:])
            ns.command = "build"
            return ns
        ns = self.convert.parse_args(argv)
        ns.command = None
        return ns


def build_parser() -> _Parser:
    return _Parser()


def _cli_overrides_from_args(args: argparse.Namespace) -> dict:
    mapping = {
        "title": args.title,
        "author": args.author,
        "lang": args.lang,
        "publisher": args.publisher,
        "year": args.year,
        "isbn": args.isbn,
    }
    if args.font:
        mapping["fonts"] = args.font
    return {k: v for k, v in mapping.items() if v is not None}


def _run_typst(typ_path: Path, pdf_path: Path, root: Path) -> None:
    result = subprocess.run(
        ["typst", "compile", "--root", str(root), str(typ_path), str(pdf_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        if result.stdout:
            sys.stderr.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode,
            ["typst", "compile", str(typ_path), str(pdf_path)],
            output=result.stdout,
            stderr=result.stderr,
        )


def convert_single(
    input_path: Path,
    output_path: Path,
    cli_overrides: dict,
    workdir: Path,
    explicit_toml: Path | None = None,
) -> int:
    if not input_path.exists():
        print(f"error: {input_path} not found", file=sys.stderr)
        return 2

    root = load_fb2(input_path)
    doc = parse_document(root)
    config = load_book_config(
        input_path, cli_overrides=cli_overrides, explicit_toml=explicit_toml
    )
    doc = doc.model_copy(update={"meta": apply_config_to_meta(doc.meta, config)})

    workdir.mkdir(parents=True, exist_ok=True)
    result = render(doc, workdir=workdir, fonts=config.fonts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _run_typst(result.typ_path, output_path, PROJECT_ROOT)
    return 0


def _default_output_name(input_path: Path) -> str:
    name = input_path.name
    for suffix in (".fb2.zip", ".fb2"):
        if name.lower().endswith(suffix):
            return name[: -len(suffix)] + ".pdf"
    return input_path.stem + ".pdf"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        from book_converter.batch import build_batch

        return build_batch(args.books_dir, args.out_dir)

    if args.input is None:
        parser.print_help()
        return 1

    input_path = args.input
    output_path = args.output or Path.cwd() / _default_output_name(input_path)
    cli_overrides = _cli_overrides_from_args(args)
    workdir = Path("build") / "_work" / input_path.stem
    return convert_single(
        input_path=input_path,
        output_path=output_path,
        cli_overrides=cli_overrides,
        workdir=workdir,
        explicit_toml=args.config,
    )


if __name__ == "__main__":
    raise SystemExit(main())
