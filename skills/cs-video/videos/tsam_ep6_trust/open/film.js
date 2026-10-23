// TSAM #6 cold open: Sam passes a secret note to Ada; it goes through Mallory, who reads and edits it.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Shots = globalThis.Shots, TP = globalThis.TP;
  const { ev, sent } = S;
  const { clamp, lerp, ease } = U;
  const K = Kit.init({ main: 'Inter, sans-serif', mainWeight: 600, cardFont: TP.HAND, roles: TP.ROLES });
  globalThis.CAST = TP.CAST;
  const SAM = 380, MAL = 960, ADA = 1540;

  function board(ctx) {
    G.rrect(ctx, 560, 110, 800, 330, 12, { fill: '#2F4A3A', lw: 7, seed: 21 });
    G.text(ctx, 'TSAM: lecture 1', 960, 210, { size: 56, fam: TP.HAND, color: '#EDEFE6', align: 'center', boil: 0 });
    G.line(ctx, [[700, 280], [900, 280], [930, 340], [1220, 340]], { lw: 4, color: '#EDEFE6', seed: 22 });
    G.text(ctx, 'A  →  ?  →  B', 960, 400, { size: 48, fam: TP.HAND, color: '#F2D27A', align: 'center', boil: 0 });
  }
  function scene(ctx, t) {
    TP.room(ctx, { wall: '#EEF0E6', stripe: '#DDE2D0' });
    board(ctx);
    // the note's journey
    const t0 = ev.hook + 2.8, t1 = sent('a1', 0) + 0.2;
    let note = null, text = 'pw: hunter2', rot = 0;
    if (t > t0 && t < t0 + 1.0) { const f = TP.fly(t, t0, 1.0, [SAM + 110, 640], [MAL - 40, 620], 130); note = [f.x, f.y]; rot = f.rot * 0.2; }
    else if (t >= t0 + 1.0 && t < t1) { note = [MAL + 40, 540 + Math.sin(t * 2) * 6]; if (t > sent('m1', 1) + 0.6) text = 'pw: m4ll0ry'; }
    else if (t >= t1 && t < t1 + 1.0) { const f = TP.fly(t, t1, 1.0, [MAL + 40, 620], [ADA - 110, 640], 130); note = [f.x, f.y]; rot = f.rot * 0.2; text = 'pw: m4ll0ry'; }
    else if (t >= t1 + 1.0) { note = [ADA - 110, 640]; text = 'pw: m4ll0ry'; }
    // desks and people
    for (const x of [SAM, MAL, ADA]) TP.schoolDesk(ctx, x);
    const so = { role: 'sam', look: 0.6, seed: 2 };
    if (t < t0) so.gesture = 'point';
    if (t > ev.m1 && t < ev.a1) { so.eyes = 'wide'; so.brows = 'up'; }
    if (t > ev.a1 && t < ev.s2) so.gesture = 'facepalm';
    if (t > ev.s2 && t < ev.a2) so.gesture = 'pointUp';
    if (t > ev.a2) so.gesture = 'think';
    K.actor(ctx, TP.CAST.sam, SAM, 930, 0.72, t, so);
    const mo = { role: 'mallory', look: 0, seed: 3, mouth: 'smirk' };
    if (t > t0 + 1.0 && t < t1) { mo.gesture = 'phone'; mo.look = 0.3; mo.lookY = -0.3; }
    if (t > ev.m2 && t < ev.a3) { mo.gesture = 'clap'; mo.eyes = 'happy'; }
    K.actor(ctx, TP.CAST.mallory, MAL, 930, 0.72, t, mo);
    const ao = { role: 'ada', look: -0.6, seed: 1 };
    if (t > ev.a1 && t < ev.s2) { ao.gesture = 'point'; ao.look = -0.9; ao.brows = 'up'; }
    if (t > ev.a2 && t < ev.m2) ao.gesture = 'shrug';
    if (t > ev.a3) { ao.gesture = 'pointUp'; ao.eyes = 'happy'; }
    K.actor(ctx, TP.CAST.ada, ADA, 930, 0.72, t, ao);
    if (note) TP.note(ctx, note[0], note[1], 1.6, rot, { text, seed: 81 });
    // signs
    TP.sign(K, ctx, t, ev.m1 + 1.0, ev.a1, MAL, 360, 'reading... and editing', { size: 46, color: TP.PURPLE, rot: -0.03, seed: 3 });
    TP.sign(K, ctx, t, sent('a1', 1), ev.s2, 960, 90, 'Mallory = every network in between', { size: 50, color: TP.RED, seed: 4 });
    TP.sign(K, ctx, t, sent('s2', 1), ev.a2, 380, 470, 'share the key how?', { size: 46, color: TP.BLUE, rot: 0.03, seed: 5 });
    TP.sign(K, ctx, t, ev.a2 + 0.8, ev.a3, 1540, 470, 'who really sent it?', { size: 46, color: TP.ORANGE, rot: -0.03, seed: 6 });
  }
  function outro(ctx, t) {
    TP.room(ctx, { wall: '#EEF0E6', stripe: '#DDE2D0' });
    TP.episodeTitle(K, ctx, t, ev.outro, 6, 'Trust on the Internet', 'DNS, keys, certificates and firewalls');
  }
  const film = Shots.film([
    { at: 0, draw: (ctx, t) => scene(ctx, t), cam: (s) => ({ zoom: 1 + 0.04 * ease.inOutQuad(s.u) }) },
    { at: S.cuts.outro, draw: (ctx, t) => outro(ctx, t), in: { type: 'paper', dur: 0.8 } },
  ]);
  Studio.film({ draw: (ctx, t) => K.frame(ctx, t, film, [[0, 960]]), post: { paper: 0.35, vignette: 0.2, grain: 0.04 }, fadeOut: 0.6 });
})();
