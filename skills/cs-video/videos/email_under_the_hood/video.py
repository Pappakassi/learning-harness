"""How email works under the hood, with Hr. Schiffel. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo.effects import Countdown, CountUp  # noqa: E402
from csvideo.story import P, StoryScene, theme_intro, theme_outro, txt  # noqa: E402
from csvideo.story_kit import (ByteRow, Envelope, Laptop, Padlock, Server, Terminal, pulse,  # noqa: E402
                               trail_dot)

SCENES = ["Intro", "Hook", "Cast", "MxLookup", "Smtp", "EnvelopeVsLetter", "Attachments", "Trust", "Fetch", "Outro"]

# the pipeline used in several scenes
X = {"you": -5.6, "out": -2.1, "in": 1.6, "box": 5.3}


def pipeline():
    you = Laptop("you", P.TEAL, scale=0.75).move_to([X["you"], 0.3, 0])
    out = Server("smtp.ru.is", P.BLUE, scale=0.8).move_to([X["out"], 0.3, 0])
    inn = Server("mx.example.jp", P.PINK, scale=0.8).move_to([X["in"], 0.3, 0])
    yuki = Laptop("Yuki", P.GOLD, scale=0.75).move_to([X["box"], 0.3, 0])
    nodes = [you, out, inn, yuki]
    wires = VGroup(*[Line(a.body.get_right() if hasattr(a, "body") else a.get_right(), b.get_left(), stroke_color=P.MUTED, stroke_width=3)
                     for a, b in zip(nodes, nodes[1:])])
    for w, a, b in zip(wires, nodes, nodes[1:]):
        w.put_start_and_end_on(a.get_right() + RIGHT * 0.1 + UP * 0.1, b.get_left() + LEFT * 0.1 + UP * 0.1)
    protos = VGroup(*[txt(s, size=24, color=c, weight="BOLD").next_to(w, UP, buff=0.2)
                      for s, c, w in (("SMTP :587", P.BLUE, wires[0]), ("SMTP :25", P.PINK, wires[1]), ("IMAP :993", P.GOLD, wires[2]))])
    return nodes, wires, protos


class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "How email works", "under the hood, with Hr. Schiffel")
        self.wait(0.3)


class Hook(StoryScene):
    def construct(self):
        g = self.add_gnome("fierce", animate=False)
        a = Laptop("you, in Akureyri", P.TEAL, scale=0.9).move_to([-4.6, -0.6, 0])
        b = Laptop("Yuki, in Tokyo", P.GOLD, scale=0.9).move_to([3.6, -0.6, 0])
        arc = ArcBetweenPoints(a.get_top() + UP * 0.2, b.get_top() + UP * 0.2, angle=-PI / 2.2, stroke_color=P.FAINT, stroke_width=3)
        with self.say("You press send. A second later, the message is sitting in an inbox in Tokyo."):
            self.play(FadeIn(a, shift=UP * 0.2), FadeIn(b, shift=UP * 0.2))
            self.play(Create(arc), run_time=0.8)
            env = Envelope("yuki@example.jp", width=1.2).move_to(arc.get_start())
            self.add(env)
            self.play(MoveAlongPath(env, arc), run_time=2.2, rate_func=smooth)
            self.play(Flash(b.screen, color=P.GOLD, line_length=0.3))
        with self.say("Gnomes. Obviously. Very fast gnomes.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        with self.say("Close. But what's really carrying it is a chain of servers, a few short text "
                      "conversations, and the DNS. Let's open it up."):
            self.play(g.change("thinking", look=LEFT), run_time=0.6)
            self.play(FadeOut(env), Uncreate(arc), run_time=0.8)
            self.play(FadeOut(a), FadeOut(b))


class Cast(StoryScene):
    def construct(self):
        self.chapter("1. The journey", label="1  The journey")
        g = self.add_gnome("fierce")
        nodes, wires, protos = pipeline()
        you, out, inn, yuki = nodes
        with self.say("It starts in your mail app, on your laptop."):
            self.play(FadeIn(you, shift=UP * 0.2))
        with self.say("Your app hands the message to your own provider's outgoing server, using SMTP, "
                      "the simple mail transfer protocol."):
            self.play(Create(wires[0]), FadeIn(out, shift=UP * 0.2))
            self.play(Write(protos[0]))
            e = Envelope(width=0.8).move_to(you.get_center() + UP * 0.9)
            self.play(FadeIn(e, scale=0.5))
            self.play(e.animate.move_to(out.get_center() + UP * 1.2), pulse(wires[0], P.BLUE), run_time=1.2)
        with self.say("That server finds the recipient's mail server, and passes the message on. "
                      "Server to server, it's SMTP again."):
            self.play(Create(wires[1]), FadeIn(inn, shift=UP * 0.2))
            self.play(Write(protos[1]))
            self.play(e.animate.move_to(inn.get_center() + UP * 1.2), pulse(wires[1], P.PINK), run_time=1.2)
        with self.say("There it waits in Yuki's mailbox, until her own app comes to collect it, with a "
                      "different protocol: IMAP."):
            self.play(Create(wires[2]), FadeIn(yuki, shift=UP * 0.2))
            self.play(Write(protos[2]))
            self.play(e.animate.move_to(yuki.get_center() + UP * 0.9), pulse(wires[2], P.GOLD), run_time=1.2)
            self.play(Flash(yuki.screen, color=P.GOLD, line_length=0.3))
        key = txt("SMTP pushes mail towards the recipient.   IMAP lets the recipient pull it.", size=26, color=P.FG).move_to(DOWN * 1.9)
        with self.say("Notice the two directions. SMTP pushes mail towards the recipient. IMAP lets the "
                      "recipient pull it."):
            self.play(Write(key), run_time=1.5)
        with self.say("Three hops, two protocols, zero magic.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(FadeOut(e), FadeOut(key), g.change("fierce"))


class MxLookup(StoryScene):
    def construct(self):
        self.chapter("2. Where does it go?", label="2  The MX record")
        g = self.add_gnome("fierce", animate=False)
        nodes, wires, protos = pipeline()
        self.add(*nodes, wires, protos)
        out = nodes[1]
        with self.say("But how does your provider's server know where Yuki's mail server is? All it "
                      "has is the address: yuki at example dot j p."):
            self.play(self.zoom_to(out, margin=3.2))
            self.play(Indicate(out, color=P.BLUE))
        others = VGroup(nodes[0], nodes[2], nodes[3], wires, protos)
        self.play(self.zoom_reset(), FadeOut(others), out.animate.move_to([-4.2, -0.4, 0]), run_time=1.2)
        dns = Server("DNS", P.PURPLE, scale=0.8).move_to([0.6, 1.2, 0])
        wire = Line(out.get_right() + UP * 0.2, dns.get_left(), stroke_color=P.PURPLE, stroke_width=3)
        q = txt("MX  example.jp ?", size=28, color=P.BLUE, weight="BOLD").next_to(wire.get_center(), UP + LEFT, buff=0.15)
        with self.say("It asks the DNS a special question. Not the usual: what's the address of this "
                      "name? But: who handles mail for example dot j p?"):
            self.play(FadeIn(dns), Create(wire))
            self.play(Write(q))
            self.play(pulse(wire, P.BLUE))
        ans = VGroup(txt("10  mx1.example.jp", size=28, color=P.GREEN, font="DejaVu Sans Mono"),
                     txt("20  mx2.example.jp", size=28, color=P.MUTED, font="DejaVu Sans Mono")).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        ans.next_to(dns, RIGHT, buff=0.5)
        with self.say("The answer is a list of MX records, mail exchangers, each with a priority. "
                      "The lowest number is tried first. The other is a backup."):
            self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in ans], lag_ratio=0.4))
            self.play(Circumscribe(ans[0], color=P.GREEN))
        a_rec = txt("mx1.example.jp  →  203.0.113.25", size=28, color=P.YELLOW, font="DejaVu Sans Mono").move_to([1.6, -1.3, 0])
        with self.say("One more ordinary lookup turns that name into an IP address, and the server "
                      "opens a TCP connection to it, on port twenty-five."):
            self.play(TransformFromCopy(ans[0][4:], a_rec), run_time=1.0)
            self.play(Indicate(a_rec, color=P.YELLOW))
        with self.say("The MX record. That's DNS doing post office work.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(g.change("fierce"), FadeOut(VGroup(q, wire, dns, ans, a_rec, out)))


class Smtp(StoryScene):
    def construct(self):
        self.chapter("3. The SMTP conversation", label="3  SMTP")
        g = self.add_gnome("fierce", animate=False)
        term = Terminal(width=9.4, lines=10, title="TCP connection to mx1.example.jp, port 25", font_size=24).move_to(UP * 0.2)
        with self.say("Here's the part that surprises everyone. Once the TCP connection is open, the two "
                      "servers just talk. In plain text. Like this."):
            self.play(FadeIn(term, scale=0.95))
        steps = [
            ([("220 mx1.example.jp ESMTP ready", "S")], "The receiving server speaks first: two twenty, I'm ready."),
            ([("EHLO smtp.ru.is", "C"), ("250-mx1.example.jp hello", "S"), ("250 STARTTLS", "S")],
             "The sender says hello, EHLO, and the server lists what it supports. Including STARTTLS."),
        ]
        for lines, say in steps:
            with self.say(say):
                for t, w in lines:
                    self.play(term.type(t, w))
        lock = Padlock(P.GOLD, closed=False, size=0.6).next_to(term.box, RIGHT, buff=0.3).shift(UP * 1.2)
        with self.say("STARTTLS switches the rest of the conversation to encryption, so nobody on the "
                      "way can read it."):
            self.play(term.type("STARTTLS", "C"))
            self.play(FadeIn(lock, scale=0.6))
            self.play(lock.close(), term.box.animate.set_stroke(P.GOLD, 3), run_time=0.6)
        steps = [
            ([("MAIL FROM:<hinni@ru.is>", "C"), ("250 OK", "S")], "Then: mail from. Who is sending."),
            ([("RCPT TO:<yuki@example.jp>", "C"), ("250 OK", "S")], "Recipient to. Who should get it. One line per recipient."),
            ([("DATA", "C"), ("354 end with a single dot", "S")], "DATA: here comes the message itself."),
            ([("Subject: Tómas's birthday", None), ("Hi Yuki, see you on Friday!", None), (".", "C"), ("250 queued as 7F3A2", "S")],
             "The headers and the text follow, and a line with a single dot means: that's the end."),
            ([("QUIT", "C"), ("221 bye", "S")], "Quit. Bye. Done."),
        ]
        for lines, say in steps:
            with self.say(say):
                for t, w in lines:
                    self.play(term.type(t, w))
        with self.say("Just text! You could type that yourself. Gnomes did, in the nineteen eighties.", who="gnome"):
            self.play(g.change("angry"))
            self.play(g.hop())
        self.play(g.change("fierce"), FadeOut(VGroup(term, lock)))


class EnvelopeVsLetter(StoryScene):
    def construct(self):
        self.chapter("4. The envelope and the letter", label="4  Envelope vs letter")
        g = self.add_gnome("fierce", animate=False)
        env = Envelope(width=5.2).move_to([-3.3, 0.5, 0])
        outside = VGroup(txt("MAIL FROM: hinni@ru.is", size=19, color="#3A2A10", font="DejaVu Sans Mono"),
                         txt("RCPT TO:   yuki@example.jp", size=19, color="#3A2A10", font="DejaVu Sans Mono"),
                         txt("RCPT TO:   boss@ru.is", size=19, color="#3A2A10", font="DejaVu Sans Mono")).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        outside.move_to(env.body.get_center() + DOWN * 0.45)
        env_l = txt("the envelope (SMTP)", size=22, color=P.GOLD).next_to(env, UP, buff=0.2)
        with self.say("There's a subtle idea hiding in that conversation. MAIL FROM and RCPT TO are like "
                      "the envelope. The post office reads only those."):
            self.play(FadeIn(env, shift=UP * 0.2), FadeIn(env_l))
            self.play(Write(outside[:2]))
        letter = RoundedRectangle(corner_radius=0.08, width=4.8, height=3.0, fill_color="#FBF7EE", fill_opacity=1, stroke_width=0).move_to([3.1, 0.5, 0])
        inside = VGroup(txt("From: hinni@ru.is", size=19, color="#222222", font="DejaVu Sans Mono"),
                        txt("To:   yuki@example.jp", size=19, color="#222222", font="DejaVu Sans Mono"),
                        txt("Subject: Tómas's birthday", size=19, color="#222222", font="DejaVu Sans Mono"),
                        txt("Hi Yuki, see you on Friday!", size=21, color="#444444")).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        inside[3].shift(DOWN * 0.25)
        inside.move_to(letter)
        let_l = txt("the letter (headers + text)", size=22, color=P.FG).next_to(letter, UP, buff=0.2)
        with self.say("The From and To headers are written on the letter inside. Your mail app shows "
                      "you those. And nothing forces them to match the envelope."):
            self.play(TransformFromCopy(env.body, letter), FadeIn(let_l), run_time=1.0)
            self.play(Write(inside), run_time=1.5)
        with self.say("That's how blind copy works. The boss is on the envelope, but not written on "
                      "the letter, so Yuki never sees him."):
            self.play(Write(outside[2]))
            self.play(Circumscribe(outside[2], color=P.PINK), Indicate(inside[1], color=P.PINK))
        self.play(FadeOut(VGroup(env, outside, letter, inside, env_l, let_l)))
        fake_env = Envelope(width=5.2).move_to([-3.3, 0.9, 0])
        fe = txt("MAIL FROM: mallory@evil.example", size=19, color="#3A2A10", font="DejaVu Sans Mono").move_to(fake_env.body.get_center() + DOWN * 0.4)
        fake_letter = RoundedRectangle(corner_radius=0.08, width=5.0, height=1.6, fill_color="#FBF7EE", fill_opacity=1, stroke_width=0).move_to([3.1, 0.9, 0])
        fl = VGroup(txt("From: ceo@yourbank.com", size=19, color="#222222", font="DejaVu Sans Mono"),
                    txt("Subject: urgent, reset password", size=19, color="#222222", font="DejaVu Sans Mono")).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(fake_letter)
        q = txt("Which sender does your mail app show?", size=30, color=P.YELLOW, weight="BOLD").move_to([-0.6, -1.1, 0])
        cd = Countdown(3).scale(0.7).next_to(q, RIGHT, buff=0.4)
        with self.say("Your turn. On the envelope: mallory at evil dot example. On the letter: the CEO "
                      "of your bank. Which one does your mail app show you?"):
            self.play(FadeIn(fake_env), Write(fe), FadeIn(fake_letter), Write(fl))
            self.play(Write(q))
            self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        with self.say("The letter. The bank's name. That's why faking a sender is so easy, unless the "
                      "receiver checks. More on that in a moment."):
            self.play(FadeOut(cd), Circumscribe(fl[0], color=P.RED), fake_letter.animate.set_stroke(P.RED, 4))
        with self.say("Bah! Forgery. In my mailbox.", who="gnome"):
            self.play(g.change("angry"))
        self.play(g.change("fierce"), FadeOut(VGroup(fake_env, fe, fake_letter, fl, q)))


class Attachments(StoryScene):
    def construct(self):
        self.chapter("5. Attachments", label="5  Attachments: base64")
        g = self.add_gnome("fierce", animate=False)
        photo = ByteRow(["FF", "D8", "FF", "E0", "00", "10", "4A", "46"], color=P.TEAL).move_to(UP * 1.6)
        lab = txt("the first bytes of a JPEG photo", size=22, color=P.MUTED).next_to(photo, UP, buff=0.2)
        with self.say("SMTP was built for plain text. So what about a photo? A photo is raw bytes, and "
                      "many of them aren't printable characters at all."):
            self.play(FadeIn(lab), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in photo], lag_ratio=0.08))
        three = photo[:3]
        bits = "111111111101100011111111"
        row = VGroup(*[txt(b, size=24, color=P.TEAL, font="DejaVu Sans Mono") for b in bits]).arrange(RIGHT, buff=0.07).move_to(UP * 0.2)
        with self.say("The trick is called base64. Take three bytes. That's twenty-four bits."):
            self.play(*[photo[i].animate.set_opacity(0.25) for i in range(3, 8)], Circumscribe(three, color=P.YELLOW))
            self.play(TransformFromCopy(three, row), run_time=1.2)
        groups = VGroup(*[VGroup(*row[i * 6:(i + 1) * 6]) for i in range(4)])
        with self.say("Cut them into four groups of six bits."):
            self.play(*[groups[i].animate.shift(RIGHT * (i - 1.5) * 0.45) for i in range(4)], run_time=0.8)
            braces = VGroup(*[Brace(gp, DOWN, color=P.MUTED) for gp in groups])
            self.play(FadeIn(braces))
        chars = VGroup(*[txt(c, size=48, color=P.YELLOW, font="DejaVu Sans Mono", weight="BOLD") for c in "/9j/"])
        for c, b in zip(chars, braces):
            c.next_to(b, DOWN, buff=0.15)
        with self.say("Six bits make a number from zero to sixty-three, and each number is one safe, "
                      "printable character. Every JPEG in your inbox starts with slash, nine, j, slash."):
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in chars], lag_ratio=0.25))
        cu = CountUp("a 3 MB photo becomes", 3, size=30, color=P.GOLD, fmt="{:.1f} MB").move_to(DOWN * 2.35)
        with self.say("Three bytes become four characters, so attachments grow by about a third on the way."):
            self.play(FadeIn(cu))
            self.play(cu.to(4.0, run_time=1.4))
        with self.say("A third bigger. For nothing. Typical.", who="gnome"):
            self.play(g.change("angry"), run_time=0.5)
        self.play(g.change("fierce"), FadeOut(VGroup(photo, lab, row, braces, chars, cu)))


class Trust(StoryScene):
    def construct(self):
        self.chapter("6. Can I trust the sender?", label="6  SPF, DKIM, DMARC")
        g = self.add_gnome("fierce", animate=False)
        srv = Server("mx.example.jp", P.PINK, scale=1.0).move_to([0.8, 0.4, 0])
        checks = VGroup()
        names = [("SPF", "is this server allowed to send for ru.is?"),
                 ("DKIM", "does the signature match ru.is's public key?"),
                 ("DMARC", "what does ru.is say to do if they fail?")]
        for i, (n, d) in enumerate(names):
            light = Circle(radius=0.17, fill_color=P.FAINT, fill_opacity=1, stroke_color=P.MUTED, stroke_width=2)
            row = VGroup(light, txt(n, size=26, color=P.FG, weight="BOLD"), txt(d, size=20, color=P.MUTED)).arrange(RIGHT, buff=0.25)
            checks.add(row)
        checks.arrange(DOWN, aligned_edge=LEFT, buff=0.32).next_to(srv, RIGHT, buff=0.5).shift(LEFT * 0.2)
        VGroup(srv, checks).move_to(UP * 0.4)
        with self.say("So the receiving server checks. Three checks, all published in the sender's DNS."):
            self.play(FadeIn(srv), LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in checks], lag_ratio=0.3))
        with self.say("SPF: a list of the servers that may send mail for r u dot i s. DKIM: a digital "
                      "signature on the message, checked against a public key in DNS."):
            self.play(Indicate(checks[0][1]), run_time=0.8)
            self.play(Indicate(checks[1][1]), run_time=0.8)
        with self.say("And DMARC: the domain's instructions for what to do when those checks fail."):
            self.play(Indicate(checks[2][1]), run_time=0.8)
        good = Envelope("from hinni@ru.is", width=1.5).move_to([-5.6, 0.4, 0])
        with self.say("A real message from Hinni passes: green, green, green. Delivered."):
            self.play(FadeIn(good))
            self.play(good.animate.move_to(srv.get_center() + LEFT * 1.6), run_time=1.0)
            for c in checks:
                self.play(c[0].animate.set_fill(P.GREEN, 1).set_stroke(P.GREEN), run_time=0.3)
            self.play(good.animate.shift(DOWN * 2.2).set_opacity(0), run_time=0.6)
        self.play(*[c[0].animate.set_fill(P.FAINT, 1).set_stroke(P.MUTED) for c in checks], run_time=0.3)
        bad = Envelope("from ceo@yourbank.com", width=1.5).move_to([-5.6, 0.4, 0])
        bin_ = VGroup(Polygon([-0.5, 0.4, 0], [0.5, 0.4, 0], [0.38, -0.5, 0], [-0.38, -0.5, 0], fill_color=P.FAINT, fill_opacity=1,
                              stroke_color=P.RED, stroke_width=3), txt("rejected", size=20, color=P.RED)).move_to([-2.0, -2.0, 0])
        bin_[1].next_to(bin_[0], RIGHT, buff=0.2)
        with self.say("Mallory's forgery doesn't come from the bank's servers, and has no valid signature. "
                      "Red, red. And the bank's DMARC policy says: reject."):
            self.play(FadeIn(bad), FadeIn(bin_))
            self.play(bad.animate.move_to(srv.get_center() + LEFT * 1.6), run_time=1.0)
            self.play(checks[0][0].animate.set_fill(P.RED, 1).set_stroke(P.RED), run_time=0.3)
            self.play(checks[1][0].animate.set_fill(P.RED, 1).set_stroke(P.RED), run_time=0.3)
            self.play(checks[2][0].animate.set_fill(P.RED, 1).set_stroke(P.RED), run_time=0.3)
            self.play(bad.animate.move_to(bin_[0]).scale(0.3), run_time=0.8)
        with self.say("Into the bin! Hah!", who="gnome"):
            self.play(g.change("happy"))
            self.play(g.hop())
        self.play(g.change("fierce"), FadeOut(VGroup(srv, checks, bad, bin_, good)))


class Fetch(StoryScene):
    def construct(self):
        self.chapter("7. Picking it up", label="7  IMAP and POP3")
        g = self.add_gnome("fierce", animate=False)
        box = Server("Yuki's mailbox", P.PINK, scale=0.9).move_to([0, 0.6, 0])
        phone = RoundedRectangle(corner_radius=0.15, width=0.9, height=1.5, fill_color=P.FAINT, fill_opacity=1,
                                 stroke_color=P.GOLD, stroke_width=3).move_to([-4.2, 0.4, 0])
        lap = Laptop("laptop", P.GOLD, scale=0.7).move_to([4.2, 0.4, 0])
        pl = txt("phone", size=22, color=P.GOLD).next_to(phone, DOWN, buff=0.15)
        w1 = Line(phone.get_right(), box.get_left() + LEFT * 0.1, stroke_color=P.MUTED)
        w2 = Line(box.get_right() + RIGHT * 0.1, lap.get_left(), stroke_color=P.MUTED)
        with self.say("Last step. The message sits on Yuki's mail server. With IMAP, her phone and her "
                      "laptop both look at that same mailbox."):
            self.play(FadeIn(box), FadeIn(phone), FadeIn(pl), FadeIn(lap), Create(w1), Create(w2))
        msgs = VGroup(*[RoundedRectangle(corner_radius=0.03, width=0.62, height=0.13, fill_color=c, fill_opacity=0.9, stroke_width=0)
                        for c in (P.GOLD, P.BLUE, P.GREEN)]).arrange(DOWN, buff=0.07)
        m_phone = msgs.copy().move_to(phone)
        m_lap = msgs.copy().scale(1.2).move_to(lap.screen)
        with self.say("Read it on the phone, and it's marked as read on the laptop too. Folders, flags and "
                      "deletions all stay in sync, because they live on the server."):
            self.play(FadeIn(m_phone), FadeIn(m_lap), pulse(w1, P.GOLD), pulse(w2, P.GOLD))
            self.play(m_phone[0].animate.set_opacity(0.3), run_time=0.5)
            self.play(pulse(w1, P.GOLD), pulse(w2, P.GOLD), m_lap[0].animate.set_opacity(0.3), run_time=0.8)
        pop = txt("POP3: download, then delete from the server", size=26, color=P.MUTED).move_to(DOWN * 1.9)
        with self.say("The older POP3 works like a real post box: the app downloads the mail and "
                      "usually deletes it from the server. Fine for one computer, awkward for three."):
            self.play(Write(pop))
        with self.say("IMAP for me. I have many devices. Gnome devices.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(FadeOut(VGroup(box, phone, pl, lap, w1, w2, m_phone, m_lap, pop)), g.change("fierce"))


class Outro(StoryScene):
    def construct(self):
        self.chapter("The whole trip", label="Recap")
        g = self.add_gnome("fierce", animate=False)
        nodes, wires, protos = pipeline()
        with self.say("So, the whole trip. Your app sends with SMTP. Your server asks DNS for the MX "
                      "record, and talks SMTP to the receiving server."):
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nodes], lag_ratio=0.15), Create(wires))
            self.play(Write(protos[0]), Write(protos[1]))
        with self.say("That server checks SPF, DKIM and DMARC, and files it in a mailbox, where IMAP "
                      "keeps every device in sync."):
            self.play(Write(protos[2]))
            dot, tr, anim = trail_dot([nodes[0].get_center() + UP * 0.9, nodes[1].get_center() + UP * 1.2,
                                       nodes[2].get_center() + UP * 1.2, nodes[3].get_center() + UP * 0.9], P.YELLOW, run_time=2.4)
            self.add(tr, dot)
            self.play(anim)
            self.play(Flash(dot, color=P.YELLOW, line_length=0.3))
            self.remove(dot, tr)
        with self.say("All of it plain text over TCP, with a bit of encryption on top. Next time: S S H.", who="gnome"):
            self.play(g.change("happy"))
        self.play(FadeOut(VGroup(*nodes, wires, protos)), FadeOut(self._title))
        self.unpin(self._title)
        self._title = None
        theme_outro(self, "Tschüss!")
