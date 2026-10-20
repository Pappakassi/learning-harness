// THE FILM: Sam asks how to integrate x³eˣ; Ada solves it on the whiteboard with integration by parts,
// three rounds like recursive calls (a call stack fills on the board), then unwinds, checks the answer
// with the product rule and leaves a teaser. Pure function of t; all times from score.js.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots;
  const TEX = globalThis.TEX;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const INK = '#1F1B17', MUTED = '#5D6B78', F = '#D9622B', GC = '#2F7FB5', RED = '#C9352B', GOOD = '#3E9A4A', HI = '#F2C94C';
  const HAND = '"Patrick Hand", sans-serif';
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: HAND,
    roles: { teacher: { label: 'Ada', color: '#C25E18' }, student: { label: 'Sam', color: GC } } });
  const between = (t, a, b) => t >= a && t < b;

  const CAST = {
    teacher: { skin: Ch.SKIN_TONES[2], hair: '#2A1E18', hairStyle: 'bun', outfit: 'shirt', shirt: '#E2782C', trim: '#B85A1C', bottoms: 'pants', shorts: '#2E3440', glasses: 'round', shoes: '#4A3426' },
    student: { skin: Ch.SKIN_TONES[0], hair: '#9A7350', hairStyle: 'quiff', outfit: 'hoodie', shirt: '#3B7EA1', trim: '#2B5E79', bottoms: 'pants', shorts: '#3A3F4A', shoes: '#5A4232', eyeColor: '#6E9FC4' },
  };
  globalThis.CAST = CAST;

  // ---------- formulas (LaTeX → SVG by cartoon/tex.py) ----------
  const IMG = {};
  async function loadTex() { await Promise.all(Object.keys(TEX).map(async (k) => { IMG[k] = await Studio.loadImage(`assets/tex/${k}.svg`); })); }
  const PX = 4.6; // screen px per TeX pt (one size for everything, so letters match across lines)
  const size = (name, s = PX, maxW = 1e9) => { const k = Math.min(s, maxW / TEX[name].w); return [TEX[name].w * k, TEX[name].h * k]; };
  // write a formula on: revealed left to right with a pen dot at the edge; (x, y) = left (or centre) edge, vertical middle
  function math(ctx, name, x, y, t, t0, { s = PX, align = 'left', maxW = 880, dur } = {}) {
    const img = IMG[name]; if (!img || t < t0) return null;
    const [w, h] = size(name, s, maxW);
    const d = dur ?? 0.45 + w / 1100;
    const u = ease.inOutQuad(clamp((t - t0) / d));
    const x0 = align === 'center' ? x - w / 2 : x, y0 = y - h / 2;
    ctx.save(); ctx.beginPath(); ctx.rect(x0 - 4, y0 - 10, (w + 8) * u, h + 20); ctx.clip();
    ctx.drawImage(img, x0, y0, w, h); ctx.restore();
    if (u > 0 && u < 1) { ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(x0 + w * u, y0 + h * (0.55 + 0.25 * Math.sin(t * 40)), 4, 0, Math.PI * 2); ctx.fill(); }
    return { x: x0, y: y0, w, h };
  }
  const hand = (ctx, s, x, y, sz, color = INK, align = 'left') => G.text(ctx, s, x, y, { size: sz, fam: HAND, weight: 400, color, align, boil: 0 });

  // ---------- the room and the board ----------
  const BX = 330, BY = 90, BW = 1260, BH = 610; // board
  const MX = 380, SPX = 1320; // math area left edge, call-stack panel left edge
  function room(ctx) {
    ctx.fillStyle = '#EFE6D6'; ctx.fillRect(-200, -200, 2400, 1500);
    G.poly(ctx, [[-100, 860], [2020, 850], [2020, 1200], [-100, 1200]], { fill: '#B98E62', lw: 4, seed: 11, step: 60, hatch: { color: 'rgba(80,40,10,0.18)', gap: 14, angle: 0.05 } });
  }
  function board(ctx) {
    G.rrect(ctx, BX, BY, BW, BH, 14, { fill: '#FBFBF7', lw: 6, seed: 21, hatch: { color: 'rgba(0,0,0,0.035)', gap: 16 } });
    G.rrect(ctx, BX - 20, BY + BH - 10, BW + 40, 22, 6, { fill: '#9AA3AD', lw: 4, seed: 22 });
    for (const [x, c] of [[BX + 80, '#C9352B'], [BX + 120, '#2F7FB5'], [BX + 160, '#3E9A4A']]) G.rrect(ctx, x, BY + BH - 22, 32, 12, 4, { fill: c, lw: 2.5, seed: 23 + x });
  }

  // ---------- the call stack (one frame per round) ----------
  const FRAMES = [
    { tex: 's1', val: null, push: ev.r1, pop: ev.pop1 },
    { tex: 's2', val: 'v2', push: ev.r2, pop: ev.pop2 },
    { tex: 's3', val: 'v3', push: ev.r3, pop: ev.pop3 },
  ];
  function stack(ctx, t) {
    if (t < ev.r1 - 0.4 || t > ev.pop1 + 0.6) return; // the panel exists only while there are frames
    ctx.save(); ctx.globalAlpha *= clamp((t - ev.r1 + 0.4) / 0.3) * (1 - clamp((t - ev.pop1) / 0.6));
    ctx.save(); ctx.setLineDash([10, 10]); ctx.strokeStyle = 'rgba(31,27,23,0.35)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(SPX - 20, BY + 30); ctx.lineTo(SPX - 20, BY + BH - 40); ctx.stroke(); ctx.restore();
    hand(ctx, 'call stack', SPX + 115, BY + 54, 34, MUTED, 'center');
    ctx.restore();
    FRAMES.forEach((f, i) => {
      const inU = ease.outBack(clamp((t - f.push) / 0.45));
      const outU = clamp((t - f.pop) / 0.6);
      if (inU <= 0 || outU >= 1) return;
      const y = BY + BH - 90 - i * 120 - (1 - inU) * 260 - ease.inQuad(outU) * 120;
      ctx.save(); ctx.globalAlpha *= clamp(inU * 2) * (1 - outU);
      const top = i === FRAMES.filter((g) => t >= g.push && t < g.pop).length - 1;
      G.rrect(ctx, SPX - 6, y - 50, 246, 100, 12, { fill: top ? '#FFF4D6' : '#FFFFFF', lw: 3.5, seed: 60 + i });
      hand(ctx, `round ${i + 1}`, SPX + 8, y - 22, 26, MUTED);
      math(ctx, f.tex, SPX + 125, y + 16, t, f.push, { s: 3.2, align: 'center', dur: 0.01 });
      ctx.restore();
    });
  }

  // the power going down: x³ → x² → x → 1, along the bottom of the board during the rounds
  function powers(ctx, t) {
    if (t < ev.smaller - 0.2 || t > ev.unwind - 0.3) return;
    const steps = [['p3', ev.smaller - 0.2], ['p2', ev.smaller + 0.5], ['p1', ev.r3a], ['p0', ev.base + 0.2]];
    const y = BY + BH - 70;
    hand(ctx, 'power:', MX, y + 12, 34, MUTED);
    steps.forEach(([n, t0], i) => {
      if (t < t0) return;
      const x = MX + 140 + i * 150;
      const cur = i === steps.filter(([, s]) => t >= s).length - 1;
      if (i > 0) { const a = clamp((t - t0) / 0.3); ctx.save(); ctx.globalAlpha *= a; hand(ctx, '→', x - 80, y + 14, 44, MUTED); ctx.restore(); }
      if (cur) { ctx.save(); ctx.globalAlpha *= 0.5; G.ellipse(ctx, x + 20, y, 46, 36, { fill: HI, lw: 0, seed: 70 + i }); ctx.restore(); }
      math(ctx, n, x + 20, y, t, t0, { s: 5.5, align: 'center', dur: 0.2 });
    });
    if (t > ev.base + 0.2) { const a = ease.outBack(clamp((t - ev.base - 0.4) / 0.4)); ctx.save(); ctx.translate(MX + 800, y); ctx.scale(a, a); hand(ctx, 'no ∫ left ✓', 0, 12, 40, GOOD, 'center'); ctx.restore(); }
  }

  // ---------- board pages ----------
  const PAGES = {
    intro(ctx, t) {
      math(ctx, 'problem', 960 - 60, 190, t, ev.problem, { s: 5.6, align: 'center' });
      if (t > ev.plan + 0.2) { const a = clamp((t - ev.plan - 0.2) / 0.4); ctx.save(); ctx.globalAlpha *= a; hand(ctx, 'integration by parts', 900, 300, 50, F, 'center'); ctx.restore(); }
      math(ctx, 'formula', 860, 400, t, ev.formula, { align: 'center', maxW: 900 });
      math(ctx, 'pickf', 640, 530, t, ev.pickf, { s: 5.2, align: 'center' });
      if (t > ev.pickf) hand(ctx, 'differentiate: gets simpler', 640, 610, 34, MUTED, 'center');
      math(ctx, 'pickg', 1100, 530, t, ev.pickg, { s: 5.2, align: 'center' });
      if (t > ev.pickg + 0.6) hand(ctx, 'integrate: stays eˣ', 1100, 610, 34, MUTED, 'center');
    },
    r1(ctx, t) {
      hand(ctx, 'Round 1', MX, 160, 48, F);
      math(ctx, 'r1a', MX + 200, 160, t, ev.r1a, { s: 4.2 });
      math(ctx, 'r1b', MX + 560, 160, t, ev.r1b, { s: 4.2 });
      math(ctx, 'r1c', MX, 290, t, ev.r1c);
      const d = math(ctx, 'r1d', MX + 160, 410, t, ev.r1d);
      if (d && t > ev.still) { // the integral that's still there
        const a = clamp((t - ev.still) / 0.4);
        ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = RED; ctx.lineWidth = 5;
        ctx.beginPath(); ctx.ellipse(d.x + d.w * 0.74, d.y + d.h / 2, d.w * 0.3, d.h * 0.62, -0.04, 0, Math.PI * 2 * clamp((t - ev.still) / 0.6)); ctx.stroke();
        ctx.restore();
      }
      if (t > ev.recursive) { const a = clamp((t - ev.recursive) / 0.4); ctx.save(); ctx.globalAlpha *= a; hand(ctx, 'same move again ↻', MX + 600, 530, 42, GC); ctx.restore(); }
    },
    r2(ctx, t) {
      hand(ctx, 'Round 2', MX, 160, 48, F);
      math(ctx, 'r2a', MX + 200, 160, t, ev.r2a, { s: 4.2 });
      math(ctx, 'r2b', MX + 560, 160, t, ev.r2b, { s: 4.2 });
      math(ctx, 'r2c', MX, 320, t, ev.r2c);
    },
    r3(ctx, t) {
      hand(ctx, 'Round 3', MX, 160, 48, F);
      math(ctx, 'r3a', MX + 200, 160, t, ev.r3a, { s: 4.2 });
      math(ctx, 'r3b', MX + 560, 160, t, ev.r3b, { s: 4.2 });
      math(ctx, 'r3c', MX, 300, t, ev.r3c);
      const d = math(ctx, 'r3d', MX + 230, 420, t, ev.r3d);
      if (d && t > ev.base) { ctx.save(); ctx.globalAlpha *= 0.35; G.rrect(ctx, d.x - 12, d.y - 14, d.w + 24, d.h + 28, 10, { fill: GOOD, lw: 0, seed: 81 }); ctx.restore(); }
    },
    unwind(ctx, t) {
      hand(ctx, 'Unwind', MX, 160, 48, GOOD);
      math(ctx, 'u2a', MX, 250, t, ev.u2a);
      math(ctx, 'u2b', MX + 200, 350, t, ev.u2b);
      math(ctx, 'u1a', MX, 480, t, ev.u1a, { maxW: 900 });
      math(ctx, 'u1b', MX + 200, 590, t, ev.u1b, { maxW: 720 });
    },
    final(ctx, t) {
      hand(ctx, 'Answer', MX, 160, 48, GOOD);
      const d = math(ctx, 'final', 860, 380, t, ev.finalW, { s: 5.0, align: 'center', dur: 1.6, maxW: 860 });
      if (d && t > ev.box) {
        const u = clamp((t - ev.box) / 0.8);
        ctx.save(); ctx.strokeStyle = GOOD; ctx.lineWidth = 6; ctx.setLineDash([2000]); ctx.lineDashOffset = 2000 * (1 - u);
        ctx.strokeRect(d.x - 30, d.y - 26, d.w + 60, d.h + 52); ctx.restore();
      }
    },
    check(ctx, t) {
      hand(ctx, 'Check: differentiate', MX, 160, 48, F);
      math(ctx, 'final', MX + 460, 250, t, ev.check - 0.3, { s: 3.4, align: 'center', dur: 0.01 });
      math(ctx, 'c1', MX - 20, 390, t, ev.c1, { maxW: 1180, dur: 2.2 });
      const d = math(ctx, 'c2', MX + 520, 520, t, ev.c2, { s: 5.2 });
      if (d && t > ev.ok) { const a = ease.outBack(clamp((t - ev.ok) / 0.4)); ctx.save(); ctx.translate(d.x + d.w + 120, d.y + d.h / 2); ctx.scale(a, a); hand(ctx, 'it checks out!', 0, 12, 44, GOOD, 'center'); ctx.restore(); }
    },
  };
  function pageAt(t) { let p = S.pages[0]; for (const q of S.pages) if (t >= q[1]) p = q; return p; }
  function boardContent(ctx, t) {
    const [id, t0] = pageAt(t);
    const i = S.pages.findIndex((p) => p[0] === id);
    const u = clamp((t - t0) / 0.35);
    if (i > 0 && u < 1) { // the previous page wipes away
      ctx.save(); ctx.globalAlpha *= 1 - u; PAGES[S.pages[i - 1][0]](ctx, t); ctx.restore();
      // an eraser swipe
      ctx.save(); ctx.globalAlpha *= Math.sin(Math.PI * u) * 0.8;
      G.rrect(ctx, lerp(BX, BX + BW - 300, u), BY + 120, 140, 70, 10, { fill: '#5A6470', lw: 3, seed: 91 });
      ctx.restore();
      return;
    }
    PAGES[id](ctx, t);
  }

  // ---------- acting ----------
  function people(ctx, t) {
    const st = { role: 'student', look: 0.7, seed: 2 };
    if (t < ev.plan) { st.gesture = 'think'; st.brows = 'up'; }
    if (between(t, ev.still - 0.1, ev.smaller)) { st.eyes = 'wide'; st.brows = 'up'; st.gesture = 'shrug'; }
    if (between(t, ev.base - 0.1, ev.unwind)) { st.gesture = 'cheer'; st.eyes = 'happy'; }
    if (between(t, ev.pause0, ev.pause1)) { st.gesture = 'think'; st.look = 0.9; }
    if (between(t, ev.ok, ev.wow + 1.5)) { st.gesture = 'thumbsUp'; st.eyes = 'happy'; }
    K.actor(ctx, CAST.student, 170, 935, 0.72, t, st);
    const te = { role: 'teacher', look: -0.6, seed: 1 };
    const explaining = [[ev.formula, ev.pickg + 2.5], [ev.r1a, ev.r1d + 2], [ev.r2a, ev.r2c + 3], [ev.r3a, ev.r3d + 2], [ev.u2a, ev.u1b + 2.5], [ev.box - 0.5, ev.box + 2], [ev.c1, ev.ok]];
    if (explaining.some(([a, b]) => between(t, a, b))) { te.handL = [-215, -300 + 30 * Math.sin(t * 1.3)]; te.look = -0.9; }
    if (between(t, ev.base, ev.unwind)) te.gesture = 'thumbsUp';
    if (between(t, ev.yourturn, ev.pause1)) { te.gesture = 'point'; te.look = 0.2; }
    if (t > ev.teaser) { te.gesture = 'pointUp'; te.look = -0.3; }
    K.actor(ctx, CAST.teacher, 1760, 945, 0.74, t, te);
  }

  // ---------- signs ----------
  function signs(ctx, t) {
    // your turn: a countdown ring while the viewer pauses
    K.card(ctx, t, ev.yourturn, ev.pause1 + 0.2, 960, 55, 520, 100, (c) => {
      hand(c, 'Your turn: check it!', -40, 14, 46, INK, 'center');
      const u = clamp((t - ev.pause0) / (ev.pause1 - ev.pause0));
      c.save(); c.lineWidth = 8; c.strokeStyle = '#E3DED5'; c.beginPath(); c.arc(205, 0, 30, 0, Math.PI * 2); c.stroke();
      c.strokeStyle = F; c.beginPath(); c.arc(205, 0, 30, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (1 - u)); c.stroke(); c.restore();
      if (t > ev.pause0) hand(c, String(Math.max(1, Math.ceil(3 * (1 - u)))), 205, 12, 34, INK, 'center');
    }, { seed: 5 });
    K.card(ctx, t, ev.teaser, null, 960, 60, 560, 110, (c) => { hand(c, 'Next:', -200, 14, 40, MUTED); math(c, 'teaser', 50, 0, t, ev.teaser + 0.2, { s: 3.6, align: 'center' }); }, { rot: -0.02, seed: 6 });
  }

  function shotBoard(ctx, t) { room(ctx); board(ctx); boardContent(ctx, t); stack(ctx, t); powers(ctx, t); people(ctx, t); signs(ctx, t); }
  function shotOutro(ctx, t) {
    room(ctx);
    K.title(ctx, t, ev.outro, null, 'Integration by parts', 'repeat until no ∫ is left, then unwind');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => shotBoard(ctx, t), cam: (s) => {
      // gentle push-ins on the key moments, back out between them
      const k = [[0, 1, 0, 0], [ev.formula, 1.0, 0, 0], [ev.formula + 1, 1.05, -30, 0], [ev.pickg + 2, 1.05, -30, 0], [ev.r1, 1.0, 0, 0], [ev.final, 1.0, 0, 0], [ev.box, 1.06, -30, 0], [ev.yourturn, 1.0, 0, 0], [S.DURATION, 1, 0, 0]];
      let i = 0; while (i < k.length - 2 && s.t > k[i + 1][0]) i++;
      const u = ease.inOutCubic(clamp((s.t - k[i][0]) / Math.max(0.001, k[i + 1][0] - k[i][0])));
      return { zoom: lerp(k[i][1], k[i + 1][1], u), x: lerp(k[i][2], k[i + 1][2], u), y: lerp(k[i][3], k[i + 1][3], u) };
    } },
    { at: S.cuts.outro, draw: (ctx, t) => shotOutro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);

  Studio.film({
    async init() { await loadTex(); },
    draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]),
    post: { paper: 0.35, vignette: 0.18, grain: 0.035 },
    fadeOut: 1.0,
  });
})();
