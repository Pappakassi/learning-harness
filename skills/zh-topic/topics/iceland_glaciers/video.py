"""冰島的冰川 — Mandarin ink-style video. Storyboard: storyboard.md, facts: research.md."""
from pathlib import Path

from zhkit.video import ZhScene  # must come before csvideo (selects ink theme)
from zhkit import geo, lang

import numpy as np
from manim import *  # noqa: F403

from csvideo import theme as T
from csvideo.effects import Countdown, Swarm, glow, shake

HERE = Path(__file__).resolve().parent
SCENES = ["Hook", "SnowToIce", "WhyBlue", "HowBig", "FireUnderIce", "Shrinking", "Teaser"]

GEO = geo.load(HERE / "geo.json")
ICE = ManimColor("#9DBCCB")
ICE_DEEP = ManimColor("#3E6E8A")
MAGMA = ManimColor("#B23A2E")
VOLCANOES = {"格里姆火山": (-17.33, 64.42), "巴達本加火山": (-17.53, 64.64), "卡特拉": (-19.08, 63.63)}
OK_LONLAT = (-20.87, 64.60)

# names and terms stay whole in captions (same list as the book's gloss)
GLOSSED = frozenset(l.split("|")[0].strip() for l in (HERE / "book.txt").read_text().split("=== gloss")[1]
                    .split("=== chapter")[0].splitlines() if "|" in l)
lang.add_words(GLOSSED)


if not (HERE / "backdrop.png").exists():          # generated, not committed
    from zhkit import art
    art.video_backdrop(HERE / "backdrop.png")


class Base(ZhScene):
    backdrop_path = HERE / "backdrop.png"
    known_words = frozenset({"冰島"})
    glossed_words = GLOSSED


def iceland(center=(0, 0.3), width=9.0, height=4.6, land_w=5, ice_op=0.55):
    P = geo.Projector(GEO["bbox"], center=center, width=width, height=height)
    land = geo.ink_shape(GEO["land"], P, width=land_w)
    ice = {n: geo.ink_shape(v, P, color=ICE_DEEP, width=1.2, fill=ICE, fill_opacity=ice_op)
           for n, v in GEO["glaciers"].items()}
    return P, land, ice


def label(s, size=26, color=None, weight="NORMAL"):
    return Text(s, font=T.BODY_FONT, font_size=size, color=color or T.FG, weight=weight)


class Hook(Base):
    def construct(self):
        P, land, ice = iceland()
        with self.say("這是冰島。它的名字裡有一個「冰」字。"):
            self.play(Create(land, run_time=3.0, rate_func=smooth))
        allice = VGroup(*ice.values())
        with self.say("可是，冰川只蓋住了冰島大約十分之一的土地。"):
            self.play(LaggedStart(*[FadeIn(g, scale=0.9) for g in allice], lag_ratio=0.12),
                      run_time=2.0)
        dots = VGroup()
        for name, (lon, lat) in VOLCANOES.items():
            d = Dot(P(lon, lat), radius=0.09, color=MAGMA).set_z_index(5)
            dots.add(d)
        with self.say("更奇怪的是，在這些冰的下面，還藏著火山。"):
            self.play(FadeIn(dots, scale=2), run_time=0.6)
            for _ in range(2):
                self.play(*[Flash(d, color=MAGMA, line_length=0.25, num_lines=10) for d in dots],
                          run_time=0.8)
        with self.say("冰和火在一起，會發生什麼事呢？"):
            self.play(Indicate(dots, color=MAGMA, scale_factor=1.6), run_time=1.2)
        self.play(FadeOut(VGroup(land, allice, dots)), run_time=0.8)
        title = label("冰島的冰川", size=72, weight="MEDIUM").move_to(UP * 0.4)
        sub = label("冰與火之間的國度", size=30, color=T.MUTED).next_to(title, DOWN, buff=0.4)
        self.play(Write(title, run_time=1.6), FadeIn(sub, shift=UP * 0.1))
        self.wait(0.8)


class SnowToIce(Base):
    def construct(self):
        self.show_title("雪怎麼變成冰")
        base_y, x0, width = -1.7, -2.4, 4.0
        ground = Line([x0 - 2.5, base_y, 0], [x0 + 2.5, base_y, 0], stroke_color=T.FG,
                      stroke_width=5)
        self.add(ground)
        layers = []          # [rect, bubbles]
        year_lbl = label("第 1 年", 30).move_to([3.0, 1.3, 0])
        names = VGroup(label("雪", 28), label("冰粒", 28), label("冰", 28, ICE_DEEP, "MEDIUM"))

        def target_state(n):
            """Heights and colours for n stacked layers (top = newest)."""
            hs, cols, ops = [], [], []
            for i in range(n):                       # i = 0 bottom (oldest)
                age = n - 1 - i
                hs.append(max(0.13, 0.42 * 0.78 ** age))
                t = min(age / 6, 1)
                cols.append(interpolate_color(ManimColor("#FBF8F2"), ICE_DEEP, t ** 1.3))
                ops.append(max(0.0, 1 - age / 3))
            return hs, cols, ops

        def place(n, anims):
            hs, cols, ops = target_state(n)
            y = base_y
            for i, (rect, bub) in enumerate(layers[:n]):
                anims.append(rect.animate.stretch_to_fit_height(hs[i])
                             .move_to([x0, y + hs[i] / 2, 0]).set_fill(cols[i], 1))
                anims.append(bub.animate.set_stroke(opacity=ops[i]).stretch_to_fit_height(hs[i] * 0.4)
                             .move_to([x0, y + hs[i] / 2, 0]))
                y += hs[i]

        def drop(k, rt=0.55):
            rect = Rectangle(width=width, height=0.42, stroke_color=T.MUTED, stroke_width=1.2,
                             fill_color=ManimColor("#FBF8F2"), fill_opacity=1).move_to([x0, 2.3, 0])
            bub = VGroup(*[Circle(radius=0.05, stroke_color=T.MUTED, stroke_width=1.5, fill_opacity=0)
                           .move_to([x0 + dx, 2.3, 0]) for dx in np.linspace(-1.6, 1.6, 7)])
            layers.append((rect, bub))
            self.add(rect, bub)
            anims = []
            place(len(layers), anims)
            new_year = label(f"第 {k} 年", 30).move_to(year_lbl)
            self.play(*anims, Transform(year_lbl, new_year), run_time=rt)

        with self.say("一切都從雪開始。高山上的雪，到了夏天也沒有全部融化。"):
            self.add(year_lbl)
            drop(1, 0.8)
            drop(2, 0.8)
        with self.say("第二年，新的雪又蓋在舊的雪上面。一年又一年，越來越厚。"):
            for k in range(3, 9):
                drop(k, 0.6)
        with self.say("上面越重，下面的雪就被壓得越緊，空氣也被擠了出去。"):
            for k in range(9, 13):
                drop(k, 0.55)
            self.play(Transform(year_lbl, label("很多很多年", 30).move_to(year_lbl)), run_time=0.5)

        top = layers[-1][0]
        bottom = layers[0][0]
        mid = layers[len(layers) // 2][0]
        names[0].next_to(top, RIGHT, buff=0.4)
        names[1].next_to(mid, RIGHT, buff=0.4)
        names[2].next_to(bottom, RIGHT, buff=0.4).shift(UP * 0.15)
        with self.say("輕輕的雪花變成小小的冰粒，最後變成又硬又重的冰。"):
            self.play(LaggedStart(*[FadeIn(n, shift=LEFT * 0.2) for n in names], lag_ratio=0.5))

        stack = VGroup(*[VGroup(r, b) for r, b in layers])
        slope = Line([x0 - 2.5, base_y + 0.3, 0], [x0 + 3.5, base_y - 0.45, 0], stroke_color=T.FG,
                     stroke_width=5)
        arrow = Arrow([x0 + 1.0, 0.3, 0], [x0 + 3.6, -0.15, 0], color=ICE_DEEP, stroke_width=6)
        with self.say("冰夠厚、夠重的時候，就會因為自己的重量，慢慢往下流。"):
            self.play(FadeOut(names), FadeOut(year_lbl), run_time=0.4)
            self.play(Transform(ground, slope),
                      stack.animate.apply_matrix([[1, 0.0], [-0.125, 1]], about_point=[x0 - 2.0, base_y, 0])
                      .shift(RIGHT * 0.6 + UP * 0.3),
                      run_time=1.6)
            self.play(GrowArrow(arrow))
            self.play(stack.animate.shift(RIGHT * 0.25 + DOWN * 0.05), run_time=1.5, rate_func=linear)
        with self.say("這就是冰川：一大片會慢慢移動的冰。"):
            self.play(Indicate(stack, color=ICE_DEEP, scale_factor=1.03), run_time=1.2)


class WhyBlue(Base):
    def construct(self):
        self.show_title("冰為什麼是藍色的")
        block = RoundedRectangle(corner_radius=0.2, width=4.6, height=3.0, stroke_color=ICE_DEEP,
                                 stroke_width=3, fill_color=ICE, fill_opacity=0.55)
        block.move_to([0.6, 0.0, 0])
        deep = RoundedRectangle(corner_radius=0.15, width=3.6, height=2.0, stroke_width=0,
                                fill_color=ICE_DEEP, fill_opacity=0.35).move_to(block)
        sun = VGroup(*[Line(ORIGIN, 0.35 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=T.YELLOW,
                            stroke_width=4).shift([-5.3, 2.2, 0]) for a in np.linspace(0, TAU, 12, endpoint=False)],
                     Circle(radius=0.22, stroke_color=T.YELLOW, stroke_width=4).move_to([-5.3, 2.2, 0]))
        eye = VGroup(Ellipse(width=0.9, height=0.45, stroke_color=T.FG, stroke_width=3),
                     Dot(radius=0.12, color=T.FG)).move_to([-5.0, -1.2, 0])
        with self.say("很老的冰，裡面幾乎沒有空氣，冰也特別緊。"):
            self.play(FadeIn(block), FadeIn(deep), run_time=1.0)
            self.play(FadeIn(sun), FadeIn(eye), run_time=0.6)
        entry = block.get_left() + UP * 0.6 + RIGHT * 0.05
        rays = VGroup()
        for c, dy in ((MAGMA, 0.12), (T.GREEN, 0.0), (ICE_DEEP, -0.12)):
            rays.add(Line([-5.0, 2.0 + dy, 0], entry + UP * dy, stroke_color=c, stroke_width=5))
        inside = {
            "red": Line(entry + UP * 0.12, entry + RIGHT * 1.2 + DOWN * 0.3, stroke_color=MAGMA, stroke_width=5),
            "green": Line(entry, entry + RIGHT * 2.0 + DOWN * 0.6, stroke_color=T.GREEN, stroke_width=5),
            "blue": Line(entry + DOWN * 0.12, entry + RIGHT * 2.6 + DOWN * 1.2, stroke_color=ICE_DEEP, stroke_width=6),
        }
        with self.say("陽光照進冰裡。陽光裡其實有很多顏色的光。"):
            self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.2), run_time=1.2)
            self.play(*[Create(l) for l in inside.values()], run_time=1.2)
        with self.say("紅色的光被冰吸收了，跑不出來。"):
            self.play(inside["red"].animate.set_stroke(opacity=0), rays[0].animate.set_stroke(opacity=0.2),
                      Flash(inside["red"].get_end(), color=MAGMA, line_length=0.2), run_time=1.0)
            self.play(inside["green"].animate.set_stroke(opacity=0.15), run_time=0.8)
        back = Line(inside["blue"].get_end(), eye.get_center() + RIGHT * 0.5, stroke_color=ICE_DEEP,
                    stroke_width=6)
        with self.say("藍色的光比較不容易被吸收，最後回到我們的眼睛裡。"):
            self.play(Create(back), run_time=1.2)
            self.play(eye[1].animate.set_color(ICE_DEEP).scale(1.3), Flash(eye, color=ICE_DEEP), run_time=0.8)
        with self.say("所以，冰越老、越緊，藍色就越深。"):
            self.play(deep.animate.set_fill(ICE_DEEP, 0.75), run_time=1.5)


class HowBig(Base):
    def construct(self):
        self.show_title("瓦特納冰川有多大")
        P = geo.Projector(GEO["bbox"], center=(0, 0), width=26, height=13)
        vat = geo.ink_shape(GEO["glaciers"]["Vatnajökull"], P, color=ICE_DEEP, width=2.5, fill=ICE,
                            fill_opacity=0.6)
        vat.move_to([-2.0, 0.35, 0])
        if vat.height > 4.2:
            vat.scale_to_fit_height(4.2)
        pts = vat[0].get_vertices()[:, :2]
        area = 0.5 * abs(np.dot(pts[:, 0], np.roll(pts[:, 1], 1)) - np.dot(pts[:, 1], np.roll(pts[:, 0], 1)))
        side = np.sqrt(area * 6341 / 7700)
        sh = DashedVMobject(Square(side_length=side, stroke_color=MAGMA, stroke_width=4), num_dashes=40)
        sh.move_to(vat.get_center() + LEFT * 0.2)
        vat_lbl = VGroup(label("瓦特納冰川", 28, ICE_DEEP, "MEDIUM"), label("約 7,700 平方公里", 24)).arrange(DOWN, buff=0.1)
        vat_lbl.move_to([3.8, 1.3, 0])
        sh_lbl = VGroup(label("上海", 28, MAGMA, "MEDIUM"), label("約 6,341 平方公里", 24)).arrange(DOWN, buff=0.1)
        sh_lbl.move_to([3.8, -0.4, 0])
        with self.say("冰島最大的冰川，叫瓦特納冰川。"):
            self.play(DrawBorderThenFill(vat), run_time=1.8)
            self.play(FadeIn(vat_lbl, shift=LEFT * 0.2))
        with self.say("它有多大呢？我們把整個上海放上去看看。"):
            self.play(Create(sh), FadeIn(sh_lbl, shift=LEFT * 0.2), run_time=1.6)
        with self.say("冰比上海還要大。上海所有的高樓和馬路，都能藏在冰下面。"):
            self.play(Indicate(vat, color=ICE_DEEP, scale_factor=1.03), run_time=1.2)
            self.play(sh.animate.set_stroke(opacity=0.5), run_time=0.6)

        self.clear_content()
        self.show_title("瓦特納冰川有多厚")
        floor = -1.6
        unit = 4.2 / 1000          # screen units per metre
        ice_col = Rectangle(width=1.6, height=950 * unit, stroke_color=ICE_DEEP, stroke_width=3,
                            fill_color=ICE, fill_opacity=0.7).move_to([-2.4, floor + 950 * unit / 2, 0])
        ice_lbl = label("950 公尺", 28, ICE_DEEP, "MEDIUM").next_to(ice_col, LEFT, buff=0.3).align_to(ice_col, UP)

        def tower(x, y0):
            h = 508 * unit
            segs = VGroup()
            n = 8
            body = h * 0.82
            for i in range(n):
                seg_h = body / n
                w0, w1 = 0.62, 0.78
                yb = y0 + i * seg_h
                segs.add(Polygon([x - w0 / 2, yb, 0], [x + w0 / 2, yb, 0], [x + w1 / 2, yb + seg_h, 0],
                                 [x - w1 / 2, yb + seg_h, 0], stroke_color=T.FG, stroke_width=2,
                                 fill_color=T.FAINT, fill_opacity=1))
            spire = Line([x, y0 + body, 0], [x, y0 + h, 0], stroke_color=T.FG, stroke_width=3)
            return VGroup(segs, spire)
        t1 = tower(0.6, floor)
        t_lbl = label("台北一〇一：508 公尺", 26).next_to(t1, RIGHT, buff=0.3).align_to(t1, UP)
        ground = Line([-4.5, floor, 0], [4.5, floor, 0], stroke_color=T.FG, stroke_width=4)
        with self.say("它也非常厚。最厚的地方，差不多有九百五十公尺。"):
            self.play(Create(ground), GrowFromEdge(ice_col, DOWN), run_time=1.6)
            self.play(FadeIn(ice_lbl))
        with self.say("台北一〇一有五百零八公尺高。"):
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in t1[0]], lag_ratio=0.15),
                      Create(t1[1]), run_time=1.4)
            self.play(FadeIn(t_lbl))
        q = label("冰有幾座台北一〇一那麼高？", 28, MAGMA, "MEDIUM").move_to([4.15, 2.2, 0])
        cd = Countdown(3, color=MAGMA).move_to([4.4, -0.6, 0])
        with self.say("猜一猜：冰有幾座台北一〇一那麼高？"):
            self.play(FadeIn(q, shift=DOWN * 0.1), FadeIn(cd, scale=1.3))
        self.play(cd.run())
        self.play(FadeOut(cd), run_time=0.3)
        t2 = tower(0.6, floor + 508 * unit)
        with self.say("答案是：差不多兩座！"):
            self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in t2[0]], lag_ratio=0.12),
                      Create(t2[1]), run_time=1.4)
            self.play(Indicate(ice_col, color=ICE_DEEP, scale_factor=1.04))


class FireUnderIce(Base):
    def construct(self):
        self.show_title("冰下面的火")
        rock = Polygon([-6.0, -1.5, 0], [-6.0, 0.2, 0], [-4.0, 0.9, 0], [-1.5, 0.8, 0], [0.8, 0.0, 0],
                       [3.0, -0.9, 0], [6.0, -1.1, 0], [6.0, -1.5, 0],
                       stroke_color=T.FG, stroke_width=4, fill_color=ManimColor("#CFC5B3"), fill_opacity=1)
        cap = Polygon([-6.0, 0.2, 0], [-4.0, 0.9, 0], [-1.5, 0.8, 0], [0.8, 0.0, 0], [0.8, 0.55, 0],
                      [-1.5, 1.9, 0], [-4.0, 2.05, 0], [-6.0, 1.6, 0],
                      stroke_color=ICE_DEEP, stroke_width=3, fill_color=ICE, fill_opacity=0.8)
        sea = VGroup(*[Line([3.6 + 0.2 * k, -1.05 - 0.12 * k, 0], [6.0, -1.05 - 0.12 * k, 0],
                            stroke_color=ICE_DEEP, stroke_width=3) for k in range(3)])
        sea_lbl = label("大海", 24, ICE_DEEP).move_to([5.2, -0.4, 0])
        magma = Ellipse(width=2.2, height=0.7, stroke_width=0, fill_color=MAGMA, fill_opacity=0.85)
        magma.move_to([-3.0, -0.9, 0])
        with self.say("瓦特納冰川下面有好幾座火山，格里姆火山是最活躍的。"):
            self.play(FadeIn(rock), FadeIn(cap), FadeIn(sea), FadeIn(sea_lbl), run_time=1.2)
            self.play(FadeIn(magma, scale=0.5), run_time=0.8)
        heat = VGroup(*[ParametricFunction(lambda t, x=x: [x + 0.08 * np.sin(t * 9), t, 0], t_range=[-0.5, 0.75],
                                           stroke_color=MAGMA, stroke_width=3) for x in (-3.5, -3.0, -2.5)])
        pocket = Ellipse(width=0.4, height=0.15, stroke_width=0, fill_color=ICE_DEEP, fill_opacity=0.9)
        pocket.move_to([-3.0, 1.0, 0])
        with self.say("火山在冰下噴發，上面的冰很快就開始融化。"):
            self.play(LaggedStart(*[Create(h) for h in heat], lag_ratio=0.3), run_time=1.2)
            self.add(pocket)
            self.play(pocket.animate.stretch_to_fit_width(2.2).stretch_to_fit_height(0.55)
                      .move_to([-3.0, 1.15, 0]), run_time=2.0)
        with self.say("融化的水留在冰下面，越來越多。"):
            self.play(pocket.animate.stretch_to_fit_width(2.8).stretch_to_fit_height(0.7), run_time=1.5)
            self.play(shake(cap, amplitude=0.04, times=6, run_time=0.6))
        # bridge on the route
        bridge = VGroup(Arc(radius=0.55, start_angle=0, angle=PI, stroke_color=T.FG, stroke_width=4),
                        Line([-0.55, 0, 0], [0.55, 0, 0], stroke_color=T.FG, stroke_width=4)).move_to([2.3, -0.45, 0])
        b_lbl = label("2011", 22, T.MUTED).next_to(bridge, UP, buff=0.1)
        self.play(FadeIn(bridge), FadeIn(b_lbl), run_time=0.5)
        src = [np.array([-3.0 + dx, 1.0, 0]) for dx in np.linspace(-0.9, 0.9, 12)]
        flood = Swarm(src, [5.5, -1.1, 0], color=ICE_DEEP, n=220, speed=0.55, streak=0.35, width=4).start()
        flood.set_z_index(4)
        self.add(flood)
        with self.say("最後，大量的水突然衝出來，一直衝向大海。這就是冰川洪水。",
                      en="A jökulhlaup: a glacial outburst flood."):
            self.play(flood.set_intensity(1.0, run_time=1.2), pocket.animate.set_fill(opacity=0.3), run_time=1.2)
            self.play(shake(bridge, amplitude=0.1, times=8, run_time=0.8))
            self.play(Rotate(bridge, angle=-0.6, about_point=bridge.get_right()), bridge.animate.shift(DOWN * 0.4)
                      .set_opacity(0), run_time=1.0)
        with self.say("二〇一一年，一次冰川洪水沖走了環島公路上的一座橋。"):
            self.wait(0.5)
        self.play(flood.set_intensity(0, run_time=1.0))
        flood.stop()


class Shrinking(Base):
    def construct(self):
        self.show_title("正在變小的冰川")
        P, land, ice = iceland(center=(0, 0.2), width=8.2, height=4.0, land_w=4)
        allice = VGroup(*ice.values())
        k0 = 1 / np.sqrt(0.82)
        for g in allice:
            g.scale(k0)
        year = label("1890 年", 34, T.FG, "MEDIUM").move_to([4.8, 2.0, 0])
        self.play(FadeIn(land), FadeIn(allice), FadeIn(year))
        tracker = ValueTracker(1890)
        year.add_updater(lambda m: m.become(label(f"{int(tracker.get_value())} 年", 34, T.FG, "MEDIUM")
                                             .move_to([4.8, 2.0, 0])))
        with self.say("從十九世紀末到現在，冰島的冰川少了兩千兩百多平方公里。"):
            self.play(tracker.animate.set_value(2019), *[g.animate.scale(1 / k0) for g in allice],
                      run_time=4.0, rate_func=linear)
        year.clear_updaters()
        ok = Dot(P(*OK_LONLAT), radius=0.12, color=ICE_DEEP).set_z_index(5)
        ok_lbl = label("奧克", 26, ICE_DEEP, "MEDIUM").next_to(ok, UP, buff=0.12)
        with self.say("二〇一四年，一條叫奧克的冰川太小、太薄，已經不能再移動了。"):
            self.play(FadeIn(ok, scale=2), FadeIn(ok_lbl), run_time=0.6)
            self.play(Flash(ok, color=ICE_DEEP), run_time=0.6)
            self.play(ok.animate.set_opacity(0.15).scale(0.5), ok_lbl.animate.set_opacity(0.4), run_time=1.5)

        self.play(FadeOut(VGroup(land, allice, ok, ok_lbl, year)), run_time=0.6)
        plaque = RoundedRectangle(corner_radius=0.1, width=6.4, height=3.3, stroke_color=T.FG, stroke_width=3,
                                  fill_color=ManimColor("#D9CFBE"), fill_opacity=1).move_to(UP * 0.35)
        lines = VGroup(label("給未來的一封信", 34, T.FG, "MEDIUM"),
                       label("我們知道正在發生什麼，", 26),
                       label("也知道應該做什麼。", 26),
                       label("只有你們知道，我們有沒有做到。", 26),
                       label("2019 年 8 月", 22, T.MUTED)).arrange(DOWN, buff=0.18).move_to(plaque)
        with self.say("二〇一九年，人們在那裡放了一塊紀念牌：「給未來的一封信」。",
                      en="2019: a plaque, \"A letter to the future\"."):
            self.play(FadeIn(plaque, scale=0.95), Write(lines[0]), run_time=1.6)
        with self.say("信上說：我們知道正在發生什麼，也知道應該做什麼。"):
            self.play(FadeIn(lines[1]), FadeIn(lines[2]), run_time=1.0)
        with self.say("只有你們知道，我們有沒有做到。"):
            self.play(FadeIn(lines[3]), FadeIn(lines[4]), run_time=1.0)
        with self.say("信上還說：大約兩百年以後，冰島所有的冰川可能都會消失。"):
            self.play(Indicate(lines[0], color=MAGMA, scale_factor=1.05), run_time=1.2)


class Teaser(Base):
    def construct(self):
        from zhkit import art
        png = HERE / "build" / "enso.png"
        png.parent.mkdir(exist_ok=True)
        if not png.exists():
            art.enso(900, seed=7).save(png)
        enso = ImageMobject(str(png)).set_height(4.6).move_to(UP * 0.35)
        arc = Arc(radius=1.65, start_angle=PI * 0.6, angle=-TAU * 0.93, stroke_color=T.FG, stroke_width=26)
        arc.move_to(UP * 0.35)
        with self.say("一條冰川，記住了幾百年的雪，也記住了火山的故事。"):
            self.play(Create(arc, run_time=2.0, rate_func=rush_from))
            self.play(FadeIn(enso), FadeOut(arc), run_time=1.0)
        with self.say("下一次你站在冰川上，不妨停下來，安靜地聽一聽。"):
            self.play(enso.animate.set_opacity(0.3), run_time=1.5)
        nxt = VGroup(label("下一個故事", 24, T.MUTED), label("冰島的歷史", 44, T.FG, "MEDIUM")).arrange(DOWN, buff=0.18)
        nxt.move_to(enso)
        with self.say("下一個故事：第一批來到冰島的人，是怎麼在冰和火之間生活的？"):
            self.play(FadeIn(nxt, shift=UP * 0.15), run_time=1.0)
        self.wait(1.0)
