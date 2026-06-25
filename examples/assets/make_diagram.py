"""Generate the architecture diagram used by the demo deck.

Run with:  python examples/assets/make_diagram.py
Produces:  examples/assets/architecture.png

Kept as code (not just a binary blob) so the demo asset is reproducible and reviewable.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
BG = (255, 255, 255)
NAVY = (15, 39, 66)
TEAL = (47, 158, 143)
SLATE = (91, 107, 124)
SOFT = (227, 241, 239)
INK = (31, 41, 51)


def _font(size: int, bold: bool = False):
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Helvetica.ttc"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _centered(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2 - tb[1]), text, font=font, fill=fill)


def _rounded(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_f = _font(46, bold=True)
    label_f = _font(30, bold=True)
    small_f = _font(24)

    d.text((80, 50), "Cell-based architecture", font=title_f, fill=NAVY)
    d.line((80, 120, 1520, 120), fill=TEAL, width=5)

    # Global router
    _rounded(d, (80, 170, 1520, 270), 18, NAVY)
    _centered(d, (80, 170, 1520, 270), "Global Router  —  deterministic user -> cell mapping",
              label_f, (255, 255, 255))

    # Cells
    cells = ["Cell 1", "Cell 2", "Cell 3", "Cell N"]
    gap = 40
    cw = (1440 - gap * (len(cells) - 1)) / len(cells)
    x = 80
    for name in cells:
        box = (x, 340, x + cw, 660)
        _rounded(d, box, 18, SOFT, outline=TEAL, width=3)
        _centered(d, (x, 360, x + cw, 410), name, label_f, NAVY)
        for j, svc in enumerate(("API", "Workers", "Data store")):
            sb = (x + 24, 430 + j * 70, x + cw - 24, 430 + j * 70 + 54)
            _rounded(d, sb, 10, (255, 255, 255), outline=SLATE, width=2)
            _centered(d, sb, svc, small_f, INK)
        cx = x + cw / 2
        d.line((cx, 270, cx, 340), fill=SLATE, width=3)
        x += cw + gap

    _centered(d, (80, 720, 1520, 780),
              "Each cell is fully isolated - a bad deploy can affect only one cell.",
              small_f, SLATE)

    out = Path(__file__).resolve().parent / "architecture.png"
    img.save(out, "PNG")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
