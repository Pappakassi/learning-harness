"""How does a machine learn? Gradient descent with Hr. Schiffel. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo.effects import Countdown, CountUp  # noqa: E402
from csvideo.story import P, StoryScene, halo, theme_intro, theme_outro, txt  # noqa: E402

SCENES = ["Intro", "Hook", "Loss", "Landscape", "Downhill", "Repeat", "RealModels", "Recap"]

RIDES = [(1, 3), (2, 5)]          # km, fare (thousand kr)
ETA = 0.05


def M(*parts, size=1.0, color=P.FG):
    return MathTex(*parts, color=color).scale(size)


def loss(w, b):
    return sum((w * x + b - y) ** 2 for x, y in RIDES)


def grad(w, b):
    e1, e2 = w + b - 3, 2 * w + b - 5
    return np.array([2 * e1 + 4 * e2, 2 * e1 + 2 * e2])


def descent(eta=ETA, steps=300, start=(0.0, 0.0)):
    p = np.array(start, dtype=float)
    path = [p.copy()]
    for _ in range(steps):
        p = p - eta * grad(*p)
        path.append(p.copy())
    return path


PATH = descent()


# ---------------- reusable pictures ----------------
def data_plot(center, w0=0.0, b0=0.0, size=1.0, wb=None):
    """km-vs-fare plot with the two rides and a model line driven by trackers w, b
    (or by wb(), a function returning (w, b), when given)."""
    ax = Axes(x_range=[0, 3, 1], y_range=[0, 7, 1], x_length=4.6 * size, y_length=3.9 * size,
              axis_config={"stroke_color": P.MUTED, "include_tip": False, "font_size": 22},
              x_axis_config={"numbers_to_include": [1, 2]}, y_axis_config={"numbers_to_include": [1, 3, 5]})
    ax.move_to(center)
    xl = txt("km", size=20, color=P.MUTED).next_to(ax.x_axis.get_end(), DOWN, buff=0.15)
    yl = txt("fare (1000 kr)", size=20, color=P.MUTED).next_to(ax.y_axis.get_end(), UP, buff=0.12)
    dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.09, color=P.GOLD).set_z_index(5) for x, y in RIDES])
    w, b = ValueTracker(w0), ValueTracker(b0)
    cur = wb or (lambda: (w.get_value(), b.get_value()))
    line = always_redraw(lambda: Line(ax.c2p(0, cur()[1]), ax.c2p(3, cur()[0] * 3 + cur()[1]),
                                      color=P.BLUE, stroke_width=5))
    return SimpleGroup(ax=ax, labels=VGroup(xl, yl), dots=dots, line=line, w=w, b=b)


class SimpleGroup:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def all(self):
        return VGroup(self.ax, self.labels, self.dots, self.line)


def loss_map(center, w_range=(-0.5, 3.0), b_range=(-1.0, 2.5), length=4.4, levels=(0.05, 0.3, 1, 3, 8, 20, 34)):
    """Top-down map of the loss: axes w (east) and b (north), contour rings of L."""
    ax = Axes(x_range=[w_range[0], w_range[1], 1], y_range=[b_range[0], b_range[1], 1], x_length=length,
              y_length=length * (b_range[1] - b_range[0]) / (w_range[1] - w_range[0]),
              axis_config={"stroke_color": P.MUTED, "include_tip": False, "font_size": 20},
              x_axis_config={"numbers_to_include": [0, 1, 2]}, y_axis_config={"numbers_to_include": [0, 1, 2]})
    ax.move_to(center)
    (x0, y0, _), (x1, y1, _) = ax.c2p(w_range[0], b_range[0]), ax.c2p(w_range[1], b_range[1])
    rings = VGroup()
    for i, c in enumerate(levels):
        col = interpolate_color(ManimColor(P.TEAL), ManimColor(P.PURPLE), i / max(1, len(levels) - 1))
        f = ImplicitFunction(lambda X, Y, c=c: loss(*ax.p2c([X, Y, 0])) - c, x_range=[x0, x1], y_range=[y0, y1],
                             color=col, stroke_width=2.2, min_depth=6, max_quads=2500)
        rings.add(f)
    rings.set_stroke(opacity=0.75)
    wl = txt("w  (price per km)", size=20, color=P.MUTED).next_to(ax.x_axis, DOWN, buff=0.38)
    bl = txt("b  (start fee)", size=20, color=P.MUTED).next_to(ax.y_axis.get_end(), UP, buff=0.12)
    star = Star(n=5, outer_radius=0.14, color=P.GREEN, fill_opacity=1).move_to(ax.c2p(2, 1)).set_z_index(4)
    return SimpleGroup(ax=ax, rings=rings, labels=VGroup(wl, bl), star=star)


# ---------------- scenes ----------------
class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "How does a machine learn?", "gradient descent, with Hr. Schiffel")
        self.wait(0.3)


class Hook(StoryScene):
    def construct(self):
        g = self.add_gnome("fierce", animate=False)
        d = data_plot([-2.6, 0.1, 0])
        with self.say("A taxi app in Akureyri wants to guess fares. It has seen exactly two rides."):
            self.play(Create(d.ax), FadeIn(d.labels), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(p, scale=2) for p in d.dots], lag_ratio=0.4))
        tags = VGroup(txt("1 km: 3000 kr", size=22, color=P.GOLD).next_to(d.dots[0], RIGHT, buff=0.15),
                      txt("2 km: 5000 kr", size=22, color=P.GOLD).next_to(d.dots[1], RIGHT, buff=0.15))
        with self.say("One kilometre cost three thousand krónur. Two kilometres cost five thousand."):
            self.play(FadeIn(tags, shift=LEFT * 0.1))
        rule = M(r"\text{fare}", r"=", r"w", r"\cdot \text{km}", r"+", r"b", size=1.15).move_to([3.2, 1.7, 0])
        rule[2].set_color(P.PINK)
        rule[5].set_color(P.TEAL)
        knobs = VGroup(txt("w = price per km", size=24, color=P.PINK), txt("b = start fee", size=24, color=P.TEAL)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(rule, DOWN, buff=0.45)
        with self.say("The app's model is a straight line. Two knobs: w, the price per kilometre, and b, the start fee."):
            self.play(Write(rule), run_time=1.2)
            self.play(FadeIn(knobs, shift=UP * 0.1))
        with self.say("At first both knobs are at zero. Every ride is free. Very wrong."):
            self.play(Create(d.line), run_time=1.0)
            self.play(Indicate(d.line, color=P.RED), run_time=1.0)
        q = txt("?", size=96, color=P.YELLOW, weight="BOLD").move_to([3.2, -1.2, 0])
        with self.say("Nobody tells the app the real price rule. Yet a few hundred tiny steps later, it knows it. How?"):
            self.play(FadeIn(q, scale=0.5))
            self.play(d.w.animate.set_value(2), d.b.animate.set_value(1), run_time=2.0)
            self.play(d.w.animate.set_value(0), d.b.animate.set_value(0), run_time=0.8)
        with self.say("Easy. It guesses randomly until it gets lucky!", who="gnome"):
            self.play(g.change("happy"), g.hop())
        with self.say("Not quite. It uses exactly the calculus from your exam."):
            self.play(g.change("surprised"))
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g,)], g.change("fierce"), run_time=0.8)


class Loss(StoryScene):
    def construct(self):
        self.chapter("1. Measure the mistake", label="1  Loss")
        g = self.add_gnome("thinking", animate=False)
        d = data_plot([-3.3, 0.0, 0])
        self.add(d.ax, d.labels, d.dots, d.line)
        bars = VGroup(*[Line(d.ax.c2p(x, 0), d.ax.c2p(x, y), color=P.RED, stroke_width=6) for x, y in RIDES])
        errs = VGroup(txt("off by 3", size=22, color=P.RED).next_to(bars[0], RIGHT, buff=0.12),
                      txt("off by 5", size=22, color=P.RED).next_to(bars[1], RIGHT, buff=0.12))
        with self.say("First, the app measures how wrong it is. For each ride: the guess, minus the real fare."):
            self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.4), run_time=1.2)
            self.play(FadeIn(errs))
        sq = M(r"(0-3)^2", r"+", r"(0-5)^2", r"=", r"9", r"+", r"25", r"=", r"34", size=1.0).move_to([2.9, 1.8, 0])
        sq[8].set_color(P.RED)
        with self.say("Square each error, so misses in both directions count, and add them up. Nine plus twenty-five is thirty-four."):
            self.play(Write(sq[:3]), run_time=1.2)
            self.play(Write(sq[3:]), run_time=1.2)
        name = txt("the loss", size=30, color=P.RED, weight="BOLD").next_to(sq, DOWN, buff=0.35)
        with self.say("That number is called the loss. Big loss, bad model. Zero loss, perfect model."):
            self.play(FadeIn(name, shift=UP * 0.1), FadeIn(halo(sq[8], P.RED)))
        gen = M(r"L(", r"w", r",", r"b", r")", r"=", r"(w\cdot 1 + b - 3)^2", r"+", r"(w\cdot 2 + b - 5)^2",
                size=0.75).move_to([3.1, -0.6, 0])
        gen[1].set_color(P.PINK)
        gen[3].set_color(P.TEAL)
        with self.say("With the knobs as letters, the loss is a function of two variables: L of w and b."):
            self.play(Write(gen), run_time=1.8)
        with self.say("Two variables. Just like f of x and y on your exam. Only the letters changed."):
            self.play(Indicate(gen[:5], color=P.YELLOW), run_time=1.2)
        with self.say("Squares? Aha. So small mistakes are cheap and big ones hurt. Like my hat budget.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class Landscape(StoryScene):
    def construct(self):
        self.chapter("2. The loss is a landscape", label="2  Landscape")
        g = self.add_gnome("fierce", animate=False)
        mp = loss_map([-1.2, 0.05, 0])
        with self.say("Here's a map. East is the price knob w. North is the start-fee knob b. Every spot is one possible model."):
            self.play(Create(mp.ax), FadeIn(mp.labels), run_time=1.2)
        with self.say("The rings show the height: the loss at that spot, like on a hiking map."):
            self.play(LaggedStart(*[Create(r) for r in reversed(mp.rings)], lag_ratio=0.15), run_time=2.6)
        here = Dot(mp.ax.c2p(0, 0), radius=0.11, color=P.PINK).set_z_index(6)
        hl = txt("start: L = 34", size=22, color=P.PINK).next_to(here, DL, buff=0.08)
        with self.say("Our clueless start, w zero and b zero, sits high up on the slope. Loss thirty-four."):
            self.play(FadeIn(here, scale=2), FadeIn(hl))
        sl = txt("L = 0", size=22, color=P.GREEN).next_to(mp.star, RIGHT, buff=0.12)
        with self.say("Somewhere there's a lowest point, where the loss is zero. That's the model we want."):
            self.play(FadeIn(mp.star, scale=2), FadeIn(sl))
            self.play(Flash(mp.star, color=P.GREEN, line_length=0.25))
        goal = txt("Training =\nwalking downhill", size=32, color=P.YELLOW, weight="BOLD").move_to([4.3, 0.8, 0])
        with self.say("So training a model means one thing: walk downhill on this landscape, until you reach the bottom."):
            self.play(FadeIn(goal, shift=LEFT * 0.2))
        with self.say("But the computer can't see the map. It only feels the slope right under its feet."):
            self.play(*[r.animate.set_stroke(opacity=0.12) for r in mp.rings], FadeOut(mp.star), FadeOut(sl), run_time=1.2)
        with self.say("Hiking blindfolded? Ach. I've done worse.", who="gnome"):
            self.play(g.change("angry"))
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class Downhill(StoryScene):
    def construct(self):
        self.chapter("3. Which way is downhill?", label="3  Gradient")
        g = self.add_gnome("thinking", animate=False)
        lw = M(r"\frac{\partial L}{\partial w}", r"=", r"2(w+b-3)", r"\cdot 1", r"+", r"2(2w+b-5)", r"\cdot 2", size=0.95)
        lb = M(r"\frac{\partial L}{\partial b}", r"=", r"2(w+b-3)", r"\cdot 1", r"+", r"2(2w+b-5)", r"\cdot 1", size=0.95)
        pair = VGroup(lw, lb).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([-0.6, 1.3, 0])
        with self.say("The slope under its feet is the partial derivatives. One for each knob."):
            self.play(Write(lw[:3]), Write(lb[:3]), run_time=1.6)
        with self.say("Each bracket is squared, so it's the chain rule: power down, times the derivative of the inside."):
            self.play(Write(lw[3:]), Write(lb[3:]), run_time=1.6)
            self.play(*[m.animate.set_color(P.YELLOW) for m in (lw[3], lw[6], lb[3], lb[6])], run_time=0.6)
        vals = M(r"\text{at } (0,0):\quad", r"\nabla L", r"=", r"(-26,\;-16)", size=1.0).next_to(pair, DOWN, buff=0.55)
        vals[3].set_color(P.RED)
        with self.say("Plug in our start, zero and zero. Minus six minus twenty, and minus six minus ten. The gradient is minus twenty-six, minus sixteen."):
            self.play(Write(vals), run_time=2.0)
        with self.say("Exactly the skills you drilled. Partial derivatives and the chain rule.", who="gnome"):
            self.play(g.change("happy"), g.hop())
        self.play(FadeOut(pair), vals.animate.scale(0.8).move_to([3.4, 2.3, 0]), g.change("fierce"), run_time=0.9)

        mp = loss_map([-3.0, -0.1, 0], length=4.0)
        mp.rings.set_stroke(opacity=0.45)
        here = Dot(mp.ax.c2p(0, 0), radius=0.1, color=P.PINK).set_z_index(6)
        self.play(FadeIn(mp.ax), FadeIn(mp.rings), FadeIn(mp.labels), FadeIn(here), run_time=0.8)
        o = mp.ax.c2p(0, 0)
        u = np.array([-26, -16, 0]) / np.linalg.norm([-26, -16])
        up_arrow = Arrow(o, o + 1.3 * u, buff=0, color=P.RED, stroke_width=6)
        upl = txt("uphill", size=22, color=P.RED).next_to(up_arrow.get_end(), DOWN, buff=0.1)
        with self.say("Careful. The gradient points uphill. The steepest way up, away from the bottom."):
            self.play(GrowArrow(up_arrow), FadeIn(upl))
        dn_arrow = Arrow(o, o - 1.3 * u, buff=0, color=P.GREEN, stroke_width=6)
        dnl = txt("downhill", size=22, color=P.GREEN).next_to(dn_arrow.get_end(), RIGHT, buff=0.1)
        with self.say("We want down. So we flip it, and step the opposite way. That's the minus sign in training."):
            self.play(TransformFromCopy(up_arrow, dn_arrow), FadeIn(dnl), run_time=1.2)
        rule = M(r"w_{\text{new}}", r"=", r"w", r"-", r"0.05", r"\cdot", r"\frac{\partial L}{\partial w}", size=1.0).move_to([3.3, 1.0, 0])
        rule[4].set_color(P.YELLOW)
        step = txt("0.05 = step size", size=22, color=P.YELLOW).next_to(rule, DOWN, buff=0.25)
        with self.say("The update rule: new w is old w, minus a small step size times the slope. Same for b."):
            self.play(Write(rule), run_time=1.4)
            self.play(FadeIn(step))
        plug = M(r"w_{\text{new}}", r"=", r"0", r"-", r"0.05", r"\cdot", r"(-26)", r"=", r"\;?", size=0.95).next_to(step, DOWN, buff=0.45)
        q = txt("your turn", size=26, color=P.YELLOW, weight="BOLD").next_to(plug, DOWN, buff=0.35).shift(LEFT * 0.6)
        with self.say("Your turn. Zero, minus zero point zero five, times minus twenty-six. What's the new w?"):
            self.play(Write(plug), FadeIn(q), run_time=1.4)
        cd = Countdown(3).next_to(q, RIGHT, buff=0.4)
        self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        self.play(FadeOut(cd), FadeOut(q), run_time=0.3)
        ans = M(r"1.3", size=0.95, color=P.GREEN).move_to(plug[8]).align_to(plug[8], LEFT)
        bnew = M(r"b_{\text{new}}", r"=", r"0 - 0.05\cdot(-16)", r"=", r"0.8", size=0.95).next_to(plug, DOWN, buff=0.3).align_to(plug, LEFT)
        bnew[4].set_color(P.GREEN)
        with self.say("Minus times minus is plus. One point three. And b becomes zero point eight."):
            self.play(Transform(plug[8], ans), run_time=0.8)
            self.play(Write(bnew), run_time=1.2)
        new = Dot(mp.ax.c2p(1.3, 0.8), radius=0.1, color=P.PINK).set_z_index(6)
        trail = Line(o, new.get_center(), color=P.PINK, stroke_width=3)
        lnew = M(r"L:\; 34 \;\to\; 3.37", size=0.95, color=P.GREEN).next_to(bnew, DOWN, buff=0.35).align_to(bnew, LEFT)
        with self.say("One step, and the loss drops from thirty-four to about three point four. Ten times better."):
            self.play(FadeOut(up_arrow), FadeOut(upl), FadeOut(dn_arrow), FadeOut(dnl), run_time=0.4)
            self.play(Create(trail), here.animate.move_to(new), run_time=1.0)
            self.play(Write(lnew), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], run_time=0.8)


class Repeat(StoryScene):
    def construct(self):
        self.chapter("4. Repeat, repeat, repeat", label="4  Training")
        g = self.add_gnome("fierce", animate=False)
        k = ValueTracker(0)

        def pos():
            t = k.get_value()
            i = min(int(t), len(PATH) - 2)
            a = t - i
            return PATH[i] * (1 - a) + PATH[i + 1] * a

        d = data_plot([-3.5, 0.35, 0], size=0.85, wb=pos)
        mp = loss_map([2.6, 0.2, 0], length=3.9)
        mp.rings.set_stroke(opacity=0.5)
        dot = always_redraw(lambda: Dot(mp.ax.c2p(*pos()), radius=0.1, color=P.PINK).set_z_index(6))
        trail = always_redraw(lambda: VMobject(stroke_color=P.PINK, stroke_width=3).set_points_as_corners(
            [mp.ax.c2p(*p) for p in PATH[:int(k.get_value()) + 1]] + [mp.ax.c2p(*pos())]))
        step_lbl = always_redraw(lambda: txt(f"step {int(round(k.get_value()))}", size=24, color=P.MUTED)
                                 .move_to([-3.5, 2.45, 0]))
        loss_lbl = always_redraw(lambda: txt(f"loss {loss(*pos()):.2f}", size=28, color=P.RED, weight="BOLD")
                                 .next_to(step_lbl, RIGHT, buff=0.5))
        with self.say("Now just do it again. And again. Left, the app's guess line. Right, where it stands on the map."):
            self.play(FadeIn(d.all()), FadeIn(mp.ax), FadeIn(mp.rings), FadeIn(mp.labels), FadeIn(mp.star), run_time=1.0)
            self.add(trail, dot, step_lbl, loss_lbl)
            self.wait(0.5)
        with self.say("Step one. Step two. Step three. Huge drops: thirty-four, three point four, zero point three, zero point zero four."):
            for i in range(1, 4):
                self.play(k.animate.set_value(i), run_time=1.0, rate_func=smooth)
                self.wait(0.4)
        with self.say("Then it slows down. The bottom is a long, narrow valley, and it creeps along the valley floor."):
            self.play(k.animate.set_value(60), run_time=4.0, rate_func=linear)
        with self.say("Three hundred steps later, it arrives. The line runs straight through both rides."):
            self.play(k.animate.set_value(300), run_time=3.0, rate_func=rate_functions.ease_out_sine)
            self.play(Flash(mp.star, color=P.GREEN, line_length=0.25), Indicate(d.line, color=P.GREEN), run_time=1.0)
        res = M(r"w = 2,\quad b = 1", size=1.0, color=P.GREEN).move_to([-3.5, -2.35, 0])
        with self.say("w is two, b is one. Two thousand per kilometre, plus a thousand to start. Nobody told it that."):
            self.play(Write(res), run_time=1.2)
        self.play(*[FadeOut(m) for m in (trail, dot, step_lbl, loss_lbl, d.all(), mp.ax, mp.rings, mp.labels, mp.star)],
                  res.animate.move_to(UP * 1.9).scale(1.2), run_time=1.0)
        flat = M(r"\frac{\partial L}{\partial w} = 0", r",\qquad", r"\frac{\partial L}{\partial b} = 0", size=1.0).move_to(UP * 0.4)
        note = txt("the flat spot = a critical point (a minimum)", size=28, color=P.YELLOW).next_to(flat, DOWN, buff=0.45)
        with self.say("At the bottom the ground is flat. Both partial derivatives are zero."):
            self.play(Write(flat), run_time=1.4)
        with self.say("That's a critical point, a minimum. Exactly what exam problem five asks you to find, by hand."):
            self.play(FadeIn(note, shift=UP * 0.1))
        with self.say("By hand, with two knobs. Computers walk, because they have billions.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(*[FadeOut(m) for m in (res, flat, note)], g.change("fierce"), run_time=0.8)


class RealModels(StoryScene):
    def construct(self):
        self.chapter("5. Real models", label="5  Real models")
        g = self.add_gnome("surprised", animate=False)
        knobs = CountUp("knobs", 2, size=40, color=P.YELLOW).move_to(UP * 2.0)
        with self.say("Our taxi model had two knobs. Real models have many more."):
            self.play(FadeIn(knobs))
        ex = VGroup(*[VGroup(txt(a, size=26, weight="BOLD"), txt(b, size=22, color=P.MUTED)).arrange(DOWN, buff=0.12)
                      for a, b in (("spam filter", "thousands"), ("photo app", "millions"), ("chatbot", "billions"))]
                    ).arrange(RIGHT, buff=1.1).move_to(UP * 0.6)
        with self.say("A spam filter: thousands. An app that recognises photos: millions. A chatbot: billions."):
            self.play(FadeIn(ex[0], shift=UP * 0.1), knobs.to(5000, run_time=1.0, log=True))
            self.play(FadeIn(ex[1], shift=UP * 0.1), knobs.to(25_000_000, run_time=1.0, log=True))
            self.play(FadeIn(ex[2], shift=UP * 0.1), knobs.to(1_000_000_000, run_time=1.2, log=True))
        with self.say("Same recipe for all of them. Loss, gradient, step downhill. Billions of times."):
            self.play(Indicate(knobs, color=P.GOLD), run_time=1.2)
        self.play(FadeOut(ex), knobs.animate.scale(0.7).move_to(UP * 2.4 + RIGHT * 3.6), run_time=0.7)
        names = ["input", "layer 1", "layer 2", "layer 3", "loss"]
        cols = [P.MUTED, P.BLUE, P.BLUE, P.BLUE, P.RED]
        boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.15, width=1.75, height=0.8, stroke_color=c, stroke_width=3),
                                txt(n, size=22, color=c)) for n, c in zip(names, cols)]).arrange(RIGHT, buff=0.55).move_to(UP * 0.3)
        fwd = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.08, color=P.MUTED, stroke_width=4,
                             max_tip_length_to_length_ratio=0.3) for i in range(4)])
        with self.say("A real model is stacked in layers. Each layer is a function, fed into the next one."):
            self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.1) for b in boxes], lag_ratio=0.2), run_time=1.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in fwd], lag_ratio=0.2), run_time=1.0)
        nest = M(r"L\big(\,f_3(\,f_2(\,f_1(x)\,)\,)\,\big)", size=1.0).next_to(boxes, DOWN, buff=0.55)
        with self.say("So the loss is a function inside a function inside a function."):
            self.play(Write(nest), run_time=1.4)
        back = VGroup(*[CurvedArrow(boxes[i + 1].get_bottom() + DOWN * 0.05, boxes[i].get_bottom() + DOWN * 0.05,
                                    angle=-PI / 2.2, color=P.GOLD, stroke_width=4) for i in range(3, -1, -1)])
        cr = txt("chain rule, layer by layer, backwards", size=24, color=P.GOLD).next_to(nest, DOWN, buff=0.4)
        with self.say("To get the slope, you use the chain rule. Outer derivative, times the inside's derivative, layer by layer, from the back."):
            self.play(FadeOut(nest), run_time=0.3)
            self.play(LaggedStart(*[Create(a) for a in back], lag_ratio=0.35), FadeIn(cr), run_time=2.2)
        bp = txt("backpropagation", size=40, color=P.YELLOW, weight="BOLD").next_to(cr, DOWN, buff=0.3)
        with self.say("That has a famous name: backpropagation. It's just your chain rule, run very many times."):
            self.play(Write(bp), run_time=1.0)
            self.play(FadeIn(halo(bp, P.YELLOW)), run_time=0.5)
        with self.say("Power down, times the inside. A billion times. My poor pencil.", who="gnome"):
            self.play(g.change("angry"))
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class Recap(StoryScene):
    def construct(self):
        self.chapter("The recipe", label="Recipe")
        g = self.add_gnome("lecturing", animate=False)
        steps = VGroup(*[txt(s, size=30) for s in (
            "1.  Loss: measure the mistake as a function of the knobs",
            "2.  Gradient: partial derivatives (chain rule!) point uphill",
            "3.  Step the other way:  w  ←  w  −  step · slope",
            "4.  Repeat until the ground is flat",
        )]).arrange(DOWN, aligned_edge=LEFT, buff=0.36).move_to(UP * 0.9)
        for s, c in zip(steps, (P.RED, P.YELLOW, P.GREEN, P.BLUE)):
            s[0:2].set_color(c)
        with self.say("That's how a machine learns. Measure the mistake. Find the slope. Step downhill. Repeat."):
            for s in steps:
                self.play(FadeIn(s, shift=RIGHT * 0.2), run_time=0.6)
        self.play(steps.animate.scale(0.7).to_edge(UP, buff=0.95), run_time=0.7)
        mp = loss_map([-1.6, -0.75, 0], w_range=(-5.0, 6.0), b_range=(-3.5, 4.5), length=3.3, levels=(1, 8, 34, 100, 300))
        mp.rings.set_stroke(opacity=0.5)
        bad = [np.array([0.0, 0.0]), np.array([5.2, 3.2]), np.array([-3.84, -2.4])]
        dot = Dot(mp.ax.c2p(*bad[0]), radius=0.09, color=P.PINK).set_z_index(6)
        with self.say("One last thing. What if the step size is too big? Say zero point two instead of zero point zero five."):
            self.play(FadeIn(mp.ax), FadeIn(mp.rings), FadeIn(mp.star), FadeIn(dot), run_time=0.8)
        nums = M(r"L:\; 34", size=0.95, color=P.RED).move_to([3.4, -0.3, 0])
        with self.say("It overshoots the valley. Thirty-four. Then a hundred and three. Then three hundred and thirteen."):
            self.play(FadeIn(nums))
            for p, s in zip(bad[1:], (r"L:\; 34 \to 103", r"L:\; 34 \to 103 \to 313")):
                seg = Line(dot.get_center(), mp.ax.c2p(*p), color=P.PINK, stroke_width=3)
                self.play(Create(seg), dot.animate.move_to(mp.ax.c2p(*p)),
                          Transform(nums, M(s, size=0.95, color=P.RED).move_to([3.4, -0.3, 0])), run_time=0.9)
        with self.say("Choosing the step size is an art of its own. That's the next video."):
            self.play(Indicate(nums, color=P.GOLD), run_time=1.0)
        with self.say("Small steps! Like a gnome on ice.", who="gnome"):
            self.play(g.change("happy"), g.hop())
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], run_time=0.6)
        theme_outro(self)
