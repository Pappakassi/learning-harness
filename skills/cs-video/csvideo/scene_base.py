"""CSScene: the base class every video scene inherits from.

It gives you:
  * self.say(text)      -> narration block (voice + caption), use as `with self.say(...) as t:`
  * self.show_title(s)  -> scene title at the top, replaces the previous one
  * self.clear_content() -> fade out everything except the title
  * an automatic layout check after every animation (warnings go to layout_report.txt)

Draft mode: set CSVIDEO_DRAFT=1 to skip TTS and use silent audio of estimated
length. Rendering is much faster and layout problems show up the same way.
"""
from __future__ import annotations

import os
import subprocess
import textwrap
from contextlib import contextmanager
from pathlib import Path

from manim import (DOWN, UP, FadeIn, FadeOut, ReplacementTransform, RoundedRectangle,
                   Text, VGroup, config, logger)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService, initialize_speech_service

from . import theme as T

REPORT_PATH = Path(os.environ.get("CSVIDEO_REPORT", "layout_report.txt"))
WORDS_PER_SEC = 2.5
CAPTION_CHARS = 70
CAPTION_MAX_LINES = 3


def report(msg: str):
    """Write a warning to the layout report (shown at the end of render.py)."""
    logger.warning(msg)
    with REPORT_PATH.open("a") as f:
        f.write(msg + "\n")


class SilentService(SpeechService):
    """Draft-mode speech: silence with the length real speech would roughly take."""

    def __init__(self, **kwargs):
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "silent"}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        secs = max(1.0, len(text.split()) / WORDS_PER_SEC)
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        subprocess.run(["sox", "-n", "-r", "22050", "-c", "1", str(Path(cache_dir) / audio_path),
                        "trim", "0", f"{secs:.2f}"], check=True)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_path)}


def make_text(s, size=T.BODY_SIZE, color=T.FG, font=T.BODY_FONT, **kw) -> Text:
    return Text(s, font_size=size, color=color, font=font, **kw)


class CSScene(VoiceoverScene):
    show_captions = True

    def setup(self):
        super().setup()
        self.camera.background_color = T.BG
        if os.environ.get("CSVIDEO_DRAFT") == "1":
            self.set_speech_service(SilentService())
        else:
            from .voice import make_speech_service
            self.set_speech_service(make_speech_service())
        self._title = None
        self._caption = None
        self._warned = set()

    # ---------- titles ----------
    def show_title(self, text: str, run_time: float = 0.8):
        new = make_text(text, size=T.HEADING_SIZE, weight="BOLD").move_to(UP * T.TITLE_Y)
        if new.width > T.FRAME_W - 2 * T.SAFE_MARGIN:
            new.scale_to_fit_width(T.FRAME_W - 2 * T.SAFE_MARGIN)
        if self._title is None:
            self.play(FadeIn(new, shift=DOWN * 0.2), run_time=run_time)
        else:
            self.play(ReplacementTransform(self._title, new), run_time=run_time)
        self._title = new
        return new

    def clear_content(self, run_time: float = 0.6, keep_title: bool = True):
        keep = {self._title, self._caption} if keep_title else {self._caption}
        others = [m for m in self.mobjects if m not in keep]
        if others:
            self.play(*[FadeOut(m) for m in others], run_time=run_time)
        if not keep_title and self._title is not None:
            self.play(FadeOut(self._title), run_time=run_time)
            self._title = None

    # ---------- narration ----------
    def _make_caption(self, text: str) -> VGroup:
        lines = textwrap.wrap(text, CAPTION_CHARS)
        if len(lines) > CAPTION_MAX_LINES:
            self._warn(f"caption has {len(lines)} lines (max {CAPTION_MAX_LINES}); "
                       f"split this narration into smaller say() blocks: {text[:50]}...")
        label = make_text("\n".join(lines), size=T.CAPTION_SIZE, color=T.FG, line_spacing=0.9)
        max_w = T.FRAME_W - 2 * T.SAFE_MARGIN - 0.4
        if label.width > max_w:
            label.scale_to_fit_width(max_w)
        box = RoundedRectangle(corner_radius=0.12, width=label.width + 0.5,
                               height=label.height + 0.3, fill_color=T.BG,
                               fill_opacity=0.85, stroke_width=0)
        cap = VGroup(box, label)
        cap.move_to(DOWN * (config.frame_height / 2 - T.SAFE_MARGIN - cap.height / 2))
        return cap

    @contextmanager
    def say(self, text: str, caption: bool | None = None):
        """Narrate `text`. Animations inside the block play while it is spoken;
        the block waits until the speech ends. Use t.duration to size run_times."""
        show = self.show_captions if caption is None else caption
        cap = None
        if show:
            cap = self._make_caption(text)
            self.add(cap)
            self._caption = cap
        with self.voiceover(text=text) as tracker:
            yield tracker
        if cap is not None:
            self.remove(cap)
            self._caption = None

    # ---------- layout check ----------
    def _warn(self, msg: str):
        key = (type(self).__name__, msg)
        if key in self._warned:
            return
        self._warned.add(key)
        t = getattr(self.renderer, "time", 0.0)
        line = f"[{type(self).__name__} @ {t:5.1f}s] {msg}"
        logger.warning(line)
        with REPORT_PATH.open("a") as f:
            f.write(line + "\n")

    def _check_layout(self):
        half_w = config.frame_width / 2 - 0.05
        half_h = config.frame_height / 2 - 0.05
        for m in self.mobjects:
            if m is self._caption or getattr(m, "skip_layout_check", False):
                continue
            if m.width == 0 and m.height == 0:
                continue
            name = getattr(m, "layout_name", type(m).__name__)
            if (m.get_left()[0] < -half_w or m.get_right()[0] > half_w
                    or m.get_top()[1] > half_h or m.get_bottom()[1] < -half_h):
                self._warn(f"{name} goes off-screen")
            if self._caption is not None and m.get_bottom()[1] < self._caption.get_top()[1] - 0.02:
                self._warn(f"{name} overlaps the caption area (bottom at y={m.get_bottom()[1]:.2f})")
            if (self._title is not None and m is not self._title
                    and m.get_top()[1] > self._title.get_bottom()[1] + 0.02):
                self._warn(f"{name} overlaps the title (top at y={m.get_top()[1]:.2f})")

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        self._check_layout()
