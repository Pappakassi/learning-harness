"""Livelier effects: particle swarms, gauges, glows, shakes, counting numbers.

These are what make a video feel alive instead of like slides:
  * Swarm      many particles streaming from sources to a target (traffic, ACK floods)
  * Gauge      a dial whose needle and color react to load
  * glow()     soft halo behind a mobject (fake bloom)
  * shake()    quick jitter for "overloaded" moments
  * CountUp    a number that counts smoothly instead of morphing
  * scatter_ring()  points spread around a center, for crowds of hosts
"""
from __future__ import annotations

import numpy as np
from manim import (DOWN, PI, TAU, UP, AnimationGroup, Arc, Circle, Create, Dot, Line, Rectangle,
                   Succession, Text, ValueTracker, VGroup, always_redraw, interpolate_color,
                   linear)
from manim.animation.animation import Animation

from . import theme as T


def _txt(s, size, color=T.FG, **kw):
    return Text(str(s), font_size=size, color=color, font=T.BODY_FONT, **kw)


def scatter_ring(center, rx: float, ry: float, n: int, inner: float = 0.25, seed: int = 1):
    """n random points in an elliptical ring around center (inner = hole size, 0..1)."""
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        x, y = rng.uniform(-1, 1, 2)
        r = np.hypot(x, y)
        if inner <= r <= 1:
            pts.append(np.array(center) + np.array([x * rx, y * ry, 0.0]))
    return pts


class Swarm(VGroup):
    """Particles (short streaks) flowing from `sources` to `target`, continuously.

    swarm.start() adds an updater so it runs during any play()/wait() until
    swarm.stop(). `rate` = how many particles are in flight per source (0..1 = some
    sources idle). The group is excluded from the layout check.
    """

    def __init__(self, sources, target, color=T.GREEN, n: int = 300, speed: float = 0.55,
                 streak: float = 0.18, width: float = 2.5, seed: int = 2, colors=None,
                 **kwargs):
        """colors: optional list, one colour per source (particles take their source's)."""
        super().__init__(**kwargs)
        self.skip_layout_check = True
        rng = np.random.default_rng(seed)
        self.target = np.array(target, dtype=float)
        idx = rng.integers(0, len(sources), n)
        self.src = np.array([sources[i] for i in idx], dtype=float)
        self.phase = rng.uniform(0, 1, n)
        self.speed = speed * rng.uniform(0.7, 1.3, n)
        self.streak = streak
        self.t = 0.0
        self.intensity = 0.0        # 0 = invisible, 1 = full stream (animate via set_intensity)
        for k in range(n):
            c = colors[idx[k]] if colors is not None else color
            self.add(Line(UP * 0.0, UP * 0.01, stroke_color=c, stroke_width=width))
        self._apply()

    def _apply(self):
        frac = (self.phase + self.t * self.speed) % 1.0
        for k, ln in enumerate(self.submobjects):
            s = self.src[k]
            d = self.target - s
            p = s + d * frac[k]
            u = d / (np.linalg.norm(d) + 1e-9)
            visible = self.phase[k] < self.intensity
            ln.put_start_and_end_on(p - u * self.streak, p + u * 0.001)
            ln.set_stroke(opacity=(0.9 * min(1, frac[k] * 4)) if visible else 0)

    def _tick(self, mob, dt):
        self.t += dt
        self._apply()

    def start(self):
        self.add_updater(self._tick)
        return self

    def stop(self):
        self.remove_updater(self._tick)
        return self

    def set_intensity(self, value: float, run_time: float = 1.0):
        """Animation fading the stream from its current intensity to `value`."""
        return _IntensityAnim(self, value, run_time=run_time)


class _IntensityAnim(Animation):
    def __init__(self, swarm, value, **kw):
        self.start_v, self.end_v = swarm.intensity, value
        super().__init__(swarm, rate_func=linear, **kw)

    def begin(self):
        self.start_v = self.mobject.intensity
        super().begin()

    def interpolate_mobject(self, alpha):
        self.mobject.intensity = self.start_v + (self.end_v - self.start_v) * alpha


class Gauge(VGroup):
    """A half-circle dial. gauge.tracker drives it: self.play(gauge.to(0.9)).

    Values above 1.0 push the needle past the red end (overload).
    """

    def __init__(self, label: str = "load", radius: float = 1.1, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Gauge"
        self.radius = radius
        self.tracker = ValueTracker(0.0)
        segs = VGroup()
        n = 24
        for i in range(n):
            a0 = PI - PI * i / n
            c = interpolate_color(T.GREEN, T.YELLOW, min(1, i / (n * 0.55))) if i < n * 0.55 \
                else interpolate_color(T.YELLOW, T.RED, (i - n * 0.55) / (n * 0.45))
            segs.add(Arc(radius=radius, start_angle=a0, angle=-PI / n * 0.85,
                         stroke_color=c, stroke_width=10))
        self.segs = segs
        hub = Dot(radius=0.07, color=T.FG)
        self.hub = hub

        def needle():
            v = self.tracker.get_value()
            ang = PI - PI * min(v, 1.1)
            tip = hub.get_center() + radius * 0.92 * np.array([np.cos(ang), np.sin(ang), 0])
            col = T.RED if v > 1 else T.FG
            return Line(hub.get_center(), tip, stroke_color=col, stroke_width=5)
        self.needle = always_redraw(needle)

        def readout():
            v = self.tracker.get_value()
            col = T.RED if v > 1 else (T.YELLOW if v > 0.6 else T.FG)
            t = _txt(f"{v * 100:,.0f}%", T.BODY_SIZE, color=col, weight="BOLD")
            return t.next_to(hub, DOWN, buff=0.15)
        self.readout = always_redraw(readout)
        self.caption = _txt(label, T.SMALL_SIZE, color=T.MUTED)
        self.add(segs, hub, self.needle, self.readout)
        self.caption.next_to(segs, UP, buff=0.15)
        self.add(self.caption)

    def to(self, value: float, run_time: float = 1.5, rate_func=None):
        kw = {"run_time": run_time}
        if rate_func:
            kw["rate_func"] = rate_func
        return self.tracker.animate(**kw).set_value(value)


def glow(mob, color=T.RED, layers: int = 7, spread: float = 0.6, opacity: float = 0.07):
    """Soft halo: stacked translucent circles centered on mob. Add it *behind* mob."""
    r0 = max(mob.width, mob.height) / 2
    g = VGroup(*[Circle(radius=r0 + spread * (i + 1) / layers, stroke_width=0,
                        fill_color=color, fill_opacity=opacity).move_to(mob)
                 for i in range(layers)])
    g.skip_layout_check = True
    return g


def shake(mob, amplitude: float = 0.08, times: int = 8, run_time: float = 0.6):
    """Quick jitter animation (for overload / error moments)."""
    rng = np.random.default_rng(3)
    steps = []
    dt = run_time / (times + 1)
    for _ in range(times):
        v = rng.uniform(-1, 1, 3) * amplitude
        v[2] = 0
        steps.append(mob.animate(run_time=dt / 2, rate_func=linear).shift(v))
        steps.append(mob.animate(run_time=dt / 2, rate_func=linear).shift(-v))
    return Succession(*steps)


class CountUp(VGroup):
    """A label whose number counts smoothly: self.play(c.to(10_000, run_time=2)).

    `log=True` counts on a log scale, so 6 -> 10,000 doesn't sprint past the
    small numbers in one frame.
    """

    def __init__(self, label: str, value: float = 0, size: int = T.BODY_SIZE,
                 color=T.FG, fmt: str = "{:,.0f}", **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "CountUp"
        self.tracker = ValueTracker(value)
        self.fmt = fmt
        self.lab = _txt(label + ":", size, color=T.MUTED)
        self.add(self.lab)

        def num():
            t = _txt(self.fmt.format(self.tracker.get_value()), size, color=color, weight="BOLD")
            return t.next_to(self.lab, np.array([1, 0, 0]), buff=0.2)
        self.num = always_redraw(num)
        self.add(self.num)

    def to(self, value: float, run_time: float = 2.0, log: bool = False):
        if not log:
            return self.tracker.animate(run_time=run_time).set_value(value)
        v0 = max(self.tracker.get_value(), 1)
        a, b = np.log10(v0), np.log10(value)
        return _LogCount(self.tracker, a, b, run_time=run_time)


class _LogCount(Animation):
    def __init__(self, tracker, a, b, **kw):
        self.a, self.b = a, b
        super().__init__(tracker, **kw)

    def interpolate_mobject(self, alpha):
        self.mobject.set_value(10 ** (self.a + (self.b - self.a) * self.rate_func(alpha)))


class RaceBars(VGroup):
    """Horizontal bars that grow at the same speed: the shortest total finishes first.

    Each row is (label, label_color, [(value, color), ...]): the segments are stacked,
    e.g. link cost then the neighbour's claimed distance. Lengths are value * unit.

        race = RaceBars([("via A", T.CYAN, [(4, T.CYAN), (20, T.CYAN)]), ...],
                        origin=[-5, 1, 0], unit=0.2)
        self.play(race.to(race.best_total(), run_time=2))   # stops when the winner arrives
        self.play(race.crown())                              # winner glows, others dim
        self.play(race.to(race.max_total(), run_time=1))     # the losers finish
    Segment values are written inside segments once they are fully grown, and the total
    appears at the end of each finished bar.
    """

    def __init__(self, rows, origin=(-5.0, 1.0, 0.0), unit: float = 0.2, row_gap: float = 0.85,
                 bar_h: float = 0.5, size: int = T.BODY_SIZE - 4, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "RaceBars"
        self.rows, self.unit, self.bar_h, self.size = rows, unit, bar_h, size
        self.origin = np.array(origin, dtype=float)
        self.tracker = ValueTracker(0.0)
        self.totals = [sum(v for v, _ in segs) for _, _, segs in rows]
        self.ys = [self.origin[1] - i * row_gap for i in range(len(rows))]
        self.labels = VGroup()
        for (label, color, _), y in zip(rows, self.ys):
            t = _txt(label, size, color=color, weight="BOLD")
            t.move_to([self.origin[0] - 0.25, y, 0], aligned_edge=np.array([1, 0, 0]))
            self.labels.add(t)
        top = self.ys[0] + bar_h * 0.9
        bottom = self.ys[-1] - bar_h * 0.9
        self.start_line = Line([self.origin[0], top, 0], [self.origin[0], bottom, 0],
                               stroke_color=T.MUTED, stroke_width=3)
        self.dimmed = set()
        self.bars = always_redraw(self._draw)
        self.add(self.labels, self.start_line, self.bars)

    def _draw(self):
        t = self.tracker.get_value()
        g = VGroup()
        for i, ((_, _, segs), y) in enumerate(zip(self.rows, self.ys)):
            op = 0.3 if i in self.dimmed else 1.0
            start = 0.0
            for k, (v, color) in enumerate(segs):
                shown = max(0.0, min(t - start, v))
                if shown > 1e-3:
                    w = shown * self.unit
                    x0 = self.origin[0] + start * self.unit
                    fill = 0.95 if k == 0 else 0.45
                    r = Rectangle(width=w, height=self.bar_h, stroke_width=1.5, stroke_color=color,
                                  fill_color=color, fill_opacity=fill * op).set_stroke(opacity=op)
                    r.move_to([x0 + w / 2, y, 0])
                    g.add(r)
                    if shown >= v - 1e-6:
                        lab = _txt(str(v), self.size - 4, color=T.BG if k == 0 else T.FG,
                                   weight="BOLD").set_opacity(op)
                        if lab.width < w - 0.08:
                            g.add(lab.move_to(r))
                start += v
            if t >= self.totals[i] - 1e-6:
                tot = _txt(f"= {self.totals[i]}", self.size, color=T.FG, weight="BOLD")
                tot.set_opacity(op)
                tot.move_to([self.origin[0] + self.totals[i] * self.unit + 0.2, y, 0],
                            aligned_edge=np.array([-1, 0, 0]))
                g.add(tot)
        return g

    def best_index(self):
        return int(np.argmin(self.totals))

    def best_total(self):
        return min(self.totals)

    def max_total(self):
        return max(self.totals)

    def to(self, value: float, run_time: float | None = None, speed: float = 9.0):
        """Grow all bars to `value` units at constant speed (`speed` units per second)."""
        dist = abs(value - self.tracker.get_value())
        rt = run_time if run_time is not None else max(0.3, dist / speed)
        return self.tracker.animate(run_time=rt, rate_func=linear).set_value(value)

    def crown(self, color=T.GREEN):
        """Animation: box the winning row; the others dim on the next redraw."""
        i = self.best_index()
        self.dimmed = {j for j in range(len(self.rows)) if j != i}
        w = self.totals[i] * self.unit + 1.4
        box = Rectangle(width=w + self.labels[i].width + 0.5, height=self.bar_h + 0.3,
                        stroke_color=color, stroke_width=4)
        box.move_to([self.origin[0] - self.labels[i].width - 0.35 + box.width / 2, self.ys[i], 0])
        self.winner_box = box
        return AnimationGroup(Create(box), self.labels[i].animate.set_color(color))


class Countdown(VGroup):
    """A ring that empties over `seconds` with the number in the middle (your-turn pause).

        cd = Countdown(3).move_to(RIGHT * 5)
        self.play(FadeIn(cd)); self.play(cd.run()); self.play(FadeOut(cd))
    """

    def __init__(self, seconds: int = 3, radius: float = 0.55, color=T.YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Countdown"
        self.seconds = seconds
        self.tracker = ValueTracker(float(seconds))
        self.center_dot = Dot(radius=0.001, fill_opacity=0)
        track = Circle(radius=radius, stroke_color=T.FAINT, stroke_width=10)

        def ring():
            frac = max(self.tracker.get_value() / self.seconds, 0.0001)
            return Arc(radius=radius, start_angle=PI / 2, angle=TAU * frac, stroke_color=color,
                       stroke_width=10, arc_center=self.center_dot.get_center())

        def num():
            n = int(np.ceil(self.tracker.get_value() - 1e-6))
            return _txt(str(max(n, 0)), T.HEADING_SIZE, color=color, weight="BOLD") \
                .move_to(self.center_dot.get_center())
        self.add(self.center_dot, track, always_redraw(ring), always_redraw(num))

    def run(self):
        return self.tracker.animate(run_time=self.seconds, rate_func=linear).set_value(0)
