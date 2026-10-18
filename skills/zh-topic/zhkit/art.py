"""Generative sumi-e (ink wash) artwork: paper, mountains, glaciers, ensō, seals.

Everything is drawn with numpy + Pillow, so each topic gets its own artwork
without any image downloads. Minimal colour: ink on rice paper, a red seal, and an
occasional pale glacier-blue wash.

    from zhkit import art
    art.cover("冰島的冰川", "冰與火之間", "cover.png")
    art.chapter_art("glacier", "ch1.png", seed=3)
"""
from __future__ import annotations

import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PAPER = (243, 237, 225)
INK = (31, 27, 23)
SEAL = (178, 58, 46)
ICE = (120, 160, 182)
FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


@lru_cache(maxsize=4)
def font_path(weight: str = "Regular") -> str:
    local = FONT_DIR / f"LXGWWenKaiTC-{weight}.ttf"
    if local.exists():
        return str(local)
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", f"LXGW WenKai TC:style={weight}"],
                             capture_output=True, text=True).stdout.strip()
        if out:
            return out
    except FileNotFoundError:
        pass
    raise FileNotFoundError("LXGW WenKai TC font not found; run setup.sh")


def _font(size, weight="Regular"):
    return ImageFont.truetype(font_path(weight), size)


# ---------------------------------------------------------------- basics
def paper(w: int, h: int, seed: int = 0) -> Image.Image:
    """Warm rice paper with faint fibres and a soft vignette."""
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(PAPER, np.float32)
    noise = rng.normal(0, 1, (h // 4 + 1, w // 4 + 1)).astype(np.float32)
    noise = np.array(Image.fromarray(((noise * 20) + 128).clip(0, 255).astype(np.uint8))
                     .resize((w, h), Image.BICUBIC)).astype(np.float32) - 128
    base += noise[..., None] * 0.18
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(int(w * h / 9000)):                      # fibres
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(8, 40)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))],
               fill=(150, 135, 110, int(rng.uniform(8, 22))), width=1)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vig = (1 - 0.07 * np.clip(r - 0.6, 0, 1)).astype(np.float32)
    arr = (np.array(img).astype(np.float32) * vig[..., None]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _ridge(w: int, rng, base: float, amp: float, rough: float = 1.0, plateau: float = 0.0):
    x = np.linspace(0, 1, w)
    y = np.zeros(w)
    for k in range(1, 7):
        f = rng.uniform(0.6, 1.4) * (2 ** k) * 0.7
        y += math.pow(0.55, k) * rough * np.sin(2 * math.pi * (f * x + rng.uniform(0, 1)))
    # one or two main peaks
    for _ in range(int(rng.integers(1, 3))):
        c, s = rng.uniform(0.2, 0.8), rng.uniform(0.12, 0.3)
        y += 1.2 * np.exp(-((x - c) / s) ** 2)
    if plateau:
        y = np.minimum(y, np.quantile(y, 1 - plateau))
    y = (y - y.min()) / (np.ptp(y) + 1e-9)
    return base - y * amp


def _wash(img: Image.Image, ridge, color, alpha: float, fade: float, blur: float = 2.0):
    """Ink wash below a ridge line, strongest at the ridge and fading downward (mist)."""
    w, h = img.size
    yy = np.arange(h)[:, None]
    depth = (yy - ridge[None, :]) / fade
    mask = np.where(depth >= 0, np.clip(1 - depth, 0, 1) ** 0.8, 0) * alpha
    rng = np.random.default_rng(int(alpha * 1000) + w)
    tex = rng.normal(1.0, 0.18, (h // 6 + 1, w // 6 + 1)).astype(np.float32)
    tex = np.array(Image.fromarray(((tex - 0.4) * 160).clip(0, 255).astype(np.uint8))
                   .resize((w, h), Image.BICUBIC)).astype(np.float32) / 160 + 0.4
    mask = (mask * tex).clip(0, 1)
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.BoxBlur(4)).filter(ImageFilter.GaussianBlur(blur + 3))
    layer = Image.new("RGB", (w, h), color)
    img.paste(layer, (0, 0), m)
    return img


def mountains(img: Image.Image, seed: int = 0, layers: int = 4, top: float = 0.35,
              bottom: float = 0.75, glacier: bool = False, volcano: bool = False):
    """Layered ink mountains in the lower part of `img` (fractions of height)."""
    w, h = img.size
    rng = np.random.default_rng(seed)
    for i in range(layers):
        t = i / max(layers - 1, 1)
        base = h * (top + (bottom - top) * t) + h * 0.12
        amp = h * (0.22 - 0.1 * t)
        ridge = _ridge(w, rng, base, amp, rough=1.0 - 0.3 * t,
                       plateau=0.35 if (glacier and i == 0) else 0.0)
        alpha = 0.16 + 0.55 * t
        fade = h * (0.10 + 0.12 * t)
        if glacier and i == 0:
            _wash(img, ridge, ICE, 0.45, h * 0.05, blur=3)          # pale blue ice cap edge
            _wash(img, ridge + h * 0.035, INK, 0.22, h * 0.10, blur=3)
        else:
            _wash(img, ridge, INK, alpha, fade, blur=2.5 - t)
        if volcano and i == 1:
            top_x = int(np.argmin(ridge))
            smoke(img, top_x, int(ridge[top_x]), seed=seed)
    return img


def smoke(img: Image.Image, x: int, y: int, seed: int = 0):
    """A soft plume of ash rising from (x, y), drifting sideways as it rises."""
    rng = np.random.default_rng(seed + 11)
    w, h = img.size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    px, py = float(x), float(y)
    for s in range(60):
        r = 6 + s * 1.1
        px += 1.6 + math.sin(s / 7) * 2.5
        py -= 4.2
        a = int(110 * (1 - s / 60) ** 1.2)
        for _ in range(3):
            ox, oy = rng.normal(0, r * 0.35, 2)
            d.ellipse([px + ox - r, py + oy - r, px + ox + r, py + oy + r], fill=a)
    layer = layer.filter(ImageFilter.GaussianBlur(9))
    arr = np.array(layer).astype(np.float32) / 255 * 0.55
    img.paste(Image.new("RGB", (w, h), INK), (0, 0),
              Image.fromarray((arr * 255).astype(np.uint8)))
    return img


def waves(img: Image.Image, y0: float, y1: float, seed: int = 0, n: int = 9):
    """Horizontal brush lines for water / floods between fractions y0..y1 of height."""
    w, h = img.size
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(n):
        y = h * (y0 + (y1 - y0) * k / n) + rng.uniform(-4, 4)
        x = rng.uniform(0, w * 0.25)
        L = rng.uniform(w * 0.3, w * 0.7)
        pts = [(x + t, y + 6 * math.sin(t / 40 + k)) for t in np.linspace(0, L, 80)]
        for j in range(len(pts) - 1):
            frac = j / len(pts)
            wd = max(1, int(7 * math.sin(math.pi * frac)))
            d.line([pts[j], pts[j + 1]], fill=INK + (int(150 * math.sin(math.pi * frac)),), width=wd)
    return img


def enso(size: int, seed: int = 0, color=INK, gap_deg: float = 22) -> Image.Image:
    """A brushed ensō: heavy wet start, thinning stroke, dry-brush tail."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    R = size * 0.36
    start = rng.uniform(0, 2 * math.pi)
    span = 2 * math.pi - math.radians(gap_deg)
    steps = 1400
    n_b = 46
    offs = np.sort(rng.uniform(-1, 1, n_b))
    load = rng.uniform(0.75, 1.0, n_b)          # ink load per bristle
    dry_at = rng.uniform(0.55, 1.05, n_b)       # where each bristle runs dry
    for s in range(steps):
        f = s / steps
        a = start + span * f
        r = R * (1 + 0.03 * math.sin(2 * a + seed) + 0.01 * math.sin(7 * a))
        width = size * (0.105 * (1 - f) ** 0.7 + 0.012 + 0.02 * math.exp(-f * 30))
        for b in range(n_b):
            if f > dry_at[b] and rng.random() < 0.85:
                continue
            rr = r + offs[b] * width / 2
            x, y = c + rr * math.cos(a), c + rr * math.sin(a)
            alpha = int(235 * load[b] * (1 - 0.45 * f))
            dot = 1.6 + 1.4 * (1 - f)
            d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=color + (alpha,))
    return img.filter(ImageFilter.GaussianBlur(0.7))


def seal(chars: str, size: int = 160, seed: int = 0) -> Image.Image:
    """A red name seal (印章) with carved white characters, 1-4 chars."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size * 0.04
    d.rounded_rectangle([m, m, size - m, size - m], radius=size * 0.06, fill=SEAL + (235,))
    n = len(chars)
    if n == 1:
        cells = [(0.5, 0.5, 0.72)]
    elif n == 2:
        cells = [(0.5, 0.29, 0.40), (0.5, 0.71, 0.40)]
    elif n == 3:
        cells = [(0.70, 0.5, 0.62), (0.30, 0.29, 0.38), (0.30, 0.71, 0.38)]
    else:   # traditional order: right column top-down, then left column
        cells = [(0.70, 0.29, 0.38), (0.70, 0.71, 0.38), (0.30, 0.29, 0.38), (0.30, 0.71, 0.38)]
    for ch, (cx, cy, s) in zip(chars, cells):
        f = _font(int(size * s), "Medium")
        d.text((size * cx, size * cy), ch, font=f, fill=(250, 244, 236, 255), anchor="mm")
    arr = np.array(img)
    wear = rng.random(arr.shape[:2]) < 0.035                 # worn stone texture
    arr[wear & (arr[..., 3] > 0), 3] = 90
    edge = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(0.6))
    return edge


def brush_text_vertical(img: Image.Image, text: str, x: int, y: int, size: int,
                        color=INK, spacing: float = 1.08, weight: str = "Medium"):
    """Write text top-to-bottom (traditional vertical layout) starting at (x, y)."""
    d = ImageDraw.Draw(img, "RGBA")
    f = _font(size, weight)
    for i, ch in enumerate(text):
        d.text((x, y + i * size * spacing), ch, font=f, fill=color + (255,), anchor="mt")
    return img


def _fade_edges(img: Image.Image, margin: float = 0.12) -> Image.Image:
    """Blend the picture into plain paper near its edges (vignette for chapter art)."""
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    fx = np.clip(np.minimum(xx, w - 1 - xx) / (w * margin), 0, 1)
    fy = np.clip(np.minimum(yy, h - 1 - yy) / (h * margin), 0, 1)
    a = (fx * fy) ** 0.8
    plain = np.array(paper(w, h, seed=99)).astype(np.float32)
    arr = np.array(img).astype(np.float32)
    out = plain * (1 - a[..., None]) + arr * a[..., None]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


# ---------------------------------------------------------------- compositions
def cover(title: str, subtitle: str, out, tag: str = "HSK 4–5", seal_chars: str = "冰火",
          seed: int = 1, w: int = 1600, h: int = 2400):
    img = paper(w, h, seed)
    mountains(img, seed=seed, layers=4, top=0.50, bottom=0.80, glacier=True)
    e = enso(int(w * 0.62), seed=seed)
    img.paste(e, (int(w * 0.04), int(h * 0.10)), e)
    size = int(w * 0.13)
    brush_text_vertical(img, title, int(w * 0.80), int(h * 0.08), size)
    if subtitle:
        brush_text_vertical(img, subtitle, int(w * 0.64), int(h * 0.12), int(size * 0.42),
                            color=(110, 100, 90), weight="Regular")
    s = seal(seal_chars, int(w * 0.12), seed)
    img.paste(s, (int(w * 0.80 - w * 0.06), int(h * 0.08 + len(title) * size * 1.08 + 30)), s)
    d = ImageDraw.Draw(img)
    d.text((int(w * 0.06), int(h * 0.95)), tag, font=_font(int(w * 0.03)), fill=(120, 110, 100),
           anchor="lm")
    img.save(out)
    return out


def chapter_art(kind: str, out, seed: int = 0, w: int = 1600, h: int = 640, number: str = ""):
    """Wide ink vignette for a chapter opening. kind: mountains | glacier | volcano |
    flood | melt | enso."""
    img = paper(w, h, seed)
    if kind in ("mountains", "glacier", "volcano", "melt"):
        mountains(img, seed=seed, layers=3 if kind != "melt" else 2, top=0.15, bottom=0.55,
                  glacier=kind in ("glacier", "melt"), volcano=kind == "volcano")
    if kind == "flood":
        mountains(img, seed=seed, layers=2, top=0.05, bottom=0.30, volcano=True)
        waves(img, 0.62, 0.92, seed=seed)
    if kind == "melt":
        waves(img, 0.78, 0.95, seed=seed, n=5)
    if kind == "enso":
        e = enso(int(h * 0.95), seed=seed)
        img.paste(e, ((w - e.width) // 2, (h - e.height) // 2), e)
    img = _fade_edges(img)
    if number:
        s = seal(number, int(h * 0.2), seed)
        img.paste(s, (int(w * 0.88), int(h * 0.12)), s)
    img.save(out)
    return out


def video_backdrop(out, w: int = 1920, h: int = 1080, seed: int = 5):
    """Paper with very faint distant mountains at the bottom, for video scenes."""
    img = paper(w, h, seed)
    mountains(img, seed=seed, layers=2, top=0.78, bottom=0.88)
    arr = np.array(img).astype(np.float32)
    base = np.array(paper(w, h, seed)).astype(np.float32)
    img = Image.fromarray((base * 0.55 + arr * 0.45).astype(np.uint8))   # keep it faint
    img.convert("RGBA").save(out)        # Manim's ImageMobject wants RGBA
    return out
