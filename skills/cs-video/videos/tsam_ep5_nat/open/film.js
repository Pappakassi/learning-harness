// TSAM #5 cold open: Ada can't reach Sam's game server; his NAT router only lets replies in.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots, TP = globalThis.TP;
  const { ev, sent } = S;
  const { clamp, lerp, ease } = U;
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: TP.HAND, roles: TP.ROLES });
  globalThis.CAST = TP.CAST;
  const R = [900, 470], CLOUD = [1240, 190], SAM_LAP = [520, 760], ADA_LAP = [1460, 760];

  function cloud(ctx, x, y) {
    for (const [dx, dy, r] of [[-110, 10, 70], [-40, -30, 85], [50, -20, 80], [120, 15, 65], [0, 30, 80]]) G.ellipse(ctx, x + dx, y + dy, r, r * 0.8, { fill: '#FFFFFF', lw: 0, seed: 70 + dx });
    G.text(ctx, 'Internet', x, y + 20, { size: 46, fam: TP.HAND, color: TP.BLUE, align: 'center', boil: 0 });
  }
  // a packet going along a list of points between t0 and t0+dur
  function along(ctx, t, t0, dur, pts, color, label) {
    if (t < t0 || t > t0 + dur) return null;
    const u = (t - t0) / dur * (pts.length - 1), i = Math.min(Math.floor(u), pts.length - 2), f = u - i;
    const x = lerp(pts[i][0], pts[i + 1][0], f), y = lerp(pts[i][1], pts[i + 1][1], f);
    G.rrect(ctx, x - 66, y - 28, 132, 56, 10, { fill: color, lw: 3.5, seed: 81 });
    if (label) G.text(ctx, label, x, y + 12, { size: 36, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 });
    return [x, y];
  }
  function scene(ctx, t) {
    // two rooms: Sam's (left) and Ada's (right), the Internet between them
    ctx.fillStyle = '#E8F1E4'; ctx.fillRect(-300, -300, 1400, 1700);
    ctx.fillStyle = '#F4E7EF'; ctx.fillRect(1100, -300, 1400, 1700);
    G.line(ctx, [[1100, -50], [1100, 860]], { lw: 8, seed: 3 });
    G.poly(ctx, [[-300, 860], [2300, 850], [2300, 1400], [-300, 1400]], { fill: '#B98E62', lw: 4, seed: 11, step: 60 });
    cloud(ctx, CLOUD[0], CLOUD[1]);
    G.text(ctx, "Sam's home", 300, 120, { size: 44, fam: TP.HAND, color: TP.GREEN, align: 'center', boil: 0 });
    G.text(ctx, "Ada's place", 1700, 120, { size: 44, fam: TP.HAND, color: TP.PINK, align: 'center', boil: 0 });
    // cables
    G.line(ctx, [[SAM_LAP[0], SAM_LAP[1] - 180], [R[0] - 60, R[1] + 30]], { lw: 5, color: '#4A4F5A', seed: 12 });
    G.line(ctx, [[R[0] + 60, R[1] - 30], [CLOUD[0] - 120, CLOUD[1] + 50]], { lw: 5, color: '#4A4F5A', seed: 13 });
    G.line(ctx, [[CLOUD[0] + 120, CLOUD[1] + 50], [ADA_LAP[0], ADA_LAP[1] - 180]], { lw: 5, color: '#4A4F5A', seed: 14 });
    // Ada's knocks bounce off the router; Sam's own requests go out and replies come in
    const knocks = [ev.hook + 0.8, ev.hook + 3.2, ev.a3 + 0.6];
    let bounced = false;
    for (const k of knocks) {
      const p = along(ctx, t, k, 1.6, [[ADA_LAP[0], ADA_LAP[1] - 190], [CLOUD[0] + 60, CLOUD[1] + 40], [R[0] + 70, R[1] - 20]], '#F7B6C8', 'join?');
      if (t > k + 1.6 && t < k + 2.4) { bounced = true; const u = (t - k - 1.6) / 0.8; G.text(ctx, '✕', R[0] + 110, R[1] - 60 - u * 30, { size: 80, color: TP.RED, align: 'center', alpha: 1 - u, boil: 0 }); }
    }
    const asks = [ev.s2 + 0.3, ev.a3 + 2.6];
    for (const k of asks) {
      along(ctx, t, k, 1.4, [[SAM_LAP[0], SAM_LAP[1] - 190], [R[0], R[1]], [CLOUD[0] - 60, CLOUD[1] + 40]], '#BDE6C3', 'GET');
      along(ctx, t, k + 1.6, 1.4, [[CLOUD[0] - 60, CLOUD[1] + 40], [R[0], R[1]], [SAM_LAP[0], SAM_LAP[1] - 190]], '#9FD9AA', 'reply');
    }
    TP.router(ctx, R[0], R[1], 0.85, t, bounced ? 'angry' : 'calm', { seed: 6 });
    G.rrect(ctx, R[0] - 140, R[1] + 46, 280, 18, 5, { fill: '#9C6B43', lw: 4, seed: 15 });
    // desks and laptops
    TP.desk(ctx, SAM_LAP[0], 360); TP.desk(ctx, ADA_LAP[0], 360);
    TP.laptop(ctx, SAM_LAP[0], SAM_LAP[1], 0.85, (c) => { G.text(c, 'game server', 0, -8, { size: 26, fam: TP.HAND, color: TP.GREEN, align: 'center', boil: 0 }); G.text(c, '192.168.1.30', 0, 26, { size: 24, fam: TP.HAND, color: TP.INK, align: 'center', boil: 0 }); }, { seed: 31 });
    TP.laptop(ctx, ADA_LAP[0], ADA_LAP[1], 0.85, (c) => { G.text(c, 'connecting...', 0, 0, { size: 26, fam: TP.HAND, color: t > ev.hook + 2 ? TP.RED : TP.INK, align: 'center', boil: 0 }); }, { seed: 41 });
    // Sam
    const so = { role: 'sam', look: 0.4, seed: 2 };
    if (t > ev.s1 && t < ev.a2) so.gesture = 'point';
    if (t > ev.a2 && t < ev.s2) { so.eyes = 'wide'; so.brows = 'up'; }
    if (t > ev.s2 && t < ev.a3) so.gesture = 'shrug';
    if (t > ev.s3) so.gesture = 'think';
    K.actor(ctx, TP.CAST.sam, 260, 930, 0.72, t, so);
    // Ada on the phone
    const ao = { role: 'ada', look: -0.5, seed: 1, gesture: 'phone' };
    if (t > ev.a4) { ao.gesture = 'pointUp'; ao.eyes = 'happy'; }
    K.actor(ctx, TP.CAST.ada, 1730, 930, 0.72, t, ao);
    // signs
    TP.sign(K, ctx, t, ev.hook + 2.2, ev.s1, 1240, 420, 'timed out', { size: 54, color: TP.RED, seed: 3 });
    TP.sign(K, ctx, t, ev.a2 + 0.8, ev.s2, 520, 400, 'private address!', { size: 52, color: TP.PURPLE, rot: -0.03, seed: 4 });
    TP.sign(K, ctx, t, sent('a3', 1), ev.s3 + 0.6, 900, 250, 'replies only', { size: 52, color: TP.GREEN, rot: 0.02, seed: 5 });
  }
  function outro(ctx, t) {
    TP.room(ctx, { wall: '#E8F1E4', stripe: '#D7E6D1' });
    TP.episodeTitle(K, ctx, t, ev.outro, 5, 'Home networks', 'NAT, port forwarding and WiFi');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => scene(ctx, t), cam: (s) => ({ zoom: 1 + 0.03 * ease.inOutQuad(s.u) }) },
    { at: S.cuts.outro, draw: (ctx, t) => outro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]), post: { paper: 0.35, vignette: 0.2, grain: 0.04 }, fadeOut: 0.6 });
})();
