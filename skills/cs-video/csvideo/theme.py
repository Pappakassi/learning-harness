"""Shared look for every video: colors, fonts, sizes and screen zones.

Change things here, not inside scenes, so all videos stay consistent.
"""
from manim import ManimColor

# Colors (dark background, high-contrast accents)
BG = ManimColor("#0F1117")
FG = ManimColor("#E8EAF0")        # main text
MUTED = ManimColor("#7A8194")     # secondary text, dimmed cells
FAINT = ManimColor("#2A2F3D")     # panel backgrounds, cell fill
BLUE = ManimColor("#5B9CFF")      # pointer "lo", primary accent
ORANGE = ManimColor("#FF9F43")    # pointer "hi", secondary accent
YELLOW = ManimColor("#FFD93D")    # pointer "mid", the thing being looked at
GREEN = ManimColor("#4ADE80")     # success / found
RED = ManimColor("#F87171")       # discarded / wrong
PURPLE = ManimColor("#B794F6")    # extra accent

# Fonts (falls back to Manim's default if not installed)
BODY_FONT = "Inter"
CODE_FONT = "DejaVu Sans Mono"

# Text sizes
TITLE_SIZE = 44
HEADING_SIZE = 34
BODY_SIZE = 28
SMALL_SIZE = 22
CAPTION_SIZE = 24
CODE_SIZE = 22

# Screen zones (Manim frame is 14.22 wide x 8 tall, centered on 0,0)
FRAME_W = 14.22
FRAME_H = 8.0
SAFE_MARGIN = 0.35          # keep everything this far from the edge
TITLE_Y = 3.3               # where scene titles sit
CAPTION_TOP = -2.9          # captions live below this line; content stays above
CONTENT_TOP = 2.75          # content stays below this line when a title is shown
CONTENT_BOTTOM = -2.5       # content stays above this line (room for a 2-line caption)
CONTENT_H = CONTENT_TOP - CONTENT_BOTTOM
CONTENT_MID_Y = (CONTENT_TOP + CONTENT_BOTTOM) / 2

# Colourful extras
CYAN = ManimColor("#22D3EE")
PINK = ManimColor("#F472B6")
LIME = ManimColor("#A3E635")
CORAL = ManimColor("#FB7185")
# rotating palette for "one colour per thing" (receivers, hosts, series)
PALETTE = [CYAN, PINK, LIME, ORANGE, PURPLE, YELLOW, BLUE, CORAL]
TITLE_GRADIENT = [CYAN, BLUE, PURPLE, PINK]
# backdrop: vertical gradient + soft coloured glows
BG_TOP = ManimColor("#121A3A")
BG_BOTTOM = ManimColor("#1B0F2E")
BLOBS = [((-5.5, 2.5), CYAN, 3.2), ((5.8, -2.2), PINK, 3.4), ((1.5, 3.4), PURPLE, 2.6)]
COLORFUL = True     # set False for the plain dark style
