"""TSAM #5: home networks: private addresses, NAT translation, reboot, port forwarding, hole punching, WiFi APs."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.04")

from manim import *  # noqa: E402

from csvideo import BulletList, Bubble, Callout, Card, Chip, CSScene, NetNode, Packet, make_text  # noqa: E402
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, Gauge, glow, scatter_ring, shake  # noqa: E402

SCENES = ["Private", "Translate", "Reboot", "WayIn", "HolePunch", "Wifi", "Recap"]


def home_layout():
    """The 2023 exam's home network: three hosts, a NAT router, the Internet, an ssh server."""
    hosts = VGroup(*[NetNode(f"192.168.1.{n}", "host", scale=1.0, color=c) for n, c in ((30, T.CYAN), (31, T.MUTED), (32, T.MUTED))])
    hosts.arrange(DOWN, buff=0.55).move_to([-5.2, 0.75, 0])
    router = NetNode("NAT", "router", scale=1.5).move_to([-1.7, 0.75, 0])
    inside = make_text("192.168.1.1", size=T.SMALL_SIZE - 2, color=T.MUTED).next_to(router, DOWN, buff=0.15).shift(LEFT * 0.55)
    outside = make_text("14.11.12.144", size=T.SMALL_SIZE - 2, color=T.ORANGE, weight="BOLD").next_to(router, UP, buff=0.15).shift(RIGHT * 0.55)
    server = NetNode("130.208.240.8", "host", scale=1.0, color=T.PINK).move_to([4.9, 0.75, 0])
    cloud = VGroup(*[Circle(radius=r, fill_color=T.FG, fill_opacity=0.08, stroke_width=0).move_to([1.6 + dx, 0.75 + dy, 0])
                     for dx, dy, r in ((-0.6, 0, 0.7), (0.2, 0.3, 0.8), (0.9, -0.05, 0.65), (0.1, -0.35, 0.6))])
    cl = make_text("Internet", size=T.SMALL_SIZE, color=T.MUTED).move_to([1.6, 0.75, 0])
    wires = VGroup(*[Line(h.get_right(), router.get_left(), stroke_color=T.MUTED, stroke_width=2.5) for h in hosts],
                   Line(router.get_right(), server.get_left(), stroke_color=T.MUTED, stroke_width=2.5))
    return hosts, router, inside, outside, server, VGroup(cloud, cl), wires


class Private(CSScene):
    def construct(self):
        self.show_title("Private addresses: the same in every home")
        homes = VGroup()
        for i in range(3):
            house = VGroup(Square(1.6, fill_color=T.PALETTE[i], fill_opacity=0.18, stroke_color=T.PALETTE[i], stroke_width=3),
                           Triangle(fill_color=T.PALETTE[i], fill_opacity=0.7, stroke_width=0).stretch_to_fit_width(1.9).stretch_to_fit_height(0.7))
            house[1].next_to(house[0], UP, buff=0)
            ip = make_text("192.168.1.30", size=T.SMALL_SIZE, color=T.FG, weight="BOLD").move_to(house[0])
            homes.add(VGroup(house, ip))
        homes.arrange(RIGHT, buff=1.1).move_to(UP * 1.0)
        with self.say("There aren't enough addresses for every device. So homes use private addresses, "
                      "and every home reuses the same ones."):
            self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.3) for h in homes], lag_ratio=0.25))
            self.play(*[Indicate(h[1], color=T.YELLOW) for h in homes])
        ranges = VGroup(*[Chip(r, c, size=T.BODY_SIZE - 2, filled=True) for r, c in
                          (("10.0.0.0 / 8", T.CYAN), ("172.16.0.0 / 12", T.PINK), ("192.168.0.0 / 16", T.LIME))])
        ranges.arrange(RIGHT, buff=0.4).move_to(DOWN * 1.05)
        rule = make_text("never routed on the public Internet", size=T.BODY_SIZE - 2, color=T.MUTED).next_to(ranges, DOWN, buff=0.3)
        with self.say("Three ranges are set aside for this. Routers on the Internet never forward them, "
                      "so they can be reused in millions of homes at once."):
            self.play(LaggedStart(*[FadeIn(r, scale=1.2) for r in ranges], lag_ratio=0.2))
            self.play(FadeIn(rule))


class Translate(CSScene):
    def construct(self):
        self.show_title("NAT: the router speaks for everyone")
        hosts, router, inside, outside, server, cloud, wires = home_layout()
        with self.say("Here's a home network. Three devices with private addresses, and a router with "
                      "one public address: fourteen, eleven, twelve, one forty-four."):
            self.play(FadeIn(wires), FadeIn(cloud), *[FadeIn(h) for h in hosts], FadeIn(router), FadeIn(server))
            self.play(FadeIn(inside), FadeIn(outside), Indicate(outside, color=T.ORANGE))
        # NAT table
        tbl_title = make_text("NAT table", size=T.SMALL_SIZE + 2, color=T.ORANGE, weight="BOLD")
        tbl_row = make_text("62000  ↔  192.168.1.30 : 51000", size=T.SMALL_SIZE + 2, color=T.FG)
        tbl = VGroup(tbl_title, tbl_row).arrange(DOWN, buff=0.15)
        box = SurroundingRectangle(tbl, color=T.ORANGE, buff=0.2, corner_radius=0.1)
        table = VGroup(box, tbl).move_to([-1.7, -1.25, 0])

        def hdr(src, dst, color):
            return VGroup(make_text(f"from  {src}", size=T.SMALL_SIZE, color=color),
                          make_text(f"to      {dst}", size=T.SMALL_SIZE, color=color)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        h1 = hdr("192.168.1.30 : 51000", "130.208.240.8 : 22", T.CYAN).move_to([-3.6, 2.35, 0])
        p = Packet("ssh", T.CYAN, size=18).scale(1.3)
        with self.say("The laptop opens an ssh connection to port twenty-two on the server. Its packet "
                      "says: from one ninety-two, one sixty-eight, one, thirty, port fifty-one thousand."):
            self.play(FadeIn(h1, shift=DOWN * 0.2))
            self.play(p.travel([hosts[0].get_center(), router.get_center()], run_time=1.2))
        h2 = hdr("14.11.12.144 : 62000", "130.208.240.8 : 22", T.ORANGE).move_to([2.2, 2.35, 0])
        with self.say("The router swaps the private source for its own public address, and a new port, "
                      "sixty-two thousand. And it writes that down in its NAT table."):
            self.play(router.flash(T.ORANGE, 6), TransformFromCopy(h1, h2), run_time=1.0)
            self.play(FadeIn(table, shift=UP * 0.2))
            self.play(p.animate.set_color(T.ORANGE), run_time=0.3)
            self.play(p.travel([router.get_center(), server.get_center()], run_time=1.2))
            self.remove(p)
        h3 = hdr("130.208.240.8 : 22", "14.11.12.144 : 62000", T.PINK).move_to([2.2, 2.35, 0])
        with self.say("The server only ever sees the router. It replies to fourteen, eleven, twelve, "
                      "one forty-four, port sixty-two thousand."):
            self.play(Transform(h2, h3), FadeOut(h1))
            r = Packet("reply", T.PINK, size=18).scale(1.3)
            self.play(r.travel([server.get_center(), router.get_center()], run_time=1.2))
        q = make_text("which device gets it?", size=T.BODY_SIZE, color=T.YELLOW, weight="BOLD").move_to([2.6, -1.3, 0])
        cd = Countdown(3).move_to([5.3, -1.3, 0])
        with self.say("Your turn. The reply arrives at port sixty-two thousand. Where does the router "
                      "send it, and to which port?"):
            self.play(FadeIn(q), FadeIn(cd, scale=1.3))
        self.play(cd.run())
        h4 = hdr("130.208.240.8 : 22", "192.168.1.30 : 51000", T.CYAN).move_to([-3.6, 2.35, 0])
        with self.say("It looks up sixty-two thousand in its table: one ninety-two, one sixty-eight, one, "
                      "thirty, port fifty-one thousand. The laptop. The round trip is complete."):
            self.play(FadeOut(cd), FadeOut(q), Indicate(tbl_row, color=T.YELLOW), FadeIn(h4))
            self.play(r.animate.set_color(T.CYAN), run_time=0.3)
            self.play(r.travel([router.get_center(), hosts[0].get_center()], run_time=1.2))
            self.play(hosts[0].flash(T.GREEN, 6))


class Reboot(CSScene):
    def construct(self):
        self.show_title("What if the router restarts?")
        hosts, router, inside, outside, server, cloud, wires = home_layout()
        tbl = VGroup(make_text("NAT table", size=T.SMALL_SIZE + 2, color=T.ORANGE, weight="BOLD"),
                     make_text("62000  ↔  192.168.1.30 : 51000", size=T.SMALL_SIZE + 2, color=T.FG)).arrange(DOWN, buff=0.15)
        box = SurroundingRectangle(tbl, color=T.ORANGE, buff=0.2, corner_radius=0.1)
        table = VGroup(box, tbl).move_to([-1.7, -1.25, 0])
        self.add(wires, cloud, *hosts, router, server, outside, table)
        with self.say("Now someone power-cycles the router. The NAT table lives in its memory, "
                      "so it's wiped."):
            self.play(router.flash(T.RED, 8), shake(router, 0.08, 8, 0.8))
            self.play(FadeOut(tbl[1]), box.animate.set_stroke(T.RED), run_time=0.8)
        with self.say("The next packet from the server arrives for port sixty-two thousand. The router "
                      "has no idea who that was, so it drops it."):
            r = Packet("reply", T.PINK, size=18).scale(1.3)
            self.play(r.travel([server.get_center(), router.get_center()], run_time=1.2))
            self.play(r.animate.set_color(T.RED).shift(DOWN * 0.8).set_opacity(0), run_time=0.6)
        c = Callout("The ssh connection hangs and breaks: you have to reconnect", color=T.RED, size=T.BODY_SIZE - 2).move_to([0, -1.3, 0])
        with self.say("The ssh session freezes, and eventually times out. You have to connect again."):
            self.play(FadeOut(table), FadeIn(c, shift=UP * 0.2))


class WayIn(CSScene):
    def construct(self):
        self.show_title("The catch: nobody can call in")
        hosts, router, inside, outside, server, cloud, wires = home_layout()
        self.add(wires, cloud, *hosts, router, server, outside)
        srv_lab = make_text("Ada", size=T.SMALL_SIZE, color=T.PINK, weight="BOLD").next_to(server, DOWN, buff=0.15)
        with self.say("Now flip it around. Ada wants to connect in to Sam's game server, on port "
                      "seven seven seven seven."):
            self.play(FadeIn(srv_lab))
            p = Packet("join :7777", T.PINK, size=18).scale(1.3)
            self.play(p.travel([server.get_center(), router.get_center()], run_time=1.2))
        with self.say("The router has nothing in its table for that port. Nobody inside asked, so it "
                      "drops the packet."):
            self.play(p.animate.set_color(T.RED), shake(router, 0.06, 6, 0.5))
            self.play(FadeOut(p, shift=DOWN * 0.8))
        e2e = Callout("NAT breaks the end-to-end principle", color=T.ORANGE, size=T.BODY_SIZE).move_to([0.8, -1.3, 0])
        with self.say("That's why people say NAT breaks the end-to-end principle: not every machine can "
                      "talk directly to every other one any more."):
            self.play(FadeIn(e2e, shift=UP * 0.2))
        self.clear_content()
        cards = VGroup(
            Card("Port forwarding", "a fixed rule in the router:\nport 7777  →  192.168.1.30", color=T.CYAN, width=5.6, size=T.SMALL_SIZE + 2, min_height=1.7),
            Card("UPnP", "the app asks the router\nto open a port for it", color=T.LIME, width=5.6, size=T.SMALL_SIZE + 2, min_height=1.7),
            Card("Hole punching (STUN)", "both sides call out at once,\nso both routers expect replies", color=T.PINK, width=5.6, size=T.SMALL_SIZE + 2, min_height=1.7),
            Card("Relay (TURN)", "a public server in the middle\npasses everything along", color=T.ORANGE, width=5.6, size=T.SMALL_SIZE + 2, min_height=1.7),
        )
        cards.arrange_in_grid(2, 2, buff=0.35).move_to(UP * 0.35)
        lines = ["The simplest fix is port forwarding: a fixed rule in the router that sends port seven seven "
                 "seven seven to Sam's laptop.",
                 "With UPnP, the game asks the router to open that port by itself.",
                 "Video calls and games often use hole punching. Let's see that one.",
                 "And when nothing else works, a relay server in the middle passes everything along."]
        for card, text in zip([cards[0], cards[1], cards[3], cards[2]], [lines[0], lines[1], lines[3], lines[2]]):
            with self.say(text):
                self.play(FadeIn(card, shift=UP * 0.2), run_time=0.7)
        self.play(Indicate(cards[2], color=T.PINK), run_time=0.8)


class HolePunch(CSScene):
    def construct(self):
        self.show_title("Hole punching")
        a = NetNode("Sam", "host", scale=1.1, color=T.CYAN).move_to([-5.6, -1.3, 0])
        ra = NetNode("NAT A", "router", scale=1.2).move_to([-2.9, -1.3, 0])
        rb = NetNode("NAT B", "router", scale=1.2).move_to([2.9, -1.3, 0])
        b = NetNode("Ada", "host", scale=1.1, color=T.PINK).move_to([5.6, -1.3, 0])
        st = NetNode("rendezvous server", "sender", scale=1.0, color=T.YELLOW).move_to([0, 1.7, 0])
        wires = VGroup(Line(a.get_right(), ra.get_left(), stroke_color=T.MUTED), Line(ra.get_right(), rb.get_left(), stroke_color=T.MUTED),
                       Line(rb.get_right(), b.get_left(), stroke_color=T.MUTED), Line(ra.get_top(), st.get_bottom(), stroke_color=T.MUTED),
                       Line(rb.get_top(), st.get_bottom(), stroke_color=T.MUTED))
        with self.say("Both Sam and Ada are behind NAT routers. First, each one contacts a public "
                      "rendezvous server."):
            self.play(FadeIn(wires), *[FadeIn(n) for n in (a, ra, rb, b, st)])
            pa, pb = Packet("hi", T.CYAN, size=18).scale(1.2), Packet("hi", T.PINK, size=18).scale(1.2)
            self.play(pa.travel([a.get_center(), ra.get_center(), st.get_center()], run_time=1.3),
                      pb.travel([b.get_center(), rb.get_center(), st.get_center()], run_time=1.3))
            self.remove(pa, pb)
        ba = Bubble("Ada is at\n31.4.5.6 : 40001", T.YELLOW, tail="up", size=T.SMALL_SIZE).next_to(ra, UP, buff=0.35).shift(LEFT * 1.6)
        bb = Bubble("Sam is at\n14.11.12.144 : 62000", T.YELLOW, tail="up", size=T.SMALL_SIZE).next_to(rb, UP, buff=0.35).shift(RIGHT * 1.6)
        with self.say("The server sees their public addresses and ports, and tells each one where to "
                      "find the other."):
            self.play(FadeIn(ba, scale=0.7), FadeIn(bb, scale=0.7))
        holes = VGroup(*[Circle(radius=0.55, stroke_color=T.GREEN, stroke_width=5).move_to(r) for r in (ra, rb)])
        with self.say("Then both send a packet to each other at the same moment. Each outgoing packet "
                      "punches a hole: now each router expects a reply from the other side."):
            p1, p2 = Packet("to Ada", T.CYAN, size=18).scale(1.2), Packet("to Sam", T.PINK, size=18).scale(1.2)
            self.play(p1.travel([a.get_center(), ra.get_center(), [0, -1.3, 0]], run_time=1.4),
                      p2.travel([b.get_center(), rb.get_center(), [0, -1.0, 0]], run_time=1.4))
            self.play(Create(holes), run_time=0.6)
            self.play(p1.travel([[0, -1.3, 0], rb.get_center(), b.get_center()], run_time=1.2),
                      p2.travel([[0, -1.0, 0], ra.get_center(), a.get_center()], run_time=1.2))
            self.remove(p1, p2)
        with self.say("So the other's packets look like replies, and they're let in. A direct connection, "
                      "through two NATs."):
            self.play(a.flash(T.GREEN, 6), b.flash(T.GREEN, 6), FadeOut(ba), FadeOut(bb))
            self.play(FadeIn(glow(ra, T.GREEN, layers=4, spread=0.15)), FadeIn(glow(rb, T.GREEN, layers=4, spread=0.15)), run_time=0.6)


class Wifi(CSScene):
    def construct(self):
        self.show_title("WiFi: four access points, one door")
        hall = Rectangle(width=10.5, height=4.0, stroke_color=T.MUTED, stroke_width=3).move_to([0, 0.4, 0])
        door = Line([-5.25, -0.75, 0], [-5.25, -1.5, 0], stroke_color=T.BG, stroke_width=10)
        dl = make_text("door", size=T.SMALL_SIZE, color=T.YELLOW).next_to(door, LEFT, buff=0.1)
        corners = [(-4.7, 1.95), (4.7, 1.95), (-4.7, -1.15), (4.7, -1.15)]
        aps = VGroup(*[NetNode(f"AP{i + 1}", "router", scale=1.0, color=T.PALETTE[i]).move_to([x, y, 0]) for i, (x, y) in enumerate(corners)])
        with self.say("A lecture hall has four WiFi access points, one in each corner. Each can handle "
                      "about sixty devices. But there's only one door."):
            self.play(Create(hall), FadeIn(door), FadeIn(dl), LaggedStart(*[FadeIn(ap, scale=1.3) for ap in aps], lag_ratio=0.15))
        g = Gauge("AP3 load", radius=0.6).move_to([2.6, -0.9, 0]).set_z_index(5)
        dots = VGroup()
        import random
        rnd = random.Random(3)
        seats = [[rnd.uniform(-3.8, 3.8), rnd.uniform(-0.9, 1.8), 0] for _ in range(40)]
        links = VGroup()
        with self.say("Students walk in by the door. Their phones join the strongest signal they see, "
                      "and that's the access point by the door."):
            self.play(FadeIn(g))
            anims = []
            for i, s in enumerate(seats):
                d = Dot([-5.0, -1.1, 0], radius=0.07, color=T.PALETTE[2])
                dots.add(d)
                anims.append(Succession(Wait(i * 0.07), d.animate(run_time=1.0).move_to(s)))
            self.play(*anims, g.to(1.3, run_time=4.0))
            links = VGroup(*[Line(d.get_center(), aps[2].get_center(), stroke_color=T.PALETTE[2], stroke_width=1, stroke_opacity=0.5) for d in dots])
            self.play(Create(links), run_time=0.8)
        with self.say("Then they sit down all over the room, but their phones stay stuck to that first "
                      "access point. It's overloaded, while the other three sit idle."):
            self.play(aps[2].flash(T.RED, 7), shake(aps[2], 0.06, 8, 0.7))
            self.play(*[aps[i].animate.set_opacity(0.4) for i in (0, 1, 3)])
        rogue = Callout("Rogue access point: an unauthorised AP on the network. It bypasses security and can see traffic",
                        color=T.RED, size=T.BODY_SIZE - 4, max_width=12.5).move_to([0, 0.3, 0])
        with self.say("And watch out for rogue access points: someone plugs in their own, or fakes your "
                      "network's name. It bypasses your security, and sees everything that passes through."):
            self.play(FadeOut(VGroup(g, dots, links, hall, door, dl, aps)), run_time=0.6)
            self.play(FadeIn(rogue, shift=UP * 0.2))


class Recap(CSScene):
    def construct(self):
        self.show_title("Home networks: recap")
        items = [
            "Private ranges: 10/8, 172.16/12, 192.168/16, reused everywhere",
            "NAT rewrites address + port on the way out, and remembers it",
            "Reboot = table lost = connections break",
            "Nobody can call in: port forwarding, UPnP, hole punching, relays",
            "WiFi: clients stick to the AP by the door; beware rogue APs",
        ]
        bl = BulletList(items, size=T.BODY_SIZE + 2, spacing=0.5).move_to(UP * 0.2)
        self.add(bl)
        lines = ["To recap. Homes use private addresses that the Internet never routes.",
                 "The NAT router rewrites the address and port of outgoing packets, and remembers how.",
                 "Lose that table, and connections break.",
                 "Nobody outside can start a connection in, unless you forward a port or punch a hole.",
                 "And on WiFi, where you walk in decides which access point you're stuck with."]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()
        self.show_title("Coming next: who can you trust?")
        lock = VGroup(RoundedRectangle(corner_radius=0.15, width=1.6, height=1.3, fill_color=T.YELLOW, fill_opacity=1, stroke_width=0),
                      Arc(radius=0.55, start_angle=0, angle=PI, stroke_color=T.YELLOW, stroke_width=14).shift(UP * 0.65))
        lock.move_to(UP * 0.4)
        with self.say("Every packet passes through routers, WiFi and networks run by strangers. So how "
                      "can anything be secret, or trusted? That's next."):
            self.play(FadeIn(lock, scale=0.6))
            self.play(Wiggle(lock), run_time=1.2)
        self.wait(0.6)
