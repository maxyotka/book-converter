from book_converter.render.escape import typst_escape, typst_string


def test_typst_escape_escapes_markup_chars():
    assert typst_escape("a [b] c") == "a \\[b\\] c"
    assert typst_escape("#tag") == "\\#tag"
    assert typst_escape("$x$") == "\\$x\\$"
    assert typst_escape("a*b") == "a\\*b"


def test_typst_escape_backslash():
    assert typst_escape("a\\b") == "a\\\\b"


def test_typst_string_wraps_and_escapes():
    assert typst_string('say "hi"') == '"say \\"hi\\""'
    assert typst_string("") == '""'
