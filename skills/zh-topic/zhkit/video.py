"""ZhScene: a CSScene for Mandarin videos in the ink (sumi-e) style.

- Mandarin narration (Kokoro + misaki G2P); traditional text is fine.
- Captions in WenKai: Chinese, pinyin over words above HSK 4, optional English line
  (`self.say(text, en="...")`) only when it really helps.
- Rice-paper backdrop with faint distant mountains.

Import this module BEFORE csvideo in a video file (it selects the ink theme).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

os.environ.setdefault("CSVIDEO_THEME", "ink")

from manim import (DOWN, UP, ImageMobject, Line, RoundedRectangle, Text, VGroup,  # noqa: E402
                   config)
from manim_voiceover.services.base import SpeechService, initialize_speech_service  # noqa: E402

from csvideo import CSScene  # noqa: E402
from csvideo import theme as T  # noqa: E402

from . import lang  # noqa: E402

CHARS_PER_SEC = 4.2          # Mandarin speaking rate estimate for draft mode
LINE_CHARS = 22              # caption wrap width
PUNCT = "，。！？；：、"


class SilentZh(SpeechService):
    def __init__(self, **kwargs):
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = cache_dir or self.cache_dir
        input_data = {"input_text": text, "service": "silent-zh"}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        n = sum(1 for ch in text if lang.is_chinese(ch))
        secs = max(1.0, n / CHARS_PER_SEC)
        audio_path = path or (self.get_audio_basename(input_data) + ".wav")
        subprocess.run(["sox", "-n", "-r", "22050", "-c", "1", str(Path(cache_dir) / audio_path),
                        "trim", "0", f"{secs:.2f}"], check=True)
        return {"input_text": text, "input_data": input_data, "original_audio": str(audio_path)}


def wrap_zh(text: str, width: int = LINE_CHARS) -> list[str]:
    """Wrap Chinese text into lines of at most `width` chars, breaking after
    punctuation where possible and never inside a word."""
    words = lang.segment(text)
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) > width and cur:
            # move back to the last punctuation if it's not too far back
            cut = max(cur.rfind(p) for p in PUNCT)
            if cut >= width * 0.5 and cut < len(cur) - 1:
                lines.append(cur[:cut + 1])
                cur = cur[cut + 1:]
            else:
                lines.append(cur)
                cur = ""
        cur += w
    if cur:
        lines.append(cur)
    return lines


def zh_line(line: str, size: int = 30, py_size: int = 15, max_level: int = 4, known=frozenset(),
            color=None, py_color=None, glossed=frozenset(), seen: dict | None = None,
            limit: int = 2) -> VGroup:
    """One line of Chinese with pinyin above words harder than `max_level`."""
    color = color or T.FG
    py_color = py_color or T.BLUE
    txt = Text(line, font=T.BODY_FONT, font_size=size, color=color)
    glyphs = [g for g in txt.submobjects]
    chars = [ch for ch in line if not ch.isspace()]
    out = VGroup(txt)
    if len(glyphs) != len(chars):
        return out
    idx = 0
    for seg in lang.segment(line):
        for w, hard in lang.units(seg, max_level, known, glossed):
            n = len([c for c in w if not c.isspace()])
            if hard and seen is not None:
                seen[w] = seen.get(w, 0) + 1
                hard = seen[w] <= limit
            if hard:
                for k, syl in enumerate(lang.pinyin_chars(w, line)):
                    if idx + k >= len(glyphs):
                        break
                    g = glyphs[idx + k]
                    py = Text(syl, font="Inter", font_size=py_size, color=py_color)
                    if py.width > g.width * 1.1:
                        py.scale_to_fit_width(g.width * 1.1)
                    py.move_to(g.get_center()).align_to(txt, UP).shift(UP * (py.height + 0.07))
                    out.add(py)
            idx += n
    return out


class ZhScene(CSScene):
    """Base scene for Mandarin ink-style videos."""

    pinyin_level = 4          # words above this HSK level get pinyin in captions
    pinyin_repeats = 2        # ...for their first N uses in each scene
    known_words: frozenset = frozenset()    # words to treat as easy (e.g. 冰島)
    glossed_words: frozenset = frozenset()  # names/terms kept whole (from the book's gloss)
    backdrop_path = None      # set to a PNG from art.video_backdrop; None = plain paper

    def setup(self):
        super().setup()
        if os.environ.get("CSVIDEO_DRAFT") == "1":
            self.set_speech_service(SilentZh())
        else:
            from .voice_zh import make_zh_service
            self.set_speech_service(make_zh_service())
        self.camera.background_color = T.BG
        if self.backdrop_path and Path(self.backdrop_path).exists():
            bg = ImageMobject(str(self.backdrop_path))
            bg.height = config.frame_height
            bg.set_z_index(-100)
            self._backdrop = bg
            self.add(bg)

    def _make_caption(self, text: str, en: str | None = None) -> VGroup:
        lines = wrap_zh(text)
        if len(lines) > 2:
            self._warn(f"caption has {len(lines)} lines (max 2); split this narration: {text[:20]}…")
        if not hasattr(self, "_py_seen"):
            self._py_seen = {}
        rows = VGroup(*[zh_line(l, max_level=self.pinyin_level, known=self.known_words,
                                glossed=self.glossed_words, seen=self._py_seen,
                                limit=self.pinyin_repeats)
                        for l in lines]).arrange(DOWN, buff=0.12)
        content = VGroup(rows)
        if en:
            e = Text(en, font="Inter", font_size=18, color=T.MUTED, slant="ITALIC")
            content.add(e)
            content.arrange(DOWN, buff=0.12)
        max_w = config.frame_width - 2 * T.SAFE_MARGIN - 0.4
        if content.width > max_w:
            content.scale_to_fit_width(max_w)
        box = RoundedRectangle(corner_radius=0.12, width=content.width + 0.6,
                               height=content.height + 0.3, fill_color=T.BG,
                               fill_opacity=0.88, stroke_color=T.MUTED, stroke_width=0.8)
        content.move_to(box)
        cap = VGroup(box, content)
        cap.move_to(DOWN * (config.frame_height / 2 - T.SAFE_MARGIN - cap.height / 2))
        cap.set_z_index(50)
        return cap

    from contextlib import contextmanager as _cm

    @_cm
    def say(self, text: str, en: str | None = None, caption: bool | None = None):
        show = self.show_captions if caption is None else caption
        cap = None
        if show:
            cap = self._make_caption(text, en)
            self.add(cap)
            self._caption = cap
        with self.voiceover(text=text) as tracker:
            yield tracker
        if cap is not None:
            self.remove(cap)
            self._caption = None

    def show_title(self, text: str, run_time: float = 0.8):
        """Title in brush font with a small red seal mark to its left."""
        return super().show_title(text, run_time)
