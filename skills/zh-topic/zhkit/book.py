"""Build a graded-reader EPUB from a simple text source.

Source format (book.txt):

    title: 冰島的冰川
    subtitle: 冰與火之間的國度
    seal: 冰火
    level: 4                     # words above this HSK level get pinyin + glossary
    known: 冰島                  # comma-separated words never glossed
    === gloss
    冰川 | glacier
    瓦特納冰川 | Vatnajökull, Iceland's largest glacier
    === chapter 雪怎麼變成冰 | art=glacier
    Paragraph text, one paragraph per line.
    Another paragraph.
    ? Question text || answer text
    === chapter ...

Hard words (above `level` or not in HSK) get ruby pinyin on their first use in each
chapter and go into that chapter's glossary. English comes from the gloss block, else
the HSK list; the build stops if a hard word has no English.
"""
from __future__ import annotations

import html
import io
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import art, lang

CSS = """
@font-face { font-family: "WenKai"; src: url("../fonts/wenkai.ttf"); }
body { font-family: "WenKai", serif; background: #F3EDE1; color: #1F1B17;
       line-height: 2.1; margin: 0 6%; font-size: 1.15em; }
h1 { font-weight: normal; font-size: 1.7em; text-align: center; margin: 0.6em 0 0.2em;
     letter-spacing: 0.15em; }
.num { text-align: center; color: #B23A2E; font-size: 0.95em; letter-spacing: 0.3em; }
img.art { width: 100%; display: block; margin: 0.6em 0 1em; }
p { text-indent: 2em; margin: 0 0 0.9em; text-align: justify; }
ruby rt { font-size: 0.48em; color: #4F7A93; font-family: sans-serif; letter-spacing: 0; }
h2 { font-size: 1.05em; font-weight: normal; color: #B23A2E; border-top: 1px solid #C9BFAE;
     padding-top: 0.8em; margin-top: 1.6em; letter-spacing: 0.2em; }
table.gloss { width: 100%; border-collapse: collapse; font-size: 0.9em; line-height: 1.6; }
table.gloss td { padding: 0.25em 0.4em; border-bottom: 1px dotted #C9BFAE; vertical-align: top; }
td.w { white-space: nowrap; font-size: 1.1em; } td.p { color: #4F7A93; font-family: sans-serif;
       font-size: 0.85em; white-space: nowrap; } td.e { color: #6B6258; font-family: sans-serif;
       font-size: 0.8em; }
ol.q { line-height: 1.9; } ol.q li { margin-bottom: 0.4em; }
.ans { color: #6B6258; } .seal { text-align: center; margin-top: 2em; }
.title-page { text-align: center; margin-top: 30%; } .title-page h1 { font-size: 2.2em; }
.sub { color: #857C70; letter-spacing: 0.2em; }
"""


@dataclass
class Chapter:
    title: str
    art: str = "mountains"
    paras: list = field(default_factory=list)
    questions: list = field(default_factory=list)   # (q, a)


@dataclass
class Book:
    meta: dict
    gloss: dict
    chapters: list

    @property
    def level(self) -> int:
        return int(self.meta.get("level", 4))

    @property
    def known(self) -> frozenset:
        return frozenset(w.strip() for w in self.meta.get("known", "").split(",") if w.strip())

    def text(self) -> str:
        return "\n".join(p for c in self.chapters for p in [c.title] + c.paras
                         + [q for q, _ in c.questions])


def parse(path) -> Book:
    meta, gloss, chapters = {}, {}, []
    mode = "meta"
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("=== gloss"):
            mode = "gloss"
            continue
        if line.startswith("=== chapter"):
            rest = line[len("=== chapter"):].strip()
            title, _, opts = rest.partition("|")
            ch = Chapter(title.strip())
            for kv in opts.split(","):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    if k.strip() == "art":
                        ch.art = v.strip()
            chapters.append(ch)
            mode = "chapter"
            continue
        if mode == "meta":
            k, _, v = line.partition(":")
            meta[k.strip()] = v.split("#")[0].strip()
        elif mode == "gloss":
            w, _, e = line.partition("|")
            gloss[w.strip()] = e.strip()
        else:
            if line.startswith("?"):
                q, _, a = line[1:].partition("||")
                chapters[-1].questions.append((q.strip(), a.strip()))
            else:
                chapters[-1].paras.append(line)
    book = Book(meta, gloss, chapters)
    lang.add_words(list(gloss) + list(book.known))
    return book


def english_for(book: Book, w: str, py: str | None = None):
    return book.gloss.get(w) or lang.english(w, py)


def _units(book: Book, text: str):
    for w in lang.segment(text):
        yield from lang.units(w, book.level, book.known, frozenset(book.gloss))


def hard_words(book: Book, text: str) -> list[str]:
    return [w for w, _ in hard_words_py(book, text)]


def hard_words_py(book: Book, text: str) -> list[tuple]:
    """[(word, pinyin_in_context)] for hard words, first occurrence order."""
    seen, out = set(), []
    for para in text.split("\n"):
        for w, hard in _units(book, para):
            if hard and w not in seen:
                seen.add(w)
                out.append((w, lang.pinyin(w, para)))
    return out


def report(book: Book) -> str:
    """Level profile + missing glosses, as text."""
    prof = lang.profile(book.text())
    tot = prof["tokens"] or 1
    by = prof["by_level"]
    glossed = {w for c in book.chapters for w in hard_words(book, "\n".join(c.paras))}
    lines = [f"Characters (Chinese): {sum(1 for ch in book.text() if lang.is_chinese(ch))}",
             f"Word tokens: {tot}"]
    cum = 0
    for lv in range(1, 8):
        cum += by.get(lv, 0)
        lines.append(f"  ≤ HSK {lv}: {100 * cum / tot:5.1f}%")
    lines.append(f"  not in HSK list: {100 * by.get(None, 0) / tot:5.1f}%")
    over5 = [w for w in glossed if (lang.word_level(w) or 9) > 5 and w not in book.gloss]
    lines.append(f"Glossed words: {len(glossed)}")
    missing = [w for w in sorted(glossed) if not english_for(book, w)]
    if missing:
        lines.append("MISSING GLOSS (add to === gloss): " + "、".join(missing))
    if over5:
        lines.append("Above HSK 5 without a custom gloss (consider a simpler word): "
                     + "、".join(sorted(over5)))
    return "\n".join(lines)


def _ruby_para(book: Book, para: str, seen: set) -> str:
    out = []
    for w, hard in _units(book, para):
        if hard and w not in seen:
            seen.add(w)
            sy = lang.pinyin_chars(w, para)
            out.append("<ruby>" + "".join(f"{html.escape(c)}<rt>{html.escape(p)}</rt>"
                                          for c, p in zip(w, sy)) + "</ruby>")
        else:
            out.append(html.escape(w))
    return "".join(out)


def _subset_font(chars: str) -> bytes:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    font = TTFont(art.font_path("Regular"))
    opts = subset.Options()
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    sub.populate(text=chars + "0123456789，。！？；：、「」（）《》—…·")
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def _jpeg(png_path) -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.open(png_path).convert("RGB").save(buf, "JPEG", quality=86, optimize=True)
    return buf.getvalue()


NUMS = "一二三四五六七八九十"


def _plain(py: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", py) if not unicodedata.combining(c)).lower()


def build(src, out_epub, work_dir) -> Path:
    from ebooklib import epub

    book = parse(src)
    missing = [w for c in book.chapters for w in hard_words(book, "\n".join(c.paras))
               if not english_for(book, w)]
    if missing:
        raise SystemExit("Add glosses for: " + "、".join(dict.fromkeys(missing)))

    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    m = book.meta
    eb = epub.EpubBook()
    eb.set_identifier(str(uuid.uuid4()))
    eb.set_title(m.get("title", "Book"))
    eb.set_language("zh-Hant")
    eb.add_author(m.get("author", "learning-harness"))

    cover_png = work / "cover.png"
    art.cover(m.get("title", ""), m.get("subtitle", ""), cover_png,
              tag=f"HSK {book.level}–{book.level + 1}", seal_chars=m.get("seal", "書")[:4])
    eb.set_cover("images/cover.jpg", _jpeg(cover_png))

    css = epub.EpubItem(uid="css", file_name="styles/book.css", media_type="text/css",
                        content=CSS.replace("../fonts/", "../fonts/"))
    eb.add_item(css)

    all_chars = "".join(sorted(set(book.text() + m.get("title", "") + m.get("subtitle", "")
                                   + "".join(book.gloss) + "第章生詞問題答案參考詞彙表目錄"
                                   )))
    eb.add_item(epub.EpubItem(uid="font", file_name="fonts/wenkai.ttf",
                              media_type="font/ttf", content=_subset_font(all_chars)))

    def page(fname, title, body):
        c = epub.EpubHtml(title=title, file_name=fname, lang="zh-Hant")
        c.content = f"<html><head><link rel='stylesheet' href='styles/book.css'/></head><body>{body}</body></html>"
        c.add_item(css)
        eb.add_item(c)
        return c

    spine = ["cover"]
    title_pg = page("title.xhtml", m.get("title", ""),
                    f"<div class='title-page'><h1>{html.escape(m.get('title', ''))}</h1>"
                    f"<p class='sub'>{html.escape(m.get('subtitle', ''))}</p></div>")
    spine.append(title_pg)
    toc = []
    all_gloss = {}
    for i, ch in enumerate(book.chapters):
        png = work / f"ch{i + 1}.png"
        art.chapter_art(ch.art, png, seed=i + 3, number=NUMS[i] if i < 10 else "")
        img_name = f"images/ch{i + 1}.jpg"
        eb.add_item(epub.EpubItem(uid=f"img{i}", file_name=img_name, media_type="image/jpeg",
                                  content=_jpeg(png)))
        seen: set = set()
        paras = "".join(f"<p>{_ruby_para(book, p, seen)}</p>" for p in ch.paras)
        words = hard_words_py(book, "\n".join(ch.paras))
        rows = "".join(f"<tr><td class='w'>{html.escape(w)}</td><td class='p'>{html.escape(py)}</td>"
                       f"<td class='e'>{html.escape(english_for(book, w, py))}</td></tr>" for w, py in words)
        for w, py in words:
            all_gloss.setdefault(w, (py, english_for(book, w, py)))
        qs = "".join(f"<li>{html.escape(q)}</li>" for q, _ in ch.questions)
        body = (f"<p class='num'>第{NUMS[i]}章</p><h1>{html.escape(ch.title)}</h1>"
                f"<img class='art' src='{img_name}' alt=''/>{paras}"
                + (f"<h2>生詞</h2><table class='gloss'>{rows}</table>" if rows else "")
                + (f"<h2>想一想</h2><ol class='q'>{qs}</ol>" if qs else ""))
        c = page(f"ch{i + 1}.xhtml", ch.title, body)
        spine.append(c)
        toc.append(c)

    ans = "".join(f"<h2>第{NUMS[i]}章　{html.escape(c.title)}</h2><ol class='q ans'>"
                  + "".join(f"<li>{html.escape(a)}</li>" for _, a in c.questions) + "</ol>"
                  for i, c in enumerate(book.chapters) if c.questions)
    ans_pg = page("answers.xhtml", "參考答案", f"<h1>參考答案</h1>{ans}")
    vocab_rows = "".join(f"<tr><td class='w'>{html.escape(w)}</td><td class='p'>{html.escape(py)}</td>"
                         f"<td class='e'>{html.escape(e)}</td></tr>"
                         for w, (py, e) in sorted(all_gloss.items(), key=lambda kv: _plain(kv[1][0])))
    vocab_pg = page("vocab.xhtml", "詞彙表", f"<h1>詞彙表</h1><table class='gloss'>{vocab_rows}</table>")
    spine += [ans_pg, vocab_pg]
    toc += [ans_pg, vocab_pg]

    eb.toc = toc
    eb.spine = spine
    eb.add_item(epub.EpubNcx())
    eb.add_item(epub.EpubNav())
    out = Path(out_epub)
    epub.write_epub(str(out), eb)
    return out
