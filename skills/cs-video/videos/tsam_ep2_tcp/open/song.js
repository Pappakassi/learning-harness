// TSAM cold open sound: dialogue over a light pad; pops at each line, extra pops at SFX times, chime at the title.
const path = require('path');
const fs = require('fs');
const { SR, Bus, reverb } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { DURATION, m, ev, VO } = sc;
const SFX = fs.existsSync(path.join(__dirname, 'sfx.json')) ? JSON.parse(fs.readFileSync(path.join(__dirname, 'sfx.json'))) : {};
const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const pad = bus(), fx = bus(), verb = bus();
const voice = MIX.loadAudio(path.join(__dirname, 'out', 'narration.wav'), { at: 0, gain: 1.0, length: DURATION });
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  const dur = Math.min(c.t1, DURATION) - c.t0;
  for (const n of c.notes) { const { L, R } = I.padNote(n + 12, dur, { cutoff: 1100, attack: 0.8, release: 1.2 }); pad.addStereo(L, R, c.t0, 0.05); }
}
const at = (k) => (typeof k === 'number' ? k : ev[k]);
(SFX.pops || []).forEach((k, i) => fx.addMono(I.pop(1500 + (i % 4) * 250, 40 + i), at(k), 0.2));
(SFX.whoosh || []).forEach((k) => fx.addMono(I.noiseSweep(0.45, 500, 3200, { q: 1 }), at(k) - 0.1, 0.13));
[m('C6'), m('E6'), m('G6'), m('C7')].forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, ev.outro + i * 0.18, 0.12); verb.addMono(b, ev.outro + i * 0.18, 0.14); });
fx.addMono(I.noiseSweep(0.6, 400, 4000, { q: 1 }), ev.outro - 0.2, 0.12);
MIX.duck([pad, fx], voice, { depth: 0.45, attack: 0.05, release: 0.4 });
const stems = { voice, pad, fx, verb: reverb(verb, { room: 0.8, damp: 0.4 }) };
const mix = MIX.mixdown(stems, { voice: 1.0, pad: 1.3, fx: 1.0, verb: 1.0 }, { stemDir: null });
MIX.highpass(mix, 30);
MIX.fadeOut(mix, DURATION - 1.2, DURATION);
const M = MIX.master(mix, 0.8, undefined, { lufs: -16 });
MIX.writeWav(path.join(__dirname, 'out', 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s, ${M.lufs.toFixed(1)} LUFS)`);
