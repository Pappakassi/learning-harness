#!/bin/bash
# webcopy.sh <in.mp4> <out.mp4> : 720p two-pass copy under ~14 MB (for hosting with a 15 MB per-file limit)
set -e
IN="$1"; OUT="$2"; T="$(mktemp -d)"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
VB=$(python3 -c "print(int((14.0*8*1000/ $D - 96)))")
ffmpeg -y -loglevel error -i "$IN" -vf "hqdn3d=3:3:6:6,scale=1280:720:flags=lanczos" -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -passlogfile "$T/p" -an -f mp4 /dev/null
ffmpeg -y -loglevel error -i "$IN" -vf "hqdn3d=3:3:6:6,scale=1280:720:flags=lanczos" -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -passlogfile "$T/p" -c:a aac -b:a 96k -movflags +faststart "$OUT"
rm -rf "$T"; ls -la "$OUT"
