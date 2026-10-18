# learning-harness

A personal AI pipeline for studying Chinese and computer science: turning
material into custom explainer videos, books and other study formats.

## Skills

| Skill | What it does |
|---|---|
| [`skills/cs-video`](skills/cs-video/SKILL.md) | Narrated, captioned CS explainer videos from a topic prompt (Manim + Kokoro TTS) |

Planned: epub book generation, Chinese-language video formats.

## Quick start (cs-video)

```bash
cd skills/cs-video
bash setup.sh
cd examples/binary_search
../../.venv/bin/python ../../scripts/render.py video.py -q m
```
The video lands in `examples/binary_search/build/`.
