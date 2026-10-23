// TSAM #4 cold open: Sam checks into the network hotel; receptionist Ada (DHCP) offers room 100; Mallory runs a rogue desk.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots, TP = globalThis.TP;
  const { ev, sent } = S;
  const { clamp, lerp, ease } = U;
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: TP.HAND, roles: TP.ROLES });
  globalThis.CAST = TP.CAST;
  const DESK_X = 1240, ADA_X = 1240, SAM_END = 700;

  function keyBoard(ctx, t) {
    G.rrect(ctx, DESK_X - 300, 150, 600, 300, 12, { fill: '#8B6B4A', lw: 5, seed: 31, hatch: { color: 'rgba(0,0,0,0.12)', gap: 20, angle: 1.4 } });
    G.text(ctx, 'ROOMS', DESK_X, 200, { size: 40, fam: TP.HAND, color: '#F6E7C8', align: 'center', boil: 0 });
    const rooms = [97, 98, 99, 100, 101, 102, 103, 104];
    rooms.forEach((r, i) => {
      const x = DESK_X - 225 + (i % 4) * 150, y = 260 + Math.floor(i / 4) * 100;
      G.ellipse(ctx, x, y, 7, 7, { fill: '#D8C9A8', lw: 2, seed: 40 + i });
      const taken = r === 100 && t > ev.a2 + 0.5;
      if (!taken) TP.key(ctx, x + 6, y + 30, 0.45, String(r), Math.PI / 2 - 0.2);
      if (r === 100 && t > ev.a1 && t < ev.a2 + 0.5) G.ellipse(ctx, x, y + 40, 60, 60, { fill: 'rgba(233,183,62,0.25)', lw: 3, stroke: TP.YELLOW, seed: 49 });
    });
  }
  function scene(ctx, t) {
    TP.room(ctx, { wall: '#EFE7DA', stripe: '#E2D3BC', window: [160, 140] });
    keyBoard(ctx, t);
    // Ada behind the desk
    const ao = { role: 'ada', look: -0.6, seed: 1 };
    if (t < ev.a1) { ao.eyes = 'happy'; }
    if (t > ev.a1 && t < ev.m1) ao.gesture = 'wave';
    if (t > ev.m1 && t < ev.s2) { ao.gesture = 'akimbo'; ao.brows = 'up'; ao.look = 0.8; }
    if (t > ev.a2 && t < ev.s3) ao.gesture = 'thumbsUp';
    if (t > ev.a3) ao.gesture = 'pointUp';
    K.actor(ctx, TP.CAST.ada, ADA_X, 930, 0.76, t, ao);
    TP.reception(ctx, DESK_X, 520, 760);
    TP.bell(ctx, DESK_X + 180, 735);
    // the key flying to Sam
    const f = TP.fly(t, ev.a2 + 2.0, 0.9, [ADA_X - 120, 700], [SAM_END + 120, 650], 120);
    if (f && f.u < 1) TP.key(ctx, f.x, f.y, 0.6, '100', f.rot);
    // Sam walks in with a suitcase
    const walkU = clamp((t - 0.2) / 2.6);
    const sx = lerp(-160, SAM_END, ease.outQuad(walkU));
    TP.suitcase(ctx, sx - 110, 905, 0.9, '#C0504D');
    const so = { role: 'sam', look: 0.6, seed: 2 };
    if (walkU < 1) so.walk = t * 6;
    else if (t < ev.a1) { so.gesture = 'wave'; so.brows = 'up'; }
    if (t > ev.m1 && t < ev.s2) { so.eyes = 'wide'; so.brows = 'up'; so.look = 1; }
    if (t > ev.s2 && t < ev.a2) so.gesture = 'pointUp';
    if (t > ev.a2 + 2.9 && t < ev.s3) { so.gesture = 'cheer'; so.eyes = 'happy'; }
    if (t > ev.a2 + 2.9) TP.key(ctx, sx + 120, 650, 0.6, '100', 0.3);
    if (t > ev.s3) { so.gesture = 'think'; }
    K.actor(ctx, TP.CAST.sam, sx, 930, 0.74, t, so);
    // Mallory slides in from the right with a cardboard "desk"
    const mIn = clamp((t - ev.m1 + 0.4) / 0.6) * (1 - clamp((t - ev.s2 - 1.5) / 0.6));
    if (mIn > 0) {
      const mx = lerp(2100, 1720, ease.outBack(mIn));
      K.actor(ctx, TP.CAST.mallory, mx, 930, 0.74, t, { role: 'mallory', look: -0.8, seed: 3, gesture: 'point', mouth: 'smirk' });
      G.rrect(ctx, mx - 110, 720, 220, 150, 6, { fill: '#C9A46E', lw: 4, seed: 61 });
      G.text(ctx, 'ROOMS 4 U', mx, 810, { size: 34, fam: TP.HAND, color: TP.RED, align: 'center', boil: 0 });
    }
    // signs: the four DHCP steps
    TP.sign(K, ctx, t, sent('hook', 1), ev.a1, 960, 110, 'DISCOVER  (shouted to everyone)', { size: 50, color: TP.BLUE, seed: 3 });
    TP.sign(K, ctx, t, ev.a1 + 1.2, ev.m1, 960, 110, 'OFFER:  room 100', { size: 56, color: TP.ORANGE, seed: 4 });
    TP.sign(K, ctx, t, ev.m1 + 0.8, ev.s2, 1700, 430, 'rogue server!', { size: 50, color: TP.RED, rot: 0.04, seed: 5 });
    TP.sign(K, ctx, t, ev.s2 + 1.6, ev.a2, 960, 110, 'REQUEST:  room 100', { size: 56, color: TP.BLUE, seed: 6 });
    TP.sign(K, ctx, t, ev.a2 + 0.6, ev.s3, 960, 110, 'ACK  (lease: 24 hours)', { size: 56, color: TP.GREEN, seed: 7 });
  }
  function outro(ctx, t) {
    TP.room(ctx, { wall: '#EFE7DA', stripe: '#E2D3BC' });
    TP.episodeTitle(K, ctx, t, ev.outro, 4, 'Addresses', 'IP, subnets, MAC, ARP and DHCP');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => scene(ctx, t), cam: (s) => ({ zoom: 1 + 0.04 * ease.inOutQuad(s.u) }) },
    { at: S.cuts.outro, draw: (ctx, t) => outro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]), post: { paper: 0.35, vignette: 0.2, grain: 0.04 }, fadeOut: 0.6 });
})();
