---
name: cs-video
description: Make a narrated computer-science explainer video (Manim animation + offline voice + captions) from a topic prompt, e.g. "make a video explaining quicksort partitioning". Use for algorithm, data-structure and CS-concept explainers delivered as MP4.
---

# CS explainer videos

Turns a topic into a 1–4 minute narrated, captioned explainer video. The video is
built from tested templates in `csvideo/` (arrays, pointers, code panels...), voiced
offline with Piper TTS, and checked frame by frame before it is delivered.

Everything below is relative to this skill folder (`skills/cs-video/`).

## 0. Setup (once per machine)

```bash
bash setup.sh          # venv, Python packages, narration voice
```
Use `.venv/bin/python` for every script. If setup reports missing system tools,
install them with the printed command first.

## 1. Storyboard first

Create `videos/<topic_slug>/storyboard.md` (copy the shape of
`examples/binary_search/storyboard.md`):

- **Learning goal**: one sentence: what the viewer can *do* afterwards.
- **Format**: pick the one that fits the topic best, and vary it between videos.
  Never default to the same shape every time.
  - *problem → key idea → trace → why → recap* (algorithms)
  - *misconception first*: show the wrong approach failing, then fix it
  - *build it up*: start from the dumbest version, improve step by step
  - *compare two*: same input through A and B side by side
  - *one question, many angles*: a puzzle answered three ways
- **Running example**: one small concrete input reused across scenes. Work out
  every step of the trace by hand in the storyboard, including the values,
  indices and pointer moves, so the animation can't drift from the real algorithm.
- **Scene table**: 3–6 scenes, each with what is on screen + gist of narration.
- **One misconception** to address explicitly.

## 2. Write `videos/<topic_slug>/video.py`

```python
from manim import *
from csvideo import ArrayView, Pointers, CodePanel, Counter, BulletList, Callout, CSScene, make_text
from csvideo import theme as T

SCENES = ["Intro", "Trace", "Recap"]       # play order, required by render.py

class Intro(CSScene):
    def construct(self):
        self.show_title("Quicksort")
        arr = ArrayView([5, 2, 9, 1]).move_to(UP * 0.4)
        with self.say("Here are four unsorted numbers.") as t:   # voice + caption
            self.play(FadeIn(arr), run_time=1)
```

**Templates** (`csvideo/templates.py`). Methods *return animations*; pass them to `self.play`:

| Template | Use | Key methods |
|---|---|---|
| `ArrayView(values, max_width=)` | arrays, lists | `highlight(i, color)`, `unhighlight(i)`, `mark(i)`, `set_active_range(lo, hi, reset_outside=True)`, `cell(i)`, `anchor_below(i)` |
| `Pointers(arr, {"lo":0,"hi":9})` | index pointers; same-index pointers stack automatically | `move(lo=5, mid=None)` (None hides one) |
| `CodePanel(code, max_width=)` | code with line highlight (0-indexed lines) | `highlight(k, color)`, `clear_highlight()` |
| `Counter("checks", 0, fmt="{:,}")` | step / comparison counts | `set(n)` |
| `BulletList([...])` | recap points | `reveal(i)` |
| `Callout(text, color)` | the key sentence of a scene | — |

**Scene helpers** (`CSScene`): `show_title(text)`, `say(text)` (context manager, yields
a tracker with `.duration`), `clear_content()`, `make_text(s, size, color)`.

If a topic needs a structure no template covers (tree, graph, stack, hash table,
linked list...), **add a new template to `templates.py`** following the same pattern
(VGroup subclass, `layout_name`, methods return animations), test it in isolation, and
then use it. Don't hand-draw one-off structures inside a scene.

### Rules that keep videos good
- **Narration**: one `say()` block = 1–2 sentences (≤ ~30 words) so captions stay
  ≤ 2 lines. Spell out numbers the way they should be spoken ("thirty-one").
  Talk to the viewer plainly, with no filler or hype.
- **Timing**: animations inside a `say()` block should fit in its speech
  (use `t.duration`); the block waits for speech to end anyway.
- **Layout zones** (`theme.py`): titles at the top, content between
  `T.CONTENT_TOP` and `T.CONTENT_BOTTOM`, captions below. Side-by-side layouts:
  left content centered near x = −3.5, right near x = +3.6, each ≤ 6.7 wide.
- **Never animate the same mobject twice in one `play()`** (e.g. `unhighlight(4)`
  together with `set_active_range(...)` touching cell 4); the second animation wins
  partially and leaves visual residue.
- Use `Text` for words (Inter font) and `MathTex` only for real formulas.
- Colors come from `theme.py` only. Meaning stays consistent: yellow = currently
  looked at, green = success/found, red = discarded, blue/orange = pointers.
- Manim 0.22 API: `Create` (not `ShowCreation`), `self.play(mob.animate.x())`.

## 3. Draft render (fast, silent, 480p)

```bash
cd videos/<topic_slug>
../../.venv/bin/python ../../scripts/render.py video.py --draft
```
Fix any traceback. The script prints **LAYOUT WARNINGS** (something off-screen,
overlapping the title, or covering captions). Fix every one.

## 4. Look at the frames (required)

```bash
../../.venv/bin/python ../../scripts/frames.py build/<topic_slug>_draft.mp4 --every 3
```
Read **every** contact sheet in `build/frames/`. Check for: leftover highlights or
outlines, overlapping labels, text too small to read, empty screens during long
narration, visuals that don't match the narration, wrong values in the trace.
Zoom with `--at <seconds>` for a full-size frame. Fix, re-render, re-check.
Mid-morph frames of a changing number look garbled; that's expected.

## 5. Final render

```bash
../../.venv/bin/python ../../scripts/render.py video.py -q m    # 720p (≈1 min render per min of video)
../../.venv/bin/python ../../scripts/render.py video.py -q h    # 1080p60, slower
```
The narrated version is usually shorter than the draft estimate. Spot-check 2–3
frames again, and run `ffmpeg -i <mp4> -af silencedetect=n=-40dB:d=2.5 -f null -`
to catch dead air. Short pauses at scene changes are fine.

## 6. Deliver

Send the MP4 from `build/` with a one-line summary. Commit `storyboard.md` and
`video.py` (not `build/`, which is git-ignored).

## Voices

Default: `voices/en-us-lessac-medium.onnx` (Piper, offline). Any Piper `.onnx`
voice works; set `CSVIDEO_VOICE=/path/to/voice.onnx`. Changing the voice text or
model re-generates audio; unchanged lines come from cache.
