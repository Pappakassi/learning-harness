#!/usr/bin/env bash
# One-time setup for the cs-video skill.
#   bash setup.sh
# Creates .venv/ in this folder, installs Python packages, and downloads the
# default narration voice. System tools (ffmpeg, LaTeX, Pango, SoX) must be
# installed first; the commands for each OS are printed if any are missing.
set -euo pipefail
cd "$(dirname "$0")"

missing=()
for tool in ffmpeg latex dvisvgm sox pkg-config; do
  command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done
if ! pkg-config --exists pangocairo 2>/dev/null; then missing+=("pango"); fi

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing system tools: ${missing[*]}"
  echo
  echo "  Ubuntu/Debian: sudo apt-get install -y ffmpeg texlive texlive-latex-extra dvisvgm sox libpango1.0-dev pkg-config"
  echo "  macOS (Homebrew): brew install ffmpeg sox pango pkg-config && brew install --cask mactex-no-gui"
  echo "  Windows: use WSL (Ubuntu) and the Ubuntu line above"
  exit 1
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q --upgrade pip setuptools wheel
.venv/bin/pip install -q -r requirements.txt

mkdir -p voices
if [ ! -f voices/en-us-lessac-medium.onnx ]; then
  echo "Downloading narration voice (~60 MB)..."
  curl -sSL -o voices/lessac.tar.gz \
    https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
  tar xzf voices/lessac.tar.gz -C voices
  rm voices/lessac.tar.gz
fi

echo "Setup done. Test with:"
echo "  cd examples/binary_search && ../../.venv/bin/python ../../scripts/render.py video.py --draft"
