#!/usr/bin/env python3
"""Mandarin (Simplified) dialogue -> out/narration.wav, out/voice.json (lip-sync) and vo.js.

Blue Iceland ice cave intro for Chinese-speaking guests. Each line is split into
sentences (for captions) and phrases (for pauses and timed visuals).
Run with the cs-video venv:
  /home/claude/learning-harness/skills/cs-video/.venv/bin/python narration.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ZH = Path("/home/claude/learning-harness/skills/zh-topic")
sys.path.insert(0, str(ZH))
from zhkit.voice_zh import SherpaZhService, pieces  # noqa: E402

SR = 48000
SPEAKERS = {"guide": 64, "tourist": 3}       # zm_015 (male), zf_001 (female)
SPEED = {"guide": 0.9, "tourist": 0.95}

# (id, pause before in seconds, who, sentences). Each sentence: (spoken text, Chinese caption, English caption).
# The spoken text can differ from the caption (the English greeting is split at a Chinese comma for a pause).
LINES = [
    ("hello", 3.8, "guide", [
        ("Hello，my name is Henry。", "Hello! My name is Henry.", ""),
        ("大家好！我叫亨利。", "大家好！我叫亨利。", "Hi everyone! I'm Henry."),
        ("欢迎参加我们的冰洞之旅。我是你们今天的向导。", "欢迎参加我们的冰洞之旅。我是你们今天的向导。", "Welcome to our ice cave tour. I'm your guide today."),
    ]),
    ("jeep", 0.6, "guide", [("我们先坐上这辆大大的超级吉普车，它叫乌尼莫克。", None, "First we get into this big super jeep. It's called a Unimog.")]),
    ("drive", 0.7, "guide", [
        ("开车大约三十分钟，就到冰川了。", None, "It's about a 30-minute drive to the glacier."),
        ("路上有点颠，请坐好。", None, "The road is a bit bumpy, so please stay seated."),
    ]),
    ("gear", 0.9, "guide", [("到了停车场，每个人都会拿到一个头盔和一副冰爪。", None, "At the parking lot, everyone gets a helmet and a pair of crampons.")]),
    ("carry", 0.5, "guide", [
        ("头盔请戴好。", None, "Please put your helmet on."),
        ("冰爪请自己拿着，从停车场一直带到冰洞。", None, "Carry your own crampons from the parking lot all the way to the cave."),
    ]),
    ("ask", 0.8, "tourist", [("走过去要多久？", None, "How long is the walk?")]),
    ("walk", 0.4, "guide", [
        ("大约三十分钟。", None, "About 30 minutes."),
        ("我们要走过一片冰碛，就是冰川留下的石头和沙子。", None, "We cross a glacier moraine: rocks and sand left behind by the glacier."),
    ]),
    ("hard", 0.4, "guide", [
        ("路不平，有一点难度。", None, "The ground is uneven and moderately challenging."),
        ("请慢慢走，注意脚下。", None, "Walk slowly and watch your step."),
    ]),
    ("cave", 1.0, "guide", [
        ("冰洞里会有很多别的旅行团。", None, "There are many other tour groups in the cave."),
        ("请一直跟着我们的团，千万不要走散。", None, "Always stay with our group. Never wander off."),
    ]),
    ("photo", 0.9, "tourist", [("我可以把头盔摘下来拍照吗？", None, "Can I take my helmet off for a photo?")]),
    ("helmet", 0.3, "guide", [
        ("不可以！", None, "No!"),
        ("整个行程中，任何时候都不能摘下头盔。", None, "Never take your helmet off, at any time during the trip."),
    ]),
    ("ready", 1.0, "guide", [
        ("请穿好登山靴和暖和的衣服。", None, "Please wear hiking boots and warm clothes."),
        ("准备好了吗？", None, "Are you ready?"),
        ("我们出发吧！", None, "Let's go!"),
    ]),
]
SENT = re.compile(r"(?<=[。！？])")


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
    tts = SherpaZhService._load()
    placed, cursor = [], 0.0
    for lid, gap, who, sentences in LINES:
        text = "".join(c or z for z, c, _ in sentences)
        at = round(cursor + gap, 2)
        chunks, phrases, sents, pos, sr = [], [], [], 0, 24000
        for sent, cap, en in sentences:
            s0 = pos
            for chunk, pause in pieces(sent):
                g = tts.generate(chunk, sid=SPEAKERS[who], speed=SPEED[who])
                sr = g.sample_rate
                x = np.asarray(g.samples, dtype=np.float32)
                phrases.append([chunk, pos])
                chunks.append(x)
                pos += len(x)
                if pause:
                    n = int(sr * pause)
                    chunks.append(np.zeros(n, dtype=np.float32))
                    pos += n
            sents.append([cap or sent, s0, pos, en])
        a = np.concatenate(chunks)
        a = np.interp(np.arange(0, len(a) * SR / sr) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        loud = np.abs(a) > 0.01
        a *= 0.12 / (np.sqrt(np.mean(a[loud] ** 2)) if loud.any() else 1)
        f = lambda p: round(at + p / sr, 3)  # noqa: E731
        placed.append({"id": lid, "t": at, "end": round(at + len(a) / SR, 3), "who": who, "text": text,
                       "phrases": [[c, f(p)] for c, p in phrases],
                       "sents": [[s, f(p0), f(p1), en] for s, p0, p1, en in sents], "_a": a})
        cursor = at + len(a) / SR
        print(f"{lid:7s} {who:8s} {at:6.2f} -> {placed[-1]['end']:6.2f}  {text}")
    end = placed[-1]["end"] + 8.0
    bus = np.zeros(int(end * SR), dtype=np.float32)
    for p in placed:
        i = int(p["t"] * SR)
        bus[i:i + len(p["_a"])] += p.pop("_a")
    (HERE / "out").mkdir(exist_ok=True)
    sf.write(HERE / "out" / "narration.wav", bus, SR)
    mouth = mouth_track(bus, SR)
    (HERE / "out" / "voice.json").write_text(json.dumps(
        {"engine": "kokoro-v1.1-zh", "lines": [{k: l[k] for k in ("t", "end", "who", "text")} for l in placed],
         "mouth": mouth}, ensure_ascii=False))
    (HERE / "vo.js").write_text(
        "// generated by narration.py: dialogue timings, captions, and the mouth track for lip-sync\n"
        "(function () {\n  const VO = " + json.dumps({"lines": placed, "mouth": mouth}, ensure_ascii=False)
        + ";\n  if (typeof module !== 'undefined') module.exports = VO; else globalThis.VO = VO;\n})();\n")
    print(f"speech ends {placed[-1]['end']:.1f}s")


if __name__ == "__main__":
    main()
