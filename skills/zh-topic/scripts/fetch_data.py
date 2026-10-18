#!/usr/bin/env python3
"""Download the complete HSK vocabulary and write a compact lookup to data/hsk.json.

Each entry: simplified -> [old_level, new_level, [[traditional, pinyin, english], ...]]
old_level = HSK 2.0 (1-6), new_level = HSK 3.0 (1-7); either may be null.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/complete.json"
OUT = Path(__file__).resolve().parent.parent / "data" / "hsk.json"


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    raw = Path(src).read_text() if src else urllib.request.urlopen(URL).read().decode()
    data = json.loads(raw)
    out = {}
    for e in data:
        old = [int(m.group(1)) for l in e["level"] if (m := re.match(r"old-(\d)", l))]
        new = [int(m.group(1)) for l in e["level"] if (m := re.match(r"new-(\d)", l))]
        forms = [[f["traditional"], f["transcriptions"]["pinyin"], "; ".join(f["meanings"][:2])]
                 for f in e["forms"]]
        out[e["simplified"]] = [min(old) if old else None, min(new) if new else None, forms]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(out)} words -> {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
