# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-04-17

First stable release: universal FB2 → PDF converter with pluggable typography,
hardened parser, localized template, and complete packaging metadata.

### Added
- Hatchling build backend; installable via `uv sync` / `pip install`.
- MIT license with appendix covering the bundled PT Serif (SIL OFL 1.1).
- Full PyPI metadata in `pyproject.toml`: classifiers, keywords, project URLs.
- Typography plugin registry with Russian, English, and passthrough engines.
- FB2 parser covers `<part>`, `<subtitle>`, `<epigraph>`, `<cite>`, `<poem>`,
  `<table>`, `<image>` / `<binary>`, footnotes, and all inline tags.
- Layered configuration: FB2 metadata → `<stem>.toml` → CLI flags.
- Single-shot and batch CLI modes (`book-converter <input>` / `build`).
- Localized `classic.typ` strings (Contents, Source, Series, typeset notice).
- Integration smoke tests for two representative FB2 books (slow marker).

### Changed
- Template skips empty publisher / year / ISBN on the copyright page.
- Untitled FB2 sections no longer emit empty TOC entries — renderer passes
  `title: none` to `part` / `chapter` / `subsection` when titles are blank.
- Table flattening preserves inline formatting (bold, italic, sub, sup) when
  joining cells into pipe-delimited paragraphs.
- `flatten` / `rebuild` helpers extracted to the typography base module so
  language plugins share the same sentinel-based text transform pipeline.

### Security
- `defusedxml` replaces stdlib `xml.etree` to mitigate XXE / billion laughs.
- Path traversal guard on FB2 image references and output paths.
- Footnote and empty-section rendering hardened against malformed input.

[1.0.0]: https://github.com/maxyotka/book-converter/releases/tag/v1.0.0
