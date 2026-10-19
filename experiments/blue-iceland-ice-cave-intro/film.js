// THE FILM: a Blue Iceland guide tells Chinese-speaking guests what the ice cave tour is like:
// the Unimog super jeep (30 min), helmet + crampons at the parking lot, the 30-minute moraine walk,
// busy caves (stay with the group) and the helmet rule. Pure function of t; timings from score.js / vo.js.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio;
  const Subs = globalThis.Subs, Shots = globalThis.Shots;
  const { ev, VO } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const X = (x) => (x * W) / 1920, Y = (y) => (y * H) / 1080;
  const ZH = 'WenKai, "Noto Sans CJK SC", sans-serif';
  const LAT = 'Inter, sans-serif';
  const HEAD = -404; // head centre in a standing person's own units
  const RED = '#D9412F', INK = '#1F1B17', ICE = '#2F7FB5';
  const between = (t, a, b) => t >= a && t < b;
  const pop = (t, t0, d = 0.35) => ease.outBack(clamp((t - t0) / d));

  // ---------- cast ----------
  const STY = {
    guide: { skin: Ch.SKIN_TONES[1], hair: '#5A3A22', hairStyle: 'short', facialHair: 'trimmed', outfit: 'hoodie',
      shirt: '#C8402F', trim: '#8E2A1F', bottoms: 'pants', shorts: '#2E3440', headwear: 'cap', headwearColor: '#2E3440', shoes: '#4A3426' },
    asker: { skin: Ch.SKIN_TONES[0], hair: '#1E1A18', hairStyle: 'ponytail', outfit: 'hoodie', shirt: '#3B7EA1', trim: '#2B5E79',
      bottoms: 'pants', shorts: '#3A3F4A', glasses: 'round', build: 'slim', shoes: '#5A4232' },
    friend: { skin: Ch.SKIN_TONES[1], hair: '#151515', hairStyle: 'short', outfit: 'hoodie', shirt: '#E0A33A', trim: '#B47E23',
      bottoms: 'pants', shorts: '#30343C', shoes: '#4A3426' },
    kid: { skin: Ch.SKIN_TONES[0], hair: '#2B211E', hairStyle: 'bun', outfit: 'hoodie', shirt: '#5E8C5A', trim: '#3F6A3C',
      bottoms: 'pants', shorts: '#30343C', build: 'slim', shoes: '#5A4232' },
    elder: { skin: Ch.SKIN_TONES[1], hair: '#C9C6C0', hairStyle: 'short', outfit: 'hoodie', shirt: '#7A5A9E', trim: '#5A3F78',
      bottoms: 'pants', shorts: '#3A3F4A', glasses: 'round', shoes: '#4A3426' },
  };
  globalThis.CAST = STY;
  const GROUP = ['asker', 'friend', 'kid', 'elder'];
  const SIZE = { guide: 1, asker: 0.92, friend: 0.96, kid: 0.76, elder: 0.94 };

  // a person; o.helmet puts the helmet on, o.crampon hangs crampons from the right hand
  function actor(ctx, id, x, y, s, t, o = {}) {
    const st = Object.assign({}, STY[id]);
    if (o.helmet) { st.headwear = 'helmet'; st.headwearColor = o.helmetColor || RED; }
    else if (o.bare) st.headwear = 'none';
    const p = {
      x, y, s: s * SIZE[id], pose: o.walk != null ? 'walk' : 'stand', walk: o.walk || 0, style: st,
      blink: (t + U.hash(id.length, 2) * 3) % 3.6 < 0.12 ? 1 : 0, look: o.look ?? 0, lookY: o.lookY ?? 0,
      eyes: o.eyes, brows: o.brows, gesture: o.gesture, handL: o.handL, handR: o.handR, mouth: o.mouth || 'smile',
      headRot: o.headRot || 0, rot: o.rot || 0, seed: 300 + id.length * 17,
    };
    const role = id === 'guide' ? 'guide' : id === 'asker' ? 'tourist' : null;
    if (role) { const mm = Subs.mouth(VO, t, role); if (mm.talking) p.mouth = mm; }
    Ch.person(ctx, p);
    if (o.crampon) {
      const k = p.s, hand = o.handR || [92, -180];
      const bob = p.pose === 'walk' ? -Math.abs(Math.sin(2 * Math.PI * p.walk)) * 12 * k : 0;
      crampon(ctx, x + hand[0] * k, y + hand[1] * k + bob, k * 1.1, Math.sin(t * 3 + id.length) * 0.12);
    }
    return p;
  }
  const headAt = (x, y, s, id) => [x, y + HEAD * s * SIZE[id]];

  // ---------- props ----------
  function crampon(ctx, x, y, s, rot = 0) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    G.line(ctx, [[-8, -8], [-20, 20], [-16, 40]], { lw: 6, color: '#C23A2A', seed: 401 });
    G.line(ctx, [[8, -8], [20, 20], [16, 40]], { lw: 6, color: '#C23A2A', seed: 402 });
    const metal = { fill: '#B9C1C9', lw: 3.5, hatch: { color: 'rgba(40,50,60,0.2)', gap: 5 } };
    G.rrect(ctx, -30, 36, 60, 56, 14, { ...metal, seed: 403 });
    G.rrect(ctx, -26, 112, 52, 42, 12, { ...metal, seed: 404 });
    G.line(ctx, [[0, 90], [0, 114]], { lw: 6, color: '#8D97A1', seed: 405 });
    for (const sd of [-1, 1]) for (const yy of [46, 70, 122, 144]) {
      G.poly(ctx, [[sd * 28, yy - 7], [sd * 46, yy], [sd * 28, yy + 7]], { fill: '#DDE3E8', lw: 2.5, seed: 406 + yy + sd, step: 30 });
    }
    G.poly(ctx, [[-14, 30], [0, 12], [14, 30]], { fill: '#DDE3E8', lw: 2.5, seed: 420, step: 30 });
    ctx.restore();
  }
  function helmetIcon(ctx, x, y, s, color = RED) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    Ch.headwear(ctx, { headwear: 'helmet', headwearColor: color }, 7);
    ctx.restore();
  }
  function boot(ctx, x, y, s) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.poly(ctx, [[-40, -80], [20, -80], [24, -30], [70, -10], [76, 18], [-46, 18]], { fill: '#8A5A34', lw: 4, seed: 431, hatch: { color: 'rgba(0,0,0,0.15)', gap: 6 } });
    G.rrect(ctx, -50, 10, 130, 18, 8, { fill: '#2B2622', lw: 3.5, seed: 432 });
    for (let k = 0; k < 4; k++) G.line(ctx, [[-10, -68 + k * 14], [16, -64 + k * 14]], { lw: 3, color: '#F2C94C', seed: 433 + k });
    ctx.restore();
  }
  function jacket(ctx, x, y, s) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    G.poly(ctx, [[-30, -70], [30, -70], [76, -40], [64, 4], [44, -10], [44, 60], [-44, 60], [-44, -10], [-64, 4], [-76, -40]],
      { fill: '#2F7FB5', lw: 4, seed: 441, hatch: { color: 'rgba(0,0,0,0.15)', gap: 6 } });
    G.line(ctx, [[0, -66], [0, 58]], { lw: 3, color: '#F2F4F2', seed: 442 });
    for (let k = 0; k < 3; k++) G.line(ctx, [[-42, -20 + k * 24], [42, -20 + k * 24]], { lw: 2, color: 'rgba(255,255,255,0.4)', seed: 443 + k });
    ctx.restore();
  }
  function tick(ctx, x, y, s, u) {
    if (u <= 0) return;
    const a = [x - 22 * s, y], b = [x - 4 * s, y + 20 * s], c = [x + 30 * s, y - 26 * s];
    const pts = u < 0.4 ? [a, [lerp(a[0], b[0], u / 0.4), lerp(a[1], b[1], u / 0.4)]] : [a, b, [lerp(b[0], c[0], (u - 0.4) / 0.6), lerp(b[1], c[1], (u - 0.4) / 0.6)]];
    G.line(ctx, pts, { lw: 9 * s, color: '#3E9A4A', seed: 450 });
  }

  // the Unimog super jeep, side view facing right; wheels at y=0
  function unimog(ctx, x, y, s, { facing = 1, roll = 0, bounce = 0, tilt = 0, faces = 0, t = 0 } = {}) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s * facing, s);
    ctx.fillStyle = 'rgba(20,10,20,0.22)'; ctx.beginPath(); ctx.ellipse(0, 6, 470, 22, 0, 0, Math.PI * 2); ctx.fill();
    const wheel = (wx) => {
      G.ellipse(ctx, wx, -110, 110, 110, { fill: '#25282D', lw: 5, seed: 460 + wx });
      for (let k = 0; k < 16; k++) {
        const a = roll + (k / 16) * Math.PI * 2;
        G.rrect(ctx, wx + Math.cos(a) * 100 - 9, -110 + Math.sin(a) * 100 - 9, 18, 18, 4, { fill: '#33373D', lw: 2, seed: 470 + k });
      }
      G.ellipse(ctx, wx, -110, 56, 56, { fill: '#C9A33A', lw: 4, seed: 490 + wx });
      for (let k = 0; k < 6; k++) {
        const a = roll + (k / 6) * Math.PI * 2;
        G.ellipse(ctx, wx + Math.cos(a) * 34, -110 + Math.sin(a) * 34, 7, 7, { fill: '#5E4A1A', lw: 0, seed: 495 + k });
      }
      G.ellipse(ctx, wx, -110, 16, 16, { fill: '#7A6420', lw: 3, seed: 499 });
    };
    ctx.save(); ctx.translate(0, -bounce); ctx.rotate(tilt);
    // chassis and fenders
    G.rrect(ctx, -440, -210, 880, 46, 10, { fill: '#2A2D33', lw: 4, seed: 501 });
    // passenger box
    G.rrect(ctx, -450, -520, 600, 320, 30, { fill: '#2F4A63', lw: 5, seed: 502, hatch: { color: 'rgba(255,255,255,0.06)', gap: 9 } });
    G.rrect(ctx, -450, -330, 600, 30, 8, { fill: '#E9B73E', lw: 3.5, seed: 503 });
    G.rrect(ctx, -460, -548, 620, 30, 10, { fill: '#3A3E45', lw: 3.5, seed: 504 }); // roof rack
    for (let k = 0; k < 6; k++) G.line(ctx, [[-440 + k * 118, -548], [-440 + k * 118, -575]], { lw: 4, color: '#3A3E45', seed: 505 + k });
    G.line(ctx, [[-450, -575], [150, -575]], { lw: 5, color: '#3A3E45', seed: 512 });
    // windows with passengers
    for (let k = 0; k < 4; k++) {
      const wx = -420 + k * 140;
      G.rrect(ctx, wx, -490, 112, 120, 18, { fill: '#BFE1F2', lw: 4, seed: 520 + k });
      if (k < faces) {
        ctx.save(); ctx.beginPath(); ctx.rect(wx, -490, 112, 120); ctx.clip();
        const bob = Math.sin(t * 9 + k * 1.7) * 6 * Math.min(1, bounce / 8 + 0.3);
        const hairs = ['#1E1A18', '#151515', '#2B211E', '#C9C6C0'];
        const skin = [Ch.SKIN_TONES[0], Ch.SKIN_TONES[1], Ch.SKIN_TONES[0], Ch.SKIN_TONES[1]];
        G.ellipse(ctx, wx + 56, -400 + bob, 34, 38, { fill: skin[k], lw: 3.5, seed: 530 + k });
        G.ellipse(ctx, wx + 56, -432 + bob, 34, 16, { fill: hairs[k], lw: 3, seed: 535 + k });
        G.ellipse(ctx, wx + 68, -402 + bob, 4, 5, { fill: INK, lw: 0, seed: 540 + k });
        G.ellipse(ctx, wx + 46, -402 + bob, 4, 5, { fill: INK, lw: 0, seed: 545 + k });
        G.line(ctx, [[wx + 48, -384 + bob], [wx + 58, -380 + bob], [wx + 68, -384 + bob]], { lw: 3, seed: 550 + k });
        ctx.restore();
      }
      ctx.save(); ctx.globalAlpha *= 0.5; G.line(ctx, [[wx + 14, -470], [wx + 40, -470]], { lw: 5, color: '#FFFFFF', seed: 555 + k }); ctx.restore();
    }
    // door with steps
    G.line(ctx, [[-430 + 4 * 140, -500], [-430 + 4 * 140, -215]], { lw: 3, color: '#1D2F40', seed: 560 });
    G.rrect(ctx, 120, -200, 60, 14, 4, { fill: '#55595F', lw: 3, seed: 561 });
    // cab
    G.poly(ctx, [[160, -470], [330, -470], [400, -330], [460, -300], [470, -210], [160, -210]], { fill: '#2F4A63', lw: 5, seed: 562, step: 30 });
    G.poly(ctx, [[190, -446], [318, -446], [372, -336], [190, -336]], { fill: '#BFE1F2', lw: 4, seed: 563, step: 30 });
    G.ellipse(ctx, 260, -384, 30, 34, { fill: Ch.SKIN_TONES[1], lw: 3.5, seed: 564 });
    G.ellipse(ctx, 260, -414, 32, 14, { fill: '#2E3440', lw: 3, seed: 565 });
    G.rrect(ctx, 440, -290, 26, 30, 8, { fill: '#F6E27A', lw: 3, seed: 566 }); // headlight
    G.rrect(ctx, 430, -230, 50, 34, 8, { fill: '#2A2D33', lw: 3.5, seed: 567 }); // bumper
    G.rrect(ctx, 140, -520, 20, 120, 6, { fill: '#2A2D33', lw: 3, seed: 568 }); // snorkel
    G.rrect(ctx, 130, -530, 40, 18, 6, { fill: '#2A2D33', lw: 3, seed: 569 });
    for (const fx of [-250, 270]) G.poly(ctx, [[fx - 140, -200], [fx - 120, -250], [fx + 120, -250], [fx + 140, -200]], { fill: '#23262B', lw: 4, seed: 570 + fx, step: 30 });
    ctx.restore();
    wheel(-250); wheel(270);
    ctx.restore();
  }

  // ---------- scenery ----------
  function sky(ctx, top = '#9CC3DD', mid = '#E7F0F4', bot = '#F5F2EA') {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, top); g.addColorStop(0.55, mid); g.addColorStop(1, bot);
    ctx.fillStyle = g; ctx.fillRect(-W, -H, W * 3, H * 3);
  }
  // a tiling ridge: off scrolls it left (parallax)
  function ridge(ctx, off, base, amp, seg, fill, seed, { snow = false, hatch = null } = {}) {
    const k0 = Math.floor(off / seg), dx = off - k0 * seg;
    const pts = [[-seg * 2, Y(1200)]];
    const peaks = [];
    for (let i = -2; i <= Math.ceil(W / seg) + 2; i++) {
      const h = amp * (0.35 + 0.65 * U.hash(i + k0, seed));
      const x = i * seg - dx, yv = base - h;
      pts.push([x, yv]); peaks.push([x, yv, h]);
      pts.push([x + seg * 0.5, base - amp * 0.2 * U.hash(i + k0, seed + 1)]);
    }
    pts.push([W + seg * 3, Y(1200)]);
    G.poly(ctx, pts, { fill, lw: 4, seed, step: 40, hatch });
    if (snow) for (const [x, yv, h] of peaks) {
      if (h < amp * 0.6) continue;
      const w = seg * 0.18;
      G.poly(ctx, [[x - w, yv + w * 0.9], [x, yv], [x + w, yv + w * 0.9], [x + w * 0.3, yv + w * 0.6], [x - w * 0.3, yv + w * 0.75]], { fill: '#F4F7F8', lw: 3, seed: seed + Math.round(x), step: 30 });
    }
  }
  function iceCap(ctx, x0, y0, w) {
    G.poly(ctx, [[x0, y0 + Y(60)], [x0 + w * 0.15, y0], [x0 + w * 0.5, y0 - Y(20)], [x0 + w * 0.85, y0 - Y(6)], [x0 + w, y0 + Y(40)], [x0 + w, Y(1200)], [x0, Y(1200)]],
      { fill: '#F1F6F8', lw: 4, seed: 611, step: 40, hatch: { color: 'rgba(80,140,180,0.18)', gap: 12, angle: 0.15 } });
  }
  function gravel(ctx, y0, off = 0, { fill = '#77706A', dots = 90, seed = 620 } = {}) {
    G.poly(ctx, [[-X(100), y0], [W + X(100), y0 - Y(10)], [W + X(100), H + Y(100)], [-X(100), H + Y(100)]], { fill, lw: 4, seed, step: 60 });
    for (let i = 0; i < dots; i++) {
      const xx = (((U.hash(i, seed) * (W + 200) - off * (0.6 + 0.4 * U.hash(i, 3))) % (W + 200)) + W + 200) % (W + 200) - 100;
      const yy = y0 + Y(10) + U.hash(i, seed + 1) * (H - y0);
      const r = X(3 + 10 * U.hash(i, seed + 2)) * (0.6 + (yy - y0) / (H - y0 + 1));
      G.ellipse(ctx, xx, yy, r * 1.4, r, { fill: U.hash(i, 9) > 0.5 ? '#5C5650' : '#8E877F', lw: r > X(6) ? 2.5 : 0, seed: seed + i });
    }
  }
  function lagoon(ctx, t) {
    G.poly(ctx, [[-X(100), Y(600)], [W + X(100), Y(590)], [W + X(100), Y(760)], [-X(100), Y(770)]], { fill: '#4E8FB5', lw: 4, seed: 631, step: 60, hatch: { color: 'rgba(255,255,255,0.12)', gap: 14, angle: 0.05 } });
    const bergs = [[160, 640, 120], [520, 690, 80], [900, 620, 150], [1320, 700, 90], [1700, 650, 130]];
    for (const [bx, by, bw] of bergs) {
      const bob = Math.sin(t * 0.8 + bx) * 3;
      G.poly(ctx, [[X(bx - bw), Y(by + bob)], [X(bx - bw * 0.6), Y(by - bw * 0.5 + bob)], [X(bx - bw * 0.1), Y(by - bw * 0.7 + bob)], [X(bx + bw * 0.5), Y(by - bw * 0.4 + bob)], [X(bx + bw), Y(by + bob)]],
        { fill: '#EEF7FB', lw: 3.5, seed: 640 + bx, step: 26, hatch: { color: 'rgba(60,150,210,0.35)', gap: 7, angle: -0.5 } });
    }
  }
  function backdrop(ctx, t, { lagoonOn = true } = {}) {
    sky(ctx);
    ridge(ctx, 0, Y(470), Y(220), X(300), '#5D6B78', 11, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, X(400), Y(470), X(900));
    if (lagoonOn) lagoon(ctx, t);
  }
  function snow(ctx, t, n = 50) {
    ctx.save();
    for (let i = 0; i < n; i++) {
      const x = ((U.hash(i, 1) * W + t * (12 + U.hash(i, 2) * 20)) % (W + 40)) - 20;
      const y = ((U.hash(i, 3) * H + t * (30 + U.hash(i, 4) * 40)) % (H + 40)) - 20;
      ctx.globalAlpha = 0.45 + 0.4 * U.hash(i, 5);
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath(); ctx.arc(x, y, 2 + 2.5 * U.hash(i, 6), 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- signs ----------
  // a pop-up card centred at (x, y); inner(ctx) draws in the card's own coordinates (centre 0,0)
  function card(ctx, t, t0, t1, x, y, w, h, inner, { rot = 0, seed = 1, fill = 'rgba(255,253,248,0.96)' } = {}) {
    const a = clamp((t - t0) / 0.4), out = t1 == null ? 1 : clamp((t1 - t) / 0.3);
    if (a <= 0 || out <= 0) return;
    const k = ease.outBack(a) * (0.7 + 0.3 * out);
    ctx.save(); ctx.globalAlpha *= out; ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k, k);
    G.tornPaper(ctx, -w / 2, -h / 2, w, h, { fill, seed, shadow: true });
    inner(ctx);
    ctx.restore();
  }
  const zh = (ctx, s, x, y, size, color = INK, align = 'center') => G.text(ctx, s, x, y, { size, fam: ZH, weight: 500, color, align, boil: 0 });
  function clockFace(ctx, x, y, r, u) {
    G.ellipse(ctx, x, y, r, r, { fill: '#FFFFFF', lw: 5, seed: 701 });
    if (u > 0) {
      ctx.save(); ctx.fillStyle = 'rgba(47,127,181,0.35)'; ctx.beginPath(); ctx.moveTo(x, y);
      ctx.arc(x, y, r - 6, -Math.PI / 2, -Math.PI / 2 + Math.PI * u); ctx.closePath(); ctx.fill(); ctx.restore();
    }
    for (let k = 0; k < 12; k++) { const a = (k / 12) * Math.PI * 2; G.line(ctx, [[x + Math.cos(a) * r * 0.8, y + Math.sin(a) * r * 0.8], [x + Math.cos(a) * r * 0.92, y + Math.sin(a) * r * 0.92]], { lw: 3, seed: 702 + k }); }
    const a = -Math.PI / 2 + Math.PI * u;
    G.line(ctx, [[x, y], [x + Math.cos(a) * r * 0.78, y + Math.sin(a) * r * 0.78]], { lw: 6, color: RED, seed: 720 });
    G.ellipse(ctx, x, y, 7, 7, { fill: INK, lw: 0, seed: 721 });
  }
  function clockCard(ctx, t, t0, t1, x, y) {
    card(ctx, t, t0, t1, x, y, X(380), Y(170), (c) => {
      clockFace(c, -X(110), 0, Y(58), ease.inOutQuad(clamp((t - t0 - 0.3) / 2.2)));
      zh(c, '约', X(20), Y(-18), Y(34), '#5D6B78', 'left');
      zh(c, '30 分钟', X(20), Y(42), Y(58), INK, 'left');
    }, { rot: -0.03, seed: 31 });
  }
  function meterCard(ctx, t, t0, t1, x, y) {
    card(ctx, t, t0, t1, x, y, X(420), Y(170), (c) => {
      zh(c, '难度：中等', 0, -Y(22), Y(48));
      for (let k = 0; k < 5; k++) {
        const on = k < 3 && t > t0 + 0.5 + k * 0.25;
        G.rrect(c, -X(150) + k * X(62), Y(10), X(50), Y(38), 10, { fill: on ? ['#5FA85A', '#E9B73E', '#E58A3A'][k] : '#E3DED5', lw: 3, seed: 740 + k });
      }
    }, { rot: 0.02, seed: 37 });
  }
  function noSign(ctx, x, y, r, t0, t) {
    const a = clamp((t - t0) / 0.3);
    if (a <= 0) return;
    const k = ease.outBack(a);
    const sh = Math.sin((t - t0) * 40) * Math.exp(-(t - t0) * 5) * X(14);
    ctx.save(); ctx.translate(x + sh, y); ctx.scale(k, k);
    G.ellipse(ctx, 0, 0, r + 10, r + 10, { fill: '#FFFFFF', lw: 4, seed: 751 });
    helmetIcon(ctx, 0, r * 0.35 - Math.abs(Math.sin(t * 4)) * 8, r / 105);
    G.line(ctx, [[0, -r * 0.55], [0, -r * 0.9]], { lw: 8, color: INK, seed: 752 });
    G.line(ctx, [[-16, -r * 0.75], [0, -r * 0.92], [16, -r * 0.75]], { lw: 8, color: INK, seed: 753 });
    ctx.save(); ctx.lineWidth = r * 0.16; ctx.strokeStyle = '#D02A1E';
    ctx.beginPath(); ctx.arc(0, 0, r * 0.92, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-r * 0.65, -r * 0.65); ctx.lineTo(r * 0.65, r * 0.65); ctx.stroke(); ctx.restore();
    ctx.restore();
  }

  // ---------- captions: the sentence being spoken ----------
  function caption(ctx, t) {
    const line = VO.lines.find((l) => t >= l.t - 0.1 && t <= l.end + 0.35);
    if (!line) return;
    let si = 0;
    line.sents.forEach((s, i) => { if (t >= s[1] - 0.1) si = i; });
    const [text, s0, s1] = line.sents[si];
    const last = si === line.sents.length - 1;
    const a = clamp((t - s0 + 0.12) / 0.15) * (last ? 1 - clamp((t - line.end - 0.15) / 0.2) : 1);
    const size = Y(52);
    const tw = G.measure(ctx, text, size, ZH, 500);
    const sc = Math.min(1, (W - X(260)) / tw);
    const w = tw * sc, y = H - Y(70);
    ctx.save(); ctx.globalAlpha = a;
    G.tornPaper(ctx, W / 2 - w / 2 - X(46), y - Y(72), w + X(92), Y(104), { fill: 'rgba(255,253,248,0.93)', seed: 7 + si, shadow: true });
    const who = line.who === 'guide' ? '向导' : '游客';
    G.text(ctx, who, W / 2 - w / 2 - X(32), y - Y(50), { size: Y(20), fam: ZH, color: line.who === 'guide' ? RED : ICE, boil: 0 });
    G.text(ctx, text, W / 2, y, { size: size * sc, fam: ZH, weight: 500, color: INK, align: 'center', boil: 0 });
    ctx.restore();
    void s1;
  }

  // a looping walk phase for a person walking in place
  const wph = (t, d = 0) => ((t + d) / (2 * S.STEP)) % 1;

  // ================= SHOTS =================
  // 1 · base at the Glacier Lagoon: hello, then the Unimog
  const BASE = { guide: 380, asker: 660, friend: 800, kid: 925, elder: 1050 };
  function shotBase(ctx, t) {
    backdrop(ctx, t);
    gravel(ctx, Y(760));
    unimog(ctx, X(1520), Y(905), X(0.72), { facing: -1, t });
    const gy = Y(915);
    for (const id of ['elder', 'kid', 'friend', 'asker']) {
      const o = { look: -0.7, helmet: false };
      if (t > ev.unimog) { o.look = 0.9; }
      if (t > ev.hello + 0.3 && t < ev.hello + 2.6 && id === 'kid') o.gesture = 'wave';
      if (t > ev.unimog + 0.2 && t < ev.unimog + 2.4) { o.eyes = 'wide'; o.mouth = id === 'asker' ? undefined : 'o'; o.brows = 'up'; }
      actor(ctx, id, X(BASE[id]), gy, 0.6, t, o);
    }
    const g = { look: 0.6 };
    if (t > ev.hello + 0.1 && t < ev.hello + 2.6) { g.gesture = 'wave'; g.eyes = 'happy'; }
    else if (t > ev.jeep + 0.4 && t < ev.jeep + 5) { g.gesture = 'point'; g.look = 0.9; }
    actor(ctx, 'guide', X(BASE.guide), gy, 0.66, t, g);
    card(ctx, t, ev.unimog, ev.drive + 1, X(1500), Y(250), X(470), Y(150), (c) => {
      zh(c, '乌尼莫克', 0, -Y(8), Y(62));
      zh(c, '超级吉普车', 0, Y(44), Y(34), '#5D6B78');
    }, { rot: 0.03, seed: 41 });
    title(ctx, t, 0, ev.hello + 1.2);
  }
  function title(ctx, t, t0, t1) {
    const a = clamp((t - t0 - 0.2) / 0.6), out = clamp((t1 - t) / 0.5);
    if (a <= 0 || out <= 0) return;
    ctx.save(); ctx.globalAlpha = a * out;
    const k = 0.92 + 0.08 * ease.outBack(a);
    ctx.translate(W / 2, Y(260)); ctx.scale(k, k);
    G.tornPaper(ctx, -X(420), -Y(150), X(840), Y(290), { fill: 'rgba(255,253,248,0.95)', seed: 12, shadow: true });
    G.text(ctx, 'Blue Iceland', 0, -Y(50), { size: Y(58), fam: LAT, weight: 800, color: ICE, align: 'center', boil: 0 });
    zh(ctx, '冰洞探险', 0, Y(50), Y(104));
    zh(ctx, '出发前须知', 0, Y(112), Y(38), '#5D6B78');
    ctx.restore();
  }

  // 2 · the drive: side view, scrolling landscape, a 30-minute clock
  function shotDrive(ctx, t, s) {
    const dt = t - ev.drive;
    const speed = X(520);
    sky(ctx, '#8EB9D6', '#E3EEF3', '#EFE9DF');
    ridge(ctx, dt * X(30), Y(520), Y(240), X(360), '#5D6B78', 21, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, lerp(X(1500), X(700), s.u), Y(500), X(1600));
    ridge(ctx, dt * X(140), Y(720), Y(110), X(260), '#6F655C', 23, { hatch: { color: 'rgba(0,0,0,0.12)', gap: 9 } });
    gravel(ctx, Y(800), dt * speed, { fill: '#6E675F', dots: 110, seed: 640 });
    const bumpK = t > ev.bumpy ? 1 : 0.35;
    const bounce = (Math.abs(Math.sin(dt * 7.3)) * 10 + Math.abs(Math.sin(dt * 3.1)) * 8) * bumpK;
    const tilt = Math.sin(dt * 2.3) * 0.015 * bumpK;
    // dust behind the truck
    for (let i = 0; i < 10; i++) {
      const age = ((dt * 2 + i * 0.1) % 1);
      ctx.save(); ctx.globalAlpha = 0.35 * (1 - age);
      G.ellipse(ctx, X(560) - age * X(320), Y(930) - age * Y(60), X(30 + age * 60), Y(20 + age * 40), { fill: '#B9AE9F', lw: 0, seed: 660 + i });
      ctx.restore();
    }
    unimog(ctx, X(960), Y(960), X(0.78), { roll: (dt * speed) / X(0.78 * 110), bounce, tilt, faces: 4, t });
    if (t > ev.bumpy + 0.2) {
      for (const [k, dx] of [[0, -230], [1, -40], [2, 140]]) {
        const a = clamp((t - ev.bumpy - 0.2 - k * 0.15) / 0.3);
        ctx.save(); ctx.globalAlpha = a; zh(ctx, '！', X(960 + dx), Y(520) - Math.abs(Math.sin(t * 6 + k)) * Y(18), Y(70), RED); ctx.restore();
      }
    }
    clockCard(ctx, t, ev.thirty, null, X(330), Y(170));
  }

  // 3 · the parking lot: helmets and crampons
  const LOT = { guide: 330, asker: 760, friend: 920, kid: 1070, elder: 1220 };
  const giveT = (kind, i) => (kind === 'helmet' ? ev.helmet : ev.crampon) + i * 0.22;
  function shotGear(ctx, t) {
    sky(ctx);
    ridge(ctx, X(500), Y(470), Y(200), X(320), '#5D6B78', 31, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, -X(100), Y(470), X(2200));
    // the moraine and the glacier edge ahead
    ridge(ctx, X(100), Y(640), Y(70), X(200), '#7A7068', 33, { hatch: { color: 'rgba(0,0,0,0.12)', gap: 9 } });
    gravel(ctx, Y(700), 0, { fill: '#857D74', seed: 650 });
    // parking sign
    G.rrect(ctx, X(1630), Y(560), X(14), Y(200), 4, { fill: '#55595F', lw: 3, seed: 671 });
    G.rrect(ctx, X(1580), Y(500), X(110), Y(110), 12, { fill: '#2F6FB5', lw: 4, seed: 672 });
    G.text(ctx, 'P', X(1635), Y(590), { size: Y(84), fam: LAT, weight: 800, color: '#FFFFFF', align: 'center', boil: 0 });
    unimog(ctx, X(1700), Y(790), X(0.4), { facing: -1, t });
    const gy = Y(930);
    // tourists (back to front by x)
    GROUP.forEach((id, i) => {
      const hT = giveT('helmet', i) + 0.7, cT = giveT('crampon', i) + 0.7;
      const o = { look: -0.6, helmet: t >= hT, crampon: t >= cT };
      if (t >= hT && t < hT + 0.5) o.eyes = 'happy';
      if (t > ev.hold && t < ev.hold + 2.4 && o.crampon) { o.handR = [130, -300]; }
      if (id === 'asker' && between(t, ev.ask - 0.2, ev.walk)) { o.brows = 'up'; o.gesture = 'think'; o.look = -0.8; }
      actor(ctx, id, X(LOT[id]), gy, 0.6, t, o);
    });
    const g = { look: 0.6, helmet: true };
    if (between(t, ev.helmet - 0.3, ev.crampon + 1.4)) g.gesture = 'point';
    if (between(t, ev.path, ev.path + 3)) { g.gesture = 'pointUp'; }
    actor(ctx, 'guide', X(LOT.guide), gy, 0.66, t, g);
    // gear flying from the guide to each tourist
    const from = [X(LOT.guide + 120), Y(700)];
    GROUP.forEach((id, i) => {
      const s = 0.6 * SIZE[id];
      for (const kind of ['helmet', 'crampon']) {
        const u = clamp((t - giveT(kind, i)) / 0.7);
        if (u <= 0 || u >= 1) continue;
        const to = kind === 'helmet' ? headAt(X(LOT[id]), gy, X(0.6), id) : [X(LOT[id]) + X(92 * s), gy - Y(180 * s)];
        const e = ease.inOutQuad(u);
        const x = lerp(from[0], to[0], e), y = lerp(from[1], to[1], e) - Math.sin(Math.PI * u) * Y(220);
        if (kind === 'helmet') helmetIcon(ctx, x, y, X(s));
        else crampon(ctx, x, y, X(s * 1.1), u * 6);
      }
    });
    // the cards
    card(ctx, t, ev.helmet - 0.2, ev.hold, X(760), Y(170), X(300), Y(220), (c) => {
      helmetIcon(c, 0, Y(48), 0.62); zh(c, '头盔', 0, Y(82), Y(46));
    }, { rot: -0.04, seed: 51 });
    card(ctx, t, ev.crampon - 0.2, ev.path, X(1120), Y(170), X(300), Y(220), (c) => {
      crampon(c, 0, -Y(96), 0.6, 0); zh(c, '冰爪', 0, Y(82), Y(46));
    }, { rot: 0.03, seed: 52 });
    card(ctx, t, ev.wear, ev.hold, X(390), Y(170), X(360), Y(120), (c) => { zh(c, '头盔请戴好', -X(20), Y(16), Y(46)); tick(c, X(150), Y(0), 0.8, clamp((t - ev.wear - 0.4) / 0.4)); }, { rot: 0.02, seed: 53 });
    card(ctx, t, ev.hold, ev.path, X(1460), Y(170), X(360), Y(120), (c) => { zh(c, '冰爪自己拿着', 0, Y(16), Y(46)); }, { rot: -0.02, seed: 54 });
    // the route: parking lot -> ice cave
    card(ctx, t, ev.path, ev.walk + 1, X(960), Y(170), X(980), Y(170), (c) => {
      G.rrect(c, -X(440), -Y(40), X(80), Y(80), 12, { fill: '#2F6FB5', lw: 3.5, seed: 61 });
      G.text(c, 'P', -X(400), Y(26), { size: Y(62), fam: LAT, weight: 800, color: '#FFFFFF', align: 'center', boil: 0 });
      zh(c, '停车场', -X(270), Y(16), Y(44));
      const u = clamp((t - ev.path - 0.4) / 1.4);
      G.line(c, [[-X(170), 0], [lerp(-X(170), X(170), u), 0]], { lw: 7, color: '#8E877F', seed: 62 });
      if (u > 0.95) G.line(c, [[X(146), -Y(18)], [X(172), 0], [X(146), Y(18)]], { lw: 7, color: '#8E877F', seed: 63 });
      crampon(c, lerp(-X(150), X(140), u), -Y(44), 0.3, 1.57);
      zh(c, '冰洞', X(260), Y(16), Y(44));
      G.poly(c, [[X(330), Y(40)], [X(350), -Y(30)], [X(400), -Y(46)], [X(450), -Y(30)], [X(470), Y(40)]], { fill: '#BFE6F7', lw: 3.5, seed: 64, step: 20 });
      G.poly(c, [[X(370), Y(40)], [X(380), Y(0)], [X(400), -Y(14)], [X(420), Y(0)], [X(430), Y(40)]], { fill: '#1E5F8F', lw: 0, seed: 65, step: 20 });
    }, { rot: -0.01, seed: 55 });
  }

  // 4 · the moraine walk toward the cave mouth
  function walkPos(i, t) {
    const u = clamp((t - ev.walk) / (ev.cave - ev.walk));
    const k = 0.42 + 0.34 * u - i * 0.13;
    return { x: X(lerp(200, 1240, k) + Math.sin(k * 7) * 50), y: lerp(Y(1150), Y(650), Math.pow(clamp(k, 0, 1), 0.85)), s: lerp(0.9, 0.3, k), k };
  }
  function shotWalk(ctx, t) {
    sky(ctx);
    ridge(ctx, X(900), Y(450), Y(200), X(330), '#5D6B78', 41, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    // glacier front with the cave mouth
    G.poly(ctx, [[-X(100), Y(560)], [X(500), Y(500)], [X(1000), Y(470)], [X(1500), Y(500)], [X(2020), Y(540)], [X(2020), Y(720)], [-X(100), Y(720)]],
      { fill: '#EAF3F7', lw: 4, seed: 42, step: 40, hatch: { color: 'rgba(60,140,190,0.25)', gap: 10, angle: 0.2 } });
    const mx = X(1290), my = Y(650);
    const gl = ctx.createRadialGradient(mx, my - Y(40), 0, mx, my - Y(40), X(160));
    gl.addColorStop(0, 'rgba(90,190,240,0.6)'); gl.addColorStop(1, 'rgba(90,190,240,0)');
    ctx.fillStyle = gl; ctx.fillRect(mx - X(200), my - Y(220), X(400), Y(300));
    G.poly(ctx, [[mx - X(110), my], [mx - X(90), my - Y(80)], [mx, my - Y(120)], [mx + X(90), my - Y(80)], [mx + X(110), my]], { fill: '#7FCBEF', lw: 4, seed: 43, step: 24 });
    G.poly(ctx, [[mx - X(70), my], [mx - X(50), my - Y(60)], [mx, my - Y(84)], [mx + X(50), my - Y(60)], [mx + X(70), my]], { fill: '#1B5684', lw: 0, seed: 44, step: 24 });
    // moraine: hummocks of dark gravel and boulders
    ridge(ctx, X(300), Y(700), Y(60), X(180), '#5E5852', 45, { hatch: { color: 'rgba(0,0,0,0.15)', gap: 8 } });
    gravel(ctx, Y(690), 0, { fill: '#6A635C', dots: 160, seed: 660 });
    for (let i = 0; i < 14; i++) {
      const bx = X(U.hash(i, 71) * 1920), by = Y(760 + U.hash(i, 72) * 300), r = X(18 + 50 * U.hash(i, 73)) * (by / Y(900));
      G.poly(ctx, [[bx - r, by], [bx - r * 0.7, by - r * 0.7], [bx, by - r * 0.9], [bx + r * 0.8, by - r * 0.6], [bx + r, by]], { fill: U.hash(i, 74) > 0.5 ? '#4E4944' : '#827A71', lw: 3.5, seed: 680 + i, step: 20, hatch: { color: 'rgba(0,0,0,0.15)', gap: 6 } });
    }
    // the path (pale trodden line)
    const path = [];
    for (let k = -0.1; k <= 0.75; k += 0.03) path.push([X(lerp(200, 1240, k) + Math.sin(k * 7) * 50), lerp(Y(1150), Y(650), Math.pow(k, 0.85))]);
    G.line(ctx, path, { lw: 10, color: 'rgba(190,180,165,0.6)', seed: 690 });
    // hikers, far first; on "路不平" they wobble
    const ids = ['guide', ...GROUP];
    const hard = t > ev.hard;
    ids.map((id, i) => ({ id, i, p: walkPos(i, t) })).sort((a, b) => a.p.y - b.p.y).forEach(({ id, i, p }) => {
      if (p.y > H + Y(40)) return;
      const o = { helmet: true, crampon: id !== 'guide', walk: wph(t, i * 0.3), look: -0.5 };
      if (hard) o.rot = Math.sin(t * 3 + i) * 0.04;
      if (hard && id === 'kid' && between(t, ev.hard + 0.5, ev.hard + 1.6)) { o.rot = -0.14; o.eyes = 'wide'; o.handL = [-170, -330]; o.mouth = 'o'; }
      if (id === 'guide' && between(t, ev.slow, ev.slow + 2.5)) { o.gesture = 'point'; o.look = 0.4; o.lookY = 0.5; o.walk = undefined; }
      actor(ctx, id, p.x, p.y, X(p.s), t, o);
    });
    clockCard(ctx, t, ev.walk + 0.3, ev.hard, X(330), Y(170));
    card(ctx, t, ev.moraine, ev.hard, X(1450), Y(170), X(520), Y(170), (c) => {
      zh(c, '冰碛', 0, -Y(14), Y(62));
      if (t > ev.rocks) zh(c, '= 石头 + 沙子', 0, Y(50), Y(38), '#5D6B78');
    }, { rot: 0.02, seed: 71 });
    if (between(t, ev.moraine + 0.3, ev.hard)) {
      const a = clamp((t - ev.moraine - 0.3) / 0.4);
      ctx.save(); ctx.globalAlpha = a;
      G.line(ctx, [[X(1440), Y(260)], [X(1500), Y(560)], [X(1560), Y(800)]], { lw: 5, color: INK, seed: 72 });
      G.line(ctx, [[X(1530), Y(770)], [X(1560), Y(805)], [X(1580), Y(762)]], { lw: 5, color: INK, seed: 73 });
      ctx.restore();
    }
    meterCard(ctx, t, ev.meter, null, X(360), Y(170));
    card(ctx, t, ev.slow, null, X(1480), Y(170), X(520), Y(130), (c) => { zh(c, '慢慢走 · 注意脚下', 0, Y(18), Y(48)); }, { rot: -0.02, seed: 74 });
  }

  // 5 · inside the ice cave: other groups, stay together, the helmet rule
  const CAVE = { guide: 460, asker: 760, friend: 900, kid: 1030, elder: 1160 };
  const OTHERS = [
    { x: 260, y: 720, s: 0.3, helmet: '#F2C94C', shirts: ['#3E6B8E', '#A04A3A', '#4C7A4A', '#8A6AA8'] },
    { x: 1560, y: 730, s: 0.32, helmet: '#F4F4F0', shirts: ['#C27A2A', '#2F5E7E', '#7E2F4A', '#5A5A62'] },
    { x: 1020, y: 640, s: 0.22, helmet: '#4CA35A', shirts: ['#B84A3A', '#3A5A8A', '#D0A040'] },
  ];
  function caveBg(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#0F4C78'); g.addColorStop(0.5, '#2E86C1'); g.addColorStop(1, '#BFE3F3');
    ctx.fillStyle = g; ctx.fillRect(-W, -H, W * 3, H * 3);
    // scalloped ice (the cave's dimpled walls)
    for (let i = 0; i < 70; i++) {
      const x = X(U.hash(i, 81) * 2000 - 40), y = Y(U.hash(i, 82) * 620 - 40), r = X(60 + 90 * U.hash(i, 83));
      ctx.save(); ctx.globalAlpha = 0.18 + 0.2 * U.hash(i, 84);
      G.ellipse(ctx, x, y, r, r * 0.7, { fill: U.hash(i, 85) > 0.5 ? '#9ADCF7' : '#5AB2E3', lw: 0, seed: 800 + i });
      ctx.restore();
    }
    // light from the entrance, top right
    const lx = X(1700), ly = Y(120);
    const gl = ctx.createRadialGradient(lx, ly, 0, lx, ly, X(700));
    gl.addColorStop(0, 'rgba(230,250,255,0.55)'); gl.addColorStop(1, 'rgba(230,250,255,0)');
    ctx.fillStyle = gl; ctx.fillRect(-W, -H, W * 3, H * 3);
    // darker arch edges
    G.poly(ctx, [[-X(100), -Y(100)], [X(260), -Y(100)], [X(140), Y(300)], [X(60), Y(720)], [-X(100), Y(780)]], { fill: 'rgba(8,40,70,0.55)', lw: 4, seed: 861, step: 40 });
    G.poly(ctx, [[W + X(100), -Y(100)], [X(1720), -Y(100)], [X(1820), Y(260)], [X(1880), Y(700)], [W + X(100), Y(760)]], { fill: 'rgba(8,40,70,0.5)', lw: 4, seed: 862, step: 40 });
    G.poly(ctx, [[-X(100), -Y(100)], [W + X(100), -Y(100)], [W + X(100), Y(40)], [X(1400), Y(90)], [X(960), Y(60)], [X(500), Y(100)], [-X(100), Y(50)]], { fill: 'rgba(8,40,70,0.45)', lw: 4, seed: 863, step: 40 });
    // floor: ice and grit
    G.poly(ctx, [[-X(100), Y(700)], [X(600), Y(660)], [X(1300), Y(670)], [W + X(100), Y(700)], [W + X(100), H + Y(100)], [-X(100), H + Y(100)]], { fill: '#CFE6EF', lw: 4, seed: 864, step: 50, hatch: { color: 'rgba(60,120,160,0.2)', gap: 12, angle: 0.1 } });
    for (let i = 0; i < 40; i++) {
      const x = X(U.hash(i, 91) * 1920), y = Y(700 + U.hash(i, 92) * 380);
      G.ellipse(ctx, x, y, X(4 + 6 * U.hash(i, 93)), Y(3 + 3 * U.hash(i, 94)), { fill: '#8FA6B3', lw: 0, seed: 900 + i });
    }
    void t;
  }
  function otherGroups(ctx, t) {
    OTHERS.forEach((g, gi) => g.shirts.forEach((shirt, k) => {
      const x = X(g.x + (k - g.shirts.length / 2) * 90 * g.s / 0.3) + Math.sin(t * 0.6 + gi * 2 + k) * X(10);
      const st = { skin: Ch.SKIN_TONES[(k + gi) % 3], hair: ['#2A1E18', '#6A4A2A', '#151515', '#B8A070'][k % 4], hairStyle: k % 2 ? 'short' : 'ponytail',
        outfit: 'hoodie', shirt, trim: shirt, bottoms: 'pants', shorts: '#30343C', headwear: 'helmet', headwearColor: g.helmet };
      Ch.person(ctx, { x, y: Y(g.y + (k % 2) * 14), s: X(g.s), pose: 'stand', style: st, look: Math.sin(t * 0.5 + k) * 0.8, lookY: -0.3, mouth: 'smile', seed: 1000 + gi * 10 + k });
    }));
  }
  function shotCave(ctx, t) {
    // camera: push in on the asker for the photo question, back out for the rule
    const zk = [[ev.cave, 1, 960, 540], [ev.photo - 0.3, 1, 960, 540], [ev.photo + 0.6, 1.35, 820, 600], [ev.rule, 1.35, 820, 600], [ev.rule + 1.0, 1, 960, 540]];
    let i = 0; while (i < zk.length - 2 && t > zk[i + 1][0]) i++;
    const u = ease.inOutCubic(clamp((t - zk[i][0]) / Math.max(0.001, zk[i + 1][0] - zk[i][0])));
    const z = lerp(zk[i][1], zk[i + 1][1], u), cx = X(lerp(zk[i][2], zk[i + 1][2], u)), cy = Y(lerp(zk[i][3], zk[i + 1][3], u));
    ctx.save();
    ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-cx, -cy);
    caveBg(ctx, t);
    otherGroups(ctx, t);
    const gy = Y(950);
    // the rope loop around our group on "请一直跟着我们的团"
    const loopA = clamp((t - ev.follow) / 1.0) * (1 - clamp((t - ev.photo + 0.5) / 0.5));
    if (loopA > 0) {
      ctx.save(); ctx.globalAlpha = loopA;
      ctx.setLineDash([X(26), X(18)]); ctx.lineDashOffset = -t * 40; ctx.lineWidth = X(7); ctx.strokeStyle = '#E9B73E';
      ctx.beginPath(); ctx.ellipse(X(810), Y(810), X(470), Y(250), 0, 0, Math.PI * 2 * clamp((t - ev.follow) / 1.0)); ctx.stroke();
      ctx.restore();
    }
    // the kid wanders toward the white helmets, then comes back
    const strayU = clamp((t - ev.stray) / 1.2) * (1 - clamp((t - ev.stray - 1.8) / 1.0));
    const kidX = X(lerp(CAVE.kid, 1420, ease.inOutQuad(strayU)));
    const lift = clamp((t - ev.lift) / 0.6) * (1 - clamp((t - ev.no - 0.3) / 0.5));
    const order = ['elder', 'kid', 'friend', 'asker'];
    for (const id of order) {
      const x = id === 'kid' ? kidX : X(CAVE[id]);
      const o = { helmet: true, look: -0.5 };
      if (id === 'kid' && strayU > 0.02) { o.walk = strayU < 1 ? wph(t) : undefined; o.look = 0.8; if (t > ev.stray + 1.8) { o.look = -0.8; o.eyes = 'wide'; } }
      if (id === 'asker') {
        if (between(t, ev.photo - 0.2, ev.no)) { o.brows = 'up'; o.look = -0.7; }
        if (lift > 0) {
          o.helmet = false; o.bare = true;
          const s = 0.62 * SIZE.asker, hy = HEAD - 40 - lift * 90;
          o.handL = [-86, hy + 30]; o.handR = [86, hy + 30];
        }
        if (between(t, ev.no, ev.no + 1.2)) { o.eyes = 'wide'; o.mouth = 'o'; }
      }
      const p = actor(ctx, id, x, gy, X(0.62), t, o);
      if (id === 'asker' && lift > 0) helmetIcon(ctx, x, gy + (HEAD - 10 - lift * 90) * p.s, p.s);
    }
    const g = { helmet: true, look: 0.7 };
    if (between(t, ev.follow, ev.follow + 2.6)) { g.gesture = 'pointUp'; }
    if (between(t, ev.stray + 0.8, ev.stray + 2.4)) { g.gesture = 'wave'; g.look = 1; g.brows = 'up'; }
    if (between(t, ev.no - 0.1, ev.no + 2.0)) { g.gesture = 'point'; g.brows = 'down'; g.look = 1; }
    actor(ctx, 'guide', X(CAVE.guide), gy, X(0.66), t, g);
    if (between(t, ev.stray + 0.9, ev.stray + 2.6)) {
      const a = pop(t, ev.stray + 0.9);
      ctx.save(); ctx.translate(X(1420), Y(500)); ctx.scale(a, a);
      G.ellipse(ctx, 0, 0, X(52), X(52), { fill: '#FFFFFF', lw: 4, seed: 951 });
      G.line(ctx, [[-X(22), -X(22)], [X(22), X(22)]], { lw: 10, color: '#D02A1E', seed: 952 });
      G.line(ctx, [[X(22), -X(22)], [-X(22), X(22)]], { lw: 10, color: '#D02A1E', seed: 953 });
      ctx.restore();
    }
    ctx.restore();
    // screen-space signs
    OTHERS.forEach((og, gi) => {
      card(ctx, t, ev.groups + gi * 0.3, ev.follow, X(og.x), Y(og.y - 260 * og.s / 0.3 - 60), X(260), Y(80), (c) => zh(c, '别的旅行团', 0, Y(14), Y(36)), { rot: (gi - 1) * 0.03, seed: 61 + gi });
    });
    card(ctx, t, ev.follow + 0.3, ev.photo - 0.3, X(960), Y(150), X(560), Y(140), (c) => { zh(c, '跟紧我们的团！', 0, Y(20), Y(60)); }, { rot: -0.02, seed: 66 });
    card(ctx, t, ev.stray + 0.6, ev.photo - 0.3, X(960), Y(290), X(380), Y(100), (c) => { zh(c, '不要走散', 0, Y(16), Y(46), RED); }, { rot: 0.03, seed: 67 });
    if (t > ev.no + 0.05) noSign(ctx, X(1420), Y(330), X(150), ev.no + 0.05, t);
    card(ctx, t, ev.rule, null, X(1420), Y(610), X(500), Y(150), (c) => {
      zh(c, '整个行程', 0, -Y(16), Y(44), '#5D6B78'); zh(c, '不能摘头盔', 0, Y(46), Y(58), RED);
    }, { rot: -0.02, seed: 68 });
  }

  // 6 · ready: boots, warm clothes, let's go
  function shotReady(ctx, t) {
    backdrop(ctx, t);
    gravel(ctx, Y(760));
    unimog(ctx, X(1600), Y(860), X(0.55), { facing: -1, t });
    const gy = Y(950), go = t > ev.go;
    const xs = { guide: 300, asker: 560, friend: 720, kid: 860, elder: 1000 };
    for (const id of ['elder', 'kid', 'friend', 'asker']) {
      const o = { helmet: true, look: -0.5, crampon: !go };
      if (go) { o.gesture = 'cheer'; o.eyes = 'happy'; o.mouth = 'grin'; o.look = 0; }
      actor(ctx, id, X(xs[id]), gy, X(0.62), t, o);
    }
    const g = { helmet: true, look: 0.6 };
    if (between(t, ev.boots, ev.clothes + 2)) g.gesture = 'point';
    if (go) { g.gesture = 'pointUp'; g.eyes = 'happy'; }
    actor(ctx, 'guide', X(xs.guide), gy, X(0.66), t, g);
    card(ctx, t, ev.boots, null, X(1440), Y(170), X(560), Y(170), (c) => {
      boot(c, -X(170), Y(20), 0.85); zh(c, '登山靴', X(-50), Y(18), Y(52), INK, 'left'); tick(c, X(230), -Y(10), 1, clamp((t - ev.boots - 0.5) / 0.4));
    }, { rot: 0.02, seed: 81 });
    card(ctx, t, ev.clothes, null, X(1440), Y(370), X(560), Y(170), (c) => {
      jacket(c, -X(190), Y(0), 0.8); zh(c, '暖和的衣服', X(-70), Y(18), Y(48), INK, 'left'); tick(c, X(230), -Y(10), 1, clamp((t - ev.clothes - 0.5) / 0.4));
    }, { rot: -0.02, seed: 82 });
    if (go) G.confetti(ctx, t, ev.go, { n: 90, seed: 3 });
  }

  // 7 · outro: the Unimog drives off toward the glacier
  function shotOutro(ctx, t) {
    backdrop(ctx, t);
    gravel(ctx, Y(760));
    const dt = t - ev.outro;
    const x = X(700) + Math.pow(Math.max(0, dt - 0.8), 1.6) * X(160);
    unimog(ctx, x, Y(905), X(0.72), { roll: Math.pow(Math.max(0, dt - 0.8), 1.6) * X(160) / X(0.72 * 110), bounce: Math.abs(Math.sin(dt * 7)) * 6, faces: 4, t });
    const a = clamp((dt - 0.6) / 0.6);
    ctx.save(); ctx.globalAlpha = a;
    const k = 0.92 + 0.08 * ease.outBack(a);
    ctx.translate(W / 2, Y(250)); ctx.scale(k, k);
    G.tornPaper(ctx, -X(460), -Y(160), X(920), Y(320), { fill: 'rgba(255,253,248,0.95)', seed: 13, shadow: true });
    G.text(ctx, 'Blue Iceland', 0, -Y(66), { size: Y(56), fam: LAT, weight: 800, color: ICE, align: 'center', boil: 0 });
    zh(ctx, '冰洞探险', 0, Y(30), Y(96));
    zh(ctx, '跟紧团队 · 全程戴头盔', 0, Y(110), Y(42), RED);
    ctx.restore();
    snow(ctx, t, 40);
  }

  const film = Shots.film([
    { at: 0, draw: (ctx, t) => shotBase(ctx, t), cam: (s) => ({ zoom: lerp(1, 1.06, ease.inOutQuad(clamp((s.t - ev.jeep) / 3))), x: lerp(0, -X(120), ease.inOutQuad(clamp((s.t - ev.jeep) / 3))) }) },
    { at: S.cuts.drive, draw: shotDrive, in: { type: 'whip', dir: 'left', dur: 0.5 } },
    { at: S.cuts.gear, draw: (ctx, t) => shotGear(ctx, t), in: { type: 'paper', dur: 0.9 } },
    { at: S.cuts.walk, draw: (ctx, t) => shotWalk(ctx, t), in: { type: 'wipe', dir: 'left', dur: 0.7 } },
    { at: S.cuts.cave, draw: (ctx, t) => shotCave(ctx, t), in: { type: 'iris', at: [X(1290), Y(600)], dur: 1.0, color: '#0B2F4C' } },
    { at: S.cuts.ready, draw: (ctx, t) => shotReady(ctx, t), in: { type: 'paper', dur: 0.9 } },
    { at: S.cuts.outro, draw: (ctx, t) => shotOutro(ctx, t), in: { type: 'fade', dur: 0.8 } },
  ]);

  Studio.film({
    async init() { await Studio.loadFont('WenKai', 'assets/LXGWWenKai-sub.ttf', 500); },
    draw(ctx, t) {
      film(ctx, t);
      caption(ctx, t);
    },
    post: { paper: 0.4, vignette: 0.22, grain: 0.04 },
    fadeOut: 1.2,
  });
})();
