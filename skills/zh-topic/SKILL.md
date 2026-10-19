---
name: zh-topic
description: Make a Mandarin Chinese explainer video (ink-wash style, traditional characters, selective pinyin) plus a matching HSK 4–5 graded-reader EPUB on any topic, e.g. "make a Chinese video and book about glaciers in Iceland". Watch first, then read.
---

# Chinese topic video + graded reader

One topic in, two outputs that share facts and vocabulary:

1. **Video** (~3 min): Mandarin narration (Kokoro + misaki G2P for correct tones), sumi-e ink
   style on rice paper, traditional-character captions with pinyin over words above HSK 4,
   an English line only where it really helps. Built on the `cs-video` engine.
2. **EPUB** (~3,000 characters, 4–6 chapters): traditional characters at HSK 4–5,
   per-character ruby pinyin on a hard word's first use in each chapter, a glossary and
   3 comprehension questions per chapter, answer key, full vocabulary list, generated
   zen ink artwork (cover with vertical calligraphy title + red seal, chapter vignettes),
   embedded brush font (LXGW WenKai TC, subset).

Watch the video first (it primes the words), then read the book.

Everything below is relative to `skills/zh-topic/` in the repo **Pappakassi/learning-harness**.

## 0. Setup (once per session/machine)

If the repo isn't on disk: attach it (add-repo tool, owner `Pappakassi`, repo
`learning-harness`, push access) and `git clone --depth 1 https://github.com/Pappakassi/learning-harness ~/learning-harness`.

```bash
cd ~/learning-harness/skills/cs-video && bash setup.sh     # engine, voices (once)
cd ../zh-topic && bash setup.sh                             # Chinese extras, fonts, HSK list
```
Use `../cs-video/.venv/bin/python` for every script below (written `PY`).

## 1. Research first → `topics/<slug>/research.md`

Search the web and write the facts with numbered sources. **Every number in the video or
book must come from this file.** Add 1–2 comparisons a Chinese-speaking viewer can feel
(e.g. "bigger than Shanghai", "two Taipei 101s"), and look those numbers up too.
If the topic is a place, run `PY scripts/fetch_geo.py <Country> topics/<slug>/geo.json`
for real outlines (country + glaciers from Natural Earth) to draw maps.

## 2. Write the book → `topics/<slug>/book.txt`

Format (see `topics/iceland_glaciers/book.txt`):
```
title: 冰島的冰川
subtitle: 冰與火之間的國度
seal: 冰火                 # 1–4 chars for the red seal on the cover
level: 4                    # words above this get pinyin + glossary
known: 冰島                 # never glossed
=== gloss                   # names and topic terms (kept whole, English given)
冰川 | glacier
=== chapter 雪怎麼變成冰 | art=glacier      # art: mountains|glacier|volcano|flood|melt|enso
One paragraph per line.
? Question || answer
```
Writing rules: traditional characters (Taiwan usage), short sentences, HSK 1–4 grammar,
one new idea per paragraph, concrete images, a little story or human angle per chapter,
~500–650 characters per chapter, last chapter practical or personal. Only facts from
`research.md`.

Check the level, then fix until it passes:
```bash
PY -c "import sys; sys.path.insert(0,'.'); from zhkit import book as B; print(B.report(B.parse('topics/<slug>/book.txt')))"
```
Targets: **≥ 90% of words ≤ HSK 5**, no `MISSING GLOSS`, and replace words in the
"Above HSK 5 without a custom gloss" list with simpler ones unless they are the topic's
core words. Then build:
```bash
PY -c "import sys; sys.path.insert(0,'.'); from zhkit import book as B; B.build('topics/<slug>/book.txt', 'topics/<slug>/build/<slug>.epub', 'topics/<slug>/build/book_art')"
```
Look at it: unzip the epub and screenshot `ch1.xhtml`, `ch3.xhtml`, `vocab.xhtml` with
Playwright/Chromium (paper background, ruby pinyin, glossary, art all visible; pinyin
readings right in context).

## 3. Storyboard → `topics/<slug>/storyboard.md`

Follow the cs-video storyboard + **Make it engaging** rules (hook in 10 s, picture first,
one "your turn" with `Countdown`, change every 10–20 s, teaser at the end; the teaser can
name the next topic). Use the same facts and key words as the book, so the video primes
the vocabulary.

## 4. Video → `topics/<slug>/video.py`

```python
from zhkit.video import ZhScene          # FIRST: selects the ink theme
from zhkit import geo, lang
from manim import *
from csvideo import theme as T
from csvideo.effects import Countdown, Swarm, shake

SCENES = ["Hook", ...]

class Base(ZhScene):
    backdrop_path = HERE / "backdrop.png"    # PY -c "...art.video_backdrop('topics/<slug>/backdrop.png')"
    known_words = frozenset({"冰島"})
    glossed_words = GLOSSED                  # gloss words from book.txt (keeps names whole)

class Hook(Base):
    def construct(self):
        with self.say("這是冰島。", en="optional English line"):
            ...
```
- `self.say(text, en=None)`: ≤ ~40 characters per block (two caption lines of 22). Give
  `en=` only for a tricky term or a quote, 2–4 times per video.
- Pinyin shows over words above HSK 4, first 2 uses per scene (`pinyin_repeats`).
- Ink look: colours from `theme` (ink theme: FG ink, RED seal, BLUE/ICE washes), font
  `T.BODY_FONT` (WenKai). Real maps with `geo.Projector` + `geo.ink_shape`. All cs-video
  templates and effects work. Keep content above y ≈ −1.9 (captions are taller in Chinese).
- Images in Manim need Pillow < 12 (setup pins it) and RGBA PNGs.

Render, check, fix (same loop as cs-video):
```bash
PY scripts/render_video.py topics/<slug>/video.py --draft
PY ../cs-video/scripts/frames.py topics/<slug>/build/<slug>_draft.mp4 --every 3   # read every sheet
PY scripts/render_video.py topics/<slug>/video.py -q m                             # narrated 720p
```
The narrated render takes ~4–5 min per minute of video; run it in the background.

## 5. Deliver

Send the MP4 and the EPUB (copy it to a Chinese file name, e.g. `冰島的冰川.epub`) with a
one-line summary each. Commit `research.md`, `book.txt`, `storyboard.md`, `video.py`,
`geo.json` (not `build/` or `backdrop.png`, which is regenerated) and push.

## Voices

Default: **Kokoro v1.1-zh** (Mandarin-trained) via sherpa-onnx, male voice `zm_015`
(`CSVIDEO_ZH_SPEAKER=64`), **10% slower** (`CSVIDEO_ZH_SPEED=0.9`), with short pauses
inserted at Chinese punctuation (comma ≈ 0.22 s, full stop ≈ 0.45 s; `PAUSES` in
`zhkit/voice_zh.py`). Female: speaker 3 (`zf_001`), 47 (`zf_083`), 55 (`zf_093`); other
male: 60 (`zm_011`). Fallback: `CSVIDEO_ZH_ENGINE=kokoro10` (Kokoro v1.0 + misaki).
Write numbers like 一〇一 freely; the voice reads 〇 as 零.
