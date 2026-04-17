# Contributing

Thanks for considering a contribution. The project is a Python CLI that parses
FB2, builds a typed Document IR, and compiles it to PDF via Typst. Changes are
welcome in any of these layers.

## Dev setup

```bash
git clone https://github.com/maxyotka/book-converter.git
cd book-converter
uv sync
uv run pytest
```

Typst ≥ 0.12 must be on `PATH` for integration tests and real PDF output.

## Running tests

```bash
uv run pytest              # ~90 fast tests (parser, IR, render, typography)
uv run pytest -m slow      # + real `typst compile` on bundled fixtures
```

Add tests for every behavioral change. The fast suite must stay green and fast;
reserve `@pytest.mark.slow` for anything that spawns a subprocess or produces a
real PDF.

## Project layout

```
src/book_converter/  parser, IR, config, render, typography
templates/           classic.typ + bundled PT Serif (OFL)
tests/               pytest suite + fixtures
```

Key abstractions:

- **Typography plugin**: implement `transform_paragraph(inlines) -> inlines`
  and register via `typography/registry.py`. Helpers `flatten` / `rebuild` in
  `typography/base.py` convert between inline lists and text-with-sentinels so
  regex-based rules can work at the string level.
- **Document IR** (`ir.py`): Pydantic v2 model. Parser output and renderer
  input — treat it as the contract between layers.
- **Template** (`templates/classic.typ`): book-level Typst template with
  `part` / `chapter` / `subsection` / `epigraph` / `cite-block` / `poem`.

## Adding a language

1. Create `src/book_converter/typography/<lang>.py` with a class implementing
   `TypographyPlugin`.
2. Register it in `typography/registry.py` keyed by ISO 639-1 code.
3. Add unit tests mirroring `tests/test_typography_russian.py`.
4. Add translation strings to the `l10n` dict in `templates/classic.typ` if the
   language needs localized UI strings (Contents, Source, …).

## Commit style

Atomic commits, imperative mood, conventional-commit prefix where it helps
(`feat`, `fix`, `refactor`, `test`, `docs`, `chore`). Example:

```
fix(render): skip empty headings to keep the TOC clean
```

## Pull requests

- One topic per PR.
- Describe the user-visible effect and reference any fixture or test that
  proves it.
- CI must pass. If you touch rendering, include a short note about what the
  output looked like before/after.
