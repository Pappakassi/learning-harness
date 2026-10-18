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

from manim import (DOWN, LEFT, RIGHT, UP, logger, AnimationGroup, Arrow, FadeIn, FadeOut,
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
