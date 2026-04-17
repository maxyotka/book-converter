from book_converter.ir import (
    Epigraph,
    InlineText,
    Paragraph,
    Section,
)
from book_converter.render.typst import render_section


def _no_fn(nid):
    return None


def test_part_level_1():
    s = Section(level=1, title=[[InlineText(text="Книга первая")]], blocks=[])
    out = render_section(s, _no_fn)
    assert out.startswith("#part(")
    assert "Книга первая" in out


def test_chapter_level_2_with_number_label():
    s = Section(
        level=2,
        title=[[InlineText(text="Глава 1")], [InlineText(text="Начало")]],
        blocks=[Paragraph(inlines=[InlineText(text="короткий")])],
    )
    out = render_section(s, _no_fn)
    assert "#chapter(" in out
    assert "Глава 1" in out
    assert "Начало" in out


def test_chapter_level_2_without_number_label():
    s = Section(
        level=2,
        title=[[InlineText(text="Эпилог")]],
        blocks=[],
    )
    out = render_section(s, _no_fn)
    assert "#chapter(" in out
    assert "Эпилог" in out


def test_subsection_level_3():
    s = Section(level=3, title=[[InlineText(text="Раздел A")]], blocks=[])
    out = render_section(s, _no_fn)
    assert "#subsection(" in out
    assert "level: 3" in out


def test_dropcap_applied_to_first_paragraph_of_level_2():
    long_text = "Первый параграф, достаточно длинный для буквицы. " * 5
    s = Section(
        level=2,
        title=[[InlineText(text="Глава 1")]],
        blocks=[Paragraph(inlines=[InlineText(text=long_text)])],
    )
    out = render_section(s, _no_fn)
    assert "#dropcap" in out


def test_dropcap_skips_epigraph_before_paragraph():
    long_text = "Первый параграф длинный достаточно для буквицы. " * 5
    s = Section(
        level=2,
        title=[[InlineText(text="Глава 1")]],
        blocks=[
            Epigraph(blocks=[Paragraph(inlines=[InlineText(text="эпи")])], author=None),
            Paragraph(inlines=[InlineText(text=long_text)]),
        ],
    )
    out = render_section(s, _no_fn)
    assert "#dropcap" in out


def test_no_dropcap_for_short_first_paragraph():
    s = Section(
        level=2,
        title=[[InlineText(text="Глава 1")]],
        blocks=[Paragraph(inlines=[InlineText(text="короткий")])],
    )
    out = render_section(s, _no_fn)
    assert "#dropcap" not in out


def test_untitled_part_passes_title_none():
    s = Section(level=1, title=[], blocks=[Paragraph(inlines=[InlineText(text="intro")])])
    out = render_section(s, _no_fn)
    assert "#part(title: none)" in out


def test_untitled_chapter_passes_title_none():
    s = Section(level=2, title=[], blocks=[Paragraph(inlines=[InlineText(text="x")])])
    out = render_section(s, _no_fn)
    assert "title: none" in out
    assert "#chapter(" in out


def test_untitled_part_with_empty_title_lines_passes_none():
    # Guard: title with empty inline lines (e.g. whitespace-only) must also collapse.
    s = Section(level=1, title=[[InlineText(text="")], [InlineText(text="   ")]], blocks=[])
    out = render_section(s, _no_fn)
    assert "#part(title: none)" in out


def test_untitled_subsection_passes_title_none():
    s = Section(level=3, title=[], blocks=[])
    out = render_section(s, _no_fn)
    assert "#subsection(level: 3, title: none)" in out
