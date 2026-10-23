#!/bin/bash
# make_open.sh <episode-dir> : scaffold the cartoon cold open in <episode-dir>/open and wire in the series files.
set -e
SERIES="$(cd "$(dirname "$0")" && pwd)"
CSV="$(cd "$SERIES/../.." && pwd)"
D="$1/open"
[ -d "$D/engine" ] || "$CSV/.venv/bin/python" "$CSV/cartoon/new_cartoon.py" "$D" --lang en > /dev/null
cp "$SERIES/props.js" "$SERIES/score.js" "$SERIES/song.js" "$D/"
grep -q props.js "$D/index.html" || sed -i 's#<script src="film.js"></script>#<script src="props.js"></script>\n<script src="film.js"></script>#' "$D/index.html"
python3 - "$D/narration.py" <<'PY'
import sys, re
p = sys.argv[1]; s = open(p).read()
if "from lines import" not in s:
    s = re.sub(r"VOICES = \{.*?\n\]\n", "sys.path.insert(0, str(HERE))\nfrom lines import VOICES, SPEED, LINES  # noqa: E402\n", s, flags=re.S)
    open(p, "w").write(s)
PY
echo "open project ready: $D"
