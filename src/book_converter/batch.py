"""Batch-build all FB2 files in a directory."""
from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import ParseError

from pydantic import ValidationError

from book_converter.cli import _default_output_name, convert_single

_RECOVERABLE = (
    FileNotFoundError,
    ValueError,
    ParseError,
    ValidationError,
    zipfile.BadZipFile,
    subprocess.CalledProcessError,
    OSError,
)


def _discover_inputs(books_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for p in sorted(books_dir.rglob("*")):
        if p.is_file() and (
            p.name.lower().endswith(".fb2") or p.name.lower().endswith(".fb2.zip")
        ):
            paths.append(p)
    return paths


def build_batch(books_dir: Path, out_dir: Path) -> int:
    books_dir = Path(books_dir)
    out_dir = Path(out_dir)
    if not books_dir.exists():
        print(f"error: books directory {books_dir} not found", file=sys.stderr)
        return 2

    inputs = _discover_inputs(books_dir)
    if not inputs:
        print(f"warning: no FB2 files in {books_dir}", file=sys.stderr)
        return 0

    failures: list[tuple[Path, str]] = []
    successes: list[Path] = []

    for fb2 in inputs:
        output_name = _default_output_name(fb2)
        output_path = out_dir / output_name
        workdir = out_dir / "_work" / fb2.stem
        try:
            convert_single(
                input_path=fb2,
                output_path=output_path,
                cli_overrides={},
                workdir=workdir,
                explicit_toml=None,
            )
            successes.append(fb2)
        except _RECOVERABLE as e:
            failures.append((fb2, str(e)))
            print(f"error: {fb2.name}: {e}", file=sys.stderr)

    print(
        f"\nbuild summary: {len(successes)} ok, {len(failures)} failed",
        file=sys.stderr,
    )
    return 0 if not failures else 1
