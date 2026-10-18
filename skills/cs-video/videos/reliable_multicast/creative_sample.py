"""Creative style test: ACK implosion with zoom-out, ACK swarm and overload gauge."""
from manim import *

from csvideo import CSScene, NetTree, make_text
from csvideo import theme as T
from csvideo.effects import CountUp, Gauge, Swarm, glow, scatter_ring, shake

SCENES = ["AckFlood"]

PARENTS = {"R1": "S", "R2": "S", "A": "R1", "B": "R1", "C": "R1", "D": "R2", "E": "R2", "F": "R2"}
KINDS = {"S": "sender", "R1": "router", "R2": "router"}
HOSTS = ["A", "B", "C", "D", "E", "F"]
CENTER = np.array([-0.7, 0.1, 0])


class AckFlood(CSScene):
    def construct(self):
        self.show_title("Problem 1: ACK implosion")
        tree = NetTree(PARENTS, kinds=KINDS, width=7.5, level_gap=1.35).move_to(LEFT * 0.7 + UP * 0.35)
        gauge = Gauge("sender load").move_to(RIGHT * 5.3 + UP * 1.0)
        self.play(FadeIn(tree), FadeIn(gauge))

        # 1. small group: harmless
        with self.say("Every receiver ACKs every packet. With six receivers, the sender barely notices."):
            acks, anim = tree.gather(HOSTS, "S", "ACK", T.GREEN, run_time=2.0)
            self.play(anim, gauge.to(0.06, run_time=2.0))
            self.play(FadeOut(acks), run_time=0.3)

        # 2. zoom out to a huge group
        sender = tree["S"]
        host_dots = VGroup(*[Dot(tree[h].get_center(), radius=0.09, color=T.MUTED) for h in HOSTS])
        ring6 = [CENTER + 1.0 * np.array([np.cos(a), np.sin(a) * 0.7, 0])
                 for a in np.linspace(0, TAU, 7)[:-1]]
        field_pts = scatter_ring(CENTER, rx=3.8, ry=2.25, n=650, inner=0.18, seed=4)
        field = VGroup(*[Dot(p, radius=0.035, color=T.MUTED) for p in field_pts])
        field.skip_layout_check = True
        count = CountUp("receivers", 6, size=T.BODY_SIZE - 4)
        count.move_to([3.6, -0.7, 0], aligned_edge=LEFT)
        with self.say("But a multicast group can be huge. Let's zoom out."):
            self.play(FadeOut(VGroup(*[tree[n] for n in ("R1", "R2")]), tree.link_group),
                      *[ReplacementTransform(tree[h], d) for h, d in zip(HOSTS, host_dots)],
                      sender.animate.move_to(CENTER), FadeIn(count), run_time=1.0)
            self.play(*[d.animate.move_to(p) for d, p in zip(host_dots, ring6)], run_time=0.8)
            field.scale(3.0, about_point=CENTER).set_opacity(0)
            self.add(field)
            self.play(host_dots.animate.scale(0.25, about_point=CENTER).set_opacity(0),
                      field.animate.scale(1 / 3.0, about_point=CENTER).set_opacity(0.8),
                      count.to(10_000, run_time=2.4, log=True),
                      run_time=2.4, rate_func=smooth)
            self.remove(host_dots)
        self.bring_to_front(sender)

        # 3. the flood
        swarm = Swarm(field_pts, CENTER, color=T.GREEN, n=420, speed=0.5, streak=0.28, width=3).start()
        halo = glow(sender, T.RED, layers=8, spread=0.9)
        self.add(swarm)
        self.bring_to_front(sender)
        with self.say("Ten thousand receivers, each acknowledging a thousand packets a second, "
                      "all aimed at one machine."):
            self.play(swarm.set_intensity(1.0, run_time=3.0), gauge.to(0.92, run_time=3.5),
                      FadeIn(halo), rate_func=linear, run_time=3.5)

        rate = CountUp("ACKs/s", 0, size=T.BODY_SIZE - 4, color=T.ORANGE)
        rate.move_to([3.6, -1.4, 0], aligned_edge=LEFT)
        bits = make_text("≈ 5 Gbit/s", size=T.BODY_SIZE, color=T.RED, weight="BOLD")
        bits.next_to(rate, DOWN, buff=0.25).align_to(rate, LEFT)
        with self.say("That's ten million ACKs a second. Five gigabits of nothing but acknowledgements."):
            self.play(FadeIn(rate), run_time=0.3)
            self.play(rate.to(10_000_000, run_time=2.2, log=True), gauge.to(1.08, run_time=2.2))
            self.play(FadeIn(bits, scale=1.4), run_time=0.5)

        rings = VGroup(*[Circle(radius=0.4, stroke_color=T.RED, stroke_width=6).move_to(CENTER)
                         for _ in range(3)])
        rings.skip_layout_check = True
        with self.say("The sender drowns."):
            self.play(gauge.to(1.25, run_time=0.6, rate_func=rush_into),
                      sender.shape.animate.set_stroke(T.RED, 8).set_fill(T.RED, 0.35),
                      halo.animate.scale(1.5), run_time=0.6)
            self.play(shake(sender, amplitude=0.1, times=10, run_time=0.9),
                      LaggedStart(*[r.animate(run_time=1.2).scale(7).set_stroke(opacity=0)
                                    for r in rings], lag_ratio=0.25))
        self.play(swarm.set_intensity(0, run_time=1.0))
        swarm.stop()
        self.wait(0.3)
