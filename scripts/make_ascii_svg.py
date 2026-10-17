"""Turn an image (the Grafikcem logo, or later a portrait) into a self-typing ASCII SVG.

Usage: python scripts/make_ascii_svg.py [image] [--cols 54] [--out grafikcem-ascii.svg]
Needs Pillow; runs locally only (the daily workflow never calls it).
"""
import argparse
import os
import sys

from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
from brand import GRAPHITE, LINE, MONO, MUTED, PAPER, RED, esc  # noqa: E402

RAMP = " .:-=+*#%@"  # bright (sparse) -> dark (dense)
CHAR_W = 6.6
CHAR_H = 12.0
PAD_X = 22
PAD_TOP = 46
PAD_BOTTOM = 22


def load_grid(path, cols):
    image = Image.open(path).convert("RGBA")
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(white, image).convert("L")
    # Crop to the ink so the art fills the grid.
    box = ImageOps.invert(gray).getbbox()
    if box:
        margin = int(max(gray.size) * 0.02)
        box = (max(box[0] - margin, 0), max(box[1] - margin, 0),
               min(box[2] + margin, gray.width), min(box[3] + margin, gray.height))
        gray = gray.crop(box)
    rows = max(1, round(cols * gray.height / gray.width * (CHAR_W / CHAR_H)))
    small = gray.resize((cols, rows), Image.LANCZOS)
    grid = []
    for y in range(rows):
        line = []
        for x in range(cols):
            darkness = 1 - small.getpixel((x, y)) / 255
            line.append(RAMP[min(len(RAMP) - 1, int(darkness * len(RAMP)))])
        grid.append("".join(line).rstrip())
    return grid, gray.size


def accent_cells(grid, size, box):
    """Cells inside a normalized box (x0, y0, x1, y1 in 0..1) get the accent colour."""
    if not box:
        return set()
    rows = len(grid)
    cols = max(len(r) for r in grid)
    x0, y0, x1, y1 = box
    return {
        (x, y)
        for y in range(rows)
        for x in range(cols)
        if x0 <= (x + 0.5) / cols <= x1 and y0 <= (y + 0.5) / rows <= y1
    }


def build_svg(grid, accent, title):
    cols = max(len(r) for r in grid)
    width = round(PAD_X * 2 + cols * CHAR_W)
    height = round(PAD_TOP + len(grid) * CHAR_H + PAD_BOTTOM)
    row_delay = 0.045
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        "<style>",
        f".t{{font-family:{MONO};font-size:11px;fill:{PAPER};white-space:pre}}",
        f".a{{fill:{RED}}}",
        f".h{{font-family:{MONO};font-size:11px;fill:{MUTED}}}",
        "@keyframes wipe{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
        ".row{transform-origin:left center;transform:scaleX(0);"
        "animation:wipe .32s steps(18,end) forwards}",
        ".cur{animation:blink 1s step-end infinite}",
        "@media (prefers-reduced-motion:reduce){.row{animation:none;transform:none}}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="10" fill="{GRAPHITE}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{LINE}"/>',
        f'<circle cx="20" cy="18" r="5" fill="{RED}"/><circle cx="36" cy="18" r="5" fill="{LINE}"/>'
        f'<circle cx="52" cy="18" r="5" fill="{LINE}"/>',
        f'<text x="{width / 2:.0f}" y="22" text-anchor="middle" class="h">{esc(title)}</text>',
    ]
    for y, line in enumerate(grid):
        if not line.strip():
            continue
        baseline = PAD_TOP + (y + 1) * CHAR_H - 2
        spans = []
        current_accent = None
        buf = ""
        for x, ch in enumerate(line):
            is_accent = (x, y) in accent and ch != " "
            if is_accent != current_accent and buf:
                spans.append((current_accent, buf))
                buf = ""
            current_accent = is_accent
            buf += ch
        if buf:
            spans.append((current_accent, buf))
        tspans = "".join(
            f'<tspan class="a">{esc(t)}</tspan>' if a else esc(t) for a, t in spans
        )
        delay = y * row_delay
        parts.append(
            f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD_X}" y="{baseline:.1f}" class="t" xml:space="preserve">{tspans}</text></g>'
        )
    last = len(grid)
    cursor_y = PAD_TOP + last * CHAR_H + 4
    parts.append(
        f'<rect class="cur" x="{PAD_X}" y="{cursor_y - 10:.1f}" width="7" height="12" fill="{RED}" '
        f'style="animation-delay:{last * row_delay:.2f}s"/>'
    )
    parts.append("</svg>")
    return "\n".join(parts), width, height


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", default=os.path.join(here, "kaynak", "grafikcem-logo.png"))
    parser.add_argument("--cols", type=int, default=54)
    parser.add_argument("--out", default=os.path.join(here, "grafikcem-ascii.svg"))
    parser.add_argument("--title", default="grafikcem.txt")
    # The sparkle above the dotted İ in the logo, as a fraction of the cropped image.
    parser.add_argument("--accent", default="0.34,0.28,0.43,0.36")
    args = parser.parse_args()
    grid, size = load_grid(args.image, args.cols)
    box = tuple(float(v) for v in args.accent.split(",")) if args.accent else None
    svg, width, height = build_svg(grid, accent_cells(grid, size, box), args.title)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"{args.out} {width}x{height}, {len(grid)} rows")


if __name__ == "__main__":
    main()
