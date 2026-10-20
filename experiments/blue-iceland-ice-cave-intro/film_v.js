// THE PHONE FILM (9:16, 1080x1920): the same story and timings as film.js, composed for a tall screen
// instead of cropped from the wide one: the guide big in the foreground, the moraine path climbing up
// the screen to the cave, a tall ice cave, signs at the top and captions at the bottom.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots;
  if (G.H <= G.W) return; // wide renders use film.js
  const B = globalThis.BI;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const { actor, crampon, helmetIcon, boot, jacket, tick, unimog, ridge, iceCap, sky, clockFace, noSign, logo, zh, GROUP, SIZE, HEAD, INK, RED, ICE, LAT, pop, between, wph } = B;
  const W = 1080, H = 1920;
  const MUTED = '#5D6B78';

  // ---------- pieces ----------
  function card(ctx, t, t0, t1, x, y, w, h, inner, { rot = 0, seed = 1, fill = 'rgba(255,253,248,0.96)' } = {}) {
    const a = clamp((t - t0) / 0.4), out = t1 == null ? 1 : clamp((t1 - t) / 0.3);
    if (a <= 0 || out <= 0) return;
    const k = ease.outBack(a) * (0.7 + 0.3 * out);
    ctx.save(); ctx.globalAlpha *= out; ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k, k);
    G.tornPaper(ctx, -w / 2, -h / 2, w, h, { fill, seed, shadow: true }); inner(ctx);
    ctx.restore();
  }
  function clockCard(ctx, t, t0, t1, x, y) {
    card(ctx, t, t0, t1, x, y, 440, 180, (c) => {
      clockFace(c, -130, 0, 62, ease.inOutQuad(clamp((t - t0 - 0.3) / 2.2)));
      zh(c, '约', -40, -18, 36, MUTED, 'left'); zh(c, '30 分钟', -40, 46, 62, INK, 'left');
    }, { rot: -0.03, seed: 31 });
  }
  function meterCard(ctx, t, t0, t1, x, y) {
    card(ctx, t, t0, t1, x, y, 440, 180, (c) => {
      zh(c, '难度：中等', 0, -22, 52);
      for (let k = 0; k < 5; k++) {
        const on = k < 3 && t > t0 + 0.5 + k * 0.25;
        G.rrect(c, -160 + k * 66, 12, 54, 40, 10, { fill: on ? ['#5FA85A', '#E9B73E', '#E58A3A'][k] : '#E3DED5', lw: 3, seed: 740 + k });
      }
    }, { rot: 0.02, seed: 37 });
  }
  function vsnow(ctx, t, n = 60) {
    ctx.save();
    for (let i = 0; i < n; i++) {
      const x = ((U.hash(i, 1) * W + t * (12 + U.hash(i, 2) * 20)) % (W + 40)) - 20;
      const y = ((U.hash(i, 3) * H + t * (30 + U.hash(i, 4) * 40)) % (H + 40)) - 20;
      ctx.globalAlpha = 0.45 + 0.4 * U.hash(i, 5); ctx.fillStyle = '#FFFFFF';
      ctx.beginPath(); ctx.arc(x, y, 2 + 2.5 * U.hash(i, 6), 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }
  function ground(ctx, y0, off = 0, { fill = '#77706A', dots = 120, seed = 620 } = {}) {
    G.poly(ctx, [[-100, y0], [W + 100, y0 - 10], [W + 100, H + 100], [-100, H + 100]], { fill, lw: 4, seed, step: 60 });
    for (let i = 0; i < dots; i++) {
      const xx = (((U.hash(i, seed) * (W + 200) - off * (0.6 + 0.4 * U.hash(i, 3))) % (W + 200)) + W + 200) % (W + 200) - 100;
      const yy = y0 + 10 + U.hash(i, seed + 1) * (H - y0);
      const r = (3 + 10 * U.hash(i, seed + 2)) * (0.6 + (yy - y0) / (H - y0 + 1));
      G.ellipse(ctx, xx, yy, r * 1.4, r, { fill: U.hash(i, 9) > 0.5 ? '#5C5650' : '#8E877F', lw: r > 6 ? 2.5 : 0, seed: seed + i });
    }
  }
  function lagoon(ctx, t, y0 = 860, y1 = 1060) {
    G.poly(ctx, [[-100, y0], [W + 100, y0 - 8], [W + 100, y1], [-100, y1 + 8]], { fill: '#4E8FB5', lw: 4, seed: 631, step: 60, hatch: { color: 'rgba(255,255,255,0.12)', gap: 14, angle: 0.05 } });
    for (const [bx, by, bw] of [[120, y0 + 50, 90], [430, y0 + 90, 60], [700, y0 + 30, 120], [980, y0 + 100, 70]]) {
      const bob = Math.sin(t * 0.8 + bx) * 3;
      G.poly(ctx, [[bx - bw, by + bob], [bx - bw * 0.6, by - bw * 0.5 + bob], [bx - bw * 0.1, by - bw * 0.7 + bob], [bx + bw * 0.5, by - bw * 0.4 + bob], [bx + bw, by + bob]],
        { fill: '#EEF7FB', lw: 3.5, seed: 640 + bx, step: 26, hatch: { color: 'rgba(60,150,210,0.35)', gap: 7, angle: -0.5 } });
    }
  }
  function lagoonScene(ctx, t) {
    sky(ctx);
    ridge(ctx, 0, 820, 300, 280, '#5D6B78', 11, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, 80, 800, 760);
    lagoon(ctx, t);
    ground(ctx, 1050);
  }
  const titleCard = (ctx, t, t0, t1, line, y = 300) => {
    const a = clamp((t - t0 - 0.1) / 0.4), out = t1 == null ? 1 : clamp((t1 - t) / 0.5);
    if (a <= 0 || out <= 0) return;
    ctx.save(); ctx.globalAlpha *= a * out; ctx.translate(W / 2, y);
    G.tornPaper(ctx, -500, -190, 1000, 400, { fill: 'rgba(255,253,248,0.96)', seed: 12, shadow: true });
    logo(ctx, t, t0 + 0.3, { width: 880, line });
    ctx.restore();
  };

  // ---------- 1 · hello at the lagoon, the Unimog behind ----------
  const ROW = { asker: 470, friend: 610, kid: 740, elder: 870 };
  function shotHello(ctx, t) {
    lagoonScene(ctx, t);
    const lift = ease.outBack(clamp((t - ev.unimog) / 0.5)) * 0.05; // the truck "hops" when it's named
    unimog(ctx, 820, 1215, 0.42 + lift, { facing: -1, t });
    for (const id of ['elder', 'kid', 'friend', 'asker']) {
      const o = { look: -0.7 };
      if (t > ev.unimog) o.look = 0.9;
      if (between(t, ev.hello + 0.3, ev.hello + 2.6) && id === 'kid') o.gesture = 'wave';
      if (between(t, ev.unimog + 0.2, ev.unimog + 2.4)) { o.eyes = 'wide'; o.brows = 'up'; if (id !== 'asker') o.mouth = 'o'; }
      actor(ctx, id, ROW[id], 1340, 0.58, t, o);
    }
    const g = { look: 0.5 };
    if (between(t, ev.hello + 0.1, ev.hello + 2.6)) { g.gesture = 'wave'; g.eyes = 'happy'; }
    else if (between(t, ev.jeep + 0.4, ev.jeep + 5)) { g.gesture = 'point'; g.look = 0.9; }
    actor(ctx, 'guide', 230, 1600, 0.95, t, g);
    card(ctx, t, ev.unimog, ev.drive + 1, 760, 820, 460, 160, (c) => { zh(c, '乌尼莫克', 0, -6, 64); zh(c, '超级吉普车', 0, 50, 34, MUTED); }, { rot: 0.03, seed: 41 });
    titleCard(ctx, t, 0, ev.hello + 2.7, '冰洞探险 · 出发前须知');
  }

  // ---------- 2 · the drive: side view, the land scrolling, a big clock on top ----------
  function shotDrive(ctx, t) {
    const dt = t - ev.drive, speed = 520;
    sky(ctx, '#8EB9D6', '#E3EEF3', '#EFE9DF');
    ridge(ctx, dt * 30, 900, 330, 300, '#5D6B78', 21, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, lerp(900, 120, clamp(dt / 9)), 880, 1400);
    ridge(ctx, dt * 140, 1110, 120, 220, '#6F655C', 23, { hatch: { color: 'rgba(0,0,0,0.12)', gap: 9 } });
    ground(ctx, 1180, dt * speed, { fill: '#6E675F', dots: 140, seed: 640 });
    const bumpK = t > ev.bumpy ? 1 : 0.35;
    const bounce = (Math.abs(Math.sin(dt * 7.3)) * 10 + Math.abs(Math.sin(dt * 3.1)) * 8) * bumpK;
    for (let i = 0; i < 10; i++) {
      const age = (dt * 2 + i * 0.1) % 1;
      ctx.save(); ctx.globalAlpha = 0.35 * (1 - age);
      G.ellipse(ctx, 230 - age * 260, 1350 - age * 60, 26 + age * 50, 18 + age * 34, { fill: '#B9AE9F', lw: 0, seed: 660 + i });
      ctx.restore();
    }
    unimog(ctx, 560, 1390, 0.6, { roll: (dt * speed) / (0.6 * 110), bounce, tilt: Math.sin(dt * 2.3) * 0.015 * bumpK, faces: 4, t });
    if (t > ev.bumpy + 0.2) for (const [k, dx] of [[0, -170], [1, -30], [2, 110]]) {
      const a = clamp((t - ev.bumpy - 0.2 - k * 0.15) / 0.3);
      ctx.save(); ctx.globalAlpha = a; zh(ctx, '！', 560 + dx, 930 - Math.abs(Math.sin(t * 6 + k)) * 18, 76, RED); ctx.restore();
    }
    ctx.save(); ctx.translate(W / 2, 330); ctx.scale(1.3, 1.3); clockCard(ctx, t, ev.thirty, null, 0, 0); ctx.restore();
  }

  // ---------- 3 · the parking lot: helmets and crampons ----------
  const LOT = { asker: 500, friend: 640, kid: 770, elder: 900 };
  const giveT = (kind, i) => (kind === 'helmet' ? ev.helmet : ev.crampon) + i * 0.22;
  function shotGear(ctx, t) {
    sky(ctx);
    ridge(ctx, 300, 760, 260, 280, '#5D6B78', 31, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    iceCap(ctx, -100, 760, 1300);
    ridge(ctx, 100, 960, 80, 200, '#7A7068', 33, { hatch: { color: 'rgba(0,0,0,0.12)', gap: 9 } });
    ground(ctx, 1010, 0, { fill: '#857D74', seed: 650 });
    G.rrect(ctx, 985, 860, 12, 170, 4, { fill: '#55595F', lw: 3, seed: 671 });
    G.rrect(ctx, 940, 800, 100, 100, 12, { fill: '#2F6FB5', lw: 4, seed: 672 });
    G.text(ctx, 'P', 990, 878, { size: 76, fam: LAT, weight: 800, color: '#FFFFFF', align: 'center', boil: 0 });
    unimog(ctx, 820, 1060, 0.26, { facing: -1, t });
    const gy = 1350;
    GROUP.forEach((id, i) => {
      const hT = giveT('helmet', i) + 0.7, cT = giveT('crampon', i) + 0.7;
      const o = { look: -0.6, helmet: t >= hT, crampon: t >= cT };
      if (between(t, hT, hT + 0.5)) o.eyes = 'happy';
      if (between(t, ev.hold, ev.hold + 2.4) && o.crampon) o.handR = [130, -300];
      if (id === 'asker' && between(t, ev.ask - 0.2, ev.walk)) { o.brows = 'up'; o.gesture = 'think'; o.look = -0.8; }
      actor(ctx, id, LOT[id], gy, 0.6, t, o);
    });
    const g = { look: 0.6, helmet: true };
    if (between(t, ev.helmet - 0.3, ev.crampon + 1.4)) g.gesture = 'point';
    if (between(t, ev.path, ev.path + 3)) g.gesture = 'pointUp';
    actor(ctx, 'guide', 210, 1600, 0.92, t, g);
    const from = [360, 1180];
    GROUP.forEach((id, i) => {
      const s = 0.6 * SIZE[id];
      for (const kind of ['helmet', 'crampon']) {
        const u = clamp((t - giveT(kind, i)) / 0.7);
        if (u <= 0 || u >= 1) continue;
        const to = kind === 'helmet' ? [LOT[id], gy + HEAD * s] : [LOT[id] + 92 * s, gy - 180 * s];
        const e = ease.inOutQuad(u);
        const x = lerp(from[0], to[0], e), y = lerp(from[1], to[1], e) - Math.sin(Math.PI * u) * 220;
        if (kind === 'helmet') helmetIcon(ctx, x, y, s); else crampon(ctx, x, y, s * 1.1, u * 6);
      }
    });
    // signs, top of the screen
    card(ctx, t, ev.helmet - 0.2, ev.path, 330, 300, 330, 250, (c) => { helmetIcon(c, 0, 50, 0.72); zh(c, '头盔', 0, 96, 52); }, { rot: -0.04, seed: 51 });
    card(ctx, t, ev.crampon - 0.2, ev.path, 750, 300, 330, 250, (c) => { crampon(c, 0, -110, 0.7, 0); zh(c, '冰爪', 0, 96, 52); }, { rot: 0.03, seed: 52 });
    card(ctx, t, ev.wear, ev.hold, 330, 560, 400, 120, (c) => { zh(c, '头盔请戴好', -20, 18, 50); tick(c, 160, 0, 0.8, clamp((t - ev.wear - 0.4) / 0.4)); }, { rot: 0.02, seed: 53 });
    card(ctx, t, ev.hold, ev.path, 750, 560, 400, 120, (c) => { zh(c, '冰爪自己拿着', 0, 18, 50); }, { rot: -0.02, seed: 54 });
    // the route: parking lot → ice cave, as a vertical strip (it's a walk "up" the screen next)
    card(ctx, t, ev.path, ev.walk + 0.6, W / 2, 400, 900, 230, (c) => {
      G.rrect(c, -400, -50, 90, 90, 12, { fill: '#2F6FB5', lw: 3.5, seed: 61 });
      G.text(c, 'P', -355, 22, { size: 68, fam: LAT, weight: 800, color: '#FFFFFF', align: 'center', boil: 0 });
      zh(c, '停车场', -355, 92, 40);
      const u = clamp((t - ev.path - 0.4) / 1.4);
      G.line(c, [[-270, 0], [lerp(-270, 250, u), 0]], { lw: 8, color: '#8E877F', seed: 62 });
      if (u > 0.95) G.line(c, [[224, -20], [252, 0], [224, 20]], { lw: 8, color: '#8E877F', seed: 63 });
      crampon(c, lerp(-250, 230, u), -52, 0.32, 1.57);
      G.poly(c, [[300, 46], [320, -30], [355, -50], [390, -30], [410, 46]], { fill: '#BFE6F7', lw: 3.5, seed: 64, step: 20 });
      G.poly(c, [[330, 46], [340, 0], [355, -14], [370, 0], [380, 46]], { fill: '#1E5F8F', lw: 0, seed: 65, step: 20 });
      zh(c, '冰洞', 355, 92, 40);
    }, { rot: -0.01, seed: 55 });
  }

  // ---------- 4 · the moraine: the path climbs the screen to the cave ----------
  const pathXY = (k) => [540 + Math.sin(k * 6.5) * 230 * (1 - 0.6 * k), lerp(1950, 930, Math.pow(clamp(k, 0, 1), 0.8))];
  function walkPos(i, t) {
    const u = clamp((t - ev.walk) / (ev.cave - ev.walk));
    const k = 0.3 + 0.42 * u - i * 0.14;
    const [x, y] = pathXY(k);
    return { x, y, s: lerp(0.9, 0.32, clamp(k, 0, 1)), k };
  }
  function shotWalk(ctx, t) {
    sky(ctx);
    ridge(ctx, 600, 660, 260, 300, '#5D6B78', 41, { snow: true, hatch: { color: 'rgba(20,30,40,0.18)', gap: 10, angle: -0.6 } });
    G.poly(ctx, [[-100, 740], [300, 690], [700, 670], [1180, 720], [1180, 980], [-100, 980]], { fill: '#EAF3F7', lw: 4, seed: 42, step: 40, hatch: { color: 'rgba(60,140,190,0.25)', gap: 10, angle: 0.2 } });
    const mx = 610, my = 930;
    const gl = ctx.createRadialGradient(mx, my - 60, 0, mx, my - 60, 200);
    gl.addColorStop(0, 'rgba(90,190,240,0.6)'); gl.addColorStop(1, 'rgba(90,190,240,0)');
    ctx.fillStyle = gl; ctx.fillRect(mx - 240, my - 260, 480, 340);
    G.poly(ctx, [[mx - 130, my], [mx - 105, my - 100], [mx, my - 150], [mx + 105, my - 100], [mx + 130, my]], { fill: '#7FCBEF', lw: 4, seed: 43, step: 24 });
    G.poly(ctx, [[mx - 85, my], [mx - 60, my - 75], [mx, my - 105], [mx + 60, my - 75], [mx + 85, my]], { fill: '#1B5684', lw: 0, seed: 44, step: 24 });
    ridge(ctx, 300, 980, 60, 180, '#5E5852', 45, { hatch: { color: 'rgba(0,0,0,0.15)', gap: 8 } });
    ground(ctx, 960, 0, { fill: '#6A635C', dots: 220, seed: 660 });
    for (let i = 0; i < 18; i++) {
      const by = 1040 + U.hash(i, 72) * 880, bx = U.hash(i, 71) * W, r = (16 + 46 * U.hash(i, 73)) * (by / 1500);
      const [px] = pathXY(clamp(1 - (by - 930) / 1020, 0, 1));
      if (Math.abs(bx - px) < 120) continue; // keep the path clear
      G.poly(ctx, [[bx - r, by], [bx - r * 0.7, by - r * 0.7], [bx, by - r * 0.9], [bx + r * 0.8, by - r * 0.6], [bx + r, by]], { fill: U.hash(i, 74) > 0.5 ? '#4E4944' : '#827A71', lw: 3.5, seed: 680 + i, step: 20, hatch: { color: 'rgba(0,0,0,0.15)', gap: 6 } });
    }
    const path = []; for (let k = -0.05; k <= 1.0; k += 0.02) path.push(pathXY(k));
    G.line(ctx, path, { lw: 14, color: 'rgba(190,180,165,0.55)', seed: 690 });
    const ids = ['guide', ...GROUP];
    const hard = t > ev.hard;
    ids.map((id, i) => ({ id, i, p: walkPos(i, t) })).sort((a, b) => a.p.y - b.p.y).forEach(({ id, i, p }) => {
      if (p.y > H + 60) return;
      const o = { helmet: true, crampon: id !== 'guide', walk: wph(t, i * 0.3), look: -0.3 };
      if (hard) o.rot = Math.sin(t * 3 + i) * 0.04;
      if (hard && id === 'kid' && between(t, ev.hard + 0.5, ev.hard + 1.6)) { o.rot = -0.14; o.eyes = 'wide'; o.handL = [-170, -330]; o.mouth = 'o'; }
      if (id === 'guide' && between(t, ev.slow, ev.slow + 2.5)) { o.gesture = 'point'; o.lookY = 0.5; o.walk = undefined; }
      actor(ctx, id, p.x, p.y, p.s, t, o);
    });
    clockCard(ctx, t, ev.walk + 0.3, ev.hard, 280, 240);
    card(ctx, t, ev.moraine, ev.hard, 790, 240, 420, 180, (c) => { zh(c, '冰碛', 0, -12, 66); if (t > ev.rocks) zh(c, '= 石头 + 沙子', 0, 52, 38, MUTED); }, { rot: 0.02, seed: 71 });
    meterCard(ctx, t, ev.meter, null, 280, 240);
    card(ctx, t, ev.slow, null, 790, 240, 420, 180, (c) => { zh(c, '慢慢走', 0, -16, 56); zh(c, '注意脚下', 0, 52, 46, RED); }, { rot: -0.02, seed: 74 });
  }

  // ---------- 5 · the ice cave: tall, with groups in depth ----------
  const OUR = { guide: 170, asker: 400, friend: 570, kid: 730, elder: 900 };
  const OTHERS = [
    { x: 210, y: 1150, s: 0.3, helmet: '#F2C94C', shirts: ['#3E6B8E', '#A04A3A', '#4C7A4A'] },
    { x: 860, y: 1160, s: 0.32, helmet: '#F4F4F0', shirts: ['#C27A2A', '#2F5E7E', '#7E2F4A'] },
    { x: 540, y: 1040, s: 0.22, helmet: '#4CA35A', shirts: ['#B84A3A', '#3A5A8A', '#D0A040'] },
  ];
  function caveBg(ctx) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#0B3A60'); g.addColorStop(0.45, '#2E86C1'); g.addColorStop(0.62, '#7CC6EA'); g.addColorStop(1, '#C9E5F1');
    ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    for (let i = 0; i < 90; i++) {
      const x = U.hash(i, 81) * 1180 - 50, y = U.hash(i, 82) * 1100 - 40, r = 50 + 80 * U.hash(i, 83);
      ctx.save(); ctx.globalAlpha = 0.16 + 0.2 * U.hash(i, 84);
      G.ellipse(ctx, x, y, r, r * 0.7, { fill: U.hash(i, 85) > 0.5 ? '#9ADCF7' : '#5AB2E3', lw: 0, seed: 800 + i });
      ctx.restore();
    }
    const gl = ctx.createRadialGradient(540, 120, 0, 540, 120, 700);
    gl.addColorStop(0, 'rgba(230,250,255,0.5)'); gl.addColorStop(1, 'rgba(230,250,255,0)');
    ctx.fillStyle = gl; ctx.fillRect(-200, -200, W + 400, H + 400);
    // the arch: dark ice walls closing in at the sides
    G.poly(ctx, [[-100, -100], [180, -100], [90, 500], [40, 1100], [-100, 1180]], { fill: 'rgba(8,40,70,0.55)', lw: 4, seed: 861, step: 40 });
    G.poly(ctx, [[W + 100, -100], [900, -100], [990, 520], [1040, 1100], [W + 100, 1170]], { fill: 'rgba(8,40,70,0.5)', lw: 4, seed: 862, step: 40 });
    G.poly(ctx, [[-100, 1100], [400, 1060], [800, 1070], [W + 100, 1110], [W + 100, H + 100], [-100, H + 100]], { fill: '#CFE6EF', lw: 4, seed: 864, step: 50, hatch: { color: 'rgba(60,120,160,0.2)', gap: 12, angle: 0.1 } });
    for (let i = 0; i < 50; i++) G.ellipse(ctx, U.hash(i, 91) * W, 1100 + U.hash(i, 92) * 800, 4 + 6 * U.hash(i, 93), 3 + 3 * U.hash(i, 94), { fill: '#8FA6B3', lw: 0, seed: 900 + i });
  }
  function otherGroups(ctx, t) {
    OTHERS.forEach((g, gi) => g.shirts.forEach((shirt, k) => {
      const x = g.x + (k - 1) * 290 * g.s + Math.sin(t * 0.6 + gi * 2 + k) * 8;
      const st = { skin: Ch.SKIN_TONES[(k + gi) % 3], hair: ['#2A1E18', '#6A4A2A', '#151515'][k % 3], hairStyle: k % 2 ? 'short' : 'ponytail',
        outfit: 'hoodie', shirt, trim: shirt, bottoms: 'pants', shorts: '#30343C', headwear: 'helmet', headwearColor: g.helmet };
      Ch.person(ctx, { x, y: g.y + (k % 2) * 12, s: g.s, pose: 'stand', style: st, look: Math.sin(t * 0.5 + k) * 0.8, lookY: -0.3, mouth: 'smile', seed: 1000 + gi * 10 + k });
    }));
  }
  function shotCave(ctx, t) {
    // push in on the asker for the photo question, back out for the rule
    const zk = [[ev.cave, 1, 540, 960], [ev.photo - 0.3, 1, 540, 960], [ev.photo + 0.6, 1.35, 430, 1180], [ev.rule, 1.35, 430, 1180], [ev.rule + 1.0, 1, 540, 960]];
    let i = 0; while (i < zk.length - 2 && t > zk[i + 1][0]) i++;
    const u = ease.inOutCubic(clamp((t - zk[i][0]) / Math.max(0.001, zk[i + 1][0] - zk[i][0])));
    const z = lerp(zk[i][1], zk[i + 1][1], u), cx = lerp(zk[i][2], zk[i + 1][2], u), cy = lerp(zk[i][3], zk[i + 1][3], u);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-cx, -cy);
    caveBg(ctx);
    otherGroups(ctx, t);
    OTHERS.forEach((og, gi) => card(ctx, t, ev.groups + gi * 0.3, ev.follow, og.x, og.y - 600 * og.s - 40, 230, 72, (c) => zh(c, '别的旅行团', 0, 12, 34), { rot: (gi - 1) * 0.03, seed: 61 + gi }));
    const gy = 1560;
    const loopA = clamp((t - ev.follow) / 1.0) * (1 - clamp((t - ev.photo + 0.5) / 0.5));
    if (loopA > 0) {
      ctx.save(); ctx.globalAlpha = loopA; ctx.setLineDash([26, 18]); ctx.lineDashOffset = -t * 40; ctx.lineWidth = 8; ctx.strokeStyle = '#E9B73E';
      ctx.beginPath(); ctx.ellipse(535, 1400, 500, 250, 0, 0, Math.PI * 2 * clamp((t - ev.follow) / 1.0)); ctx.stroke(); ctx.restore();
    }
    const strayU = clamp((t - ev.stray) / 1.2) * (1 - clamp((t - ev.stray - 1.8) / 1.0));
    const lift = clamp((t - ev.lift) / 0.6) * (1 - clamp((t - ev.no - 0.3) / 0.5));
    for (const id of ['elder', 'kid', 'friend', 'asker']) {
      const kid = id === 'kid';
      const x = kid ? lerp(OUR.kid, 880, ease.inOutQuad(strayU)) : OUR[id];
      const y = kid ? lerp(gy, 1260, ease.inOutQuad(strayU)) : gy;
      const s = kid ? lerp(0.66, 0.42, ease.inOutQuad(strayU)) : 0.66;
      const o = { helmet: true, look: -0.5 };
      if (kid && strayU > 0.02) { o.walk = strayU < 1 ? wph(t) : undefined; o.look = 0.8; if (t > ev.stray + 1.8) { o.look = -0.8; o.eyes = 'wide'; } }
      if (id === 'asker') {
        if (between(t, ev.photo - 0.2, ev.no)) { o.brows = 'up'; o.look = -0.7; }
        if (lift > 0) { o.helmet = false; o.bare = true; const hy = HEAD - 40 - lift * 90; o.handL = [-86, hy + 30]; o.handR = [86, hy + 30]; }
        if (between(t, ev.no, ev.no + 1.2)) { o.eyes = 'wide'; o.mouth = 'o'; }
      }
      const p = actor(ctx, id, x, y, s, t, o);
      if (id === 'asker' && lift > 0) helmetIcon(ctx, x, y + (HEAD - 10 - lift * 90) * p.s, p.s);
      if (kid && between(t, ev.stray + 0.9, ev.stray + 2.6)) {
        const a = pop(t, ev.stray + 0.9);
        ctx.save(); ctx.translate(x, y - 330 * s - 60); ctx.scale(a, a);
        G.ellipse(ctx, 0, 0, 44, 44, { fill: '#FFFFFF', lw: 4, seed: 951 });
        G.line(ctx, [[-18, -18], [18, 18]], { lw: 9, color: '#D02A1E', seed: 952 }); G.line(ctx, [[18, -18], [-18, 18]], { lw: 9, color: '#D02A1E', seed: 953 });
        ctx.restore();
      }
    }
    const g = { helmet: true, look: 0.7 };
    if (between(t, ev.follow, ev.follow + 2.6)) g.gesture = 'pointUp';
    if (between(t, ev.stray + 0.8, ev.stray + 2.4)) { g.gesture = 'wave'; g.look = 1; g.brows = 'up'; }
    if (between(t, ev.no - 0.1, ev.no + 2.0)) { g.gesture = 'point'; g.brows = 'down'; g.look = 1; }
    actor(ctx, 'guide', OUR.guide, gy + 30, 0.72, t, g);
    ctx.restore();
    // signs in screen space
    card(ctx, t, ev.follow + 0.3, ev.photo - 0.3, W / 2, 230, 640, 150, (c) => zh(c, '跟紧我们的团！', 0, 22, 66), { rot: -0.02, seed: 66 });
    card(ctx, t, ev.stray + 0.6, ev.photo - 0.3, W / 2, 420, 420, 110, (c) => zh(c, '不要走散', 0, 18, 54, RED), { rot: 0.03, seed: 67 });
    if (t > ev.no + 0.05) noSign(ctx, W / 2, 330, 190, ev.no + 0.05, t);
    card(ctx, t, ev.rule, null, W / 2, 650, 560, 170, (c) => { zh(c, '整个行程', 0, -20, 46, MUTED); zh(c, '不能摘头盔', 0, 50, 66, RED); }, { rot: -0.02, seed: 68 });
  }

  // ---------- 6 · ready: boots, warm clothes, let's go ----------
  function shotReady(ctx, t) {
    lagoonScene(ctx, t);
    unimog(ctx, 830, 1190, 0.4, { facing: -1, t });
    const go = t > ev.go;
    for (const id of ['elder', 'kid', 'friend', 'asker']) {
      const o = { helmet: true, look: -0.5, crampon: !go };
      if (go) { o.gesture = 'cheer'; o.eyes = 'happy'; o.mouth = 'grin'; o.look = 0; }
      actor(ctx, id, ROW[id], 1350, 0.6, t, o);
    }
    const g = { helmet: true, look: 0.6 };
    if (between(t, ev.boots, ev.clothes + 2)) g.gesture = 'point';
    if (go) { g.gesture = 'pointUp'; g.eyes = 'happy'; }
    actor(ctx, 'guide', 230, 1600, 0.95, t, g);
    card(ctx, t, ev.boots, null, W / 2, 250, 620, 170, (c) => { boot(c, -210, 20, 0.95); zh(c, '登山靴', -80, 20, 58, INK, 'left'); tick(c, 230, -10, 1.1, clamp((t - ev.boots - 0.5) / 0.4)); }, { rot: 0.02, seed: 81 });
    card(ctx, t, ev.clothes, null, W / 2, 460, 620, 170, (c) => { jacket(c, -220, 0, 0.9); zh(c, '暖和的衣服', -110, 20, 54, INK, 'left'); tick(c, 230, -10, 1.1, clamp((t - ev.clothes - 0.5) / 0.4)); }, { rot: -0.02, seed: 82 });
    if (go) G.confetti(ctx, t, ev.go, { n: 120, seed: 3, x0: 0, x1: W });
  }

  // ---------- 7 · outro: the Unimog drives off, the logo ----------
  function shotOutro(ctx, t) {
    lagoonScene(ctx, t);
    const dt = t - ev.outro, d = Math.pow(Math.max(0, dt - 0.8), 1.6) * 150;
    unimog(ctx, 420 + d, 1320, 0.55, { roll: d / (0.55 * 110), bounce: Math.abs(Math.sin(dt * 7)) * 6, faces: 4, t });
    const a = clamp((dt - 0.4) / 0.4);
    ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, 400);
    G.tornPaper(ctx, -500, -230, 1000, 500, { fill: 'rgba(255,253,248,0.96)', seed: 13, shadow: true });
    logo(ctx, t, ev.outro + 0.5, { width: 880, line: '跟紧团队 · 全程戴头盔' });
    const ea = clamp((dt - 2.4) / 0.5);
    if (ea > 0) { ctx.globalAlpha *= ea; G.text(ctx, 'Stay with your group', 0, 190, { size: 34, fam: LAT, weight: 600, color: MUTED, align: 'center', boil: 0 }); }
    ctx.restore();
    vsnow(ctx, t, 50);
  }

  const film = Shots.film([
    { at: 0, draw: shotHello },
    { at: S.cuts.drive, draw: shotDrive, in: { type: 'whip', dir: 'left', dur: 0.5 } },
    { at: S.cuts.gear, draw: shotGear, in: { type: 'paper', dur: 0.9 } },
    { at: S.cuts.walk, draw: shotWalk, in: { type: 'wipe', dir: 'up', dur: 0.7 } },
    { at: S.cuts.cave, draw: shotCave, in: { type: 'iris', at: [610, 860], dur: 1.0, color: '#0B2F4C' } },
    { at: S.cuts.ready, draw: shotReady, in: { type: 'paper', dur: 0.9 } },
    { at: S.cuts.outro, draw: shotOutro, in: { type: 'fade', dur: 0.8 } },
  ]);
  Studio.film({
    async init() { await Studio.loadFont('WenKai', 'assets/LXGWWenKai-sub.ttf', 500); await B.loadLogo(); },
    draw(ctx, t) { film(ctx, t); B.captionV(ctx, t); },
    post: { paper: 0.4, vignette: 0.22, grain: 0.04 },
    fadeOut: 1.2,
  });
})();
