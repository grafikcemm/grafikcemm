"""Render data/contributions.json as an animated 53-week heatmap in Grafikcem red.

Usage: python scripts/render_heatmap_svg.py [--out contrib-heatmap.svg]
"""
import argparse
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from brand import GRAPHITE, LINE, MONO, MUTED, PAPER, RED, esc  # noqa: E402

PALETTE = [LINE, "#4a1a1e", "#7a1420", "#a70f20", "#d4142a", RED]
CELL = 11
GAP = 3
LEFT = 44
TOP = 66
WIDTH = 860
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level(count, top):
    if count <= 0:
        return 0
    if top <= 4:
        return min(5, count + 1)
    for i, threshold in enumerate((0.1, 0.25, 0.45, 0.7), start=1):
        if count <= top * threshold:
            return i
    return 5


def build(data):
    days = data["days"][-371:]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    top = max((d["count"] for d in days), default=0)
    cols = (offset + len(days) + 6) // 7
    grid_w = cols * (CELL + GAP)
    left = max(LEFT, (WIDTH - grid_w) // 2)
    height = TOP + 7 * (CELL + GAP) + 64
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{data["total"]} contributions in the last year">',
        "<style>",
        f".m{{font-family:{MONO};font-size:10px;fill:{MUTED}}}",
        f".s{{font-family:{MONO};font-size:12px;fill:{PAPER}}}",
        f".n{{font-family:{MONO};font-size:12px;fill:{RED};font-weight:700}}",
        "@keyframes drop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}",
        ".c{opacity:0;animation:drop .3s ease-out forwards}",
        "@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}}",
        "</style>",
        f'<rect width="{WIDTH}" height="{height}" rx="10" fill="{GRAPHITE}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="none" stroke="{LINE}"/>',
        f'<circle cx="20" cy="18" r="5" fill="{RED}"/><circle cx="36" cy="18" r="5" fill="{LINE}"/>'
        f'<circle cx="52" cy="18" r="5" fill="{LINE}"/>',
        f'<text x="{WIDTH / 2:.0f}" y="22" text-anchor="middle" class="m">contributions.sh</text>',
    ]
    last_month = None
    for i, day in enumerate(days):
        idx = i + offset
        col, row = divmod(idx, 7)
        d = date.fromisoformat(day["date"])
        if row == 0 or i == 0:
            if d.month != last_month and col < cols - 1:
                parts.append(f'<text x="{left + col * (CELL + GAP)}" y="{TOP - 10}" class="m">{MONTHS[d.month - 1]}</text>')
                last_month = d.month
        x = left + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        delay = (col + row) * 0.012
        fill = PALETTE[level(day["count"], top)]
        parts.append(
            f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{CELL}" '
            f'height="{CELL}" rx="2.5" fill="{fill}"><title>{esc(day["date"])}: {day["count"]}</title></rect>'
        )
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{left - 30}" y="{TOP + row * (CELL + GAP) + 9}" class="m">{label}</text>')
    fy = TOP + 7 * (CELL + GAP) + 30
    parts.append(
        f'<text x="{left}" y="{fy}" class="s"><tspan class="n">{data["total"]:,}</tspan> contributions in the last year'
        f'  ·  longest streak <tspan class="n">{data["longest_streak"]}</tspan> days'
        f'  ·  current <tspan class="n">{data["current_streak"]}</tspan></text>'
    )
    lx = left + grid_w - 6 * (CELL + GAP) - 64
    parts.append(f'<text x="{lx}" y="{fy + 22}" class="m">Less</text>')
    for i, colour in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + 32 + i * (CELL + GAP)}" y="{fy + 13}" width="{CELL}" height="{CELL}" rx="2.5" fill="{colour}"/>'
        )
    parts.append(f'<text x="{lx + 36 + 6 * (CELL + GAP)}" y="{fy + 22}" class="m">More</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=os.path.join(here, "data", "contributions.json"))
    parser.add_argument("--out", default=os.path.join(here, "contrib-heatmap.svg"))
    args = parser.parse_args()
    with open(args.data, encoding="utf-8") as handle:
        data = json.load(handle)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(build(data))
    print(f"{args.out}: {data['total']} contributions")


if __name__ == "__main__":
    main()
