// THE SOUND: the Mandarin dialogue (out/narration.wav from narration.py) over a soft pad
// and wind, with a crampon crunch on every footstep and a ding when the blue light lands.
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

// soft pad, a cold airy chord loop
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  const dur = Math.min(c.t1, DURATION) - c.t0;
  for (const n of c.notes) { const { L, R } = I.padNote(n + 12, dur, { cutoff: 900, attack: 1.2, release: 1.6 }); pad.addStereo(L, R, c.t0, 0.05); }
}
// wind
fx.addMono(I.noiseSweep(DURATION, 380, 520, { q: 0.4, pink: true }), 0, 0.05);
// a little sparkle when the guide waves hello
[m('E6'), m('G6'), m('C7')].forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, ev.hello + 0.3 + i * 0.12, 0.08); verb.addMono(b, ev.hello + 0.3 + i * 0.12, 0.1); });
// red light dies in the ice: a soft low thud
fx.addMono(I.thud(85, 0.12), ev.redGone, 0.35);
// blue light reaches the eye: a clear ding (the gag)
{ const b = I.musicBox(m('B6'), { decay: 1.6 }); fx.addMono(b, ev.blueEye, 0.22); verb.addMono(b, ev.blueEye, 0.25); }
// crampons on ice: a crunchy click per footstep, panned with the walker
const pan = { guide: -0.4, asker: 0, friend: 0.2, kid: 0.35 };
for (const s of sc.steps) {
  const seed = Math.round(s.t * 100);
  steps.addMono(I.shaker(1, seed), s.t, 0.16, pan[s.who]);
  steps.addMono(I.woodTick(1.8 + (seed % 5) * 0.08), s.t, 0.05, pan[s.who]);
}
// title: a closing music-box phrase
[m('A5'), m('C6'), m('E6'), m('A6')].forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, ev.title + i * 0.28, 0.1); verb.addMono(b, ev.title + i * 0.28, 0.12); });

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
