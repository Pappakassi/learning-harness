"""Reusable, tested building blocks for CS explainer scenes.

Each template is a Manim VGroup you can position like any mobject, and
its methods RETURN animations (you pass them to self.play), so they
compose with everything else in a scene.

    arr = ArrayView([3, 8, 12, 17])
    ptr = Pointers(arr, {"lo": 0, "hi": 3})
    self.play(FadeIn(arr), FadeIn(ptr))
    self.play(ptr.move(lo=2), arr.set_active_range(2, 3))
"""
from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, logger, AnimationGroup, Arrow, FadeIn, FadeOut, Line,
                   Polygon,
                   Rectangle, RoundedRectangle, Square, Text, Transform, VGroup)

from . import theme as T


def _txt(s, size, color=T.FG, font=T.BODY_FONT, **kw):
    return Text(str(s), font_size=size, color=color, font=font, **kw)


# --------------------------------------------------------------------------
# ArrayView
# --------------------------------------------------------------------------
class ArrayView(VGroup):
    """A row of boxed values with optional index labels underneath."""

    def __init__(self, values, cell_size: float = 0.85, max_width: float = 12.0,
                 show_indices: bool = True, value_size: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "ArrayView"
        self.values = list(values)
        n = len(self.values)
        cell_size = min(cell_size, max_width / max(n, 1))
        self.cell_size = cell_size
        self.boxes = VGroup()
        self.labels = VGroup()
        for i, v in enumerate(self.values):
            box = Square(side_length=cell_size, stroke_color=T.MUTED, stroke_width=2.5,
                         fill_color=T.FAINT, fill_opacity=1)
            box.move_to(RIGHT * i * cell_size)
            lab = _txt(v, value_size * cell_size / 0.85, color=T.FG)
            if lab.width > cell_size * 0.8:
                lab.scale_to_fit_width(cell_size * 0.8)
            lab.move_to(box)
            self.boxes.add(box)
            self.labels.add(lab)
        self.add(self.boxes, self.labels)
        self.indices = VGroup()
        if show_indices:
            for i, box in enumerate(self.boxes):
                idx = _txt(i, T.SMALL_SIZE * min(1, cell_size / 0.85), color=T.MUTED)
                idx.next_to(box, DOWN, buff=0.12)
                self.indices.add(idx)
            self.add(self.indices)
        self.move_to([0, 0, 0])

    def __len__(self):
        return len(self.values)

    def cell(self, i: int) -> VGroup:
        return VGroup(self.boxes[i], self.labels[i])

    def anchor_below(self, i: int):
        """Point just under cell i (under its index label if shown)."""
        ref = self.indices[i] if len(self.indices) else self.boxes[i]
        return ref.get_bottom() + DOWN * 0.08

    def anchor_above(self, i: int):
        return self.boxes[i].get_top() + UP * 0.08

    # ---- animations ----
    def highlight(self, i: int, color=T.YELLOW):
        return AnimationGroup(
            self.boxes[i].animate.set_stroke(color=color, width=5),
            self.labels[i].animate.set_color(color))

    def unhighlight(self, i: int):
        return AnimationGroup(
            self.boxes[i].animate.set_stroke(color=T.MUTED, width=2.5),
            self.labels[i].animate.set_color(T.FG))

    def mark(self, i: int, color=T.GREEN):
        """Fill a cell solidly, e.g. 'found'."""
        return AnimationGroup(
            self.boxes[i].animate.set_fill(color=color, opacity=0.9).set_stroke(color=color, width=5),
            self.labels[i].animate.set_color(T.BG))

    def set_active_range(self, lo: int, hi: int, reset_outside: bool = True):
        """Dim every cell outside [lo, hi]; undim the ones inside.

        Cells outside also lose any highlight outline (reset_outside=True), so
        don't combine this with unhighlight() on the same cell in one play() --
        two animations on one mobject in the same play() fight each other.
        """
        anims = []
        for i in range(len(self)):
            inside = lo <= i <= hi
            op = 1.0 if inside else 0.22
            box_anim = self.boxes[i].animate.set_opacity(op)
            if not inside and reset_outside:
                box_anim = box_anim.set_stroke(color=T.MUTED, width=2.5)
            anims.append(box_anim)
            anims.append(self.labels[i].animate.set_opacity(op))
            if len(self.indices):
                anims.append(self.indices[i].animate.set_opacity(op))
        return AnimationGroup(*anims)


# --------------------------------------------------------------------------
# Pointers
# --------------------------------------------------------------------------
class Pointers(VGroup):
    """Named index pointers (lo / mid / hi, i / j, ...) under or over an ArrayView.

    Pointers that land on the same index share one arrow and their names are
    stacked, so labels never overlap. Set a pointer to None to hide it.
    """

    DEFAULT_COLORS = {"lo": T.BLUE, "hi": T.ORANGE, "mid": T.YELLOW,
                      "i": T.BLUE, "j": T.ORANGE, "k": T.PURPLE}

    def __init__(self, array: ArrayView, positions: dict, colors: dict | None = None,
                 side: str = "down", arrow_len: float = 0.55, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Pointers"
        self.array = array
        self.colors = {**self.DEFAULT_COLORS, **(colors or {})}
        self.side = side
        self.arrow_len = arrow_len
        self.order = list(positions.keys())
        self.positions = dict(positions)
        self.add(*self._build(self.positions).submobjects)

    def _build(self, positions: dict) -> VGroup:
        out = VGroup()
        by_index: dict[int, list[str]] = {}
        for name in self.order:
            idx = positions.get(name)
            if idx is not None:
                by_index.setdefault(idx, []).append(name)
        size = T.SMALL_SIZE + 2
        for idx, names in sorted(by_index.items()):
            color = self.colors.get(names[0], T.FG)
            if self.side == "down":
                tip = self.array.anchor_below(idx)
                arrow = Arrow(tip + DOWN * self.arrow_len, tip, buff=0, color=color,
                              stroke_width=5, max_tip_length_to_length_ratio=0.35)
            else:
                tip = self.array.anchor_above(idx)
                arrow = Arrow(tip + UP * self.arrow_len, tip, buff=0, color=color,
                              stroke_width=5, max_tip_length_to_length_ratio=0.35)
            labels = VGroup(*[_txt(n, size, color=self.colors.get(n, T.FG), weight="BOLD")
                              for n in names]).arrange(DOWN, buff=0.08)
            if self.side == "down":
                labels.next_to(arrow, DOWN, buff=0.08)
            else:
                labels.next_to(arrow, UP, buff=0.08)
            out.add(VGroup(arrow, labels))
        return out

    def move(self, **changes):
        """Animate pointers to new indices, e.g. ptr.move(lo=5, mid=None)."""
        self.positions.update(changes)
        for k in changes:
            if k not in self.order:
                self.order.append(k)
        target = self._build(self.positions)
        return Transform(self, target)


# --------------------------------------------------------------------------
# CodePanel
# --------------------------------------------------------------------------
KEYWORDS = ["def", "while", "elif", "if", "else", "return", "for", "in", "and", "or", "not"]


class CodePanel(VGroup):
    """Monospaced code on a panel, with a movable line highlight.

    Indentation is preserved. Keywords get a color. Lines are 0-indexed.
    """

    def __init__(self, code: str, size: int = T.CODE_SIZE, max_width: float = 6.6,
                 max_height: float = T.CONTENT_H, title: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "CodePanel"
        raw = code.strip("\n").split("\n")
        char_w = Text("M" * 20, font=T.CODE_FONT, font_size=size).width / 20
        line_h = Text("Mg", font=T.CODE_FONT, font_size=size).height * 1.55
        self.lines = VGroup()
        for k, line in enumerate(raw):
            stripped = line.lstrip(" ")
            indent = len(line) - len(stripped)
            if stripped:
                # color the keyword that starts the line (def / while / if / return ...)
                first = stripped.split(" ")[0].rstrip(":")
                t2c = {f"[0:{len(first)}]": T.PURPLE} if first in KEYWORDS else {}
                mob = Text(stripped, font=T.CODE_FONT, font_size=size, color=T.FG, t2c=t2c)
            else:
                mob = Text(".", font=T.CODE_FONT, font_size=size).set_opacity(0)
            mob.move_to([0, -k * line_h, 0], aligned_edge=LEFT)
            mob.shift(RIGHT * (indent * char_w - mob.get_left()[0]))
            # put every line on the same baseline grid regardless of glyph height
            self.lines.add(mob)
        for k, mob in enumerate(self.lines):
            mob.set_y(-k * line_h, )
        self.line_h = line_h
        pad = 0.3
        w = self.lines.width + 2 * pad
        h = self.lines.height + 2 * pad
        self.panel = RoundedRectangle(corner_radius=0.15, width=w, height=h,
                                      fill_color=T.FAINT, fill_opacity=1, stroke_width=0)
        self.panel.move_to(self.lines)
        self.bar = Rectangle(width=w - 0.12, height=line_h * 0.92, fill_color=T.YELLOW,
                             fill_opacity=0, stroke_width=0)
        self.bar.move_to([self.panel.get_center()[0], self.lines[0].get_center()[1], 0])
        self.add(self.panel, self.bar, self.lines)
        if title:
            self.header = _txt(title, T.SMALL_SIZE, color=T.MUTED)
            self.header.next_to(self.panel, UP, buff=0.12, aligned_edge=LEFT)
            self.add(self.header)
        if self.width > max_width:
            self.scale_to_fit_width(max_width)
        if self.height > max_height:
            self.scale_to_fit_height(max_height)
        self.move_to([0, T.CONTENT_MID_Y, 0])
        self.current = None

    def highlight(self, k: int, color=T.YELLOW):
        """Move the highlight bar to line k (0-indexed)."""
        self.current = k
        y = self.lines[k].get_center()[1]
        return self.bar.animate.set_y(y).set_fill(color=color, opacity=0.22)

    def clear_highlight(self):
        self.current = None
        return self.bar.animate.set_fill(opacity=0)


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
class BulletList(VGroup):
    """Left-aligned bullet points. Reveal one at a time with .reveal(i)."""

    def __init__(self, items, size: int = T.BODY_SIZE, max_width: float = 11.0,
                 bullet_color=T.BLUE, spacing: float = 0.4, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "BulletList"
        for it in items:
            dot = _txt("•", size, color=bullet_color)
            txt = _txt(it, size)
            row = VGroup(dot, txt).arrange(RIGHT, buff=0.25)
            self.add(row)
        self.arrange(DOWN, buff=spacing, aligned_edge=LEFT)
        if self.width > max_width:
            self.scale_to_fit_width(max_width)
        for row in self:
            row.set_opacity(0)

    def reveal(self, i: int):
        return self[i].animate.set_opacity(1)


class Counter(VGroup):
    """'label: n' that animates to a new value, e.g. a step or comparison count."""

    def __init__(self, label: str, value=0, color=T.FG, size: int = T.BODY_SIZE,
                 fmt: str = "{}", **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Counter"
        self.label, self.color, self.size, self.fmt = label, color, size, fmt
        self.value = value
        self.add(*self._build(value).submobjects)

    def _build(self, value):
        g = VGroup(_txt(self.label + ":", self.size, color=T.MUTED),
                   _txt(self.fmt.format(value), self.size, color=self.color, weight="BOLD"))
        g.arrange(RIGHT, buff=0.2)
        if len(self.submobjects):
            g.move_to(self, aligned_edge=LEFT)
        return g

    def set(self, value):
        self.value = value
        return Transform(self, self._build(value))


class Card(VGroup):
    """A box with a bold heading and a short body, e.g. one option among several.

    Use "\\n" in body to break lines. Arrange several with VGroup(...).arrange(RIGHT).
    """

    def __init__(self, heading: str, body: str = "", color=T.BLUE, width: float = 4.0,
                 size: int = T.SMALL_SIZE + 2, min_height: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = f"Card {heading[:20]}"
        head = _txt(heading, size + 4, color=color, weight="BOLD")
        parts = [head]
        if body:
            parts.append(_txt(body, size, color=T.FG, line_spacing=0.9))
        content = VGroup(*parts).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        if content.width > width - 0.5:
            from .scene_base import report
            report(f"[Card '{heading}'] text was shrunk to fit; use a smaller size, "
                   f"a wider card or shorter lines so cards in a row match")
            content.scale_to_fit_width(width - 0.5)
        h = max(content.height + 0.6, min_height)
        box = RoundedRectangle(corner_radius=0.15, width=width, height=h,
                               stroke_color=color, stroke_width=3, fill_color=T.FAINT,
                               fill_opacity=1)
        content.move_to(box).align_to(box.get_top() + DOWN * 0.3, UP)
        self.box, self.heading = box, head
        self.add(box, content)


class Callout(VGroup):
    """A short statement in a colored box, for the key idea of a scene."""

    def __init__(self, text: str, color=T.BLUE, size: int = T.BODY_SIZE,
                 max_width: float = 11.0, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Callout"
        label = _txt(text, size)
        if label.width > max_width - 0.6:
            label.scale_to_fit_width(max_width - 0.6)
        box = RoundedRectangle(corner_radius=0.15, width=label.width + 0.6,
                               height=label.height + 0.45, stroke_color=color,
                               stroke_width=3, fill_color=T.FAINT, fill_opacity=1)
        label.move_to(box)
        self.add(box, label)


# --------------------------------------------------------------------------
# GridView: tables (distance vectors, routing tables, truth tables, DP tables)
# --------------------------------------------------------------------------
class GridView(VGroup):
    """A table of cells with optional row/column labels.

        g = GridView([[0, 4, 6], [5, 2, 0]], row_labels=["A", "C"], col_labels=["A", "B", "C"])
        self.play(g.highlight_col(2))
        self.play(TransformFromCopy(chip_number, g.target_text(1, 0, "7")))
        g.put(1, 0, that_text)          # after the animation: make it the cell's text

    Use "" for an empty cell. row_colors colours the row labels (and their stripe).
    """

    def __init__(self, values, row_labels=None, col_labels=None, cell_w: float = 0.72,
                 cell_h: float = 0.56, size: int = 26, row_colors=None,
                 label_size: int | None = None, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "GridView"
        self.n_rows, self.n_cols = len(values), len(values[0])
        self.cell_w, self.cell_h, self.size = cell_w, cell_h, size
        label_size = label_size or size - 2
        self.boxes = [[None] * self.n_cols for _ in range(self.n_rows)]
        self.texts = [[None] * self.n_cols for _ in range(self.n_rows)]
        body = VGroup()
        for r, row in enumerate(values):
            for c, v in enumerate(row):
                box = Rectangle(width=cell_w, height=cell_h, stroke_color=T.MUTED,
                                stroke_width=1.5, fill_color=T.FAINT, fill_opacity=0.9)
                box.move_to([c * cell_w, -r * cell_h, 0])
                txt = self._make_text(v, box)
                self.boxes[r][c], self.texts[r][c] = box, txt
                body.add(box, txt)
        self.body = body
        self.add(body)
        self.row_labels = VGroup()
        if row_labels:
            for r, lab in enumerate(row_labels):
                color = row_colors[r] if row_colors else T.FG
                t = _txt(lab, label_size, color=color, weight="BOLD")
                t.next_to(self.boxes[r][0], LEFT, buff=0.25)
                self.row_labels.add(t)
            self.add(self.row_labels)
        self.col_labels = VGroup()
        if col_labels:
            for c, lab in enumerate(col_labels):
                t = _txt(lab, label_size, color=T.MUTED, weight="BOLD")
                t.next_to(self.boxes[0][c], UP, buff=0.15)
                self.col_labels.add(t)
            self.add(self.col_labels)
        self.move_to([0, 0, 0])

    def _make_text(self, v, box, color=T.FG):
        s = str(v)
        if s == "":
            t = _txt("0", self.size).set_opacity(0)     # invisible placeholder
        else:
            t = _txt(s, self.size, color=color)
        if t.width > self.cell_w * 0.85:
            t.scale_to_fit_width(self.cell_w * 0.85)
        return t.move_to(box)

    def cell(self, r, c):
        return VGroup(self.boxes[r][c], self.texts[r][c])

    def target_text(self, r, c, value, color=T.FG):
        """A Text positioned in cell (r, c), not yet part of the grid (use with put)."""
        return self._make_text(value, self.boxes[r][c], color=color)

    def put(self, r, c, mob):
        """Make `mob` the text of cell (r, c), replacing the old one (no animation)."""
        old = self.texts[r][c]
        self.body.remove(old)
        self.body.add(mob)
        self.texts[r][c] = mob
        return self

    def set_text(self, r, c, value, color=T.FG):
        """Animation: the cell's text changes to `value`."""
        new = self.target_text(r, c, value, color)
        old = self.texts[r][c]
        self.texts[r][c] = old   # Transform morphs old into new in place
        return Transform(old, new)

    def highlight_cell(self, r, c, color=T.YELLOW):
        return self.boxes[r][c].animate.set_stroke(color=color, width=4)

    def highlight_col(self, c, color=T.YELLOW, opacity: float = 0.25):
        return AnimationGroup(*[self.boxes[r][c].animate.set_fill(color, opacity)
                                .set_stroke(color, 3) for r in range(self.n_rows)])

    def clear_col(self, c):
        return AnimationGroup(*[self.boxes[r][c].animate.set_fill(T.FAINT, 0.9)
                                .set_stroke(T.MUTED, 1.5) for r in range(self.n_rows)])

    def highlight_row(self, r, color=T.YELLOW, opacity: float = 0.25):
        return AnimationGroup(*[self.boxes[r][c].animate.set_fill(color, opacity)
                                .set_stroke(color, 3) for c in range(self.n_cols)])


class Chip(VGroup):
    """A small pill with text, e.g. a candidate sum "2 + 3 = 5" or a tag "+4"."""

    def __init__(self, text: str, color=T.BLUE, size: int = T.SMALL_SIZE + 2,
                 text_color=None, filled: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = f"Chip {text}"
        self.color = color
        label = _txt(text, size, color=text_color or (T.BG if filled else T.FG), weight="BOLD")
        pill = RoundedRectangle(corner_radius=0.16, width=label.width + 0.4,
                                height=label.height + 0.26, stroke_color=color, stroke_width=2.5,
                                fill_color=color if filled else T.FAINT,
                                fill_opacity=1 if filled else 0.95)
        label.move_to(pill)
        self.pill, self.label = pill, label
        self.add(pill, label)

    def win(self):
        """Animation: highlight as the chosen option."""
        return AnimationGroup(self.pill.animate.set_stroke(T.GREEN, 5).set_fill(T.GREEN, 0.3),
                              self.label.animate.set_color(T.GREEN))

    def lose(self):
        """Animation: fade back as a rejected option."""
        return self.animate.set_opacity(0.3)


class Bubble(VGroup):
    """A speech bubble: a node 'saying' something, e.g. its distance vector.

        b = Bubble("D is 3 away\\nF is 1 away", T.LIME, tail="left").next_to(node, RIGHT)
    tail: "down", "up", "left" or "right" (the side the tail points out of).
    """

    def __init__(self, text: str, color=T.BLUE, tail: str = "down", size: int = T.SMALL_SIZE + 2,
                 **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Bubble"
        label = _txt(text, size, color=T.FG, line_spacing=0.9)
        body = RoundedRectangle(corner_radius=0.18, width=label.width + 0.45,
                                height=label.height + 0.35, stroke_color=color, stroke_width=3,
                                fill_color=T.FAINT, fill_opacity=1)
        label.move_to(body)
        d = {"down": DOWN, "up": UP, "left": LEFT, "right": RIGHT}[tail]
        base = body.get_edge_center(d)
        perp = np.array([d[1], -d[0], 0]) * 0.16
        tip = base + d * 0.28
        tri = Polygon(base + perp - d * 0.02, base - perp - d * 0.02, tip,
                      stroke_color=color, stroke_width=3, fill_color=T.FAINT, fill_opacity=1)
        cover = Line(base + perp * 0.85, base - perp * 0.85, stroke_color=T.FAINT, stroke_width=5)
        self.body, self.label, self.tail_tip = body, label, tip
        self.add(tri, body, cover, label)
