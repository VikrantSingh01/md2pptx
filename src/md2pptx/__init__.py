"""``md2pptx`` - turn Markdown into leadership-grade PowerPoint decks."""

from __future__ import annotations

from .builder import build
from .model import Deck, Slide, SlideKind
from .parser import parse_file, parse_files, parse_markdown
from .renderer import render_deck
from .themes import available_themes, get_theme

__version__ = "0.1.0"

__all__ = [
    "build",
    "parse_file",
    "parse_files",
    "parse_markdown",
    "render_deck",
    "get_theme",
    "available_themes",
    "Deck",
    "Slide",
    "SlideKind",
    "__version__",
]
