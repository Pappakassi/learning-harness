// THE SOUND: the dialogue (out/narration.wav) over a soft pad, pops for signs, a whoosh for the halving.
const path = require('path');
const { SR, Bus, reverb } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { DURATION, m, ev } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const pad = bus(), fx = bus(), verb = bus();
const voice = MIX.loadAudio(path.join(__dirname, 'out', 'narration.wav'), { at: 0, gain: 1.0, length: DURATION });
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  const dur = Math.min(c.t1, DURATION) - c.t0;
  for (const n of c.notes) { const { L, R } = I.padNote(n + 12, dur, { cutoff: 1000, attack: 1.0, release: 1.4 }); pad.addStereo(L, R, c.t0, 0.045); }
}
[ev.middle, ev.ten].forEach((t, i) => fx.addMono(I.pop(1700 + i * 300, 30 + i), t, 0.18));
fx.addMono(I.noiseSweep(0.5, 600, 3000, { q: 1 }), ev.halve - 0.1, 0.12);
[ev.count, ev.n500, ev.n250].forEach((t, i) => { const b = I.musicBox(m(['C6', 'E6', 'G6'][i])); fx.addMono(b, t + 0.05, 0.09); verb.addMono(b, t + 0.05, 0.1); });
[m('C6'), m('E6'), m('G6'), m('C7')].forEach((n, i) => { const b = I.musicBox(n); fx.addMono(b, ev.outro + i * 0.25, 0.1); verb.addMono(b, ev.outro + i * 0.25, 0.12); });

MIX.duck([pad, fx], voice, { depth: 0.45, attack: 0.05, release: 0.4 });
const stems = { voice, pad, fx, verb: reverb(verb, { room: 0.8, damp: 0.4 }) };
const mix = MIX.mixdown(stems, { voice: 1.0, pad: 1.4, fx: 1.0, verb: 1.0 }, { stemDir: null });
MIX.highpass(mix, 30);
MIX.fadeOut(mix, DURATION - 1.4, DURATION);
const M = MIX.master(mix, 0.8, undefined, { lufs: -16 });
MIX.writeWav(path.join(__dirname, 'out', 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s, ${M.lufs.toFixed(1)} LUFS)`);
