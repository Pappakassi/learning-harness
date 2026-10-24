"""StoryScene: the 3Blue1Brown-inspired style, with a moving camera and Hr. Schiffel.

    from csvideo.story import StoryScene, P
    class Intro(StoryScene):
        def construct(self):
            self.chapter("How email works")                  # big title, then it shrinks to a corner label
            g = self.add_gnome("fierce", corner="DR")        # Hr. Schiffel, pinned to the screen corner
            with self.say("Narration..."):                   # narrator voice
                self.play(Create(thing))
            with self.say("Ach! It is just text!", who="gnome"):   # his voice; his mouth moves
                self.play(g.change("angry"))
            self.play(self.zoom_to(thing))                   # camera move; pinned things stay put
            self.play(self.zoom_reset())

Style rules (P = palette): near-black background, a few colours with fixed meanings, thin captions
without boxes (they also go to an .srt file), objects that morph into the next idea instead of
fading in and out, the camera moving in for details.
"""
from __future__ import annotations

import os
import textwrap
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from manim import (RoundedRectangle, BLACK, DOWN, LEFT, ORIGIN, RIGHT, UL, UP, Create, FadeIn, FadeOut, Line,
                   MovingCameraScene, ReplacementTransform, ScreenRectangle, Text, VGroup, Write, config)

from . import theme as T
from .mascot import Schiffel
from .scene_base import CSScene, SilentService

P = SimpleNamespace(
    BG="#0C0C0F", FG="#ECECEC", MUTED="#8A8F98", FAINT="#23252B",
    BLUE="#58C4DD", TEAL="#5CD0B3", GREEN="#83C167", YELLOW="#FFE066", GOLD="#F0AC5F",
    RED="#FC6255", PINK="#E47FB2", PURPLE="#9A72AC", ORANGE="#FF8A3D", GNOME="#FFB37A",
)
FONT = "Inter"
CAPTION_CHARS = 66


def txt(s, size=30, color=None, weight="NORMAL", font=FONT, **kw) -> Text:
    return Text(s, font_size=size, color=color or P.FG, font=font, weight=weight, **kw)


class StoryScene(CSScene, MovingCameraScene):
    show_captions = True

    def setup(self):
        super().setup()
        if self._backdrop is not None:
            self.remove(self._backdrop)
            self._backdrop = None
        self.camera.background_color = P.BG
        self._pinned = []
        self.gnome = None
        self._narrator_service = self.speech_service
        if os.environ.get("CSVIDEO_DRAFT") == "1":
            self._gnome_service = SilentService()
        else:
            from .voice import make_gnome_service
            self._gnome_service = make_gnome_service()

    # ---------- things that stay fixed on screen while the camera moves ----------
    def pin(self, mob, ref=None):
        """Keep `mob` at its current place on the SCREEN when the camera zooms or pans.
        ref(mob) -> a length used for scale (default: width; Schiffel uses his head)."""
        frame = self.camera.frame
        ref = ref or (lambda m: m.width)
        w0 = frame.width
        anchor = (lambda m: m.anchor()) if isinstance(mob, Schiffel) else (lambda m: m.get_center())
        rel = (anchor(mob) - frame.get_center()) / w0
        ratio = ref(mob) / w0

        def follow(m, dt=0):
            k = frame.width
            cur = ref(m)
            if cur > 1e-6:
                m.scale(ratio * k / cur)
            m.shift(frame.get_center() + rel * k - anchor(m))
        mob.add_updater(follow)
        self._pinned.append(mob)
        return mob

    def unpin(self, mob):
        mob.clear_updaters()
        if mob in self._pinned:
            self._pinned.remove(mob)

    # ---------- camera ----------
    def zoom_to(self, mob, margin: float = 1.35, run_time: float = 1.4):
        """Animation: move the camera so `mob` fills the frame (with a margin)."""
        w = max(mob.width * margin, mob.height * margin * config.frame_width / config.frame_height, 1.0)
        return self.camera.frame.animate(run_time=run_time).set_width(w).move_to(mob.get_center())

    def zoom_reset(self, run_time: float = 1.2):
        return self.camera.frame.animate(run_time=run_time).set_width(config.frame_width).move_to(ORIGIN)

    def spotlight(self, *keep, opacity: float = 0.15, run_time: float = 0.6):
        """Dim everything except `keep` (and pinned things). Undo with unspot()."""
        keep_ids = set()
        for k in keep:
            for f in k.get_family():
                keep_ids.add(id(f))
        self._dimmed = [m for m in self.mobjects if id(m) not in keep_ids and m not in self._pinned
                        and m is not self._caption and not any(id(f) in keep_ids for f in m.get_family())]
        if not self._dimmed:
            return None
        self.play(*[m.animate.set_opacity(opacity) for m in self._dimmed], run_time=run_time)

    def unspot(self, run_time: float = 0.6):
        dimmed = [m for m in getattr(self, "_dimmed", []) if m in self.mobjects]
        if dimmed:
            self.play(*[m.animate.set_opacity(1) for m in dimmed], run_time=run_time)
        self._dimmed = []

    # ---------- chapters ----------
    def chapter(self, title: str, label: str | None = None, hold: float = 0.6):
        """3b1b-style chapter: big centred title, then it shrinks into a small corner label."""
        if self._title is not None:
            old = self._title
            self.unpin(old)
            self.play(FadeOut(old), run_time=0.4)
            self._title = None
        big = txt(title, size=64, weight="BOLD")
        if big.width > config.frame_width - 1.5:
            big.scale_to_fit_width(config.frame_width - 1.5)
        line = Line(LEFT, RIGHT, stroke_color=P.BLUE, stroke_width=4).set_width(big.width * 0.6).next_to(big, DOWN, buff=0.25)
        self.play(Write(big), Create(line), run_time=1.2)
        self.wait(hold)
        small = txt(label or title, size=26, color=P.MUTED, weight="BOLD")
        small.to_corner(UL, buff=0.45)
        self.play(ReplacementTransform(big, small), FadeOut(line), run_time=0.8)
        self._title = small
        self.pin(small)
        return small

    # ---------- the mascot ----------
    def add_gnome(self, mood: str = "fierce", corner: str = "DR", scale: float = 0.42, animate: bool = True):
        g = Schiffel(mood).scale(scale)
        fw, fh = config.frame_width, config.frame_height
        x = fw / 2 - 1.0 if "R" in corner else -fw / 2 + 1.0
        g.shift(np.array([x, 0, 0]) - g.get_center())
        if "D" in corner:
            g.shift(UP * (-fh / 2 + 0.2 - g.get_bottom()[1]))
        else:
            g.shift(UP * (fh / 2 - 0.35 - g.get_top()[1]))
        g.set_z_index(20)
        self.gnome = g
        if animate:
            self.play(g.enter())
        else:
            self.add(g)
        self.pin(g, ref=lambda m: m.head.width)
        return g

    def gnome_says(self, text: str, side: str = "left", hold: float | None = None):
        """Show a speech bubble from Hr. Schiffel (no voice). Returns the bubble (fade it out yourself)."""
        b = self.gnome.bubble(text, side=side)
        b.set_z_index(21)
        self.play(FadeIn(b, scale=0.6, run_time=0.35))
        if hold:
            self.wait(hold)
        return b

    # ---------- narration ----------
    def _make_caption(self, text: str, who: str = "narrator") -> VGroup:
        lines = textwrap.wrap(text, CAPTION_CHARS)
        color = P.GNOME if who == "gnome" else "#DADADA"
        label = txt("\n".join(lines), size=24, color=color, line_spacing=0.85)
        label.set_stroke(BLACK, width=5, background=True)
        frame = self.camera.frame
        k = frame.width / config.frame_width
        label.scale(k)
        maxw = (config.frame_width - 4.2) * k            # keep clear of Hr. Schiffel's corner
        if label.width > maxw:
            label.scale_to_fit_width(maxw)
        label.move_to(frame.get_center() + LEFT * 0.9 * k + DOWN * (frame.height / 2 - 0.25 * k - label.height / 2))
        cap = VGroup(label)
        cap.skip_layout_check = True
        off = label.get_center() - frame.get_center()
        cap.add_updater(lambda m: m.move_to(frame.get_center() + off))   # follow camera pans
        return cap

    @contextmanager
    def say(self, text: str, who: str = "narrator", caption: bool | None = None):
        show = self.show_captions if caption is None else caption
        cap = None
        if show:
            cap = self._make_caption(text, who)
            self.add(cap)
            self._caption = cap
        if who == "gnome":
            self.speech_service = self._gnome_service
            if self.gnome is not None:
                self.gnome.start_talking()
        try:
            with self.voiceover(text=text) as tracker:
                yield tracker
        finally:
            self.speech_service = self._narrator_service
            if who == "gnome" and self.gnome is not None:
                self.gnome.stop_talking()
            if cap is not None:
                self.remove(cap)
                self._caption = None

    # ---------- layout check: only meaningful when the camera is at home ----------
    def _check_layout(self):
        f = self.camera.frame
        if abs(f.width - config.frame_width) > 0.01 or np.linalg.norm(f.get_center()) > 0.01:
            return
        skip = [m for m in self.mobjects if isinstance(m, ScreenRectangle) or m is self.gnome]
        for m in skip:
            m.skip_layout_check = True
        super()._check_layout()


# ---------- the series opener and closer (theme song + Hr. Schiffel) ----------
MUSIC_DIR = Path(__file__).resolve().parent.parent / "music" / "out"
LYRICS = ["Herr Schiffel, Herr Schiffel,", "he knows where the bits go,", "byte by byte and hop by hop,", "through the network, oh!"]


def _ensure_music():
    if not (MUSIC_DIR / "theme_intro.wav").exists():
        import subprocess
        subprocess.run(["node", str(MUSIC_DIR.parent / "gnome_theme.js"), str(MUSIC_DIR)], check=True)


def theme_intro(scene: StoryScene, title: str, subtitle: str = ""):
    """~15.6 s opener: the sung theme, Hr. Schiffel dancing, karaoke lyrics, then the episode title.
    Leaves Hr. Schiffel in the bottom-right corner (scene.gnome) and the title as a corner label."""
    from manim import (AnimationGroup, Circle, Dot, Flash, LaggedStart, Succession, Wait, rate_functions)
    _ensure_music()
    scene.add_sound(str(MUSIC_DIR / "theme_intro.wav"))
    g = Schiffel("happy").scale(0.95).move_to(DOWN * 0.35)
    g.set_z_index(20)
    scene.gnome = g
    scene.play(g.enter(run_time=0.9))                       # 0.9
    scene.play(g.hop(run_time=0.5), run_time=0.5)            # 1.4
    scene.play(g.change("fierce", look=(0.6, 0.2)), run_time=0.6)
    scene.play(g.hop(run_time=0.5), run_time=0.5)            # 2.5
    scene.play(g.blink(), run_time=0.5)
    scene.play(g.change("happy"), run_time=0.5)              # 3.5
    scene.wait(0.45)                                          # ~3.95: chorus starts at 4.0
    g.start_talking()
    lyric = None
    for i, line in enumerate(LYRICS):                         # each line = 2 bars = 2 s
        new = txt(line, size=40, color=P.GNOME, weight="BOLD").move_to(UP * 2.6)
        anims = [FadeIn(new, shift=UP * 0.2, run_time=0.4)]
        if lyric is not None:
            anims.append(FadeOut(lyric, shift=UP * 0.2, run_time=0.3))
        scene.play(*anims, run_time=0.4)
        scene.play(g.hop(run_time=0.5), run_time=0.5)
        scene.wait(0.5)
        scene.play(g.hop(height=0.25, run_time=0.5), run_time=0.5)
        scene.wait(0.1)
        lyric = new
    g.stop_talking()                                          # ~12.0
    big = txt(title, size=60, weight="BOLD").move_to(UP * 3.05)
    if big.width > config.frame_width - 1.0:
        big.scale_to_fit_width(config.frame_width - 1.0)
    sub = txt(subtitle, size=28, color=P.MUTED).next_to(big, DOWN, buff=0.2) if subtitle else VGroup()
    scene.play(FadeOut(lyric, run_time=0.3), Write(big, run_time=1.0), FadeIn(sub, run_time=1.0),
               g.animate.shift(DOWN * 0.45), run_time=1.0)
    scene.play(g.change("surprised"), run_time=0.5)          # ~13.5
    sparks = VGroup(*[Dot(radius=0.05, color=c) for c in (P.YELLOW, P.BLUE, P.PINK, P.GREEN, P.GOLD, P.RED) * 3])
    scene.play(LaggedStart(*[Flash(g.hat_tip.get_top() + RIGHT * 0.0, color=c, line_length=0.4, num_lines=12)
                             for c in (P.YELLOW, P.PINK)], lag_ratio=0.3), g.hop(run_time=0.6), run_time=0.8)
    scene.wait(1.0)                                           # ~15.3
    # settle: title to the corner, gnome to the bottom-right corner
    small = txt(title, size=26, color=P.MUTED, weight="BOLD").to_corner(UL, buff=0.45)
    target = Schiffel("fierce").scale(0.42)
    target.shift(np.array([config.frame_width / 2 - 1.0, 0, 0]) - target.get_center())
    target.shift(UP * (-config.frame_height / 2 + 0.2 - target.get_bottom()[1]))
    scene.play(ReplacementTransform(big, small), FadeOut(sub), g.animate.become(target), run_time=1.0)
    g.mood = "fierce"
    scene._title = small
    scene.pin(small)
    scene.pin(g, ref=lambda m: m.head.width)


def theme_outro(scene: StoryScene, line: str = "Tschüss!"):
    """~6 s closer: outro sting, Hr. Schiffel hops to the middle and waves goodbye."""
    from manim import Flash
    _ensure_music()
    g = scene.gnome
    scene.unpin(g)
    scene.add_sound(str(MUSIC_DIR / "outro.wav"))
    tgt = Schiffel("happy").scale(0.9).move_to(DOWN * 0.3)
    scene.play(g.animate.become(tgt), run_time=0.9)
    g.mood = "happy"
    b = g.bubble(line, side="right", size=36)
    scene.play(FadeIn(b, scale=0.6), g.hop(), run_time=0.6)
    scene.play(g.hop(), run_time=0.5)
    scene.play(g.hop(), run_time=0.5)
    scene.play(Flash(g.anchor() + UP * 2.2, color=P.YELLOW, line_length=0.5, num_lines=14), run_time=0.8)
    scene.wait(2.4)


def halo(mob, color=P.YELLOW, layers: int = 5, spread: float = 0.35, opacity: float = 0.07):
    """Soft rounded-rectangle glow that hugs `mob` (use instead of effects.glow for wide shapes)."""
    g = VGroup(*[RoundedRectangle(corner_radius=0.25 + spread * (i + 1) / layers, width=mob.width + 2 * spread * (i + 1) / layers,
                                  height=mob.height + 2 * spread * (i + 1) / layers, stroke_width=0,
                                  fill_color=color, fill_opacity=opacity).move_to(mob) for i in range(layers)])
    g.skip_layout_check = True
    g.set_z_index(-1)
    return g
