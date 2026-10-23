// cs-video cartoon kit: the reusable parts of a narrated cartoon explainer, on top of the
// animation-studio engine (G, Ch, Shots, Subs, Studio). Load after engine/video/boot.js, before film.js.
//
//   const K = Kit.init({ main: 'Inter, sans-serif', alt: 'Inter, sans-serif', mainWeight: 600 });
//   K.actor(ctx, style, x, y, s, t, { role: 'teacher', gesture: 'point', helmet: true, ... })
//   K.card(ctx, t, t0, t1, x, y, w, h, (c) => K.text(c, 'Sign', 0, 16, 48))   // a pop-up sign
//   K.title(ctx, t, t0, t1, 'Big title', 'small line')
//   Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, FOCUS) })              // wide or phone
//
// Everything is drawn on a 1920x1080 STAGE. In a 9:16 render (render.js --format 9:16) K.frame puts
// the stage in a middle band with the camera following FOCUS, moves every K.card / K.title to the top
// band (laid out in rows) and draws the captions bigger in the bottom band. So one film.js makes both.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, Subs = globalThis.Subs, VO = globalThis.VO;
  const { clamp, lerp, ease } = U;
  const W = 1920, H = 1080;

  // extra headwear for the engine's people: a climbing/safety helmet (with an optional beanie under it)
  const baseHeadwear = Ch.headwear;
  Ch.headwear = (ctx, st, seed = 1) => {
    if (st.headwear !== 'helmet') return baseHeadwear(ctx, st, seed);
    const c = st.headwearColor || '#33A6D8';
    const shade = (hex, f) => { const n = parseInt(hex.slice(1), 16); const ch = (v) => Math.max(0, Math.min(255, Math.round(v * f))); return `rgb(${ch(n >> 16)},${ch((n >> 8) & 255)},${ch(n & 255)})`; };
    for (const sd of [-1, 1]) G.line(ctx, [[sd * 64, -30], [sd * 60, 10], [sd * 44, 58]], { lw: 4, color: '#2B2B30', seed: seed + 230 + sd });
    if (st.beanie) G.rrect(ctx, -76, -34, 152, 20, 8, { fill: st.beanie, lw: 3, seed: seed + 229 });
    G.shape(ctx, [[-78, -26], [-80, -64], [-54, -100], [0, -114], [54, -100], [80, -64], [78, -26], [40, -36], [-40, -36]], { fill: c, lw: 4.5, seed: seed + 231, hatch: { color: 'rgba(0,0,0,0.12)', gap: 7 } });
    G.rrect(ctx, -84, -38, 168, 16, 8, { fill: shade(c, 0.72), lw: 3.5, seed: seed + 232 });
    for (const vx of [-30, 0, 30]) G.rrect(ctx, vx - 6, -100 + Math.abs(vx) * 0.25, 12, 26, 6, { fill: shade(c, 0.6), lw: 2, seed: seed + 233 + vx });
  };

  const Kit = {};
  Kit.init = ({ main = 'Inter, sans-serif', mainWeight = 600, alt = 'Inter, sans-serif', altWeight = 600, ink = '#1F1B17', muted = '#5D6B78',
    paper = '#F4F1EA', roles = {}, cardFont = null } = {}) => {
    const K = { W, H, VERT: G.H > G.W, OVER: [], roles };
    const VERT = K.VERT;
    K.text = (ctx, s, x, y, size, color = ink, align = 'center', fam = cardFont || main) => G.text(ctx, s, x, y, { size, fam, weight: mainWeight, color, align, boil: 0 });

    // ----- people -----
    // roles: { teacher: { voice: 'teacher', label: 'Ada', color: '#C25E18' } } maps a cast id to the VO speaker id
    K.actor = (ctx, style, x, y, s, t, o = {}) => {
      const st = Object.assign({}, style);
      if (o.helmet) { st.headwear = 'helmet'; st.headwearColor = o.helmetColor || st.helmetColor; }
      const p = {
        x, y, s, pose: o.walk != null ? 'walk' : 'stand', walk: o.walk || 0, style: st,
        blink: (t + (o.seed || 1) * 0.7) % 3.6 < 0.12 ? 1 : 0, look: o.look ?? 0, lookY: o.lookY ?? 0,
        eyes: o.eyes, brows: o.brows, gesture: o.gesture, handL: o.handL, handR: o.handR, mouth: o.mouth || 'smile',
        headRot: o.headRot || 0, rot: o.rot || 0, seed: 300 + (o.seed || 1) * 17,
      };
      if (o.role) { const mm = Subs.mouth(VO, t, o.role); if (mm.talking) p.mouth = mm; } // lip-sync to that speaker's lines
      Ch.person(ctx, p);
      return p;
    };
    K.head = (x, y, s) => [x, y - 404 * s]; // where a standing person's head centre is

    // ----- pop-up signs -----
    K.card = (ctx, t, t0, t1, x, y, w, h, inner, { rot = 0, seed = 1, fill = 'rgba(255,253,248,0.96)', stage = false } = {}) => {
      const a = clamp((t - t0) / 0.4), out = t1 == null ? 1 : clamp((t1 - t) / 0.3);
      if (a <= 0 || out <= 0) return;
      const k = ease.outBack(a) * (0.7 + 0.3 * out);
      const draw = (c) => { c.save(); c.globalAlpha *= out; c.rotate(rot); c.scale(k, k); G.tornPaper(c, -w / 2, -h / 2, w, h, { fill, seed, shadow: true }); inner(c); c.restore(); };
      if (VERT && !stage) { K.OVER.push({ x, w, h, draw }); return; }
      ctx.save(); ctx.translate(x, y); draw(ctx); ctx.restore();
    };
    // anything else for the phone's top band (drawn centred at 0,0 in a w x h box)
    K.overlay = (ctx, x, y, w, h, draw) => { if (VERT) K.OVER.push({ x, w, h, draw }); else { ctx.save(); ctx.translate(x, y); draw(ctx); ctx.restore(); } };
    K.title = (ctx, t, t0, t1, main_, sub, { w = 1200, h = 330 } = {}) => {
      const a = clamp((t - t0) / 0.5), out = t1 == null ? 1 : clamp((t1 - t) / 0.5);
      if (a <= 0 || out <= 0) return;
      const draw = (c) => {
        c.save(); c.globalAlpha *= a * out; const k = 0.92 + 0.08 * ease.outBack(a); c.scale(k, k);
        G.tornPaper(c, -w / 2, -h / 2, w, h, { fill: 'rgba(255,253,248,0.96)', seed: 12, shadow: true });
        K.text(c, main_, 0, sub ? 10 : 36, 104);
        if (sub) K.text(c, sub, 0, 92, 42, muted);
        c.restore();
      };
      if (VERT) { K.OVER.push({ big: true, x: W / 2, w, h, draw }); return; }
      ctx.save(); ctx.translate(W / 2, 260); draw(ctx); ctx.restore();
    };

    // ----- captions: the sentence being spoken, with an optional second-language line -----
    const lineAt = (t) => VO.lines.find((l) => t >= l.t - 0.1 && t <= l.end + 0.35);
    const sentence = (line, t) => {
      let si = 0; line.sents.forEach((s, i) => { if (t >= s[1] - 0.1) si = i; });
      const [text, s0, , altText] = line.sents[si];
      const lastS = si === line.sents.length - 1;
      return { si, text, altText, a: clamp((t - s0 + 0.12) / 0.15) * (lastS ? 1 - clamp((t - line.end - 0.15) / 0.2) : 1) };
    };
    const label = (line) => (roles[line.who] && roles[line.who].label) || '';
    const labelColor = (line) => (roles[line.who] && roles[line.who].color) || muted;
    K.caption = (ctx, t) => {
      const line = lineAt(t); if (!line) return;
      const { si, text, altText, a } = sentence(line, t);
      const size = 50, aSize = 29;
      const tw = Math.max(G.measure(ctx, text, size, main, mainWeight), altText ? G.measure(ctx, altText, aSize, alt, altWeight) : 0);
      const sc = Math.min(1, (W - 260) / tw), w = tw * sc, y = H - (altText ? 98 : 64);
      ctx.save(); ctx.globalAlpha = a;
      G.tornPaper(ctx, W / 2 - w / 2 - 46, y - 70, w + 92, altText ? 146 : 100, { fill: 'rgba(255,253,248,0.93)', seed: 7 + si, shadow: true });
      if (label(line)) G.text(ctx, label(line), W / 2 - w / 2 - 32, y - 48, { size: 20, fam: main, color: labelColor(line), boil: 0 });
      G.text(ctx, text, W / 2, y, { size: size * sc, fam: main, weight: mainWeight, color: ink, align: 'center', boil: 0 });
      if (altText) G.text(ctx, altText, W / 2, y + 48, { size: aSize * sc, fam: alt, weight: altWeight, color: muted, align: 'center', boil: 0 });
      ctx.restore();
    };
    // wrap: by character for CJK, by word otherwise; prefers a break after a comma near the middle
    K.wrap = (ctx, text, size, fam, weight, maxW) => {
      const cjk = /[㐀-鿿]/.test(text);
      const parts = cjk ? [...text] : text.split(/(?<= )/);
      const lines = []; let cur = '';
      for (const p of parts) { const s = cur + p; if (cur && G.measure(ctx, s.trim(), size, fam, weight) > maxW) { lines.push(cur.trim()); cur = p; } else cur = s; }
      if (cur.trim()) lines.push(cur.trim());
      if (lines.length === 2) {
        const cuts = [...text.matchAll(/[，、：；,;:]\s?/g)].map((m) => m.index + m[0].length).filter((i) => i < text.length - 1);
        cuts.sort((p, q) => Math.abs(p - text.length / 2) - Math.abs(q - text.length / 2));
        for (const i of cuts) { const A = text.slice(0, i).trim(), B = text.slice(i).trim(); if (G.measure(ctx, A, size, fam, weight) <= maxW && G.measure(ctx, B, size, fam, weight) <= maxW) return [A, B]; }
      }
      for (let i = 1; i < lines.length; i++) if (/^[，。！？、,.!?]/.test(lines[i])) { lines[i - 1] += lines[i][0]; lines[i] = lines[i].slice(1); }
      return lines.filter(Boolean);
    };

    // ----- phone (9:16) layout -----
    const TOP = 400, BAND = 1140, BOT = TOP + BAND, CY = 180;
    const SK = BAND / (H - CY), VIEW = G.W / SK; // stage px visible across the phone
    K.VIEW = VIEW;
    // focus keys: [time, x | (t) => x, cut?]; a cut jumps, otherwise the camera eases over 1.2 s
    const fval = (v, t) => (typeof v === 'function' ? v(t) : v);
    K.focusAt = (keys, t) => {
      let i = 0; while (i < keys.length - 1 && t >= keys[i + 1][0]) i++;
      const cur = keys[i], prev = keys[i - 1], x = fval(cur[1], t);
      if (!prev || cur[2]) return x;
      return lerp(fval(prev[1], t), x, ease.inOutCubic(clamp((t - cur[0]) / 1.2)));
    };
    let STAGE = null;
    K.frame = (ctx, t, film, focusKeys = [[0, W / 2]], { logo = null } = {}) => {
      if (!VERT) { film(ctx, t); K.caption(ctx, t); return; }
      if (!STAGE) STAGE = G.makeCanvas(W, H);
      const sc = STAGE.getContext('2d');
      K.OVER.length = 0;
      const gw = G.W, gh = G.H, gs = G.scale;
      G.W = W; G.H = H; G.scale = 1; // the stage is 1920x1080 for everything drawn on it (transitions too)
      sc.setTransform(1, 0, 0, 1, 0, 0); sc.globalAlpha = 1; sc.fillStyle = '#050508'; sc.fillRect(0, 0, W, H);
      try { film(sc, t); } finally { G.W = gw; G.H = gh; G.scale = gs; }
      ctx.fillStyle = paper; ctx.fillRect(0, 0, G.W, G.H);
      const fx = clamp(K.focusAt(focusKeys, t), VIEW / 2, W - VIEW / 2);
      ctx.drawImage(STAGE, fx - VIEW / 2, CY, VIEW, H - CY, 0, TOP, G.W, BAND);
      G.tornPaper(ctx, -20, TOP - 30, G.W + 40, 36, { fill: paper, seed: 3, shadow: true, tear: 6 });
      G.tornPaper(ctx, -20, BOT - 6, G.W + 40, 40, { fill: paper, seed: 4, shadow: true, tear: 6 });
      topBand(ctx, logo);
      captionV(ctx, t);
    };
    function topBand(ctx, logo) {
      const big = K.OVER.find((o) => o.big);
      if (big) { const k = Math.min((G.W - 60) / big.w, (TOP - 20) / big.h); ctx.save(); ctx.translate(G.W / 2, TOP / 2 - 6); ctx.scale(k, k); big.draw(ctx); ctx.restore(); return; }
      let areaY = 30;
      if (logo) { logo(ctx, G.W / 2, 64); areaY = 112; } // a small brand mark on top, if the film has one
      const items = K.OVER.slice().sort((a, b) => a.x - b.x);
      if (!items.length) return;
      const areaH = TOP - areaY - 26, maxW = G.W - 60, gap = 26;
      const rowsOf = (n) => (n === 1 ? [items] : [items.slice(0, Math.ceil(items.length / 2)), items.slice(Math.ceil(items.length / 2))]);
      let best = null;
      for (const n of items.length > 1 ? [1, 2] : [1]) {
        const rows = rowsOf(n);
        const k = Math.min(1, ...rows.map((r) => maxW / (r.reduce((s, o) => s + o.w, 0) + gap * (r.length - 1))),
          areaH / (rows.reduce((s, r) => s + Math.max(...r.map((o) => o.h)), 0) + gap * (rows.length - 1)));
        if (!best || k > best.k) best = { rows, k };
      }
      const { rows, k } = best;
      const totalH = rows.reduce((s, r) => s + Math.max(...r.map((o) => o.h)), 0) * k + gap * (rows.length - 1);
      let y = areaY + (areaH - totalH) / 2;
      for (const r of rows) {
        const rh = Math.max(...r.map((o) => o.h)) * k, rw = r.reduce((s, o) => s + o.w, 0) * k + gap * (r.length - 1);
        let x = (G.W - rw) / 2;
        for (const o of r) { ctx.save(); ctx.translate(x + o.w * k / 2, y + rh / 2); ctx.scale(k, k); o.draw(ctx); ctx.restore(); x += o.w * k + gap; }
        y += rh + gap;
      }
    }
    function captionV(ctx, t) {
      const line = lineAt(t); if (!line) return;
      const { si, text, altText, a } = sentence(line, t);
      const zs = 60, es = 36, maxW = G.W - 150;
      const zl = K.wrap(ctx, text, zs, main, mainWeight, maxW);
      const el = altText ? K.wrap(ctx, altText, es, alt, altWeight, maxW) : [];
      const h = zl.length * zs * 1.25 + el.length * es * 1.3 + 70;
      const y0 = BOT + 34 + (G.H - BOT - 34 - h) / 2;
      ctx.save(); ctx.globalAlpha = a;
      G.tornPaper(ctx, 36, y0, G.W - 72, h, { fill: 'rgba(255,253,248,0.97)', seed: 7 + si, shadow: true });
      if (label(line)) G.text(ctx, label(line), 64, y0 + 30, { size: 24, fam: main, color: labelColor(line), boil: 0 });
      let y = y0 + 44 + zs;
      for (const l of zl) { G.text(ctx, l, G.W / 2, y, { size: zs, fam: main, weight: mainWeight, color: ink, align: 'center', boil: 0 }); y += zs * 1.25; }
      y += 4;
      for (const l of el) { G.text(ctx, l, G.W / 2, y, { size: es, fam: alt, weight: altWeight, color: muted, align: 'center', boil: 0 }); y += es * 1.3; }
      ctx.restore();
    }
    return K;
  };
  globalThis.Kit = Kit;
})();
