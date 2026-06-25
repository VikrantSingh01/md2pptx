"""Tests for inline run parsing and themes."""

from __future__ import annotations

import pytest

from md2pptx.inline import parse_inline
from md2pptx.themes import available_themes, get_theme


def test_plain_text_single_run():
    runs = parse_inline("hello world")
    assert len(runs) == 1
    assert runs[0].text == "hello world"
    assert not runs[0].bold


def test_bold_and_italic_and_code():
    runs = parse_inline("a **b** c *d* `e`")
    rendered = [(r.text, r.bold, r.italic, r.code) for r in runs]
    assert ("b", True, False, False) in rendered
    assert ("d", False, True, False) in rendered
    assert ("e", False, False, True) in rendered


def test_link_renders_label_only():
    runs = parse_inline("see [docs](https://example.com)")
    assert any(r.text == "docs" for r in runs)
    assert all("http" not in r.text for r in runs)


def test_get_theme_aliases():
    assert get_theme("navy").name == "executive"
    assert get_theme("dark").name == "midnight"
    assert get_theme(None).name == "executive"


def test_unknown_theme_raises():
    with pytest.raises(KeyError):
        get_theme("rainbow-unicorn")


def test_available_themes_unique_sorted():
    themes = available_themes()
    assert themes == sorted(themes)
    assert "executive" in themes
    assert len(themes) == len(set(themes))
