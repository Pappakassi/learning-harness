---
name: cs-video
description: Make a narrated explainer video from a topic prompt, delivered as MP4. Two styles - Manim diagrams for algorithms, data structures and CS concepts ("make a video explaining quicksort partitioning"), or a hand-drawn cartoon with talking characters, lip-sync, signs and captions ("make a cartoon video explaining X"), in English or Mandarin, wide 16:9 and phone 9:16.
---

# CS explainer videos

Two styles. **Manim** (sections 1–6): diagrams, arrays, graphs, code; the default for
algorithms and data structures. **Cartoon** (section 7): drawn characters who talk
(lip-synced), props and pop-up signs, captions; for stories, procedures, briefings,
"explain it like a conversation" topics, or whenever the user asks for a cartoon.

Turns a topic into a 1–4 minute narrated, captioned explainer video. The video is
built from tested templates in `csvideo/` (arrays, pointers, code panels...), voiced
offline with Kokoro TTS, and checked frame by frame before it is delivered.

Everything below is relative to this skill folder (`skills/cs-video/`).

## 0. Get the code and set up (once per session/machine)

The code lives in the GitHub repo **Pappakassi/learning-harness**, folder `skills/cs-video/`.
If `skills/cs-video/csvideo/` isn't already on disk:

1. Attach the repo (in Claude's cloud workspace: the add-repo tool with owner
   `Pappakassi`, repo `learning-harness`, push access), then
   `git clone --depth 1 https://github.com/Pappakassi/learning-harness ~/learning-harness`.
2. `cd ~/learning-harness/skills/cs-video`

Then:
```bash
bash setup.sh          # venv, Python packages, narration voices
```
If setup reports missing system tools, install them with the printed command
(in a Linux workspace: `apt-get install -y ffmpeg texlive texlive-latex-extra dvisvgm sox libpango1.0-dev pkg-config`)
and run it again. Use `.venv/bin/python` for every script.

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
- **Hook, your-turn moment and teaser** (see *Make it engaging* below): write each
  one down in the storyboard before writing any code.

### Make it engaging (from research on instructional video)

Sources: Guo, Kim & Rubin 2014 (edX engagement study), Mayer's multimedia learning
principles, Grant Sanderson (3Blue1Brown) on visuals and story.

1. **Hook in the first ~10 seconds.** Open on the puzzle, not a title card: show the
   situation and ask the question the video answers ("B has never seen F, yet in a
   minute it'll know the cheapest route to it. How?"). Title card after the hook.
2. **Keep it short and segmented.** Shorter videos hold attention better. Aim for 2–4
   minutes; split into chapters with a clear visual change between them (new title,
   new layout). If a topic needs more, make a series.
3. **Picture first, then the rule.** Show the mechanism working on the example
   *before* the formula or definition appears; then name it ("that's all
   Bellman–Ford says"). The formula should feel like a summary of what was seen.
4. **Turn numbers into things you can see.** Costs become lengths (race bars),
   load becomes a gauge, traffic becomes a swarm. Avoid screens of text and
   tables-only scenes; free-form drawn visuals beat slide-like layouts.
5. **A "your turn" moment.** At least once, pose a question on screen, start a
   `Countdown`, stay silent for 3 seconds, then reveal. Let the viewer predict.
6. **Signal where to look.** Highlight the one thing being talked about and dim the
   rest; animate exactly when the narration mentions it. Don't put extra text on
   screen that repeats the narration (captions already do that).
7. **Conversational voice.** "You", "we", short sentences, a bit of energy; no
   lecture tone. Keep the pace brisk (`CSVIDEO_SPEED=1.05` is fine).
8. **Story arc.** Problem → struggle or misconception → payoff. Give the climax a
   moment (glow, burst, all routes lighting up).
9. **Change something every ~10–20 seconds** (new motion, zoom, colour, layout) so
   the screen never sits still through long narration.
10. **End with a teaser**, not just a recap: one line on what goes wrong next or what
    to learn next, with a quick visual hint.

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
| `Card(heading, body, color, width, min_height)` | options / fixes side by side; use `"\n"` in body; same `min_height` for a row | — (warns if text had to shrink) |
| `NetTree({child: parent}, kinds={...}, notes={...})` | networks laid out top-down (sender / router / host) | `send(src, dsts, label)`, `gather(srcs, dst, "ACK")` → `(packets, anim)`; `tree["A"].flash(color)`, `.reset()`, `link(a, b)`, `path(a, b)` |
| `NetNode(name, kind)` | a single host / router / sender | `flash(color)`, `reset()`, `set_note(text)` |
| `Packet(label, color)` | a packet in flight | `travel(points)` (one hop per time slice; hidden until it starts) |
| `NetGraph({name: (x, y)}, {(a, b): cost}, kinds=, colors=, dashed=)` | weighted graphs with cost labels (routing, shortest paths) | `edge(a, b)`, `cost(a, b)`, `highlight_edge(a, b, color)`, `g["A"]` |
| `GridView(values, row_labels=, col_labels=, row_colors=)` | tables: distance vectors, routing tables, DP tables | `highlight_col(c)`, `highlight_cell(r, c)`, `target_text(r, c, v)` + `put(r, c, mob)`, `set_text(r, c, v)` |
| `Chip(text, color)` | small pill: a candidate sum, a tag like "+4" | `win()`, `lose()` |
| `Bubble(text, color, tail=)` | a node "saying" something (gossip, claims) | — |

Examples: network templates in `videos/reliable_multicast/video.py`; graph + tables in `videos/distance_vector/video.py`.

**Effects** (`csvideo/effects.py`): use these to make scenes feel alive, not like slides.

| Effect | Use |
|---|---|
| `Swarm(sources, target, colors=..., n=)` | many particles streaming to one point (traffic, floods); `.start()`, `.set_intensity(v)`, `.stop()` |
| `Gauge(label)` | dial that reacts to load; `gauge.to(0.9)`, values > 1 overload into red |
| `CountUp(label, value)` | smoothly counting number; `.to(10_000, log=True)` for big jumps |
| `glow(mob, color)` | soft halo behind a mobject (`FadeIn` it; don't set_opacity) |
| `shake(mob)` | jitter for overload / error moments |
| `scatter_ring(center, rx, ry, n)` | points for a crowd of hosts around a center |
| `RaceBars(rows, origin=, unit=)` | compare totals as bars racing at equal speed; shortest finishes first. `to(v)`, `best_total()`, `crown()`, `max_total()` |
| `Countdown(3)` | "your turn" pause: ring empties, `run()` (play it outside a `say()` block = silence) |

Style examples: `videos/reliable_multicast/creative_sample.py` (zoom-out, swarm, overload) and
`videos/distance_vector/video.py` (hook, gossip bubbles, route races, your-turn countdown, teaser).
Prefer this kind of motion (zooming out to show scale, things streaming, meters
reacting) over static boxes appearing one by one.

**Colour**: the default style (`theme.COLORFUL = True`) gives a gradient backdrop,
gradient titles, and a per-item colour from `T.PALETTE` (hosts and their packets
share a colour). Give crowds and series palette colours; keep meaning colours
(green = ok, red = problem, yellow = current) for state.

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
- Objects in front of a `Swarm` or `glow`: give them `set_z_index(10)` so they stay on top.
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
`video.py` (not `build/`, which is git-ignored) and push to the repo.

## Voices

Default: **Kokoro** (offline, natural-sounding), voice `af_heart`. Change with env vars:
- `CSVIDEO_KOKORO_VOICE=am_michael` (also `bf_emma`, `am_fenrir`, ...)
- `CSVIDEO_SPEED=0.95` (slower) / `1.1` (faster)
- `CSVIDEO_TTS=piper` switches to the smaller, more robotic Piper fallback.

Changing the text, voice or speed re-generates that line's audio; unchanged lines
come from cache.

## 7. Cartoon style

Characters drawn in code (the animation-studio engine), voiced per speaker, with
lip-sync, pop-up signs, captions with an optional second-language line, and one
`film.js` that renders both **16:9** and **9:16 (phone)**. Needs the
**animation-studio** plugin (its engine is copied into each project), Node 22+ and Chrome.

```bash
.venv/bin/python cartoon/new_cartoon.py videos/<slug>_cartoon --lang en    # or --lang zh
cd videos/<slug>_cartoon
```
The project starts as a working 25-second demo (a teacher shows binary search on a whiteboard).
Replace it step by step:

1. **Script** in `narration.py` `LINES`: `(id, pause_before, speaker, [(spoken, caption_or_None, second_caption), ...])`.
   One sentence = one caption (≤ 2 lines). The second caption is optional (e.g. English under Chinese).
   Voices: `VOICES` per speaker (English Kokoro names like `am_michael`, `af_heart`; Chinese
   sherpa speaker ids, 64 = male zm_015, 3 = female zf_001), `SPEED` per speaker (1.0 = normal).
   Spoken text can differ from the caption (spell numbers out, fix a pronunciation).
   Run `../../.venv/bin/python narration.py` → `out/narration.wav`, `vo.js`.
2. **Moments** in `score.js` `ev`: named times from the dialogue, `L.<id>.t` (line start),
   `ph(id, k)` (phrase k: lines are split at punctuation), `sent(id, k)` (sentence k).
   Every visual is timed to these, so re-recording the voice keeps everything in sync.
3. **Scenes** in `film.js`, a pure function of `t` on a **1920×1080 stage**:
   - `K.actor(ctx, style, x, y, scale, t, { role, gesture, look, eyes, brows, walk, helmet, ... })` -
     a person (`Ch.person` styles: skin, hair, hairStyle, outfit, shirt, glasses, headwear, `eyeColor`);
     `role` = the speaker id whose lines move its mouth. Gestures: wave, point, pointUp, thumbsUp,
     think, cheer, shrug, clap... `walk` = cycle phase for a walking pose.
   - `K.card(ctx, t, t0, t1, x, y, w, h, inner)` - a pop-up sign; `K.title(ctx, t, t0, t1, main, sub)`.
   - Draw props with `G.*` (rrect, ellipse, poly, line, text, tornPaper, star...) - hand-drawn look.
   - Shots and transitions with `Shots.film([...])` (fade, wipe, whip, iris, paper...).
4. **Phone version**: `K.frame(ctx, t, film, FOCUS)` crops the stage to the middle band with the
   camera at `FOCUS` (`[time, x, cut?]` keys, eases between), sends every card/title to the top band
   and makes captions bigger at the bottom. The phone shows ≈ **850 stage px** across: keep each
   moment's important things within that width, or use `K.VERT` to lay out tighter for 9:16.
5. **Sound** in `song.js` (pad, pops, whooshes, footsteps from `engine/audio/instruments`), ducked under the voice.

Check, render, deliver:
```bash
export CHROME_PATH=<chrome>        # in a container: a wrapper script that adds --no-sandbox
node engine/render.js board <t1> <t2> ...                  # storyboard of chosen times; read it
node engine/render.js board <t1> ... --format 9:16         # the phone layout
node song.js
node engine/render.js video && node engine/render.js mux   # out/<folder>.mp4 (~4 min per minute of film)
node engine/render.js video --format 9:16 && node engine/render.js mux --format 9:16   # out/<folder>-9x16.mp4
node engine/render.js check                                # contact sheet + loudness
```
For a phone-first audience deliver the 9:16 file first. A full worked example (Mandarin,
English second captions, logo, helmets, walking group, cave): `experiments/blue-iceland-ice-cave-intro/`.

## 8. Hybrid: cartoon cold open + Manim body (a series)

For a YouTube-style series, open each episode with a 30–40 s cartoon scene (recurring characters
hit the problem in everyday life and ask the question), then cut to the Manim explanation.
`videos/tsam_series/` is a worked example (six TSAM computer-networks episodes):

- `make_open.sh <episode-dir>` scaffolds `<episode-dir>/open/` (cartoon engine + shared `props.js`
  cast and props, a generic `score.js` where every line id becomes `ev.<id>`, a `song.js` that reads
  pops/whooshes from `sfx.json`). Write the dialogue in `open/lines.py`, the scene in `open/film.js`.
- Render the body at 1080p30 with `render.py video.py -q f` (half the time of `-q h`).
- `assemble.sh <episode-dir> <out.mp4>` loudness-matches both parts and joins them into one 1080p30 MP4.
- On a 2-core machine run renders one at a time (a cartoon open takes ~10–15 min, a 4-min body ~25 min).

## 9. StoryScene: 3Blue1Brown-style videos with Hr. Schiffel (preferred for new videos)

`csvideo/story.py` + `csvideo/story_kit.py` + `csvideo/mascot.py`. Near-black background, a few fixed colours (`P`),
thin captions without boxes (also exported as an `.srt` next to the MP4), a moving camera, and the series mascot,
**Hr. Schiffel**: a fierce little gnome (red hat with a `</>` badge, rectangular glasses, beard below the chin) who
reacts, speaks in his own gnome voice, and sings the theme. Examples: `videos/email_under_the_hood/`, `videos/ssh_under_the_hood/`.

```python
from csvideo.story import StoryScene, P, txt, theme_intro, theme_outro
from csvideo.story_kit import Server, Laptop, Envelope, Key, Padlock, Terminal, ByteRow, pulse, trail_dot
class Intro(StoryScene):
    def construct(self):
        theme_intro(self, "How email works", "subtitle")      # ~16 s sung theme; leaves the gnome bottom-right
class Smtp(StoryScene):
    def construct(self):
        self.chapter("3. The SMTP conversation", label="3  SMTP")   # big title, shrinks to a corner label
        g = self.add_gnome("fierce")                          # pinned to the screen corner (survives camera moves)
        with self.say("Narration ..."): ...
        with self.say("Ach! Just text!", who="gnome"): self.play(g.change("angry"))   # his voice, mouth moves
        self.play(self.zoom_to(thing)); self.play(self.zoom_reset())
        theme_outro(self)                                     # last scene: outro sting + "Tschüss!"
```

- Mascot API: moods `fierce | angry | thinking | surprised | lecturing | happy`; `g.change(mood, look=..., point="left")`,
  `g.look_at(mob)`, `g.blink()`, `g.hop()`, `self.gnome_says("text")` (bubble, no voice).
- Kit: `Terminal.type(line, who="C"|"S")` for protocol transcripts, `pulse(wire)` for signals, `trail_dot(points)`,
  `Envelope`, `Key`, `Padlock(...).close()`, `Server`, `Laptop`, `ByteRow`.
- Gnome voice: Kokoro `bm_george` pitched up (`CSVIDEO_GNOME_VOICE`, `CSVIDEO_GNOME_PITCH`, `CSVIDEO_GNOME_SPEED`).
- Music: `node music/gnome_theme.js` makes `music/out/theme_intro.wav`, `bed.wav`, `outro.wav` (a gnome polka; the
  intro has a sung chorus). After the final render add the bed under the narration:
  `python scripts/add_music.py build/<x>_1080p30.mp4 --bed music/out/bed.wav --start 16.5 --end-trim 7 -o out.mp4`.
- Render with `-q f` (1080p30). Layout checks are skipped while the camera is zoomed; check those frames by eye.
- Style rules: one idea per screen; morph and move things instead of fading screens of text; let the gnome react
  once or twice per chapter (short lines, a joke or a warning), never to repeat the narration.

