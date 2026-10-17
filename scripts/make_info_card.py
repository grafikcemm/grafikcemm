"""Neofetch-style info card. Edit ROWS when your details change, then re-run.

Usage: python scripts/make_info_card.py [--out info-card.svg]   (STATIC=1 for a frozen frame)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from brand import GRAPHITE, LINE, MONO, MUTED, PAPER, RED, esc  # noqa: E402

TITLE = "grafikcem@github"
ROWS = [
    ("Name", "Ali Cem Bozma"),
    ("Role", "Graphic designer · AI-driven creative"),
    ("Base", "İstanbul, Türkiye"),
    ("Exp", "6+ years in design & social media"),
    ("", ""),
    ("Now", "GrafikcemOS · my local AI agent system"),
    ("Build", "Dijital Beyin · open-source AI memory"),
    ("Video", "YouTube @grafikcem · AI in real design work"),
    ("Social", "Instagram @grafikcem · 100K+"),
    ("", ""),
    ("Design", "Figma · Adobe · Midjourney · Nano Banana"),
    ("Agents", "Claude Code · Codex · ChatGPT"),
    ("Code", "Node.js · Next.js · TypeScript"),
    ("", ""),
    ("Web", "grafikcem.com"),
]
WIDTH = 520
ROW_H = 21
PAD_X = 24
TOP = 70


def build(static=False):
    height = TOP + len(ROWS) * ROW_H + 50
    css = [
        f".k{{font-family:{MONO};font-size:13px;fill:{RED};font-weight:600}}",
        f".v{{font-family:{MONO};font-size:13px;fill:{PAPER}}}",
        f".h{{font-family:{MONO};font-size:14px;fill:{PAPER};font-weight:700}}",
        f".m{{font-family:{MONO};font-size:11px;fill:{MUTED}}}",
    ]
    if not static:
        css += [
            "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}",
            ".r{opacity:0;animation:in .35s ease-out forwards}",
            "@media (prefers-reduced-motion:reduce){.r{animation:none;opacity:1}}",
        ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Ali Cem Bozma — Grafikcem">',
        f"<style>{''.join(css)}</style>",
        f'<rect width="{WIDTH}" height="{height}" rx="10" fill="{GRAPHITE}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="none" stroke="{LINE}"/>',
        f'<circle cx="20" cy="18" r="5" fill="{RED}"/><circle cx="36" cy="18" r="5" fill="{LINE}"/>'
        f'<circle cx="52" cy="18" r="5" fill="{LINE}"/>',
        f'<text x="{WIDTH / 2:.0f}" y="22" text-anchor="middle" class="m">neofetch</text>',
        f'<text x="{PAD_X}" y="54" class="h"><tspan fill="{RED}">grafikcem</tspan>@github</text>',
        f'<line x1="{PAD_X}" y1="{TOP - 6}" x2="{PAD_X + 150}" y2="{TOP - 6}" stroke="{LINE}" stroke-width="2"/>',
    ]
    shown = 0
    for i, (key, value) in enumerate(ROWS):
        if not key:
            continue
        y = TOP + 14 + i * ROW_H
        delay = 0.6 + shown * 0.09
        shown += 1
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        parts.append(
            f'<g class="r"{style}><text x="{PAD_X}" y="{y}" class="k">{esc(key)}</text>'
            f'<text x="{PAD_X + 76}" y="{y}" class="v">{esc(value)}</text></g>'
        )
    # Colour swatches, like neofetch's palette row.
    sy = height - 30
    swatches = [GRAPHITE, LINE, MUTED, PAPER, RED, "#a70f20"]
    for i, colour in enumerate(swatches):
        delay = 0.6 + shown * 0.09 + i * 0.05
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        parts.append(
            f'<rect class="r"{style} x="{PAD_X + i * 26}" y="{sy}" width="22" height="12" rx="2" '
            f'fill="{colour}" stroke="{LINE}"/>'
        )
    parts.append("</svg>")
    return "\n".join(parts), height


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(here, "info-card.svg"))
    args = parser.parse_args()
    svg, height = build(static=os.environ.get("STATIC") == "1")
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"{args.out} {WIDTH}x{height}")


if __name__ == "__main__":
    main()
