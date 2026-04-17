# book-converter

[English](README.md) · **Русский**

[![CI](https://github.com/maxyotka/book-converter/actions/workflows/ci.yml/badge.svg)](https://github.com/maxyotka/book-converter/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](CHANGELOG.md)

Универсальный конвертер **FB2 → красивый PDF** с книжной типографикой
(русской и английской), построенный на [Typst](https://typst.app/).

Парсит [FB2](http://www.fictionbook.org/) (включая `.fb2.zip`), строит
типизированный Document IR, применяет плагинную типографику (русская /
английская / passthrough), рендерит Typst-исходник через шаблон
`classic.typ` и компилирует PDF.

---

## Возможности

- **Полное покрытие FB2** — секции и вложенность 5+ уровней, `<part>`,
  `<subtitle>`, `<epigraph>`, `<cite>`, `<poem>`, `<table>` (flatten в
  абзацы с сохранением inline-форматирования), `<image>` / `<binary>`,
  сноски (`<a type="note">` + `<body name="notes">`) и все inline-теги.
- **Плагинная типографика** — русская (ёлочки, неразрывные пробелы после
  коротких предлогов, тире), английская (smart quotes, `--` → em-dash),
  passthrough для прочих языков. Добавить язык = модуль + строчка в
  registry.
- **Слоёный конфиг** — метаданные FB2 → `<book_stem>.toml` → CLI-флаги.
- **Два режима CLI** — single-shot (`book-converter <input>`) и batch
  (`book-converter build [dir]`) с изоляцией ошибок по книгам.
- **Защищённый парсер** — `defusedxml` от XXE, защита от path traversal,
  устойчивость к пустым секциям и битым сноскам.
- **Локализация шаблона** — строки «Оглавление» / «Источник» / «Серия» и
  copyright-формула берутся из словаря `l10n` по языку книги.

## Требования

- Python ≥ 3.11 и [uv](https://docs.astral.sh/uv/)
- [Typst CLI](https://typst.app/) ≥ 0.12 в `PATH`
- Шрифты в `templates/fonts/` — PT Serif поставляется под SIL OFL 1.1

## Установка

```bash
git clone https://github.com/maxyotka/book-converter.git
cd book-converter
uv sync
```

## Быстрый старт

```bash
# одиночная конвертация
uv run book-converter books/one.fb2.zip                    # → build/one.pdf

# батч — все .fb2 / .fb2.zip из books/
uv run book-converter build books --out-dir build

# удобный враппер
./build.sh
```

## Overrides на книгу

Рядом с `<stem>.fb2.zip` положите `<stem>.toml`:

```toml
title = "Правильный заголовок"
author = "Правильный Автор"
lang = "ru"
publisher = "ACME"
year = "2026"
isbn = "978-..."
fonts = ["EB Garamond", "Liberation Serif"]
```

Флаги (`--title`, `--author`, `--lang`, `--font`, `--publisher`, `--year`,
`--isbn`, `--config`) перекрывают TOML, TOML перекрывает метаданные FB2.
Пустые publisher / year / ISBN не попадают на copyright page.

## Архитектура

```
src/book_converter/
  cli.py              диспетчер single-shot и batch режимов
  config.py           BookConfig: склейка FB2 ↔ TOML ↔ CLI
  batch.py            сканирование books/ с изоляцией ошибок
  ir.py               Pydantic v2 Document IR
  fb2/
    loader.py         .fb2 / .fb2.zip → defusedxml-дерево
    parser.py         ET.Element → Document IR
  typography/
    base.py           Protocol + Passthrough + flatten/rebuild
    russian.py        RussianTypography
    english.py        EnglishTypography
    registry.py       lang-код → плагин, fallback на Passthrough
  render/
    typst.py          Document IR → Typst-исходник + бинарные ассеты
    escape.py         _typst_escape / _typst_string
templates/
  classic.typ         шаблон книги (part/chapter/subsection/epigraph/poem)
  fonts/              PT Serif (OFL)
books/                входные FB2 (gitignored)
build/                выходные PDF (gitignored)
tests/                pytest-сьют и фикстуры
```

## Тесты

```bash
uv run pytest          # 90 быстрых (парсер, IR, рендер, типографика)
uv run pytest -m slow  # + интеграция через typst CLI
```

Интеграционный smoke (`tests/test_integration_smoke.py`) ждёт два FB2 в
`books/`; оба gitignored, так что положите их руками — slow-тесты
скипаются, если их нет.

## Добавление языка

1. Создайте `src/book_converter/typography/<lang>.py` с классом,
   реализующим `TypographyPlugin.transform_paragraph(inlines) -> inlines`.
2. Зарегистрируйте в `typography/registry.py` по ISO 639-1 коду.
3. Повторите структуру `tests/test_typography_russian.py` для покрытия.
4. Добавьте локализованные строки в словарь `l10n` в
   `templates/classic.typ`, если нужно (Оглавление, Источник, Серия, …).

## Траблшутинг

- **`unknown font family: pt serif`** — передайте `--font-path templates/fonts`
  в Typst или запускайте через `book-converter` CLI (он подхватывает
  автоматически).
- **`program not found: book-converter`** — после `git pull` перезапустите
  `uv sync`; entry point ставится Hatchling-бэкендом.
- **Slow-тесты скипаются** — ожидаемо без двух referenced FB2 в `books/`.

## Участие

PR приветствуются. См. [CONTRIBUTING.md](CONTRIBUTING.md) — dev-сетап,
стиль коммитов, гайд по добавлению языков и вариантов шаблона.

## Лицензия

Исходный код: [MIT](LICENSE).

Встроенные шрифты PT Serif в `templates/fonts/`: SIL Open Font License 1.1 —
см. [`templates/fonts/OFL.txt`](templates/fonts/OFL.txt) и
[`templates/fonts/README.md`](templates/fonts/README.md) для полной
атрибуции.
