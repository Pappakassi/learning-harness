"""Hr. Schiffel: the series' gnome mascot (a fierce little networking expert).

    g = Schiffel("fierce").scale(0.55).to_corner(DR)
    self.play(g.enter())                          # hops in
    self.play(g.change("thinking", look=LEFT))    # mood + where he looks
    self.play(g.blink()); self.play(g.look_at(obj))
    bubble = g.bubble("Ach! Port 25?")             # a speech bubble mobject next to him
    with self.say("...", who="gnome"):              # StoryScene: his voice, mouth moves by itself
        ...

Moods: fierce (default), angry, thinking, surprised, lecturing (points right; point="left" mirrors the
arm), happy. Everything is plain VMobjects, so he morphs smoothly between moods.
"""
from __future__ import annotations

import numpy as np
from manim import (BLACK, DOWN, LEFT, PI, RIGHT, UP, WHITE, Arc, Circle, Ellipse, FadeIn, FadeOut,
                   Line, ManimColor, Polygon, Rectangle, RoundedRectangle, Square, Succession, Text,
                   Transform, UpdateFromAlphaFunc, VGroup, VMobject, interpolate_color, rate_functions,
                   there_and_back)

SKIN = "#F2C4A0"; HAIR = "#A0532C"; BEARD = "#B8662F"; HAT = "#C8352E"; HAT_D = "#9E2620"
TUNIC = "#2F7F8F"; TRIM = "#E8873A"; BELT = "#4A3020"; BUCKLE = "#D9B44A"; FRAME = "#7A5A3A"
BOOT = "#4A3020"; INK = "#1A1A1A"; BADGE = "#D9D4C7"; NOSE = "#E79A82"
MOODS = ("fierce", "angry", "thinking", "surprised", "lecturing", "happy")


def _blob(points, color):
    m = VMobject(fill_color=color, fill_opacity=1, stroke_width=0)
    m.set_points_smoothly(points)
    return m


def _arm(pts, sx=1):
    return VMobject(stroke_color=TUNIC, stroke_width=28).set_points_smoothly([[sx * x, y, 0] for x, y, _ in pts])


class Schiffel(VGroup):
    def __init__(self, mood: str = "fierce", look=(0.0, 0.0), point: str = "right", symbol: str = "</>", **kw):
        super().__init__(**kw)
        if mood not in MOODS:
            raise ValueError(f"mood must be one of {MOODS}")
        self.mood, self.point, self.symbol = mood, point, symbol
        self.layout_name = "Schiffel"
        look = np.array(look, dtype=float)[:2] if np.ndim(look) else np.array([0.0, 0.0])
        skin = dict(fill_color=SKIN, fill_opacity=1, stroke_width=0)
        boots = VGroup(*[Ellipse(width=0.62, height=0.26, fill_color=BOOT, fill_opacity=1, stroke_width=0)
                         .move_to([x, -1.55, 0]) for x in (-0.36, 0.36)])
        tunic = Polygon([-0.98, -1.45, 0], [0.98, -1.45, 0], [0.64, 0.05, 0], [-0.64, 0.05, 0],
                        fill_color=TUNIC, fill_opacity=1, stroke_width=0).round_corners(0.18)
        collar = Arc(radius=0.52, start_angle=PI + 0.35, angle=PI - 0.7, stroke_color=TRIM, stroke_width=10).move_to([0, -0.02, 0])
        belt = Rectangle(width=1.78, height=0.2, fill_color=BELT, fill_opacity=1, stroke_width=0).move_to([0, -0.95, 0])
        buckle = Square(0.26, stroke_color=BUCKLE, stroke_width=5).move_to([0, -0.95, 0])
        down = [[0.64, -0.3, 0], [0.97, -0.7, 0], [1.02, -1.0, 0]]
        arm_l, hand_l = _arm(down, -1), Circle(0.14, **skin).move_to([-1.02, -1.08, 0])
        arm_r, hand_r = _arm(down, 1), Circle(0.14, **skin).move_to([1.02, -1.08, 0])
        if mood == "angry":
            up = [[0.64, -0.3, 0], [1.1, -0.2, 0], [1.05, 0.25, 0]]
            arm_l, arm_r = _arm(up, -1), _arm(up, 1)
            hand_l = Circle(0.16, **skin).move_to([-1.05, 0.33, 0]); hand_r = Circle(0.16, **skin).move_to([1.05, 0.33, 0])
        elif mood == "thinking":
            arm_r = _arm([[0.64, -0.3, 0], [0.8, -0.65, 0], [0.4, -0.55, 0], [0.2, -0.35, 0]])
            hand_r = Circle(0.14, **skin).move_to([0.16, -0.3, 0])
        elif mood in ("surprised", "happy"):
            up = [[0.64, -0.3, 0], [1.05, 0.0, 0], [1.15, 0.45, 0]]
            arm_l, arm_r = _arm(up, -1), _arm(up, 1)
            hand_l = Circle(0.14, **skin).move_to([-1.17, 0.55, 0]); hand_r = Circle(0.14, **skin).move_to([1.17, 0.55, 0])
        elif mood == "lecturing":
            sx = 1 if point == "right" else -1
            pa = _arm([[0.64, -0.3, 0], [1.05, -0.05, 0], [1.45, 0.1, 0]], sx)
            ph = VGroup(Circle(0.14, **skin).move_to([sx * 1.55, 0.12, 0]),
                        RoundedRectangle(corner_radius=0.04, width=0.26, height=0.08, **skin).move_to([sx * 1.74, 0.14, 0]))
            if sx > 0:
                arm_r, hand_r = pa, ph
            else:
                arm_l, hand_l = pa, ph
        head = Circle(radius=0.78, **skin).move_to([0, 0.72, 0])
        ears = VGroup(*[Ellipse(width=0.22, height=0.34, **skin).move_to([s * 0.78, 0.7, 0]) for s in (-1, 1)])
        sides = VGroup(*[_blob([[s * 0.62, 1.15, 0], [s * 0.86, 0.95, 0], [s * 0.8, 0.62, 0], [s * 0.66, 0.78, 0], [s * 0.62, 1.15, 0]], HAIR) for s in (-1, 1)])
        bx = [-0.5, -0.62, -0.58, -0.42, -0.22, 0.0, 0.22, 0.42, 0.58, 0.62, 0.5, 0.25, 0.0, -0.25, -0.5]
        by = [0.28, 0.05, -0.3, -0.55, -0.72, -0.9, -0.72, -0.55, -0.3, 0.05, 0.28, 0.17, 0.14, 0.17, 0.28]
        beard = _blob([[x, y, 0] for x, y in zip(bx, by)], BEARD)
        strands = VGroup(*[Line([x, 0.05, 0], [x * 0.6, -0.55 + abs(x) * 0.3, 0], stroke_width=2.5,
                                stroke_color=interpolate_color(ManimColor(BEARD), BLACK, 0.25)) for x in (-0.35, -0.12, 0.12, 0.35)])
        hat = _blob([[-0.92, 1.12, 0], [-0.6, 1.9, 0], [-0.25, 2.75, 0], [0.12, 3.25, 0], [0.42, 3.2, 0], [0.3, 2.6, 0],
                     [0.62, 1.9, 0], [0.92, 1.12, 0], [0.0, 1.05, 0], [-0.92, 1.12, 0]], HAT)
        shade = _blob([[0.2, 1.12, 0], [0.62, 1.9, 0], [0.3, 2.6, 0], [0.42, 3.2, 0], [0.5, 2.6, 0], [0.92, 1.12, 0], [0.2, 1.12, 0]], HAT_D)
        badge = Circle(radius=0.3, fill_color=BADGE, fill_opacity=1, stroke_color="#9A958A", stroke_width=4).move_to([-0.05, 1.62, 0])
        code = Text(symbol, font="DejaVu Sans Mono", weight="BOLD", color=INK).scale_to_fit_width(0.38).move_to(badge)
        eyes, lids = VGroup(), VGroup()
        for s in (-1, 1):
            c = np.array([s * 0.3, 0.8, 0])
            if mood == "happy":
                eyes.add(VGroup(Arc(radius=0.11, start_angle=0.25, angle=PI - 0.5, stroke_color=INK, stroke_width=6).move_to(c)))
                continue
            h = 0.34 if mood == "surprised" else 0.26
            white = Ellipse(width=0.27, height=h, fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to(c)
            pupil = Circle(radius=0.07 if mood != "surprised" else 0.055, fill_color=INK, fill_opacity=1, stroke_width=0)
            pupil.move_to(c + np.array([look[0] * 0.06, look[1] * 0.06 - (0.02 if mood in ("fierce", "angry") else 0), 0]))
            glint = Circle(radius=0.02, fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to(pupil.get_center() + np.array([0.022, 0.025, 0]))
            eyes.add(VGroup(white, pupil, glint))
            if mood in ("fierce", "angry", "lecturing"):
                drop = 0.1 if mood == "angry" else 0.07
                inner, outer = c + np.array([-s * 0.16, 0.2, 0]), c + np.array([s * 0.16, 0.2, 0])
                lids.add(Polygon(inner + UP * 0.05, outer + UP * 0.05, outer + DOWN * 0.12, inner + DOWN * (0.12 + drop), **skin))
        glasses = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.44, height=0.3, stroke_color=FRAME, stroke_width=4).move_to([s * 0.3, 0.8, 0]) for s in (-1, 1)],
                         Line([-0.08, 0.84, 0], [0.08, 0.84, 0], stroke_color=FRAME, stroke_width=4),
                         *[Line([s * 0.52, 0.84, 0], [s * 0.76, 0.78, 0], stroke_color=FRAME, stroke_width=4) for s in (-1, 1)])
        tilt = {"fierce": 0.13, "angry": 0.2, "thinking": 0.0, "surprised": -0.08, "lecturing": 0.06, "happy": -0.02}[mood]
        brows = VGroup()
        for s in (-1, 1):
            t = -0.08 if (mood == "thinking" and s > 0) else tilt
            r = 0.08 if mood == "surprised" else 0.0
            brows.add(Polygon([s * 0.5, 1.08 + r, 0], [s * 0.1, 1.08 - t + r, 0], [s * 0.1, 0.97 - t + r, 0], [s * 0.5, 0.99 + r, 0],
                              fill_color=HAIR, fill_opacity=1, stroke_width=0).round_corners(0.03))
        nose = Circle(radius=0.17, fill_color=NOSE, fill_opacity=1, stroke_width=0).move_to([0, 0.56, 0])
        nose_hi = Circle(radius=0.05, fill_color=WHITE, fill_opacity=0.45, stroke_width=0).move_to([-0.06, 0.62, 0])
        mouths = {
            "fierce": Arc(radius=0.18, start_angle=0.5, angle=PI - 1.0, stroke_color=INK, stroke_width=6).move_to([0, 0.3, 0]),
            "angry": VGroup(Polygon([-0.17, 0.33, 0], [0.17, 0.33, 0], [0.12, 0.2, 0], [-0.12, 0.2, 0], fill_color=INK, fill_opacity=1, stroke_width=0),
                            Rectangle(width=0.28, height=0.045, fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to([0, 0.305, 0])),
            "thinking": Line([-0.12, 0.3, 0], [0.12, 0.27, 0], stroke_color=INK, stroke_width=6),
            "surprised": Ellipse(width=0.16, height=0.2, fill_color=INK, fill_opacity=1, stroke_width=0).move_to([0, 0.28, 0]),
            "lecturing": Line([-0.13, 0.27, 0], [0.13, 0.32, 0], stroke_color=INK, stroke_width=6),
            "happy": Arc(radius=0.2, start_angle=PI + 0.45, angle=PI - 0.9, stroke_color=INK, stroke_width=6).move_to([0, 0.29, 0]),
        }
        mouth = mouths[mood]
        talk = Ellipse(width=0.2, height=0.02, fill_color="#3A1414", fill_opacity=0, stroke_width=0).move_to([0, 0.28, 0])
        steam = VGroup()
        if mood == "angry":
            for s in (-1, 1):
                for k in range(2):
                    steam.add(Arc(radius=0.12, start_angle=-PI / 2, angle=PI, stroke_color="#BBBBBB", stroke_width=4)
                              .move_to([s * (1.05 + k * 0.18), 1.35 + k * 0.25, 0]))
        parts = [boots, arm_l, hand_l, tunic, belt, buckle, collar, ears, head, sides, beard, strands, mouth, talk,
                 eyes, lids, glasses, nose, nose_hi, hat, shade, badge, code, brows, arm_r, hand_r, steam]
        self.add(*parts)
        self.head, self.eyes, self.talk_mouth, self.hat_tip = head, eyes, talk, hat

    # ---------- geometry helpers ----------
    def unit(self):
        """Current scale: the head's radius (0.78 at scale 1)."""
        return self.head.width / 1.56

    def anchor(self):
        return self.head.get_center()

    def _target(self, mood=None, look=None, point=None):
        t = Schiffel(mood or self.mood, look if look is not None else (0, 0), point=point or self.point, symbol=self.symbol)
        t.scale(self.unit())
        t.shift(self.anchor() - t.head.get_center())
        return t

    # ---------- animations ----------
    def change(self, mood: str, look=None, point: str | None = None, run_time: float = 0.6):
        """Morph into another mood (and/or look direction: a vector like LEFT+UP*0.5)."""
        target = self._target(mood, look, point)
        self.mood = mood
        if point:
            self.point = point
        return Transform(self, target, run_time=run_time)

    def look_at(self, where, run_time: float = 0.4):
        """Turn the eyes towards a point or mobject (same mood)."""
        p = where.get_center() if hasattr(where, "get_center") else np.array(where, dtype=float)
        d = p - self.anchor()
        n = np.linalg.norm(d[:2]) or 1.0
        return self.change(self.mood, look=(d[0] / n, d[1] / n), run_time=run_time)

    def blink(self, run_time: float = 0.25):
        eyes = self.eyes
        y = eyes.get_center()[1]
        return eyes.animate(rate_func=there_and_back, run_time=run_time).stretch(0.1, 1, about_point=[eyes.get_center()[0], y, 0])

    def enter(self, run_time: float = 0.8):
        """Hop in from below."""
        return FadeIn(self, shift=UP * 0.6, run_time=run_time, rate_func=rate_functions.ease_out_back)

    def exit(self, run_time: float = 0.6):
        return FadeOut(self, shift=DOWN * 0.6, run_time=run_time)

    def hop(self, height: float = 0.35, run_time: float = 0.45):
        return self.animate(rate_func=there_and_back, run_time=run_time).shift(UP * height * self.unit())

    def bubble(self, text: str, side: str = "left", size: int = 26, color="#F2F2F2"):
        """A speech bubble positioned above-left (or above-right) of his head."""
        from .scene_base import make_text
        label = make_text(text, size=size, color="#111111", weight="BOLD")
        body = RoundedRectangle(corner_radius=0.2, width=label.width + 0.5, height=label.height + 0.4,
                                fill_color=color, fill_opacity=1, stroke_width=0)
        label.move_to(body)
        sx = -1 if side == "left" else 1
        b = VGroup(body, label)
        head = self.anchor()
        b.move_to(head + np.array([sx * (b.width / 2 + 0.55 * self.unit()), (1.3 + 0.15) * self.unit() + b.height / 2, 0]))
        tip = head + np.array([sx * 0.5 * self.unit(), 0.75 * self.unit(), 0])
        base = body.get_corner(DOWN + (RIGHT if sx < 0 else LEFT)) + np.array([-sx * 0.35, 0.02, 0])
        tail = Polygon(base + LEFT * 0.12, base + RIGHT * 0.12, tip, fill_color=color, fill_opacity=1, stroke_width=0)
        b.add_to_back(tail)
        b.layout_name = "Schiffel bubble"
        return b

    # ---------- talking (driven by StoryScene.say(..., who="gnome")) ----------
    def start_talking(self):
        state = {"t": 0.0}
        rng = np.random.default_rng(7)
        phases = rng.uniform(0, 2 * np.pi, 3)

        def flap(m, dt):
            state["t"] += dt
            t = state["t"]
            o = abs(np.sin(t * 13 + phases[0])) * 0.6 + abs(np.sin(t * 7.3 + phases[1])) * 0.4
            h = (0.02 + 0.15 * o) * self.unit()
            cx, cy = m.get_center()[0], m.get_center()[1]
            m.stretch_to_fit_height(max(h, 0.005)).move_to([cx, cy, 0])
            m.set_fill(opacity=1)
        self.talk_mouth.add_updater(flap)

    def stop_talking(self):
        self.talk_mouth.clear_updaters()
        self.talk_mouth.set_fill(opacity=0)
