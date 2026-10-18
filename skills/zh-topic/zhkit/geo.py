"""Real map outlines from Natural Earth (public domain), drawn as ink in Manim.

    python scripts/fetch_geo.py Iceland topics/iceland_glaciers/geo.json
    shapes = geo.load("topics/iceland_glaciers/geo.json")
    land = geo.ink_shape(shapes["land"], width=10)        # VGroup of polygons
    ice = geo.ink_shape(shapes["glaciers"]["Vatnajökull"], fill=T.BLUE)
"""
from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"


def _polys(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [p[0] for p in geom["coordinates"]]


def _simplify(pts, tol):
    """Drop points closer than `tol` degrees to the previous kept point."""
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) >= tol:
            out.append(p)
    return out


def extract(country: str, out_path, cache_dir, min_area: float = 0.02, tol: float = 0.03):
    """Write {land: [...], glaciers: {name: [...]}, bbox} for a country as lon/lat lists."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ("ne_10m_admin_0_countries.geojson", "ne_10m_glaciated_areas.geojson"):
        f = cache_dir / name
        if not f.exists():
            f.write_bytes(urllib.request.urlopen(NE + name).read())
        files[name] = json.loads(f.read_text())
    feat = next(f for f in files["ne_10m_admin_0_countries.geojson"]["features"]
                if f["properties"].get("ADMIN") == country)

    def area(p):
        return abs(sum(p[i][0] * p[i + 1][1] - p[i + 1][0] * p[i][1] for i in range(len(p) - 1))) / 2
    land = [_simplify(p, tol) for p in _polys(feat["geometry"]) if area(p) >= min_area]
    xs = [pt[0] for p in land for pt in p]
    ys = [pt[1] for p in land for pt in p]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    glaciers = {}
    for f in files["ne_10m_glaciated_areas.geojson"]["features"]:
        for p in _polys(f["geometry"]):
            if all(bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3] for x, y in p):
                nm = f["properties"].get("name") or f"glacier_{len(glaciers)}"
                glaciers.setdefault(nm, []).append(_simplify(p, tol / 3))
    Path(out_path).write_text(json.dumps({"land": land, "glaciers": glaciers, "bbox": bbox}))
    return out_path


def load(path) -> dict:
    return json.loads(Path(path).read_text())


class Projector:
    """lon/lat -> Manim coordinates, fitted into a box (equirectangular with cos(lat))."""

    def __init__(self, bbox, center=(0, 0), width=10.0, height=6.0):
        x0, y0, x1, y1 = bbox
        self.k = math.cos(math.radians((y0 + y1) / 2))
        w, h = (x1 - x0) * self.k, (y1 - y0)
        self.s = min(width / w, height / h)
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.center = center

    def __call__(self, lon, lat):
        return [self.center[0] + (lon - self.cx) * self.k * self.s,
                self.center[1] + (lat - self.cy) * self.s, 0]


def ink_shape(polys, proj: Projector, color=None, width: float = 4, fill=None,
              fill_opacity: float = 0.5):
    """VGroup of closed polygons (one per ring) projected with `proj`."""
    from manim import LineJointType, Polygon, VGroup
    from csvideo import theme as T
    g = VGroup()
    for p in polys:
        pts = [proj(x, y) for x, y in p[:-1]]
        if len(pts) < 3:
            continue
        poly = Polygon(*pts, stroke_color=color or T.FG, stroke_width=width,
                       fill_color=fill or T.BG, fill_opacity=fill_opacity if fill else 0)
        poly.joint_type = LineJointType.ROUND
        g.add(poly)
    return g
