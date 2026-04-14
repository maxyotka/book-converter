from pathlib import Path

import pytest

from book_converter.config import BookConfig, apply_config_to_meta, load_book_config
from book_converter.ir import BookMeta, InlineText, Paragraph


def test_bookconfig_defaults():
    cfg = BookConfig()
    assert cfg.title is None
    assert cfg.fonts == ["PT Serif", "Times New Roman", "Libertinus Serif"]


def test_bookconfig_forbids_unknown_keys():
    with pytest.raises(ValueError):
        BookConfig(not_a_field="x")


def test_apply_config_overrides_meta():
    meta = BookMeta(title="FB2 title", author="FB2 author", lang="ru")
    cfg = BookConfig(title="Override title", year="2024")
    merged = apply_config_to_meta(meta, cfg)
    assert merged.title == "Override title"
    assert merged.author == "FB2 author"
    assert merged.year == "2024"


def test_apply_config_annotation_string_becomes_paragraph():
    meta = BookMeta(title="T", author="A", lang="ru")
    cfg = BookConfig(annotation="Override annotation.")
    merged = apply_config_to_meta(meta, cfg)
    assert len(merged.annotation) == 1
    p = merged.annotation[0]
    assert isinstance(p, Paragraph)
    assert p.inlines[0].text == "Override annotation."


def test_load_book_config_picks_sidecar_toml(tmp_path):
    fb2 = tmp_path / "sample.fb2.zip"
    fb2.write_bytes(b"")
    (tmp_path / "sample.toml").write_text(
        'title = "Sidecar Title"\nyear = "2030"\n', encoding="utf-8"
    )
    cfg = load_book_config(fb2, cli_overrides={})
    assert cfg.title == "Sidecar Title"
    assert cfg.year == "2030"


def test_load_book_config_cli_over_toml(tmp_path):
    fb2 = tmp_path / "sample.fb2.zip"
    fb2.write_bytes(b"")
    (tmp_path / "sample.toml").write_text('title = "Sidecar"\n', encoding="utf-8")
    cfg = load_book_config(fb2, cli_overrides={"title": "CLI"})
    assert cfg.title == "CLI"


def test_load_book_config_explicit_path(tmp_path):
    fb2 = tmp_path / "sample.fb2.zip"
    fb2.write_bytes(b"")
    other = tmp_path / "other.toml"
    other.write_text('title = "Explicit"\n', encoding="utf-8")
    cfg = load_book_config(fb2, cli_overrides={}, explicit_toml=other)
    assert cfg.title == "Explicit"


def test_cli_fonts_prepend_to_defaults():
    from book_converter.config import merge_cli_fonts

    cfg = BookConfig()
    merged = merge_cli_fonts(defaults=cfg.fonts, cli_fonts=["My Font"])
    assert merged[0] == "My Font"
    assert merged[-1] == "Libertinus Serif"
