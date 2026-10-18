#!/usr/bin/env python3
"""Extract a country's outline and glaciers from Natural Earth into a small json.

    python scripts/fetch_geo.py Iceland topics/iceland_glaciers/geo.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zhkit import geo  # noqa: E402

if __name__ == "__main__":
    country, out = sys.argv[1], sys.argv[2]
    cache = Path(__file__).resolve().parent.parent / "data" / "naturalearth"
    geo.extract(country, out, cache)
    d = geo.load(out)
    print(f"{out}: {len(d['land'])} land rings, glaciers: {', '.join(d['glaciers'])}")
