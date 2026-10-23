// Hr. Schiffel's theme: a bouncy gnome polka, synthesized with the animation-studio audio engine.
//
//   node music/gnome_theme.js [outdir]      -> theme_intro.wav (sung, ~16 s), bed.wav (16 s loop), outro.wav (~6 s)
//
// Instruments: tuba-ish brass on the beat ("oom"), harmonium chords off the beat ("pah"),
// marimba + music box melody, wood ticks and a triangle. The intro has a sung chorus (formant tenor).
// Set ANIMATION_STUDIO to the animation-studio skill folder if the engine isn't found automatically.
const fs = require('fs');
const path = require('path');

function findEngine() {
  const env = process.env.ANIMATION_STUDIO;
  if (env && fs.existsSync(path.join(env, 'engine', 'audio', 'instruments.js'))) return path.join(env, 'engine');
  const roots = [path.join(process.env.HOME || '/root', '.claude', 'plugins'), path.join(process.env.HOME || '/root', '.claude', 'skills')];
  const stack = roots.filter((r) => fs.existsSync(r));
  while (stack.length) {
    const d = stack.pop();
    let ents = [];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch (e) { continue; }
    for (const e of ents) {
      if (!e.isDirectory()) continue;
      const p = path.join(d, e.name);
      if (e.name === 'engine' && fs.existsSync(path.join(p, 'audio', 'instruments.js')) && p.includes('animation-studio')) return p;
      if (e.name !== 'node_modules') stack.push(p);
    }
  }
  throw new Error('animation-studio engine not found: set ANIMATION_STUDIO');
}
const ENG = findEngine();
const { SR, Bus, reverb } = require(path.join(ENG, 'audio', 'dsp'));
const I = require(path.join(ENG, 'audio', 'instruments'));
const MIX = require(path.join(ENG, 'audio', 'mix'));
const Sing = require(path.join(ENG, 'audio', 'sing'));
const { m } = require(path.join(ENG, 'music'));

const OUT = process.argv[2] || path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });

const BPM = 120, B = 60 / BPM, BAR = 2 * B;          // 2/4 polka: one bar = 1 s
const CHORDS = { G: ['G3', 'B3', 'D4'], C: ['G3', 'C4', 'E4'], D: ['F#3', 'A3', 'D4'], Em: ['G3', 'B3', 'E4'] };
const ROOT = { G: ['G2', 'D2'], C: ['C2', 'G2'], D: ['D2', 'A2'], Em: ['E2', 'B2'] };
const PROG = ['G', 'G', 'D', 'D', 'G', 'C', 'D', 'G'];
// melody in eighths per bar ([note, eighths]); '-' rests
const MEL = [
  [['D5', 1], ['B4', 1], ['G4', 1], ['B4', 1]], [['D5', 2], ['G5', 2]],
  [['F#5', 1], ['E5', 1], ['D5', 1], ['C5', 1]], [['A4', 4]],
  [['B4', 1], ['C5', 1], ['D5', 1], ['B4', 1]], [['E5', 2], ['C5', 2]],
  [['A4', 1], ['B4', 1], ['C5', 1], ['A4', 1]], [['G4', 4]],
];
// sung chorus: Herr Schiffel, Herr Schiffel, he knows where the bits go, byte by byte and hop by hop, through the net-work, oh!
const LYRIC = [
  [['hair', 'D5', 2], ['shif', 'B4', 1], ['fel', 'G4', 1]], [['hair', 'D5', 2], ['shif', 'G5', 1], ['fel', 'D5', 1]],
  [['hee', 'F#5', 1], ['nohz', 'E5', 1], ['wair', 'D5', 1], ['thuh', 'C5', 1]], [['bits', 'A4', 2], ['goh', 'D5', 2]],
  [['bait', 'B4', 1], ['bai', 'C5', 1], ['bait', 'D5', 1], ['and', 'B4', 1]], [['hop', 'E5', 1], ['bai', 'D5', 1], ['hop', 'C5', 2]],
  [['throo', 'A4', 1], ['thuh', 'B4', 1], ['net', 'C5', 1], ['werk', 'A4', 1]], [['oh', 'G4', 4]],
];

function band(bars, { start = 0, melody = true, sing = false, soft = false, tag = false } = {}) {
  const len = bars * BAR + 3;
  const N = Math.ceil(len * SR);
  const oom = new Bus(N), pah = new Bus(N), lead = new Bus(N), perc = new Bus(N), voice = new Bus(N), verb = new Bus(N);
  for (let b = 0; b < bars; b++) {
    const t0 = start + b * BAR, ch = PROG[b % 8];
    // oom: root on beat 1, fifth on beat 2 (tuba-ish brass, plus a soft bass under it)
    ROOT[ch].forEach((n, k) => {
      oom.addMono(I.brassNote(m(n), B * 0.55, { bright: 0.45, stab: true, seed: 3 + k }).L || I.bass(m(n), B * 0.6), t0 + k * B, soft ? 0.35 : 0.5);
      oom.addMono(I.bass(m(n), B * 0.5, { bright: 0.3, sub: 0.8 }), t0 + k * B, soft ? 0.3 : 0.4);
    });
    // pah: harmonium chord on the off-beats
    for (const k of [0.5, 1.5]) for (const n of CHORDS[ch]) {
      const h = I.harmonium(m(n) + 12, B * 0.32, { attack: 0.01, release: 0.08, bright: 0.7, seed: 7 });
      pah.addStereo(h.L, h.R, t0 + k * B, soft ? 0.18 : 0.26);
    }
    // percussion: wood tick off-beats, triangle on bar starts every 4 bars
    for (const k of [0.5, 1.5]) perc.addMono(I.woodTick(1.0 + (b % 2) * 0.1), t0 + k * B, soft ? 0.12 : 0.2);
    if (b % 4 === 0) perc.addMono(I.triangle ? I.bell(m('G6'), 0.6) : I.woodTick(2), t0, 0.05);
    // melody
    if (melody) {
      let t = t0;
      for (const [n, e] of MEL[b % 8]) {
        const mb = I.marimba(m(n), { decay: 0.35 + 0.1 * e });
        lead.addMono(mb, t, soft ? 0.28 : 0.42, -0.15);
        if (!soft && e >= 2) { const bx = I.musicBox(m(n) + 12); lead.addMono(bx, t, 0.07, 0.25); verb.addMono(bx, t, 0.08); }
        t += e * B / 2;
      }
    }
  }
  if (sing) {
    const notes = [];
    LYRIC.forEach((bar, b) => {
      let t = (sing.at - start) + b * BAR;
      for (const [syl, n, e] of bar) { notes.push({ t, dur: e * B / 2 * 0.92, midi: m(n), syl }); t += e * B / 2; }
    });
    const v = Sing.phrase(notes, { type: 'tenor', vib: 0.3, bright: 1.1, seed: 4 });
    voice.addMono(v, start + 0.0 - 0.09 + (sing.at - start), 0.9);
    // a second, higher voice a third above for the gnome choir feel
    const v2 = Sing.phrase(notes.map((x) => ({ ...x, midi: x.midi + 4 })), { type: 'alto', vib: 0.25, seed: 9 });
    voice.addMono(v2, start - 0.09 + (sing.at - start), 0.28, 0.3);
    verb.addMono(v, start - 0.09 + (sing.at - start), 0.15);
  }
  if (tag) { // ta-da: final chord + triangle-ish bell
    const t = start + bars * BAR;
    for (const n of ['G3', 'B3', 'D4', 'G4']) { const h = I.harmonium(m(n) + 12, 0.9, { bright: 0.8 }); pah.addStereo(h.L, h.R, t, 0.25); }
    oom.addMono(I.bass(m('G2'), 0.9, { bright: 0.4 }), t, 0.5);
    lead.addMono(I.marimba(m('G5'), { decay: 0.9 }), t, 0.5);
    perc.addMono(I.bell(m('G6'), 1.2), t, 0.08); verb.addMono(I.bell(m('D7'), 1.2), t, 0.06);
  }
  const stems = { oom, pah, lead, perc, voice, verb: reverb(verb, { room: 0.7, damp: 0.4 }) };
  const mix = MIX.mixdown(stems, { oom: 1, pah: 1, lead: 1, perc: 1, voice: 1, verb: 1 }, { stemDir: null });
  MIX.highpass(mix, 35);
  return mix;
}

function trim(mix, secs) { // keep the first secs seconds, short fade at the end
  const n = Math.min(mix.n, Math.ceil(secs * SR));
  const out = new Bus(n);
  out.L.set(mix.L.subarray(0, n)); out.R.set(mix.R.subarray(0, n));
  MIX.fadeOut(out, secs - 0.4, secs);
  return out;
}

// intro: 4 bars instrumental, 8 bars sung chorus, 2 bars tag + ta-da
const intro = band(14, { sing: { at: 4 * BAR }, tag: true });
MIX.master(intro, 0.8, undefined, { lufs: -16 });
MIX.writeWav(path.join(OUT, 'theme_intro.wav'), trim(intro, 14 * BAR + 1.6));
// bed: 16 bars, soft, no singing, loops (ends on the tonic)
const bed = band(16, { soft: true });
MIX.master(bed, 0.8, undefined, { lufs: -18 });
MIX.writeWav(path.join(OUT, 'bed.wav'), trim(bed, 16 * BAR));
// outro: last 4 bars + ta-da
const outro = band(4, { start: 0, tag: true });
MIX.master(outro, 0.8, undefined, { lufs: -16 });
MIX.writeWav(path.join(OUT, 'outro.wav'), trim(outro, 4 * BAR + 1.6));
console.log(`wrote theme_intro.wav, bed.wav, outro.wav to ${OUT}`);
