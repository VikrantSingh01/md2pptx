"""Markdown (+ YAML-ish front matter) → :class:`~md2pptx.model.Deck`.

The parser is intentionally line-oriented and dependency-free. It supports the
subset of Markdown that matters for slides:

* YAML front matter (``key: value``) delimited by ``---`` at the top of file
* ``---`` on its own line separates slides
* ``#``/``##`` headings, bullet & numbered lists (nested by indentation)
* fenced code blocks, tables, block quotes and images
* speaker notes via a ``Notes:`` block or ``<!-- notes: ... -->``
* per-slide directives via ``<!-- class: section -->`` etc.
* two-column layouts via ``:::columns`` / ``:::`` fences

Inline emphasis (``**bold**``, ``*italic*``, `` `code` ``, links) is preserved
verbatim in the IR and expanded into runs by the renderer.
"""

from __future__ import annotations

import re
from pathlib import Path

from .model import (
    Bullet,
    CodeBlock,
    Column,
    Deck,
    ImageBlock,
    QuoteBlock,
    Slide,
    SlideKind,
    TableBlock,
)

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_CLASS_RE = re.compile(r"<!--\s*class:\s*([\w-]+)\s*-->", re.IGNORECASE)
_NOTES_INLINE_RE = re.compile(r"<!--\s*notes:\s*(.*?)\s*-->", re.IGNORECASE | re.DOTALL)
_IMAGE_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<path>.*?)\)\s*$")
_BULLET_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*+]|\d+\.)\s+(?P<text>.*)$")


def parse_file(path: str | Path) -> Deck:
    text = Path(path).read_text(encoding="utf-8")
    return parse_markdown(text, base_dir=Path(path).resolve().parent)


def parse_files(paths: list[str | Path]) -> Deck:
    """Parse and concatenate multiple Markdown files into a single deck.

    Front matter from the *first* file wins for deck-level metadata; slides from
    every file are appended in order.
    """

    deck: Deck | None = None
    for p in paths:
        d = parse_file(p)
        if deck is None:
            deck = d
        else:
            deck.slides.extend(d.slides)
            # Let later files contribute metadata only if the first omitted it.
            deck.title = deck.title or d.title
            deck.author = deck.author or d.author
    return deck or Deck()


def parse_markdown(text: str, base_dir: Path | None = None) -> Deck:
    deck = Deck()
    meta, body = _split_front_matter(text)
    _apply_metadata(deck, meta)

    raw_slides = _split_slides(body)
    for index, chunk in enumerate(raw_slides):
        slide = _parse_slide(chunk, base_dir)
        if slide.is_empty():
            continue
        _classify(slide, index, deck)
        deck.slides.append(slide)

    if not deck.title and deck.slides:
        deck.title = deck.slides[0].title
    return deck


# --------------------------------------------------------------------------- #
# Front matter
# --------------------------------------------------------------------------- #
def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    text = text.lstrip("\ufeff")  # strip BOM if present
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip().strip("\"'")
    return meta, text[match.end():]


def _apply_metadata(deck: Deck, meta: dict[str, str]) -> None:
    deck.title = meta.get("title", deck.title)
    deck.subtitle = meta.get("subtitle", deck.subtitle)
    deck.author = meta.get("author", deck.author)
    deck.date = meta.get("date", deck.date)
    deck.footer = meta.get("footer", deck.footer)
    deck.theme = meta.get("theme", deck.theme)


# --------------------------------------------------------------------------- #
# Slide splitting
# --------------------------------------------------------------------------- #
def _split_slides(body: str) -> list[str]:
    slides: list[str] = []
    current: list[str] = []
    in_code = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            current.append(line)
            continue
        if not in_code and re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            slides.append("\n".join(current))
            current = []
            continue
        current.append(line)
    slides.append("\n".join(current))
    return slides


# --------------------------------------------------------------------------- #
# Slide body parsing
# --------------------------------------------------------------------------- #
def _parse_slide(chunk: str, base_dir: Path | None) -> Slide:
    slide = Slide()
    lines = chunk.splitlines()

    # Pull out directives & inline notes first.
    cleaned: list[str] = []
    for line in lines:
        cls = _CLASS_RE.search(line)
        if cls:
            slide.__dict__["_directive"] = cls.group(1).lower()
            line = _CLASS_RE.sub("", line)
        note = _NOTES_INLINE_RE.search(line)
        if note:
            slide.notes = (slide.notes + "\n" + note.group(1)).strip()
            line = _NOTES_INLINE_RE.sub("", line)
        cleaned.append(line)

    _parse_blocks(cleaned, slide, base_dir)
    return slide


def _parse_blocks(lines: list[str], slide: Slide, base_dir: Path | None) -> None:
    i = 0
    n = len(lines)
    columns: list[Column] = []
    in_columns = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Column fences -----------------------------------------------------
        if stripped.startswith(":::"):
            token = stripped[3:].strip().lower()
            if token.startswith("column"):
                in_columns = True
                columns = [Column()]
                i += 1
                continue
            if token in ("", "end") and in_columns:  # closing fence
                slide.columns = columns
                in_columns = False
                i += 1
                continue
        if in_columns and stripped == "+++":  # column separator
            columns.append(Column())
            i += 1
            continue

        # Blank line --------------------------------------------------------
        if not stripped:
            i += 1
            continue

        # Speaker notes block ----------------------------------------------
        if stripped.lower().startswith("notes:"):
            note_text = stripped[len("notes:"):].strip()
            rest = [note_text] if note_text else []
            i += 1
            while i < n and lines[i].strip():
                rest.append(lines[i].strip())
                i += 1
            slide.notes = (slide.notes + "\n" + "\n".join(rest)).strip()
            continue

        # Headings ----------------------------------------------------------
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip()
            if not slide.title:
                slide.title = heading
            else:
                slide.subtitle = slide.subtitle or heading
            i += 1
            continue

        # Code fences -------------------------------------------------------
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            slide.code = CodeBlock(code="\n".join(code_lines), language=lang)
            continue

        # Images ------------------------------------------------------------
        img = _IMAGE_RE.match(stripped)
        if img:
            path = img.group("path")
            if base_dir and not (path.startswith("http") or Path(path).is_absolute()):
                path = str((base_dir / path).resolve())
            block = ImageBlock(path=path, alt=img.group("alt"))
            if in_columns:
                _current_column(columns).image = block
            else:
                slide.image = block
            i += 1
            continue

        # Block quotes ------------------------------------------------------
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            attribution = ""
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].strip()[1:].strip()
                if q.startswith("-"):
                    attribution = q.lstrip("-").strip()
                else:
                    quote_lines.append(q)
                i += 1
            slide.quote = QuoteBlock(text=" ".join(quote_lines), attribution=attribution)
            continue

        # Tables ------------------------------------------------------------
        if "|" in stripped and i + 1 < n and _is_table_separator(lines[i + 1]):
            headers = _split_row(stripped)
            i += 2  # header + separator
            rows: list[list[str]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            slide.table = TableBlock(headers=headers, rows=rows)
            continue

        # Bullets / numbered lists -----------------------------------------
        bullet = _BULLET_RE.match(line)
        if bullet:
            indent = len(bullet.group("indent").replace("\t", "  "))
            level = min(indent // 2, 4)
            ordered = bullet.group("marker").endswith(".")
            text = bullet.group("text").strip()
            b = Bullet(text=text, level=level, ordered=ordered)
            if in_columns:
                _current_column(columns).bullets.append(b)
            else:
                slide.bullets.append(b)
            i += 1
            continue

        # Plain paragraph ---------------------------------------------------
        if in_columns:
            _current_column(columns).paragraphs.append(stripped)
        else:
            slide.paragraphs.append(stripped)
        i += 1

    if in_columns and columns:
        slide.columns = columns


def _current_column(columns: list[Column]) -> Column:
    if not columns:
        columns.append(Column())
    return columns[-1]


def _is_table_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", line)) and "-" in line


def _split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #
def _classify(slide: Slide, index: int, deck: Deck) -> None:
    directive = slide.__dict__.pop("_directive", None)
    if directive in {"section", "closing", "title"}:
        slide.kind = SlideKind(directive)
        if not slide.title and slide.paragraphs:
            slide.title = slide.paragraphs.pop(0)
        return
    if directive in {k.value for k in SlideKind}:
        slide.kind = SlideKind(directive)
        return

    if slide.columns:
        slide.kind = SlideKind.TWO_COLUMN
        return
    if slide.quote and not slide.bullets and not slide.paragraphs:
        slide.kind = SlideKind.QUOTE
        return
    if slide.image and not slide.bullets and not slide.table and not slide.code:
        slide.kind = SlideKind.IMAGE
        return
    # First slide that is essentially just a title/subtitle → title slide.
    only_heading = not any(
        [slide.bullets, slide.paragraphs, slide.code, slide.table, slide.image, slide.quote]
    )
    if index == 0 and only_heading:
        slide.kind = SlideKind.TITLE
        deck.subtitle = deck.subtitle or slide.subtitle
        return
    slide.kind = SlideKind.CONTENT
