#!/usr/bin/env python3
"""Render a zh-topic video with the cs-video pipeline (ink theme, Mandarin voice).

    python scripts/render_video.py topics/<slug>/video.py --draft
    python scripts/render_video.py topics/<slug>/video.py -q m
Any extra args are passed to cs-video's render.py.
"""
import os
import subprocess
import sys
from pathlib import Path

ZH = Path(__file__).resolve().parent.parent
CS = ZH.parent / "cs-video"

if __name__ == "__main__":
    env = {**os.environ, "PYTHONPATH": f"{ZH}{os.pathsep}{os.environ.get('PYTHONPATH', '')}",
           "CSVIDEO_THEME": "ink"}
    py = CS / ".venv" / "bin" / "python"
    sys.exit(subprocess.run([str(py), str(CS / "scripts" / "render.py"), *sys.argv[1:]], env=env).returncode)
