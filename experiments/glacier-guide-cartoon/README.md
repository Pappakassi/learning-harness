# Cartoon test: a glacier guide (Mandarin)

38-second cartoon made with the **animation-studio** skill's engine plus zh-topic's Mandarin
voices and caption tools: a guide greets a group on Vatnajökull, a tourist asks why the ice
is blue, light rays explain it, and everyone walks off across the ice.

Rebuild:
1. Scaffold the engine: `node <animation-studio>/scripts/new-project.js glacier-guide-cartoon`,
   then copy these files over the scaffold's (and `skills/zh-topic/fonts/LXGWWenKaiTC-Medium.ttf`
   into `assets/`).
2. `../skills/cs-video/.venv/bin/python narration.py`  (dialogue audio, lip-sync track, captions → vo.js)
3. `node song.js && node engine/render.js video && node engine/render.js mux`
   (as root in a container: `CHROME_PATH` pointing to Chromium with `--no-sandbox`).

The finished video is attached to the repo's "Videos" release.
