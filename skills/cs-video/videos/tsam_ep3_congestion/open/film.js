// TSAM #3 cold open: Sam lags out of his game while Ada downloads; the router between them jams up.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots, TP = globalThis.TP;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: TP.HAND, roles: TP.ROLES });
  globalThis.CAST = TP.CAST;
  const R = [960, 330];
  const SAM_LAP = [560, 760], ADA_LAP = [1360, 760];

  const mood = (t) => (t > ev.a3 ? 'angry' : t > ev.a1 ? 'busy' : 'calm');
  function cable(ctx, to, seed) {
    G.line(ctx, [[R[0], R[1] + 40], [lerp(R[0], to[0], 0.5), R[1] + 160], [to[0], to[1] - 190]], { lw: 5, color: '#4A4F5A', seed });
  }
  function onCable(to, u) { // point along the cable (quadratic-ish polyline)
    const a = [R[0], R[1] + 40], b = [lerp(R[0], to[0], 0.5), R[1] + 160], c = [to[0], to[1] - 190];
    return u < 0.5 ? [lerp(a[0], b[0], u * 2), lerp(a[1], b[1], u * 2)] : [lerp(b[0], c[0], u * 2 - 1), lerp(b[1], c[1], u * 2 - 1)];
  }
  function gameScreen(ctx, t, w, h) {
    ctx.fillStyle = '#20263A'; ctx.fillRect(-w / 2, -h / 2, w, h);
    const lag = t < ev.a1 || t > ev.a3;
    const x = lag ? -40 : -60 + ((t * 80) % 120);
    G.poly(ctx, [[x - 20, 20], [x + 20, 20], [x, -14]], { fill: '#5BD1E8', lw: 3, seed: 3 });
    for (let i = 0; i < 6; i++) G.ellipse(ctx, -100 + i * 40, -50 + (i % 2) * 14, 2.5, 2.5, { fill: '#FFF', lw: 0, seed: i });
    if (lag) G.text(ctx, 'LAG 999 ms', 0, 52, { size: 26, fam: TP.HAND, color: '#FF6B6B', align: 'center', boil: 0 });
  }
  function dlScreen(ctx, t, w, h) {
    ctx.fillStyle = '#F4F7FA'; ctx.fillRect(-w / 2, -h / 2, w, h);
    G.text(ctx, 'game.zip  40 GB', 0, -26, { size: 24, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 });
    const p = clamp((t - 2) / 60);
    G.rrect(ctx, -90, 0, 180, 24, 8, { fill: '#DDE3EA', lw: 2.5, seed: 4 });
    G.rrect(ctx, -90, 0, 180 * p + 6, 24, 8, { fill: TP.GREEN, lw: 0, seed: 5 });
    G.text(ctx, `${Math.round(p * 100)}%`, 0, 56, { size: 22, fam: TP.HAND, color: TP.MUTED, align: 'center', boil: 0 });
  }
  function scene(ctx, t) {
    TP.room(ctx, { wall: '#F3EAF6', stripe: '#E6D7EE' });
    // the shelf with the router
    G.rrect(ctx, 760, 400, 400, 20, 5, { fill: '#9C6B43', lw: 4, seed: 7 });
    cable(ctx, SAM_LAP, 11); cable(ctx, ADA_LAP, 12);
    // traffic on the cables: lots to Ada, a trickle to Sam
    const dense = t > ev.a1 - 1 ? 14 : 4;
    for (let i = 0; i < dense; i++) { const u = ((t * 0.5 + i / dense) % 1); const [x, y] = onCable(ADA_LAP, u); G.rrect(ctx, x - 12, y - 9, 24, 18, 4, { fill: TP.PALETTE ? '#E6A15A' : '#E6A15A', lw: 2.5, seed: 30 + i }); }
    for (let i = 0; i < 2; i++) { const u = ((t * (t > ev.a1 && t < ev.a3 ? 0.5 : 0.18) + i / 2) % 1); const [x, y] = onCable(SAM_LAP, u); G.rrect(ctx, x - 12, y - 9, 24, 18, 4, { fill: '#5BD1E8', lw: 2.5, seed: 50 + i }); }
    // the queue piling up beside the router
    const q = Math.floor(clamp((t - ev.a2) / (ev.a3 + 2 - ev.a2)) * 9);
    for (let i = 0; i < q; i++) TP.parcel(ctx, 700 - (i % 5) * 46, 375 - Math.floor(i / 5) * 40, 0.55, i % 2 ? '#E6A15A' : '#5BD1E8', '', (i % 3 - 1) * 0.1, 60 + i);
    TP.router(ctx, R[0], R[1], 0.95, t, mood(t), { seed: 4 });
    // desks and laptops
    TP.desk(ctx, SAM_LAP[0], 380); TP.desk(ctx, ADA_LAP[0], 380);
    TP.laptop(ctx, SAM_LAP[0], SAM_LAP[1], 0.9, (c, w, h) => gameScreen(c, t, w, h), { seed: 81 });
    TP.laptop(ctx, ADA_LAP[0], ADA_LAP[1], 0.9, (c, w, h) => dlScreen(c, t, w, h), { seed: 91 });
    // Sam
    const so = { role: 'sam', look: 0.5, seed: 2, gesture: 'typing' };
    if (t < ev.a1) { so.gesture = 'facepalm'; so.eyes = 'closed'; }
    if (t > ev.s2 && t < ev.a2) { so.gesture = 'shrug'; so.brows = 'up'; so.look = 0.9; }
    if (t > ev.s3 && t < ev.a4) { so.gesture = 'think'; so.look = 0.9; }
    if (t > ev.a4) { so.gesture = 'thumbsUp'; so.eyes = 'happy'; so.look = 0.9; }
    K.actor(ctx, TP.CAST.sam, 270, 930, 0.72, t, so);
    // Ada
    const ao = { role: 'ada', look: -0.6, seed: 1, gesture: 'typing' };
    if (t > ev.a1 && t < ev.s2) { ao.gesture = 'shrug'; ao.brows = 'up'; }
    if (t > ev.a2 && t < ev.a3) { ao.gesture = 'pointUp'; }
    if (t > ev.a3 && t < ev.s3) { ao.gesture = 'point'; ao.look = -0.9; ao.lookY = -0.6; }
    if (t > ev.a4) { ao.gesture = 'pointUp'; ao.eyes = 'happy'; }
    K.actor(ctx, TP.CAST.ada, 1660, 930, 0.72, t, ao);
    // signs
    TP.sign(K, ctx, t, ev.a2 + 1.2, ev.a3, 960, 120, 'bandwidth  ≠  latency', { size: 58, color: TP.PURPLE, seed: 3 });
    TP.sign(K, ctx, t, ev.a3 + 1.0, ev.s3 + 0.5, 960, 120, 'TRAFFIC JAM', { size: 64, color: TP.RED, rot: -0.03, seed: 4 });
    TP.sign(K, ctx, t, ev.a4 + 1.0, ev.outro, 960, 120, 'TCP slows itself down', { size: 56, color: TP.GREEN, rot: 0.02, seed: 5 });
  }
  function outro(ctx, t) {
    TP.room(ctx, { wall: '#F3EAF6', stripe: '#E6D7EE' });
    TP.episodeTitle(K, ctx, t, ev.outro, 3, 'Speed & traffic jams', 'bandwidth, latency and congestion control');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => scene(ctx, t), cam: (s) => ({ zoom: 1 + 0.04 * ease.inOutQuad(s.u) }) },
    { at: S.cuts.outro, draw: (ctx, t) => outro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]), post: { paper: 0.35, vignette: 0.2, grain: 0.04 }, fadeOut: 0.6 });
})();
