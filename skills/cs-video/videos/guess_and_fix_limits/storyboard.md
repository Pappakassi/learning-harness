# Why guess and fix gets stuck — storyboard

**Learning goal:** after watching, the viewer can look at an integral like ∫ x·e^(2x) dx and say in advance whether guess and fix (substitution / reverse chain rule) can solve it, by comparing the extra piece with the inside's derivative.

**Format:** compare two — the same method run on two near-identical integrals side by side; one works, one gets stuck.
**Running example:** ∫ x·e^(x²) dx (works) vs ∫ x·e^(2x) dx (stuck).
**Target length:** ~2 minutes

Worked by hand:
- Left: inside x², guess e^(x²), check e^(x²)·2x, original x·e^(x²) → only a 2 extra → answer ½·e^(x²).
- Right: inside 2x, guess e^(2x), check e^(2x)·2, original x·e^(2x) → the x is missing; no number turns 2 into x.
- Misconception: put the x into the guess: x·e^(2x) → check needs the product rule → e^(2x) + 2x·e^(2x); the extra e^(2x) term can't be fixed.

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 1 | `Hook` | Two integrals side by side; green tick under the left, red question mark under the right. Title after. | They look almost the same; guess and fix solves one, gets stuck on the other. Why? |
| 2 | `Rule` | (e^□)′ = e^□ · □′ with □′ glowing yellow; callout. | The check always throws out exactly one extra factor: the inside's derivative. The extra piece must come back from it. |
| 3 | `Works` | Left case: original, guess, check with 2x in yellow, compare, fix. | The x comes back on its own; only a 2 is extra; divide by 2. |
| 4 | `Stuck` | Right case: guess, check with 2 in yellow; the x is crossed out red, shake. Then the misconception: x in the guess → product rule → extra e^(2x) term in red. | The check never brings back the x. Putting the x in the guess adds a term you can't fix. |
| 5 | `YourTurn` | ∫ x cos(x²) dx vs ∫ x cos x dx, countdown 3 s, then reveal inside′ under each. | Which one works? The left: 2x matches x. The right: inside′ is 1. |
| 6 | `Recap` | Two callouts (test → method), teaser: x morphs into 1. | The test; when it fails, parts differentiates the x away. |

**Misconception to address:** "just put the x into the guess" (scene 4).
**Hook:** two look-alike integrals, one solvable, one not.
**Your-turn moment:** scene 5 with a 3-second countdown.
**Teaser:** integration by parts turns the troublesome x into 1.
