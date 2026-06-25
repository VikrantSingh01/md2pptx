"""Command-line interface for md2pptx."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .builder import build
from .themes import available_themes


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2pptx",
        description="Convert Markdown into a leadership-grade PowerPoint (.pptx).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  md2pptx deck.md\n"
            "  md2pptx intro.md body.md closing.md -o quarterly.pptx\n"
            "  md2pptx deck.md --theme midnight -o dark.pptx\n"
        ),
    )
    parser.add_argument("inputs", nargs="+", help="One or more Markdown files.")
    parser.add_argument(
        "-o", "--output", help="Output .pptx path (default: <first input>.pptx)."
    )
    parser.add_argument(
        "-t", "--theme", choices=available_themes(),
        help="Override the theme (front-matter 'theme' is used otherwise).",
    )
    parser.add_argument(
        "--themes", action="store_true", help="List available themes and exit."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output.")
    parser.add_argument("-V", "--version", action="version",
                        version=f"md2pptx {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.themes:
        print("Available themes:")
        for name in available_themes():
            print(f"  • {name}")
        return 0

    for path in args.inputs:
        if not Path(path).is_file():
            parser.error(f"input file not found: {path}")

    output = args.output or str(Path(args.inputs[0]).with_suffix(".pptx"))

    try:
        deck = build(args.inputs, output, theme=args.theme)
    except KeyError as exc:  # unknown theme
        parser.error(str(exc).strip('"'))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"✓ {len(deck.slides)} slides · theme '{deck.theme}' → {output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
