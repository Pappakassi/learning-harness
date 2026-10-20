#!/usr/bin/env python3
"""Dialogue -> out/narration.wav (the voice track), out/voice.json and vo.js (timings, captions, lip-sync).

Edit LINES, then run with the cs-video venv:  ../path/to/skills/cs-video/.venv/bin/python narration.py
LANG = "en": Kokoro v1.0 voices (af_heart, am_michael, bf_emma, am_fenrir ...).
LANG = "zh": Kokoro v1.1-zh through sherpa-onnx (speaker ids: 64 = zm_015 male, 3 = zf_001 female ...).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
SKILLS = Path("__SKILLS__")          # filled in by new_cartoon.py
CSVIDEO = SKILLS / "cs-video"

LANG = "__LANG__"
SR = 48000
# speaker id (used in LINES and by the film's lip-sync) -> voice
VOICES = {"en": {"teacher": "am_michael", "student": "af_heart"},
          "zh": {"teacher": 64, "student": 3}}[LANG]
SPEED = {"teacher": 1.0, "student": 1.0}

# (id, pause before in seconds, speaker, sentences). Each sentence: (spoken, caption or None, second caption or "").
# Keep a sentence short enough for two caption lines. The id names the moment, so score.js can time visuals to it.
LINES = [
    ("hook", 1.2, "student", [("I have a thousand sorted numbers. How fast can I find one?", None, "")]),
    ("idea", 0.5, "teacher", [
        ("Look at the middle one first.", None, ""),
        ("If it's too big, the whole right half is gone, in a single step.", None, ""),
    ]),
    ("wow", 0.6, "student", [("So every look throws away half?", None, "")]),
    ("count", 0.4, "teacher", [("Exactly. A thousand, five hundred, two fifty... about ten looks in total.", None, "")]),
]

PAUSE = {"，": 0.22, "、": 0.18, "；": 0.3, "：": 0.28, "。": 0.45, "！": 0.45, "？": 0.5,
         ",": 0.2, ";": 0.28, ":": 0.25, ".": 0.4, "!": 0.4, "?": 0.45}


def pieces(text):
    """[(chunk, pause after)] split at punctuation, so phrases get natural pauses and their own start times."""
    if LANG == "zh":
        sys.path.insert(0, str(SKILLS / "zh-topic"))
        from zhkit.voice_zh import pieces as zh_pieces
        return zh_pieces(text)
    out = []
    for m in re.finditer(r"[^,;:.!?]+[,;:.!?]*", text):
        chunk = m.group(0).strip()
        if not chunk:
            continue
        p = chunk[-1] if chunk[-1] in PAUSE else ""
        out.append((chunk, PAUSE.get(p, 0.0)))
    return out


class Voice:
    def __init__(self):
        if LANG == "zh":
            sys.path.insert(0, str(SKILLS / "zh-topic"))
            from zhkit.voice_zh import SherpaZhService
            self.tts = SherpaZhService._load()
        else:
            from kokoro_onnx import Kokoro
            v = CSVIDEO / "voices"
            self.tts = Kokoro(str(v / "kokoro-v1.0.onnx"), str(v / "voices-v1.0.bin"))

    def say(self, text, who):
        if LANG == "zh":
            g = self.tts.generate(text, sid=VOICES[who], speed=SPEED[who])
            return np.asarray(g.samples, dtype=np.float32), g.sample_rate
        a, sr = self.tts.create(text, voice=VOICES[who], speed=SPEED[who], lang="en-us")
        return np.asarray(a, dtype=np.float32), sr


def mouth_track(x, sr, fps=30):
    """Per-frame mouth open/wide values from the voice's band energies (lip-sync)."""
    hop = sr // fps
    frames = int(np.ceil(len(x) / hop))
    lo, hi = np.zeros(frames), np.zeros(frames)
    win = np.hanning(hop * 2)
    freqs = np.fft.rfftfreq(hop * 2, 1 / sr)
    bl, bh = (freqs > 250) & (freqs < 900), (freqs > 1800) & (freqs < 4000)
    for f in range(frames):
        seg = x[f * hop: f * hop + hop * 2]
        if len(seg) < hop * 2:
            seg = np.pad(seg, (0, hop * 2 - len(seg)))
        sp = np.abs(np.fft.rfft(seg * win))
        lo[f], hi[f] = np.sqrt((sp[bl] ** 2).sum()), np.sqrt((sp[bh] ** 2).sum())
    tot = lo + hi
    peak = np.percentile(tot, 98) + 1e-9
    open_, wide, el = [], [], 0.0
    for f in range(frames):
        el += (tot[f] / peak - el) * 0.6
        open_.append(round(float(min(1, (max(el, 0) * 1.4) ** 0.8)), 3))
        wide.append(round(float(min(1, hi[f] / (tot[f] + 1e-9) * 2.2)), 3))
    return {"fps": fps, "open": open_, "wide": wide}


def main():
    voice = Voice()
    placed, cursor = [], 0.0
    for lid, gap, who, sentences in LINES:
        at = round(cursor + gap, 2)
        chunks, phrases, sents, pos, sr = [], [], [], 0, 24000
        for spoken, cap, alt in sentences:
            s0 = pos
            for chunk, pause in pieces(spoken):
                x, sr = voice.say(chunk, who)
                phrases.append([chunk, pos])
                chunks.append(x)
                pos += len(x)
                if pause:
                    n = int(sr * pause)
                    chunks.append(np.zeros(n, dtype=np.float32))
                    pos += n
            sents.append([cap or spoken, s0, pos, alt])
        a = np.concatenate(chunks)
        a = np.interp(np.arange(0, len(a) * SR / sr) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        loud = np.abs(a) > 0.01
        a *= 0.12 / (np.sqrt(np.mean(a[loud] ** 2)) if loud.any() else 1)
        f = lambda p: round(at + p / sr, 3)  # noqa: E731
        placed.append({"id": lid, "t": at, "end": round(at + len(a) / SR, 3), "who": who,
                       "text": " ".join(c or s for s, c, _ in sentences),
                       "phrases": [[c, f(p)] for c, p in phrases],
                       "sents": [[s, f(p0), f(p1), alt] for s, p0, p1, alt in sents], "_a": a})
        cursor = at + len(a) / SR
        print(f"{lid:8s} {who:8s} {at:6.2f} -> {placed[-1]['end']:6.2f}")
    end = placed[-1]["end"] + 8.0
    bus = np.zeros(int(end * SR), dtype=np.float32)
    for p in placed:
        i = int(p["t"] * SR)
        bus[i:i + len(p["_a"])] += p.pop("_a")
    (HERE / "out").mkdir(exist_ok=True)
    sf.write(HERE / "out" / "narration.wav", bus, SR)
    mouth = mouth_track(bus, SR)
    (HERE / "out" / "voice.json").write_text(json.dumps(
        {"lines": [{k: l[k] for k in ("t", "end", "who", "text")} for l in placed], "mouth": mouth}, ensure_ascii=False))
    (HERE / "vo.js").write_text(
        "// generated by narration.py: dialogue timings, captions, and the mouth track for lip-sync\n"
        "(function () {\n  const VO = " + json.dumps({"lines": placed, "mouth": mouth}, ensure_ascii=False)
        + ";\n  if (typeof module !== 'undefined') module.exports = VO; else globalThis.VO = VO;\n})();\n")
    print(f"speech ends {placed[-1]['end']:.1f}s")


if __name__ == "__main__":
    main()
