"""TSAM #6: trust: DNS (recursive/iterative, spoofing, DNSSEC, open resolvers), keys, Diffie-Hellman,
certificate authorities, Kerckhoffs, nonces, password hashing, firewalls."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.04")

from manim import *  # noqa: E402

from csvideo import BulletList, Bubble, Callout, Card, Chip, CSScene, NetNode, Packet, make_text  # noqa: E402
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, glow, shake  # noqa: E402

SCENES = ["Dns", "Spoof", "SharedKey", "PaintMix", "Certificates", "Toolbox", "Recap"]

BROWN = ManimColor("#9A6B3F")


def bucket(color, label="", r=0.48):
    c = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_color=T.FG, stroke_width=2)
    g = VGroup(c)
    if label:
        g.add(make_text(label, size=T.SMALL_SIZE, color=T.FG).next_to(c, DOWN, buff=0.12))
    return g


class Dns(CSScene):
    def construct(self):
        self.show_title("DNS: the Internet's phone book")
        lap = NetNode("laptop", "host", scale=1.1, color=T.CYAN).move_to([-5.4, -0.9, 0])
        res = NetNode("resolver", "sender", scale=1.1, color=T.YELLOW).move_to([-2.0, -0.9, 0])
        root = NetNode("root  .", "host", scale=1.0, color=T.PURPLE).move_to([2.6, 1.6, 0])
        tld = NetNode(".is", "host", scale=1.0, color=T.PINK).move_to([2.6, 0.1, 0])
        auth = NetNode("ru.is", "host", scale=1.0, color=T.LIME).move_to([2.6, -1.4, 0])
        wires = VGroup(Line(lap.get_right(), res.get_left(), stroke_color=T.MUTED),
                       *[Line(res.get_right(), n.get_left(), stroke_color=T.MUTED) for n in (root, tld, auth)])
        with self.say("You type www dot r u dot i s. But packets need an IP address. Finding it is the "
                      "job of DNS, the domain name system."):
            self.play(FadeIn(wires), *[FadeIn(n) for n in (lap, res, root, tld, auth)])
        with self.say("Your laptop asks one resolver, and says: please find the whole answer for me. "
                      "That's a recursive query."):
            q = Packet("www.ru.is ?", T.CYAN, size=18).scale(1.2)
            self.play(q.travel([lap.get_center(), res.get_center()], run_time=1.0))
            self.remove(q)
        steps = [(root, "ask the .is servers", T.PURPLE), (tld, "ask ru.is's server", T.PINK), (auth, "130.208.240.8", T.LIME)]
        with self.say("The resolver then asks around, one server at a time. The root says: ask the dot i s "
                      "servers. They say: ask r u dot i s. And that server finally knows the address."):
            for node, ans, c in steps:
                p = Packet("?", T.YELLOW, size=18).scale(1.2)
                self.play(p.travel([res.get_center(), node.get_center()], run_time=0.7))
                self.remove(p)
                b = Bubble(ans, c, tail="left", size=T.SMALL_SIZE).next_to(node, RIGHT, buff=0.25)
                self.play(FadeIn(b, scale=0.7), node.flash(c, 5), run_time=0.5)
        it = Chip("each server just points onward: iterative", T.YELLOW, size=T.SMALL_SIZE + 2).move_to([-2.4, 1.0, 0])
        with self.say("Those answers that just point you onward are iterative queries. The resolver "
                      "hands the final answer back, and caches it for next time."):
            self.play(FadeIn(it, shift=DOWN * 0.2))
            a = Packet("130.208.240.8", T.LIME, size=18).scale(1.2)
            self.play(a.travel([res.get_center(), lap.get_center()], run_time=1.0))
            self.play(lap.flash(T.GREEN, 6))


class Spoof(CSScene):
    def construct(self):
        self.show_title("Faking the phone book")
        lap = NetNode("laptop", "host", scale=1.1, color=T.CYAN).move_to([-5.2, 0.9, 0])
        res = NetNode("resolver", "sender", scale=1.1, color=T.YELLOW).move_to([-1.2, 0.9, 0])
        auth = NetNode("ru.is", "host", scale=1.0, color=T.LIME).move_to([4.8, 1.9, 0])
        mal = NetNode("Mallory", "host", scale=1.0, color=T.RED).move_to([4.8, -0.2, 0])
        wires = VGroup(Line(lap.get_right(), res.get_left(), stroke_color=T.MUTED), Line(res.get_right(), auth.get_left(), stroke_color=T.MUTED),
                       Line(res.get_right(), mal.get_left(), stroke_color=T.MUTED))
        self.play(FadeIn(wires), *[FadeIn(n) for n in (lap, res, auth, mal)])
        with self.say("Here's the danger. Mallory races the real server, and sends a fake answer first: "
                      "www dot r u dot i s is at my address."):
            fake = Packet("ru.is = 6.6.6.6", T.RED, size=18).scale(1.2)
            real = Packet("ru.is = 130.208.240.8", T.LIME, size=18).scale(1.2)
            self.play(fake.travel([mal.get_center(), res.get_center()], run_time=1.0),
                      Succession(Wait(0.6), real.travel([auth.get_center(), res.get_center()], run_time=1.2)))
            self.play(res.flash(T.RED, 7), FadeOut(real), shake(res, 0.06, 6, 0.5))
        with self.say("The resolver believes it, caches it, and sends everybody who asks to Mallory's "
                      "fake site. That's DNS spoofing, or cache poisoning."):
            self.remove(fake)
            for _ in range(2):
                p = Packet("6.6.6.6", T.RED, size=18).scale(1.2)
                self.play(p.travel([res.get_center(), lap.get_center()], run_time=0.8))
                self.remove(p)
        fix = Callout("DNSSEC: answers are digitally signed; a forged answer fails the check",
                      color=T.GREEN, size=T.SMALL_SIZE + 4).move_to([0, -1.0, 0])
        with self.say("The fix is DNSSEC. Real answers carry a digital signature, so a resolver can tell "
                      "a forged one, and throw it away."):
            self.play(FadeIn(fix, shift=UP * 0.2))
        open_r = Callout("Open resolver: answers anyone, so attackers abuse it to flood victims",
                         color=T.ORANGE, size=T.SMALL_SIZE + 4).move_to([0, -1.75, 0])
        with self.say("And a resolver that answers anyone on the Internet, an open resolver, gets "
                      "abused: tiny forged questions trigger big answers aimed at a victim."):
            self.play(FadeIn(open_r, shift=UP * 0.2))


class SharedKey(CSScene):
    def construct(self):
        self.show_title("Locking the note: a shared key")
        sam = NetNode("Sam", "host", scale=1.2, color=T.CYAN).move_to([-5.0, 0.6, 0])
        mal = NetNode("Mallory", "host", scale=1.2, color=T.RED).move_to([0, 0.6, 0])
        ada = NetNode("Ada", "host", scale=1.2, color=T.PINK).move_to([5.0, 0.6, 0])
        line = Line(sam.get_right(), ada.get_left(), stroke_color=T.MUTED).set_z_index(-1)
        with self.say("Back to Sam's note. Sam and Ada could lock it with a shared secret key. The same "
                      "key locks and unlocks it. That's a symmetric cipher, and it's fast."):
            self.play(FadeIn(line), FadeIn(sam), FadeIn(mal), FadeIn(ada))
            key_s = Chip("key K", T.YELLOW, filled=True).next_to(sam, DOWN, buff=0.3)
            key_a = Chip("key K", T.YELLOW, filled=True).next_to(ada, DOWN, buff=0.3)
            self.play(FadeIn(key_s), FadeIn(key_a))
            p = Packet("x7#Qp!", T.YELLOW, size=20).scale(1.3)
            self.play(p.travel([sam.get_center(), mal.get_center()], run_time=1.0))
            b = Bubble("?!", T.RED, tail="down", size=T.BODY_SIZE).next_to(mal, UP, buff=0.2)
            self.play(FadeIn(b, scale=0.6))
            self.play(p.travel([mal.get_center(), ada.get_center()], run_time=1.0), FadeOut(b))
            self.remove(p)
        with self.say("But how did they agree on that key? If Sam just sends it, Mallory copies it on "
                      "the way, and can read everything after that."):
            k = Chip("key K", T.YELLOW, filled=True)
            self.play(k.animate.move_to(mal.get_center() + UP * 0.9), run_time=1.0)
            copy = k.copy()
            self.play(copy.animate.next_to(mal, DOWN, buff=0.3), k.animate.move_to(ada.get_center() + UP * 0.9), run_time=1.0)
            self.play(Indicate(copy, color=T.RED, scale_factor=1.3))
        q = Callout("The key exchange problem: agree on a secret over a channel Mallory can read",
                    color=T.ORANGE, size=T.SMALL_SIZE + 4).move_to([0, -1.6, 0])
        with self.say("Agreeing on a secret, over a line that someone is listening to. That sounds "
                      "impossible. It isn't."):
            self.play(FadeIn(q, shift=UP * 0.2))


class PaintMix(CSScene):
    def construct(self):
        self.show_title("Diffie–Hellman: mixing paint")
        xs, xa = -4.6, 4.6
        hs = make_text("Sam", size=T.BODY_SIZE, color=T.CYAN, weight="BOLD").move_to([xs, 2.4, 0])
        ha = make_text("Ada", size=T.BODY_SIZE, color=T.PINK, weight="BOLD").move_to([xa, 2.4, 0])
        hm = make_text("Mallory sees", size=T.BODY_SIZE, color=T.RED, weight="BOLD").move_to([0, 2.4, 0])
        pub = bucket(T.YELLOW, "public").move_to([0, 1.45, 0])
        with self.say("The classic trick is Diffie–Hellman. Think of it as mixing paint. Everyone, "
                      "even Mallory, knows one public colour: yellow."):
            self.play(FadeIn(hs), FadeIn(ha), FadeIn(hm), FadeIn(pub, scale=0.6))
        sec_s = bucket(T.RED, "Sam's secret").move_to([xs, 1.45, 0])
        sec_a = bucket(T.BLUE, "Ada's secret").move_to([xa, 1.45, 0])
        with self.say("Sam picks a secret colour, red, and Ada picks blue. They never send those to anyone."):
            self.play(FadeIn(sec_s, scale=0.6), FadeIn(sec_a, scale=0.6))
        mix_s = bucket(T.ORANGE, "yellow + red").move_to([xs, 0.15, 0])
        mix_a = bucket(T.LIME, "yellow + blue").move_to([xa, 0.15, 0])
        with self.say("Each one mixes their secret into the public yellow, and sends the mixture across. "
                      "Orange from Sam, green from Ada."):
            self.play(TransformFromCopy(VGroup(pub[0], sec_s[0]), mix_s[0]), FadeIn(mix_s[1]),
                      TransformFromCopy(VGroup(pub[0], sec_a[0]), mix_a[0]), FadeIn(mix_a[1]), run_time=1.2)
            seen_o = mix_s[0].copy()
            seen_g = mix_a[0].copy()
            self.play(seen_o.animate.move_to([-0.6, 0.0, 0]), seen_g.animate.move_to([0.6, 0.0, 0]), run_time=1.0)
            self.play(mix_s[0].animate.move_to([xa - 1.4, 0.0, 0]), mix_a[0].animate.move_to([xs + 1.4, 0.0, 0]),
                      FadeOut(mix_s[1]), FadeOut(mix_a[1]), run_time=1.2)
        fin_s = bucket(BROWN, "shared secret").move_to([xs, -1.2, 0])
        fin_a = bucket(BROWN, "shared secret").move_to([xa, -1.2, 0])
        with self.say("Now each adds their own secret to what they received. Sam adds red to green. Ada "
                      "adds blue to orange. Both get exactly the same brown."):
            self.play(TransformFromCopy(VGroup(mix_a[0], sec_s[0]), fin_s[0]), FadeIn(fin_s[1]),
                      TransformFromCopy(VGroup(mix_s[0], sec_a[0]), fin_a[0]), FadeIn(fin_a[1]), run_time=1.4)
            self.play(Flash(fin_s, color=BROWN, line_length=0.3), Flash(fin_a, color=BROWN, line_length=0.3))
        q = make_text("Can Mallory make the brown?", size=T.BODY_SIZE, color=T.YELLOW, weight="BOLD").move_to([0, -1.95, 0])
        cd = Countdown(3).move_to([0, -1.0, 0]).scale(0.75)
        with self.say("Your turn. Mallory has yellow, orange and green. Can he make the brown?"):
            self.play(FadeIn(q))
            self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        wrong = bucket(ManimColor("#B08A3A"), "").move_to([0, -1.05, 0])
        cross = VGroup(Line(UL * 0.3, DR * 0.3), Line(UR * 0.3, DL * 0.3)).set_stroke(T.RED, 7).move_to(wrong)
        with self.say("No. Mixing orange and green gives him a muddy colour with far too much yellow in it. "
                      "He can't un-mix paint to get the secrets back."):
            self.play(FadeOut(cd), FadeOut(q), FadeIn(wrong, scale=0.6))
            self.play(FadeIn(cross, scale=1.6))
        note = Callout("Real Diffie–Hellman uses maths that's easy one way and practically impossible to reverse",
                       color=T.PURPLE, size=T.SMALL_SIZE + 2).move_to([0, -2.0, 0])
        with self.say("Real Diffie–Hellman does this with maths that is easy one way, and practically "
                      "impossible to undo. Public-key encryption solves the same problem."):
            self.play(FadeIn(note, scale=0.9))


class Certificates(CSScene):
    def construct(self):
        self.show_title("But who am I really talking to?")
        sam = NetNode("Sam", "host", scale=1.2, color=T.CYAN).move_to([-5.0, 0.9, 0])
        mal = NetNode("Mallory", "host", scale=1.2, color=T.RED).move_to([0, 0.9, 0])
        ada = NetNode("ru.is", "host", scale=1.2, color=T.PINK).move_to([5.0, 0.9, 0])
        line = Line(sam.get_right(), ada.get_left(), stroke_color=T.MUTED).set_z_index(-1)
        with self.say("One problem left. What if Mallory sits in the middle and does the key exchange "
                      "with both sides? Sam thinks he's talking to r u dot i s, but it's Mallory."):
            self.play(FadeIn(line), FadeIn(sam), FadeIn(mal), FadeIn(ada))
            b1 = Bubble("I'm ru.is!", T.RED, tail="down", size=T.SMALL_SIZE + 2).next_to(mal, UP, buff=0.25).shift(LEFT * 1.3)
            b2 = Bubble("I'm Sam!", T.RED, tail="down", size=T.SMALL_SIZE + 2).next_to(mal, UP, buff=0.25).shift(RIGHT * 1.3)
            self.play(FadeIn(b1, scale=0.6), FadeIn(b2, scale=0.6))
        cert = VGroup(RoundedRectangle(corner_radius=0.12, width=5.6, height=1.7, fill_color=T.FAINT, fill_opacity=1, stroke_color=T.GREEN, stroke_width=4),
                      make_text("This public key belongs to ru.is", size=T.SMALL_SIZE + 2, color=T.FG).shift(UP * 0.35),
                      make_text("signed: a Certificate Authority", size=T.SMALL_SIZE, color=T.GREEN, weight="BOLD").shift(DOWN * 0.3))
        cert.move_to([2.9, -1.2, 0])
        with self.say("That's what certificates are for. A Certificate Authority checks who owns a site, "
                      "and signs a statement: this public key belongs to r u dot i s."):
            self.play(FadeOut(b1), FadeOut(b2), FadeIn(cert, shift=UP * 0.3))
        trust = Chip("browser trusts a built-in list of CAs", T.GREEN, size=T.SMALL_SIZE + 2).move_to([-3.4, -1.2, 0])
        with self.say("Your browser ships with a list of authorities it trusts. Mallory can't forge their "
                      "signature, so his fake key gets a big red warning."):
            self.play(FadeIn(trust))
            self.play(mal.flash(T.RED, 8), shake(mal, 0.06, 8, 0.6))


class Toolbox(CSScene):
    def construct(self):
        self.show_title("Four more words from the exams")
        cards = VGroup(
            Card("Kerckhoffs' principle", "a system should stay secure even\nif everything except the key\nis public", color=T.CYAN, width=6.0, size=T.SMALL_SIZE + 2, min_height=1.9),
            Card("Nonce", "a number used once, so a\nrecorded message can't be\nreplayed later", color=T.PINK, width=6.0, size=T.SMALL_SIZE + 2, min_height=1.9),
            Card("Passwords: not MD5", "MD5 is broken and too fast to\nguess against. Use a slow,\nsalted hash", color=T.ORANGE, width=6.0, size=T.SMALL_SIZE + 2, min_height=1.9),
            Card("Firewall", "filters traffic by rules on\nIP addresses, ports\nand direction", color=T.LIME, width=6.0, size=T.SMALL_SIZE + 2, min_height=1.9),
        )
        cards.arrange_in_grid(2, 2, buff=0.3).move_to(UP * 0.3)
        lines = ["Kerckhoffs' principle: assume the attacker knows exactly how your system works. Only the key "
                 "stays secret.",
                 "A nonce is a number used once. It stops Mallory from recording a message and replaying it later.",
                 "Don't store passwords with MD5. It's broken, and so fast that guessing is cheap. Use a slow, "
                 "salted hash.",
                 "And a firewall filters traffic with rules about addresses, ports and direction."]
        for card, text in zip(cards, lines):
            with self.say(text):
                self.play(FadeIn(card, shift=UP * 0.2), run_time=0.7)
                self.play(Indicate(card.heading, scale_factor=1.08), run_time=0.6)


class Recap(CSScene):
    def construct(self):
        self.show_title("Trust on the Internet: recap")
        items = [
            "DNS turns names into addresses: recursive to the resolver, iterative beyond",
            "Spoofed answers poison caches; DNSSEC signs the real ones",
            "Symmetric keys are fast, but must be shared: Diffie–Hellman",
            "Certificates from CAs prove whose public key it is",
            "Kerckhoffs, nonces, slow salted hashes, firewalls",
        ]
        bl = BulletList(items, size=T.BODY_SIZE, spacing=0.5).move_to(UP * 0.2)
        self.add(bl)
        lines = ["To recap. DNS turns names into addresses.",
                 "Fake answers can poison it, and DNSSEC signatures stop that.",
                 "Shared keys are fast, and Diffie–Hellman lets two strangers agree on one in public.",
                 "Certificates prove who a public key really belongs to.",
                 "And a handful of principles keep the rest safe."]
        for i, text in enumerate(lines):
            with self.say(text):
                self.play(bl.reveal(i), run_time=0.6)
        self.clear_content()
        self.show_title("That's the tour!")
        eps = VGroup(*[Chip(t, T.PALETTE[i], size=T.BODY_SIZE - 4, filled=True) for i, t in enumerate(
            ["1  the journey", "2  TCP up close", "3  speed & jams", "4  addresses", "5  home networks", "6  trust"])])
        eps.arrange_in_grid(2, 3, buff=0.35).move_to(UP * 0.4)
        with self.say("That's the whole tour. Now grab an old exam, and try the questions. You'll find "
                      "you know a lot more than you think."):
            self.play(LaggedStart(*[FadeIn(e, scale=1.3) for e in eps], lag_ratio=0.15))
            self.play(*[Flash(e, color=T.PALETTE[i], line_length=0.25) for i, e in enumerate(eps)], run_time=0.8)
        self.wait(0.8)
