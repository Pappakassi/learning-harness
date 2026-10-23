"""TSAM #3: speed and traffic jams: bandwidth, latency, jitter, loss, slow start, AIMD, ECN, TCP starvation."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.04")

from manim import *  # noqa: E402

from csvideo import BulletList, Callout, Card, Chip, CSScene, NetNode, Packet, make_text  # noqa: E402
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, Gauge, RaceBars, Swarm, glow, shake  # noqa: E402

SCENES = ["FourNumbers", "Satellite", "Pigeon", "Jam", "SlowStart", "Loss", "Trouble", "Starvation", "Recap"]


def car(color, w=0.55, h=0.3):
    return RoundedRectangle(corner_radius=0.07, width=w, height=h, fill_color=color, fill_opacity=1,
                            stroke_width=0)


class FourNumbers(CSScene):
    def construct(self):
        self.show_title("What does a fast network mean?")
        boxes = {}
        spots = {"Bandwidth": (-3.5, 1.0, T.CYAN), "Latency": (3.5, 1.0, T.PINK),
                 "Jitter": (-3.5, -1.35, T.LIME), "Loss": (3.5, -1.35, T.ORANGE)}
        for name, (x, y, c) in spots.items():
            frame = RoundedRectangle(corner_radius=0.15, width=6.4, height=2.05, stroke_color=c,
                                     stroke_width=3, fill_color=T.FAINT, fill_opacity=0.6).move_to([x, y, 0])
            lab = make_text(name, size=T.BODY_SIZE, color=c, weight="BOLD").move_to([x - 2.15, y + 0.72, 0])
            boxes[name] = (frame, lab, x, y, c)
        with self.say("Fast can mean four different things. Network people measure each one "
                      "separately."):
            self.play(LaggedStart(*[FadeIn(VGroup(f, l)) for f, l, *_ in boxes.values()], lag_ratio=0.2))

        # bandwidth: lanes
        f, l, x, y, c = boxes["Bandwidth"]
        lanes = VGroup(*[Line([x - 2.8, y + 0.25 - i * 0.32, 0], [x + 2.8, y + 0.25 - i * 0.32, 0],
                              stroke_color=T.MUTED, stroke_width=1.5) for i in range(5)])
        cars = [Packet("", T.CYAN) for _ in range(12)]
        with self.say("Bandwidth is how many bits per second fit through. Think of it as the "
                      "number of lanes on a road."):
            self.play(Create(lanes), run_time=0.5)
            self.play(LaggedStart(*[p.travel([[x - 2.6, y + 0.09 - (i % 4) * 0.32, 0],
                                              [x + 2.6, y + 0.09 - (i % 4) * 0.32, 0]], run_time=1.4, rate_func=linear)
                                    for i, p in enumerate(cars)], lag_ratio=0.1))
            self.remove(*cars)
        # latency: a long road and a clock
        f, l, x, y, c = boxes["Latency"]
        road = Line([x - 2.8, y - 0.2, 0], [x + 2.8, y - 0.2, 0], stroke_color=T.MUTED, stroke_width=3)
        clock = VGroup(Circle(radius=0.32, stroke_color=c, stroke_width=4))
        hand = Line(ORIGIN, UP * 0.26, stroke_color=c, stroke_width=4)
        clock.add(hand).move_to([x + 2.4, y + 0.6, 0])
        with self.say("Latency is how long one bit takes to get from one end to the other: "
                      "the length of the road."):
            self.play(Create(road), FadeIn(clock), run_time=0.5)
            p = Packet("", T.PINK)
            self.play(p.travel([[x - 2.6, y - 0.2, 0], [x + 2.6, y - 0.2, 0]], run_time=2.2, rate_func=linear),
                      Rotate(hand, angle=-2 * PI, about_point=clock[0].get_center(), run_time=2.2))
            self.remove(p)
        # jitter: uneven gaps
        f, l, x, y, c = boxes["Jitter"]
        road2 = Line([x - 2.8, y - 0.2, 0], [x + 2.8, y - 0.2, 0], stroke_color=T.MUTED, stroke_width=3)
        with self.say("Jitter is how much the delay varies. Packets that should arrive evenly "
                      "come in bunches, and your video call stutters."):
            self.play(Create(road2), run_time=0.4)
            gaps = [0, 0.15, 0.2, 0.9, 1.0, 1.05, 1.9]
            ps = [Packet("", T.LIME) for _ in gaps]
            self.play(*[Succession(Wait(g), p.travel([[x - 2.6, y - 0.2, 0], [x + 2.6, y - 0.2, 0]],
                                                    run_time=1.1, rate_func=linear)) for g, p in zip(gaps, ps)])
            self.remove(*ps)
        # loss: one vanishes
        f, l, x, y, c = boxes["Loss"]
        road3 = Line([x - 2.8, y - 0.2, 0], [x + 2.8, y - 0.2, 0], stroke_color=T.MUTED, stroke_width=3)
        with self.say("And loss is the share of packets that never arrive at all."):
            self.play(Create(road3), run_time=0.4)
            ok1, lost = Packet("", T.ORANGE), Packet("", T.RED)
            self.play(ok1.travel([[x - 2.6, y - 0.2, 0], [x + 2.6, y - 0.2, 0]], run_time=1.2, rate_func=linear),
                      lost.travel([[x - 2.6, y - 0.2, 0], [x, y - 0.2, 0]], run_time=0.6, rate_func=linear))
            boom = VGroup(Line(UL * 0.2, DR * 0.2), Line(UR * 0.2, DL * 0.2)).set_stroke(T.RED, 6).move_to([x, y - 0.2, 0])
            self.play(FadeIn(boom, scale=2), FadeOut(lost, scale=0.2), run_time=0.4)
            self.remove(ok1)


class Satellite(CSScene):
    def construct(self):
        self.show_title("Satellite vs fibre: same speed, very different delay")
        earth = Arc(radius=9, start_angle=PI / 2 - 0.55, angle=1.1, stroke_color=T.CYAN, stroke_width=6)
        earth.move_to([0, -2.1, 0])
        rk = Dot([-3.4, -1.75, 0], color=T.PINK, radius=0.12)
        ak = Dot([-1.0, -1.55, 0], color=T.LIME, radius=0.12)
        rkl = make_text("Reykjavík", size=T.SMALL_SIZE, color=T.PINK).next_to(rk, UP, buff=0.12)
        akl = make_text("Akureyri", size=T.SMALL_SIZE, color=T.LIME).next_to(ak, UP, buff=0.12)
        sat = VGroup(Square(0.34, fill_color=T.YELLOW, fill_opacity=1, stroke_width=0),
                     Rectangle(width=1.1, height=0.18, fill_color=T.BLUE, fill_opacity=1, stroke_width=0)).move_to([2.3, 2.1, 0])
        satl = make_text("36,000 km up", size=T.SMALL_SIZE, color=T.YELLOW).next_to(sat, RIGHT, buff=0.25)
        with self.say("Here's why the difference matters. A geostationary satellite sits about "
                      "thirty six thousand kilometres above the equator."):
            self.play(Create(earth), FadeIn(rk), FadeIn(ak), FadeIn(rkl), FadeIn(akl), run_time=1.0)
            self.play(FadeIn(sat, shift=DOWN * 0.3), FadeIn(satl))
        with self.say("Even at the speed of light, going up and back down takes about a quarter "
                      "of a second. Through fibre on the ground, it takes about two milliseconds."):
            ps = Packet("via satellite", T.YELLOW, size=18)
            pf = Packet("fibre", T.LIME, size=18)
            self.play(ps.travel([rk.get_center(), sat.get_center(), ak.get_center()], run_time=4.0, rate_func=linear),
                      Succession(pf.travel([rk.get_center(), ak.get_center()], run_time=0.35, rate_func=linear),
                                 Flash(ak, color=T.LIME, line_length=0.25)))
            self.remove(ps, pf)
        race = RaceBars([("fibre", T.LIME, [(2, T.LIME)]), ("satellite", T.YELLOW, [(250, T.YELLOW)])],
                        origin=(-3.2, 0.6, 0), unit=0.03, row_gap=0.75, bar_h=0.45)
        ms = make_text("one way, in milliseconds", size=T.SMALL_SIZE, color=T.MUTED).move_to([1.0, 1.25, 0])
        with self.say("Both links can carry lots of data per second. The critical difference is "
                      "latency: every round trip over the satellite costs half a second."):
            self.play(FadeOut(VGroup(sat, satl)), FadeIn(race.labels), Create(race.start_line), FadeIn(ms))
            self.add(race)
            self.play(race.to(race.max_total(), speed=120))
            self.play(race.crown())


class Pigeon(CSScene):
    def construct(self):
        self.show_title("Never underestimate a pigeon")
        bird = VGroup(Ellipse(width=1.3, height=0.75, fill_color=T.MUTED, fill_opacity=1, stroke_width=0),
                      Circle(radius=0.26, fill_color=T.MUTED, fill_opacity=1, stroke_width=0).shift(RIGHT * 0.65 + UP * 0.3),
                      Triangle(fill_color=T.ORANGE, fill_opacity=1, stroke_width=0).scale(0.1).rotate(-PI / 2).shift(RIGHT * 0.95 + UP * 0.3),
                      Polygon([-0.2, 0.1, 0], [0.3, 0.1, 0], [-0.1, 0.75, 0], fill_color=T.FG, fill_opacity=0.9, stroke_width=0),
                      RoundedRectangle(corner_radius=0.04, width=0.42, height=0.26, fill_color=T.PINK, fill_opacity=1,
                                       stroke_width=0).shift(DOWN * 0.42))
        card = make_text("1 TB", size=T.SMALL_SIZE - 4, color=T.BG, weight="BOLD").move_to(bird[4])
        bird.add(card).move_to([-5.0, 1.5, 0])
        with self.say("Now a fun one. A pigeon carries a one terabyte memory card from Reykjavík "
                      "to Akureyri. It flies three hundred and fifty kilometres in three and a half hours."):
            self.play(FadeIn(bird))
            self.play(bird.animate.move_to([4.6, 1.7, 0]), run_time=3.0, rate_func=smooth)
        q = make_text("1 TB over a 100 Mb/s link: faster or slower?", size=T.BODY_SIZE + 2, color=T.YELLOW,
                      weight="BOLD").move_to([0, 0.2, 0])
        cd = Countdown(3).move_to([0, -0.5, 0])
        with self.say("Your turn. Copying the same terabyte over a hundred megabit link: "
                      "is that faster or slower than the bird?"):
            self.play(FadeIn(q, shift=UP * 0.2))
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        self.play(FadeOut(cd), FadeOut(q), run_time=0.3)
        race = RaceBars([("pigeon", T.PINK, [(3.5, T.PINK)]), ("100 Mb/s link", T.CYAN, [(22, T.CYAN)])],
                        origin=(-3.2, 0.3, 0), unit=0.38, row_gap=0.85, bar_h=0.5)
        hrs = make_text("hours", size=T.SMALL_SIZE, color=T.MUTED).move_to([4.4, 1.0, 0])
        with self.say("Slower! The link needs about twenty two hours. The pigeon wins easily."):
            self.play(FadeIn(race.labels), Create(race.start_line), FadeIn(hrs))
            self.add(race)
            self.play(race.to(3.5, speed=6))
            self.play(race.crown(), Flash(bird, color=T.PINK, line_length=0.3))
            self.play(race.to(race.max_total(), speed=12))
        joke = Callout("Huge bandwidth, terrible latency", color=T.PINK, size=T.BODY_SIZE).move_to([0, -1.7, 0])
        with self.say("Enormous bandwidth, terrible latency. You wouldn't want to play a game "
                      "over pigeon."):
            self.play(FadeIn(joke, shift=UP * 0.2))


class Jam(CSScene):
    def construct(self):
        self.show_title("Traffic jams: the bottleneck")
        srcs = [[-5.6, y, 0] for y in (1.8, 0.9, 0.0, -0.9, -1.8)]
        cols = [T.CYAN, T.LIME, T.ORANGE, T.PURPLE, T.BLUE]
        pcs = VGroup(*[NetNode(f"PC {i + 1}", "sender", scale=0.85, color=c).move_to(p) for i, (p, c) in enumerate(zip(srcs, cols))])
        router = NetNode("R", "router", scale=1.5).move_to([0.2, 0.0, 0]).set_z_index(10)
        dest = NetNode("Akureyri", "host", scale=1.1, color=T.PINK).move_to([5.4, 0.0, 0]).set_z_index(10)
        link = Line(router.get_right(), dest.get_left(), stroke_color=T.MUTED, stroke_width=6)
        link_l = make_text("1 Gb/s", size=T.SMALL_SIZE, color=T.MUTED).next_to(link, UP, buff=0.15)
        slots = VGroup(*[Square(0.34, stroke_color=T.FG, stroke_width=2) for _ in range(8)]).arrange(RIGHT, buff=0.04)
        slots.next_to(router, DOWN, buff=0.45)
        ql = make_text("queue", size=T.SMALL_SIZE, color=T.MUTED).next_to(slots, DOWN, buff=0.12)
        with self.say("Every link has a fixed speed. Now imagine five computers, each on a fast "
                      "internal network, all copying files through one link at the same time."):
            self.play(LaggedStart(*[FadeIn(p) for p in pcs], lag_ratio=0.1), FadeIn(router), FadeIn(dest),
                      Create(link), FadeIn(link_l), FadeIn(slots), FadeIn(ql))
        swarm = Swarm(srcs, router.get_center(), n=220, colors=cols)
        self.add(swarm)
        swarm.start()
        g = Gauge("link load", radius=0.8).move_to([3.0, -1.6, 0])
        with self.say("Together they send five times more than the link can carry. The router "
                      "puts the extra packets in a queue."):
            self.play(swarm.set_intensity(1.0, run_time=1.0), FadeIn(g), run_time=1.0)
            self.play(g.to(1.2, run_time=1.2))
            self.play(LaggedStart(*[s.animate.set_fill(cols[i % 5], 0.9) for i, s in enumerate(slots)],
                                  lag_ratio=0.25), run_time=2.0)
        with self.say("But a queue is just memory, and it fills up. Once it's full, new packets "
                      "are simply dropped."):
            drops = [Packet("", T.RED) for _ in range(5)]
            self.play(slots.animate.set_stroke(T.RED, 4), shake(router, 0.06, 8, 0.8))
            self.play(LaggedStart(*[p.travel([router.get_center() + UP * 0.6, router.get_center() + UP * 0.6 + RIGHT * (i - 2) * 0.5 + DOWN * 2.6],
                                             run_time=1.0) for i, p in enumerate(drops)], lag_ratio=0.15))
            self.remove(*drops)
        with self.say("The senders don't see the queue. All they notice is that some ACKs never "
                      "come back. That missing ACK is TCP's only clue."):
            self.play(Indicate(slots, color=T.RED), run_time=1.2)
            self.wait(1.0)
        swarm.stop()


class SlowStart(CSScene):
    def construct(self):
        self.show_title("Slow start: probing for the limit")
        ax = Axes(x_range=[0, 16, 2], y_range=[0, 18, 4], x_length=9.5, y_length=3.7, tips=False,
                  axis_config={"color": T.MUTED, "include_numbers": True, "font_size": 22}).move_to([0.3, 0.55, 0])
        xl = make_text("round trips", size=T.SMALL_SIZE, color=T.MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = make_text("window (packets in flight)", size=T.SMALL_SIZE, color=T.MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        self.ax = ax
        with self.say("So how fast should a TCP sender go? It doesn't know. So it starts small, "
                      "and keeps a congestion window: how many packets it may have in flight."):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
        vals = [1, 2, 4, 8, 16]
        dots = VGroup(*[Dot(ax.c2p(i, v), radius=0.08, color=T.CYAN) for i, v in enumerate(vals)])
        lines = VGroup(*[Line(ax.c2p(i, vals[i]), ax.c2p(i + 1, vals[i + 1]), stroke_color=T.CYAN, stroke_width=5)
                         for i in range(len(vals) - 1)])
        nums = VGroup(*[make_text(str(v), size=T.SMALL_SIZE, color=T.CYAN, weight="BOLD").next_to(d, UL, buff=0.05)
                        for v, d in zip(vals, dots)])
        with self.say("One packet. When its ACK comes back, two. Then four, eight, sixteen. "
                      "The window doubles every round trip."):
            self.play(FadeIn(dots[0]), FadeIn(nums[0]))
            for i in range(4):
                self.play(Create(lines[i]), FadeIn(dots[i + 1], scale=1.6), FadeIn(nums[i + 1]), run_time=0.7)
        tag = Chip("slow start: doubling", T.CYAN, filled=True).move_to(ax.c2p(4, 15) + LEFT * 2.6)
        with self.say("That's slow start. A funny name, because the growth is exponential. It's "
                      "slow only at the very beginning."):
            self.play(FadeIn(tag, shift=UP * 0.2))
        boom = Star(n=8, outer_radius=0.42, inner_radius=0.2, fill_color=T.RED, fill_opacity=1,
                    stroke_width=0).move_to(ax.c2p(4, 16))
        with self.say("Until a packet is lost. Then the sender knows it went too far."):
            self.play(GrowFromCenter(boom), Flash(boom, color=T.RED, line_length=0.35), run_time=0.7)
            self.play(shake(boom, 0.05, 6, 0.4))
        self.keep = VGroup(ax, xl, yl, dots, lines, nums, boom)
        self.wait(0.3)


class Loss(CSScene):
    def construct(self):
        self.show_title("Two kinds of loss signal")
        ax = Axes(x_range=[0, 16, 2], y_range=[0, 18, 4], x_length=9.5, y_length=3.7, tips=False,
                  axis_config={"color": T.MUTED, "include_numbers": True, "font_size": 22}).move_to([0.3, 0.55, 0])
        seq = [1, 2, 4, 8, 16, 1, 2, 4, 8, 9, 10, 11, 12, 6, 7, 8, 9]
        pts = [ax.c2p(i, v) for i, v in enumerate(seq)]
        first = VGroup(*[Line(pts[i], pts[i + 1], stroke_color=T.CYAN, stroke_width=5) for i in range(4)])
        self.add(ax, first, *[Dot(pts[i], radius=0.08, color=T.CYAN) for i in range(5)])
        th = DashedLine(ax.c2p(0, 8), ax.c2p(16, 8), color=T.YELLOW, stroke_width=3)
        thl = make_text("ssthresh = 8", size=T.SMALL_SIZE, color=T.YELLOW, weight="BOLD").next_to(ax.c2p(16, 8), UP, buff=0.1).shift(LEFT * 0.8)
        q = make_text("timeout at 16: new threshold? restart at?", size=T.BODY_SIZE - 2, color=T.YELLOW,
                      weight="BOLD").move_to([1.2, 2.5, 0])
        with self.say("The first signal is a timeout: no ACK at all for a long time. That's "
                      "serious. Something is badly congested."):
            self.play(Indicate(first[-1], color=T.RED), run_time=1.0)
        cd = Countdown(3).move_to([4.6, 0.9, 0])
        with self.say("Your turn. The window was sixteen. After a timeout, the threshold becomes "
                      "half the window, and the window starts again from one. What are they?"):
            self.play(FadeIn(q, shift=DOWN * 0.2))
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        self.play(FadeOut(cd), run_time=0.3)
        drop = DashedLine(pts[4], pts[5], color=T.RED, stroke_width=4)
        with self.say("Threshold eight, window one. Slow start again, but only up to eight."):
            self.play(FadeOut(q), Create(drop), Create(th), FadeIn(thl), run_time=0.8)
            for i in range(5, 8):
                self.play(Create(Line(pts[i], pts[i + 1], stroke_color=T.CYAN, stroke_width=5)), run_time=0.4)
        avoid = Chip("congestion avoidance: +1 per round trip", T.LIME, filled=True).move_to(ax.c2p(10, 15))
        with self.say("Above the threshold it gets careful, and adds just one packet per round trip. "
                      "That's called congestion avoidance."):
            self.play(FadeIn(avoid))
            for i in range(8, 12):
                self.play(Create(Line(pts[i], pts[i + 1], stroke_color=T.LIME, stroke_width=5)), run_time=0.45)
        dup = Chip("3 duplicate ACKs: halve", T.ORANGE, filled=True).move_to(ax.c2p(12, 3.2))
        with self.say("The second signal is milder: three duplicate ACKs. The receiver keeps saying "
                      "I'm still missing that one packet, so others are clearly getting through."):
            self.play(Flash(pts[12], color=T.ORANGE, line_length=0.3), FadeIn(dup))
        with self.say("So the sender only halves its window, and carries on from there."):
            self.play(Create(DashedLine(pts[12], pts[13], color=T.ORANGE, stroke_width=4)), run_time=0.5)
            for i in range(13, 16):
                self.play(Create(Line(pts[i], pts[i + 1], stroke_color=T.LIME, stroke_width=5)), run_time=0.4)
        saw = Callout("Add a little, halve on loss: the TCP sawtooth", color=T.LIME, size=T.BODY_SIZE - 2).move_to([1.6, 2.35, 0])
        with self.say("Add a little each round trip, cut in half on loss. That sawtooth is how "
                      "millions of TCP connections share the Internet without anyone in charge."):
            self.play(FadeOut(avoid), FadeIn(saw, shift=UP * 0.2))


class Trouble(CSScene):
    def construct(self):
        self.show_title("When the guessing goes wrong")
        cards = VGroup(
            Card("WiFi and mobile", "packets get lost to radio noise,\nnot congestion. TCP slows\ndown for no reason",
                 color=T.ORANGE, width=5.7, size=T.SMALL_SIZE, min_height=2.0),
            Card("Long, fast links", "satellite round trips are slow,\nso doubling once per round\ntrip takes ages",
                 color=T.YELLOW, width=5.7, size=T.SMALL_SIZE, min_height=2.0),
        ).arrange(RIGHT, buff=0.4).move_to(UP * 1.35)
        with self.say("Slow start only sees one thing: lost packets. So it struggles when loss "
                      "isn't caused by congestion, like noise on WiFi."):
            self.play(FadeIn(cards[0], shift=UP * 0.2))
        with self.say("And on long links like satellite, growing once per round trip takes a "
                      "long time."):
            self.play(FadeIn(cards[1], shift=UP * 0.2))
        a = NetNode("Sender", "sender").move_to([-5.0, -0.5, 0])
        r = NetNode("R", "router", scale=1.3).move_to([0, -0.5, 0])
        b = NetNode("Receiver", "host", color=T.PINK).move_to([5.0, -0.5, 0])
        wires = VGroup(Line(a.get_right(), r.get_left(), stroke_color=T.MUTED), Line(r.get_right(), b.get_left(), stroke_color=T.MUTED))
        with self.say("Explicit Congestion Notification, ECN, fixes the guessing. A router whose "
                      "queue is filling up marks the packet instead of dropping it."):
            self.play(FadeIn(VGroup(wires, a, r, b)))
            p = Packet("data", T.CYAN, size=18).scale(1.2)
            self.play(p.travel([a.get_center(), r.get_center()], run_time=0.9))
            flag = Packet("congested!", T.ORANGE, size=16).scale(1.1).next_to(p, UP, buff=0.05)
            self.play(FadeIn(flag, scale=1.5), r.flash(T.ORANGE, 5), run_time=0.5)
            self.play(p.travel([r.get_center(), b.get_center()], run_time=0.9),
                      flag.animate.move_to(b.get_center() + UP * 0.35), run_time=0.9)
            echo = Packet("ACK: slow down", T.ORANGE, size=16).scale(1.1)
            self.play(FadeOut(flag), echo.travel([b.get_center() + DOWN * 0.45, a.get_center() + DOWN * 0.45], run_time=1.4))
        key = Callout("The critical difference: the network tells you, instead of you guessing from losses",
                      color=T.GREEN, size=T.SMALL_SIZE + 2).move_to([0, -1.75, 0])
        with self.say("That's the critical difference. With ECN the network itself tells the "
                      "endpoints. With Van Jacobson's algorithm, the endpoints have to guess."):
            self.play(FadeOut(echo), FadeOut(p), FadeIn(key, shift=UP * 0.2), r.reset())


class Starvation(CSScene):
    def construct(self):
        self.show_title("TCP starvation: when UDP won't share")
        bar_w, x0, y = 10.0, -5.0, 0.9
        frame = Rectangle(width=bar_w, height=1.0, stroke_color=T.FG, stroke_width=3).move_to([x0 + bar_w / 2, y, 0])
        cap = make_text("the link", size=T.SMALL_SIZE, color=T.MUTED).next_to(frame, UP, buff=0.15)
        tcp = ValueTracker(0.5)

        def bars():
            w = tcp.get_value() * bar_w
            a = Rectangle(width=max(w, 0.01), height=0.9, fill_color=T.CYAN, fill_opacity=0.9, stroke_width=0)
            a.move_to([x0 + w / 2, y, 0])
            b = Rectangle(width=max(bar_w - w, 0.01), height=0.9, fill_color=T.ORANGE, fill_opacity=0.9, stroke_width=0)
            b.move_to([x0 + w + (bar_w - w) / 2, y, 0])
            ta = make_text(f"TCP {round(tcp.get_value() * 100)}%", size=T.SMALL_SIZE + 2, color=T.BG, weight="BOLD").move_to(a)
            tb = make_text(f"UDP {round((1 - tcp.get_value()) * 100)}%", size=T.SMALL_SIZE + 2, color=T.BG, weight="BOLD").move_to(b)
            g = VGroup(a, b, tb)
            if tcp.get_value() > 0.12:
                g.add(ta)
            return g
        live = always_redraw(bars)
        with self.say("Here's the catch. All of this politeness only works if everyone plays along. "
                      "UDP has no congestion control at all."):
            self.play(Create(frame), FadeIn(cap), FadeIn(live))
        with self.say("When the link fills up, the TCP flows see losses and back off. The UDP flow "
                      "doesn't. It grabs the space TCP just gave up."):
            self.play(tcp.animate.set_value(0.25), run_time=1.5)
            self.play(tcp.animate.set_value(0.08), run_time=1.5)
            self.play(shake(frame, 0.05, 6, 0.5))
        lesson = Callout("UDP apps on the public Internet should limit their own rate", color=T.ORANGE,
                         size=T.BODY_SIZE - 2).move_to([0, -0.6, 0])
        with self.say("TCP starves. That's why UDP traffic on the public Internet, like video and "
                      "games, should control its own rate too, and be TCP friendly."):
            self.play(FadeIn(lesson, shift=UP * 0.2))
        home = Callout("At home: priority queuing lets real-time traffic (games, calls) go first",
                       color=T.GREEN, size=T.SMALL_SIZE + 2).move_to([0, -1.85, 0])
        with self.say("And for Sam's lag at home? A router can put real-time traffic, like games, "
                      "in a priority queue, so it skips ahead of the big download."):
            self.play(FadeIn(home, shift=UP * 0.2), tcp.animate.set_value(0.5), run_time=1.5)


class Recap(CSScene):
    def construct(self):
        self.show_title("Speed and traffic jams: recap")
        items = [
            "Bandwidth = bits per second; latency = time to get there",
            "Jitter = varying delay; loss = packets that never arrive",
            "Slow start doubles the window until loss, then backs off",
            "Timeout: back to 1. Three duplicate ACKs: halve",
            "ECN: routers warn instead of dropping. UDP must play fair",
        ]
        bl = BulletList(items, size=T.BODY_SIZE + 2, spacing=0.5).move_to(UP * 0.2)
        self.add(bl)
        lines = ["To recap. Bandwidth is how much fits through. Latency is how long it takes.",
                 "Jitter is the wobble in the delay, and loss is what never arrives.",
                 "TCP's slow start doubles its window until something is lost.",
                 "A timeout sends it back to one. Three duplicate ACKs just halve it.",
                 "ECN lets routers warn early, and UDP apps should share the road too."]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()
        self.show_title("Coming next: addresses")
        env = VGroup(RoundedRectangle(corner_radius=0.1, width=4.6, height=2.6, stroke_color=T.PINK,
                                      fill_color=T.FAINT, fill_opacity=1, stroke_width=4),
                     make_text("to: 130.208.240.8", size=T.BODY_SIZE, color=T.PINK, weight="BOLD"))
        env[1].move_to(env[0])
        q = make_text("?", size=96, color=T.YELLOW, weight="BOLD").next_to(env, RIGHT, buff=0.5)
        with self.say("We keep saying: send it to the server's address. But what is an address, "
                      "really? That's next time."):
            self.play(FadeIn(env, scale=0.8))
            self.play(FadeIn(q, scale=1.8), Wiggle(env))
        self.wait(0.6)
