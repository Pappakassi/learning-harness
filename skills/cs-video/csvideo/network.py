"""Network diagram templates: hosts, routers, links, packets and trees.

    tree = NetTree({"R1": "S", "R2": "S", "A": "R1", "B": "R1", "C": "R2"},
                   kinds={"S": "sender", "R1": "router", "R2": "router"})
    self.play(FadeIn(tree))
    pkts, anim = tree.send("S", ["A", "B", "C"], "SEQ 1")   # one copy per destination
    self.play(anim)                                          # copies share links, split at routers
    self.play(FadeOut(pkts))

Packets sent to several destinations travel together along shared links and
split where the paths split, which is exactly how multicast copying looks.
Sending from many hosts to one node shows ACKs converging (implosion).
"""
from __future__ import annotations

import numpy as np
from manim import (DOWN, UP, AnimationGroup, Circle, Line, RoundedRectangle, Text,
                   UpdateFromAlphaFunc, VGroup, linear, smooth)

from . import theme as T


def _txt(s, size, color=T.FG, **kw):
    return Text(str(s), font_size=size, color=color, font=T.BODY_FONT, **kw)


class NetNode(VGroup):
    """A host (rounded box), router (circle) or sender (bold blue box)."""

    STYLE = {"host": T.MUTED, "router": T.PURPLE, "sender": T.BLUE}

    def __init__(self, name: str, kind: str = "host", note: str | None = None,
                 scale: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = f"NetNode {name}"
        self.name, self.kind = name, kind
        color = self.STYLE.get(kind, T.MUTED)
        if kind == "router":
            self.shape = Circle(radius=0.34 * scale, stroke_color=color, stroke_width=3,
                                fill_color=T.FAINT, fill_opacity=1)
        else:
            w = (1.0 if kind == "sender" else 0.72) * scale
            probe = _txt(name, int(22 * scale), weight="BOLD")
            w = max(w, probe.width + 0.4 * scale)   # grow the box to fit the name
            self.shape = RoundedRectangle(corner_radius=0.1, width=w, height=0.56 * scale,
                                          stroke_color=color,
                                          stroke_width=4 if kind == "sender" else 2.5,
                                          fill_color=T.FAINT, fill_opacity=1)
        self.label = _txt(name, int(22 * scale), color=T.FG, weight="BOLD")
        if self.label.width > self.shape.width * 0.85:
            self.label.scale_to_fit_width(self.shape.width * 0.85)
        self.label.move_to(self.shape)
        self.add(self.shape, self.label)
        self.note = None
        if note:
            self.set_note(note)

    def set_note(self, text: str, color=T.MUTED, side=DOWN):
        """Small text under (or over) the node, e.g. an RTT. Not animated."""
        if self.note is not None:
            self.remove(self.note)
        self.note = _txt(text, T.SMALL_SIZE - 2, color=color)
        self.note.next_to(self.shape, side, buff=0.1)
        self.add(self.note)
        return self

    def flash(self, color=T.RED, width=6):
        return self.shape.animate.set_stroke(color=color, width=width)

    def reset(self):
        color = self.STYLE.get(self.kind, T.MUTED)
        return self.shape.animate.set_stroke(color=color,
                                             width=4 if self.kind == "sender" else 2.5)


class Packet(VGroup):
    """A small labelled packet, e.g. Packet("SEQ 1", T.BLUE) or Packet("ACK", T.GREEN)."""

    def __init__(self, label: str = "", color=T.BLUE, size: int = 16, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "Packet"
        self.skip_layout_check = True  # packets are in flight; checked via frames instead
        text = _txt(label, size, color=T.BG, weight="BOLD") if label else None
        w = max(0.32, (text.width + 0.2) if text else 0.32)
        box = RoundedRectangle(corner_radius=0.07, width=w, height=0.3,
                               fill_color=color, fill_opacity=1, stroke_width=0)
        self.add(box)
        if text:
            text.move_to(box)
            self.add(text)

    def travel(self, points, run_time: float = 1.5, rate_func=smooth):
        """Animation moving this packet through a list of points, one hop per
        equal slice of time (so copies sharing a hop stay perfectly in sync).
        The packet is invisible until its animation actually starts, so packets
        waiting inside a LaggedStart don't pile up at the start point."""
        pts = [np.array(p, dtype=float) for p in points]
        hops = max(len(pts) - 1, 1)
        self.move_to(pts[0]).set_opacity(0)

        def update(mob, alpha):
            if alpha <= 0:
                mob.set_opacity(0)
                return
            mob.set_opacity(1)
            t = min(alpha, 1.0) * hops
            i = min(int(t), hops - 1)
            f = t - i
            mob.move_to(pts[i] + (pts[i + 1] - pts[i]) * f)
        return UpdateFromAlphaFunc(self, update, run_time=run_time, rate_func=rate_func)


class NetTree(VGroup):
    """A tree network laid out top-down from a {child: parent} map.

    kinds: {name: "sender" | "router" | "host"}; unlisted names are hosts.
    notes: {name: "40 ms"} small text under nodes.
    """

    def __init__(self, parents: dict, kinds: dict | None = None, notes: dict | None = None,
                 width: float = 11.0, level_gap: float = 1.45, scale: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.layout_name = "NetTree"
        kinds = kinds or {}
        self.parents = dict(parents)
        roots = {p for p in parents.values() if p not in parents}
        assert len(roots) == 1, f"tree needs exactly one root, got {roots}"
        self.root = roots.pop()
        children: dict[str, list[str]] = {}
        for c, p in parents.items():
            children.setdefault(p, []).append(c)
        self.children = children

        # leaf order (depth-first) gives x positions; parents center over children
        leaves = []

        def dfs(n):
            if n not in children:
                leaves.append(n)
            for c in children.get(n, []):
                dfs(c)
        dfs(self.root)
        depth = {self.root: 0}
        order = [self.root]
        for n in order:
            for c in children.get(n, []):
                depth[c] = depth[n] + 1
                order.append(c)

        self.nodes: dict[str, NetNode] = {}
        for n in order:
            self.nodes[n] = NetNode(n, kinds.get(n, "host"), (notes or {}).get(n), scale=scale)
        gap = width / max(len(leaves), 1)
        x_of = {leaf: (i - (len(leaves) - 1) / 2) * gap for i, leaf in enumerate(leaves)}

        def place(n):
            if n in x_of:
                return x_of[n]
            xs = [place(c) for c in children[n]]
            x_of[n] = sum(xs) / len(xs)
            return x_of[n]
        place(self.root)
        for n, node in self.nodes.items():
            node.move_to([x_of[n], -depth[n] * level_gap, 0])

        self.links: dict[tuple[str, str], Line] = {}
        link_group = VGroup()
        for c, p in parents.items():
            ln = Line(self.nodes[p].shape.get_center(), self.nodes[c].shape.get_center(),
                      stroke_color=T.MUTED, stroke_width=3)
            self.links[(p, c)] = ln
            link_group.add(ln)
        self.link_group = link_group
        self.add(link_group, *self.nodes.values())   # links behind nodes
        self.move_to([0, 0, 0])

    def __getitem__(self, name):
        if isinstance(name, str):
            return self.nodes[name]
        return super().__getitem__(name)

    def link(self, a: str, b: str) -> Line:
        return self.links.get((a, b)) or self.links[(b, a)]

    def path(self, src: str, dst: str) -> list:
        """Node centers along the tree path from src to dst."""
        def up(n):
            chain = [n]
            while n in self.parents:
                n = self.parents[n]
                chain.append(n)
            return chain
        a, b = up(src), up(dst)
        common = next(n for n in a if n in b)
        names = a[:a.index(common) + 1] + list(reversed(b[:b.index(common)]))
        return [self.nodes[n].shape.get_center() for n in names]

    def send(self, src: str, dsts, label: str = "", color=T.BLUE, run_time: float = 2.0,
             rate_func=linear):
        """One packet copy per destination; returns (packets VGroup, animation)."""
        pkts = VGroup()
        anims = []
        for d in dsts:
            p = Packet(label, color)
            anims.append(p.travel(self.path(src, d), run_time=run_time, rate_func=rate_func))
            pkts.add(p)
        return pkts, AnimationGroup(*anims)

    def gather(self, srcs, dst: str, label: str = "ACK", color=T.GREEN,
               run_time: float = 2.0, rate_func=linear, spread: float = 0.16):
        """Packets from many nodes converging on one (e.g. ACKs flowing back).

        Each packet is offset slightly (`spread`) so that, where they merge, they
        visibly pile up instead of hiding behind each other.
        """
        pkts = VGroup()
        anims = []
        n = len(srcs)
        for k, s in enumerate(srcs):
            off = np.array([(k - (n - 1) / 2) * spread * 0.9, (k % 3 - 1) * spread, 0.0])
            pts = self.path(s, dst)
            pts = [pts[0]] + [p + off for p in pts[1:]]
            p = Packet(label, color)
            anims.append(p.travel(pts, run_time=run_time, rate_func=rate_func))
            pkts.add(p)
        return pkts, AnimationGroup(*anims)
