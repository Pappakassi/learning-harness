"""TSAM #4: addresses: IPv4 bits, network/host split, masks and CIDR, broadcast, MAC, ARP, DHCP."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.04")

from manim import *  # noqa: E402

from csvideo import BulletList, Bubble, Callout, Card, Chip, CSScene, NetNode, Packet, make_text  # noqa: E402
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, CountUp, glow, shake  # noqa: E402

SCENES = ["JustANumber", "StreetAndHouse", "Special", "Cidr", "MacAddress", "Arp", "Dhcp", "Recap"]


def bits_row(octets, size=0.32, gap=0.22):
    """32 bit cells grouped in 4 octets. Returns (group, cells list)."""
    cells, groups = [], VGroup()
    for o in octets:
        g = VGroup()
        for b in format(o, "08b"):
            sq = Square(size, stroke_color=T.MUTED, stroke_width=1.5, fill_color=T.FAINT, fill_opacity=1)
            tx = make_text(b, size=18, color=T.FG, weight="BOLD").move_to(sq)
            c = VGroup(sq, tx)
            g.add(c)
            cells.append(c)
        g.arrange(RIGHT, buff=0.02)
        groups.add(g)
    groups.arrange(RIGHT, buff=gap)
    return groups, cells


def dotted(octets, colors=None, size=T.HEADING_SIZE + 6):
    parts = VGroup()
    for i, o in enumerate(octets):
        parts.add(make_text(str(o), size=size, color=(colors[i] if colors else T.FG), weight="BOLD"))
        if i < 3:
            parts.add(make_text(".", size=size, color=T.MUTED, weight="BOLD"))
    return parts.arrange(RIGHT, buff=0.08)


class JustANumber(CSScene):
    def construct(self):
        self.show_title("An IP address is just a number")
        octs = [130, 208, 240, 8]
        cols = [T.CYAN, T.PINK, T.LIME, T.ORANGE]
        addr = dotted(octs, cols).move_to(UP * 1.6)
        with self.say("Here's the address of a web server: one thirty, two oh eight, two forty, eight. "
                      "It looks like four numbers."):
            self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in addr], lag_ratio=0.12))
        row, cells = bits_row(octs)
        row.move_to(DOWN * 0.1)
        for i, g in enumerate(row):
            for c in g:
                c[0].set_stroke(cols[i], 2)
        braces = VGroup(*[make_text("8 bits", size=T.SMALL_SIZE, color=cols[i]).next_to(g, DOWN, buff=0.15)
                          for i, g in enumerate(row)])
        with self.say("Really, it's one thirty-two bit number. Each part is one byte, eight bits, "
                      "so each part goes from zero to two fifty-five."):
            self.play(*[TransformFromCopy(addr[2 * i], row[i]) for i in range(4)], run_time=1.4)
            self.play(LaggedStart(*[FadeIn(b) for b in braces], lag_ratio=0.2))
        cu = CountUp("possible addresses", 2, size=T.HEADING_SIZE, color=T.YELLOW).move_to(DOWN * 1.7)
        with self.say("Thirty-two bits give about four point three billion addresses. That sounded "
                      "like plenty in the nineteen eighties."):
            self.play(FadeIn(cu))
            self.play(cu.to(4294967296, run_time=2.0, log=True))


class StreetAndHouse(CSScene):
    def construct(self):
        self.show_title("Two parts: the street and the house")
        octs = [192, 168, 1, 30]
        addr = dotted(octs, [T.CYAN, T.CYAN, T.CYAN, T.PINK]).move_to(UP * 2.1)
        row, cells = bits_row(octs)
        row.move_to(UP * 0.9)
        with self.say("Every address has two parts. Take your laptop at home: one ninety-two, one "
                      "sixty-eight, one, thirty."):
            self.play(FadeIn(addr), FadeIn(row))
        net = VGroup(*cells[:24])
        host = VGroup(*cells[24:])
        bn = Brace(net, DOWN, color=T.CYAN)
        bh = Brace(host, DOWN, color=T.PINK)
        tn = make_text("network: the street", size=T.BODY_SIZE, color=T.CYAN, weight="BOLD").next_to(bn, DOWN, buff=0.1)
        th = make_text("host: the house", size=T.BODY_SIZE - 2, color=T.PINK, weight="BOLD").next_to(bh, DOWN, buff=0.1)
        with self.say("The first part says which network you're on, like a street name. "
                      "The rest says which machine on that network, like a house number."):
            self.play(*[c[0].animate.set_fill(T.CYAN, 0.35) for c in net], GrowFromCenter(bn), FadeIn(tn), run_time=1.0)
            self.play(*[c[0].animate.set_fill(T.PINK, 0.35) for c in host], GrowFromCenter(bh), FadeIn(th), run_time=1.0)
        mask_row, mcells = bits_row([255, 255, 255, 0])
        mask_row.move_to(DOWN * 1.15)
        ml = make_text("mask 255.255.255.0  =  /24", size=T.BODY_SIZE, color=T.YELLOW, weight="BOLD").next_to(mask_row, DOWN, buff=0.2)
        with self.say("Where does the street end? The subnet mask says so: ones over the network "
                      "part, zeros over the host part."):
            self.play(FadeOut(VGroup(bn, bh, tn, th)), FadeIn(mask_row, shift=UP * 0.2))
            self.play(*[c[0].animate.set_fill(T.YELLOW, 0.3) for c in mcells[:24]], run_time=0.8)
        with self.say("Twenty-four ones in a row. That's why it's written as slash twenty-four."):
            self.play(Write(ml))
            self.play(Indicate(ml, color=T.YELLOW, scale_factor=1.06))
        rule = Callout("Same street?  Deliver directly.   Different street?  Hand it to the router.",
                       color=T.GREEN, size=T.SMALL_SIZE + 4).move_to(DOWN * 2.15)
        with self.say("Your computer uses this to decide: if the destination is on my street, "
                      "I deliver it myself. If not, I hand it to the router."):
            self.play(FadeOut(ml), FadeIn(rule, shift=UP * 0.2))


class Special(CSScene):
    def construct(self):
        self.show_title("Special addresses on the street")
        houses = VGroup()
        labels = ["0", "1", "2", "...", "30", "...", "254", "255"]
        cols = [T.MUTED, T.PURPLE, T.CYAN, T.FAINT, T.PINK, T.FAINT, T.CYAN, T.ORANGE]
        for lab, c in zip(labels, cols):
            if lab == "...":
                houses.add(make_text("...", size=T.HEADING_SIZE, color=T.MUTED))
                continue
            body = Square(0.95, fill_color=c, fill_opacity=0.35, stroke_color=c, stroke_width=3)
            roof = Triangle(fill_color=c, fill_opacity=0.8, stroke_width=0).stretch_to_fit_width(1.15).stretch_to_fit_height(0.5)
            roof.next_to(body, UP, buff=0)
            num = make_text(lab, size=T.BODY_SIZE, color=T.FG, weight="BOLD").move_to(body)
            houses.add(VGroup(body, roof, num))
        houses.arrange(RIGHT, buff=0.35).move_to(UP * 0.9)
        street = make_text("street 192.168.1.0 / 24", size=T.BODY_SIZE, color=T.CYAN, weight="BOLD").move_to(UP * 2.35)
        with self.say("On the street one ninety-two, one sixty-eight, one, the last number goes "
                      "from zero to two fifty-five. But two of them are special."):
            self.play(FadeIn(street), LaggedStart(*[FadeIn(h, shift=UP * 0.3) for h in houses], lag_ratio=0.1))
        n0 = make_text("the street itself", size=T.SMALL_SIZE, color=T.MUTED).next_to(houses[0], DOWN, buff=0.25)
        gw = make_text("router", size=T.SMALL_SIZE, color=T.PURPLE).next_to(houses[1], DOWN, buff=0.65)
        bc = make_text("everyone!", size=T.SMALL_SIZE, color=T.ORANGE, weight="BOLD").next_to(houses[7], DOWN, buff=0.25)
        with self.say("Zero is the name of the network itself. And the very last one, two fifty-five, "
                      "is the broadcast address: a letter to it goes to every house on the street."):
            self.play(FadeIn(n0), Indicate(houses[0]))
            self.play(FadeIn(bc), Flash(houses[7], color=T.ORANGE, line_length=0.35))
            waves = [Packet("", T.ORANGE) for _ in range(5)]
            idx = [1, 2, 4, 6, 0]
            self.play(*[p.travel([houses[7].get_center(), houses[i].get_center()], run_time=1.0) for p, i in zip(waves, idx[:4])])
            self.remove(*waves)
        with self.say("By habit, the router usually takes number one. Everything in between is for "
                      "computers: two hundred and fifty-four of them."):
            self.play(FadeIn(gw), Indicate(houses[1], color=T.PURPLE))
        q = make_text("broadcast address of 10.4.7.0 / 24 ?", size=T.BODY_SIZE + 2, color=T.YELLOW, weight="BOLD").move_to(DOWN * 1.45)
        cd = Countdown(3).move_to([5.3, -1.45, 0])
        with self.say("Your turn. A network is ten, four, seven, zero, slash twenty-four. "
                      "What's its broadcast address?"):
            self.play(FadeIn(q, shift=UP * 0.2))
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        a = make_text("10.4.7.255", size=T.HEADING_SIZE + 4, color=T.ORANGE, weight="BOLD").move_to(DOWN * 1.45)
        with self.say("Ten, four, seven, two fifty-five. Keep the street, set the house part to all "
                      "ones."):
            self.play(FadeOut(cd), Transform(q, a), Flash(a, color=T.ORANGE, line_length=0.3))
        everyone = Callout("255.255.255.255  =  everyone on my local network (when I know nothing yet)",
                           color=T.ORANGE, size=T.SMALL_SIZE + 2).move_to(DOWN * 2.2)
        with self.say("And two fifty-five, four times, means everyone on my local network. A brand new "
                      "laptop uses it when it doesn't even know its own street yet."):
            self.play(q.animate.shift(UP * 0.35), FadeIn(everyone, shift=UP * 0.2))


class Cidr(CSScene):
    def construct(self):
        self.show_title("CIDR: streets of any length")
        cls = VGroup(
            Card("Class A  /8", "16.7 million hosts", color=T.CYAN, width=3.9, min_height=1.4),
            Card("Class B  /16", "65,536 hosts", color=T.PINK, width=3.9, min_height=1.4),
            Card("Class C  /24", "256 hosts", color=T.LIME, width=3.9, min_height=1.4),
        ).arrange(RIGHT, buff=0.3).move_to(UP * 1.5)
        with self.say("In the early days, networks came in three fixed sizes: class A, B and C."):
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cls], lag_ratio=0.3))
        firm = Chip("a company needs 2,000 addresses", T.YELLOW, size=T.BODY_SIZE - 2).move_to(UP * 0.05)
        with self.say("A company that needed two thousand addresses was too big for class C, so it "
                      "got a class B, and sixty-three thousand addresses went to waste."):
            self.play(FadeIn(firm, shift=UP * 0.2))
            self.play(firm.animate.next_to(cls[1], DOWN, buff=0.2), cls[2].animate.set_opacity(0.3), run_time=1.0)
            self.play(shake(cls[1], 0.05, 6, 0.5), cls[1].box.animate.set_stroke(T.RED, 5))
        fix = Card("CIDR  /21", "2,048 addresses: a snug fit", color=T.GREEN, width=5.0, min_height=1.4).move_to(DOWN * 0.95)
        with self.say("Classless Inter-Domain Routing, CIDR, lets the street name be any length. "
                      "Slash twenty-one gives two thousand and forty-eight addresses. A snug fit."):
            self.play(FadeIn(fix, shift=UP * 0.2))
            self.play(FadeIn(glow(fix, T.GREEN, layers=5, spread=0.25)), run_time=0.5)
        agg = Callout("Bonus: routers can merge many neighbouring networks into one table entry",
                      color=T.PURPLE, size=T.SMALL_SIZE + 2).move_to(DOWN * 2.05)
        with self.say("And it has a bonus: routers can merge many neighbouring networks into a single "
                      "entry, which keeps backbone routing tables small."):
            self.play(FadeIn(agg, shift=UP * 0.2))


class MacAddress(CSScene):
    def construct(self):
        self.show_title("The other address: MAC")
        card = VGroup(RoundedRectangle(corner_radius=0.12, width=4.4, height=2.3, fill_color=T.LIME, fill_opacity=0.25,
                                       stroke_color=T.LIME, stroke_width=4),
                      *[Rectangle(width=0.22, height=0.35, fill_color=T.YELLOW, fill_opacity=1, stroke_width=0)
                        .move_to([-1.8 + i * 0.32, -1.3, 0]) for i in range(12)])
        card[0].move_to([0, -0.35, 0])
        chip = Square(0.9, fill_color=T.FAINT, fill_opacity=1, stroke_color=T.FG).move_to([-1.0, -0.1, 0])
        mac = make_text("3c:22:fb:9a:1e:07", size=T.BODY_SIZE, color=T.LIME, weight="BOLD").next_to(card, DOWN, buff=0.3)
        grp = VGroup(card, chip, mac).move_to([-2.6, 0.6, 0])
        with self.say("Every network card also has a MAC address: forty-eight bits, usually burned in "
                      "at the factory."):
            self.play(FadeIn(card), FadeIn(chip), Write(mac))
        cards = VGroup(
            Card("IP address", "like your postal address\nchanges when you move\nused across the Internet",
                 color=T.CYAN, width=4.6, size=T.SMALL_SIZE + 2, min_height=2.2),
            Card("MAC address", "like your name\nstays with the card\nonly used on the local link",
                 color=T.LIME, width=4.6, size=T.SMALL_SIZE + 2, min_height=2.2),
        ).arrange(DOWN, buff=0.3).move_to([3.6, 0.3, 0])
        with self.say("So why two addresses? The IP address is like your postal address. It says where "
                      "you are, and changes when you move to another network."):
            self.play(FadeIn(cards[0], shift=LEFT * 0.3))
        with self.say("The MAC address is more like your name. It's only used to hand a frame to the "
                      "very next box on the same local network."):
            self.play(FadeIn(cards[1], shift=LEFT * 0.3))


class Arp(CSScene):
    def construct(self):
        self.show_title("ARP: who has this IP address?")
        sw = NetNode("switch", "router", scale=1.2).move_to([0, -0.15, 0])
        pos = {"laptop .30": (-4.6, 0.95), "printer .31": (-4.6, -1.25), "TV .32": (4.6, -1.25), "router .1": (4.6, 0.95)}
        cols = {"laptop .30": T.CYAN, "printer .31": T.MUTED, "TV .32": T.MUTED, "router .1": T.PURPLE}
        nodes = {k: NetNode(k, "host", scale=1.15, color=cols[k]).move_to([x, y, 0]) for k, (x, y) in pos.items()}
        wires = VGroup(*[Line(sw.get_center(), n.get_center(), stroke_color=T.MUTED, stroke_width=3).set_z_index(-1) for n in nodes.values()])
        with self.say("Here's a home network. Your laptop wants to send a packet out to the Internet, "
                      "so it has to go to the router, at dot one."):
            self.play(FadeIn(wires), FadeIn(sw), *[FadeIn(n) for n in nodes.values()])
            self.play(Indicate(nodes["router .1"], color=T.PURPLE))
        q = Bubble("Who has 192.168.1.1?\nTell 192.168.1.30", T.CYAN, tail="down", size=T.SMALL_SIZE).next_to(nodes["laptop .30"], UP, buff=0.25)
        with self.say("It knows the router's IP address, but not its MAC address. So it shouts to "
                      "everyone: who has one ninety-two, one sixty-eight, one, one?"):
            self.play(FadeIn(q, scale=0.7))
            p0 = Packet("ARP?", T.CYAN, size=16).scale(1.2)
            self.play(p0.travel([nodes["laptop .30"].get_center(), sw.get_center()], run_time=0.7))
            self.remove(p0)
            ps = [Packet("ARP?", T.CYAN, size=16).scale(1.2) for _ in range(3)]
            others = ["printer .31", "TV .32", "router .1"]
            self.play(*[p.travel([sw.get_center(), nodes[o].get_center()], run_time=0.8) for p, o in zip(ps, others)])
            self.remove(*ps)
            self.play(*[nodes[o].flash(T.YELLOW, 5) for o in others], run_time=0.4)
        a = Bubble("192.168.1.1 is at\naa:bb:cc:00:11:22", T.PURPLE, tail="down", size=T.SMALL_SIZE).next_to(nodes["router .1"], UP, buff=0.25)
        with self.say("Every device hears it, but only the router answers, straight back to the laptop: "
                      "that's me, here's my MAC address."):
            self.play(nodes["printer .31"].reset(), nodes["TV .32"].reset(), FadeIn(a, scale=0.7))
            r = Packet("I'm aa:bb:...", T.PURPLE, size=16).scale(1.2)
            self.play(r.travel([nodes["router .1"].get_center(), sw.get_center(), nodes["laptop .30"].get_center()], run_time=1.4))
            self.remove(r)
            self.play(nodes["laptop .30"].flash(T.GREEN, 5))
        bridge = Callout("ARP links the network layer (IP) to the link layer (MAC). Answers are cached.",
                         color=T.YELLOW, size=T.SMALL_SIZE + 2).move_to(DOWN * 2.05)
        with self.say("The laptop remembers the answer for a while. That's ARP: the glue between the "
                      "IP layer and the link layer."):
            self.play(FadeOut(q), FadeOut(a), FadeIn(bridge, shift=UP * 0.2))


class Dhcp(CSScene):
    def construct(self):
        self.show_title("DHCP: the hotel reception")
        XB, XS = -4.6, 4.6
        hb = make_text("new laptop", size=T.BODY_SIZE, color=T.CYAN, weight="BOLD").move_to([XB, 2.3, 0])
        hs = make_text("DHCP server", size=T.BODY_SIZE, color=T.ORANGE, weight="BOLD").move_to([XS, 2.3, 0])
        lb = Line([XB, 1.95, 0], [XB, -1.25, 0], stroke_color=T.CYAN, stroke_width=4)
        ls = Line([XS, 1.95, 0], [XS, -1.25, 0], stroke_color=T.ORANGE, stroke_width=4)
        with self.say("And where did the laptop get its address in the first place? From DHCP, "
                      "just like Sam at the hotel reception."):
            self.play(FadeIn(hb), FadeIn(hs), Create(lb), Create(ls))
        steps = [(1.55, True, "DISCOVER  to 255.255.255.255", T.CYAN),
                 (0.8, False, "OFFER  192.168.1.100", T.ORANGE),
                 (0.05, True, "REQUEST  192.168.1.100  (broadcast)", T.CYAN),
                 (-0.7, False, "ACK  lease 24 h + mask, router, DNS", T.GREEN)]
        with self.say("Discover, shouted to everyone. Offer. Request. And acknowledge, which comes "
                      "with a lease time, the mask, the router's address and a DNS server."):
            for y, ltr, text, c in steps:
                x0, x1 = (XB, XS) if ltr else (XS, XB)
                ar = Arrow([x0, y, 0], [x1, y - 0.4, 0], buff=0, stroke_width=5, color=c, max_tip_length_to_length_ratio=0.04)
                lab = make_text(text, size=T.SMALL_SIZE + 2, color=c, weight="BOLD").move_to(ar.get_center() + UP * 0.3)
                self.play(GrowArrow(ar), FadeIn(lab), run_time=0.8)
        dora = make_text("D · O · R · A", size=T.HEADING_SIZE, color=T.YELLOW, weight="BOLD").move_to([0, -1.6, 0])
        with self.say("Remember it as DORA. And beware of a rogue server like Mallory's: whoever "
                      "answers first can name itself as your router, and see all your traffic."):
            self.play(Write(dora))
            self.play(Indicate(dora, color=T.YELLOW))


class Recap(CSScene):
    def construct(self):
        self.show_title("Addresses: recap")
        items = [
            "IPv4 address = 32 bits, written as four bytes",
            "Network part (street) + host part (house); the mask marks the split",
            "Host part all ones = broadcast; 255.255.255.255 = whole local network",
            "CIDR: prefixes of any length, and smaller routing tables",
            "MAC = name on the local link; ARP finds it; DHCP hands out addresses",
        ]
        bl = BulletList(items, size=T.BODY_SIZE + 2, spacing=0.5).move_to(UP * 0.2)
        self.add(bl)
        lines = ["To recap. An IP address is a thirty-two bit number.",
                 "The mask splits it into the street and the house.",
                 "The last address on a street is broadcast: everyone.",
                 "CIDR lets networks be any size.",
                 "The MAC address works on the local link, ARP finds it, and DHCP hands out addresses."]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()
        self.show_title("Coming next: home networks and NAT")
        a = CountUp("addresses", 4.3, size=T.HEADING_SIZE, color=T.CYAN, fmt="{:.1f} billion").move_to(UP * 0.8)
        d = CountUp("devices", 1, size=T.HEADING_SIZE, color=T.PINK, fmt="{:.0f} billion").move_to(DOWN * 0.4)
        with self.say("One last puzzle. Four point three billion addresses, but over twenty billion "
                      "connected devices. How does that work? Next time: NAT."):
            self.play(FadeIn(a), FadeIn(d))
            self.play(d.to(20, run_time=2.0))
            self.play(shake(d, 0.06, 8, 0.6))
        self.wait(0.6)
