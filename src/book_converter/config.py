"""Layered book configuration: FB2 metadata <- TOML <- CLI overrides."""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from book_converter.ir import BookMeta, InlineText, Paragraph


class BookConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    author: str | None = None
    lang: str | None = None
    series_name: str | None = None
    series_number: int | None = None
    publisher: str | None = None
    year: str | None = None
    isbn: str | None = None
    annotation: str | None = None
    fonts: list[str] = Field(
        default_factory=lambda: [
            "PT Serif",
            "Times New Roman",
            "Libertinus Serif",
        ]
    )
    output: str | None = None


def merge_cli_fonts(defaults: list[str], cli_fonts: list[str]) -> list[str]:
    """Prepend CLI fonts to defaults, deduplicating while preserving order."""
    seen: set[str] = set()
    out: list[str] = []
    for f in list(cli_fonts) + list(defaults):
        if f not in seen:
            out.append(f)
            seen.add(f)
    return out


def load_book_config(
    fb2_path: Path,
    cli_overrides: dict[str, Any],
    explicit_toml: Path | None = None,
) -> BookConfig:
    data: dict[str, Any] = {}

    toml_path: Path | None = explicit_toml
    if toml_path is None:
        stem = fb2_path.name
        for suffix in (".fb2.zip", ".fb2"):
            if stem.lower().endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        candidate = fb2_path.parent / f"{stem}.toml"
        if candidate.exists():
            toml_path = candidate

    if toml_path is not None and toml_path.exists():
        with toml_path.open("rb") as f:
            data.update(tomllib.load(f))

    for k, v in cli_overrides.items():
        if v is None:
            continue
        if k == "fonts":
            data["fonts"] = merge_cli_fonts(
                defaults=data.get("fonts", BookConfig().fonts),
                cli_fonts=v,
            )
        else:
            data[k] = v

    return BookConfig(**data)


def apply_config_to_meta(meta: BookMeta, config: BookConfig) -> BookMeta:
    updates: dict[str, Any] = {}
    for field in (
        "title",
        "author",
        "lang",
        "series_name",
        "series_number",
        "publisher",
        "year",
        "isbn",
    ):
        value = getattr(config, field)
        if value is not None:
            updates[field] = value
    if config.annotation is not None:
        updates["annotation"] = [
            Paragraph(inlines=[InlineText(text=config.annotation)])
        ]
    return meta.model_copy(update=updates)
