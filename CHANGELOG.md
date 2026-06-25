# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-25

### Added
- Markdown → native `.pptx` conversion via `python-pptx`.
- YAML-style front matter for deck metadata and theme selection.
- Slide kinds: title, section, content, two-column, image, quote, closing.
- Markdown support: headings, nested/ordered bullets, tables, fenced code,
  block quotes, images, inline bold/italic/code/links.
- Speaker notes via a `Notes:` block or `<!-- notes: ... -->`.
- Three professional themes: `executive` (default), `midnight`, `slate`.
- CLI (`md2pptx`) with multi-file concatenation and theme override.
- Leadership demo deck, multi-file weekly-review demo, and a reproducible
  architecture-diagram generator.
- Test suite (parser, inline, themes, end-to-end render) and GitHub Actions CI.
