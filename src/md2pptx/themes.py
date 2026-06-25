"""Professional, presentation-ready themes.

A :class:`Theme` is a small bundle of colours, fonts and geometry. Themes are
deliberately data-only so they are easy to read, tweak and add to. All colours
are RGB hex strings; the renderer converts them to ``python-pptx`` types.

Design intent: clean, executive, high-contrast typography with generous white
space — the kind of deck you would show to a leadership team.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Palette:
    background: str
    surface: str          # panels / cards
    primary: str          # headings / brand
    secondary: str        # subdued text
    accent: str           # highlights, bullet ticks, rules
    accent_soft: str      # subtle fills
    text: str             # body text on background
    text_inverse: str     # text on dark/brand fills


@dataclass(frozen=True)
class Fonts:
    heading: str
    body: str
    mono: str


@dataclass(frozen=True)
class Theme:
    name: str
    palette: Palette
    fonts: Fonts
    # Type scale in points.
    title_size: int = 40
    section_size: int = 36
    heading_size: int = 28
    body_size: int = 18
    small_size: int = 12
    # Layout geometry in inches (16:9 canvas is 13.333 x 7.5).
    margin: float = 0.9
    aliases: tuple[str, ...] = field(default=())


_THEMES: dict[str, Theme] = {}


def _register(theme: Theme) -> Theme:
    _THEMES[theme.name.lower()] = theme
    for alias in theme.aliases:
        _THEMES[alias.lower()] = theme
    return theme


EXECUTIVE = _register(
    Theme(
        name="executive",
        aliases=("navy", "default"),
        palette=Palette(
            background="FFFFFF",
            surface="F4F6F9",
            primary="0F2742",   # deep navy
            secondary="5B6B7C",  # slate grey
            accent="2F9E8F",     # teal
            accent_soft="E3F1EF",
            text="1F2933",
            text_inverse="FFFFFF",
        ),
        fonts=Fonts(heading="Segoe UI Semibold", body="Segoe UI", mono="Consolas"),
    )
)

MIDNIGHT = _register(
    Theme(
        name="midnight",
        aliases=("dark",),
        palette=Palette(
            background="0B1220",
            surface="16203A",
            primary="FFFFFF",
            secondary="9FB0C3",
            accent="6EA8FE",
            accent_soft="1E2B4A",
            text="E6EDF5",
            text_inverse="0B1220",
        ),
        fonts=Fonts(heading="Segoe UI Semibold", body="Segoe UI", mono="Consolas"),
    )
)

SLATE = _register(
    Theme(
        name="slate",
        aliases=("warm", "graphite"),
        palette=Palette(
            background="FCFBF9",
            surface="F1EEE9",
            primary="22303C",
            secondary="6B6256",
            accent="C2733A",     # warm amber
            accent_soft="F6E7D8",
            text="2B2B2B",
            text_inverse="FFFFFF",
        ),
        fonts=Fonts(heading="Georgia", body="Calibri", mono="Consolas"),
    )
)


def get_theme(name: str | None) -> Theme:
    """Return a theme by name or alias, defaulting to ``executive``.

    Raises:
        KeyError: if a non-empty name is given that does not match any theme.
    """

    if not name:
        return EXECUTIVE
    key = name.strip().lower()
    if key not in _THEMES:
        available = ", ".join(sorted({t.name for t in _THEMES.values()}))
        raise KeyError(f"Unknown theme '{name}'. Available themes: {available}")
    return _THEMES[key]


def available_themes() -> list[str]:
    return sorted({t.name for t in _THEMES.values()})
