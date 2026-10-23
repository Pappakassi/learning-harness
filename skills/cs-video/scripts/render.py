#!/usr/bin/env python3
"""Render every scene of a video file and stitch them into one MP4.

    python scripts/render.py path/to/video.py --draft          # fast, silent, 480p
    python scripts/render.py path/to/video.py -q h             # final, narrated, 1080p
    python scripts/render.py path/to/video.py --scenes Intro   # just one scene

The video file must define SCENES = ["Intro", "Idea", ...] in play order.
Output goes to <video dir>/build/. The layout report is printed at the end.
"""
from __future__ import annotations

import argparse
import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
QUALITY = {"l": (["-ql"], "480p15"), "m": (["-qm"], "720p30"), "h": (["-qh"], "1080p60"),
           "f": (["-qh", "--frame_rate", "30"], "1080p30")}   # f: 1080p at 30 fps (half the render time of h)


def read_scenes(video: Path) -> list[str]:
    tree = ast.parse(video.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SCENES" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    sys.exit(f"{video} has no SCENES = [...] list")


def manim_exe() -> list[str]:
    local = Path(sys.executable).parent / "manim"
    return [str(local)] if local.exists() else [sys.executable, "-m", "manim"]


def stitch(parts: list[Path], out: Path):
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)],
                   check=True)
    lst.unlink()


def _shift(ts: str, off: float) -> str:
    h, m, rest = ts.split(":")
    sec, ms = rest.split(",")
    t = int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000 + off
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)) % 1000:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("-q", "--quality", choices=QUALITY, default="m")
    ap.add_argument("--draft", action="store_true", help="silent audio, 480p")
    ap.add_argument("--scenes", nargs="*", help="only these scenes (no stitching)")
    args = ap.parse_args()

    video = args.video.resolve()
    build = video.parent / "build"
    build.mkdir(exist_ok=True)
    quality = "l" if args.draft else args.quality
    flag, res = QUALITY[quality]
    scenes = args.scenes or read_scenes(video)

    report = build / "layout_report.txt"
    report.unlink(missing_ok=True)
    env = {**os.environ,
           "PYTHONPATH": f"{SKILL_DIR}{os.pathsep}{os.environ.get('PYTHONPATH', '')}",
           "CSVIDEO_REPORT": str(report)}
    if args.draft:
        env["CSVIDEO_DRAFT"] = "1"

    media = build / ("media_draft" if args.draft else "media")
    cmd = manim_exe() + [*flag, "--media_dir", str(media), "--progress_bar", "none",
                         "-v", "ERROR", str(video), *scenes]
    print("Rendering:", ", ".join(scenes))
    r = subprocess.run(cmd, env=env, cwd=video.parent)
    if r.returncode != 0:
        sys.exit("Render failed (see traceback above).")

    parts = [media / "videos" / video.stem / res / f"{s}.mp4" for s in scenes]
    missing = [p for p in parts if not p.exists()]
    if missing:
        sys.exit(f"Missing outputs: {missing}")

    if args.scenes:
        out_files = parts
    else:
        suffix = "draft" if args.draft else res
        name = video.parent.name if video.stem == "video" else f"{video.parent.name}_{video.stem}"
        out = build / f"{name}_{suffix}.mp4"
        stitch(parts, out)
        out_files = [out]
        # subtitles: manim-voiceover writes one .srt per scene; join them with time offsets
        srt_lines, offset, idx = [], 0.0, 1
        for part in parts:
            srt = part.with_suffix(".srt")
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                      "-of", "csv=p=0", str(part)], capture_output=True, text=True).stdout or 0)
            if srt.exists():
                for block in srt.read_text().strip().split("\n\n"):
                    rows = block.strip().splitlines()
                    if len(rows) >= 3 and "-->" in rows[1]:
                        a, b = [x.strip() for x in rows[1].split("-->")]
                        srt_lines.append(f"{idx}\n{_shift(a, offset)} --> {_shift(b, offset)}\n" + "\n".join(rows[2:]) + "\n")
                        idx += 1
            offset += d
        if srt_lines:
            out.with_suffix(".srt").write_text("\n".join(srt_lines))

    for f in out_files:
        dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip()
        print(f"Output: {f}  ({float(dur):.1f}s)")

    if report.exists() and report.read_text().strip():
        print("\nLAYOUT WARNINGS:\n" + report.read_text())
    else:
        print("\nLayout check: no warnings.")


if __name__ == "__main__":
    main()
