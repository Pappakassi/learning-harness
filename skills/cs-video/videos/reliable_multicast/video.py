"""Why TCP-style reliability breaks for multicast. Storyboard: storyboard.md."""
from manim import *

from csvideo import (ArrayView, BulletList, Callout, Card, CSScene, NetNode, NetTree, Packet,
                     make_text)
from csvideo import theme as T

SCENES = ["TcpPair", "MulticastTree", "AckImplosion", "SlowestReceiver", "SomeoneLost", "Fixes"]

PARENTS = {"R1": "S", "R2": "S", "A": "R1", "B": "R1", "C": "R1", "D": "R2", "E": "R2", "F": "R2"}
KINDS = {"S": "sender", "R1": "router", "R2": "router"}
HOSTS = ["A", "B", "C", "D", "E", "F"]


def make_tree():
    return NetTree(PARENTS, kinds=KINDS, width=10.5, level_gap=1.5).move_to(UP * 0.35)


class TcpPair(CSScene):
    def construct(self):
        self.show_title("How TCP makes delivery reliable")
        snd = NetNode("Sender", "sender", scale=1.5).move_to(LEFT * 4.5 + UP * 1.85)
        rcv = NetNode("Receiver", "host", scale=1.5).move_to(RIGHT * 4.5 + UP * 1.85)
        wire = Line(snd.get_right(), rcv.get_left(), stroke_color=T.MUTED, stroke_width=3)
        with self.say("Let's start with TCP. One sender, one receiver."):
            self.play(FadeIn(snd), FadeIn(rcv), Create(wire), run_time=1.2)

        y = wire.get_center()[1]
        fwd = [snd.get_right()[0] + 0.5, rcv.get_left()[0] - 0.5]
        with self.say("The sender numbers every packet with a sequence number. "
                      "The receiver answers each one with an acknowledgement, an ACK."):
            seqs = [Packet(f"SEQ {i}", T.BLUE) for i in (1, 2, 3)]
            self.play(LaggedStart(*[p.travel([[fwd[0], y + 0.25, 0], [fwd[1], y + 0.25, 0]],
                                             run_time=1.6) for p in seqs], lag_ratio=0.3))
            acks = [Packet(f"ACK {i}", T.GREEN) for i in (1, 2, 3)]
            self.play(FadeOut(*seqs, run_time=0.3),
                      LaggedStart(*[p.travel([[fwd[1], y - 0.25, 0], [fwd[0], y - 0.25, 0]],
                                             run_time=1.6) for p in acks], lag_ratio=0.3))
            self.play(FadeOut(*acks), run_time=0.3)

        head = make_text("The sender keeps, for this one receiver:", size=T.BODY_SIZE,
                         color=T.MUTED).move_to(UP * 0.75)
        bullets = BulletList([
            "Sequence numbers and which ACKs have arrived",
            "A send buffer of data not yet ACKed",
            "A timeout based on the round-trip time",
            "A congestion window",
        ], size=T.BODY_SIZE - 2, spacing=0.3).next_to(head, DOWN, buff=0.3)
        bullets.align_to(head, LEFT)
        self.add(bullets)
        with self.say("To make that work, the sender keeps state about this receiver: "
                      "sequence numbers, a buffer, a timeout and a congestion window."):
            self.play(FadeIn(head), run_time=0.5)
            for i in range(4):
                self.play(bullets.reveal(i), run_time=0.5)

        with self.say("Every one of those assumes there is exactly one receiver."):
            self.play(Circumscribe(VGroup(head, bullets), color=T.YELLOW, run_time=1.5))


class MulticastTree(CSScene):
    def construct(self):
        self.show_title("Multicast: send once, routers copy")
        tree = make_tree()
        with self.say("With multicast, one sender talks to a whole group of receivers at once."):
            self.play(FadeIn(tree, lag_ratio=0.05), run_time=1.5)

        with self.say("The sender sends each packet just once. "
                      "The routers copy it onto every branch that leads to a group member."):
            pkts, anim = tree.send("S", HOSTS, "SEQ 1", T.BLUE, run_time=2.4)
            self.play(anim)
            self.play(FadeOut(pkts), *[tree[h].flash(T.GREEN, 4) for h in HOSTS], run_time=0.6)

        q = Callout("What if every receiver ACKs, like in TCP?", color=T.YELLOW)
        q.move_to(DOWN * 2.0)
        with self.say("Efficient. But what happens if we bolt TCP's acknowledgements onto it?"):
            self.play(*[tree[h].reset() for h in HOSTS], FadeIn(q, shift=UP * 0.2))


class AckImplosion(CSScene):
    def construct(self):
        self.show_title("Problem 1: ACK implosion")
        tree = make_tree()
        self.play(FadeIn(tree))
        with self.say("The sender multicasts a packet, and every receiver gets it."):
            pkts, anim = tree.send("S", HOSTS, "SEQ 1", T.BLUE, run_time=2.0)
            self.play(anim)
            self.play(FadeOut(pkts), run_time=0.3)

        with self.say("Now every receiver sends its own ACK straight back, all at the same moment."):
            acks, anim = tree.gather(HOSTS, "S", "ACK", T.GREEN, run_time=2.4)
            self.play(anim)
            self.play(tree["S"].flash(T.RED, 8),
                      tree.link("S", "R1").animate.set_stroke(T.RED, 8),
                      tree.link("S", "R2").animate.set_stroke(T.RED, 8), run_time=0.6)

        with self.say("Six ACKs pile onto one sender, for every single packet. "
                      "Now imagine ten thousand receivers."):
            self.play(Wiggle(VGroup(tree["S"], acks), scale_value=1.15), run_time=1.4)
            self.play(FadeOut(acks), run_time=0.4)

        self.clear_content()
        lines = VGroup(
            make_text("10,000 receivers  ×  1,000 packets / s", size=T.HEADING_SIZE - 2),
            make_text("=  10,000,000 ACKs every second", size=T.HEADING_SIZE - 2, color=T.ORANGE),
            make_text("×  64 bytes each  ≈  5 Gbit/s of ACK traffic", size=T.HEADING_SIZE - 2,
                      color=T.RED),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(UP * 0.6)
        with self.say("With ten thousand receivers and a thousand packets per second, "
                      "that's ten million ACKs every second."):
            self.play(FadeIn(lines[0], shift=UP * 0.2))
            self.play(FadeIn(lines[1], shift=UP * 0.2))
        with self.say("At sixty-four bytes each, that's about five gigabits per second, "
                      "all landing on one link and one CPU."):
            self.play(FadeIn(lines[2], shift=UP * 0.2))
            self.play(Indicate(lines[2], color=T.RED, scale_factor=1.05))


class SlowestReceiver(CSScene):
    def construct(self):
        self.show_title("Problem 2: waiting for the slowest")
        buf = ArrayView(range(1, 9), max_width=6.4, show_indices=False).move_to(RIGHT * 1.2 + UP * 1.7)
        buf_label = make_text("send buffer", size=T.SMALL_SIZE + 2, color=T.MUTED)
        buf_label.next_to(buf, LEFT, buff=0.4)
        rows = VGroup()
        progress = {"A": 8, "B": 7, "C": 3}
        colors = {"A": T.GREEN, "B": T.GREEN, "C": T.RED}
        for k, (name, upto) in enumerate(progress.items()):
            y = 0.6 - k * 0.75
            label = make_text(f"{name} has ACKed", size=T.SMALL_SIZE + 2, color=T.FG)
            label.move_to([buf_label.get_right()[0], y, 0], aligned_edge=RIGHT)
            left = buf.boxes[0].get_left()[0]
            right = buf.boxes[upto - 1].get_right()[0]
            bar = Rectangle(width=right - left, height=0.32, fill_color=colors[name],
                            fill_opacity=0.8, stroke_width=0)
            bar.move_to([(left + right) / 2, y, 0])
            num = make_text(f"1–{upto}", size=T.SMALL_SIZE, color=T.BG, weight="BOLD").move_to(bar)
            rows.add(VGroup(label, bar, num))

        with self.say("Second problem. The sender can only delete a packet from its buffer "
                      "once every receiver has acknowledged it."):
            self.play(FadeIn(buf), FadeIn(buf_label))
            self.play(LaggedStart(*[AnimationGroup(FadeIn(r[0]), GrowFromEdge(r[1], LEFT),
                                                   FadeIn(r[2])) for r in rows], lag_ratio=0.4),
                      run_time=2)

        with self.say("A and B are nearly done, but C is stuck at packet three. "
                      "So packets four to eight have to stay in memory, for everyone."):
            self.play(*[buf.mark(i, T.GREEN) for i in range(3)], run_time=0.8)
            self.play(*[buf.highlight(i, T.RED) for i in range(3, 8)], run_time=0.8)
            self.play(Indicate(rows[2], color=T.RED, scale_factor=1.05))

        with self.say("Memory grows with the number of receivers, "
                      "and one stalled host holds everyone back."):
            self.wait(0.5)

        self.clear_content()
        # --- RTT: no single timeout fits everyone
        x0, x1, ms_max = -5.5, 5.5, 600

        def x_of(ms):
            return x0 + (x1 - x0) * ms / ms_max
        axis = Line([x0, -0.4, 0], [x1, -0.4, 0], stroke_color=T.MUTED, stroke_width=3)
        ticks = VGroup()
        for ms in range(0, 601, 100):
            ticks.add(Line([x_of(ms), -0.5, 0], [x_of(ms), -0.3, 0], stroke_color=T.MUTED,
                           stroke_width=2))
            ticks.add(make_text(f"{ms}", size=T.SMALL_SIZE - 2, color=T.MUTED)
                      .move_to([x_of(ms), -0.8, 0]))
        unit = make_text("round-trip time (ms)", size=T.SMALL_SIZE, color=T.MUTED)
        unit.move_to([0, -1.3, 0])

        def marker(ms, text, color):
            dot = Dot([x_of(ms), -0.4, 0], radius=0.11, color=color)
            lab = make_text(text, size=T.SMALL_SIZE + 2, color=color, weight="BOLD")
            lab.move_to([x_of(ms), 0.35, 0])
            return VGroup(dot, lab)
        near = marker(40, "next door: 40 ms", T.BLUE)
        near[1].shift(RIGHT * 0.9)
        far = marker(500, "far away: 500 ms", T.ORANGE)
        with self.say("There's also no single timeout that works. A receiver next door might "
                      "answer in forty milliseconds. One across the world, in five hundred."):
            self.play(Create(axis), FadeIn(ticks), FadeIn(unit), run_time=1)
            self.play(FadeIn(near, shift=DOWN * 0.2))
            self.play(FadeIn(far, shift=DOWN * 0.2))

        tline = DashedLine([x_of(150), -0.6, 0], [x_of(150), 1.6, 0], color=T.RED, stroke_width=4)
        tlab = make_text("timeout", size=T.SMALL_SIZE + 2, color=T.RED, weight="BOLD")
        tlab.next_to(tline, UP, buff=0.1)
        tgroup = VGroup(tline, tlab)
        with self.say("Make the timeout short, and the distant receiver gets data resent "
                      "that it was about to acknowledge."):
            self.play(Create(tline), FadeIn(tlab))
            self.play(Indicate(far, color=T.RED, scale_factor=1.1))
        with self.say("Make it long, and nearby receivers wait far too long to recover a lost packet."):
            self.play(tgroup.animate.shift(RIGHT * (x_of(590) - x_of(150))), run_time=1.2)
            self.play(Indicate(near, color=T.YELLOW, scale_factor=1.1))


class SomeoneLost(CSScene):
    def construct(self):
        self.show_title("Problem 3: someone always lost it")
        axes = Axes(x_range=[0, 500, 100], y_range=[0, 1, 0.25], x_length=7.2, y_length=3.2,
                    tips=False, axis_config={"color": T.MUTED, "include_numbers": True,
                                             "font_size": 22},
                    y_axis_config={"decimal_number_config": {"num_decimal_places": 2}})
        axes.move_to(LEFT * 1.9 + UP * 0.45)
        xl = make_text("receivers  N", size=T.SMALL_SIZE, color=T.MUTED)
        xl.next_to(axes.x_axis, DOWN, buff=0.4)
        yl = make_text("chance someone lost the packet", size=T.SMALL_SIZE, color=T.MUTED)
        yl.next_to(axes.y_axis, UP, buff=0.2).align_to(axes, LEFT)
        formula = MathTex(r"P = 1 - (1-p)^N", font_size=46, color=T.FG)
        p_note = make_text("p = 1% loss per receiver", size=T.SMALL_SIZE, color=T.MUTED)
        side = VGroup(formula, p_note).arrange(DOWN, buff=0.25).move_to(RIGHT * 4.4 + UP * 1.2)
        with self.say("Now add packet loss. If each receiver loses one percent of packets, "
                      "the chance that someone lost a given packet grows with N."):
            self.play(Create(axes), FadeIn(xl), FadeIn(yl), run_time=1.2)
            self.play(Write(formula), FadeIn(p_note))

        curve = axes.plot(lambda n: 1 - 0.99 ** n, x_range=[0, 500], color=T.ORANGE,
                          stroke_width=5)
        pt = axes.c2p(100, 1 - 0.99 ** 100)
        dot = Dot(pt, radius=0.1, color=T.YELLOW)
        guide = DashedLine(axes.c2p(100, 0), pt, color=T.YELLOW, stroke_width=2)
        lab = make_text("N = 100 → 63%", size=T.BODY_SIZE - 2, color=T.YELLOW, weight="BOLD")
        lab.next_to(dot, RIGHT, buff=0.2).shift(DOWN * 0.35)
        big = make_text("N = 1,000 → almost 100%", size=T.BODY_SIZE - 2, color=T.RED,
                        weight="BOLD").next_to(side, DOWN, buff=0.7)
        with self.say("With a hundred receivers, it's already sixty-three percent. "
                      "With a thousand, practically every packet."):
            self.play(Create(curve), run_time=1.6)
            self.play(Create(guide), FadeIn(dot), FadeIn(lab))
            self.play(FadeIn(big, shift=UP * 0.2))

        self.clear_content()
        all_card = Card("Resend to everyone", "Receivers who already had it\nget duplicates, and\nbandwidth is wasted.",
                        color=T.ORANGE, width=5.6, min_height=2.0)
        each_card = Card("Resend to each one", "That's unicast again:\nthe point of multicast\nis gone.",
                         color=T.ORANGE, width=5.6, min_height=2.0)
        cards = VGroup(all_card, each_card).arrange(RIGHT, buff=0.6).move_to(UP * 1.2)
        with self.say("So nearly every packet needs resending to somebody. "
                      "Resend to the whole group, and everyone else gets duplicates."):
            self.play(FadeIn(all_card, shift=UP * 0.2))
        with self.say("Resend to each receiver separately, and you're back to unicast."):
            self.play(FadeIn(each_card, shift=UP * 0.2))

        cc = Callout("Congestion control: the whole group runs at the worst receiver's speed",
                     color=T.RED, size=T.BODY_SIZE - 2)
        cc.next_to(cards, DOWN, buff=0.6)
        with self.say("And since TCP treats a missing ACK as congestion, the sender keeps "
                      "slowing down, to the speed of the worst link in the group."):
            self.play(FadeIn(cc, shift=UP * 0.2))


class Fixes(CSScene):
    def construct(self):
        self.show_title("How real protocols cope")
        member = Callout("Routers manage membership: the sender doesn't know who is listening",
                         color=T.PURPLE, size=T.BODY_SIZE - 2).move_to(UP * 0.3)
        with self.say("One last catch: routers manage group membership, not the sender. "
                      "It doesn't even know whose ACKs to wait for."):
            self.play(FadeIn(member, shift=UP * 0.2))
        self.play(FadeOut(member), run_time=0.5)

        cards = VGroup(
            Card("NACKs + suppression", "Receivers speak only when\nsomething is missing, and\n"
                 "stay quiet if someone\nalready asked.", color=T.BLUE, width=4.3,
                 size=T.SMALL_SIZE - 2, min_height=2.3),
            Card("Local repair", "Helpers in the tree\ncombine ACKs and resend\n"
                 "lost data from nearby.", color=T.GREEN, width=4.3,
                 size=T.SMALL_SIZE - 2, min_height=2.3),
            Card("Error correction (FEC)", "Send extra repair data,\nso receivers rebuild\n"
                 "losses without asking.", color=T.PURPLE, width=4.3,
                 size=T.SMALL_SIZE - 2, min_height=2.3),
        ).arrange(RIGHT, buff=0.3, aligned_edge=UP).move_to(UP * 0.9)
        lines = [
            "Real protocols flip the idea around. With negative ACKs, receivers only speak "
            "up when something is missing.",
            "Some arrange helpers in a tree, which combine ACKs and repair losses locally.",
            "Others send extra repair data up front, so receivers can rebuild what they lost.",
        ]
        for card, text in zip(cards, lines):
            with self.say(text):
                self.play(FadeIn(card, shift=UP * 0.2), run_time=0.8)

        app = Callout("Or skip it: RTP over UDP leaves loss to the application",
                      color=T.YELLOW, size=T.BODY_SIZE - 2).next_to(cards, DOWN, buff=0.5)
        with self.say("Or, like RTP for live audio and video, they leave loss to the application."):
            self.play(FadeIn(app, shift=UP * 0.2))
        with self.say("The lesson: TCP's per-receiver bookkeeping simply doesn't scale to a crowd."):
            self.play(Indicate(app, color=T.YELLOW, scale_factor=1.05), run_time=1.5)
        self.wait(0.8)
