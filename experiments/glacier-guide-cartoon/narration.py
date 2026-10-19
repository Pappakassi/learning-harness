#!/usr/bin/env python3
"""Mandarin dialogue -> out/narration.wav, out/voice.json (lip-sync) and vo.js (timings + captions).

Uses zh-topic's voices (Kokoro v1.1-zh via sherpa-onnx) and its pinyin tools, so the
cartoon speaks with the same voices and caption rules as the Manim videos.
Run with the cs-video venv:  ../learning-harness/skills/cs-video/.venv/bin/python narration.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ZH = Path("/home/claude/learning-harness/skills/zh-topic")
sys.path.insert(0, str(ZH))
from zhkit import lang  # noqa: E402
from zhkit.voice_zh import SherpaZhService, pieces  # noqa: E402

SR = 48000
SPEAKERS = {"guide": 64, "tourist": 3}       # zm_015 (male), zf_001 (female)
KNOWN = frozenset({"冰島"})
GLOSSED = frozenset({"瓦特納冰川", "冰爪", "嚮導"})
lang.add_words(GLOSSED)

# (pause before the line in seconds, who, text, english or None); lines follow each other
LINES = [
    (0.8, "guide", "大家好！歡迎來到瓦特納冰川。我是你們今天的嚮導。", None),
    (0.6, "tourist", "哇，好漂亮！為什麼這裡的冰是藍色的？", None),
    (0.5, "guide", "因為這些冰很老、很緊。紅色的光被吸收了，藍色的光回到我們的眼睛裡。", None),
    (1.0, "guide", "好，大家穿上冰爪，跟著我的腳印走！", "Put on your crampons and follow my footsteps!"),
]


def caption_tokens(text):
    """[[chars, pinyin_or_empty], ...] with pinyin over words above HSK 4 (per character)."""
    out = []
    for seg in lang.segment(text):
        for w, hard in lang.units(seg, 4, KNOWN, GLOSSED):
            if hard:
                for ch, py in zip(w, lang.pinyin_chars(w, text)):
                    out.append([ch, py])
            else:
                out.append([w, ""])
    return out


def mouth_track(x, sr, fps=30):
    hop = sr // fps
    frames = int(np.ceil(len(x) / hop))
    lo, hi = np.zeros(frames), np.zeros(frames)
    win = np.hanning(hop * 2)
    freqs = np.fft.rfftfreq(hop * 2, 1 / sr)
    bl = (freqs > 250) & (freqs < 900)
    bh = (freqs > 1800) & (freqs < 4000)
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
    voices = {who: SherpaZhService.__new__(SherpaZhService) for who in SPEAKERS}
    for who, v in voices.items():
        v.speaker, v.speed = SPEAKERS[who], 0.9
    placed, cursor = [], 0.0
    for gap, who, text, en in LINES:
        at = round(cursor + gap, 2)
        # synthesise phrase by phrase so we know when each phrase starts (for timed visuals)
        tts, chunks, phrase_t = voices[who]._load(), [], []
        sr, pos = 24000, 0
        for chunk, pause in pieces(lang.to_simplified(text)):
            g = tts.generate(chunk, sid=voices[who].speaker, speed=voices[who].speed)
            sr = g.sample_rate
            x = np.asarray(g.samples, dtype=np.float32)
            phrase_t.append([chunk, round(pos / sr, 3)])
            chunks.append(x)
            pos += len(x)
            if pause:
                chunks.append(np.zeros(int(sr * pause), dtype=np.float32))
                pos += int(sr * pause)
        a = np.concatenate(chunks)
        a = np.interp(np.arange(0, len(a) * SR / sr) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        rms = np.sqrt(np.mean(a[np.abs(a) > 0.01] ** 2)) if np.any(np.abs(a) > 0.01) else 1
        a *= 0.12 / rms
        placed.append((at, who, text, en, a, [[lang.to_traditional(c), round(at + t, 3)] for c, t in phrase_t]))
        cursor = at + len(a) / SR
    end = max(p[0] + len(p[4]) / SR for p in placed) + 3.0
    bus = np.zeros(int(end * SR), dtype=np.float32)
    lines = []
    for at, who, text, en, a, phr in placed:
        i = int(at * SR)
        bus[i:i + len(a)] += a
        lines.append({"t": at, "end": round(at + len(a) / SR, 3), "who": who, "text": text,
                      "en": en, "tokens": caption_tokens(text), "phrases": phr})
        prev_end = lines[-1]["end"]
        print(f"{who:8s} {at:5.2f} -> {prev_end:5.2f}  {text}")
    for a_, b_ in zip(lines, lines[1:]):
        if a_["end"] > b_["t"] - 0.3:
            print(f"WARNING: line at {b_['t']} starts before the previous ends ({a_['end']})")
    (HERE / "out").mkdir(exist_ok=True)
    sf.write(HERE / "out" / "narration.wav", bus, SR)
    vo = {"engine": "kokoro-v1.1-zh", "lines": [{k: l[k] for k in ("t", "end", "who", "text")} for l in lines],
          "mouth": mouth_track(bus, SR)}
    (HERE / "out" / "voice.json").write_text(json.dumps(vo, ensure_ascii=False))
    (HERE / "vo.js").write_text(
        "// generated by narration.py: dialogue timings, captions, and the mouth track for lip-sync\n"
        "(function () {\n  const VO = " + json.dumps({"lines": lines, "mouth": vo["mouth"]}, ensure_ascii=False)
        + ";\n  if (typeof module !== 'undefined') module.exports = VO; else globalThis.VO = VO;\n})();\n")
    print(f"total {end:.1f}s")


if __name__ == "__main__":
    main()
