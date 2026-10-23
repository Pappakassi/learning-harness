#!/usr/bin/env python3
"""Lay a music bed under a finished video, ducked under the voice.

    python scripts/add_music.py build/x_1080p30.mp4 --bed music/out/bed.wav --start 16 --end-trim 6 -o out.mp4

--start      seconds before the bed starts (e.g. after a theme intro that is already in the video)
--end-trim   seconds before the end where the bed stops (e.g. an outro sting already in the video)
--level      bed volume (default 0.22); it is ducked further while someone speaks
"""
import argparse
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--bed", required=True)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end-trim", type=float, default=0.0)
    ap.add_argument("--level", type=float, default=0.22)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                               capture_output=True, text=True).stdout)
    length = max(0.1, dur - a.start - a.end_trim)
    ms = int(a.start * 1000)
    fc = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{length:.2f},afade=t=in:d=1.5,afade=t=out:st={max(0, length - 2):.2f}:d=2,"
          f"aresample=48000,volume={a.level},adelay={ms}|{ms},apad[bed];"
          f"[0:a]aresample=48000,asplit=2[v][key];"
          f"[bed][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[ducked];"
          f"[v][ducked]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-i", a.bed, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    a.out], check=True)
    print(f"music added: {a.out}")


if __name__ == "__main__":
    main()
