"""Envelopes inside envelopes: encapsulation, with Hr. Schiffel. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo.effects import Countdown, glow, shake  # noqa: E402
from csvideo.story import P, StoryScene, halo, theme_intro, theme_outro, txt  # noqa: E402
from csvideo.story_kit import Laptop, Server, pulse  # noqa: E402

SCENES = ["Intro", "Hook", "Wrap", "Flat", "Journey", "Unwrap", "YourTurn", "Recap"]

MONO = "DejaVu Sans Mono"
C_APP, C_TCP, C_IP, C_ETH = P.YELLOW, P.BLUE, P.PINK, P.GREEN
LAYERS = [  # name, colour, header text, layer name
    ("TCP", C_TCP, "ports 51000 → 80,  SEQ 1", "transport"),
    ("IP", C_IP, "10.0.0.5 → 130.208.240.8,  TTL 64", "network"),
    ("Ethernet", C_ETH, "to: router's MAC  aa:bb:cc:00:11:22", "link"),
]


def core(size=40):
    t = txt("GET /index.html", size=size, color=P.FG, weight="BOLD")
    box = RoundedRectangle(corner_radius=0.18, width=t.width + 0.7, height=t.height + 0.55, stroke_color=C_APP,
                           stroke_width=5, fill_color=C_APP, fill_opacity=0.12)
    return VGroup(box, t.move_to(box))


def shell(inner, name, color, fields, layer, pad=0.32, head=0.62, size=24):
    """A layer envelope around `inner`: a rounded box with a header strip on top."""
    w, h = inner.width + 2 * pad, inner.height + pad + head + 0.1
    box = RoundedRectangle(corner_radius=0.22, width=w, height=h, stroke_color=color, stroke_width=5,
                           fill_color=color, fill_opacity=0.08)
    box.move_to(inner.get_center() + UP * (head - pad + 0.1) / 2)
    strip_y = box.get_top()[1] - head / 2 - 0.04
    name_t = txt(name, size=size + 4, color=color, weight="BOLD")
    name_t.move_to([box.get_left()[0] + 0.25 + name_t.width / 2, strip_y, 0])
    f = txt(fields, size=size, color=P.FG, font=MONO)
    f.next_to(name_t, RIGHT, buff=0.3)
    lay = txt(layer, size=size - 2, color=color)
    lay.move_to([box.get_right()[0] - 0.25 - lay.width / 2, strip_y, 0])
    if f.get_right()[0] > lay.get_left()[0] - 0.2:
        f.scale_to_fit_width(max(0.5, lay.get_left()[0] - 0.2 - f.get_left()[0]))
        f.next_to(name_t, RIGHT, buff=0.3)
    g = VGroup(box, name_t, f, lay)
    g.box, g.name, g.fields, g.layer = box, name_t, f, lay
    return g


def mini_packet(scale=1.0, layers=(C_APP, C_TCP, C_IP, C_ETH)):
    """A tiny nested-squares icon of a packet (innermost first)."""
    g = VGroup()
    for i, c in enumerate(layers):
        s = 0.22 + i * 0.16
        g.add(RoundedRectangle(corner_radius=0.06, width=s * 1.5, height=s, stroke_color=c, stroke_width=4,
                               fill_color=c, fill_opacity=0.25 if i == 0 else 0.06))
    return g.scale(scale)


def router(name, color=P.PURPLE):
    c = Circle(radius=0.48, stroke_color=color, stroke_width=4, fill_color=P.FAINT, fill_opacity=1)
    arrows = VGroup(*[Arrow(ORIGIN, d * 0.3, buff=0, stroke_width=4, color=color, max_tip_length_to_length_ratio=0.45)
                      for d in (UP, DOWN, LEFT, RIGHT)]).move_to(c)
    lab = txt(name, size=22, color=color, weight="BOLD").next_to(c, DOWN, buff=0.15)
    return VGroup(c, arrows, lab)


class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "Envelopes inside envelopes", "how one request gets wrapped, sent and unwrapped")
        self.wait(0.3)


class Hook(StoryScene):
    def construct(self):
        g = self.add_gnome("fierce", animate=False)
        req = core(48).move_to(UP * 0.6)
        with self.say("Your browser wants one tiny thing from a web server: get me index dot html. "
                      "Fifteen characters."):
            self.play(GrowFromCenter(req), run_time=0.8)
            hl = halo(req, C_APP)
            self.play(FadeIn(hl), run_time=0.6)
        qs = [("which program on the server?", UP * 2.2 + LEFT * 3.6, C_TCP),
              ("which computer, out of billions?", UP * 2.3 + RIGHT * 3.4, C_IP),
              ("which cable, right now?", DOWN * 1.2 + LEFT * 3.4, C_ETH)]
        bubbles = VGroup()
        for text, pos, c in qs:
            t = txt(text, size=26, color=c, weight="BOLD")
            b = VGroup(RoundedRectangle(corner_radius=0.2, width=t.width + 0.5, height=t.height + 0.4, stroke_color=c,
                                        stroke_width=3, fill_color=P.BG, fill_opacity=1), t)
            t.move_to(b[0])
            b.move_to(pos)
            bubbles.add(b)
        with self.say("But on its own it's helpless. It doesn't say which program should get it, which "
                      "computer, or which cable to take first."):
            for b in bubbles:
                self.play(FadeIn(b, scale=0.5), Wiggle(req, scale_value=1.06), run_time=0.7)
        with self.say("A naked request? It will catch its death out there! Wrap it up!", who="gnome"):
            self.play(g.change("angry"))
            self.play(shake(req, 0.08, 8, 0.6))
        with self.say("And that's exactly what the network does. Every layer wraps it in its own envelope, "
                      "with exactly one of those answers written on the outside."):
            self.play(g.change("fierce"), FadeOut(bubbles, shift=UP * 0.3), FadeOut(hl))
            self.play(req.animate.scale(0.83).move_to(ORIGIN), run_time=0.8)


class Wrap(StoryScene):
    def construct(self):
        self.chapter("1. Wrapping", label="1  Wrapping (encapsulation)")
        g = self.add_gnome("fierce", animate=False)
        req = core(40).move_to(DOWN * 0.3)
        self.add(req)
        tag = txt("application layer: HTTP", size=24, color=C_APP).next_to(req, DOWN, buff=0.3)
        with self.say("We start at the top, in the application layer. The browser speaks HTTP: get index dot html."):
            self.play(FadeIn(tag, shift=UP * 0.2), Indicate(req[1], color=C_APP))
        lines = [
            "Transport layer, TCP: port fifty-one thousand on your side, port eighty on the server, the web "
            "server's door. And a sequence number, so nothing gets lost.",
            "Network layer, IP: your address, the server's address, and a time to live of sixty-four. This is "
            "what gets it across the whole Internet.",
            "Link layer, Ethernet or WiFi: just the address of the very next box. The router in your hallway.",
        ]
        inner = req
        shells = []
        frame = self.camera.frame
        for (name, color, fields, layer), line in zip(LAYERS, lines):
            sh = shell(inner, name, color, fields, layer)
            start = SurroundingRectangle(inner, buff=0.02, corner_radius=0.2, color=color)
            with self.say(line):
                need = max(sh.width * 1.25, sh.height * 1.25 * config.frame_width / config.frame_height, config.frame_width)
                self.play(frame.animate.set_width(need).move_to(sh.get_center() + DOWN * 0.15 * need / config.frame_width),
                          FadeOut(tag) if tag in self.mobjects else Wait(0.01), run_time=0.8)
                self.play(ReplacementTransform(start, sh.box), run_time=0.7, rate_func=rate_functions.ease_out_back)
                self.play(Write(sh.name), run_time=0.4)
                self.play(AddTextLetterByLetter(sh.fields, run_time=1.2), FadeIn(sh.layer, shift=LEFT * 0.2))
                self.play(Flash(sh.name, color=color, line_length=0.3, num_lines=10), run_time=0.5)
            shells.append(sh)
            inner = VGroup(inner, sh)
        with self.say("Stamped, sealed, wrapped three times! Now that's a proper parcel.", who="gnome"):
            self.play(g.change("happy"))
            self.play(g.hop())
        with self.say("Envelopes inside envelopes. Each layer adds a header with one job, and doesn't care "
                      "at all what's inside."):
            self.play(g.change("fierce"))
            self.play(LaggedStart(*[Circumscribe(sh.box, color=sh.box.get_stroke_color(), time_width=0.6) for sh in shells],
                                  lag_ratio=0.35), run_time=2.4)
        self.play(self.zoom_reset(), FadeOut(inner), run_time=1.0)


class Flat(StoryScene):
    def construct(self):
        self.chapter("2. What the wire really sees", label="2  On the wire")
        g = self.add_gnome("fierce", animate=False)
        req = core(36)
        sh = req
        for (name, color, fields, layer) in LAYERS:
            sh = VGroup(sh, shell(sh, name, color, fields, layer, size=20))
        sh.scale_to_fit_width(8.6).move_to(UP * 0.4)
        with self.say("On the wire there are no boxes, of course. Just one long row of bytes. Watch the "
                      "envelopes flatten out."):
            self.play(FadeIn(sh, scale=0.9))
        unit = 0.115
        parts = [("Ethernet header", 14, C_ETH), ("IP header", 20, C_IP), ("TCP header", 20, C_TCP),
                 ("GET /index.html", 15, C_APP), ("check", 4, C_ETH)]
        bars = VGroup()
        for name, n, c in parts:
            r = Rectangle(width=n * unit, height=0.9, stroke_color=c, stroke_width=3, fill_color=c, fill_opacity=0.35)
            bars.add(r)
        bars.arrange(RIGHT, buff=0.02).move_to(UP * 0.3)
        nums = VGroup(*[txt(str(n), size=22, color=P.FG, weight="BOLD").move_to(b) for b, (_, n, _) in zip(bars, parts)])
        labs = VGroup()
        for i, (b, (name, n, c)) in enumerate(zip(bars, parts)):
            t = txt(name, size=20, color=c)
            t.next_to(b, UP if i % 2 == 0 else DOWN, buff=0.25)
            labs.add(t)
        with self.say("The outermost header comes first on the wire, then the next, then the next, and the "
                      "request itself sits right in the middle. Ethernet adds a little checksum at the end."):
            self.play(ReplacementTransform(sh, bars), run_time=1.6)
            self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.1) for l in labs], lag_ratio=0.2), FadeIn(nums))
        total = sum(n for _, n, _ in parts)
        over = txt(f"{total - 15} bytes of wrapping   for   15 bytes of request", size=30, color=P.GOLD, weight="BOLD").move_to(DOWN * 1.6)
        with self.say("Count them: fifty-eight bytes of wrapping, for fifteen bytes of actual request. For "
                      "small messages, headers are most of the traffic."):
            self.play(Write(over))
            self.play(*[b.animate.set_fill(opacity=0.7) for i, b in enumerate(bars) if i != 3], run_time=0.6)
        with self.say("Mostly envelope. Like my birthday presents.", who="gnome"):
            self.play(g.change("thinking", look=LEFT))
        self.play(g.change("fierce"), FadeOut(VGroup(bars, nums, labs, over)))


class Journey(StoryScene):
    def construct(self):
        self.chapter("3. Hop by hop", label="3  The journey")
        g = self.add_gnome("fierce", animate=False)
        y = 0.4
        you = Laptop("you  10.0.0.5", P.TEAL, scale=0.7).move_to([-12, y, 0])
        r1 = router("R1").move_to([-6, y, 0])
        r2 = router("R2").move_to([0, y, 0])
        srv = Server("130.208.240.8", P.PINK, scale=0.8).move_to([6.5, y, 0])
        wires = VGroup(*[Line(a.get_right() + RIGHT * 0.15, b.get_left() + LEFT * 0.15, stroke_color=P.MUTED, stroke_width=3)
                         for a, b in ((you, r1), (r1, r2), (r2, srv))])
        world = VGroup(wires, you, r1, r2, srv)
        frame = self.camera.frame
        self.add(world)
        frame.set_width(10).move_to([you.get_center()[0] + 2.5, y + 0.55, 0])
        pk = mini_packet(1.4).move_to(you.get_center() + UP * 1.45)
        ttl = txt("TTL 64", size=26, color=C_IP, weight="BOLD")
        mac = txt("to R1's MAC", size=24, color=C_ETH)
        ttl.add_updater(lambda m: m.next_to(pk, UP, buff=0.18))
        mac.add_updater(lambda m: m.next_to(pk, RIGHT, buff=0.25))
        with self.say("Now let's follow the parcel. It leaves your laptop with the Ethernet envelope "
                      "addressed to the first router, R1."):
            self.play(FadeIn(pk, scale=0.5), FadeIn(ttl), FadeIn(mac))

        def hop(rt, next_name, new_ttl, line):
            with self.say(line):
                self.play(pk.animate.move_to(rt[0].get_center() + UP * 1.45), pulse(wires[[r1, r2].index(rt)], C_ETH),
                          frame.animate.move_to([rt[0].get_center()[0], y + 0.55, 0]), run_time=1.6, rate_func=smooth)
                outer = pk[3]
                halves = VGroup(outer.copy(), outer.copy())
                self.remove(outer)
                pk.remove(outer)
                self.add(halves)
                self.play(halves[0].animate.shift(LEFT * 1.2 + UP * 0.8).rotate(0.8).set_opacity(0),
                          halves[1].animate.shift(RIGHT * 1.2 + UP * 0.8).rotate(-0.8).set_opacity(0),
                          FadeOut(mac), rt[0].animate.set_stroke(P.YELLOW, 6), run_time=0.7)
                self.remove(halves)
                self.play(Indicate(ttl, color=P.YELLOW, scale_factor=1.3), run_time=0.5)
                nt = txt(f"TTL {new_ttl}", size=26, color=C_IP, weight="BOLD").move_to(ttl)
                nt.add_updater(lambda m: m.next_to(pk, UP, buff=0.18))
                ttl.clear_updaters()
                self.play(ReplacementTransform(ttl, nt), run_time=0.5)
                fresh = RoundedRectangle(corner_radius=0.06, width=(0.22 + 3 * 0.16) * 1.5, height=0.22 + 3 * 0.16,
                                         stroke_color=C_ETH, stroke_width=4, fill_color=C_ETH, fill_opacity=0.06).scale(1.4).move_to(pk)
                nm = txt(f"to {next_name}", size=24, color=C_ETH)
                nm.next_to(pk, RIGHT, buff=0.25)
                nm.add_updater(lambda m: m.next_to(pk, RIGHT, buff=0.25))
                self.play(GrowFromCenter(fresh), FadeIn(nm), rt[0].animate.set_stroke(P.PURPLE, 4), run_time=0.6)
                pk.add(fresh)
                return nt, nm

        ttl, mac = hop(r1, "R2's MAC", 63, "At R1, the router tears off the Ethernet envelope, reads the IP address "
                       "inside, lowers the TTL by one, and wraps it in a brand new Ethernet envelope for the next hop.")
        with self.say("New envelope at every hop! Paper is cheap.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        ttl, mac = hop(r2, "server's MAC", 62, "R2 does exactly the same. Rip, read, TTL sixty-two, rewrap. The IP "
                       "addresses inside never changed. Only the outer link envelope did.")
        self.play(g.change("fierce"))
        with self.say("And the parcel reaches the server."):
            self.play(pk.animate.move_to(srv.get_center() + UP * 1.7), pulse(wires[2], C_ETH),
                      frame.animate.move_to([srv.get_center()[0] - 1.0, y + 0.55, 0]), run_time=1.6)
            self.play(Flash(srv, color=C_ETH, line_length=0.4), run_time=0.6)
        self.play(FadeOut(VGroup(pk, ttl, mac)), frame.animate.set_width(config.frame_width).move_to(ORIGIN),
                  FadeOut(world), run_time=1.2)


class Unwrap(StoryScene):
    def construct(self):
        self.chapter("4. Unwrapping", label="4  Unwrapping (decapsulation)")
        g = self.add_gnome("fierce", animate=False)
        req = core(34)
        nested = req
        shells = []
        for (name, color, fields, layer) in LAYERS:
            if name == "Ethernet":
                fields = "to: server's MAC"
            s = shell(nested, name, color, fields, layer, size=20)
            shells.append(s)
            nested = VGroup(nested, s)
        nested.scale_to_fit_width(7.0).move_to([-2.2, 0.0, 0])
        stack = VGroup()
        for name, c in [("application: web server, port 80", C_APP), ("transport: TCP", C_TCP),
                        ("network: IP", C_IP), ("link: network card", C_ETH)]:
            b = RoundedRectangle(corner_radius=0.1, width=3.6, height=0.62, stroke_color=c, stroke_width=3,
                                 fill_color=c, fill_opacity=0.08)
            stack.add(VGroup(b, txt(name, size=19, color=c, weight="BOLD").move_to(b)))
        stack.arrange(DOWN, buff=0.12).move_to([4.6, 0.3, 0])
        with self.say("At the server, it all happens backwards. Each layer opens only its own envelope, "
                      "checks it, and hands the rest up to the layer above."):
            self.play(FadeIn(nested, scale=0.9), LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in stack], lag_ratio=0.15))
        lines = ["The network card checks the MAC address: yes, that's me. Off comes the Ethernet envelope.",
                 "IP checks the destination address: that's me too. Off comes the IP envelope.",
                 "TCP looks at port eighty, puts the bytes in order, and hands the request to the web server."]
        for i, line in enumerate(lines):
            sh = shells[2 - i]
            row = stack[3 - i]
            with self.say(line):
                self.play(row[0].animate.set_fill(opacity=0.5), Flash(row, color=sh.box.get_stroke_color(), line_length=0.25), run_time=0.6)
                self.play(sh.animate.scale(1.25).set_opacity(0), run_time=0.8)
                rest = nested[0]
                nested = rest
                self.play(rest.animate.scale(1.12), run_time=0.4)
        with self.say("And finally the web server reads: get index dot html. The very same fifteen characters "
                      "the browser wrote."):
            self.play(stack[0][0].animate.set_fill(opacity=0.5), nested.animate.move_to([-2.2, 0.2, 0]).scale(1.3), run_time=0.8)
            self.play(FadeIn(halo(nested, C_APP)), Flash(nested, color=C_APP, line_length=0.4), run_time=0.8)
        with self.say("Unwrapped, read, delivered. Now it sends a reply, and the reply gets wrapped all over again!",
                      who="gnome"):
            self.play(g.change("happy"))
            self.play(g.hop())
        self.play(g.change("fierce"), *[FadeOut(m) for m in self.mobjects if m not in (g, self._title) and isinstance(m, VMobject)])


class YourTurn(StoryScene):
    def construct(self):
        self.chapter("5. Your turn", label="5  Your turn")
        g = self.add_gnome("thinking", animate=False)
        rt = router("R1").scale(1.6).move_to([-3.6, 0.3, 0])
        q = txt("Which envelopes does a router open?", size=34, color=P.YELLOW, weight="BOLD").move_to(UP * 2.0)
        opts = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.12, width=3.4, height=0.7, stroke_color=c, stroke_width=3,
                                                fill_color=c, fill_opacity=0.08), txt(n, size=24, color=c, weight="BOLD"))
                        for n, c in (("Ethernet", C_ETH), ("IP", C_IP), ("TCP", C_TCP), ("HTTP", C_APP))])
        for o in opts:
            o[1].move_to(o[0])
        opts.arrange(DOWN, buff=0.2).move_to([2.6, 0.0, 0])
        cd = Countdown(3).scale(0.8).next_to(rt, DOWN, buff=0.8)
        with self.say("Your turn. A packet passes through a router in the middle of the Internet. Which of "
                      "these envelopes does the router actually open?"):
            self.play(Write(q), FadeIn(rt), LaggedStart(*[FadeIn(o, shift=LEFT * 0.2) for o in opts], lag_ratio=0.15))
            self.play(FadeIn(cd))
        self.play(cd.run())
        with self.say("Just two. The Ethernet envelope, which it throws away, and the IP header, to find the "
                      "next hop and lower the TTL. TCP and HTTP pass through untouched."):
            self.play(FadeOut(cd))
            self.play(opts[0][0].animate.set_fill(opacity=0.5), opts[1][0].animate.set_fill(opacity=0.5),
                      Flash(opts[0], color=C_ETH), Flash(opts[1], color=C_IP))
            self.play(opts[2].animate.set_opacity(0.3), opts[3].animate.set_opacity(0.3))
        with self.say("A good router minds its own business. Unlike some gnomes I know.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(g.change("fierce"), FadeOut(VGroup(rt, q, opts)))


class Recap(StoryScene):
    def construct(self):
        self.chapter("The whole idea", label="Recap")
        g = self.add_gnome("fierce", animate=False)
        rows = [("HTTP", "what you want", C_APP), ("TCP", "which program: ports, SEQ", C_TCP),
                ("IP", "which computer: addresses, TTL", C_IP), ("Ethernet", "which next box: MAC", C_ETH)]
        stack = VGroup()
        for n, d, c in rows:
            b = RoundedRectangle(corner_radius=0.12, width=7.6, height=0.75, stroke_color=c, stroke_width=3, fill_color=c, fill_opacity=0.1)
            row = VGroup(b, txt(n, size=26, color=c, weight="BOLD"), txt(d, size=24, color=P.FG))
            row[1].move_to(b.get_left() + RIGHT * 1.0)
            row[2].next_to(row[1], RIGHT, buff=0.5)
            stack.add(row)
        stack.arrange(DOWN, buff=0.14).move_to([-0.8, 0.5, 0])
        down = Arrow([-5.4, 1.9, 0], [-5.4, -0.9, 0], color=P.GOLD, stroke_width=6)
        dl = txt("wrap", size=24, color=P.GOLD).next_to(down, LEFT, buff=0.15)
        up = Arrow([3.8, -0.9, 0], [3.8, 1.9, 0], color=P.TEAL, stroke_width=6)
        ul = txt("unwrap", size=24, color=P.TEAL).next_to(up, RIGHT, buff=0.15)
        with self.say("So: going down the stack, each layer wraps what it got in its own header. HTTP says what, "
                      "TCP says which program, IP which computer, Ethernet which next box."):
            self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in stack], lag_ratio=0.25), GrowArrow(down), FadeIn(dl))
        with self.say("Routers swap only the outer envelope on every hop. And at the other end, each layer "
                      "unwraps its own, on the way up."):
            self.play(GrowArrow(up), FadeIn(ul))
            self.play(Indicate(stack[3], color=C_ETH), run_time=0.8)
        with self.say("That's encapsulation. Envelopes all the way down.", who="gnome"):
            self.play(g.change("happy"))
        self.play(FadeOut(VGroup(stack, down, dl, up, ul)), FadeOut(self._title))
        self.unpin(self._title)
        self._title = None
        theme_outro(self, "Tschüss!")
