# Architecture

`md2pptx` is built as a small pipeline with a clean separation between *parsing*
and *rendering*. The intermediate representation (IR) is the contract between
the two halves.

```
            ┌────────────┐      ┌──────────────┐      ┌─────────────┐
 Markdown ─▶│  parser.py │ ───▶ │  Deck (IR)   │ ───▶ │ renderer.py │ ─▶ .pptx
            │ inline.py  │      │  model.py    │      │ themes.py   │
            └────────────┘      └──────────────┘      └─────────────┘
```

## Modules

| Module | Responsibility |
| --- | --- |
| `model.py` | Plain dataclasses: `Deck`, `Slide`, `Bullet`, `TableBlock`, … No `python-pptx` types. |
| `parser.py` | Line-oriented Markdown + front-matter parser → `Deck`. Zero third-party deps. |
| `inline.py` | Splits a line into styled runs (`**bold**`, `*italic*`, `` `code` ``, links). |
| `themes.py` | Data-only `Theme`/`Palette`/`Fonts` registry with aliases. |
| `renderer.py` | Turns a `Deck` into hand-placed PowerPoint shapes via `python-pptx`. |
| `builder.py` | Orchestration: parse file(s) → render → save. |
| `cli.py` | `argparse` front end (`md2pptx …`). |

## Why an IR?

Keeping a `python-pptx`-free IR in the middle buys three things:

1. **Testability** — the parser is pure data-in/data-out, so its tests need no
   PowerPoint at all and run in milliseconds.
2. **Restyleability** — all visual decisions live in `renderer.py` + `themes.py`.
   You can completely change the look without touching parsing.
3. **Reuse** — the same IR could feed a different backend (HTML, PDF) later.

## Slide classification

The parser assigns each slide a `SlideKind` (`title`, `section`, `content`,
`two_column`, `image`, `quote`, `closing`). Explicit `<!-- class: … -->`
directives win; otherwise the kind is inferred from the slide's contents
(e.g. a lone block quote → `quote`, a first heading-only slide → `title`).

## Rendering approach

The renderer drives every slide from the **blank** layout and positions shapes
by hand (titles, accent bars, footers, tables, code panels, images). This is
more code than relying on placeholders, but it is the only way to get
consistent, leadership-grade spacing and typography across themes.

## Extending

- **New theme** — add a `Theme` in `themes.py` via `_register(...)`.
- **New block type** — add a dataclass to `model.py`, parse it in `parser.py`,
  and render it in `renderer.py`. The three changes are independent and small.
