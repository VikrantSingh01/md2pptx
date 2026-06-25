"""High-level orchestration: Markdown file(s) → ``.pptx`` on disk."""

from __future__ import annotations

from pathlib import Path

from .model import Deck
from .parser import parse_files
from .renderer import render_deck
from .themes import get_theme


def build(
    inputs: list[str | Path],
    output: str | Path,
    *,
    theme: str | None = None,
) -> Deck:
    """Parse ``inputs`` and write a presentation to ``output``.

    Args:
        inputs: One or more Markdown files. Slides are concatenated in order.
        output: Destination ``.pptx`` path.
        theme: Optional theme override (front-matter ``theme`` is used otherwise).

    Returns:
        The parsed :class:`Deck` (handy for tests and tooling).
    """

    if not inputs:
        raise ValueError("At least one input Markdown file is required.")

    deck = parse_files(list(inputs))
    if theme:
        get_theme(theme)  # validate early; raises KeyError on a bad name
        deck.theme = theme

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    render_deck(deck, str(out))
    return deck
