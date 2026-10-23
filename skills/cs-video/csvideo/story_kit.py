"""Drawn props for StoryScene videos: machines, envelopes, keys and locks, a typing terminal,
signals that travel along wires, and a byte row. Flat shapes, a few colours, no boxes of text.

    srv = Server("smtp.ru.is", P.BLUE)
    term = Terminal(width=8, lines=9); self.play(term.type("EHLO smtp.ru.is", who="C"))
    self.play(pulse(line, P.YELLOW))              # a flash travelling along a wire
    dot, anim = trail_dot([a, b, c], P.GOLD)      # a dot moving along points, leaving a fading trail
"""
from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, PI, RIGHT, UP, AddTextLetterByLetter, Arc, Circle, Dot,
                   FadeIn, Line, MoveAlongPath, Polygon, Rectangle, RoundedRectangle,
                   ShowPassingFlash, Square, TracedPath, VGroup, VMobject, linear)

from .story import FONT, P, txt


class Server(VGroup):
    """A rack server: a dark box with three slots and status lights, label underneath."""

    def __init__(self, label: str = "", color=P.BLUE, scale: float = 1.0, **kw):
        super().__init__(**kw)
        self.layout_name = f"Server {label}"
        body = RoundedRectangle(corner_radius=0.12, width=1.3, height=1.6, fill_color=P.FAINT, fill_opacity=1,
                                stroke_color=color, stroke_width=3)
        slots = VGroup()
        for i in range(3):
            y = 0.5 - i * 0.48
            slot = RoundedRectangle(corner_radius=0.05, width=1.0, height=0.3, fill_color="#16181D", fill_opacity=1,
                                    stroke_color=color, stroke_width=1.5).move_to([0, y, 0])
            led = Dot([0.36, y, 0], radius=0.045, color=P.GREEN if i != 1 else color)
            vent = VGroup(*[Line([-0.38 + j * 0.09, y - 0.08, 0], [-0.38 + j * 0.09, y + 0.08, 0], stroke_color=color,
                                 stroke_width=1.5, stroke_opacity=0.6) for j in range(4)])
            slots.add(VGroup(slot, led, vent))
        self.body, self.leds = body, VGroup(*[s[1] for s in slots])
        self.add(body, slots)
        if label:
            self.label = txt(label, size=22, color=color).next_to(body, DOWN, buff=0.15)
            self.add(self.label)
        self.scale(scale)


class Laptop(VGroup):
    def __init__(self, label: str = "", color=P.TEAL, screen_text: str = "", scale: float = 1.0, **kw):
        super().__init__(**kw)
        self.layout_name = f"Laptop {label}"
        lid = RoundedRectangle(corner_radius=0.08, width=1.7, height=1.1, fill_color=P.FAINT, fill_opacity=1,
                               stroke_color=color, stroke_width=3)
        screen = RoundedRectangle(corner_radius=0.04, width=1.5, height=0.9, fill_color="#10141A", fill_opacity=1,
                                  stroke_width=0).move_to(lid)
        base = Polygon([-1.05, -0.62, 0], [1.05, -0.62, 0], [0.92, -0.5, 0], [-0.92, -0.5, 0], fill_color=color,
                       fill_opacity=0.9, stroke_width=0)
        self.screen = screen
        self.add(lid, screen, base)
        if screen_text:
            self.add(txt(screen_text, size=18, color=color).move_to(screen))
        if label:
            self.label = txt(label, size=22, color=color).next_to(base, DOWN, buff=0.15)
            self.add(self.label)
        self.scale(scale)


class Envelope(VGroup):
    """A letter envelope; `to` is written on its face; a stamp in the corner."""

    def __init__(self, to: str = "", color=P.GOLD, width: float = 1.6, **kw):
        super().__init__(**kw)
        self.layout_name = "Envelope"
        h = width * 0.62
        body = Rectangle(width=width, height=h, fill_color="#F3E3C3", fill_opacity=1, stroke_color=color, stroke_width=3)
        flap = Polygon(body.get_corner(UP + LEFT), body.get_corner(UP + RIGHT), body.get_center() + DOWN * h * 0.05,
                       fill_color="#E8D3AC", fill_opacity=1, stroke_color=color, stroke_width=2.5)
        stamp = Rectangle(width=width * 0.16, height=width * 0.19, fill_color=P.RED, fill_opacity=0.9,
                          stroke_width=0).move_to(body.get_corner(UP + RIGHT) + np.array([-width * 0.13, -width * 0.14, 0]))
        self.body = body
        self.add(body, flap, stamp)
        if to:
            t = txt(to, size=16, color="#3A2A10", weight="BOLD")
            if t.width > width * 0.85:
                t.scale_to_fit_width(width * 0.85)
            t.move_to(body.get_center() + DOWN * h * 0.25)
            self.add(t)


class Key(VGroup):
    def __init__(self, color=P.GOLD, label: str = "", size: float = 1.0, **kw):
        super().__init__(**kw)
        ring = Circle(radius=0.22, stroke_color=color, stroke_width=8)
        shaft = Line([0.22, 0, 0], [0.95, 0, 0], stroke_color=color, stroke_width=8)
        teeth = VGroup(Line([0.7, 0, 0], [0.7, -0.17, 0], stroke_color=color, stroke_width=8),
                       Line([0.86, 0, 0], [0.86, -0.22, 0], stroke_color=color, stroke_width=8))
        self.add(ring, shaft, teeth)
        if label:
            self.add(txt(label, size=18, color=color).next_to(VGroup(ring, shaft), DOWN, buff=0.12))
        self.scale(size)


class Padlock(VGroup):
    def __init__(self, color=P.GOLD, closed: bool = True, size: float = 1.0, **kw):
        super().__init__(**kw)
        body = RoundedRectangle(corner_radius=0.08, width=0.7, height=0.55, fill_color=color, fill_opacity=1, stroke_width=0)
        shackle = Arc(radius=0.24, start_angle=0, angle=PI, stroke_color=color, stroke_width=9)
        shackle.next_to(body, UP, buff=-0.02)
        if not closed:
            shackle.shift(UP * 0.18 + RIGHT * 0.12)
        hole = Circle(radius=0.06, fill_color=P.BG, fill_opacity=1, stroke_width=0).move_to(body).shift(UP * 0.03)
        self.body, self.shackle = body, shackle
        self.add(shackle, body, hole)
        self.scale(size)

    def close(self):
        return self.shackle.animate.shift(DOWN * 0.18 * self.body.width / 0.7 + LEFT * 0.12 * self.body.width / 0.7)


class Terminal(VGroup):
    """A terminal / protocol transcript. type(text, who) types a new line; old lines scroll up.
    who: "C" (client, blue), "S" (server, green), or None (plain)."""

    COLORS = {"C": P.BLUE, "S": P.GREEN, None: P.FG, "!": P.RED, "#": P.MUTED}

    def __init__(self, width: float = 8.0, lines: int = 9, title: str = "", font_size: int = 22, **kw):
        super().__init__(**kw)
        self.layout_name = "Terminal"
        self.n, self.fs = lines, font_size
        self.lh = font_size * 0.0155 + 0.08
        h = lines * self.lh + 0.75
        self.box = RoundedRectangle(corner_radius=0.15, width=width, height=h, fill_color="#121418", fill_opacity=1,
                                    stroke_color="#2E323A", stroke_width=2)
        bar = VGroup(*[Dot(radius=0.06, color=c) for c in (P.RED, P.GOLD, P.GREEN)]).arrange(RIGHT, buff=0.12)
        bar.move_to(self.box.get_corner(UP + LEFT) + np.array([0.4, -0.22, 0]))
        self.add(self.box, bar)
        if title:
            self.add(txt(title, size=18, color=P.MUTED).move_to(self.box.get_top() + DOWN * 0.22))
        self.rows = VGroup()
        self.add(self.rows)

    def _line_pos(self, i):
        top = self.box.get_top()[1] - 0.6
        return np.array([self.box.get_left()[0] + 0.35, top - i * self.lh, 0])

    def line(self, text: str, who=None):
        prefix = {"C": "C: ", "S": "S: "}.get(who, "")
        t = txt(prefix + text, size=self.fs, color=self.COLORS.get(who, P.FG), font="DejaVu Sans Mono")
        maxw = self.box.width - 0.7
        if t.width > maxw:
            t.scale_to_fit_width(maxw)
        return t

    def type(self, text: str, who=None, run_time: float | None = None):
        """Animation: append a typed line (scrolls when full)."""
        from manim import AnimationGroup, Succession
        t = self.line(text, who)
        anims = []
        if len(self.rows) >= self.n:
            first = self.rows[0]
            self.rows.remove(first)
            anims.append(AnimationGroup(first.animate.set_opacity(0),
                                        *[r.animate.shift(UP * self.lh) for r in self.rows], run_time=0.25))
        i = len(self.rows)
        t.move_to(self._line_pos(i), aligned_edge=LEFT)
        self.rows.add(t)
        rt = run_time or min(1.4, 0.25 + 0.03 * len(text))
        anims.append(AddTextLetterByLetter(t, run_time=rt))
        return Succession(*anims) if len(anims) > 1 else anims[0]

    def clear_rows(self):
        from manim import FadeOut
        old = self.rows
        self.rows = VGroup()
        self.add(self.rows)
        return FadeOut(old, run_time=0.3)


def pulse(line_or_path, color=P.YELLOW, width: float = 8, time_width: float = 0.35, run_time: float = 0.8):
    """A bright flash running along a wire (any VMobject path)."""
    c = line_or_path.copy().set_stroke(color, width=width)
    return ShowPassingFlash(c, time_width=time_width, run_time=run_time)


def trail_dot(points, color=P.GOLD, radius: float = 0.09, run_time: float = 1.5, trail: float = 0.6):
    """(dot, trail, animation): a dot moving smoothly through `points`, leaving a fading trail.
    Add `trail` to the scene before playing; remove both afterwards."""
    path = VMobject().set_points_smoothly([np.array(p, dtype=float) for p in points])
    dot = Dot(points[0], radius=radius, color=color)
    tr = TracedPath(dot.get_center, stroke_color=color, stroke_width=5, dissipating_time=trail)
    return dot, tr, MoveAlongPath(dot, path, run_time=run_time, rate_func=linear)


class ByteRow(VGroup):
    """A row of byte cells (hex or text), e.g. for base64 or a packet's bytes."""

    def __init__(self, items, color=P.BLUE, cell: float = 0.55, font_size: int = 22, **kw):
        super().__init__(**kw)
        for it in items:
            sq = Square(cell, stroke_color=color, stroke_width=2, fill_color=P.FAINT, fill_opacity=1)
            t = txt(str(it), size=font_size, color=P.FG, font="DejaVu Sans Mono").move_to(sq)
            if t.width > cell * 0.85:
                t.scale_to_fit_width(cell * 0.85)
            self.add(VGroup(sq, t))
        self.arrange(RIGHT, buff=0.04)
