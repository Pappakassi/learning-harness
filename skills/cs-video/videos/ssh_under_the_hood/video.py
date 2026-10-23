"""How SSH works under the hood, with Hr. Schiffel. Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.0")

from manim import *  # noqa: E402

from csvideo.effects import Countdown  # noqa: E402
from csvideo.story import P, StoryScene, theme_intro, theme_outro, txt  # noqa: E402
from csvideo.story_kit import Key, Laptop, Padlock, Server, Terminal, pulse, trail_dot  # noqa: E402

SCENES = ["Intro", "Hook", "Layers", "KeyExchange", "HostKey", "UserAuth", "Channels", "Tunnel", "Outro"]

L_X, R_X = -4.6, 4.6


def ends(label_r="server.ru.is"):
    you = Laptop("your laptop", P.TEAL, scale=0.8).move_to([L_X, 0.6, 0])
    srv = Server(label_r, P.PINK, scale=0.85).move_to([R_X, 0.6, 0])
    wire = Line(you.get_right() + RIGHT * 0.15, srv.get_left() + LEFT * 0.15, stroke_color=P.MUTED, stroke_width=3)
    return you, srv, wire


def paint(color, label="", r=0.38):
    c = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_color=P.FG, stroke_width=2)
    g = VGroup(c)
    if label:
        g.add(txt(label, size=20, color=P.MUTED).next_to(c, DOWN, buff=0.12))
    return g


class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "How SSH works", "a safe shell on someone else's computer")
        self.wait(0.3)


class Hook(StoryScene):
    def construct(self):
        g = self.add_gnome("fierce", animate=False)
        you, srv, wire = ends()
        term = Terminal(width=6.4, lines=3, font_size=22).move_to([-1.8, -1.35, 0])
        with self.say("You type one line, ssh, your name, at a server. A moment later you're working on a "
                      "computer in another building, or another country."):
            self.play(FadeIn(you), FadeIn(srv), Create(wire))
            self.play(FadeIn(term))
            self.play(term.type("$ ssh hinni@server.ru.is"))
            self.play(pulse(wire, P.TEAL))
            self.play(term.type("hinni@server:~$ ", "S"))
        ghosts = VGroup(*[txt(s, size=22, color=P.RED, font="DejaVu Sans Mono") for s in ("café WiFi", "ISP router", "backbone")])
        for i, gh in enumerate(ghosts):
            gh.move_to(wire.point_from_proportion(0.25 + i * 0.25) + UP * (0.45 if i % 2 == 0 else -0.45))
        with self.say("And yet every keystroke, including your password, crosses networks run by strangers."):
            self.play(LaggedStart(*[FadeIn(gh, shift=DOWN * 0.15) for gh in ghosts], lag_ratio=0.25))
        with self.say("Strangers! Like Mallory. Reading everything.", who="gnome"):
            self.play(g.change("angry"))
        with self.say("SSH has to solve three problems at once: keep it secret, prove the server is "
                      "real, and prove that you are you. Let's see how."):
            self.play(g.change("fierce"))
            self.play(FadeOut(VGroup(ghosts, term, you, srv, wire)))


class Layers(StoryScene):
    def construct(self):
        self.chapter("1. Where SSH lives", label="1  Layers")
        g = self.add_gnome("fierce")
        rows = [("your shell, files, tunnels", P.GOLD), ("SSH: encryption, keys, login", P.PINK),
                ("TCP, port 22", P.BLUE), ("IP", P.TEAL)]
        stack = VGroup()
        for i, (t, c) in enumerate(rows):
            box = RoundedRectangle(corner_radius=0.1, width=6.0, height=0.75, fill_color=c, fill_opacity=0.18,
                                   stroke_color=c, stroke_width=3)
            stack.add(VGroup(box, txt(t, size=26, color=c, weight="BOLD").move_to(box)))
        stack.arrange(DOWN, buff=0.12).move_to([-0.8, 0.3, 0])
        with self.say("SSH sits on top of an ordinary TCP connection, normally on port twenty-two. TCP "
                      "makes sure the bytes arrive in order."):
            self.play(FadeIn(stack[3], shift=UP * 0.2))
            self.play(FadeIn(stack[2], shift=UP * 0.2))
        with self.say("SSH adds everything else: the encryption, the keys, the login. And on top of it "
                      "run the things you actually want: a shell, file copies, tunnels."):
            self.play(FadeIn(stack[1], shift=UP * 0.2))
            self.play(Circumscribe(stack[1], color=P.PINK))
            self.play(FadeIn(stack[0], shift=UP * 0.2))
        ver = Terminal(width=7.0, lines=2, font_size=22).move_to(DOWN * 1.9)
        with self.say("The very first thing each side sends is plain text: a version line."):
            self.play(stack.animate.shift(UP * 0.4), FadeIn(ver))
            self.play(ver.type("SSH-2.0-OpenSSH_9.6", "C"))
            self.play(ver.type("SSH-2.0-OpenSSH_9.8", "S"))
        with self.say("After that, nothing readable ever crosses the wire again.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(g.change("fierce"), FadeOut(VGroup(stack, ver)))


class KeyExchange(StoryScene):
    def construct(self):
        self.chapter("2. A secret, agreed in public", label="2  Key exchange")
        g = self.add_gnome("fierce")
        xs, xa = -4.4, 4.4
        hs = txt("your laptop", size=26, color=P.TEAL, weight="BOLD").move_to([xs, 2.3, 0])
        ha = txt("server", size=26, color=P.PINK, weight="BOLD").move_to([xa, 2.3, 0])
        hm = txt("anyone listening sees", size=26, color=P.RED, weight="BOLD").move_to([0, 2.3, 0])
        pub = paint(P.YELLOW, "public").move_to([0, 1.2, 0])
        with self.say("To encrypt anything, both sides need a shared secret key. But they've never met, "
                      "and everything they send can be overheard."):
            self.play(FadeIn(hs), FadeIn(ha), FadeIn(hm))
        with self.say("The trick is Diffie-Hellman. Think of paint. Both sides agree, in public, on a "
                      "starting colour: yellow."):
            self.play(FadeIn(pub, scale=0.6))
        sa, sb = paint(P.RED, "secret").move_to([xs, 1.2, 0]), paint(P.BLUE, "secret").move_to([xa, 1.2, 0])
        with self.say("Each side secretly picks its own colour, and never sends it."):
            self.play(FadeIn(sa, scale=0.6), FadeIn(sb, scale=0.6))
        ma, mb = paint(P.ORANGE).move_to([xs, -0.2, 0]), paint(P.GREEN).move_to([xa, -0.2, 0])
        with self.say("Each mixes its secret into the yellow, and sends the mixture across. Orange one way, "
                      "green the other."):
            self.play(TransformFromCopy(VGroup(pub[0], sa[0]), ma[0]), TransformFromCopy(VGroup(pub[0], sb[0]), mb[0]), run_time=1.0)
            so, sg = ma[0].copy(), mb[0].copy()
            self.play(so.animate.move_to([-0.5, -0.2, 0]), sg.animate.move_to([0.5, -0.2, 0]), run_time=0.8)
            self.play(ma[0].animate.move_to([xa - 1.3, -0.2, 0]), mb[0].animate.move_to([xs + 1.3, -0.2, 0]), run_time=1.0)
        fa, fb = paint("#8B5A2B", "shared secret").move_to([xs, -1.6, 0]), paint("#8B5A2B", "shared secret").move_to([xa, -1.6, 0])
        with self.say("Each adds its own secret to what it received, and both end up with the same brown. "
                      "Someone listening only has yellow, orange and green. You can't un-mix paint."):
            self.play(TransformFromCopy(VGroup(mb[0], sa[0]), fa[0]), FadeIn(fa[1]),
                      TransformFromCopy(VGroup(ma[0], sb[0]), fb[0]), FadeIn(fb[1]), run_time=1.4)
            self.play(Flash(fa, color=P.GOLD, line_length=0.3), Flash(fb, color=P.GOLD, line_length=0.3))
        lock = Padlock(P.GOLD, size=0.7).move_to([0, -1.5, 0])
        with self.say("Real SSH does this with maths instead of paint, and from that shared number both "
                      "sides derive session keys. Now every packet is encrypted."):
            self.play(FadeIn(lock, scale=0.5))
        with self.say("Easy to mix, impossible to un-mix. Good maths. Gnome-approved.", who="gnome"):
            self.play(g.change("happy"))
        self.play(g.change("fierce"), FadeOut(VGroup(hs, ha, hm, pub, sa, sb, ma, mb, so, sg, fa, fb, lock)))


class HostKey(StoryScene):
    def construct(self):
        self.chapter("3. Is that really the server?", label="3  Host key")
        g = self.add_gnome("fierce")
        you, srv, wire = ends()
        mal = Server("Mallory", P.RED, scale=0.7).move_to([0, 0.6, 0])
        with self.say("Here's the catch. What if Mallory sits in the middle, and does a key exchange with "
                      "each side? You'd have a perfectly encrypted line, straight to Mallory."):
            self.play(FadeIn(you), FadeIn(srv), Create(wire))
            self.play(FadeIn(mal, scale=0.6), wire.animate.set_stroke(P.RED))
        with self.say("Ach! Gnome-in-the-middle! Worst kind.", who="gnome"):
            self.play(g.change("angry"))
        hk = Key(P.PINK, label="host key", size=0.8).next_to(srv, UP, buff=0.4)
        with self.say("So every SSH server has its own long-term key pair: the host key. During the "
                      "exchange, the server signs it with its private host key."):
            self.play(g.change("fierce"), FadeOut(mal), wire.animate.set_stroke(P.MUTED))
            self.play(FadeIn(hk, shift=DOWN * 0.2))
        term = Terminal(width=10.5, lines=4, font_size=20).move_to(DOWN * 1.6)
        with self.say("The first time you connect, your computer can't know that key yet. So it asks you."):
            self.play(FadeIn(term))
            self.play(term.type("The authenticity of host 'server.ru.is' can't be established.", "#"))
            self.play(term.type("ED25519 key fingerprint is SHA256:9xQf...k3Vw", "#"))
            self.play(term.type("Are you sure you want to continue connecting (yes/no)?", "#"))
        with self.say("Say yes, and the key is saved in a file called known hosts. From then on, it's "
                      "checked every time."):
            self.play(term.type("yes  ->  saved to ~/.ssh/known_hosts", "C"))
        self.play(term.clear_rows())
        q = txt("Next week the server shows a different host key. Why might that be?", size=26, color=P.YELLOW, weight="BOLD").move_to(DOWN * 0.9)
        with self.say("Your turn. A week later, the server presents a different host key. What could "
                      "that mean?"):
            self.play(FadeOut(term), Write(q))
            cd = Countdown(3).scale(0.7).move_to(DOWN * 1.9)
            self.play(FadeIn(cd), run_time=0.3)
        self.play(cd.run())
        warn = txt("WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!", size=26, color=P.RED, weight="BOLD", font="DejaVu Sans Mono").move_to(DOWN * 1.9)
        with self.say("Either the server was reinstalled, or someone is in the middle. SSH refuses to "
                      "connect until you find out which."):
            self.play(FadeOut(cd), Write(warn))
            self.play(Indicate(warn, color=P.RED))
        self.play(FadeOut(VGroup(q, warn, you, srv, wire, hk)))


class UserAuth(StoryScene):
    def construct(self):
        self.chapter("4. Proving who you are", label="4  Logging in")
        g = self.add_gnome("fierce")
        you, srv, wire = ends()
        self.add(you, srv, wire)
        with self.say("Now the server knows the line is secret. It still doesn't know who you are. You can "
                      "type a password, safely inside the encryption. But keys are better."):
            self.play(Indicate(you, color=P.TEAL))
        priv = Key(P.TEAL, label="private key", size=0.8).next_to(you, DOWN, buff=0.35)
        pubk = Padlock(P.TEAL, size=0.55).next_to(srv, DOWN, buff=0.3)
        publ = txt("public key", size=20, color=P.TEAL).next_to(pubk, DOWN, buff=0.1)
        with self.say("You make a key pair once. The private key never leaves your laptop. The public key "
                      "goes into a file on the server called authorized keys."):
            self.play(FadeIn(priv, shift=UP * 0.2))
            copy = Padlock(P.TEAL, size=0.55).move_to(you.get_center())
            self.play(FadeIn(copy))
            self.play(copy.animate.move_to(pubk.get_center()), run_time=1.2)
            self.add(pubk)
            self.remove(copy)
            self.play(FadeIn(publ))
        chal = txt("random challenge  +  session id", size=22, color=P.PINK, font="DejaVu Sans Mono")
        chal.next_to(wire, UP, buff=0.25)
        sig = txt("signature", size=22, color=P.TEAL, font="DejaVu Sans Mono").next_to(wire, DOWN, buff=0.25)
        with self.say("At login, your laptop signs some data unique to this session with the private key."):
            self.play(Write(chal))
            self.play(Indicate(priv, color=P.TEAL), run_time=0.8)
            self.play(FadeIn(sig, shift=RIGHT * 0.3), pulse(wire, P.TEAL))
        with self.say("The server checks the signature with your public key. If it fits, you're in. "
                      "No secret was ever sent, so there's nothing for anyone to steal or replay."):
            self.play(sig.animate.move_to(pubk.get_center() + LEFT * 1.4), run_time=0.8)
            self.play(pubk.close(), Flash(pubk, color=P.GREEN, line_length=0.3))
            ok = txt("logged in", size=26, color=P.GREEN, weight="BOLD").next_to(srv, UP, buff=0.3)
            self.play(FadeIn(ok, scale=1.3))
        with self.say("And guard that private key. Put a passphrase on it!", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(g.change("fierce"), FadeOut(VGroup(you, srv, wire, priv, pubk, publ, chal, sig, ok)))


class Channels(StoryScene):
    def construct(self):
        self.chapter("5. Many channels, one connection", label="5  Channels")
        g = self.add_gnome("fierce")
        you, srv, wire = ends()
        pipe = RoundedRectangle(corner_radius=0.35, width=wire.get_length(), height=2.3, stroke_color=P.GOLD,
                                stroke_width=3, fill_color=P.GOLD, fill_opacity=0.06).move_to(wire)
        lanes = [(0.65, "shell", P.TEAL), (0.0, "file copy (scp/sftp)", P.BLUE), (-0.65, "tunnel", P.PURPLE)]
        with self.say("Inside the one encrypted connection, SSH runs several channels side by side."):
            self.play(FadeIn(you), FadeIn(srv), FadeIn(pipe))
        labs = VGroup()
        for dy, name, c in lanes:
            labs.add(txt(f"channel {len(labs)}: {name}", size=20, color=c).move_to([pipe.get_left()[0] + 0.35, wire.get_center()[1] + dy + 0.2, 0], aligned_edge=LEFT))
        with self.say("A shell. A file copy. A tunnel. Each has a channel number, and their packets "
                      "simply take turns."):
            self.play(LaggedStart(*[FadeIn(l) for l in labs], lag_ratio=0.3))
            dots = []
            for k in range(3):
                for dy, name, c in lanes:
                    d = Dot(radius=0.08, color=c)
                    dots.append(d.copy())
            anims = []
            for i, d in enumerate(dots):
                dy = lanes[i % 3][0]
                y = wire.get_center()[1] + dy - 0.1
                anims.append(Succession(Wait(i * 0.15), MoveAlongPath(d, Line([pipe.get_left()[0] + 0.3, y, 0], [pipe.get_right()[0] - 0.3, y, 0]), run_time=1.5, rate_func=linear)))
            self.add(*dots)
            self.play(*anims)
            self.remove(*dots)
        with self.say("One handshake, one login, many conversations. Very efficient.", who="gnome"):
            self.play(g.change("happy"))
        self.play(g.change("fierce"), FadeOut(VGroup(you, srv, pipe, labs)))


class Tunnel(StoryScene):
    def construct(self):
        self.chapter("6. Tunnels", label="6  Port forwarding")
        g = self.add_gnome("fierce")
        you = Laptop("laptop", P.TEAL, scale=0.75).move_to([-5.0, 0.9, 0])
        fw = Rectangle(width=0.25, height=2.6, fill_color=P.RED, fill_opacity=0.5, stroke_width=0).move_to([-1.6, 0.9, 0])
        fwl = txt("firewall", size=20, color=P.RED).next_to(fw, DOWN, buff=0.1)
        srv = Server("server.ru.is", P.PINK, scale=0.75).move_to([1.3, 0.9, 0])
        db = Server("database :5432", P.BLUE, scale=0.65).move_to([4.6, 0.9, 0])
        lan = Line(srv.get_right() + RIGHT * 0.1, db.get_left() + LEFT * 0.1, stroke_color=P.MUTED)
        with self.say("Last trick. A database sits on the university's internal network. The firewall "
                      "blocks it from outside. Only port twenty-two, SSH, gets in."):
            self.play(FadeIn(you), FadeIn(fw), FadeIn(fwl), FadeIn(srv), FadeIn(db), Create(lan))
            bad = Dot([-4.0, 0.4, 0], radius=0.09, color=P.BLUE)
            self.play(bad.animate.move_to([-1.85, 0.4, 0]), run_time=0.7)
            self.play(Flash(bad, color=P.RED, line_length=0.25), FadeOut(bad))
        term = Terminal(width=9.0, lines=2, font_size=22).move_to(DOWN * 1.55)
        tube = RoundedRectangle(corner_radius=0.25, width=srv.get_left()[0] - you.get_right()[0] - 0.2, height=0.5,
                                stroke_color=P.GOLD, stroke_width=3, fill_color=P.GOLD, fill_opacity=0.1)
        tube.move_to([(you.get_right()[0] + srv.get_left()[0]) / 2, 0.9, 0])
        with self.say("Local port forwarding: your laptop listens on a local port, and everything sent "
                      "there travels through the SSH tunnel. The server passes it on to the database."):
            self.play(FadeIn(term))
            self.play(term.type("$ ssh -L 5432:database:5432 hinni@server.ru.is"))
            self.play(Create(tube), fw.animate.set_opacity(0.25))
            dot, tr, anim = trail_dot([you.get_center(), tube.get_left() + RIGHT * 0.2, tube.get_right() + LEFT * 0.2,
                                       srv.get_center(), db.get_center()], P.GOLD, run_time=2.4)
            self.add(tr, dot)
            self.play(anim)
            self.play(Flash(db, color=P.GOLD, line_length=0.3))
            self.remove(dot, tr)
        with self.say("Through the wall, encrypted all the way to the server. Sneaky, but allowed.", who="gnome"):
            self.play(g.change("lecturing", point="left"))
        self.play(g.change("fierce"), FadeOut(VGroup(you, fw, fwl, srv, db, lan, term, tube)))


class Outro(StoryScene):
    def construct(self):
        self.chapter("The whole handshake", label="Recap")
        g = self.add_gnome("fierce", animate=False)
        steps = ["TCP connect, port 22", "Versions (plain text)", "Key exchange: shared secret",
                 "Host key: is it the real server?", "Login: your key signs", "Channels: shell, files, tunnels"]
        cols = [P.BLUE, P.MUTED, P.GOLD, P.PINK, P.TEAL, P.PURPLE]
        chips = VGroup()
        for i, (s, c) in enumerate(zip(steps, cols)):
            box = RoundedRectangle(corner_radius=0.12, width=4.1, height=0.85, fill_color=c, fill_opacity=0.15, stroke_color=c, stroke_width=3)
            t = txt(f"{i + 1}. {s}", size=20, color=c, weight="BOLD")
            if t.width > 3.8:
                t.scale_to_fit_width(3.8)
            chips.add(VGroup(box, t.move_to(box)))
        chips.arrange_in_grid(2, 3, buff=(0.25, 0.5)).move_to(UP * 0.5)
        arrows = VGroup(*[Arrow(chips[i].get_right(), chips[i + 1].get_left(), buff=0.05, stroke_width=3, color=P.MUTED)
                          for i in (0, 1, 3, 4)])
        with self.say("So: a TCP connection, a version hello, a key exchange that creates a shared secret "
                      "in public, a host key that proves the server is real."):
            for i in range(4):
                self.play(FadeIn(chips[i], shift=UP * 0.2), run_time=0.6)
        with self.say("Then your key proves who you are, and many channels share the one encrypted line."):
            for i in range(4, 6):
                self.play(FadeIn(chips[i], shift=UP * 0.2), run_time=0.6)
            self.play(LaggedStart(*[Indicate(c) for c in chips], lag_ratio=0.15))
        with self.say("Secret, authentic, and you are you. Three problems, one protocol.", who="gnome"):
            self.play(g.change("happy"))
        self.play(FadeOut(chips), FadeOut(self._title))
        self.unpin(self._title)
        self._title = None
        theme_outro(self, "Tschüss!")
