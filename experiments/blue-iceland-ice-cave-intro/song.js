// THE SOUND: the Mandarin dialogue (out/narration.wav from narration.py) over a light pad,
// wind, an engine rumble in the drive, pops for each sign, crunchy footsteps on the moraine,
// a low buzz for the helmet rule and a music-box phrase at the end.
const path = require('path');
const { SR, Bus, reverb } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { DURATION, m, ev } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const pad = bus(), fx = bus(), steps = bus(), verb = bus();
const voice = MIX.loadAudio(path.join(__dirname, 'out', 'narration.wav'), { at: 0, gain: 1.0, length: DURATION });

// soft pad
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  const dur = Math.min(c.t1, DURATION) - c.t0;
  for (const n of c.notes) { const { L, R } = I.padNote(n + 12, dur, { cutoff: 1000, attack: 1.0, release: 1.4 }); pad.addStereo(L, R, c.t0, 0.045); }
}
// a gentle music-box line over the first chords of each scene
const motif = [m('E6'), m('G6'), m('A6'), m('G6'), m('E6'), m('D6')];
for (const t0 of [0.3, ev.gear + 0.6, ev.ready + 0.6]) motif.forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, t0 + i * 0.32, 0.06); verb.addMono(b, t0 + i * 0.32, 0.07); });
// wind outside, quieter in the cave
fx.addMono(I.noiseSweep(ev.cave, 380, 520, { q: 0.4, pink: true }), 0, 0.045);
fx.addMono(I.noiseSweep(DURATION - ev.ready, 380, 520, { q: 0.4, pink: true, seed: 5 }), ev.ready, 0.045);
// the Unimog: a low rumble through the drive (and when it drives off), louder on the bumpy part
fx.addMono(I.noiseSweep(ev.gear - ev.drive + 0.4, 70, 110, { q: 2, pink: true, seed: 9 }), ev.drive, 0.35);
for (let t = ev.bumpy; t < ev.gear - 0.3; t += 0.43) fx.addMono(I.thud(70 + (Math.round(t * 10) % 3) * 8, 0.1), t, 0.25);
fx.addMono(I.noiseSweep(DURATION - ev.outro, 70, 140, { q: 2, pink: true, seed: 11 }), ev.outro + 0.6, 0.3);
// transitions
for (const t of [ev.drive, ev.gear, ev.walk, ev.ready]) fx.addMono(I.paperFwip(1, Math.round(t)), t - 0.25, 0.25);
// pops for signs and the gear landing
const pops = [ev.unimog, ev.thirty, ev.helmet - 0.2, ev.crampon - 0.2, ev.wear, ev.hold, ev.path, ev.moraine, ev.meter, ev.slow,
  ev.groups, ev.follow + 0.3, ev.stray + 0.6, ev.rule, ev.boots, ev.clothes];
pops.forEach((t, i) => fx.addMono(I.pop(1600 + (i % 4) * 250, 30 + i), t + 0.05, 0.18));
for (let i = 0; i < 4; i++) { fx.addMono(I.woodTick(1.6), ev.helmet + i * 0.22 + 0.7, 0.12); fx.addMono(I.shaker(1, 40 + i), ev.crampon + i * 0.22 + 0.7, 0.14); }
// ticks for the checklist
for (const t of [ev.wear + 0.4, ev.boots + 0.5, ev.clothes + 0.5]) { const b = I.musicBox(m('C7'), { decay: 0.8 }); fx.addMono(b, t, 0.1); }
// moraine footsteps: crunchy gravel
for (const s of sc.steps) {
  const seed = Math.round(s.t * 100);
  steps.addMono(I.shaker(0.8, seed), s.t, 0.12, s.pan);
  steps.addMono(I.thud(140 + (seed % 7) * 10, 0.04, seed), s.t, 0.12, s.pan);
}
// the kid wanders off: a little "uh-oh" whistle; the guide's "no": a low buzz
fx.addMono(I.bwomp(), ev.stray + 0.9, 0.2);
fx.addMono(I.bwomp(), ev.no + 0.05, 0.3);
// cave: a cold shimmer when we enter
[m('B5'), m('E6'), m('B6')].forEach((n, i) => { const b = I.musicBox(n, { decay: 2 }); fx.addMono(b, ev.cave + 0.5 + i * 0.18, 0.07); verb.addMono(b, ev.cave + 0.5 + i * 0.18, 0.12); });
// let's go: cheer sparkle and the closing phrase
[m('C6'), m('E6'), m('G6'), m('C7')].forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, ev.go + 0.2 + i * 0.1, 0.1); verb.addMono(b, ev.go + 0.2 + i * 0.1, 0.1); });
[m('E6'), m('G6'), m('D6'), m('C6')].forEach((n, i) => { const b = I.musicBox(n, { decay: 2 }); fx.addMono(b, ev.outro + 1 + i * 0.4, 0.1); verb.addMono(b, ev.outro + 1 + i * 0.4, 0.14); });

MIX.duck([pad, fx], voice, { depth: 0.45, attack: 0.05, release: 0.4 });
const stems = { voice, pad, fx, steps, verb: reverb(verb, { room: 0.85, damp: 0.4 }) };
const GAIN = { voice: 1.0, pad: 1.4, fx: 1.0, steps: 1.0, verb: 1.0 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 30);
MIX.fadeOut(mix, DURATION - 1.4, DURATION);
const M = MIX.master(mix, 0.8, undefined, { lufs: -16 });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s, ${M.lufs.toFixed(1)} LUFS)`);
