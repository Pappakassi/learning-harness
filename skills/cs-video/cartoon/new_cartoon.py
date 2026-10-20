#!/usr/bin/env python3
"""Scaffold a cartoon explainer project: the animation-studio engine + the cs-video cartoon kit.

  .venv/bin/python cartoon/new_cartoon.py <project-dir> [--lang en|zh]

Needs the animation-studio plugin (its engine is copied into the project) and Node.js.
Set ANIMATION_STUDIO=<path to the animation-studio skill folder> if it isn't found automatically.
"""
import argparse
import glob
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[1]  # .../skills


def find_studio():
    env = os.environ.get("ANIMATION_STUDIO")
    if env and Path(env, "scripts", "new-project.js").exists():
        return Path(env)
    pats = ["~/.claude/plugins/**/skills/animation-studio", "/root/.claude/plugins/**/skills/animation-studio",
            "~/.claude/skills/animation-studio"]
    for p in pats:
        for m in glob.glob(os.path.expanduser(p), recursive=True):
            if Path(m, "scripts", "new-project.js").exists():
                return Path(m)
    raise SystemExit("animation-studio not found: install the plugin or set ANIMATION_STUDIO=<its skill folder>")


def patch_chars(path: Path):
    """Coloured irises (style.eyeColor) for the engine's people. Idempotent."""
    s = path.read_text()
    if "st.eyeColor" in s:
        return
    a = """        ctx.fillStyle = C.ink;
        ctx.beginPath(); ctx.ellipse(cx, cy, w / 2, Math.max(1.5, h / 2), 0, 0, Math.PI * 2); ctx.fill();"""
    b = a + """
        if (st.eyeColor && h > 6) {
          ctx.fillStyle = st.eyeColor; ctx.beginPath(); ctx.ellipse(cx, cy, w / 2 - 1.5, h / 2 - 1.5, 0, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(cx, cy + 1, w * 0.2, 0, Math.PI * 2); ctx.fill();
        }"""
    if a in s:
        path.write_text(s.replace(a, b))
    else:
        print("note: chars.js changed upstream; eyeColor not patched (everything else works)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--lang", default="en", choices=["en", "zh"])
    a = ap.parse_args()
    dest = Path(a.dir).resolve()
    studio = find_studio()
    # new-project.js exits non-zero when it can't find Chrome (a warning here: set CHROME_PATH before rendering)
    subprocess.run(["node", str(studio / "scripts" / "new-project.js"), str(dest)])
    if not (dest / "engine" / "video" / "chars.js").exists():
        raise SystemExit("scaffolding failed: no engine copied")
    # replace the starter film with the cartoon template
    for f in ["film.js", "score.js", "song.js", "index.html"]:
        shutil.copy(HERE / "template" / f, dest / f)
    shutil.copy(HERE / "kit.js", dest / "kit.js")
    nar = (HERE / "template" / "narration.py").read_text().replace("__SKILLS__", str(SKILLS)).replace("__LANG__", a.lang)
    (dest / "narration.py").write_text(nar)
    patch_chars(dest / "engine" / "video" / "chars.js")
    (dest / "out").mkdir(exist_ok=True)
    py = SKILLS / "cs-video" / ".venv" / "bin" / "python"
    print(f"""
cartoon project ready: {dest}
  1. edit LINES in narration.py, then:  {py} narration.py
  2. edit score.js (moments) and film.js (scenes); preview:  node engine/render.js board
  3. sound + video:  node song.js && node engine/render.js video && node engine/render.js mux
     phone version:  node engine/render.js video --format 9:16 && node engine/render.js mux --format 9:16
  (headless Chrome must run without sandbox in a container: export CHROME_PATH=<wrapper with --no-sandbox>)
""")


if __name__ == "__main__":
    main()
