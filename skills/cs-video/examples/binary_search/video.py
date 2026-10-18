"""Binary search explainer. Storyboard: storyboard.md (same folder).

Render:  python ../../scripts/render.py video.py --draft   (fast check)
         python ../../scripts/render.py video.py -q h      (final 1080p)
"""
from manim import *

from csvideo import ArrayView, BulletList, Callout, CodePanel, Counter, CSScene, Pointers, make_text
from csvideo import theme as T

SCENES = ["Problem", "KeyIdea", "Trace", "WhyFast", "Recap"]

DATA = [3, 8, 12, 17, 21, 26, 31, 40, 44, 52]
TARGET = 31

CODE = """
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        elif a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""
# code line numbers (0-indexed) used in the trace
L_INIT, L_WHILE, L_MID, L_EQ, L_RET, L_LESS, L_LO, L_ELSE, L_HI = 1, 2, 3, 4, 5, 6, 7, 8, 9


def target_label():
    return VGroup(make_text("target", size=T.BODY_SIZE, color=T.MUTED),
                  make_text(str(TARGET), size=T.HEADING_SIZE, color=T.GREEN, weight="BOLD")
                  ).arrange(RIGHT, buff=0.25)


class Problem(CSScene):
    def construct(self):
        self.show_title("Binary search")
        arr = ArrayView(DATA, max_width=10).move_to(UP * 0.4)
        goal = target_label().next_to(arr, UP, buff=0.7)
        checks = Counter("checks", 0).move_to(DOWN * 1.9)

        with self.say("Here are ten numbers, sorted from smallest to largest. "
                      "Our job is to find the number thirty-one."):
            self.play(FadeIn(arr, lag_ratio=0.1), run_time=1.5)
            self.play(FadeIn(goal, shift=DOWN * 0.2))

        ptr = Pointers(arr, {"i": 0})
        with self.say("The simplest way is to check each number in turn, from left to right.") as t:
            self.play(FadeIn(ptr), FadeIn(checks))
            for i in range(7):
                anims = [ptr.move(i=i), checks.set(i + 1), arr.highlight(i, T.YELLOW if i < 6 else T.GREEN)]
                if i > 0:
                    anims.append(arr.unhighlight(i - 1))
                self.play(*anims, run_time=0.42)
            self.play(arr.mark(6), run_time=0.5)

        with self.say("That took seven checks. With a million numbers, it could take a million. "
                      "Because the list is sorted, we can do much better."):
            self.play(Indicate(checks, color=T.ORANGE, scale_factor=1.15), run_time=1.2)


class KeyIdea(CSScene):
    def construct(self):
        self.show_title("The key idea")
        arr = ArrayView(DATA, max_width=10).move_to(UP * 0.6)
        goal = target_label().next_to(arr, UP, buff=0.7)
        self.play(FadeIn(arr), FadeIn(goal))

        ptr = Pointers(arr, {"mid": 4})
        with self.say("Instead of starting at the left, look at the middle. The middle value is twenty-one."):
            self.play(FadeIn(ptr), arr.highlight(4))

        cmp = VGroup(make_text("21", color=T.YELLOW, weight="BOLD"), make_text("<", color=T.FG),
                     make_text("31", color=T.GREEN, weight="BOLD")).arrange(RIGHT, buff=0.25)
        cmp.next_to(ptr, RIGHT, buff=0.6)
        with self.say("Twenty-one is smaller than thirty-one. And since the list is sorted, "
                      "everything to the left of it is smaller too."):
            self.play(Write(cmp), run_time=1)
            self.play(*[arr.boxes[i].animate.set_stroke(color=T.RED, width=4) for i in range(5)],
                      run_time=1)

        callout = Callout("One comparison throws away half the list.", color=T.BLUE)
        callout.next_to(ptr, DOWN, buff=0.45).set_x(0)
        with self.say("So with one comparison, we can throw away that whole half, without ever looking at it."):
            self.play(arr.set_active_range(5, 9, reset_outside=False), FadeOut(ptr), run_time=1.2)
            self.play(FadeIn(callout, shift=UP * 0.2))


class Trace(CSScene):
    def construct(self):
        self.show_title("Tracing the algorithm")
        arr = ArrayView(DATA, max_width=6.7).move_to(LEFT * 3.55 + UP * 0.9)
        goal = target_label().scale(0.85).next_to(arr, UP, buff=0.55)
        code = CodePanel(CODE, max_width=6.3).move_to(RIGHT * 3.6 + UP * T.CONTENT_MID_Y)
        steps = Counter("checks", 0, size=T.BODY_SIZE - 2).move_to(LEFT * 3.5 + DOWN * 1.9)
        self.play(FadeIn(arr), FadeIn(goal), FadeIn(code))

        ptr = Pointers(arr, {"lo": 0, "mid": None, "hi": 9})
        with self.say("We keep two pointers, low and high, marking the part of the list "
                      "that could still contain the target. At the start, that's the whole list."):
            self.play(code.highlight(L_INIT))
            self.play(FadeIn(ptr), FadeIn(steps))

        def check(mid, n, text_mid):
            with self.say(text_mid):
                self.play(code.highlight(L_WHILE), run_time=0.5)
                self.play(code.highlight(L_MID), ptr.move(mid=mid), arr.highlight(mid),
                          steps.set(n), run_time=0.8)

        # --- check 1: mid = 4, value 21 < 31 -> lo = 5
        check(4, 1, "While low hasn't passed high, we take the middle index. "
                    "Zero plus nine, halved and rounded down, is four.")
        with self.say("The value there is twenty-one. That's less than thirty-one, "
                      "so the target must be to the right. Low moves to mid plus one."):
            self.play(code.highlight(L_EQ), run_time=0.5)
            self.play(code.highlight(L_LESS), run_time=0.5)
            self.play(code.highlight(L_LO), ptr.move(lo=5, mid=None),
                      arr.set_active_range(5, 9), run_time=1)

        # --- check 2: mid = 7, value 40 > 31 -> hi = 6
        check(7, 2, "The new middle of five and nine is seven.")
        with self.say("Forty is bigger than thirty-one, so this time high moves down to mid minus one."):
            self.play(code.highlight(L_EQ), run_time=0.4)
            self.play(code.highlight(L_ELSE), run_time=0.4)
            self.play(code.highlight(L_HI), ptr.move(hi=6, mid=None),
                      arr.set_active_range(5, 6), run_time=1)

        # --- check 3: mid = 5, value 26 < 31 -> lo = 6
        check(5, 3, "The middle of five and six is five.")
        with self.say("Twenty-six is still too small, so low moves up to six."):
            self.play(code.highlight(L_LESS), run_time=0.5)
            self.play(code.highlight(L_LO), ptr.move(lo=6, mid=None),
                      arr.set_active_range(6, 6), run_time=1)

        # --- check 4: mid = 6, found
        check(6, 4, "Now low and high are both six, so the middle is six.")
        with self.say("The value there is thirty-one. Found it, in four checks instead of seven."):
            self.play(code.highlight(L_EQ), run_time=0.5)
            self.play(code.highlight(L_RET, color=T.GREEN), arr.mark(6), run_time=0.8)
            self.play(Indicate(steps, color=T.GREEN, scale_factor=1.15))


class WhyFast(CSScene):
    def construct(self):
        self.show_title("Why it's so fast")
        n = 1_000_000
        full_w = 10.0
        bar = Rectangle(width=full_w, height=0.6, fill_color=T.BLUE, fill_opacity=0.85,
                        stroke_width=0).move_to(UP * 0.9)
        frame_box = Rectangle(width=full_w, height=0.6, stroke_color=T.MUTED,
                              stroke_width=2).move_to(bar)
        left_edge = bar.get_left()
        remaining = Counter("numbers left", n, size=T.HEADING_SIZE - 4, fmt="{:,}")
        remaining.next_to(frame_box, DOWN, buff=0.5).align_to(frame_box, LEFT)
        steps = Counter("checks", 0, size=T.HEADING_SIZE - 4, color=T.YELLOW)
        steps.next_to(frame_box, DOWN, buff=0.5).align_to(frame_box, RIGHT)

        with self.say("Why is this so fast? Every check cuts what's left in half."):
            self.play(FadeIn(frame_box), GrowFromEdge(bar, LEFT), FadeIn(remaining), FadeIn(steps))

        with self.say("Start with a million numbers. Halve it, and halve it again. "
                      "After about twenty checks, only one number is left."):
            k = 0
            while n > 1:
                n = (n + 1) // 2
                k += 1
                w = max(full_w * n / 1_000_000, 0.03)
                self.play(bar.animate.stretch_to_fit_width(w).move_to(left_edge, aligned_edge=LEFT),
                          remaining.set(n), steps.set(k), run_time=0.28)
            self.play(Indicate(steps, color=T.GREEN, scale_factor=1.2))

        self.clear_content()
        formula = MathTex(r"\text{checks} \approx \log_2 n", font_size=60, color=T.FG)
        formula.move_to(UP * 1.6)
        with self.say("The number of halvings it takes to get from n down to one is the logarithm "
                      "of n, base two. That's why binary search runs in O of log n time."):
            self.play(Write(formula), run_time=2)

        rows = [("n", "one by one", "binary search"),
                ("1,000", "1,000", "10"),
                ("1,000,000", "1,000,000", "20"),
                ("1,000,000,000", "1,000,000,000", "30")]
        cells = []
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                color = T.MUTED if r == 0 else (T.GREEN if c == 2 else T.FG)
                cells.append(make_text(val, size=T.BODY_SIZE - 2, color=color,
                                       weight="BOLD" if r == 0 or c == 2 else "NORMAL"))
        table = VGroup(*cells).arrange_in_grid(rows=4, cols=3, buff=(0.9, 0.3),
                                               col_alignments="rrr")
        table.next_to(formula, DOWN, buff=0.6)
        line = Line(table.get_left(), table.get_right(), stroke_color=T.FAINT, stroke_width=2)
        line.next_to(VGroup(*cells[:3]), DOWN, buff=0.15).set_x(table.get_center()[0])
        with self.say("And the gap grows fast. A billion sorted numbers needs only about thirty checks."):
            self.play(FadeIn(VGroup(*cells[:3])), Create(line), run_time=0.6)
            for r in range(1, 4):
                self.play(FadeIn(VGroup(*cells[3 * r:3 * r + 3]), shift=UP * 0.1), run_time=0.6)


class Recap(CSScene):
    def construct(self):
        self.show_title("Recap")
        bullets = BulletList([
            "Only works on sorted data",
            "Keep lo and hi, check the middle, throw away half",
            "About log₂(n) checks: O(log n)",
        ]).move_to(UP * 0.3)
        self.add(bullets)
        lines = [
            "First: binary search only works when the data is sorted.",
            "Second: keep a low and a high pointer, check the middle, and throw away the half that can't hold the target.",
            "And third: because each check halves the list, it takes about log base two of n checks.",
        ]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bullets.reveal(i), run_time=0.6)
        self.wait(1)
