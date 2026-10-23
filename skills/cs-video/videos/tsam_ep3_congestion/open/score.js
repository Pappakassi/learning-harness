// TSAM cold open score: every line id becomes a moment ev.<id> (its start); ph/sent give phrase/sentence starts.
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
  const clock = makeClock({ bpm: 100, offset: 0 });
  const { T, BEAT } = clock;
  const L = {};
  for (const l of VO.lines) L[l.id] = l;
  const ph = (id, k) => L[id].phrases[Math.min(k, L[id].phrases.length - 1)][1];
  const sent = (id, k) => L[id].sents[Math.min(k, L[id].sents.length - 1)][1];
  const ev = {};
  for (const l of VO.lines) { ev[l.id] = l.t; ev[l.id + 'End'] = l.end; }
  const SPEECH_END = VO.lines[VO.lines.length - 1].end;
  ev.outro = SPEECH_END + 0.6;
  const DURATION = Math.ceil(SPEECH_END + 4.6);
  const cuts = { outro: ev.outro };
  const { chords } = makeChords(clock, {
    Cmaj9: { notes: ['E3', 'G3', 'B3', 'D4'], bass: 'C2' }, Am7: { notes: ['G3', 'C4', 'E4'], bass: 'A1' },
    Fmaj7: { notes: ['A3', 'C4', 'E4'], bass: 'F1' }, G6: { notes: ['G3', 'B3', 'E4'], bass: 'G1' },
  }, Array.from({ length: Math.ceil(DURATION / 2.4 / 4) * 4 + 4 }, (_, i) => [i, 0, 4, ['Cmaj9', 'Am7', 'Fmaj7', 'G6'][Math.floor(i / 2) % 4]]));
  const markers = Object.assign({}, ...VO.lines.map((l) => ({ [l.id]: l.t })), { outro: ev.outro });
  const SCORE = { FPS, FORMAT, W, H, SAFE, DURATION, clock, T, BEAT, m, chords, ev, cuts, markers, VO, L, ph, sent };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
