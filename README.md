# Book Converter

Universal FB2 → beautiful PDF converter with Russian/English book typography.

## Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- [Typst](https://typst.app/) CLI (>= 0.12)
- Fonts in `templates/fonts/` (PT Serif bundled under OFL)

## Quick start

```bash
uv sync
./build.sh          # builds all books in books/ to build/
```

Or convert one book:

```bash
uv run book-converter path/to/book.fb2.zip -o build/book.pdf
```

## Per-book overrides

Create `<book_stem>.toml` next to the FB2:

```toml
title = "Correct Title"
author = "Правильный Автор"
lang = "en"
fonts = ["EB Garamond", "Liberation Serif"]
```

CLI flags (`--title`, `--author`, `--lang`, `--font`, ...) override TOML.

## Structure

- `src/book_converter/` — Python package: parser, renderer, CLI, typography
- `templates/classic.typ` — book template
- `templates/fonts/` — bundled fonts
- `books/` — input FB2 files
- `build/` — output PDFs
- `tests/` — pytest suite (fixtures in `tests/fixtures/`)
- `docs/superpowers/specs/` — design docs
- `docs/superpowers/plans/` — implementation plans

## Tests

```bash
uv run pytest
uv run pytest -m slow    # also runs real typst compile
```
