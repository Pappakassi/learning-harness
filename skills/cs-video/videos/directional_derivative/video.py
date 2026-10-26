"""How steep is the hill? The directional derivative, with Hr. Schiffel. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo.effects import Countdown  # noqa: E402
from csvideo.story import P, StoryScene, halo, theme_intro, theme_outro, txt  # noqa: E402

SCENES = ["Intro", "Hook", "Partials", "Gradient", "UnitVector", "DotProduct", "Recipe"]


def M(*parts, size=1.0, color=P.FG):
    return MathTex(*parts, color=color).scale(size)


class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "How steep is the hill?", "the directional derivative, with Hr. Schiffel")
        self.wait(0.3)


class Hook(StoryScene):
    def construct(self):
        g = self.add_gnome("fierce", animate=False)
        c = np.array([0.6, 0.6, 0])
        rings = VGroup(*[Ellipse(width=1.3 * k, height=0.9 * k, stroke_color=interpolate_color(ManimColor(P.TEAL), ManimColor(P.BLUE), k / 6),
                                 stroke_width=2.5, stroke_opacity=0.35 + 0.08 * (6 - k)).move_to(c) for k in range(1, 7)])
        top = Dot(c, radius=0.07, color=P.GOLD)
        peak = txt("top", size=22, color=P.GOLD).next_to(top, UP, buff=0.12)
        hiker = Dot(c + np.array([-2.55, -1.0, 0]), radius=0.11, color=P.PINK).set_z_index(5)
        with self.say("Here's a hill, seen from above. Each ring is one height, like on a hiking map."):
            self.play(LaggedStart(*[Create(r) for r in reversed(rings)], lag_ratio=0.15), run_time=2.2)
            self.play(FadeIn(top), FadeIn(peak))
        with self.say("You're standing here. Which way you walk changes how steep it feels."):
            self.play(FadeIn(hiker, scale=2))
        p = hiker.get_center()
        up = (c - p) / np.linalg.norm(c - p)
        side = np.array([-up[1], up[0], 0])
        diag = (up + 0.5 * side) / np.linalg.norm(up + 0.5 * side)
        a1 = Arrow(p, p + 1.5 * up, buff=0, color=P.RED, stroke_width=6)
        a2 = Arrow(p, p + 1.9 * side, buff=0, color=P.GREEN, stroke_width=6)
        a3 = Arrow(p, p + 1.9 * diag, buff=0, color=P.YELLOW, stroke_width=6)
        l1 = txt("steep", size=24, color=P.RED).move_to(a1.get_center() + np.array([0.15, -0.35, 0]))
        l2 = txt("flat", size=24, color=P.GREEN).next_to(a2.get_end(), LEFT, buff=0.12)
        l3 = txt("somewhere\nin between", size=22, color=P.YELLOW).next_to(a3.get_end(), RIGHT, buff=0.12)
        with self.say("Straight at the top, it's steep. Along a ring, it's flat. In between, somewhere in between."):
            self.play(GrowArrow(a1), FadeIn(l1), run_time=0.9)
            self.play(GrowArrow(a2), FadeIn(l2), run_time=0.9)
            self.play(GrowArrow(a3), FadeIn(l3), run_time=0.9)
        with self.say("The directional derivative answers one question: how steep is it in the direction I choose?"):
            self.play(Indicate(a3, color=P.YELLOW, scale_factor=1.15), run_time=1.4)
        with self.say("Ach, I don't walk around hills. I go straight up. Like a proper gnome.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(*[FadeOut(m) for m in (rings, top, peak, hiker, a1, a2, a3, l1, l2, l3)], g.change("fierce"), run_time=0.8)


class Partials(StoryScene):
    def construct(self):
        self.chapter("1. Partial derivatives", label="1  Partials")
        g = self.add_gnome("thinking", animate=False)
        f = M(r"f(x,y)", r"=", r"x^2", r"\,y", size=1.3).move_to(UP * 1.9)
        with self.say("Our hill is f of x and y, equals x squared times y. Two inputs: east, and north."):
            self.play(Write(f), run_time=1.4)
        east = Arrow(LEFT * 0.6, RIGHT * 0.6, buff=0, color=P.BLUE, stroke_width=6).move_to([-3.4, 0.7, 0])
        el = txt("walk east: only x changes", size=24, color=P.BLUE).next_to(east, DOWN, buff=0.2)
        fx1 = M(r"\frac{\partial f}{\partial x}", r"=", r"2x", r"\cdot", r"y", size=1.1).next_to(el, DOWN, buff=0.45)
        fx1[4].set_color(P.GOLD)
        with self.say("Walk east, and only x changes. So y is frozen. It acts like a plain number."):
            self.play(GrowArrow(east), FadeIn(el))
            self.play(f[3].animate.set_color(P.GOLD), run_time=0.6)
        with self.say("x squared gives two x, and the frozen y is copied along, untouched. Two x y."):
            self.play(Write(fx1), run_time=1.4)
        north = Arrow(DOWN * 0.6, UP * 0.6, buff=0, color=P.PINK, stroke_width=6).move_to([3.4, 0.7, 0])
        nl = txt("walk north: only y changes", size=24, color=P.PINK).next_to(north, DOWN, buff=0.2)
        fy1 = M(r"\frac{\partial f}{\partial y}", r"=", r"x^2", r"\cdot", r"1", r"=x^2", size=1.1).next_to(nl, DOWN, buff=0.45)
        fy1[2].set_color(P.GOLD)
        with self.say("Walk north, and now x is frozen. x squared is just a number sitting in front of y."):
            self.play(f[3].animate.set_color(P.FG), f[2].animate.set_color(P.GOLD), GrowArrow(north), FadeIn(nl), run_time=1.0)
        with self.say("y differentiates to one, and x squared is copied. So the answer is x squared."):
            self.play(Write(fy1), run_time=1.4)
        with self.say("Freeze it. Copy it. Never differentiate the frozen one. Simple!", who="gnome"):
            self.play(g.change("happy"), g.hop())
        self.play(*[FadeOut(m) for m in (f, east, el, fx1, north, nl, fy1)], g.change("fierce"), run_time=0.8)


class Gradient(StoryScene):
    def construct(self):
        self.chapter("2. The gradient", label="2  Gradient")
        g = self.add_gnome("fierce", animate=False)
        grad = M(r"\nabla f", r"=", r"\big(", r"2xy", r",\;", r"x^2", r"\big)", size=1.2).move_to([-3.3, 1.4, 0])
        grad[3].set_color(P.BLUE)
        grad[5].set_color(P.PINK)
        with self.say("Put the two slopes side by side in a bracket. That's the gradient, written with an upside-down triangle."):
            self.play(Write(grad), run_time=1.6)
        at = M(r"\nabla f(3,1)", r"=", r"\big(", r"2\cdot 3\cdot 1", r",\;", r"3^2", r"\big)", size=1.0).next_to(grad, DOWN, buff=0.6).align_to(grad, LEFT)
        res = M(r"=", r"(6,\;9)", size=1.2, color=P.YELLOW).next_to(at, DOWN, buff=0.4).align_to(at, LEFT)
        with self.say("At the point three, one: two times three times one is six. Three squared is nine."):
            self.play(FadeIn(at, shift=DOWN * 0.2), run_time=1.0)
            self.play(Write(res), run_time=0.8)
        plane = NumberPlane(x_range=[-1, 10, 1], y_range=[-1, 10, 1], x_length=4.4, y_length=4.4,
                            background_line_style={"stroke_color": P.FAINT, "stroke_width": 1},
                            axis_config={"stroke_color": P.MUTED}).move_to([3.4, -0.2, 0])
        vec = Arrow(plane.c2p(0, 0), plane.c2p(6, 9), buff=0, color=P.YELLOW, stroke_width=6)
        vl = M(r"(6,9)", size=0.9, color=P.YELLOW).next_to(vec.get_end(), LEFT, buff=0.15)
        with self.say("Drawn as an arrow, six across and nine up."):
            self.play(Create(plane), run_time=1.0)
            self.play(GrowArrow(vec), FadeIn(vl))
        with self.say("And it always points the steepest way uphill. Straight at the top of the hill."):
            self.play(Indicate(vec, color=P.GOLD, scale_factor=1.08), Flash(vec.get_end(), color=P.YELLOW, line_length=0.3), run_time=1.2)
        with self.say("Steepest way up! Now we're talking.", who="gnome"):
            self.play(g.change("happy"), g.hop())
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class UnitVector(StoryScene):
    def construct(self):
        self.chapter("3. A unit vector", label="3  Unit vector")
        g = self.add_gnome("thinking", animate=False)
        plane = NumberPlane(x_range=[-1, 5, 1], y_range=[-1, 5, 1], x_length=4.8, y_length=4.8,
                            background_line_style={"stroke_color": P.FAINT, "stroke_width": 1},
                            axis_config={"stroke_color": P.MUTED}).move_to([-3.2, -0.1, 0])
        o = plane.c2p(0, 0)
        v = Arrow(o, plane.c2p(3, 4), buff=0, color=P.TEAL, stroke_width=6)
        with self.say("Now pick the direction you want to walk. Say three across and four up."):
            self.play(Create(plane), run_time=0.8)
            self.play(GrowArrow(v))
        leg1 = Line(o, plane.c2p(3, 0), color=P.MUTED, stroke_width=4)
        leg2 = Line(plane.c2p(3, 0), plane.c2p(3, 4), color=P.MUTED, stroke_width=4)
        t3 = M("3", size=0.9).next_to(leg1, DOWN, buff=0.1)
        t4 = M("4", size=0.9).next_to(leg2, RIGHT, buff=0.1)
        length = M(r"|(3,4)|", r"=", r"\sqrt{3^2+4^2}", r"=", r"\sqrt{25}", r"=", r"5", size=1.0).move_to([3.2, 1.3, 0])
        length[6].set_color(P.TEAL)
        with self.say("Its length comes from Pythagoras. Three squared plus four squared is twenty-five. The root is five."):
            self.play(Create(leg1), Create(leg2), FadeIn(t3), FadeIn(t4))
            self.play(Write(length), run_time=1.6)
        unit = M(r"\hat u", r"=", r"\left(\tfrac{3}{5},\;\tfrac{4}{5}\right)", size=1.2, color=P.TEAL).next_to(length, DOWN, buff=0.8)
        circ = Circle(radius=plane.x_axis.unit_size, color=P.TEAL, stroke_opacity=0.4).move_to(o)
        short = Arrow(o, plane.c2p(0.6, 0.8), buff=0, color=P.TEAL, stroke_width=6, max_tip_length_to_length_ratio=0.35)
        with self.say("We only care about the direction, not how far. So shrink it to length one: divide both numbers by five."):
            self.play(Write(unit), run_time=1.0)
            self.play(Create(circ), Transform(v, short), FadeOut(leg1), FadeOut(leg2), FadeOut(t3), FadeOut(t4), run_time=1.4)
        with self.say("Same direction, length exactly one. That's a unit vector, written with a little hat."):
            self.play(Indicate(unit, color=P.TEAL), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class DotProduct(StoryScene):
    def construct(self):
        self.chapter("4. The dot product", label="4  Dot product")
        g = self.add_gnome("fierce", animate=False)
        rule = M(r"(a,\,b)\cdot(c,\,d)", r"=", r"ac + bd", size=1.1).move_to(UP * 1.9)
        with self.say("Last skill. To dot two vectors, multiply the matching parts and add. You get one number."):
            self.play(Write(rule), run_time=1.4)
        lhs = M(r"D_{\hat u}f", r"=", r"\nabla f", r"\cdot", r"\hat u", size=1.1).move_to(UP * 0.7)
        lhs[2].set_color(P.YELLOW)
        lhs[4].set_color(P.TEAL)
        with self.say("And the slope in our direction is the gradient, dotted with the unit vector. That's the directional derivative."):
            self.play(FadeIn(lhs, shift=UP * 0.2), run_time=1.0)
        a = M(r"(", r"6", r",\;", r"9", r")", size=1.3, color=P.YELLOW)
        dot = M(r"\cdot", size=1.3)
        b = M(r"\big(", r"\tfrac{3}{5}", r",\;", r"\tfrac{4}{5}", r"\big)", size=1.3, color=P.TEAL)
        row = VGroup(a, dot, b).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.6)
        with self.say("For our hill: six, nine, dotted with three fifths, four fifths."):
            self.play(FadeIn(row, shift=UP * 0.2))
        c1 = CurvedArrow(a[1].get_bottom() + DOWN * 0.1, b[1].get_bottom() + DOWN * 0.1, angle=PI / 2.5, color=P.GOLD)
        c2 = CurvedArrow(a[3].get_bottom() + DOWN * 0.1, b[3].get_bottom() + DOWN * 0.1, angle=PI / 2.8, color=P.PINK)
        q = txt("your turn", size=28, color=P.YELLOW, weight="BOLD").move_to([4.2, 1.2, 0])
        with self.say("Your turn. Multiply the matching parts and add them up."):
            self.play(Create(c1), Create(c2), FadeIn(q))
        cd = Countdown(3).move_to([4.2, 0.0, 0])
        self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        self.play(FadeOut(cd), FadeOut(q), run_time=0.3)
        ans = M(r"6\cdot\tfrac{3}{5}", r"+", r"9\cdot\tfrac{4}{5}", r"=", r"\tfrac{18}{5}", r"+", r"\tfrac{36}{5}", r"=", r"\tfrac{54}{5}",
                size=1.15).move_to(DOWN * 2.0)
        ans[8].set_color(P.GREEN)
        with self.say("Six times three fifths is eighteen fifths. Nine times four fifths is thirty-six fifths."):
            self.play(Write(ans[:7]), run_time=2.0)
        with self.say("Together, fifty-four fifths. About ten point eight. That's how steep it is in our direction."):
            self.play(Write(ans[7:]), run_time=1.0)
            self.play(FadeIn(halo(ans[8], P.GREEN)), run_time=0.6)
        with self.say("Ten point eight? Steep. My knees are already complaining.", who="gnome"):
            self.play(g.change("surprised"), g.hop())
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (g, self._title)], g.change("fierce"), run_time=0.8)


class Recipe(StoryScene):
    def construct(self):
        self.chapter("The exam recipe", label="Recipe")
        g = self.add_gnome("lecturing", animate=False)
        steps = VGroup(*[txt(s, size=30) for s in (
            "1.  Partial derivatives: freeze the other variable",
            "2.  Gradient: put them in a bracket, plug in the point",
            "3.  Unit vector: divide the direction by its length",
            "4.  Dot product: multiply matching parts, add",
        )]).arrange(DOWN, aligned_edge=LEFT, buff=0.38).move_to(UP * 0.5)
        cols = (P.BLUE, P.YELLOW, P.TEAL, P.GREEN)
        for s, c in zip(steps, cols):
            s[0:2].set_color(c)
        with self.say("So on the exam, it's always the same four steps."):
            self.play(FadeIn(steps[0], shift=RIGHT * 0.2), run_time=0.6)
        with self.say("Partials. Gradient at the point. Unit vector. Dot product. Done."):
            for s in steps[1:]:
                self.play(FadeIn(s, shift=RIGHT * 0.2), run_time=0.6)
        tease = M(r"\text{steepest slope} = |\nabla f| = \sqrt{6^2+9^2} = \sqrt{117} \approx 10.8", size=0.85, color=P.YELLOW).move_to(DOWN * 1.9 + LEFT * 0.7)
        with self.say("One last thing. Walk along the gradient itself, and you get the steepest slope of all: the length of the gradient."):
            self.play(Write(tease), run_time=1.8)
        with self.say("Almost the same as our ten point eight. Our direction was nearly straight up the hill already."):
            self.play(Indicate(tease, color=P.GOLD), run_time=1.2)
        with self.say("Four steps. Write every one down. The grader loves it.", who="gnome"):
            self.play(g.change("happy"))
        self.play(*[FadeOut(m) for m in (steps, tease)], run_time=0.6)
        theme_outro(self)
