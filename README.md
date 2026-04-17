# book-converter

[![CI](https://github.com/maxyotka/book-converter/actions/workflows/ci.yml/badge.svg)](https://github.com/maxyotka/book-converter/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](CHANGELOG.md)

Universal **FB2 → beautiful PDF** converter with book-grade Russian / English
typography, built on [Typst](https://typst.app/).

Parses [FB2](http://www.fictionbook.org/) (including `.fb2.zip`), builds a
typed Document IR, applies pluggable typography (Russian, English,
passthrough), renders a Typst source via the `classic.typ` template, and
compiles the PDF.

> **RU.** Универсальный конвертер **FB2 → PDF** с книжной типографикой
> (русской и английской). Парсер FB2 (`.fb2` и `.fb2.zip`) строит типизированный
> Document IR, типографика применяется плагином по языку, шаблон `classic.typ`
> рендерит Typst-исходник, компиляция — через Typst CLI.

---

## Highlights

- **Full FB2 coverage** — sections nested 5+ levels, `<part>`, `<subtitle>`,
  `<epigraph>`, `<cite>`, `<poem>`, `<table>` (flattened with inline
  formatting preserved), `<image>` / `<binary>`, footnotes
  (`<a type="note">` + `<body name="notes">`), and every inline tag.
- **Pluggable typography** — Russian (Russian quotes, non-breaking spaces
  after short prepositions, em-dashes), English (smart quotes, `--` →
  em-dash), passthrough for the rest. Adding a language = one module + one
  registry line.
- **Layered config** — FB2 metadata → `<book_stem>.toml` → CLI flags.
- **Two CLI modes** — single-shot (`book-converter <input>`) and batch
  (`book-converter build [dir]`) with per-book error isolation.
- **Hardened parser** — `defusedxml` against XXE, path-traversal guards,
  defensive handling of empty sections and malformed footnotes.
- **Localized template** — Contents / Source / Series / typeset notice
  strings are pulled from an `l10n` dict keyed by the book's language.

## Requirements

- Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/)
- [Typst CLI](https://typst.app/) ≥ 0.12 on `PATH`
- Fonts in `templates/fonts/` — PT Serif ships under the SIL OFL 1.1

## Install

```bash
git clone https://github.com/maxyotka/book-converter.git
cd book-converter
uv sync
```

## Quick start

```bash
# single shot
uv run book-converter books/one.fb2.zip                    # → build/one.pdf

# batch — every .fb2 / .fb2.zip under books/
uv run book-converter build books --out-dir build

# convenience wrapper
./build.sh
```

## Per-book overrides

Drop `<stem>.toml` next to `<stem>.fb2.zip`:

```toml
title = "Correct Title"
author = "Correct Author"
lang = "en"
publisher = "ACME"
year = "2026"
isbn = "978-..."
fonts = ["EB Garamond", "Liberation Serif"]
```

Flags (`--title`, `--author`, `--lang`, `--font`, `--publisher`, `--year`,
`--isbn`, `--config`) override TOML, which overrides FB2 metadata. Empty
publisher / year / ISBN are skipped on the copyright page.

## Architecture

```
src/book_converter/
  cli.py              single-shot + batch dispatch
  config.py           BookConfig: FB2 ↔ TOML ↔ CLI merge
  batch.py            books/ scan with per-book error isolation
  ir.py               Pydantic v2 Document IR
  fb2/
    loader.py         .fb2 / .fb2.zip → defusedxml tree
    parser.py         ET.Element → Document IR
  typography/
    base.py           Protocol + Passthrough + flatten/rebuild helpers
    russian.py        RussianTypography
    english.py        EnglishTypography
    registry.py       lang-code → plugin, fallback Passthrough
  render/
    typst.py          Document IR → Typst source + binary assets
    escape.py         _typst_escape / _typst_string
templates/
  classic.typ         book template (part/chapter/subsection/epigraph/poem)
  fonts/              PT Serif (OFL)
books/                input FB2 (gitignored)
build/                output PDF (gitignored)
tests/                pytest suite + fixtures
```

## Tests

```bash
uv run pytest          # 90 fast tests (parser, IR, render, typography)
uv run pytest -m slow  # + integration compile via typst CLI
```

Integration smoke (`tests/test_integration_smoke.py`) expects two FB2 files
in `books/`; both are gitignored, so drop them in yourself — slow tests skip
when they are absent.

## Adding a language

1. Create `src/book_converter/typography/<lang>.py` with a class implementing
   `TypographyPlugin.transform_paragraph(inlines) -> inlines`.
2. Register it in `typography/registry.py` by its ISO 639-1 code.
3. Mirror `tests/test_typography_russian.py` for coverage.
4. Add localized strings to the `l10n` dict in `templates/classic.typ` if
   needed (Contents, Source, Series, …).

## Troubleshooting

- **`unknown font family: pt serif`** — pass `--font-path templates/fonts`
  to Typst, or use the `book-converter` CLI which wires it up automatically.
- **`program not found: book-converter`** — re-run `uv sync` after pulling;
  the entry point is installed by the Hatchling build backend.
- **Slow tests skip** — expected unless you drop the two referenced FB2
  files into `books/`.

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup, commit
style, and guidance on adding new languages or template variants.

## License

Source code: [MIT](LICENSE).

Bundled PT Serif fonts under `templates/fonts/`: SIL Open Font License 1.1 —
see [`templates/fonts/OFL.txt`](templates/fonts/OFL.txt) and
[`templates/fonts/README.md`](templates/fonts/README.md) for full
attribution.
