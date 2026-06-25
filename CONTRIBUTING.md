# Contributing

Thanks for your interest in improving **md2pptx**!

## Getting set up

```bash
git clone https://github.com/VikrantSingh01/md2pptx
cd md2pptx
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Before you open a PR

- `ruff check src tests` - lint must pass.
- `pytest -q` - all tests must pass.
- Add or update tests for any behaviour change.
- Keep the parser free of `python-pptx` imports (see
  [docs/architecture.md](docs/architecture.md)).

## Conventions

- Python 3.9+; `from __future__ import annotations` at the top of modules.
- Small, focused functions; comment only what genuinely needs explaining.
- New visual features should be demonstrated in `examples/leadership-demo.md`.

## Adding a theme

Register a `Theme` in `src/md2pptx/themes.py`:

```python
MY_THEME = _register(Theme(
    name="my-theme",
    palette=Palette(...),
    fonts=Fonts(heading="...", body="...", mono="Consolas"),
))
```

Then it's instantly available via `--theme my-theme`.

## Reporting bugs

Open an issue with a minimal `.md` that reproduces the problem and what you
expected the slide to look like.
