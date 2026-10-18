"""Distance vector routing at node B. Storyboard: storyboard.md."""
from manim import *

from csvideo import Card, Chip, CSScene, GridView, NetGraph, Packet, make_text
from csvideo import theme as T
from csvideo.effects import glow

SCENES = ["Setup", "Rule", "Compute", "Result"]

NBR = ["A", "C", "E"]
LINK = {"A": 4, "C": 2, "E": 6}
DV = {"A": [0, 4, 6, 20, 13, 5], "C": [5, 2, 0, 3, 10, 1], "E": [13, 6, 10, 7, 0, 8]}
DEST = ["A", "B", "C", "D", "E", "F"]
COL = {"A": T.CYAN, "C": T.LIME, "E": T.ORANGE, "D": T.PURPLE, "F": T.PINK, "B": T.BLUE}

POS = {"B": (-0.4, 0.55), "A": (-4.3, 1.5), "E": (3.6, 1.5), "C": (-0.4, -1.65),
       "D": (-4.3, -1.65), "F": (3.6, -1.65)}


def graph(with_hidden=True):
    pos = POS if with_hidden else {k: v for k, v in POS.items() if k not in "DF"}
    edges = {("B", "A"): 4, ("B", "C"): 2, ("B", "E"): 6}
    dashed = set()
    if with_hidden:
        edges.update({("C", "D"): None, ("C", "F"): None})
        dashed = {("C", "D"), ("C", "F")}
    return NetGraph(pos, edges, kinds={"B": "sender"}, colors=COL, dashed=dashed, scale=1.25)


class Setup(CSScene):
    def construct(self):
        self.show_title("Distance vector routing at B")
        g = graph()
        hidden = VGroup(g["D"], g["F"], g.edge("C", "D"), g.edge("C", "F"))
        qs = VGroup(*[make_text("?", size=T.HEADING_SIZE, color=T.MUTED, weight="BOLD")
                      .next_to(g[n], UP, buff=0.15) for n in ("D", "F")])
        known = VGroup(g["B"], g.edge("B", "A"), g.edge("B", "C"), g.edge("B", "E"),
                       g.cost("B", "A"), g.cost("B", "C"), g.cost("B", "E"),
                       g["A"], g["C"], g["E"])
        with self.say("Node B can only see its own links: A at cost four, C at cost two, "
                      "and E at cost six."):
            self.play(FadeIn(g["B"], scale=1.3), run_time=0.6)
            self.play(LaggedStart(*[AnimationGroup(Create(g.edge("B", n)), FadeIn(g[n]),
                                                   FadeIn(g.cost("B", n)))
                                    for n in NBR], lag_ratio=0.35), run_time=2)

        for m in (g["D"], g["F"]):
            m.set_opacity(0.25)
        with self.say("D and F are out there too, but B has no idea how to reach them yet."):
            self.play(FadeIn(g["D"]), FadeIn(g["F"]), FadeIn(qs, shift=DOWN * 0.1))

        with self.say("So each neighbour sends B its distance vector: how far it thinks it is "
                      "from every node."):
            pk = [Packet(f"{n}'s vector", COL[n]) for n in NBR]
            self.play(LaggedStart(*[p.travel([g[n].get_center(), g["B"].get_center()],
                                             run_time=1.6) for p, n in zip(pk, NBR)],
                                  lag_ratio=0.3))
            self.play(*[FadeOut(p, scale=0.5) for p in pk], Indicate(g["B"], color=T.YELLOW),
                      run_time=0.6)

        self.clear_content()
        grid = GridView([DV[n] for n in NBR], row_labels=NBR, col_labels=DEST,
                        row_colors=[COL[n] for n in NBR], cell_w=0.9, cell_h=0.7, size=30)
        grid.move_to(UP * 0.3)
        note = make_text("each row: one neighbour's claimed distance to every node",
                         size=T.SMALL_SIZE + 2, color=T.MUTED).next_to(grid, DOWN, buff=0.45)
        with self.say("Here they are: one row per neighbour, one column per destination."):
            self.play(FadeIn(grid.col_labels), run_time=0.4)
            for r in range(3):
                row = VGroup(grid.row_labels[r], *[grid.cell(r, c) for c in range(6)])
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.5)
            self.play(FadeIn(note))


class Rule(CSScene):
    def construct(self):
        self.show_title("The rule: Bellman–Ford")
        eq = MathTex(r"D_B(y)", r"=", r"\min_{v}", r"\{", r"c(B,v)", r"+", r"D_v(y)", r"\}",
                     font_size=64)
        eq[4].set_color(T.CYAN)
        eq[6].set_color(T.ORANGE)
        eq.move_to(UP * 1.7)
        b1 = Brace(eq[4], DOWN, color=T.CYAN)
        t1 = make_text("cost of B's link\nto neighbour v", size=T.SMALL_SIZE + 2, color=T.CYAN)
        t1.next_to(b1, DOWN, buff=0.1).shift(LEFT * 0.9)
        b2 = Brace(eq[6], DOWN, color=T.ORANGE)
        t2 = make_text("v's claimed distance\nto destination y", size=T.SMALL_SIZE + 2,
                       color=T.ORANGE)
        t2.next_to(b2, DOWN, buff=0.1).shift(RIGHT * 0.9)
        with self.say("For each destination, B tries every neighbour."):
            self.play(Write(eq), run_time=1.8)
        with self.say("It adds the cost of its link to that neighbour to the neighbour's "
                      "claimed distance, and keeps the smallest total."):
            self.play(GrowFromCenter(b1), FadeIn(t1))
            self.play(GrowFromCenter(b2), FadeIn(t2))
            self.play(Circumscribe(eq[2], color=T.GREEN, run_time=1.2))

        mist = VGroup(
            Card("Mistake 1: skip the link cost",
                 "C says D is 3 away.\nBut reaching C costs 2,\nso the total is 5.",
                 color=T.RED, width=5.4, size=T.SMALL_SIZE, min_height=1.9),
            Card("Mistake 2: wrong next hop",
                 "To reach D, B sends to C.\nThe next hop is always\none of B's neighbours.",
                 color=T.RED, width=5.4, size=T.SMALL_SIZE, min_height=1.9),
        ).arrange(RIGHT, buff=0.5).move_to(DOWN * 1.25)
        with self.say("Watch out for two classic mistakes: forgetting the link cost, and "
                      "writing the destination as the next hop."):
            self.play(FadeOut(VGroup(b1, t1, b2, t2)), eq.animate.shift(UP * 0.3), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mist], lag_ratio=0.5))


class Compute(CSScene):
    def construct(self):
        self.show_title("Filling in B's routing table")
        grid = GridView([DV[n] for n in NBR], row_labels=NBR, col_labels=DEST,
                        row_colors=[COL[n] for n in NBR], cell_w=0.7, cell_h=0.74, size=28)
        grid.move_to([-3.35, 0.9, 0])
        tags = VGroup(*[Chip(f"+{LINK[n]}", COL[n], size=T.SMALL_SIZE)
                        .next_to(grid.row_labels[r], LEFT, buff=0.2) for r, n in enumerate(NBR)])
        tag_note = make_text("link cost", size=T.SMALL_SIZE - 2, color=T.MUTED)
        tag_note.next_to(tags, UP, buff=0.2)

        table = GridView([["", ""] if d != "B" else ["–", "–"] for d in DEST],
                         row_labels=DEST, col_labels=["cost", "next hop"],
                         row_colors=[COL[d] for d in DEST], cell_w=1.35, cell_h=0.6, size=26)
        table.move_to([4.5, 0.2, 0])
        self.play(FadeIn(grid), FadeIn(tags), FadeIn(tag_note), FadeIn(table))

        def chips_for(c):
            out = VGroup()
            for r, n in enumerate(NBR):
                total = LINK[n] + DV[n][c]
                ch = Chip(f"{LINK[n]} + {DV[n][c]} = {total}", COL[n], size=T.SMALL_SIZE + 2)
                ch.move_to([0.2, grid.boxes[r][0].get_center()[1], 0])
                out.add(ch)
            return out

        def solve(dest, lines, fast=False):
            c = DEST.index(dest)
            totals = [LINK[n] + DV[n][c] for n in NBR]
            k = totals.index(min(totals))
            chips = chips_for(c)
            with self.say(lines[0]):
                self.play(grid.highlight_col(c), table.highlight_cell(c, 0), run_time=0.5)
                if fast:
                    self.play(LaggedStart(*[FadeIn(ch, shift=LEFT * 0.3) for ch in chips],
                                          lag_ratio=0.2), run_time=1.0)
                else:
                    for ch in chips:
                        self.play(FadeIn(ch, shift=LEFT * 0.3), run_time=0.7)
            cost_t = table.target_text(c, 0, totals[k], color=T.GREEN)
            hop_t = table.target_text(c, 1, NBR[k], color=COL[NBR[k]])
            with self.say(lines[1]):
                self.play(chips[k].win(), *[chips[j].lose() for j in range(3) if j != k],
                          run_time=0.6)
                self.play(TransformFromCopy(chips[k].label, cost_t),
                          TransformFromCopy(grid.row_labels[k], hop_t), run_time=1.0)
            self.remove(cost_t, hop_t)
            table.put(c, 0, cost_t)
            table.put(c, 1, hop_t)
            self.play(FadeOut(chips), grid.clear_col(c),
                      table.boxes[c][0].animate.set_stroke(T.MUTED, 1.5), run_time=0.4)

        solve("A", ["Start with destination A. Through A it's four plus zero. Through C, "
                    "two plus five. Through E, six plus thirteen.",
                    "The smallest is four, through A itself. Cost four, next hop A."])
        solve("C", ["Destination C: through C it's just two.",
                    "The direct link wins. Cost two, next hop C."], fast=True)
        solve("D", ["Now D, which B isn't even connected to. Through A it's twenty-four, "
                    "through C five, through E thirteen.",
                    "So B reaches D for five, and the next hop is C, not D."])
        solve("E", ["For E, the direct link costs six.",
                    "That beats going through C for twelve. Cost six, next hop E."], fast=True)
        solve("F", ["And F: through C it's two plus one.",
                    "Three, with C as the next hop again."], fast=True)

        halo = glow(table, T.GREEN, layers=8, spread=0.5).set_z_index(-1)
        with self.say("That's B's complete routing table."):
            self.play(FadeIn(halo), Circumscribe(table, color=T.GREEN, run_time=1.5))


class Result(CSScene):
    def construct(self):
        self.show_title("What B learned")
        g = graph()
        for e in (("C", "D"), ("C", "F")):
            g.edge(*e).set_stroke(color=COL[e[1]], width=3)
        claims = VGroup(*[make_text(f"C: {d} is {DV['C'][DEST.index(d)]} away",
                                    size=T.SMALL_SIZE, color=COL[d])
                          .move_to(g.edge("C", d).get_center() + DOWN * 0.35)
                          for d in ("D", "F")])
        base = VGroup(*[m for m in g if m not in (g["D"], g["F"], g.edge("C", "D"),
                                                  g.edge("C", "F"))])
        self.play(FadeIn(base))
        with self.say("Back on the map, D and F now have a route, both behind C."):
            self.play(FadeIn(g["D"], scale=1.3), FadeIn(g["F"], scale=1.3),
                      Create(g.edge("C", "D")), Create(g.edge("C", "F")), run_time=1.2)
            self.play(FadeIn(claims))

        routes = {"A": ["B", "A"], "C": ["B", "C"], "D": ["B", "C", "D"],
                  "E": ["B", "E"], "F": ["B", "C", "F"]}
        for n in NBR:
            g[n].set_z_index(5)
        g["B"].set_z_index(5)
        with self.say("Traffic for C, D and F all leaves through C, because C is cheap to "
                      "reach and close to the others."):
            self.play(g.highlight_edge("B", "C", T.LIME, 8), run_time=0.4)
            pk = []
            for wave in range(3):
                for d in ("C", "D", "F"):
                    p = Packet(d, COL[d])
                    p.set_z_index(3)
                    pk.append((p, d))
            self.play(LaggedStart(*[p.travel([g[x].get_center() for x in routes[d]],
                                             run_time=1.6, rate_func=linear) for p, d in pk],
                                  lag_ratio=0.15))
            self.remove(*[p for p, _ in pk])

        with self.say("A and E are reached directly. And B did all this without ever seeing "
                      "the whole network, only its neighbours' claims."):
            self.play(g.highlight_edge("B", "A", T.CYAN, 8), g.highlight_edge("B", "E", T.ORANGE, 8),
                      run_time=0.5)
            pk = [(Packet(d, COL[d]), d) for d in ("A", "E") for _ in range(2)]
            for p, _ in pk:
                p.set_z_index(3)
            self.play(LaggedStart(*[p.travel([g[x].get_center() for x in routes[d]],
                                             run_time=1.3, rate_func=linear) for p, d in pk],
                                  lag_ratio=0.25))
            self.remove(*[p for p, _ in pk])
        self.wait(0.5)
