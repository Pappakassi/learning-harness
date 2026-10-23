// TSAM #2 cold open: Sam throws parcels faster than Ada can unpack them; her basket fills (Win = 0).
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots, TP = globalThis.TP;
  const { ev, ph } = S;
  const { clamp, ease } = U;
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: TP.HAND, roles: TP.ROLES });
  globalThis.CAST = TP.CAST;

  const SAM_X = 330, ADA_X = 1640, BASKET = [1330, 820];
  const HAND = [SAM_X + 120, 600];
  // the throws, simulated once: each parcel lands in the basket while there is room, else on the floor
  const start = ph('hook', 2), stop = ev.a3 + 0.4, gap = 0.55, dur = 0.9;
  const throws = [];
  for (let t0 = start; t0 < stop; t0 += gap) throws.push({ t0, land: t0 + dur });
  const unpacks = [];
  for (let t = start + 2.2; t < ev.a3; t += 1.7) unpacks.push(t);
  const evts = [...throws.map((p) => ({ t: p.land, p })), ...unpacks.map((t) => ({ t, un: true }))].sort((a, b) => a.t - b.t);
  let n = 0, floorN = 0;
  const fillAt = [];
  for (const e of evts) {
    if (e.un) { if (n > 0) n--; fillAt.push([e.t, n]); continue; }
    if (n < 6) { e.p.dest = 'basket'; n++; fillAt.push([e.t, n]); } else { e.p.dest = 'floor'; e.p.fx = BASKET[0] - 260 + (floorN * 97) % 520; e.p.rot = (floorN % 3 - 1) * 0.4; floorN++; }
  }
  const basketCount = (t) => { let v = 0; for (const [tt, c] of fillAt) if (t >= tt) v = c; return v; };
  const COLORS = ['#D9A86C', '#E7B98A', '#C99358', '#E6A15A'];

  function scene(ctx, t) {
    TP.room(ctx, { wall: '#EAF2F8', stripe: '#D6E6F2', window: [820, 170] });
    // Sam's pile of parcels still to send
    const left = Math.max(0, 12 - throws.filter((p) => t >= p.t0).length);
    for (let i = 0; i < Math.min(left, 12); i++) TP.parcel(ctx, 540 + (i % 4) * 66, 830 - Math.floor(i / 4) * 54, 0.78, COLORS[i % 4], '', (i % 2 ? 0.05 : -0.05), 200 + i);
    // basket and floor
    TP.basket(ctx, BASKET[0], BASKET[1], basketCount(t) / 6);
    for (const p of throws) if (p.dest === 'floor' && t >= p.land) TP.parcel(ctx, p.fx, 860, 0.7, '#B5835A', '', p.rot, 300 + p.fx % 50);
    // flying parcels
    throws.forEach((p, i) => {
      if (t < p.t0 || t > p.land) return;
      const end = p.dest === 'basket' ? [BASKET[0] - 20 + (i % 3) * 20, BASKET[1] - 70] : [p.fx, 860];
      const f = TP.fly(t, p.t0, dur, HAND, end, 240);
      if (f) TP.parcel(ctx, f.x, f.y, 0.7, COLORS[i % 4], String(i + 1), f.rot * 0.3, 400 + i);
    });
    // Sam
    const so = { role: 'sam', look: 0.6, seed: 2 };
    if (t < start) so.gesture = 'wave';
    else if (t < stop) { so.gesture = (Math.floor((t - start) / gap) % 2) ? 'point' : 'pointUp'; so.eyes = 'happy'; }
    if (t > ev.a3 && t < ev.s3) { so.eyes = 'wide'; so.brows = 'up'; }
    if (t > ev.s3) { so.gesture = 'shrug'; so.brows = 'up'; }
    if (t > ev.a4 + 1) so.gesture = 'think';
    K.actor(ctx, TP.CAST.sam, SAM_X, 930, 0.74, t, so);
    // Ada
    const ao = { role: 'ada', look: -0.5, seed: 1 };
    if (t < ev.a1) ao.gesture = 'wave';
    else if (t < ev.a2) { ao.gesture = 'shrug'; ao.eyes = 'wide'; ao.brows = 'up'; }
    else if (t < ev.a3) { ao.gesture = 'facepalm'; }
    else if (t < ev.s3) { ao.gesture = 'pointUp'; ao.brows = 'up'; ao.eyes = 'wide'; }
    else if (t > ev.a4) { ao.gesture = 'thumbsUp'; ao.eyes = 'happy'; }
    K.actor(ctx, TP.CAST.ada, ADA_X, 930, 0.74, t, ao);
    // signs
    TP.sign(K, ctx, t, ev.a1 + 0.6, ev.a2, 1330, 520, 'unpacking... slowly', { size: 46, seed: 3 });
    TP.sign(K, ctx, t, ev.a2 + 1.2, ev.a3, 1180, 560, 'dropped: send again!', { size: 46, color: TP.RED, rot: -0.03, seed: 4 });
    TP.sign(K, ctx, t, ev.a3 + 1.4, ev.s3 + 1.5, 1300, 420, 'WINDOW = 0', { size: 80, h: 140, color: TP.RED, rot: 0.03, seed: 5 });
    TP.sign(K, ctx, t, ev.s3 + 2.0, ev.outro, 560, 420, 'when do I restart?', { size: 50, color: TP.BLUE, rot: -0.02, seed: 6 });
  }
  function outro(ctx, t) {
    TP.room(ctx, { wall: '#EAF2F8', stripe: '#D6E6F2' });
    TP.episodeTitle(K, ctx, t, ev.outro, 2, 'TCP up close', 'handshakes, windows and Nagle');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => scene(ctx, t), cam: (s) => ({ zoom: 1 + 0.05 * ease.inOutQuad(s.u) }) },
    { at: S.cuts.outro, draw: (ctx, t) => outro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]), post: { paper: 0.35, vignette: 0.2, grain: 0.04 }, fadeOut: 0.6 });
})();
