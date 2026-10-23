// TSAM series: shared cast and props for the cartoon cold opens. Load after kit.js, before film.js.
// Everything draws on the 1920x1080 stage; the floor line is y = 860, actors stand at y ~ 930.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch;
  const { clamp, lerp, ease } = U;
  const TP = {};
  TP.INK = '#1F1B17'; TP.MUTED = '#5D6B78'; TP.RED = '#D8443A'; TP.GREEN = '#3E9A4A'; TP.BLUE = '#2F7FB5';
  TP.ORANGE = '#E2782C'; TP.PURPLE = '#7B4FB8'; TP.YELLOW = '#E9B73E'; TP.PINK = '#E0507A'; TP.TEAL = '#1E9C9C';
  TP.HAND = '"Patrick Hand", sans-serif';

  TP.CAST = {
    sam: { skin: Ch.SKIN_TONES[1], hair: '#4A3020', hairStyle: 'quiff', outfit: 'hoodie', shirt: '#2F8FCF', trim: '#1F6A9C', bottoms: 'pants', shorts: '#2E3440', shoes: '#4A3426', eyeColor: '#3B7A57' },
    ada: { skin: Ch.SKIN_TONES[3], hair: '#1F1612', hairStyle: 'bun', outfit: 'shirt', shirt: '#E2782C', trim: '#B85A1C', bottoms: 'pants', shorts: '#3A3F4A', glasses: 'round', shoes: '#3A2A20', eyeColor: '#5A3A20' },
    mallory: { skin: Ch.SKIN_TONES[0], hair: '#111111', hairStyle: 'short', outfit: 'hoodie', shirt: '#3A2F4F', trim: '#241C33', bottoms: 'pants', shorts: '#1E1E24', glasses: 'sun', shoes: '#111111' },
  };
  TP.ROLES = { sam: { label: 'Sam', color: '#2F7FB5' }, ada: { label: 'Ada', color: '#C25E18' }, mallory: { label: 'Mallory', color: '#6A3FA0' } };

  // ---------- rooms ----------
  TP.room = (ctx, { wall = '#F2E6D0', floor = '#B98E62', stripe = null, window = null } = {}) => {
    ctx.fillStyle = wall; ctx.fillRect(-300, -300, 2600, 1700);
    if (stripe) { ctx.fillStyle = stripe; ctx.fillRect(-300, 560, 2600, 300); G.line(ctx, [[-300, 560], [2300, 560]], { lw: 4, seed: 3 }); }
    if (window) {
      const [x, y] = window;
      G.rrect(ctx, x, y, 360, 260, 10, { fill: '#BFE3F2', lw: 6, seed: 5 });
      G.ellipse(ctx, x + 270, y + 70, 40, 40, { fill: '#F8D45C', lw: 3, seed: 6 });
      G.poly(ctx, [[x + 10, y + 250], [x + 120, y + 150], [x + 210, y + 220], [x + 290, y + 160], [x + 350, y + 250]], { fill: '#8FB89A', lw: 3, seed: 7 });
      G.line(ctx, [[x + 180, y], [x + 180, y + 260]], { lw: 5, seed: 8 });
      G.line(ctx, [[x, y + 130], [x + 360, y + 130]], { lw: 5, seed: 9 });
    }
    G.poly(ctx, [[-300, 860], [2300, 850], [2300, 1400], [-300, 1400]], { fill: floor, lw: 4, seed: 11, step: 60, hatch: { color: 'rgba(80,40,10,0.18)', gap: 14, angle: 0.05 } });
  };

  TP.desk = (ctx, x, w = 420, top = 760, color = '#9C6B43') => {
    G.rrect(ctx, x - w / 2, top, w, 26, 6, { fill: color, lw: 4, seed: 21 + x % 7 });
    for (const lx of [x - w / 2 + 24, x + w / 2 - 44]) G.rrect(ctx, lx, top + 24, 20, 860 - top + 40, 4, { fill: G.tint(color, -0.15), lw: 3.5, seed: 22 + lx % 5 });
  };

  // laptop seen from the side-front, screen faces the viewer a little; screen(ctx, w, h) draws inside
  TP.laptop = (ctx, x, y, s = 1, screen = null, { seed = 1, lid = '#3A4250' } = {}) => {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.rrect(ctx, -130, -170, 260, 170, 12, { fill: lid, lw: 4, seed });
    G.rrect(ctx, -116, -158, 232, 146, 6, { fill: '#DDF1F7', lw: 2.5, seed: seed + 1 });
    if (screen) { ctx.save(); ctx.translate(0, -85); screen(ctx, 232, 146); ctx.restore(); }
    G.poly(ctx, [[-160, 0], [160, 0], [140, 18], [-140, 18]], { fill: '#8D95A3', lw: 4, seed: seed + 2 });
    ctx.restore();
  };

  // a router with antennas, blinking lights and a face. mood: 'calm' | 'busy' | 'angry' | 'door'
  TP.router = (ctx, x, y, s, t, mood = 'calm', { seed = 4, label = '' } = {}) => {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    const shake = mood === 'angry' ? Math.sin(t * 40) * 4 : 0;
    ctx.translate(shake, 0);
    for (const ax of [-70, 70]) G.line(ctx, [[ax, -60], [ax * 1.2, -170]], { lw: 7, seed: seed + ax });
    for (const ax of [-70, 70]) G.ellipse(ctx, ax * 1.2, -172, 9, 9, { fill: TP.INK, lw: 2, seed: seed + 3 });
    const body = mood === 'angry' ? '#F2B2A8' : mood === 'busy' ? '#F7DE9B' : '#DCE6EF';
    G.rrect(ctx, -130, -70, 260, 110, 22, { fill: body, lw: 5, seed: seed + 5 });
    // eyes
    const blink = (t * 0.9 + seed) % 3.3 < 0.12;
    for (const ex of [-40, 40]) {
      if (blink) G.line(ctx, [[ex - 12, -30], [ex + 12, -30]], { lw: 5, seed: seed + ex });
      else G.ellipse(ctx, ex, -30, 11, mood === 'angry' ? 8 : 13, { fill: TP.INK, lw: 2, seed: seed + ex });
      if (mood === 'angry') G.line(ctx, [[ex - 20, -54 + (ex < 0 ? -6 : 6)], [ex + 20, -54 + (ex < 0 ? 6 : -6)]], { lw: 5, seed: seed + ex + 1 });
    }
    if (mood === 'angry') G.line(ctx, [[-22, 4], [-8, -4], [8, 4], [22, -4]], { lw: 4.5, seed: seed + 9, step: 6 });
    else G.line(ctx, [[-18, -2], [0, 6], [18, -2]], { lw: 4.5, seed: seed + 9 });
    // lights
    for (let i = 0; i < 5; i++) {
      const on = Math.sin(t * (mood === 'calm' ? 3 : 11) + i * 1.7) > (mood === 'calm' ? 0.2 : -0.3);
      G.ellipse(ctx, -80 + i * 40, 22, 7, 7, { fill: on ? (mood === 'angry' ? TP.RED : TP.GREEN) : '#7A8478', lw: 2, seed: seed + 20 + i });
    }
    if (mood === 'angry') for (let i = 0; i < 3; i++) { const p = ((t * 1.2 + i / 3) % 1); G.text(ctx, '!', 150 + i * 26, -70 - p * 40, { size: 50, fam: TP.HAND, color: TP.RED, alpha: 1 - p, boil: 0 }); }
    if (label) G.text(ctx, label, 0, 90, { size: 40, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 });
    ctx.restore();
  };

  // a cardboard parcel (a packet)
  TP.parcel = (ctx, x, y, s = 1, color = '#D9A86C', label = '', rot = 0, seed = 1) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    G.rrect(ctx, -40, -32, 80, 64, 6, { fill: color, lw: 4, seed });
    G.line(ctx, [[-40, -6], [40, -6]], { lw: 3, color: 'rgba(60,30,10,0.55)', seed: seed + 1 });
    if (label) G.text(ctx, label, 0, 22, { size: 28, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 });
    ctx.restore();
  };

  // position along a throw: an arc from a to b between t0 and t0+dur; null before, the end point after
  TP.fly = (t, t0, dur, a, b, h = 180) => {
    if (t < t0) return null;
    const u = clamp((t - t0) / dur);
    return { x: lerp(a[0], b[0], u), y: lerp(a[1], b[1], u) - Math.sin(Math.PI * u) * h, u, rot: u * 6 };
  };

  TP.basket = (ctx, x, y, fill = 0, { seed = 31 } = {}) => {
    // parcels stacked inside, 0..1
    const n = Math.round(fill * 6);
    for (let i = 0; i < n; i++) TP.parcel(ctx, x - 60 + (i % 3) * 60, y - 40 - Math.floor(i / 3) * 52, 0.75, ['#D9A86C', '#C99358', '#E6B97A'][i % 3], '', (i % 2 ? 0.08 : -0.06), seed + i);
    G.poly(ctx, [[x - 130, y - 70], [x + 130, y - 70], [x + 105, y + 40], [x - 105, y + 40]], { fill: '#C8955A', lw: 5, seed, hatch: { color: 'rgba(80,40,10,0.35)', gap: 16, angle: 0.8 } });
    G.text(ctx, fill >= 1 ? 'FULL' : 'buffer', x, y + 10, { size: 36, fam: TP.HAND, color: fill >= 1 ? TP.RED : TP.INK, align: 'center', boil: 0 });
  };

  TP.reception = (ctx, x, w = 640) => {
    G.rrect(ctx, x - w / 2, 640, w, 230, 10, { fill: '#7E5B3E', lw: 5, seed: 41, hatch: { color: 'rgba(0,0,0,0.12)', gap: 18, angle: 1.4 } });
    G.rrect(ctx, x - w / 2 - 20, 620, w + 40, 30, 8, { fill: '#A57A52', lw: 4, seed: 42 });
    G.text(ctx, 'RECEPTION', x, 760, { size: 54, fam: TP.HAND, color: '#F6E7C8', align: 'center', boil: 0 });
  };
  TP.bell = (ctx, x, y) => {
    G.ellipse(ctx, x, y, 34, 26, { fill: '#E9B73E', lw: 4, seed: 51 });
    G.rrect(ctx, x - 44, y + 18, 88, 12, 4, { fill: '#8A6A2A', lw: 3, seed: 52 });
    G.ellipse(ctx, x, y - 30, 7, 7, { fill: '#8A6A2A', lw: 2, seed: 53 });
  };
  TP.key = (ctx, x, y, s = 1, label = '', rot = 0) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    G.ellipse(ctx, -40, 0, 26, 26, { fill: '#E9B73E', lw: 4, seed: 61 });
    G.ellipse(ctx, -40, 0, 9, 9, { fill: '#FFF8E8', lw: 3, seed: 62 });
    G.rrect(ctx, -16, -7, 90, 14, 4, { fill: '#E9B73E', lw: 4, seed: 63 });
    G.rrect(ctx, 50, 5, 12, 18, 2, { fill: '#E9B73E', lw: 3, seed: 64 });
    if (label) { G.rrect(ctx, -70, 30, 90, 46, 6, { fill: '#FFFDF6', lw: 3, seed: 65 }); G.text(ctx, label, -25, 62, { size: 30, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 }); }
    ctx.restore();
  };
  TP.suitcase = (ctx, x, y, s = 1, color = '#C0504D') => {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.rrect(ctx, -60, -100, 120, 100, 12, { fill: color, lw: 4, seed: 71 });
    G.rrect(ctx, -22, -122, 44, 26, 8, { fill: 'none', lw: 5, seed: 72 });
    G.line(ctx, [[-60, -50], [60, -50]], { lw: 3, seed: 73 });
    ctx.restore();
  };
  TP.note = (ctx, x, y, s = 1, rot = 0, { text = '', locked = false, seed = 81 } = {}) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    G.rrect(ctx, -60, -42, 120, 84, 4, { fill: '#FFFBEA', lw: 3.5, seed });
    if (text) G.text(ctx, text, 0, 10, { size: 26, fam: TP.HAND, color: TP.BLUE, align: 'center', boil: 0 });
    else for (let i = 0; i < 3; i++) G.line(ctx, [[-42, -18 + i * 18], [36 - i * 14, -18 + i * 18]], { lw: 3, color: TP.BLUE, seed: seed + i });
    if (locked) TP.padlock(ctx, 0, 6, 0.8);
    ctx.restore();
  };
  TP.padlock = (ctx, x, y, s = 1, color = '#E9B73E') => {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.shape(ctx, [[-22, -10], [-22, -34], [-14, -48], [0, -52], [14, -48], [22, -34], [22, -10]], { closed: false, lw: 7, seed: 91 });
    G.rrect(ctx, -32, -12, 64, 50, 8, { fill: color, lw: 4, seed: 92 });
    G.ellipse(ctx, 0, 10, 6, 8, { fill: TP.INK, lw: 2, seed: 93 });
    ctx.restore();
  };
  TP.schoolDesk = (ctx, x) => {
    G.rrect(ctx, x - 150, 740, 300, 22, 6, { fill: '#C79A62', lw: 4, seed: 101 + x % 9 });
    for (const lx of [x - 130, x + 112]) G.rrect(ctx, lx, 760, 16, 120, 4, { fill: '#7A7F88', lw: 3, seed: 102 + lx % 7 });
  };
  // a pop-up hand-lettered sign
  TP.sign = (K, ctx, t, t0, t1, x, y, text, { w = null, h = 110, size = 54, color = TP.INK, rot = 0, seed = 5 } = {}) => {
    const ww = w || Math.max(260, text.length * size * 0.5 + 80);
    K.card(ctx, t, t0, t1, x, y, ww, h, (c) => G.text(c, text, 0, size * 0.35, { size, fam: TP.HAND, weight: 400, color, align: 'center', boil: 0 }), { rot, seed });
  };
  // an episode title card: big text with an episode tag
  TP.episodeTitle = (K, ctx, t, t0, ep, title, sub) => {
    K.title(ctx, t, t0, null, title, sub);
    const a = ease.outBack(clamp((t - t0 - 0.3) / 0.5));
    if (a > 0 && !K.VERT) { ctx.save(); ctx.translate(960 - 520, 120); ctx.rotate(-0.08); ctx.scale(a, a); G.rrect(ctx, -110, -40, 220, 80, 14, { fill: TP.PINK, lw: 4, seed: 111 }); G.text(ctx, `TSAM #${ep}`, 0, 16, { size: 44, fam: TP.HAND, color: '#FFFFFF', align: 'center', boil: 0 }); ctx.restore(); }
    if (t > t0) G.confetti(ctx, t, t0, { n: 90, seed: ep * 7, spawn: 0.8, fall: 300 });
  };
  globalThis.TP = TP;
})();
