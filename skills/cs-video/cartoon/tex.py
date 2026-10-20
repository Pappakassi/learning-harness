#!/usr/bin/env python3
"""Render LaTeX formulas to SVG files a cartoon can draw (Studio.loadImage + K.math).

  ../../.venv/bin/python ../../cartoon/tex.py tex.json      (run inside the cartoon project)

tex.json: {"name": "latex body", ...}. Writes assets/tex/<name>.svg plus assets/tex/index.js
(UMD global TEX = {name: {w, h}} in pt, for layout). Colours: \\color{F} (orange), \\color{G} (blue),
\\color{R} (red), \\color{K} (green), or any xcolor name / HTML.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PRE = r"""\documentclass[preview,border=1pt]{standalone}
\usepackage{amsmath,amssymb}
\usepackage[dvipsnames]{xcolor}
\definecolor{F}{HTML}{D9622B}\definecolor{G}{HTML}{2F7FB5}\definecolor{R}{HTML}{C9352B}\definecolor{K}{HTML}{3E9A4A}
\definecolor{I}{HTML}{1F1B17}
\begin{document}\color{I}$\displaystyle %s$\end{document}
"""


def main():
    spec = Path(sys.argv[1] if len(sys.argv) > 1 else "tex.json")
    items = json.loads(spec.read_text())
    out = (spec.parent / "assets" / "tex").resolve()
    out.mkdir(parents=True, exist_ok=True)
    sizes = {}
    with tempfile.TemporaryDirectory() as td:
        for name, body in items.items():
            (Path(td) / f"{name}.tex").write_text(PRE % body)
            subprocess.run(["latex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"], cwd=td,
                           check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", str(out / f"{name}.svg"), f"{name}.dvi"],
                           cwd=td, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            svg = (out / f"{name}.svg").read_text()
            m = re.search(r"width='([\d.]+)pt' height='([\d.]+)pt'", svg)
            sizes[name] = {"w": float(m.group(1)), "h": float(m.group(2))}
            print(f"{name:10s} {sizes[name]['w']:7.1f} x {sizes[name]['h']:5.1f} pt")
    (out / "index.js").write_text("(function () { const TEX = " + json.dumps(sizes) +
                                  "; if (typeof module !== 'undefined') module.exports = TEX; else globalThis.TEX = TEX; })();\n")


if __name__ == "__main__":
    main()
