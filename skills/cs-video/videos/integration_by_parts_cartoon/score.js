// THE SCORE: every time comes from the dialogue (vo.js), so the board writing, the call stack,
// lip-sync and sounds all share one clock.
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const VO = node ? require('./vo') : globalThis.VO;
  const { m, makeClock, makeChords } = MU;

  const FPS = 30;
  const FORMAT = U.pickFormat('16:9');
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const clock = makeClock({ bpm: 92, offset: 0 });
  const { T, BEAT } = clock;
  const L = {};
  for (const l of VO.lines) L[l.id] = l;
  const ph = (id, k) => L[id].phrases[k][1];
  const sent = (id, k) => L[id].sents[k][1];

  const ev = {
    hook: L.hook.t, problem: L.hook.t + 0.3,
    plan: L.plan.t, formula: sent('plan', 1),
    pickf: ph('pickf', 1), pickg: ph('pickf', 2),
    r1: L.r1.t, r1a: L.r1.t + 0.1, r1b: ph('r1', 1), r1c: ph('r1', 3), r1d: ph('r1', 5),
    still: L.still.t, smaller: ph('smaller', 2), recursive: ph('smaller', 4),
    r2: L.r2.t, r2a: ph('r2', 1), r2b: ph('r2', 2) + 0.4, r2c: ph('r2', 3),
    r3: L.r3.t, r3a: ph('r3', 1), r3b: ph('r3', 2) + 0.4, r3c: ph('r3', 3), r3d: ph('r3', 4),
    base: L.base.t,
    unwind: L.unwind.t, pop3: ph('unwind', 1), u2a: ph('unwind', 3), u2b: ph('unwind', 4), pop2: ph('unwind', 5), u1a: ph('unwind', 5) + 0.3, u1b: ph('unwind', 6),
    final: L.final.t, finalW: L.final.t + 0.2, pop1: L.final.t, box: ph('final', 3),
    yourturn: L.yourturn.t, pause0: L.yourturn.end, pause1: L.check.t,
    check: L.check.t, c1: L.check.t + 0.3, c2: ph('check', 1), ok: ph('check', 2),
    wow: L.wow.t, teaser: ph('teaser', 2),
  };
  const SPEECH_END = VO.lines[VO.lines.length - 1].end;
  ev.outro = SPEECH_END + 0.8;
  const DURATION = Math.ceil(SPEECH_END + 5.5);
  // board pages: [id, start]
  const pages = [['intro', 0], ['r1', ev.r1 - 0.4], ['r2', ev.r2 - 0.4], ['r3', ev.r3 - 0.4], ['unwind', ev.unwind - 0.3], ['final', ev.final - 0.3], ['check', ev.check - 0.3]];
  const cuts = { board: 0, outro: ev.outro };

  const { chords } = makeChords(clock, {
    Cmaj9: { notes: ['E3', 'G3', 'B3', 'D4'], bass: 'C2' }, Am7: { notes: ['G3', 'C4', 'E4'], bass: 'A1' },
    Fmaj7: { notes: ['A3', 'C4', 'E4'], bass: 'F1' }, G6: { notes: ['G3', 'B3', 'E4'], bass: 'G1' },
  }, Array.from({ length: Math.ceil(DURATION / 2.6 / 4) * 4 + 4 }, (_, i) => [i, 0, 4, ['Cmaj9', 'Am7', 'Fmaj7', 'G6'][Math.floor(i / 2) % 4]]));

  const markers = { hook: ev.hook, formula: ev.formula, r1: ev.r1, still: ev.still, r2: ev.r2, r3: ev.r3, base: ev.base, unwind: ev.unwind, final: ev.final, yourturn: ev.yourturn, check: ev.check, teaser: ev.teaser, outro: ev.outro };
  const SCORE = { FPS, FORMAT, W, H, SAFE, DURATION, clock, T, BEAT, m, chords, ev, pages, cuts, markers, VO, L };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
