"""Chinese text tools: script conversion, segmentation, HSK levels, pinyin, glosses.

Text is written in traditional characters. For analysis it is converted to
simplified (OpenCC t2s is character-for-character, so offsets line up), segmented
with jieba, and each word is looked up in the HSK list (HSK 2.0 levels 1-6; HSK 3.0
used as a fallback).
"""
from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "hsk.json"
HAN = re.compile(r"[㐀-鿿]")

# words treated as known regardless of HSK (very common in any topic text)
ALWAYS_EASY = {"冰島", "冰岛"}


@lru_cache(maxsize=1)
def _cc():
    import opencc
    return opencc.OpenCC("t2s"), opencc.OpenCC("s2twp")


def to_simplified(text: str) -> str:
    return _cc()[0].convert(text)


def to_traditional(text: str) -> str:
    return _cc()[1].convert(text)


@lru_cache(maxsize=1)
def hsk() -> dict:
    return json.loads(DATA.read_text())


@lru_cache(maxsize=1)
def _jieba():
    import jieba
    jieba.setLogLevel(logging.WARNING)
    for w in hsk():
        jieba.add_word(w)
    return jieba


def add_words(words):
    """Teach the segmenter extra words (names, terms) so they stay whole."""
    jb = _jieba()
    for w in words:
        jb.add_word(to_simplified(w), freq=200000)


def segment(text: str) -> list[str]:
    """Split traditional text into words (returned in the original characters)."""
    simp = to_simplified(text)
    if len(simp) != len(text):            # conversion changed length: fall back to chars
        return list(text)
    out, i = [], 0
    for tok in _jieba().cut(simp, HMM=False):
        out.append(text[i:i + len(tok)])
        i += len(tok)
    return out


def is_chinese(word: str) -> bool:
    return bool(HAN.search(word))


# traditional chars OpenCC leaves alone on their own but HSK lists in another form
CHAR_FIX = {"著": "着", "裡": "里", "麼": "么"}


def _key(word: str) -> str:
    s = to_simplified(word)
    return "".join(CHAR_FIX.get(c, c) for c in s)


def _entry(word: str):
    return hsk().get(_key(word)) or hsk().get(to_simplified(word))


def level(word: str):
    """HSK level of a word as listed (2.0 levels; 3.0 as fallback, 7 = advanced), or None."""
    e = _entry(word)
    if not e:
        return None
    return e[0] if e[0] is not None else e[1]


@lru_cache(maxsize=20000)
def split_known(word: str):
    """Split a word into the fewest HSK-listed pieces; returns (pieces, max_level) or None."""
    simp = _key(word)
    n = len(simp)
    best = [None] * (n + 1)          # best[i] = (count, max_level, pieces)
    best[0] = (0, 0, [])
    for i in range(1, n + 1):
        for j in range(max(0, i - 4), i):
            if best[j] is None:
                continue
            e = hsk().get(simp[j:i])
            if not e:
                continue
            l = e[0] if e[0] is not None else e[1]
            cand = (best[j][0] + 1, max(best[j][1], l), best[j][2] + [word[j:i]])
            if best[i] is None or cand[:2] < best[i][:2]:
                best[i] = cand
    return (best[n][2], best[n][1]) if best[n] else None


@lru_cache(maxsize=20000)
def word_level(word: str):
    """Effective difficulty: the listed level, or the level of its easiest split into
    known pieces if that is lower (火山 = 火 + 山 is easy even though 火山 is HSK 6;
    很多 = 很 + 多). None if it can't be built from known words."""
    direct = level(word)
    split = split_known(word) if len(word) > 1 else None
    comp = split[1] if split and len(split[0]) > 1 else None
    if comp is None and 2 <= len(word) <= 3:          # transparent: 火山 = 火 + 山
        chars = [level(c) for c in word]
        if all(c is not None for c in chars):
            comp = max(chars)
    vals = [v for v in (direct, comp) if v is not None]
    return min(vals) if vals else None


def units(word: str, max_level: int = 4, known=frozenset(), glossed=frozenset()):
    """What to gloss inside a segmented word: the word itself, or (for an unlisted word
    made of known pieces, like 太薄) just its hard pieces. Returns [(piece, is_hard)]."""
    if not is_chinese(word) or word in known:
        return [(word, False)]
    if word in glossed or level(word) is not None:
        return [(word, is_hard(word, max_level, known))]
    split = split_known(word)
    if split and len(split[0]) > 1:
        return [(p, is_hard(p, max_level, known)) for p in split[0]]
    return [(word, is_hard(word, max_level, known))]


def _norm(py: str) -> str:
    return py.replace(" ", "").lower()


def _forms(word: str):
    e = _entry(word)
    return e[2] if e else []


def _is_surname(meaning: str) -> bool:
    return meaning.lower().startswith("surname")


def pinyin(word: str, context: str | None = None) -> str:
    """Pinyin for a word. With `context` (the sentence it appears in), the reading is
    worked out from the sentence (重量 zhòng, 重複 chóng), which avoids picking a
    surname or rare reading from the dictionary."""
    from pypinyin import Style, pinyin as _py
    if context and word in context:
        i = context.index(word)
        syl = _py(to_simplified(context), style=Style.TONE, errors=lambda x: list(x))
        flat = [s[0] for s in syl]
        if len(flat) == len(context):
            return "".join(flat[i:i + len(word)])
    forms = [f for f in _forms(word) if not _is_surname(f[2])] or _forms(word)
    if len(word) > 1 and forms:
        return _norm(forms[0][1])
    return "".join(s[0] for s in _py(to_simplified(word), style=Style.TONE))


def pinyin_chars(word: str, context: str | None = None) -> list[str]:
    """One syllable per character (for per-character ruby)."""
    from pypinyin import Style, pinyin as _py
    if context and word in context:
        i = context.index(word)
        syl = _py(to_simplified(context), style=Style.TONE, errors=lambda x: list(x))
        if len(syl) == len(context):
            return [s[0] for s in syl[i:i + len(word)]]
    return [s[0] for s in _py(to_simplified(word), style=Style.TONE)]


def english(word: str, py: str | None = None):
    """English meaning; with `py`, the meaning of that reading (not a surname if possible)."""
    forms = _forms(word)
    if not forms:
        return None
    if py:
        same = [f for f in forms if _norm(f[1]) == _norm(py)]
        if same:
            forms = same
    good = [f for f in forms if not _is_surname(f[2])]
    return (good or forms)[0][2]


def is_hard(word: str, max_level: int = 4, known=frozenset()) -> bool:
    """True for a Chinese word above `max_level` or not in the HSK list at all."""
    if not is_chinese(word) or word in ALWAYS_EASY or word in known:
        return False
    lv = word_level(word)
    return lv is None or lv > max_level


def profile(text: str) -> dict:
    """Share of Chinese word tokens per HSK level (None = not in HSK)."""
    counts: dict = {}
    total = 0
    for w in segment(text):
        if not is_chinese(w):
            continue
        lv = word_level(w)
        counts[lv] = counts.get(lv, 0) + 1
        total += 1
    return {"tokens": total, "by_level": counts}
