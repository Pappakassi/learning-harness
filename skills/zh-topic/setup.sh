#!/usr/bin/env bash
# Setup for zh-topic. Run cs-video/setup.sh first (it creates the shared .venv and voices).
set -euo pipefail
cd "$(dirname "$0")"
PY=../cs-video/.venv/bin/python
[ -x "$PY" ] || { echo "Run ../cs-video/setup.sh first"; exit 1; }

$PY -m pip install -q -r requirements.txt

mkdir -p fonts data
if [ ! -f fonts/LXGWWenKaiTC-Regular.ttf ]; then
  echo "Downloading LXGW WenKai TC (brush-style font, SIL OFL)..."
  for w in Regular Medium; do
    curl -sSL -o fonts/LXGWWenKaiTC-$w.ttf \
      https://github.com/lxgw/LxgwWenkaiTC/releases/download/v1.520/LXGWWenKaiTC-$w.ttf
  done
fi
mkdir -p ~/.fonts && cp fonts/LXGWWenKaiTC-*.ttf ~/.fonts/ && (fc-cache -f >/dev/null 2>&1 || true)

if ! fc-list :lang=zh-tw | grep -q .; then
  echo "Tip: install Noto CJK too (Ubuntu: sudo apt-get install -y fonts-noto-cjk)"
fi

if [ ! -f data/hsk.json ]; then
  echo "Building HSK vocabulary list..."
  $PY scripts/fetch_data.py
fi
echo "zh-topic ready. Example: topics/iceland_glaciers/"
