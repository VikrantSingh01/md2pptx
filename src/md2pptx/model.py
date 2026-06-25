"""Intermediate representation (IR) for a presentation.

The parser turns Markdown into these plain dataclasses; the renderer turns the
dataclasses into a PowerPoint file. Keeping the IR free of any ``python-pptx``
types makes the parser trivially unit-testable and the two halves decoupled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SlideKind(str, Enum):
    """High level slide archetypes that map to distinct visual layouts."""

    TITLE = "title"
    SECTION = "section"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE = "image"
    QUOTE = "quote"
    CLOSING = "closing"


@dataclass
class Bullet:
    """A single list item, possibly nested and possibly numbered."""

    text: str
    level: int = 0
    ordered: bool = False


@dataclass
class TableBlock:
    headers: list[str]
    rows: list[list[str]]


@dataclass
class CodeBlock:
    code: str
    language: str = ""


@dataclass
class ImageBlock:
    path: str
    alt: str = ""


@dataclass
class QuoteBlock:
    text: str
    attribution: str = ""


@dataclass
class Column:
    """One column of a two-column slide."""

    bullets: list[Bullet] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    image: ImageBlock | None = None


@dataclass
class Slide:
    kind: SlideKind = SlideKind.CONTENT
    title: str = ""
    subtitle: str = ""
    eyebrow: str = ""  # small kicker text above a title (e.g. section number)
    bullets: list[Bullet] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    code: CodeBlock | None = None
    table: TableBlock | None = None
    image: ImageBlock | None = None
    quote: QuoteBlock | None = None
    columns: list[Column] = field(default_factory=list)
    notes: str = ""

    def is_empty(self) -> bool:
        return not any(
            [
                self.title,
                self.subtitle,
                self.eyebrow,
                self.bullets,
                self.paragraphs,
                self.code,
                self.table,
                self.image,
                self.quote,
                self.columns,
            ]
        )


@dataclass
class Deck:
    """A full presentation: metadata plus an ordered list of slides."""

    title: str = ""
    subtitle: str = ""
    author: str = ""
    date: str = ""
    footer: str = ""
    theme: str = "executive"
    slides: list[Slide] = field(default_factory=list)
