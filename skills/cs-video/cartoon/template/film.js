// THE FILM (demo): a student asks how to find a number among a thousand sorted ones; the teacher
// shows binary search on a whiteboard. Replace the scenes with your topic; keep the K.* parts.
// Pure function of t; all times from score.js (which reads vo.js).
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const INK = '#1F1B17', MUTED = '#5D6B78', HI = '#E9B73E', OUT = '#C9C3B8', GOOD = '#3E9A4A';
  const MAIN = '"Patrick Hand", "Noto Sans CJK SC", sans-serif'; // the hand-drawn font; for Chinese films use a CJK font
  const K = Kit.init({ main: 'Inter, "Noto Sans CJK SC", sans-serif', mainWeight: 600, cardFont: MAIN,
    roles: { teacher: { label: 'Ada', color: '#C25E18' }, student: { label: 'Sam', color: '#2F7FB5' } } });

  // ---------- cast (any Ch.person style: skin, hair, hairStyle, outfit, shirt, glasses, headwear, eyeColor ...) ----------
  const CAST = {
    teacher: { skin: Ch.SKIN_TONES[1], hair: '#3A2A20', hairStyle: 'bun', outfit: 'shirt', shirt: '#E2782C', trim: '#B85A1C', bottoms: 'pants', shorts: '#2E3440', glasses: 'round', shoes: '#4A3426' },
    student: { skin: Ch.SKIN_TONES[0], hair: '#6A4A2A', hairStyle: 'quiff', outfit: 'hoodie', shirt: '#3B7EA1', trim: '#2B5E79', bottoms: 'pants', shorts: '#3A3F4A', shoes: '#5A4232' },
  };
  globalThis.CAST = CAST; // for `render.js cast` (an audition sheet)

  // ---------- scenery ----------
  function room(ctx) {
    ctx.fillStyle = '#EFE6D6'; ctx.fillRect(-200, -200, 2400, 1500);
    G.poly(ctx, [[-100, 860], [2020, 850], [2020, 1200], [-100, 1200]], { fill: '#B98E62', lw: 4, seed: 11, step: 60, hatch: { color: 'rgba(80,40,10,0.18)', gap: 14, angle: 0.05 } });
  }
  // the whiteboard with 16 sorted numbers standing for the thousand
  const NUMS = [3, 8, 12, 17, 21, 26, 30, 34, 41, 47, 52, 58, 63, 70, 76, 88];
  function board(ctx, t) {
    // the phone shows ~850 stage px across, so the board is narrower there (K.VERT = 9:16 render)
    const bx = K.VERT ? 960 : 1140, bw = K.VERT ? 820 : 1240;
    G.rrect(ctx, bx - bw / 2, 150, bw, 520, 14, { fill: '#FBFBF7', lw: 6, seed: 21, hatch: { color: 'rgba(0,0,0,0.04)', gap: 16 } });
    G.rrect(ctx, bx - bw / 2 - 20, 660, bw + 40, 22, 6, { fill: '#9AA3AD', lw: 4, seed: 22 });
    const n = NUMS.length, cw = K.VERT ? 47 : 68, x0 = bx - (n * cw) / 2, y = 380;
    // which part is still "alive": all, then the left half after the halving
    const cut = clamp((t - ev.halve) / 0.6);
    NUMS.forEach((v, i) => {
      const x = x0 + i * cw;
      const mid = i === 7 && t > ev.middle;
      const gone = i >= 7 && cut > 0;
      ctx.save(); ctx.globalAlpha = gone ? 1 - 0.65 * cut : 1;
      const drop = gone ? cut * 26 : 0;
      G.rrect(ctx, x + 4, y - 40 + drop, cw - 8, 80, 10, { fill: mid ? HI : gone ? OUT : '#FFFFFF', lw: 3.5, seed: 30 + i });
      G.text(ctx, String(v), x + cw / 2, y + 14 + drop, { size: K.VERT ? 26 : 34, fam: MAIN, weight: 400, color: INK, align: 'center', boil: 0 });
      ctx.restore();
    });
    if (t > ev.middle) { // the arrow on the middle one
      const a = ease.outBack(clamp((t - ev.middle) / 0.4));
      G.line(ctx, [[x0 + 7.5 * cw, 250 + 20 * (1 - a)], [x0 + 7.5 * cw, 320]], { lw: 6, color: INK, seed: 40 });
      G.line(ctx, [[x0 + 7.5 * cw - 14, 304], [x0 + 7.5 * cw, 322], [x0 + 7.5 * cw + 14, 304]], { lw: 6, color: INK, seed: 41 });
    }
    // the countdown of how many are left: 1000 -> 500 -> 250 ... -> 1
    if (t > ev.count) {
      const steps = [[ev.count, '1000'], [ev.n500, '500'], [ev.n250, '250'], [ev.ten, '... 1']];
      steps.forEach(([t0, s], i) => {
        const a = ease.outBack(clamp((t - t0) / 0.35));
        if (a <= 0) return;
        ctx.save(); ctx.translate(bx - bw / 2 + 110 + i * (bw - 220) / 3.4, 560); ctx.scale(a, a);
        G.text(ctx, s, 0, 0, { size: 52, fam: MAIN, weight: 400, color: i === 3 ? GOOD : INK, align: 'left', boil: 0 });
        ctx.restore();
      });
    }
  }

  // ---------- shots ----------
  function shotBoard(ctx, t) {
    room(ctx);
    board(ctx, t);
    // the student wonders, then is amazed; the teacher points at the board while explaining
    const sOpts = { role: 'student', look: 0.7, seed: 2 };
    if (t < ev.middle) { sOpts.gesture = 'think'; sOpts.brows = 'up'; }
    if (t > ev.wow - 0.2 && t < ev.count) { sOpts.eyes = 'wide'; sOpts.brows = 'up'; }
    if (t > ev.ten + 0.3) { sOpts.gesture = 'cheer'; sOpts.eyes = 'happy'; }
    K.actor(ctx, CAST.student, 260, 930, 0.72, t, sOpts);
    const tOpts = { role: 'teacher', look: -0.4, seed: 1 };
    if (t > ev.middle - 0.3 && t < ev.wow) { tOpts.gesture = 'pointUp'; tOpts.look = 0.4; }
    if (t > ev.count) tOpts.gesture = 'thumbsUp';
    K.actor(ctx, CAST.teacher, K.VERT ? 1500 : 1820, 940, 0.74, t, tOpts);
    // pop-up signs (they move to the top band in the phone version)
    K.card(ctx, t, ev.middle, ev.wow, 1140, 90, 520, 120, (c) => K.text(c, 'Look at the middle', 0, 18, 52, INK, 'center', MAIN), { seed: 5 });
    K.card(ctx, t, ev.halve, ev.count, 1640, 90, 380, 120, (c) => K.text(c, 'Half is gone!', 0, 18, 52, '#C9352B', 'center', MAIN), { rot: 0.03, seed: 6 });
    K.card(ctx, t, ev.ten, null, 1140, 90, 460, 120, (c) => K.text(c, '~10 looks', 0, 18, 56, GOOD, 'center', MAIN), { rot: -0.02, seed: 7 });
  }
  function shotOutro(ctx, t) {
    room(ctx);
    K.title(ctx, t, ev.outro, null, 'Binary search', 'halve it, again and again');
  }

  const film = Shots.film([
    { at: 0, draw: (ctx, t) => shotBoard(ctx, t), cam: (s) => ({ zoom: lerp(1, 1.05, ease.inOutQuad(s.u)) }) },
    { at: S.cuts.outro, draw: (ctx, t) => shotOutro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  // where the phone version's camera looks: [time, stage x, cut?]
  const FOCUS = [[0, 420, true], [ev.middle - 0.4, 1000], [ev.wow - 0.3, 520], [ev.count - 0.2, 960], [S.cuts.outro, 960, true]];

  Studio.film({
    draw: (ctx, t) => K.frame(ctx, t, film, FOCUS),
    post: { paper: 0.4, vignette: 0.2, grain: 0.04 },
    fadeOut: 1.0,
  });
})();
