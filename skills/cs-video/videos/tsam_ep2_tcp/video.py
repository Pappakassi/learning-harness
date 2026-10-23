"""TSAM #2: TCP up close: handshake, windows, Win=0, silly window syndrome and Nagle."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.03")

from manim import *  # noqa: E402

from csvideo import Bubble, BulletList, Callout, Card, Chip, CSScene, Packet, make_text  # noqa: E402
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, CountUp, Gauge, glow, shake  # noqa: E402

SCENES = ["Handshake", "RandomStart", "Window", "SillyWindow", "Nagle", "Recap"]

XB, XS = -4.6, 4.6


def timelines(scene, left="Browser", right="Server"):
    hb = make_text(left, size=T.BODY_SIZE, color=T.CYAN, weight="BOLD").move_to([XB, 2.3, 0])
    hs = make_text(right, size=T.BODY_SIZE, color=T.PINK, weight="BOLD").move_to([XS, 2.3, 0])
    lb = Line([XB, 1.95, 0], [XB, -2.4, 0], stroke_color=T.CYAN, stroke_width=4)
    ls = Line([XS, 1.95, 0], [XS, -2.4, 0], stroke_color=T.PINK, stroke_width=4)
    return VGroup(hb, hs, lb, ls)


def msg(y0, ltr, text, color, dy=0.5, size=T.SMALL_SIZE + 4):
    x0, x1 = (XB, XS) if ltr else (XS, XB)
    a = Arrow([x0, y0, 0], [x1, y0 - dy, 0], buff=0, stroke_width=5, color=color,
              max_tip_length_to_length_ratio=0.04)
    lab = make_text(text, size=size, color=color, weight="BOLD").move_to(a.get_center() + UP * 0.33)
    return a, lab


class Handshake(CSScene):
    def construct(self):
        self.show_title("Saying hello: the three-way handshake")
        tl = timelines(self)
        with self.say("Before TCP sends a single byte of data, the two sides shake hands. "
                      "It's a lot like starting a phone call."):
            self.play(FadeIn(tl[0]), FadeIn(tl[1]), Create(tl[2]), Create(tl[3]), run_time=1.0)
        steps = [
            (1.55, True, "SYN   seq = x", T.CYAN, "Hello? Can you hear me?",
             "First the browser sends a SYN. It means: let's talk, and my byte numbers start at x."),
            (0.5, False, "SYN-ACK   seq = y,  ack = x + 1", T.PINK, "Yes! Can you hear me?",
             "The server answers with a SYN-ACK: I hear you, and my numbers start at y."),
            (-0.55, True, "ACK   ack = y + 1", T.LIME, "Yes, I hear you!",
             "Then the browser sends a final ACK: I hear you too."),
        ]
        bubbles = []
        for y, ltr, text, color, said, line in steps:
            a, lab = msg(y, ltr, text, color)
            b = Bubble(said, color, tail="up", size=T.SMALL_SIZE)
            b.next_to(a.get_start(), DOWN, buff=0.2).shift(RIGHT * (1.5 if ltr else -1.5))
            with self.say(line):
                self.play(GrowArrow(a), FadeIn(lab, shift=UP * 0.1), run_time=1.0)
                self.play(FadeIn(b, scale=0.6), run_time=0.4)
            self.play(FadeOut(b), run_time=0.3)
        ok = Chip("connection open", T.GREEN, size=T.BODY_SIZE, filled=True).move_to([0, -1.6, 0])
        with self.say("Three messages, and the connection is open. Now data can flow both ways."):
            self.play(FadeIn(ok, scale=1.4), Flash(ok, color=T.GREEN, line_length=0.35, num_lines=14))
            self.play(FadeIn(glow(ok, T.GREEN, layers=4, spread=0.15)), run_time=0.6)


class RandomStart(CSScene):
    def construct(self):
        self.show_title("Why don't the numbers start at 1?")
        cu = CountUp("first sequence number", 1, size=T.HEADING_SIZE, color=T.YELLOW).move_to(UP * 1.6)
        with self.say("In the exercises we count from one. But in a real capture, the first "
                      "sequence number looks random, like four million, seven hundred thousand."):
            self.play(FadeIn(cu))
            self.play(cu.to(4782910, run_time=2.2, log=True))
        old = Packet("old SEQ 501", T.MUTED, size=20).scale(1.4).move_to([-5.0, -0.4, 0])
        shield = VGroup(Circle(radius=1.15, stroke_color=T.CYAN, stroke_width=6),
                        make_text("expects\n4,782,911+", size=T.SMALL_SIZE - 4, color=T.CYAN)).move_to([2.2, -0.4, 0])
        with self.say("That's on purpose. A stray packet from an older connection, still drifting "
                      "around the network, won't fit the new numbers."):
            self.play(FadeIn(shield))
            self.play(old.animate.move_to([-0.4, -0.4, 0]), run_time=1.2)
            self.play(old.animate.set_color(T.RED), shake(old, 0.08, 6, 0.5))
            self.play(old.animate.shift(LEFT * 1.6 + DOWN * 0.8).set_opacity(0.2), run_time=0.6)
        hacker = Card("Attacker", "has to guess the number\nto fake a packet", color=T.RED, width=4.6,
                      min_height=1.6).move_to([-3.6, -1.2, 0])
        dice = VGroup(*[RoundedRectangle(corner_radius=0.12, width=0.8, height=0.8, stroke_color=T.ORANGE,
                                         fill_color=T.FAINT, fill_opacity=1) for _ in range(3)]).arrange(RIGHT, buff=0.25)
        dice.move_to([3.6, -1.2, 0])
        qs = VGroup(*[make_text("?", size=T.HEADING_SIZE, color=T.ORANGE, weight="BOLD").move_to(d) for d in dice])
        with self.say("And an attacker who wants to slip a fake packet into your connection "
                      "has to guess the numbers first."):
            self.play(FadeOut(old), FadeIn(hacker, shift=UP * 0.2), FadeIn(dice), FadeIn(qs))
            self.play(*[Rotate(d, angle=PI / 2, run_time=0.8) for d in dice], Wiggle(qs))
        self.clear_content()

        self.show_title("Hanging up: FIN")
        tl = timelines(self)
        self.play(FadeIn(tl), run_time=0.5)
        rows = [(1.5, True, "FIN", T.ORANGE), (0.6, False, "ACK", T.LIME),
                (-0.3, False, "FIN", T.ORANGE), (-1.2, True, "ACK", T.LIME)]
        with self.say("Hanging up takes four messages. Each side sends a FIN when it has finished "
                      "talking, and the other side acknowledges it."):
            for y, ltr, text, color in rows:
                a, lab = msg(y, ltr, text, color, dy=0.35)
                self.play(GrowArrow(a), FadeIn(lab), run_time=0.6)


class Window(CSScene):
    def construct(self):
        self.show_title("The window: don't overflow me")
        W, x0, y = 8.0, -4.6, 0.6
        unit = W / 2000

        def x_of(b):
            return x0 + b * unit
        frame = RoundedRectangle(corner_radius=0.1, width=W, height=1.1, stroke_color=T.FG,
                                 stroke_width=4).move_to([x0 + W / 2, y, 0])
        lab = make_text("receive buffer: 2000 bytes", size=T.SMALL_SIZE + 2, color=T.MUTED)
        lab.next_to(frame, UP, buff=0.2)
        app = VGroup(RoundedRectangle(corner_radius=0.15, width=2.0, height=1.3, stroke_color=T.LIME,
                                      fill_color=T.FAINT, fill_opacity=1, stroke_width=4),
                     make_text("app", size=T.BODY_SIZE, color=T.LIME, weight="BOLD")).move_to([5.5, y, 0])
        app[1].move_to(app[0])
        with self.say("The receiver keeps incoming data in a buffer until the application "
                      "reads it. Say this buffer holds two thousand bytes."):
            self.play(Create(frame), FadeIn(lab), FadeIn(app))

        def block(b0, b1, color):
            return Rectangle(width=(b1 - b0) * unit, height=1.0, fill_color=color, fill_opacity=0.85,
                             stroke_width=0).move_to([(x_of(b0) + x_of(b1)) / 2, y, 0])
        a1 = block(0, 1200, T.CYAN)
        t1 = make_text("1200", size=T.BODY_SIZE, color=T.BG, weight="BOLD").move_to(a1)
        with self.say("Twelve hundred bytes arrive."):
            self.play(GrowFromEdge(a1, LEFT), FadeIn(t1), run_time=1.0)
        read = block(0, 600, T.LIME)
        with self.say("The app reads six hundred of them, and then it gets busy with something else."):
            self.play(FadeIn(read), run_time=0.4)
            self.play(read.animate.move_to(app).scale(0.2).set_opacity(0), run_time=1.0)
            left_part = block(600, 1200, T.CYAN)
            self.play(Transform(a1, left_part), Transform(t1, make_text(
                "600", size=T.BODY_SIZE, color=T.BG, weight="BOLD").move_to(left_part)), run_time=0.6)
            packed = block(0, 600, T.CYAN)
            self.play(a1.animate.move_to(packed), t1.animate.move_to(packed), run_time=0.6)

        q = make_text("window = free space = ?", size=T.HEADING_SIZE, color=T.YELLOW,
                      weight="BOLD").move_to([0, -1.2, 0])
        cd = Countdown(3).move_to([4.8, -1.2, 0])
        with self.say("Your turn. The free space is the window the receiver advertises to the "
                      "sender. How big is it now?"):
            self.play(FadeIn(q, shift=UP * 0.2))
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        free = Rectangle(width=1400 * unit, height=1.0, fill_color=T.YELLOW, fill_opacity=0.25,
                         stroke_color=T.YELLOW, stroke_width=3).move_to([(x_of(600) + x_of(2000)) / 2, y, 0])
        ans = make_text("window = 2000 − 600 = 1400", size=T.HEADING_SIZE, color=T.YELLOW,
                        weight="BOLD").move_to(q)
        with self.say("Fourteen hundred. Only the six hundred unread bytes take up room."):
            self.play(FadeOut(cd), Transform(q, ans), FadeIn(free), run_time=0.8)
            self.play(Indicate(free, color=T.YELLOW, scale_factor=1.03))

        a2 = block(600, 2000, T.PINK)
        t2 = make_text("1400", size=T.BODY_SIZE, color=T.BG, weight="BOLD").move_to(a2)
        with self.say("Then fourteen hundred more bytes arrive. Now the buffer is completely full."):
            self.play(FadeOut(free), GrowFromEdge(a2, LEFT), run_time=1.2)
            self.add(t2)
            self.play(frame.animate.set_stroke(T.RED, 7), shake(frame, 0.06, 6, 0.6))
        win0 = Packet("Win = 0", T.RED, size=24).scale(1.6)
        with self.say("So the receiver sends a segment with the window set to zero. It means: "
                      "stop sending, I have no room."):
            self.play(FadeOut(q), win0.travel([[x_of(1000), -0.9, 0], [-5.4, -0.9, 0]], run_time=1.4))
            stop = make_text("sender pauses", size=T.BODY_SIZE, color=T.RED, weight="BOLD")
            stop.move_to([-4.3, -1.7, 0])
            self.play(FadeIn(stop, scale=1.2))
        with self.say("While it waits, the sender sends a tiny probe now and then, asking: "
                      "is it still zero?"):
            for _ in range(2):
                p = Packet("probe", T.ORANGE, size=18).scale(1.2)
                self.play(p.travel([[-5.2, -0.3, 0], [x_of(300), -0.3, 0]], run_time=0.9))
                self.remove(p)
                r = Packet("Win = 0", T.RED, size=18).scale(1.2)
                self.play(r.travel([[x_of(300), -0.3, 0], [-5.2, -0.3, 0]], run_time=0.9))
                self.remove(r)
        upd = Packet("Win = 1000", T.GREEN, size=24).scale(1.6)
        with self.say("When the app finally reads, the receiver announces the new window, "
                      "and data flows again."):
            reader = block(0, 1000, T.LIME)
            rest = block(0, 1000, T.PINK)
            rest_t = make_text("1000 unread", size=T.BODY_SIZE - 2, color=T.BG, weight="BOLD").move_to(rest)
            self.play(FadeIn(reader), run_time=0.3)
            self.play(reader.animate.move_to(app).scale(0.2).set_opacity(0), app.animate.set_stroke(T.GREEN, 7),
                      FadeOut(VGroup(a1, t1, a2, t2)), FadeIn(rest), FadeIn(rest_t), run_time=1.0)
            self.play(frame.animate.set_stroke(T.FG, 4), FadeOut(stop), FadeOut(win0),
                      upd.travel([[x_of(1000), -0.9, 0], [-5.0, -0.9, 0]], run_time=1.4))


class SillyWindow(CSScene):
    def construct(self):
        self.show_title("Silly window syndrome")
        with self.say("But here's a trap. Imagine the app reads just one byte at a time."):
            app = make_text("app reads 1 byte", size=T.BODY_SIZE, color=T.LIME, weight="BOLD").move_to(UP * 1.8)
            self.play(FadeIn(app, shift=DOWN * 0.2))
        win = Packet("Win = 1", T.ORANGE, size=24).scale(1.5).move_to(UP * 0.9)
        with self.say("The receiver announces a window of one, and the sender dutifully sends "
                      "exactly one byte."):
            self.play(FadeIn(win, scale=1.4))
        # the lorry with one sweet in the back
        body = RoundedRectangle(corner_radius=0.12, width=5.2, height=1.7, fill_color=T.FAINT,
                                fill_opacity=1, stroke_color=T.CYAN, stroke_width=5)
        cab = RoundedRectangle(corner_radius=0.15, width=1.5, height=1.25, fill_color=T.CYAN,
                               fill_opacity=0.8, stroke_width=0).next_to(body, RIGHT, buff=0.05).align_to(body, DOWN)
        wheels = VGroup(*[Circle(radius=0.32, fill_color=T.FG, fill_opacity=1, stroke_width=0)
                          .move_to(body.get_bottom() + RIGHT * dx + DOWN * 0.2) for dx in (-1.7, 1.4)],
                        Circle(radius=0.32, fill_color=T.FG, fill_opacity=1, stroke_width=0)
                        .move_to(cab.get_bottom() + DOWN * 0.2))
        hdr = make_text("40 bytes of headers", size=T.SMALL_SIZE + 2, color=T.CYAN).move_to(body).shift(UP * 0.4)
        sweet = Dot(radius=0.09, color=T.PINK).move_to(body).shift(DOWN * 0.35)
        sweet_l = make_text("1 byte", size=T.SMALL_SIZE, color=T.PINK).next_to(sweet, RIGHT, buff=0.15)
        lorry = VGroup(body, cab, wheels, hdr, sweet, sweet_l).move_to([-9, -1.1, 0])
        with self.say("Wrapped in forty bytes of TCP and IP headers. It's like a lorry crossing "
                      "the country with one sweet in the back."):
            self.play(lorry.animate.move_to([-1.2, -1.1, 0]), run_time=2.0, rate_func=smooth)
            self.play(Indicate(sweet, color=T.PINK, scale_factor=3))
        g = Gauge("useful data", radius=0.85).move_to([5.0, -1.0, 0])
        with self.say("Only one byte in forty-one is useful. About two percent. The network is "
                      "busy, but almost nothing gets done."):
            self.play(FadeIn(g))
            self.play(g.to(0.024, run_time=1.0))
            self.play(shake(g, 0.05, 6, 0.5))
        fix = Callout("Receiver's fix: don't advertise a window until a big chunk is free",
                      color=T.GREEN, size=T.BODY_SIZE - 2).move_to(DOWN * 1.2)
        with self.say("This is silly window syndrome. The receiver's fix: keep quiet until a "
                      "decent chunk of the buffer is free, then advertise it."):
            self.play(FadeOut(lorry), FadeOut(g), FadeIn(fix, shift=UP * 0.2))


class Nagle(CSScene):
    def construct(self):
        self.show_title("The sender's fix: Nagle's algorithm")
        keys = VGroup(*[Chip(c, T.PALETTE[i], size=T.BODY_SIZE, filled=True) for i, c in enumerate("hello")])
        keys.arrange(RIGHT, buff=0.35).move_to([-3.8, 1.6, 0])
        with self.say("The sender can make the same mistake. Say you type hello in a remote "
                      "terminal, over a slow link."):
            self.play(LaggedStart(*[FadeIn(k, shift=DOWN * 0.3) for k in keys], lag_ratio=0.25))
        lane1 = make_text("without Nagle", size=T.SMALL_SIZE + 2, color=T.MUTED).move_to([-4.6, 0.55, 0])
        lane2 = make_text("with Nagle", size=T.SMALL_SIZE + 2, color=T.MUTED).move_to([-4.6, -0.8, 0])
        dst1, dst2 = [5.6, 0.55, 0], [5.6, -0.8, 0]
        with self.say("Without help, every keystroke goes out as its own tiny packet: "
                      "five packets, two hundred bytes of headers."):
            self.play(FadeIn(lane1))
            ps = [Packet(c, T.PALETTE[i], size=18).scale(1.3) for i, c in enumerate("hello")]
            self.play(LaggedStart(*[p.travel([[-3.2, 0.55, 0], dst1], run_time=1.6) for p in ps], lag_ratio=0.2))
            n1 = make_text("5 packets", size=T.BODY_SIZE, color=T.RED, weight="BOLD").move_to([3.6, 1.1, 0])
            self.play(FadeIn(n1))
        with self.say("Nagle's rule: send the first byte right away. While its ACK is on the way "
                      "back, collect everything else the user types."):
            self.play(FadeIn(lane2))
            p_h = Packet("h", T.PALETTE[0], size=18).scale(1.3)
            self.play(p_h.travel([[-3.2, -0.8, 0], dst2], run_time=1.2), FadeOut(keys[0]))
            bucket = RoundedRectangle(corner_radius=0.1, width=2.2, height=0.7, stroke_color=T.YELLOW,
                                      stroke_width=3).move_to([-2.2, -1.5, 0])
            bl = make_text("waiting", size=T.SMALL_SIZE, color=T.YELLOW).next_to(bucket, DOWN, buff=0.1)
            self.play(Create(bucket), FadeIn(bl), *[keys[i].animate.scale(0.6).move_to(bucket.get_center() + RIGHT * (i - 2.5) * 0.48) for i in range(1, 5)], run_time=1.2)
            ack = Packet("ACK", T.LIME, size=18).scale(1.3)
            self.play(ack.travel([dst2, [-3.2, -0.8, 0]], run_time=1.2))
        with self.say("When the ACK arrives, the rest goes out together, in one packet."):
            big = Packet("ello", T.PALETTE[1], size=20).scale(1.5)
            self.play(FadeOut(VGroup(*keys[1:])), FadeOut(bucket), FadeOut(bl), FadeOut(ack),
                      big.travel([[-3.2, -0.8, 0], dst2], run_time=1.4))
            n2 = make_text("2 packets", size=T.BODY_SIZE, color=T.GREEN, weight="BOLD").move_to([3.6, -0.25, 0])
            self.play(FadeIn(n2), Flash(n2, color=T.GREEN, line_length=0.3))
        self.clear_content()
        cards = VGroup(
            Card("Good for", "bulk transfers and\nchatty apps on slow links:\nfewer, fuller packets",
                 color=T.GREEN, width=5.6, min_height=2.2),
            Card("Bad for", "games and remote terminals:\neach keystroke waits\nfor an ACK",
                 color=T.ORANGE, width=5.6, min_height=2.2),
        ).arrange(RIGHT, buff=0.5).move_to(UP * 0.3)
        with self.say("The price is a little delay. That's why real-time games often switch "
                      "Nagle off, with an option called TCP no delay."):
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.4))


class Recap(CSScene):
    def construct(self):
        self.show_title("TCP up close: recap")
        items = [
            "Handshake: SYN, SYN-ACK, ACK. Hang up with FIN + ACK each way",
            "Start numbers are random: no stray old packets, harder to fake",
            "Window = free buffer space. Win = 0 means stop; probes check back",
            "Tiny packets waste the link: wait for space, and Nagle batches bytes",
        ]
        bl = BulletList(items, size=T.BODY_SIZE + 2, spacing=0.55).move_to(UP * 0.2)
        self.add(bl)
        lines = ["To recap. TCP opens with a three-way handshake, and closes with a FIN from each side.",
                 "Its starting numbers are random, for safety.",
                 "The window tells the sender how much room the receiver has. Zero means stop.",
                 "And tiny packets waste the link, so both sides try to send fewer, fuller ones."]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()
        self.show_title("Coming next: traffic jams")
        road = VGroup(*[Line([-6, y, 0], [6, y, 0], stroke_color=T.MUTED, stroke_width=3) for y in (0.9, -0.9)])
        cars = VGroup(*[RoundedRectangle(corner_radius=0.1, width=0.9, height=0.5, fill_color=T.PALETTE[i % 8],
                                         fill_opacity=1, stroke_width=0).move_to([-5.6 + i * 0.95, 0, 0])
                        for i in range(10)])
        with self.say("The window protects the receiver. But what about all the routers in between? "
                      "Next time: speed, and traffic jams."):
            self.play(FadeIn(road))
            self.play(cars.animate.shift(RIGHT * 3.0), run_time=1.6, rate_func=rush_from)
            self.play(shake(cars, 0.05, 8, 0.8))
        self.wait(0.6)
