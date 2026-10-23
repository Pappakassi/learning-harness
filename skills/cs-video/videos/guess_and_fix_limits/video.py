from manim import *
from csvideo import CSScene, Callout, make_text
from csvideo.effects import Countdown, glow, shake
from csvideo import theme as T

SCENES = ["Hook", "Rule", "Works", "Stuck", "YourTurn", "Recap"]

LX, RX = -3.5, 3.6


def M(*parts, size=1.0):
    return MathTex(*parts, color=T.FG).scale(size)


class Hook(CSScene):
    def construct(self):
        left = M(r"\int x\,e^{x^2}\,dx", size=1.5).move_to([LX, 0.6, 0])
        right = M(r"\int x\,e^{2x}\,dx", size=1.5).move_to([RX, 0.6, 0])
        with self.say("Here are two integrals that look almost the same. Only the exponent is different.") as t:
            self.play(FadeIn(left, shift=UP * 0.2), run_time=1)
            self.play(FadeIn(right, shift=UP * 0.2), run_time=1)
        tick = make_text("works", size=T.BODY_SIZE, color=T.GREEN, weight="BOLD").next_to(left, DOWN, buff=0.6)
        stuck = make_text("stuck ?", size=T.BODY_SIZE, color=T.RED, weight="BOLD").next_to(right, DOWN, buff=0.6)
        with self.say("Guess and fix solves the left one in three lines. On the right, it gets stuck.") as t:
            self.play(FadeIn(tick, scale=1.3), run_time=0.8)
            self.wait(0.6)
            self.play(FadeIn(stuck, scale=1.3), run_time=0.8)
            self.play(shake(right), run_time=0.6)
        with self.say("Why? The answer is one small test you can do in your head.") as t:
            self.play(Indicate(right, color=T.YELLOW), run_time=1.2)
        self.clear_content()
        self.show_title("Why guess and fix gets stuck")
        self.wait(0.6)


class Rule(CSScene):
    def construct(self):
        self.show_title("What the check does")
        guess = M(r"\text{guess: integrate the outer, keep the inside}", size=0.9).move_to(UP * 1.6)
        with self.say("Remember the method. You guess by integrating the outer function and keeping the inside.") as t:
            self.play(FadeIn(guess), run_time=1)
        chain = M(r"\big(e^{\square}\big)'", r"=", r"e^{\square}", r"\cdot", r"\square'", size=1.6).move_to(UP * 0.1)
        chain[4].set_color(T.YELLOW)
        with self.say("Then you check by differentiating. The chain rule always throws out one extra factor.") as t:
            self.play(Write(chain[:4]), run_time=1.5)
            self.play(FadeIn(chain[4], scale=1.6), run_time=0.8)
        g = glow(chain[4], color=T.YELLOW)
        lab = make_text("the inside's derivative", size=T.SMALL_SIZE, color=T.YELLOW).next_to(chain[4], DOWN, buff=0.45)
        with self.say("That factor is the inside's derivative. It's the only new thing the check can bring back.") as t:
            self.play(FadeIn(g), FadeIn(lab, shift=UP * 0.1), run_time=1)
        call = Callout("The extra piece in front has to come back from that factor.", color=T.YELLOW,
                       size=T.SMALL_SIZE + 2).move_to(DOWN * 1.7)
        with self.say("So whatever sits in front of the integral has to come back from that one factor.") as t:
            self.play(FadeIn(call, shift=UP * 0.2), run_time=1)
        self.wait(0.5)


class Works(CSScene):
    def construct(self):
        self.show_title("Case 1: it works")
        orig = M(r"\int", r"x", r"\,e^{x^2}\,dx", size=1.3).move_to([-3.2, 1.7, 0])
        orig[1].set_color(T.CYAN)
        guess = M(r"\text{guess: }", r"e^{x^2}", size=1.1)
        check = M(r"\text{check: }", r"e^{x^2}", r"\cdot", r"2x", size=1.1)
        check[3].set_color(T.YELLOW)
        fix = M(r"\text{fix: }", r"\tfrac{1}{2}\,e^{x^2}", size=1.1)
        fix[1].set_color(T.GREEN)
        steps = VGroup(guess, check, fix).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(orig, DOWN, buff=0.6).align_to(orig, LEFT)
        with self.say("Take the left one. The inside is x squared, so the guess is just e to the x squared.") as t:
            self.play(FadeIn(orig), run_time=0.8)
            self.play(FadeIn(guess, shift=RIGHT * 0.2), run_time=0.8)
        with self.say("Check it. The chain rule throws out the inside's derivative, two x.") as t:
            self.play(FadeIn(check[:3], shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(check[3], scale=1.5), run_time=0.7)
        arrow = CurvedArrow(check[3].get_right() + RIGHT * 0.15, orig[1].get_bottom() + DOWN * 0.12,
                            angle=PI / 2.2, color=T.GREEN)
        note = make_text("x is back on its own\nonly a 2 is extra", size=T.SMALL_SIZE + 2, color=T.GREEN,
                         line_spacing=0.9).move_to([3.3, 0.4, 0])
        with self.say("Compare with the original. The x came back on its own. Only a two is extra.") as t:
            self.play(Create(arrow), Indicate(orig[1], color=T.CYAN), run_time=1.2)
            self.play(FadeIn(note, shift=LEFT * 0.2), run_time=0.8)
        with self.say("Divide by two, and you're done: one half e to the x squared.") as t:
            self.play(FadeIn(fix, shift=RIGHT * 0.2), run_time=0.8)
            self.play(Circumscribe(fix, color=T.GREEN), run_time=1.2)
        self.wait(0.4)


class Stuck(CSScene):
    def construct(self):
        self.show_title("Case 2: it gets stuck")
        orig = M(r"\int", r"x", r"\,e^{2x}\,dx", size=1.3).move_to([-3.2, 1.7, 0])
        orig[1].set_color(T.CYAN)
        guess = M(r"\text{guess: }", r"e^{2x}", size=1.1)
        check = M(r"\text{check: }", r"e^{2x}", r"\cdot", r"2", size=1.1)
        check[3].set_color(T.YELLOW)
        steps = VGroup(guess, check).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(orig, DOWN, buff=0.6).align_to(orig, LEFT)
        with self.say("Now the right one. The inside is two x, so the guess is e to the two x.") as t:
            self.play(FadeIn(orig), run_time=0.8)
            self.play(FadeIn(guess, shift=RIGHT * 0.2), run_time=0.8)
        with self.say("Check it. The inside's derivative is just two. A plain number, with no x.") as t:
            self.play(FadeIn(check[:3], shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(check[3], scale=1.5), run_time=0.7)
        cross = Cross(orig[1], stroke_color=T.RED, stroke_width=6)
        note = make_text("the x never\ncomes back", size=T.SMALL_SIZE + 2, color=T.RED,
                         line_spacing=0.9).move_to([3.3, 1.2, 0])
        with self.say("But the original has an x in front, and the check never brings it back.") as t:
            self.play(Create(cross), run_time=0.8)
            self.play(FadeIn(note, shift=LEFT * 0.2), shake(orig), run_time=0.8)
        with self.say("Dividing by a number can't fix that. No number turns two into x.") as t:
            self.play(Indicate(check[3], color=T.RED), run_time=1.2)
        self.clear_content()

        q = make_text("What if you put the x into the guess?", size=T.BODY_SIZE, color=T.ORANGE).move_to(UP * 1.8)
        g2 = M(r"\text{guess: }", r"x\,e^{2x}", size=1.1).move_to(UP * 0.7)
        c2 = M(r"\text{check: }", r"e^{2x}", r"+", r"2x\,e^{2x}", size=1.1).move_to(DOWN * 0.5)
        with self.say("A tempting idea: just put the x into the guess.") as t:
            self.play(FadeIn(q), run_time=0.8)
            self.play(FadeIn(g2, shift=RIGHT * 0.2), run_time=0.8)
        with self.say("Now the check needs the product rule, and it adds a whole extra term.") as t:
            self.play(FadeIn(c2, shift=RIGHT * 0.2), run_time=1)
            self.play(c2[1].animate.set_color(T.RED), run_time=0.6)
        ul = Underline(c2[1], color=T.RED, buff=0.08)
        with self.say("That extra e to the two x can't be fixed either. Guess and fix is simply the wrong tool here.") as t:
            self.play(Create(ul), run_time=0.6)
            self.play(shake(c2), run_time=0.6)
        self.wait(0.4)


class YourTurn(CSScene):
    def construct(self):
        self.show_title("Your turn")
        left = M(r"\int x\cos(x^2)\,dx", size=1.3).move_to([LX, 1.0, 0])
        right = M(r"\int x\cos(x)\,dx", size=1.3).move_to([RX, 1.0, 0])
        with self.say("Which of these can guess and fix handle? Look at the inside's derivative.") as t:
            self.play(FadeIn(left), FadeIn(right), run_time=1)
        cd = Countdown(3).move_to(DOWN * 1.0)
        self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        self.play(FadeOut(cd), run_time=0.3)
        li = M(r"\text{inside}' = 2x", size=1.0).next_to(left, DOWN, buff=0.6)
        li.set_color(T.GREEN)
        ri = M(r"\text{inside}' = 1", size=1.0).next_to(right, DOWN, buff=0.6)
        ri.set_color(T.RED)
        with self.say("The left one. Its inside is x squared, with derivative two x, which matches the x in front.") as t:
            self.play(FadeIn(li, shift=UP * 0.1), run_time=0.8)
            self.play(Circumscribe(left, color=T.GREEN), run_time=1.2)
        with self.say("On the right, the inside is plain x. Its derivative is one, so the x in front has nowhere to come from.") as t:
            self.play(FadeIn(ri, shift=UP * 0.1), run_time=0.8)
            self.play(shake(right), run_time=0.6)
        self.wait(0.4)


class Recap(CSScene):
    def construct(self):
        self.show_title("The test")
        a = Callout("extra piece = a number × inside′   →   guess and fix", color=T.GREEN,
                    size=T.BODY_SIZE).move_to(UP * 1.4)
        b = Callout("anything else   →   integration by parts", color=T.ORANGE,
                    size=T.BODY_SIZE).move_to(UP * 0.0)
        with self.say("So here's the test. Compare the extra piece with the inside's derivative.") as t:
            self.play(FadeIn(a, shift=UP * 0.2), run_time=1)
        with self.say("If they match up to a number, guess and fix works. If not, switch methods.") as t:
            self.play(FadeIn(b, shift=UP * 0.2), run_time=1)
        x = M(r"x", size=1.8).move_to([-1.2, -1.5, 0]).set_color(T.CYAN)
        arr = M(r"\xrightarrow{\;d/dx\;}", size=1.2).next_to(x, RIGHT, buff=0.3)
        one = M(r"1", size=1.8).next_to(arr, RIGHT, buff=0.3).set_color(T.GREEN)
        with self.say("Next time: integration by parts. Its trick is to differentiate the x, so it turns into one and disappears.") as t:
            self.play(FadeIn(x), run_time=0.6)
            self.play(FadeIn(arr), TransformFromCopy(x, one), run_time=1.4)
        self.wait(1)
