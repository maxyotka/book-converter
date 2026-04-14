"""Render Document IR → Typst source."""
from __future__ import annotations

import re as _re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from book_converter.ir import (
    Binary,
    Block,
    Cite,
    Document,
    Epigraph,
    Footnote,
    Image,
    Inline,
    InlineEmphasis,
    InlineFootnoteRef,
    InlineLink,
    InlineStrong,
    InlineSub,
    InlineSup,
    InlineText,
    Paragraph,
    Poem,
    PoemStanza,
    SceneBreak,
    Section,
    Subtitle,
)
from book_converter.render.escape import typst_escape, typst_string
from book_converter.typography import registry as _typo_registry

FootnoteResolver = Callable[[str], object]


def render_inlines(inlines: list[Inline], footnote_resolver: FootnoteResolver) -> str:
    parts: list[str] = []
    for node in inlines:
        parts.append(_render_one(node, footnote_resolver))
    return "".join(parts)


def _render_one(node: Inline, fn_resolver: FootnoteResolver) -> str:
    if isinstance(node, InlineText):
        return typst_escape(node.text)
    if isinstance(node, InlineEmphasis):
        return f"#emph[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineStrong):
        return f"#strong[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineSub):
        return f"#sub[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineSup):
        return f"#super[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineLink):
        return f"#link({typst_string(node.url)})[{render_inlines(node.children, fn_resolver)}]"
    if isinstance(node, InlineFootnoteRef):
        body = fn_resolver(node.note_id)
        if body is None:
            print(f"warning: unresolved footnote ref '{node.note_id}'", file=sys.stderr)
            return "#super[?]"
        return f"#footnote[{body}]"
    return ""


def _maybe_author(author) -> str:
    if author is None:
        return "none"
    return f"[{render_inlines(author, lambda _nid: None)}]"


def render_block(
    block,
    footnote_resolver: FootnoteResolver,
    image_path: Callable[[str], str] | None = None,
) -> str:
    if image_path is None:
        image_path = lambda bid: bid

    if isinstance(block, Paragraph):
        return f"#para[{render_inlines(block.inlines, footnote_resolver)}]"
    if isinstance(block, Subtitle):
        return f"#subtitle[{render_inlines(block.inlines, footnote_resolver)}]"
    if isinstance(block, SceneBreak):
        return "#scene-break"
    if isinstance(block, Image):
        return f"#book-image[#image({typst_string(image_path(block.binary_id))}, width: 80%)]"
    if isinstance(block, Epigraph):
        author = _maybe_author(block.author)
        body = "\n".join(render_block(b, footnote_resolver, image_path) for b in block.blocks)
        return f"#epigraph(author: {author})[\n{body}\n]"
    if isinstance(block, Cite):
        author = _maybe_author(block.author)
        body = "\n".join(render_block(b, footnote_resolver, image_path) for b in block.blocks)
        return f"#cite-block(author: {author})[\n{body}\n]"
    if isinstance(block, Poem):
        title = "none" if block.title is None else f"[{render_inlines(block.title, footnote_resolver)}]"
        author = _maybe_author(block.author)
        stanzas_src = []
        for stanza in block.stanzas:
            lines_src = [f"[{render_inlines(line, footnote_resolver)}]" for line in stanza.lines]
            stanzas_src.append("(" + ", ".join(lines_src) + ",)")
        stanzas_tuple = "(" + ", ".join(stanzas_src) + ",)"
        return f"#poem(title: {title}, author: {author}, stanzas: {stanzas_tuple})"
    raise TypeError(f"render_block does not handle {type(block).__name__}")


_CHAPTER_LABEL_RE = _re.compile(r"^\s*(Глава|Chapter|Part)\s+\S+", _re.IGNORECASE)


def _has_nested_sections(sections: list) -> bool:
    """True if any top-level section contains a nested Section block."""
    for s in sections:
        for b in s.blocks:
            if isinstance(b, Section):
                return True
    return False


def _plain_text_length(inlines: list) -> int:
    total = 0
    for n in inlines:
        if isinstance(n, InlineText):
            total += len(n.text)
        elif hasattr(n, "children"):
            total += _plain_text_length(n.children)
    return total


def _first_paragraph_plain(inlines: list) -> str:
    parts = []
    for n in inlines:
        if isinstance(n, InlineText):
            parts.append(n.text)
        elif hasattr(n, "children"):
            parts.append(_first_paragraph_plain(n.children))
    return "".join(parts)


def _render_title_lines(title: list, fn_resolver: FootnoteResolver) -> str:
    rendered = [render_inlines(line, fn_resolver) for line in title]
    return " \\ ".join(rendered)


def render_section(
    section,
    footnote_resolver: FootnoteResolver,
    image_path: Callable[[str], str] | None = None,
    level_offset: int = 0,
) -> str:
    image_path = image_path or (lambda bid: bid)
    effective_level = section.level + level_offset

    if effective_level == 1:
        title_src = _render_title_lines(section.title, footnote_resolver)
        parts: list[str] = [f"#part(title: [{title_src}])"]
        for block in section.blocks:
            if isinstance(block, Section):
                parts.append(render_section(block, footnote_resolver, image_path, level_offset))
            else:
                parts.append(render_block(block, footnote_resolver, image_path))
        return "\n".join(parts)

    if effective_level == 2:
        if section.title and _CHAPTER_LABEL_RE.match(_first_paragraph_plain(section.title[0])):
            number_line = render_inlines(section.title[0], footnote_resolver)
            rest_lines = [render_inlines(line, footnote_resolver) for line in section.title[1:]]
            title_src = " \\ ".join(rest_lines) if rest_lines else ""
            number_arg = f"number: {typst_string(number_line)}, "
        else:
            number_arg = ""
            title_src = _render_title_lines(section.title, footnote_resolver)
        body = _render_section_body(section, footnote_resolver, image_path, dropcap=True, level_offset=level_offset)
        return f"#chapter({number_arg}title: [{title_src}])[\n{body}\n]"

    title_src = _render_title_lines(section.title, footnote_resolver)
    body = _render_section_body(section, footnote_resolver, image_path, dropcap=False, level_offset=level_offset)
    return f"#subsection(level: {effective_level}, title: [{title_src}])[\n{body}\n]"


def _render_section_body(
    section,
    fn_resolver: FootnoteResolver,
    image_path: Callable[[str], str],
    dropcap: bool,
    level_offset: int = 0,
) -> str:
    dropcap_done = not dropcap
    parts: list[str] = []
    for block in section.blocks:
        if isinstance(block, Section):
            parts.append(render_section(block, fn_resolver, image_path, level_offset))
            continue
        if (
            not dropcap_done
            and isinstance(block, Paragraph)
            and _plain_text_length(block.inlines) >= 120
        ):
            plain = _first_paragraph_plain(block.inlines)
            first = plain[0]
            rest_inlines = [InlineText(text=plain[1:])]
            rest_src = render_inlines(rest_inlines, fn_resolver)
            parts.append(f"#para[#dropcap({typst_string(first)})[{rest_src}]]")
            dropcap_done = True
            continue
        parts.append(render_block(block, fn_resolver, image_path))
    return "\n".join(parts)


def _strip_fnref(inlines: list, warned: list) -> list:
    out: list = []
    for n in inlines:
        if isinstance(n, InlineFootnoteRef):
            warned[0] = True
            continue
        if isinstance(n, InlineText):
            out.append(n)
        elif isinstance(n, InlineLink):
            out.append(InlineLink(url=n.url, children=_strip_fnref(n.children, warned)))
        elif hasattr(n, "children"):
            out.append(type(n)(children=_strip_fnref(n.children, warned)))
        else:
            out.append(n)
    return out


def make_footnote_resolver(footnotes: dict[str, Footnote]) -> FootnoteResolver:
    def _resolve(note_id: str):
        fn = footnotes.get(note_id)
        if fn is None:
            return None
        warned = [False]
        parts: list[str] = []
        for block in fn.blocks:
            if isinstance(block, Paragraph):
                stripped = _strip_fnref(block.inlines, warned)
                parts.append(render_inlines(stripped, lambda _n: None))
        if warned[0]:
            print(f"warning: nested footnote in '{note_id}' flattened", file=sys.stderr)
        return " ".join(parts)

    return _resolve


@dataclass
class RenderResult:
    typ_path: Path
    assets: list


def _write_binaries(binaries: dict, workdir: Path) -> dict:
    assets_dir = workdir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    for bid, binary in binaries.items():
        target = assets_dir / binary.filename
        target.write_bytes(binary.data)
        mapping[bid] = f"assets/{binary.filename}"
    return mapping


def _render_annotation(blocks: list, footnote_resolver: FootnoteResolver) -> str:
    parts = []
    for b in blocks:
        if isinstance(b, Paragraph):
            parts.append(render_inlines(b.inlines, footnote_resolver))
    return " ".join(parts)


def _apply_typography(doc, typography):
    def _transform_blocks(blocks: list) -> list:
        out = []
        for b in blocks:
            if isinstance(b, Paragraph):
                out.append(Paragraph(inlines=typography.transform_paragraph(b.inlines)))
            elif isinstance(b, Subtitle):
                out.append(Subtitle(inlines=typography.transform_paragraph(b.inlines)))
            elif isinstance(b, Section):
                out.append(Section(
                    level=b.level,
                    title=[typography.transform_paragraph(line) for line in b.title],
                    blocks=_transform_blocks(b.blocks),
                ))
            elif isinstance(b, Epigraph):
                out.append(Epigraph(
                    blocks=_transform_blocks(b.blocks),
                    author=typography.transform_paragraph(b.author) if b.author else None,
                ))
            elif isinstance(b, Cite):
                out.append(Cite(
                    blocks=_transform_blocks(b.blocks),
                    author=typography.transform_paragraph(b.author) if b.author else None,
                ))
            elif isinstance(b, Poem):
                new_stanzas = [
                    PoemStanza(lines=[typography.transform_paragraph(line) for line in st.lines])
                    for st in b.stanzas
                ]
                out.append(Poem(
                    title=typography.transform_paragraph(b.title) if b.title else None,
                    stanzas=new_stanzas,
                    author=typography.transform_paragraph(b.author) if b.author else None,
                ))
            else:
                out.append(b)
        return out

    new_sections = [
        Section(
            level=s.level,
            title=[typography.transform_paragraph(line) for line in s.title],
            blocks=_transform_blocks(s.blocks),
        )
        for s in doc.sections
    ]
    new_footnotes = {
        fid: Footnote(id=fid, blocks=_transform_blocks(fn.blocks))
        for fid, fn in doc.footnotes.items()
    }
    new_meta = doc.meta.model_copy(update={
        "annotation": _transform_blocks(doc.meta.annotation),
    })
    return Document(
        meta=new_meta,
        sections=new_sections,
        footnotes=new_footnotes,
        binaries=doc.binaries,
    )


def render(doc, workdir, fonts: list) -> RenderResult:
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    typography = _typo_registry.get(doc.meta.lang)
    doc = _apply_typography(doc, typography)

    asset_map = _write_binaries(doc.binaries, workdir)

    def image_path(bid: str) -> str:
        return asset_map.get(bid, f"assets/{bid}")

    fn_resolver = make_footnote_resolver(doc.footnotes)

    lines: list[str] = []
    lines.append('#import "/templates/classic.typ": *')
    lines.append("")
    lines.append("#show: book.with(")
    lines.append(f"  title: {typst_string(doc.meta.title)},")
    lines.append(f"  author: {typst_string(doc.meta.author)},")
    lines.append(f"  lang: {typst_string(doc.meta.lang)},")
    fonts_src = "(" + ", ".join(typst_string(f) for f in fonts) + ",)"
    lines.append(f"  fonts: {fonts_src},")
    if doc.meta.series_name is not None:
        lines.append(f"  series-name: {typst_string(doc.meta.series_name)},")
        lines.append(f"  series-number: {doc.meta.series_number},")
    if doc.meta.cover_binary_id and doc.meta.cover_binary_id in doc.binaries:
        cover_path = asset_map[doc.meta.cover_binary_id]
        lines.append(
            f'  cover: image({typst_string(cover_path)}, width: 100%, height: 100%, fit: "cover"),'
        )
    lines.append(f"  publisher: {typst_string(doc.meta.publisher)},")
    lines.append(f"  year: {typst_string(doc.meta.year)},")
    lines.append(f"  isbn: {typst_string(doc.meta.isbn)},")
    ann_src = _render_annotation(doc.meta.annotation, fn_resolver)
    lines.append(f"  annotation: [{ann_src}],")
    lines.append(")")
    lines.append("")

    if doc.sections and not _has_nested_sections(doc.sections):
        min_top_level = min(s.level for s in doc.sections)
        level_offset = max(0, 2 - min_top_level)
    else:
        level_offset = 0
    for section in doc.sections:
        lines.append(render_section(section, fn_resolver, image_path, level_offset))
        lines.append("")

    typ_source = "\n".join(lines)
    typ_path = workdir / "book.typ"
    typ_path.write_text(typ_source, encoding="utf-8")

    return RenderResult(typ_path=typ_path, assets=list((workdir / "assets").glob("*")))
