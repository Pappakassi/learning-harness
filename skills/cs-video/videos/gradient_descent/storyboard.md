# How does a machine learn? (gradient descent) — storyboard

**Learning goal:** the viewer can explain how a model is trained: measure the mistake as a loss L(w, b), take the
partial derivatives (chain rule) to get the gradient, and step against it, w ← w − η·∂L/∂w; and can do one
training step by hand.

**Format:** build it up — one small idea per chapter on a single running example, then zoom out to real models.
**Style:** StoryScene with Hr. Schiffel (theme intro/outro).
**Running example:** a taxi app in Akureyri learning its price rule. Two past rides:
1 km cost 3 (thousand kr), 2 km cost 5. Model: fare = w·km + b (w = price per km, b = start fee).
The hidden true rule is fare = 2·km + 1.
**Target length:** ~4 minutes including the 16 s theme.

Worked by hand (checked numerically):
- Loss L(w, b) = (w·1 + b − 3)² + (w·2 + b − 5)².
- Start w = 0, b = 0: guesses 0 and 0, errors −3 and −5, L = 9 + 25 = 34.
- ∂L/∂w = 2(w+b−3)·1 + 2(2w+b−5)·2;  ∂L/∂b = 2(w+b−3) + 2(2w+b−5)  (chain rule: the ·1, ·2 are the inside's derivative).
- At (0,0): ∂L/∂w = −6 − 20 = −26; ∂L/∂b = −6 − 10 = −16. Gradient (−26, −16) points uphill.
- Step with η = 0.05: w = 0 − 0.05·(−26) = 1.3; b = 0 − 0.05·(−16) = 0.8. New L = 0.81 + 2.56 = 3.37.
- Path (η = 0.05): step 1 (1.3, 0.8) L 3.37; step 2 (1.71, 1.05) L 0.34; step 3 (1.84, 1.13) L 0.04;
  step 10 (1.91, 1.15); step 50 (1.95, 1.08); step 100 (1.98, 1.04); step 300 (2.00, 1.00) L ≈ 0.
  Big drops first, then a slow crawl along the floor of a long narrow valley.
- Flat spot: ∂L/∂w = 0 and ∂L/∂b = 0 → w = 2, b = 1 (the critical point; a minimum). Same as exam problem 5.
- Teaser, η = 0.2: (0,0) → (5.2, 3.2) L 103 → (−3.84, −2.4) L 313 → L 949: bounces out of the valley.

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 0 | `Intro` | Theme song, title "How does a machine learn?" | — |
| 1 | `Hook` | Plot km vs fare, two ride dots; a flat model line at 0; "?" | Nobody tells the app the price rule. In a few hundred tiny steps it finds it. How? Gnome: guesses randomly? |
| 2 | `Loss` | Red error bars from line to dots, turned into squares; L = 9 + 25 = 34 counter | Measure the mistake: error, square it, add. That number is the loss. |
| 3 | `Landscape` | Map of (w, b) with contour rings of L; dot at (0,0) height 34; star at the bottom | Every pair of knobs is a spot on a map; L is the height. Training = find the lowest point. Same as f(x, y) from the exam. |
| 4 | `Downhill` | Partials with chain rule, plug in (0,0) → (−26, −16); arrow uphill, flipped arrow downhill; update rule; your turn → 1.3; data line tilts | The gradient points uphill (misconception!), so step the opposite way, small step size. Your turn: new w? |
| 5 | `Repeat` | Dot walks the path on the map; data-plot line swings to fit; step counter and loss counter | Repeat. Big drops, then a slow crawl along the valley. Ends at w = 2, b = 1: the flat spot, the critical point. |
| 6 | `RealModels` | Knob counter 2 → 1,000 → 1 billion; examples (spam filter, photos, chat); layer boxes with chain-rule arrows going backwards | Real models: billions of knobs, same recipe. Layers = function inside function, so the chain rule runs backwards: backpropagation. |
| 7 | `Recap` | Three-line recipe; teaser: too-big step bouncing out of the valley | Loss → gradient → step against it, repeat. Teaser: what if the step is too big? Outro. |

**Misconception to address:** the gradient points *uphill*, not downhill, so training subtracts it (scene 4).
**Hook:** the app learns a rule nobody told it.
**Your-turn moment:** scene 4, 3-second countdown before w = 1.3.
**Teaser:** a step size of 0.2 makes the loss explode: 34 → 103 → 313.
