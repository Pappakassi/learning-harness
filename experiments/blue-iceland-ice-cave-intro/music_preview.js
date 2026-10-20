// Three cheerful background-music ideas, 20 s each, as previews: node music_preview.js
// -> out/preview-A-ukulele.wav, out/preview-B-folkpop.wav, out/preview-C-pentatonic.wav
const path = require('path');
const { SR, Bus, reverb } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const { m } = require('./engine/music');

const LEN = 20;
const N = Math.ceil(LEN * SR);
const out = (name, stems, gains) => {
  const mix = MIX.mixdown(stems, gains, { stemDir: null });
  MIX.highpass(mix, 30); MIX.fadeOut(mix, LEN - 1.5, LEN);
  const M = MIX.master(mix, 0.8, undefined, { lufs: -16 });
  MIX.writeWav(path.join(__dirname, 'out', name), mix);
  console.log(`${name}  ${M.lufs.toFixed(1)} LUFS`);
};
const chordNotes = { C: ['C4', 'E4', 'G4'], G: ['B3', 'D4', 'G4'], Am: ['C4', 'E4', 'A4'], F: ['C4', 'F4', 'A4'], D: ['D4', 'F#4', 'A4'], Em: ['E4', 'G4', 'B4'], Bm: ['D4', 'F#4', 'B4'] };
const bassOf = { C: 'C2', G: 'G1', Am: 'A1', F: 'F1', D: 'D2', Em: 'E2', Bm: 'B1' };

// A · ukulele + glockenspiel, 116 bpm: bright strums, a music-box tune, shaker and claps (classic explainer)
{
  const b = 60 / 116, bar = 4 * b;
  const uke = new Bus(N), glock = new Bus(N), perc = new Bus(N), low = new Bus(N), verb = new Bus(N);
  const prog = ['C', 'G', 'Am', 'F'];
  const tune = ['E6', 'G6', 'A6', 'G6', 'E6', 'D6', 'C6', 'D6', 'E6', 'E6', 'D6', 'C6', 'A5', 'C6', 'D6', 'C6'];
  for (let i = 0, t = 0; t < LEN; i++, t = i * bar) {
    const ch = prog[i % 4];
    [0, 1, 1.5, 2.5, 3, 3.5].forEach((beat, k) => chordNotes[ch].forEach((n, j) => uke.addMono(I.pluck(m(n) + 12, { decay: 0.18, seed: i * 10 + k }), t + beat * b + j * 0.012, k % 2 ? 0.09 : 0.13, -0.25)));
    low.addMono(I.bass(m(bassOf[ch]), bar * 0.9, { bright: 0.4 }), t, 0.32);
    for (let k = 0; k < 8; k++) perc.addMono(I.shaker(k % 2 ? 0.6 : 1, i * 8 + k), t + k * b / 2, 0.1, 0.3);
    [1, 3].forEach((beat) => perc.addMono(I.clap({ seed: i + beat }), t + beat * b, 0.22));
    if (i >= 2) for (let k = 0; k < 4; k++) { const n = tune[((i - 2) * 4 + k) % tune.length]; const g = I.musicBox(m(n), { decay: 0.9 }); glock.addMono(g, t + k * b, 0.14, 0.2); verb.addMono(g, t + k * b, 0.08); }
  }
  out('preview-A-ukulele.wav', { uke, glock, perc, low, verb: reverb(verb, { room: 0.6, damp: 0.5 }) }, { uke: 1, glock: 1, perc: 1, low: 1, verb: 1 });
}

// B · Nordic folk-pop, 124 bpm: acoustic guitar, stomp + clap, a whistled hook (think travel-vlog cheerful)
{
  const b = 60 / 124, bar = 4 * b;
  const gtr = new Bus(N), drums = new Bus(N), lead = new Bus(N), low = new Bus(N), verb = new Bus(N);
  const prog = ['D', 'Bm', 'G', 'A'];
  chordNotes.A = ['C#4', 'E4', 'A4'];
  bassOf.A = 'A1';
  const hook = [['F#5', 0, 1], ['A5', 1, 1], ['B5', 2, 0.5], ['A5', 2.5, 0.5], ['F#5', 3, 1], ['E5', 4, 1], ['D5', 5, 1], ['E5', 6, 2]];
  for (let i = 0, t = 0; t < LEN; i++, t = i * bar) {
    const ch = prog[i % 4];
    [0, 1, 1.5, 2, 3, 3.5].forEach((beat, k) => chordNotes[ch].forEach((n, j) => gtr.addMono(I.guitar(m(n), 0.5, { bright: 0.6, seed: i * 9 + k + j }), t + beat * b + j * 0.01, 0.11, 0.2)));
    low.addMono(I.bass(m(bassOf[ch]), bar * 0.9, { bright: 0.5 }), t, 0.3);
    [0, 2].forEach((beat) => drums.addMono(I.kick({ punch: 0.8, tail: 0.25 }), t + beat * b, 0.55));
    [1, 3].forEach((beat) => drums.addMono(I.clap({ seed: i * 3 + beat }), t + beat * b, 0.3));
    if (i >= 2 && i % 2 === 0) for (const [n, at, d] of hook) { const x = I.strings(m(n), d * b * 0.9, { attack: 0.03, release: 0.12, bright: 1.4 }); lead.addMono(x.L || x, t + at * b, 0.12); verb.addMono(x.L || x, t + at * b, 0.06); }
  }
  out('preview-B-folkpop.wav', { gtr, drums, lead, low, verb: reverb(verb, { room: 0.7, damp: 0.4 }) }, { gtr: 1, drums: 1, lead: 1, low: 1, verb: 1 });
}

// C · pentatonic bounce, 108 bpm: plucked "zither" melody on the Chinese pentatonic scale, marimba, wood blocks
{
  const b = 60 / 108, bar = 4 * b;
  const zither = new Bus(N), mar = new Bus(N), perc = new Bus(N), low = new Bus(N), verb = new Bus(N);
  const scale = ['C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'D6'];
  const mel = [2, 3, 4, 3, 2, 1, 0, 1, 2, 4, 5, 4, 3, 2, 3, 2, 4, 5, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 0];
  const prog = ['C', 'Am', 'F', 'G'];
  for (let i = 0, t = 0; t < LEN; i++, t = i * bar) {
    const ch = prog[i % 4];
    for (let k = 0; k < 8; k++) { // marimba arpeggio in eighths
      const n = chordNotes[ch][k % 3];
      mar.addMono(I.marimba(m(n), { decay: 0.3, seed: i * 8 + k }), t + k * b / 2, 0.16, -0.2);
    }
    low.addMono(I.bass(m(bassOf[ch]), bar * 0.9, { bright: 0.35 }), t, 0.3);
    for (let k = 0; k < 4; k++) perc.addMono(I.woodTick(k % 2 ? 1.8 : 1.4), t + k * b + (k % 2 ? b / 2 : 0), 0.18, k % 2 ? 0.3 : -0.3);
    if (i >= 1) for (let k = 0; k < 8; k++) {
      const n = scale[mel[((i - 1) * 8 + k) % mel.length]];
      const z = I.pluck(m(n), { decay: 0.32, cutoff: 4200, seed: i * 31 + k });
      zither.addMono(z, t + k * b / 2, 0.2, 0.15); verb.addMono(z, t + k * b / 2, 0.1);
      if (k % 4 === 3) zither.addMono(I.pluck(m(n) + 12, { decay: 0.2, seed: k }), t + k * b / 2 + 0.06, 0.07, 0.2); // a little grace note
    }
  }
  out('preview-C-pentatonic.wav', { zither, mar, perc, low, verb: reverb(verb, { room: 0.75, damp: 0.35 }) }, { zither: 1, mar: 1, perc: 1, low: 1, verb: 1 });
}
