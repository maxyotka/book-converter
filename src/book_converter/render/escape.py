"""Escape helpers for Typst content and string literals."""
from __future__ import annotations


def typst_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("#", "\\#")
        .replace("@", "\\@")
        .replace("$", "\\$")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("`", "\\`")
        .replace("<", "\\<")
        .replace(">", "\\>")
        .replace("/", "\\/")
    )


def typst_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
