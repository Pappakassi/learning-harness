// THE FILM: a glacier guide greets a group on Vatnajökull, explains why the ice is blue,
// and leads them off across the ice. Pure function of t; timings from score.js / vo.js.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio;
  const Subs = globalThis.Subs;
  const { ev, VO } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const X = (x) => (x * W) / 1920, Y = (y) => (y * H) / 1080;
  const GROUND = Y(860);
  const ZH = 'WenKai, "Noto Sans CJK TC", sans-serif';

  // ---------- cast ----------
  const STY = {
    guide: { skin: Ch.SKIN_TONES[1], hair: '#5A3A22', hairStyle: 'short', facialHair: 'trimmed', outfit: 'hoodie',
      shirt: '#C8402F', trim: '#8E2A1F', bottoms: 'pants', shorts: '#2E3440', headwear: 'cap', headwearColor: '#2E3440', build: 'regular' },
    asker: { skin: Ch.SKIN_TONES[0], hair: '#1E1A18', hairStyle: 'ponytail', outfit: 'hoodie', shirt: '#3B7EA1', trim: '#2B5E79',
      bottoms: 'pants', shorts: '#3A3F4A', glasses: 'round', build: 'slim' },
    friend: { skin: Ch.SKIN_TONES[1], hair: '#151515', hairStyle: 'short', outfit: 'hoodie', shirt: '#E0A33A', trim: '#B47E23',
      bottoms: 'pants', shorts: '#30343C', headwear: 'cap', headwearColor: '#E8E4DA', build: 'regular' },
    kid: { skin: Ch.SKIN_TONES[0], hair: '#2B211E', hairStyle: 'bun', outfit: 'hoodie', shirt: '#5E8C5A', trim: '#3F6A3C',
      bottoms: 'pants', shorts: '#30343C', build: 'slim' },
  };
  globalThis.CAST = STY;
  const SCALE = { guide: 0.66, asker: 0.6, friend: 0.62, kid: 0.5 };
  const HOME = { guide: X(560), asker: X(1130), friend: X(1330), kid: X(1500) };
  const VANISH = [X(150), Y(640)]; // where the hikers disappear, far up the glacier

  // where each walker is at t (front-view walk toward the far left, shrinking with distance)
  function walker(id, t) {
    const w = S.walkers.find((v) => v.id === id);
    const t0 = ev.walk + w.delay;
    const s0 = SCALE[id];
    if (t < t0) return { x: HOME[id], y: GROUND, s: s0, walking: false };
    const k = 1 - Math.exp(-(t - t0) / 5.5); // eases toward the vanishing point
    const x = lerp(HOME[id], VANISH[0], k), y = lerp(GROUND, VANISH[1], k * 0.9);
    const s = lerp(s0, 0.16, k);
    return { x, y, s, walking: true, walk: ((t - t0) / (2 * S.STEP)) % 1 };
  }

  // ---------- scenery ----------
  function sky(ctx) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#A9C9DE'); g.addColorStop(0.55, '#E9F1F4'); g.addColorStop(1, '#F6F3EC');
    ctx.fillStyle = g; ctx.fillRect(-X(200), -Y(200), W + X(400), H + Y(400));
  }
  function mountains(ctx) {
    G.poly(ctx, [[X(-100), Y(470)], [X(160), Y(300)], [X(330), Y(380)], [X(560), Y(250)], [X(760), Y(360)], [X(980), Y(280)],
      [X(1220), Y(390)], [X(1420), Y(230)], [X(1660), Y(350)], [X(2020), Y(300)], [X(2020), Y(560)], [X(-100), Y(560)]],
    { fill: '#5D6B78', lw: 4, seed: 11, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    for (const [x, y, w] of [[160, 300, 90], [560, 250, 110], [980, 280, 95], [1420, 230, 120]]) {
      G.poly(ctx, [[X(x - w), Y(y + w * 0.75)], [X(x), Y(y)], [X(x + w), Y(y + w * 0.75)], [X(x + w * 0.4), Y(y + w * 0.55)],
        [X(x), Y(y + w * 0.8)], [X(x - w * 0.45), Y(y + w * 0.6)]], { fill: '#F4F7F8', lw: 3, seed: 20 + x });
    }
  }
  function glacier(ctx, t) {
    // the ice cap: a broad white sheet with blue shadows
    G.poly(ctx, [[X(-100), Y(560)], [X(400), Y(520)], [X(900), Y(545)], [X(1400), Y(510)], [X(2020), Y(540)], [X(2020), H + 80], [X(-100), H + 80]],
      { fill: '#F1F6F8', lw: 4, seed: 31, hatch: { color: 'rgba(80,140,180,0.16)', gap: 12, angle: 0.15 } });
    // flow lines and small crevasses
    for (let i = 0; i < 9; i++) {
      const y = Y(600 + i * 34), x0 = X(-50 + U.hash(i, 3) * 300), x1 = x0 + X(500 + U.hash(i, 4) * 700);
      G.line(ctx, [[x0, y], [x1 * 0.5 + x0 * 0.5, y + Y(8)], [x1, y - Y(4)]], { color: 'rgba(90,150,190,0.35)', lw: 2.5, seed: 40 + i });
    }
    // the big blue crevasse (between guide and tourists)
    const cx = X(850), cy = Y(700);
    const glowT = clamp((t - ev.answer) / 1.5) * (1 - clamp((t - ev.go - 2) / 2));
    if (glowT > 0) {
      const gl = ctx.createRadialGradient(cx, cy, 0, cx, cy, X(260));
      gl.addColorStop(0, `rgba(80,170,230,${0.45 * glowT})`); gl.addColorStop(1, 'rgba(80,170,230,0)');
      ctx.fillStyle = gl; ctx.fillRect(cx - X(260), cy - Y(260), X(520), Y(520));
    }
    G.poly(ctx, [[cx - X(150), cy], [cx - X(60), cy - Y(22)], [cx + X(70), cy - Y(16)], [cx + X(160), cy + Y(4)],
      [cx + X(60), cy + Y(26)], [cx - X(70), cy + Y(22)]], { fill: '#2F7FB5', lw: 4, seed: 51, hatch: { color: 'rgba(10,50,90,0.35)', gap: 7 } });
    G.poly(ctx, [[cx - X(95), cy + Y(2)], [cx, cy - Y(10)], [cx + X(95), cy + Y(4)], [cx + X(10), cy + Y(14)]],
      { fill: '#14507E', lw: 0, seed: 52 });
  }
  function snow(ctx, t) {
    ctx.save();
    for (let i = 0; i < 70; i++) {
      const x = ((U.hash(i, 1) * W + t * (12 + U.hash(i, 2) * 20)) % (W + 40)) - 20;
      const y = ((U.hash(i, 3) * H + t * (30 + U.hash(i, 4) * 40)) % (H + 40)) - 20;
      ctx.globalAlpha = 0.5 + 0.4 * U.hash(i, 5);
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath(); ctx.arc(x, y, 2 + 2.5 * U.hash(i, 6), 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- the light-ray gag (why the ice is blue) ----------
  function rays(ctx, t) {
    if (t < ev.answer + 1.0 || t > ev.go + 1.0) return;
    const fade = 1 - clamp((t - ev.go) / 1.0);
    const sun = [X(260), Y(150)], ice = [X(850), Y(700)];
    const sunA = clamp((t - ev.answer - 1.0) / 0.6) * fade;
    ctx.save(); ctx.globalAlpha = sunA;
    G.rays(ctx, sun[0], sun[1], { n: 12, r0: X(46), r1: X(78), color: '#E3B23C', lw: 6, spin: t * 0.3 });
    G.ellipse(ctx, sun[0], sun[1], X(40), X(40), { fill: '#F2C94C', lw: 4, seed: 61 });
    ctx.restore();
    const draw = (color, off, u, lw = 7) => {
      if (u <= 0) return;
      const a = [sun[0] + off, sun[1] + X(40)], b = [ice[0] + off * 0.6, ice[1] - Y(10)];
      G.line(ctx, [a, [lerp(a[0], b[0], u), lerp(a[1], b[1], u)]], { color, lw, seed: 70 + off });
    };
    const inU = clamp((t - ev.answer - 1.6) / 1.4);
    ctx.save(); ctx.globalAlpha = fade;
    // red: travels in, then dies at the ice on "紅色的光被吸收了"
    const redA = 1 - clamp((t - ev.red - 0.6) / 0.7);
    if (redA > 0) { ctx.save(); ctx.globalAlpha = fade * redA; draw('#C8402F', -X(26), inU); ctx.restore(); }
    if (t > ev.red + 0.6 && t < ev.red + 1.6) {
      const p = clamp((t - ev.red - 0.6) / 1.0);
      ctx.save(); ctx.globalAlpha = (1 - p) * fade;
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * Math.PI * 2, r = X(14 + 40 * p);
        G.ellipse(ctx, ice[0] - X(16) + Math.cos(a) * r, ice[1] - Y(14) + Math.sin(a) * r, X(6), X(6), { fill: '#C8402F', lw: 0, seed: 80 + i });
      }
      ctx.restore();
    }
    draw('#5F9E5A', 0, inU, 5);
    draw('#2F7FB5', X(26), inU);
    // blue: bounces back up to the asker's eyes on "藍色的光回到我們的眼睛裡"
    const bU = clamp((t - ev.blue) / (ev.blueEye - ev.blue));
    if (bU > 0) {
      const a = [ice[0] + X(16), ice[1] - Y(10)];
      const eye = [HOME.asker - X(8), GROUND - SCALE.asker * 395];
      const p = ease.inOutQuad(bU);
      G.line(ctx, [a, [lerp(a[0], eye[0], p), lerp(a[1], eye[1], p)]], { color: '#2F7FB5', lw: 7, seed: 90 });
      if (t >= ev.blueEye && t < ev.blueEye + 0.6) {
        const q = (t - ev.blueEye) / 0.6;
        ctx.save(); ctx.globalAlpha = 1 - q;
        G.star(ctx, eye[0], eye[1], X(16 + 30 * q), { fill: '#7FC4F0', rot: q });
        ctx.restore();
      }
    }
    ctx.restore();
  }

  // ---------- acting ----------
  const mouth = (who, t) => Subs.mouth(VO, t, who);
  function person(ctx, id, t) {
    const p = walker(id, t);
    const o = { x: p.x, y: p.y, s: p.s, pose: 'stand', style: STY[id], blink: (t + U.hash(id.length) * 3) % 3.7 < 0.12 ? 1 : 0 };
    if (p.walking) { o.pose = 'walk'; o.walk = p.walk; }
    const talking = (id === 'guide' || id === 'asker') ? mouth(id === 'guide' ? 'guide' : 'tourist', t) : null;
    if (talking && talking.talking) o.mouth = talking;
    const inLine = (i) => t >= VO.lines[i].t && t <= VO.lines[i].end + 0.3;
    if (id === 'guide') {
      o.look = p.walking ? -0.8 : 0.6;
      if (t >= ev.hello + 0.2 && t < ev.hello + 2.8) { o.gesture = 'wave'; o.eyes = 'happy'; }
      else if (inLine(1)) { o.look = 0.9; o.mouth = o.mouth || 'smile'; }
      else if (inLine(2) && !p.walking) {
        o.handR = [230, -330]; o.look = 0.4; o.lookY = 0.4; // points down at the blue crevasse
        if (t > ev.blueEye) { o.eyes = 'happy'; o.handR = undefined; o.gesture = 'thumbsUp'; }
      } else if (inLine(3) && !p.walking) { o.gesture = 'pointUp'; o.look = -0.6; }
      if (!o.mouth) o.mouth = 'smile';
    } else {
      const lookAtGuide = clamp((HOME.guide - p.x) / X(600), -1, 1);
      o.look = p.walking ? -0.8 : lookAtGuide;
      o.mouth = o.mouth || 'smile';
      if (id === 'asker') {
        if (inLine(1)) { o.eyes = 'wide'; o.brows = 'up'; o.handL = [-230, -320]; }
        if (t >= ev.blueEye && t < ev.go) { o.eyes = 'wide'; o.mouth = o.mouth.talking ? o.mouth : 'o'; o.brows = 'up'; }
      } else if (inLine(1) || inLine(2)) {
        o.look = -0.7; o.lookY = 0.5; // everyone peers at the crevasse
      }
      if (t >= ev.blueEye && t < ev.blueEye + 2.5 && id !== 'asker') { o.eyes = 'happy'; o.mouth = 'grin'; }
    }
    Ch.person(ctx, o);
  }

  // ---------- captions: Chinese with pinyin over the harder words ----------
  function caption(ctx, t) {
    const line = VO.lines.find((l) => t >= l.t - 0.1 && t <= l.end + 0.35);
    if (!line) return;
    const a = clamp((t - line.t + 0.1) / 0.2) * (1 - clamp((t - line.end - 0.15) / 0.2));
    const size = Y(46), pys = Y(19);
    const toks = line.tokens;
    const widths = toks.map(([s]) => G.measure(ctx, s, size, ZH, 500));
    const total = widths.reduce((x, y) => x + y, 0);
    const scale = Math.min(1, (W - X(240)) / total);
    const w = total * scale, x0 = W / 2 - w / 2, y = H - Y(76) - (line.en ? Y(26) : 0);
    ctx.save(); ctx.globalAlpha = a;
    const boxH = Y(118) + (line.en ? Y(34) : 0);
    G.tornPaper(ctx, x0 - X(40), y - Y(84), w + X(80), boxH, { fill: 'rgba(255,253,248,0.92)', seed: 7, shadow: true });
    const who = line.who === 'guide' ? '嚮導' : '遊客';
    G.text(ctx, who, x0 - X(28), y - Y(64), { size: Y(18), fam: ZH, color: line.who === 'guide' ? '#C8402F' : '#3B7EA1', boil: 0 });
    let x = x0;
    toks.forEach(([s, py], i) => {
      const cw = widths[i] * scale;
      G.text(ctx, s, x, y, { size: size * scale, fam: ZH, weight: 500, color: '#1F1B17', boil: 0 });
      if (py) G.text(ctx, py, x + cw / 2, y - size * scale - Y(2), { size: pys * scale, fam: 'Inter, sans-serif', color: '#2F7FB5', align: 'center', boil: 0 });
      x += cw;
    });
    if (line.en) G.text(ctx, line.en, W / 2, y + Y(36), { size: Y(22), fam: 'Inter, sans-serif', color: '#6B6258', align: 'center', boil: 0 });
    ctx.restore();
  }

  function title(ctx, t) {
    const a = clamp((t - ev.title) / 0.8);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    G.tornPaper(ctx, W / 2 - X(360), Y(70), X(720), Y(250), { fill: 'rgba(255,253,248,0.94)', seed: 12, shadow: true });
    G.text(ctx, '冰島的冰川', W / 2, Y(200), { size: Y(110), fam: ZH, weight: 500, color: '#1F1B17', align: 'center' });
    G.text(ctx, '跟著嚮導，走上冰川', W / 2, Y(272), { size: Y(40), fam: ZH, color: '#5D6B78', align: 'center' });
    ctx.restore();
  }

  // gentle camera: push in toward the speaker / the crevasse
  function camera(t) {
    const k = [
      [0, 1.0, 960, 560], [ev.ask - 0.4, 1.05, 900, 600], [ev.ask + 0.6, 1.14, 1040, 640],
      [ev.answer + 0.4, 1.14, 1040, 640], [ev.answer + 1.4, 1.08, 820, 560], [ev.go, 1.08, 820, 560],
      [ev.walk + 0.5, 1.0, 960, 540], [S.DURATION, 1.0, 960, 540],
    ];
    let i = 0; while (i < k.length - 2 && t > k[i + 1][0]) i++;
    const u = ease.inOutCubic(clamp((t - k[i][0]) / Math.max(0.001, k[i + 1][0] - k[i][0])));
    return { z: lerp(k[i][1], k[i + 1][1], u), cx: X(lerp(k[i][2], k[i + 1][2], u)), cy: Y(lerp(k[i][3], k[i + 1][3], u)) };
  }

  Studio.film({
    async init() { await Studio.loadFont('WenKai', 'assets/LXGWWenKaiTC-Medium.ttf', 500); },
    draw(ctx, t) {
      const c = camera(t);
      ctx.save();
      ctx.translate(W / 2, H / 2); ctx.scale(c.z, c.z); ctx.translate(-c.cx, -c.cy);
      sky(ctx); mountains(ctx); glacier(ctx, t);
      rays(ctx, t);
      // draw back-to-front: whoever is further up the glacier first
      const ids = ['kid', 'friend', 'asker', 'guide'].sort((a, b) => walker(a, t).y - walker(b, t).y);
      for (const id of ids) person(ctx, id, t);
      snow(ctx, t);
      ctx.restore();
      caption(ctx, t);
      title(ctx, t);
    },
    post: { paper: 0.45, vignette: 0.25, grain: 0.04 },
    fadeOut: 1.2,
  });
})();
