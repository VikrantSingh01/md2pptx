"""Tests for the Markdown → IR parser."""

from __future__ import annotations

from md2pptx.model import SlideKind
from md2pptx.parser import parse_markdown


def test_front_matter_metadata():
    deck = parse_markdown(
        """---
title: My Deck
author: Ada Lovelace
theme: midnight
footer: Confidential
---

# My Deck
## A subtitle
"""
    )
    assert deck.title == "My Deck"
    assert deck.author == "Ada Lovelace"
    assert deck.theme == "midnight"
    assert deck.footer == "Confidential"


def test_slides_split_on_rule():
    deck = parse_markdown("# A\n\n---\n\n## B\n\n---\n\n## C")
    assert len(deck.slides) == 3
    assert deck.slides[0].kind == SlideKind.TITLE
    assert [s.title for s in deck.slides] == ["A", "B", "C"]


def test_horizontal_rule_inside_code_is_not_a_split():
    md = "## Code\n\n```\nline1\n---\nline2\n```\n"
    deck = parse_markdown(md)
    assert len(deck.slides) == 1
    assert "---" in deck.slides[0].code.code


def test_bullets_with_nesting_and_ordering():
    deck = parse_markdown("## List\n\n- a\n  - b\n- c\n1. first\n2. second")
    bullets = deck.slides[0].bullets
    assert bullets[0].text == "a" and bullets[0].level == 0
    assert bullets[1].text == "b" and bullets[1].level == 1
    assert bullets[3].ordered is True


def test_table_parsing():
    md = "## T\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |"
    table = parse_markdown(md).slides[0].table
    assert table.headers == ["A", "B"]
    assert table.rows == [["1", "2"], ["3", "4"]]


def test_quote_slide_detection():
    md = "## Q\n\n> Stay hungry\n> - Steve"
    slide = parse_markdown("---\ntheme: executive\n---\n\n# Title\n\n---\n\n" + md).slides[1]
    assert slide.kind == SlideKind.QUOTE
    assert slide.quote.text == "Stay hungry"
    assert slide.quote.attribution == "Steve"


def test_section_directive():
    deck = parse_markdown("# T\n\n---\n\n<!-- class: section -->\n\nPart One")
    assert deck.slides[1].kind == SlideKind.SECTION
    assert deck.slides[1].title == "Part One"


def test_two_columns():
    md = (
        "## Two\n\n:::columns\n- left 1\n- left 2\n+++\n- right 1\n:::\n"
    )
    slide = parse_markdown(md).slides[0]
    assert slide.kind == SlideKind.TWO_COLUMN
    assert len(slide.columns) == 2
    assert slide.columns[0].bullets[0].text == "left 1"
    assert slide.columns[1].bullets[0].text == "right 1"


def test_speaker_notes_block():
    md = "## S\n\n- point\n\nNotes:\nThis is a note.\nSecond line."
    slide = parse_markdown(md).slides[0]
    assert "This is a note." in slide.notes
    assert "Second line." in slide.notes


def test_closing_directive():
    deck = parse_markdown("# T\n\n---\n\n<!-- class: closing -->\n\n# Thanks")
    assert deck.slides[1].kind == SlideKind.CLOSING


def test_empty_slides_are_skipped():
    deck = parse_markdown("# T\n\n---\n\n\n\n---\n\n## Real")
    assert [s.title for s in deck.slides] == ["T", "Real"]
