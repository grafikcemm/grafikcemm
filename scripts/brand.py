"""Shared brand tokens (from grafikcem.com) for every generated SVG."""

GRAPHITE = "#121314"   # background
PANEL = "#1b1c1e"      # card / title bar
LINE = "#2a2b2e"       # hairlines, empty heatmap cells
PAPER = "#f5f3ef"      # main text
MUTED = "#9a978f"      # secondary text
RED = "#f51b2b"        # signal red accent
RED_DEEP = "#a70f20"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
