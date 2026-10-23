#!/bin/bash
# assemble.sh <episode-dir> <output.mp4> : cartoon cold open + Manim body -> one 1080p30 MP4, both parts loudness-matched.
set -e
EP="$(cd "$1" && pwd)"; OUT="$2"
OPEN="$EP/open/out/open.mp4"
BODY="$(ls "$EP"/build/*_1080p30.mp4 | head -1)"
TMP="$(mktemp -d)"
norm() { ffmpeg -y -loglevel error -i "$1" -vf "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setsar=1" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -ac 2 -c:v libx264 -crf 19 -preset medium -c:a aac -b:a 192k "$2"; }
norm "$OPEN" "$TMP/a.mp4"
norm "$BODY" "$TMP/b.mp4"
printf "file '%s'\nfile '%s'\n" "$TMP/a.mp4" "$TMP/b.mp4" > "$TMP/list.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/list.txt" -c copy -movflags +faststart "$OUT"
rm -rf "$TMP"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | xargs printf "assembled %s (%.1fs)\n" "$OUT"
