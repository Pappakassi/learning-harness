"""How the Internet moves your data: a beginner's intro to TSAM. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo import (BulletList, Bubble, Callout, Card, Chip, Counter, CSScene,  # noqa: E402
                     NetGraph, NetNode, Packet, make_text)
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, CountUp, Gauge, Swarm, glow, scatter_ring, shake  # noqa: E402

SCENES = ["Hook", "Packets", "Layers", "Routing", "Tcp", "Recap"]

COL = {"Laptop": T.BLUE, "Server": T.PINK}


def route_graph(dy=0.0):
    pos = {"Laptop": (-5.6, dy), "R1": (-2.9, dy), "R2": (0, dy + 1.35), "R3": (0, dy - 1.35),
           "R4": (2.9, dy), "Server": (5.6, dy)}
    edges = {("Laptop", "R1"): None, ("R1", "R2"): None, ("R1", "R3"): None,
             ("R2", "R4"): None, ("R3", "R4"): None, ("R4", "Server"): None}
    kinds = {"Laptop": "sender", "R1": "router", "R2": "router", "R3": "router", "R4": "router"}
    return NetGraph(pos, edges, kinds=kinds, colors={"Server": T.PINK}, scale=1.15)


def pts(g, names):
    return [g[n].get_center() for n in names]


class Hook(CSScene):
    def construct(self):
        laptop = NetNode("Laptop", "sender", scale=1.4).move_to([-5.0, 0.5, 0])
        server = NetNode("Web server", "host", scale=1.4, color=T.PINK).move_to([5.0, 0.5, 0])
        for n in (laptop, server):
            n.set_z_index(10)
        lab_a = make_text("Akureyri", size=T.SMALL_SIZE, color=T.MUTED).next_to(laptop, DOWN, buff=0.25)
        lab_r = make_text("Reykjavík", size=T.SMALL_SIZE, color=T.MUTED).next_to(server, DOWN, buff=0.25)
        fog_pts = scatter_ring([0, 0.5, 0], rx=3.2, ry=2.0, n=180, inner=0.05, seed=4)
        fog = VGroup(*[Dot(p, radius=0.03, color=T.MUTED).set_opacity(0.35) for p in fog_pts])
        fog.skip_layout_check = True
        boxes = VGroup(*[NetNode("", "router", scale=0.6).move_to(p).set_opacity(0.6)
                         for p in [(-2.2, 1.4, 0), (-1.0, -0.4, 0), (0.6, 1.7, 0), (1.4, -0.2, 0),
                                   (2.4, 1.1, 0), (-0.2, 0.7, 0)]])
        path = [laptop.get_center(), [-2.2, 1.4, 0], [-0.2, 0.7, 0], [1.4, -0.2, 0],
                [2.4, 1.1, 0], server.get_center()]
        with self.say("You're in Akureyri. You click a link, and your laptop asks a web server "
                      "in Reykjavík for a page."):
            self.play(FadeIn(laptop, scale=1.3), FadeIn(lab_a), run_time=0.7)
            self.play(FadeIn(fog, lag_ratio=0.003), FadeIn(boxes), FadeIn(server), FadeIn(lab_r),
                      run_time=1.2)
            req = Packet("GET page", T.BLUE).set_z_index(5)
            self.play(req.travel(path, run_time=2.0))
            self.remove(req)

        page = VGroup(RoundedRectangle(corner_radius=0.08, width=1.3, height=1.6,
                                       stroke_color=T.PINK, stroke_width=3, fill_color=T.FAINT,
                                       fill_opacity=1),
                      *[Line([-0.45, 0.5 - i * 0.28, 0], [0.45 - (i % 2) * 0.3, 0.5 - i * 0.28, 0],
                             stroke_color=T.MUTED, stroke_width=3) for i in range(4)])
        page.next_to(laptop, UP, buff=0.35)
        with self.say("A few hundredths of a second later, the page is on your screen."):
            back = [Packet("", T.PINK).set_z_index(5) for _ in range(6)]
            self.play(LaggedStart(*[p.travel(path[::-1], run_time=1.4) for p in back],
                                  lag_ratio=0.12))
            self.remove(*back)
            self.play(FadeIn(page, shift=UP * 0.2), laptop.flash(T.GREEN, 5), run_time=0.6)

        q = make_text("?", size=96, color=T.YELLOW, weight="BOLD").move_to([0, 0.5, 0]).set_z_index(10)
        with self.say("It crossed machines that have never heard of you, on cables shared "
                      "with millions of people. How did it find its way?"):
            self.play(Wiggle(boxes, scale_value=1.15), run_time=1.2)
            self.play(FadeIn(q, scale=1.8))
        self.play(FadeOut(VGroup(fog, boxes, laptop, server, lab_a, lab_r, page, q)), run_time=0.6)


class Packets(CSScene):
    def construct(self):
        self.show_title("Step 1: cut the data into packets")
        a = NetNode("Laptop", "sender", scale=1.3).move_to([-5.3, 0.6, 0])
        b = NetNode("Server", "host", scale=1.3, color=T.PINK).move_to([5.3, 0.6, 0])
        wire = Line(a.get_right(), b.get_left(), stroke_color=T.MUTED, stroke_width=4)
        block = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.6, fill_color=T.PINK,
                                 fill_opacity=1, stroke_width=0)
        block_t = make_text("the whole page", size=T.SMALL_SIZE, color=T.BG, weight="BOLD")
        blk = VGroup(block, block_t.move_to(block)).move_to(b.get_left() + LEFT * 1.5 + UP * 0.6)
        with self.say("You might picture a private wire from you to the server, with the page "
                      "flowing down it in one piece."):
            self.play(FadeIn(a), FadeIn(b), Create(wire), run_time=0.8)
            self.play(FadeIn(blk))
            self.play(blk.animate.move_to(a.get_right() + RIGHT * 1.5 + UP * 0.6), run_time=1.8)

        cross = VGroup(Line(UL * 0.35, DR * 0.35), Line(UR * 0.35, DL * 0.35)).set_stroke(T.RED, 9)
        cross.move_to(blk)
        y = wire.get_center()[1]
        others = [Packet("", c) for c in (T.CYAN, T.LIME, T.ORANGE, T.PURPLE, T.CYAN, T.LIME,
                                          T.ORANGE, T.PURPLE)]
        with self.say("That's not how it works. The cables are shared by everyone, "
                      "so nobody gets to hog them."):
            self.play(FadeIn(cross, scale=2), blk.animate.set_opacity(0.35))
            self.play(LaggedStart(*[p.travel([[a.get_right()[0] + 0.3, y, 0],
                                              [b.get_left()[0] - 0.3, y, 0]], run_time=1.2,
                                             rate_func=linear) for p in others], lag_ratio=0.15))
            self.remove(*others)
        self.clear_content()

        whole = RoundedRectangle(corner_radius=0.08, width=7.0, height=0.9, fill_color=T.PINK,
                                 fill_opacity=1, stroke_width=0).move_to(UP * 1.4)
        whole_t = make_text("web page: 3,000 bytes", size=T.BODY_SIZE, color=T.BG,
                            weight="BOLD").move_to(whole)
        left = RoundedRectangle(corner_radius=0.08, width=4.4, height=0.9, fill_color=T.CYAN,
                                fill_opacity=1, stroke_width=0).move_to([-2.5, 1.4, 0])
        right = left.copy().set_fill(T.LIME).move_to([2.5, 1.4, 0])
        lt = make_text("packet 1: bytes 1–1500", size=T.SMALL_SIZE + 2, color=T.BG,
                       weight="BOLD").move_to(left)
        rt = make_text("packet 2: bytes 1501–3000", size=T.SMALL_SIZE + 2, color=T.BG,
                       weight="BOLD").move_to(right)
        mtu = Chip("MTU: at most about 1500 bytes per packet", T.YELLOW, size=T.SMALL_SIZE + 2)
        mtu.move_to(UP * 0.1)
        with self.say("Instead, the data is cut into small pieces called packets."):
            self.play(FadeIn(whole), FadeIn(whole_t))
            self.play(ReplacementTransform(VGroup(whole, whole_t), VGroup(left, lt, right, rt)),
                      run_time=1.0)
        with self.say("On a normal network, one packet carries at most about fifteen hundred "
                      "bytes. That limit is called the MTU."):
            self.play(FadeIn(mtu, shift=UP * 0.2))
            self.play(Indicate(mtu, color=T.YELLOW, scale_factor=1.05))
        cu = CountUp("a 3 MB photo", 2, size=T.HEADING_SIZE, color=T.ORANGE).move_to(DOWN * 1.2)
        with self.say("So a three megabyte photo becomes about two thousand packets."):
            self.play(FadeIn(cu))
            self.play(cu.to(2000, run_time=1.6, log=True))
            unit = make_text("packets", size=T.HEADING_SIZE, color=T.ORANGE).next_to(cu, RIGHT, buff=0.3)
            self.play(FadeIn(unit))
        self.clear_content()

        g = route_graph(dy=-0.1)
        with self.say("Each packet travels on its own. Two packets from the same page can even "
                      "take different routes."):
            self.play(FadeIn(g, lag_ratio=0.05), run_time=1.0)
            p1 = Packet("1", T.CYAN).set_z_index(5)
            p2 = Packet("2", T.LIME).set_z_index(5)
            r1 = pts(g, ["Server", "R4", "R2", "R1", "Laptop"])
            r2 = pts(g, ["Server", "R4", "R3", "R1", "Laptop"])
            self.play(p1.travel(r1, run_time=3.0, rate_func=linear),
                      Succession(Wait(0.3), p2.travel(r2, run_time=2.0, rate_func=linear)))
        arr = VGroup(Packet("2", T.LIME, size=20), Packet("1", T.CYAN, size=20))
        arr.arrange(RIGHT, buff=0.2).scale(1.8)
        arr.next_to(g["Laptop"], UP, buff=0.5)
        with self.say("So packet two can arrive before packet one. Something has to put them "
                      "back in order. Keep that in mind."):
            self.remove(p1, p2)
            self.play(FadeIn(arr, shift=DOWN * 0.2))
            self.play(shake(arr, amplitude=0.06, times=6, run_time=0.6))
            self.play(Swap(arr[0], arr[1]), run_time=0.8)


class Layers(CSScene):
    def construct(self):
        self.show_title("Step 2: envelopes inside envelopes")
        cy = 0.15
        spec = [  # (name, layer, fields, color, width, height)
            ("HTTP", "application", "GET /index.html", T.YELLOW, 3.8, 0.8),
            ("TCP", "transport", "ports 51000 → 80,  SEQ 1", T.CYAN, 6.4, 1.9),
            ("IP", "network", "10.0.0.5 → 130.208.240.8,  TTL 64", T.PINK, 9.0, 3.0),
            ("Ethernet / WiFi", "link", "to the next box's MAC address", T.LIME, 11.6, 4.1),
        ]
        rings = []
        for i, (name, layer, fields, color, w, h) in enumerate(spec):
            box = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color,
                                   stroke_width=4, fill_color=T.FAINT,
                                   fill_opacity=0.55 if i else 1).move_to([0, cy, 0])
            box.set_z_index(-i)
            if i == 0:
                txt = make_text(fields, size=T.BODY_SIZE - 2, color=T.FG, weight="BOLD").move_to(box)
                tag = make_text(name, size=T.SMALL_SIZE - 2, color=color, weight="BOLD")
                tag.next_to(box, UP, buff=0.05).align_to(box, LEFT).shift(RIGHT * 0.15)
                tag.set_opacity(0)   # HTTP name is spoken; keep the centre clean
                rings.append(VGroup(box, txt))
                continue
            top = box.get_top()[1] - 0.28
            head = VGroup(make_text(name, size=T.SMALL_SIZE, color=color, weight="BOLD"),
                          make_text(fields, size=T.SMALL_SIZE - 2, color=T.FG)).arrange(RIGHT, buff=0.3)
            head.move_to([box.get_left()[0] + 0.2 + head.width / 2, top, 0])
            lay = make_text(layer, size=T.SMALL_SIZE - 2, color=color)
            lay.move_to([box.get_right()[0] - 0.2 - lay.width / 2, top, 0])
            rings.append(VGroup(box, head, lay))

        lines = [
            "A packet isn't just your data. Each layer of the network wraps it in its own "
            "envelope, with a header for one job.",
            "At the top is the application layer. Your browser speaks HTTP: get me the page.",
            "The transport layer, TCP, adds port numbers to reach the right program, and a "
            "sequence number so nothing gets lost.",
            "The network layer, IP, adds your address and the server's. That's what gets the "
            "packet across the whole Internet.",
            "And the link layer, Ethernet or WiFi, addresses it only to the very next box, "
            "using a MAC address.",
        ]
        with self.say(lines[0]):
            self.play(FadeIn(rings[0], scale=0.92), run_time=0.9)
        with self.say(lines[1]):
            self.play(Indicate(rings[0], color=T.YELLOW, scale_factor=1.1), run_time=1.0)
        for ring, text in zip(rings[1:], lines[2:]):
            with self.say(text):
                self.play(FadeIn(ring, scale=0.92), run_time=0.9)

        eth = rings[3]
        with self.say("At every hop, the link envelope is thrown away and replaced. "
                      "The IP envelope normally stays the same, end to end."):
            self.play(eth.animate.set_opacity(0.15), run_time=0.6)
            self.play(eth.animate.set_opacity(1), run_time=0.6)
            self.play(Circumscribe(rings[2][0], color=T.PINK, run_time=1.4))


class Routing(CSScene):
    def construct(self):
        self.show_title("Step 3: routers pass it on, hop by hop")
        g = route_graph(dy=-0.55)
        self.play(FadeIn(g), run_time=0.6)
        bub = Bubble("to 130.208.240.8?\nsend it to R2", T.PURPLE, tail="down")
        bub.next_to(g["R1"], UP, buff=0.35)
        with self.say("Every router does one simple thing. It reads the destination IP address, "
                      "looks it up in its routing table, and passes the packet on."):
            p = Packet("IP", T.PINK).set_z_index(5)
            self.play(p.travel(pts(g, ["Laptop", "R1"]), run_time=1.0))
            self.play(g["R1"].flash(T.YELLOW, 5), GrowFromPoint(bub, g["R1"].get_center()),
                      run_time=0.7)
        with self.say("It never knows the whole route. Only the next hop."):
            self.play(p.travel(pts(g, ["R1", "R2"]), run_time=0.8), FadeOut(bub),
                      g.highlight_edge("R1", "R2", T.YELLOW, 6))
            self.play(p.travel(pts(g, ["R2", "R4", "Server"]), run_time=1.4),
                      g.highlight_edge("R2", "R4", T.YELLOW, 6),
                      g.highlight_edge("R4", "Server", T.YELLOW, 6))
            self.play(g["Server"].flash(T.GREEN, 5), run_time=0.4)
        self.remove(p)
        self.play(*[g.reset_edge(a, b) for a, b in [("R1", "R2"), ("R2", "R4"), ("R4", "Server")]],
                  g["R1"].reset(), g["Server"].reset(), run_time=0.4)

        ttl = Counter("TTL", 64, color=T.ORANGE, size=T.HEADING_SIZE).move_to([-4.3, 1.9, 0])
        with self.say("Each router also lowers one number in the IP header by one. "
                      "It's called the time to live, or TTL."):
            self.play(FadeIn(ttl))
            p = Packet("IP", T.PINK).set_z_index(5)
            hops = ["Laptop", "R1", "R2", "R4"]
            for k in range(3):
                self.play(p.travel(pts(g, hops[k:k + 2]), run_time=0.7))
                self.play(ttl.set(63 - k), g[hops[k + 1]].flash(T.ORANGE, 5), run_time=0.4)
        with self.say("Why bother? Suppose two routers point at each other by mistake."):
            self.play(g[hops[1]].reset(), g[hops[2]].reset(), run_time=0.2)
            self.play(g.highlight_edge("R2", "R4", T.RED, 7), run_time=0.5)
            loop_r2 = Bubble("send it to R4", T.RED, tail="down").next_to(g["R2"], UP, buff=0.3)
            loop_r4 = Bubble("send it to R2", T.RED, tail="up").next_to(g["R4"], DOWN, buff=0.3)
            self.play(FadeIn(loop_r2), FadeIn(loop_r4))
        with self.say("The packet would circle between them forever. With TTL, it gets thrown "
                      "away when the count reaches zero."):
            self.play(ttl.set(5), run_time=0.3)
            for k in range(5):
                a, b = ("R4", "R2") if k % 2 == 0 else ("R2", "R4")
                self.play(p.travel(pts(g, [a, b]), run_time=0.4, rate_func=linear))
                self.play(ttl.set(4 - k), run_time=0.15)
            self.play(p.animate.set_color(T.RED), shake(p, 0.08, 6, 0.5))
            self.play(FadeOut(p, scale=0.2), Indicate(ttl, color=T.RED), run_time=0.6)


class Tcp(CSScene):
    def construct(self):
        self.show_title("Step 4: TCP makes it reliable")
        xb, xs = -4.6, 4.6
        hb = make_text("Browser", size=T.BODY_SIZE, color=T.BLUE, weight="BOLD").move_to([xb, 2.3, 0])
        hs = make_text("Server", size=T.BODY_SIZE, color=T.PINK, weight="BOLD").move_to([xs, 2.3, 0])
        lb = Line([xb, 1.95, 0], [xb, -2.4, 0], stroke_color=T.BLUE, stroke_width=3)
        ls = Line([xs, 1.95, 0], [xs, -2.4, 0], stroke_color=T.PINK, stroke_width=3)
        with self.say("Packets can get lost, or arrive out of order. TCP fixes that by "
                      "numbering every byte it sends."):
            self.play(FadeIn(hb), FadeIn(hs), Create(lb), Create(ls), run_time=1.0)

        def msg(y0, left_to_right, text, color, dy=0.55, x_end=None):
            x0, x1 = (xb, xs) if left_to_right else (xs, xb)
            if x_end is not None:
                x1 = x_end
            arrow = Arrow([x0, y0, 0], [x1, y0 - dy, 0], buff=0, stroke_width=4, color=color,
                          max_tip_length_to_length_ratio=0.04)
            lab = make_text(text, size=T.SMALL_SIZE + 2, color=color, weight="BOLD")
            lab.move_to(arrow.get_center() + UP * 0.32)
            return arrow, lab

        a1, t1 = msg(1.6, True, "500 bytes   SEQ 1", T.BLUE)
        with self.say("Your browser sends a five hundred byte request. Its sequence number is "
                      "one: these are bytes one to five hundred."):
            self.play(GrowArrow(a1), FadeIn(t1), run_time=1.2)
        a2, t2 = msg(0.75, False, "1200 bytes   SEQ 1   ACK 501", T.PINK)
        with self.say("The server answers with twelve hundred bytes of the page, "
                      "and it adds ACK five hundred and one."):
            self.play(GrowArrow(a2), FadeIn(t2), run_time=1.2)
        rule = Callout("ACK = the next byte I expect", color=T.GREEN, size=T.SMALL_SIZE + 2)
        rule.move_to([0, 2.3, 0])
        with self.say("ACK five hundred and one means: I have everything up to byte five hundred. "
                      "Send me byte five hundred and one next."):
            self.play(FadeIn(rule, shift=DOWN * 0.2))
            self.play(Indicate(t2, color=T.GREEN, scale_factor=1.08))

        a3, t3 = msg(-0.1, True, "ACK  ?", T.BLUE)
        cd = Countdown(3).move_to([0, -1.5, 0])
        with self.say("Your turn. The browser now acknowledges those twelve hundred bytes, "
                      "which started at byte one. What ACK number does it send?"):
            self.play(GrowArrow(a3), FadeIn(t3), run_time=1.0)
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        self.play(FadeOut(cd), run_time=0.3)
        t3b = make_text("ACK 1201", size=T.SMALL_SIZE + 2, color=T.GREEN, weight="BOLD").move_to(t3)
        with self.say("One plus twelve hundred: ACK twelve hundred and one. "
                      "The next byte it expects."):
            self.play(Transform(t3, t3b), Flash(t3b, color=T.GREEN, line_length=0.3))
            h = glow(t3b, T.GREEN, layers=5, spread=0.3)
            self.play(FadeIn(h), run_time=0.5)
        self.play(FadeOut(VGroup(a1, t1, a2, t2, a3, t3, h)), run_time=0.5)

        a4, t4 = msg(1.4, False, "bytes 1201 – 2600", T.PINK, dy=0.3, x_end=0.0)
        boom = VGroup(Line(UL * 0.25, DR * 0.25), Line(UR * 0.25, DL * 0.25)).set_stroke(T.RED, 8)
        boom.move_to(a4.get_end())
        clock = make_text("waiting...  timeout!", size=T.SMALL_SIZE + 2, color=T.ORANGE,
                          weight="BOLD").move_to([xs - 1.9, 0.5, 0])
        a5, t5 = msg(0.0, False, "bytes 1201 – 2600, again", T.PINK, dy=0.55)
        with self.say("And if a packet is lost on the way? No ACK comes back."):
            self.play(GrowArrow(a4), FadeIn(t4), run_time=1.0)
            self.play(FadeIn(boom, scale=2), a4.animate.set_color(T.RED))
        with self.say("After a timeout, the sender simply sends it again."):
            self.play(FadeIn(clock), shake(clock, 0.05, 6, 0.6))
            self.play(GrowArrow(a5), FadeIn(t5), run_time=1.0)
            self.play(Flash(a5.get_end(), color=T.GREEN, line_length=0.3), run_time=0.5)
        self.clear_content()

        cards = VGroup(
            Card("TCP", "numbered, ACKed, resent\nreliable and in order\nweb, files, email",
                 color=T.CYAN, width=5.4, min_height=2.3),
            Card("UDP", "no numbers, no ACKs\nfast, but no guarantees\nvideo calls, games",
                 color=T.ORANGE, width=5.4, min_height=2.3),
        ).arrange(RIGHT, buff=0.6).move_to(UP * 0.3)
        with self.say("Its sibling, UDP, skips all of this. No numbers, no ACKs, no resending."):
            self.play(FadeIn(cards[0], shift=UP * 0.2))
            self.play(FadeIn(cards[1], shift=UP * 0.2))
        with self.say("That's why video calls use UDP. A packet that arrives late is useless "
                      "anyway."):
            self.play(Indicate(cards[1], color=T.ORANGE, scale_factor=1.04), run_time=1.2)


class Recap(CSScene):
    def construct(self):
        self.show_title("The whole journey")
        items = [
            "Data is cut into packets, at most about 1500 bytes each",
            "Layers wrap it: HTTP, then TCP, then IP, then Ethernet",
            "Routers forward hop by hop on the IP address; TTL stops loops",
            "TCP numbers bytes; ACK = the next byte expected",
        ]
        bl = BulletList(items, size=T.BODY_SIZE + 4, spacing=0.6).move_to(UP * 0.2)
        self.add(bl)
        lines = [
            "So, to recap. Your data is cut into packets.",
            "Each layer wraps it in its own envelope.",
            "Routers pass it along, one hop at a time, and TTL stops it from looping forever.",
            "And TCP numbers every byte, so lost data gets noticed and sent again.",
        ]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()

        self.show_title("Coming next: traffic jams")
        router = NetNode("R", "router", scale=1.6).move_to([1.0, 0.4, 0]).set_z_index(10)
        server = NetNode("Server", "host", scale=1.3, color=T.PINK).move_to([5.0, 0.4, 0])
        server.set_z_index(10)
        link = Line(router.get_right(), server.get_left(), stroke_color=T.MUTED, stroke_width=5)
        srcs = [[-5.5, y, 0] for y in (2.0, 1.0, 0.0, -1.0, -2.0)]
        senders = VGroup(*[NetNode("", "sender", scale=0.8, color=c).move_to(p)
                           for p, c in zip(srcs, [T.CYAN, T.LIME, T.ORANGE, T.PURPLE, T.BLUE])])
        swarm = Swarm(srcs, router.get_center(), n=260,
                      colors=[T.CYAN, T.LIME, T.ORANGE, T.PURPLE, T.BLUE])
        gauge = Gauge("link load", radius=0.9).move_to([3.2, -1.4, 0])
        self.add(swarm)
        swarm.start()
        with self.say("But what happens when everyone sends at once, and one link fills up?"):
            self.play(FadeIn(senders), FadeIn(router), FadeIn(server), Create(link), FadeIn(gauge),
                      run_time=0.8)
            self.play(swarm.set_intensity(0.5, run_time=1.0), gauge.to(0.6, run_time=1.0))
            self.play(swarm.set_intensity(1.0, run_time=1.0), gauge.to(1.15, run_time=1.2))
        with self.say("Packets get dropped, and TCP has to slow down. That's congestion control, "
                      "and slow start. It's the next video."):
            self.play(link.animate.set_stroke(T.RED, 7), router.flash(T.RED, 7),
                      shake(router, 0.08, 8, 0.8))
            self.play(FadeIn(glow(router, T.RED, layers=6, spread=0.5)), run_time=0.6)
            self.wait(1.0)
        swarm.stop()
        self.wait(0.5)
