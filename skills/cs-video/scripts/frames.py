#!/usr/bin/env python3
"""Pull frames out of a rendered video so they can be looked at.

    python scripts/frames.py build/video.mp4                 # contact sheets, 1 frame / 2s
    python scripts/frames.py build/video.mp4 --every 1
    python scripts/frames.py build/video.mp4 --at 12.5 40    # single frames at timestamps

Contact sheets are 4x3 grids, each tile labelled with its timestamp, saved to
<video dir>/frames/. Look at every sheet before calling a video finished.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--every", type=float, default=2.0, help="seconds between sampled frames")
    ap.add_argument("--at", type=float, nargs="*", help="exact timestamps instead of sheets")
    ap.add_argument("--width", type=int, default=480, help="tile width in pixels")
    args = ap.parse_args()

    out = args.video.parent / "frames"
    out.mkdir(exist_ok=True)

    if args.at:
        for t in args.at:
            dst = out / f"{args.video.stem}_t{t:06.1f}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i",
                            str(args.video), "-frames:v", "1", str(dst)], check=True)
            print(dst)
        return

    for old in out.glob(f"{args.video.stem}_sheet_*.png"):
        old.unlink()
    label = ("drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=22:fontcolor=white:"
             "box=1:boxcolor=black@0.6:boxborderw=4")
    vf = f"fps=1/{args.every},{label},scale={args.width}:-1,tile=4x3:padding=4:color=gray"
    pattern = out / f"{args.video.stem}_sheet_%02d.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(args.video),
                    "-vf", vf, "-vsync", "vfr", str(pattern)], check=True)
    for p in sorted(out.glob(f"{args.video.stem}_sheet_*.png")):
        print(p)


if __name__ == "__main__":
    main()
