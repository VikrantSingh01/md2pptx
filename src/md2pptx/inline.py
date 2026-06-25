"""Inline Markdown → styled text runs.

Splits a string into ``(text, bold, italic, code)`` tuples so the renderer can
emit ``python-pptx`` runs with the right character formatting. Supports
``**bold**``, ``*italic*`` / ``_italic_``, `` `code` `` and ``[label](url)``
(rendered as the label text).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_TOKEN_RE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<bold>\*\*[^*]+\*\*|__[^_]+__)"
    r"|(?P<italic>\*[^*]+\*|_[^_]+_)"
    r"|(?P<link>\[[^\]]+\]\([^)]+\))"
)
_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\([^)]+\)")


@dataclass(frozen=True)
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False


def parse_inline(text: str) -> list[Run]:
    """Return the styled runs for a single line of Markdown text."""

    runs: list[Run] = []
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > pos:
            runs.append(Run(text[pos:m.start()]))
        if m.group("code"):
            runs.append(Run(m.group("code")[1:-1], code=True))
        elif m.group("bold"):
            runs.append(Run(m.group("bold")[2:-2], bold=True))
        elif m.group("italic"):
            runs.append(Run(m.group("italic")[1:-1], italic=True))
        elif m.group("link"):
            runs.append(Run(_LINK_RE.match(m.group("link")).group("label")))
        pos = m.end()
    if pos < len(text):
        runs.append(Run(text[pos:]))
    return runs or [Run(text)]
