"""Distance vector routing at node B (engaging version). Storyboard: storyboard.md."""
import os

os.environ.setdefault("CSVIDEO_SPEED", "1.05")

from manim import *  # noqa: E402

from csvideo import (Bubble, Card, Chip, CSScene, GridView, NetGraph, Packet,  # noqa: E402
                     make_text)
from csvideo import theme as T  # noqa: E402
from csvideo.effects import Countdown, RaceBars, glow, scatter_ring, shake  # noqa: E402

SCENES = ["Hook", "Gossip", "FirstRace", "Rule", "Races", "Payoff", "Teaser"]

NBR = ["A", "C", "E"]
LINK = {"A": 4, "C": 2, "E": 6}
DV = {"A": [0, 4, 6, 20, 13, 5], "C": [5, 2, 0, 3, 10, 1], "E": [13, 6, 10, 7, 0, 8]}
DEST = ["A", "B", "C", "D", "E", "F"]
COL = {"A": T.CYAN, "C": T.LIME, "E": T.ORANGE, "D": T.PURPLE, "F": T.PINK, "B": T.BLUE}
POS = {"B": (-0.4, 0.55), "A": (-4.3, 1.5), "E": (3.6, 1.5), "C": (-0.4, -1.65),
       "D": (-4.3, -1.65), "F": (3.6, -1.65)}


def graph():
    edges = {("B", "A"): 4, ("B", "C"): 2, ("B", "E"): 6, ("C", "D"): None, ("C", "F"): None}
    g = NetGraph(POS, edges, kinds={"B": "sender"}, colors=COL,
                 dashed={("C", "D"), ("C", "F")}, scale=1.25)
    for d in ("D", "F"):
        g.edge("C", d).set_stroke(color=COL[d], width=3)
    return g


def race_for(dest, origin=(-4.2, 1.2, 0), unit=0.36, row_gap=1.0, bar_h=0.55):
    c = DEST.index(dest)
    rows = [(f"via {n}", COL[n], [(LINK[n], COL[n]), (DV[n][c], COL[n])]) for n in NBR]
    return RaceBars(rows, origin=origin, unit=unit, row_gap=row_gap, bar_h=bar_h)


class Hook(CSScene):
    def construct(self):
        b = graph()["B"].move_to(ORIGIN + UP * 0.3)
        fog_pts = scatter_ring(b.get_center(), rx=6.0, ry=2.6, n=260, inner=0.3, seed=7)
        fog = VGroup(*[Dot(p, radius=0.03, color=T.MUTED).set_opacity(0.35) for p in fog_pts])
        fog.skip_layout_check = True
        pkt = Packet("to F", T.PINK).next_to(b, RIGHT, buff=0.25)
        q = make_text("?", size=60, color=T.PINK, weight="BOLD").next_to(pkt, UP, buff=0.15)
        with self.say("Node B wants to send a packet to F. But B has never seen F, "
                      "and it can't see the network."):
            self.play(FadeIn(fog, lag_ratio=0.002), FadeIn(b, scale=1.4), run_time=1.2)
            self.play(FadeIn(pkt, shift=RIGHT * 0.2), FadeIn(q, scale=1.5))
            self.play(Wiggle(VGroup(pkt, q)), run_time=1.0)

        teaser = make_text("cheapest route: 3, via C", size=T.HEADING_SIZE, color=T.GREEN,
                           weight="BOLD").move_to(DOWN * 1.4)
        with self.say("Yet in about a minute, B will know the cheapest route: three, through C. "
                      "Let's see how it figures that out."):
            self.play(FadeIn(teaser, scale=1.3), Flash(b, color=T.GREEN, line_length=0.4))
            self.play(Indicate(teaser, color=T.GREEN, scale_factor=1.06))
        self.play(FadeOut(VGroup(fog, b, pkt, q, teaser)), run_time=0.6)


class Gossip(CSScene):
    def construct(self):
        self.show_title("Distance vector routing")
        g = graph()
        for n in ("D", "F"):
            g[n].set_opacity(0.25)
        known = VGroup(g["B"], *[VGroup(g.edge("B", n), g.cost("B", n), g[n]) for n in NBR])
        with self.say("B only knows its own links: four to A, two to C, and six to E."):
            self.play(FadeIn(g["B"], scale=1.3), run_time=0.5)
            self.play(LaggedStart(*[AnimationGroup(Create(g.edge("B", n)), FadeIn(g[n]),
                                                   FadeIn(g.cost("B", n))) for n in NBR],
                                  lag_ratio=0.35), FadeIn(g["D"]), FadeIn(g["F"]), run_time=2)

        def vec_text(n):
            v = DV[n]
            return f"A {v[0]}   B {v[1]}   C {v[2]}\nD {v[3]}   E {v[4]}   F {v[5]}"
        bubbles = {
            "A": Bubble(vec_text("A"), COL["A"], tail="up").next_to(g["A"], DOWN, buff=0.3),
            "C": Bubble(vec_text("C"), COL["C"], tail="left").next_to(g["C"], RIGHT, buff=0.35),
            "E": Bubble(vec_text("E"), COL["E"], tail="up").next_to(g["E"], DOWN, buff=0.3),
        }
        with self.say("So the neighbours gossip. Each one tells B how far it thinks it is "
                      "from every node."):
            self.play(LaggedStart(*[GrowFromPoint(bubbles[n], g[n].get_center()) for n in NBR],
                                  lag_ratio=0.4), run_time=2)

        grid = GridView([DV[n] for n in NBR], row_labels=NBR, col_labels=DEST,
                        row_colors=[COL[n] for n in NBR], cell_w=0.9, cell_h=0.7, size=30)
        grid.move_to(UP * 0.3)
        rows = [VGroup(grid.row_labels[r], *[grid.cell(r, c) for c in range(6)]) for r in range(3)]
        with self.say("B collects those claims into a table: one row per neighbour, "
                      "one column per destination."):
            self.play(FadeOut(g), run_time=0.5)
            self.play(FadeIn(grid.col_labels),
                      *[ReplacementTransform(bubbles[n], rows[r]) for r, n in enumerate(NBR)],
                      run_time=1.4)


class FirstRace(CSScene):
    def construct(self):
        self.show_title("How far is D?")
        race = race_for("D")
        legend = VGroup(
            VGroup(Rectangle(width=0.5, height=0.3, fill_color=T.FG, fill_opacity=0.95,
                             stroke_width=0),
                   make_text("cost of B's link", size=T.SMALL_SIZE, color=T.MUTED)).arrange(RIGHT, buff=0.2),
            VGroup(Rectangle(width=0.5, height=0.3, fill_color=T.FG, fill_opacity=0.45,
                             stroke_width=0),
                   make_text("neighbour's claim", size=T.SMALL_SIZE, color=T.MUTED)).arrange(RIGHT, buff=0.2),
        ).arrange(RIGHT, buff=0.8).move_to(DOWN * 1.9)
        with self.say("B isn't connected to D at all. But it can reach D through A, C or E."):
            self.play(FadeIn(race.labels, shift=RIGHT * 0.2), Create(race.start_line))
            self.add(race)
        with self.say("Each route costs B's link to that neighbour, plus whatever the neighbour "
                      "claims. Let's race them."):
            self.play(FadeIn(legend))
            self.play(race.to(LINK["C"] + 0.01, run_time=0.8))
        with self.say("Through C: two plus three. It finishes first, at five."):
            self.play(race.to(race.best_total(), run_time=1.0))
            self.play(race.crown())
        with self.say("Through E costs thirteen, and through A a whole twenty-four."):
            self.play(race.to(race.max_total(), run_time=2.0))


class Rule(CSScene):
    def construct(self):
        self.show_title("That race is Bellman–Ford")
        eq = MathTex(r"D_B(y)", r"=", r"\min_{v}", r"\{", r"c(B,v)", r"+", r"D_v(y)", r"\}",
                     font_size=64)
        eq[4].set_color(T.CYAN)
        eq[6].set_color(T.ORANGE)
        eq.move_to(UP * 1.6)
        b1 = Brace(eq[4], DOWN, color=T.CYAN)
        t1 = make_text("B's link", size=T.SMALL_SIZE + 4, color=T.CYAN).next_to(b1, DOWN, buff=0.1)
        b2 = Brace(eq[6], DOWN, color=T.ORANGE)
        t2 = make_text("neighbour's claim", size=T.SMALL_SIZE + 4, color=T.ORANGE)
        t2.next_to(b2, DOWN, buff=0.1)
        with self.say("What you just watched has a name: the Bellman-Ford equation."):
            self.play(Write(eq), run_time=1.6)
        with self.say("Link cost plus claim, for every neighbour. The shortest one wins."):
            self.play(GrowFromCenter(b1), FadeIn(t1), run_time=0.7)
            self.play(GrowFromCenter(b2), FadeIn(t2), run_time=0.7)
            self.play(Circumscribe(eq[2], color=T.GREEN, run_time=1.0))

        mist = VGroup(
            Card("Trap 1: forgetting the link", "C says D is 3 away,\nbut reaching C costs 2.\n"
                 "The real total is 5.", color=T.RED, width=5.4, size=T.SMALL_SIZE, min_height=1.9),
            Card("Trap 2: wrong next hop", "To reach D, B hands the\npacket to C. The next hop\n"
                 "is always a neighbour.", color=T.RED, width=5.4, size=T.SMALL_SIZE, min_height=1.9),
        ).arrange(RIGHT, buff=0.5).move_to(DOWN * 1.35)
        with self.say("Two traps to avoid: forgetting the link cost, and writing D itself as "
                      "the next hop."):
            self.play(FadeOut(VGroup(b1, t1, b2, t2)), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mist], lag_ratio=0.5))


class Races(CSScene):
    def construct(self):
        self.show_title("B's routing table, one race at a time")
        table = GridView([["", ""] if d != "B" else ["–", "–"] for d in DEST],
                         row_labels=DEST, col_labels=["cost", "next hop"],
                         row_colors=[COL[d] for d in DEST], cell_w=1.3, cell_h=0.6, size=26)
        table.move_to([4.6, 0.2, 0])
        self.play(FadeIn(table))
        origin = (-4.3, 1.4, 0)

        def fill(dest, src_point=None):
            c = DEST.index(dest)
            col = [LINK[n] + DV[n][c] for n in NBR]
            k = col.index(min(col))
            cost_t = table.target_text(c, 0, min(col), color=T.GREEN)
            hop_t = table.target_text(c, 1, NBR[k], color=COL[NBR[k]])
            if src_point is not None:
                fly = make_text(str(min(col)), size=T.BODY_SIZE, color=T.GREEN,
                                weight="BOLD").move_to(src_point)
                self.add(fly)
                self.play(Transform(fly, cost_t), FadeIn(hop_t, scale=1.4), run_time=0.8)
                self.remove(fly)
            else:
                self.play(FadeIn(cost_t, scale=1.4), FadeIn(hop_t, scale=1.4), run_time=0.6)
            table.put(c, 0, cost_t)
            table.put(c, 1, hop_t)

        def run_race(dest, line_start, line_end, fast=True):
            tag = Chip(f"to {dest}", COL[dest], size=T.BODY_SIZE - 4, filled=True)
            tag.move_to([-4.3 + 1.6, 2.3, 0])
            race = race_for(dest, origin=origin, unit=0.2, row_gap=0.85, bar_h=0.48)
            with self.say(line_start):
                self.play(FadeIn(tag), FadeIn(race.labels), Create(race.start_line), run_time=0.5)
                self.add(race)
                self.play(race.to(race.best_total(), speed=7))
                self.play(race.crown(), run_time=0.5)
            i = race.best_index()
            end = [origin[0] + race.best_total() * race.unit + 0.5, race.ys[i], 0]
            with self.say(line_end):
                self.play(race.to(race.max_total(), speed=14))
                fill(dest, end)
            self.play(FadeOut(VGroup(race, tag, race.winner_box)), run_time=0.4)

        with self.say("Now the rest of the table. D we already know: five, through C."):
            self.play(table.highlight_cell(3, 0), run_time=0.4)
            fill("D")
            self.play(table.boxes[3][0].animate.set_stroke(T.MUTED, 1.5), run_time=0.3)
        run_race("A", "To A, the direct link wins easily.", "Four, next hop A.")
        run_race("C", "To C, direct again.", "Just two, next hop C.")
        run_race("E", "To E, the direct link costs six.",
                 "Going through C would cost twelve, so it's six, next hop E.")

        # --- your turn: F
        tag = Chip("to F", COL["F"], size=T.BODY_SIZE - 4, filled=True)
        tag.move_to([-4.3 + 1.6, 2.3, 0])
        race = race_for("F", origin=origin, unit=0.2, row_gap=0.85, bar_h=0.48)
        sums = VGroup(*[make_text(f"{LINK[n]} + {DV[n][5]}", size=T.BODY_SIZE - 2, color=COL[n],
                                  weight="BOLD").move_to([origin[0] + 1.2, y, 0])
                        for n, y in zip(NBR, race.ys)])
        cd = Countdown(3).move_to([0.9, -1.6, 0])
        with self.say("Your turn. To reach F, which neighbour wins? Pause and work it out."):
            self.play(FadeIn(tag), FadeIn(race.labels), Create(race.start_line), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in sums], lag_ratio=0.3))
            self.play(FadeIn(cd, scale=1.3), run_time=0.4)
        self.play(cd.run())
        self.play(FadeOut(cd), FadeOut(sums), run_time=0.4)
        self.add(race)
        with self.say("Through C: two plus one, three. Did you get it?"):
            self.play(race.to(race.best_total(), speed=7))
            self.play(race.crown(), run_time=0.5)
        end = [origin[0] + race.best_total() * race.unit + 0.5, race.ys[1], 0]
        with self.say("Three, with C as the next hop again."):
            self.play(race.to(race.max_total(), speed=14))
            fill("F", end)
        self.play(FadeOut(VGroup(race, tag, race.winner_box)), run_time=0.4)

        halo = glow(table, T.GREEN, layers=8, spread=0.5).set_z_index(-1)
        with self.say("And that's B's complete routing table."):
            self.play(table.animate.move_to([0.6, 0.2, 0]), run_time=0.8)
            halo.move_to(table)
            self.play(FadeIn(halo), Circumscribe(table, color=T.GREEN, run_time=1.2))


class Payoff(CSScene):
    def construct(self):
        self.show_title("What B learned")
        g = graph()
        for n in g.nodes.values():
            n.set_z_index(5)
        hidden = [g["D"], g["F"], g.edge("C", "D"), g.edge("C", "F")]
        base = VGroup(*[m for m in g if m not in hidden])
        self.play(FadeIn(base))
        with self.say("Back on the map: D and F turn out to sit behind C."):
            self.play(FadeIn(g["D"], scale=1.4), FadeIn(g["F"], scale=1.4),
                      Create(g.edge("C", "D")), Create(g.edge("C", "F")), run_time=1.2)

        routes = {"A": ["B", "A"], "C": ["B", "C"], "D": ["B", "C", "D"],
                  "E": ["B", "E"], "F": ["B", "C", "F"]}
        with self.say("So traffic for C, D and F all leaves through C. It's cheap to reach, "
                      "and close to everything else."):
            self.play(g.highlight_edge("B", "C", T.LIME, 8), run_time=0.4)
            pk = [(Packet(d, COL[d]).set_z_index(3), d) for _ in range(3) for d in ("C", "D", "F")]
            self.play(LaggedStart(*[p.travel([g[x].get_center() for x in routes[d]],
                                             run_time=1.5, rate_func=linear) for p, d in pk],
                                  lag_ratio=0.15))
            self.remove(*[p for p, _ in pk])
        with self.say("A and E get the direct links. And B worked all of this out from gossip "
                      "alone, without ever seeing the map."):
            self.play(g.highlight_edge("B", "A", T.CYAN, 8), g.highlight_edge("B", "E", T.ORANGE, 8),
                      run_time=0.5)
            pk = [(Packet(d, COL[d]).set_z_index(3), d) for _ in range(2) for d in ("A", "E")]
            self.play(LaggedStart(*[p.travel([g[x].get_center() for x in routes[d]],
                                             run_time=1.2, rate_func=linear) for p, d in pk],
                                  lag_ratio=0.2))
            self.remove(*[p for p, _ in pk])
            self.play(*[Flash(g[n], color=COL[n], line_length=0.3) for n in ("A", "C", "D", "E", "F")],
                      run_time=0.8)


class Teaser(CSScene):
    def construct(self):
        self.show_title("Coming next: a nasty surprise")
        b = graph()["B"].move_to(LEFT * 2.6 + UP * 0.6)
        c = graph()["C"].move_to(RIGHT * 2.6 + UP * 0.6)
        d = graph()["D"].move_to(RIGHT * 5.4 + UP * 0.6)
        link_bc = Line(b.get_right(), c.get_left(), stroke_color=T.LIME, stroke_width=4)
        link_cd = Line(c.get_right(), d.get_left(), stroke_color=T.PURPLE, stroke_width=4)
        for m in (b, c, d):
            m.set_z_index(5)
        self.play(FadeIn(VGroup(link_bc, link_cd, b, c, d)))
        cross = VGroup(Line(UL * 0.3, DR * 0.3), Line(UR * 0.3, DL * 0.3)).set_stroke(T.RED, 8)
        cross.move_to(link_cd)
        with self.say("But what if the link from C to D breaks?"):
            self.play(link_cd.animate.set_stroke(T.RED, 4, opacity=0.4), FadeIn(cross, scale=2),
                      shake(d, amplitude=0.08, times=6, run_time=0.6))

        guess_b = make_text("B: D is 5", size=T.BODY_SIZE, color=T.FG, weight="BOLD")
        guess_c = make_text("C: D is ∞", size=T.BODY_SIZE, color=T.RED, weight="BOLD")
        guess_b.next_to(b, DOWN, buff=0.6)
        guess_c.next_to(c, DOWN, buff=0.6)
        with self.say("C asks around, and B says it can reach D for five. "
                      "B doesn't mention that its route goes through C."):
            self.play(FadeIn(guess_b), FadeIn(guess_c))
            p = Packet("D: 5", T.BLUE)
            self.play(p.travel([b.get_center(), c.get_center()], run_time=1.0))
            self.remove(p)
        values = [7, 9, 11, 13, 15]
        with self.say("So C believes seven. Then B believes nine. Then eleven, thirteen, "
                      "creeping up two at a time."):
            for i, v in enumerate(values):
                who, other = (c, b) if i % 2 == 0 else (b, c)
                tgt = guess_c if i % 2 == 0 else guess_b
                name = "C" if i % 2 == 0 else "B"
                p = Packet(f"D: {v - 2}", T.ORANGE)
                new = make_text(f"{name}: D is {v}", size=T.BODY_SIZE, color=T.ORANGE,
                                weight="BOLD").move_to(tgt)
                self.play(p.travel([other.get_center(), who.get_center()], run_time=0.55),
                          Transform(tgt, new, run_time=0.55))
                self.remove(p)
            self.play(shake(VGroup(guess_b, guess_c), amplitude=0.06, times=6, run_time=0.6))
        with self.say("Here it stops once the route through E is cheaper. In other networks it "
                      "never stops. That's count to infinity, and it's the next video."):
            self.play(Indicate(guess_b, color=T.ORANGE, scale_factor=1.1), run_time=1.0)
        self.wait(0.6)
