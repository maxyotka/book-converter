# Book Converter — «Русалка. Поиск»

Конвертирует FB2 книгу Владимира Сотникова «Русалка. Поиск» (серия «Веня Пухов», №3)
в красиво оформленный PDF с русской типографикой, буквицами и шмуцтитулами.

## Требования

- Python 3.11+ и [uv](https://docs.astral.sh/uv/)
- [Typst](https://typst.app/) CLI (>= 0.12)
- Шрифт PT Serif в `src/fonts/` (уже включён)

## Сборка

```bash
uv sync
./build.sh
```

Результат: `build/Rusalka-Poisk.pdf`.

## Структура

- `src/fb2_to_typst.py` — парсер FB2 → Typst-источник + обложка
- `src/template.typ` — шаблон оформления (книжная типографика)
- `src/fonts/` — PT Serif (OFL)
- `tests/` — pytest-тесты для парсера
- `docs/superpowers/specs/` — дизайн-документ
- `docs/superpowers/plans/` — план реализации

## Тесты

```bash
uv run pytest
```
