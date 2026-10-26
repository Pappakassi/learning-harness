# How steep is the hill? (directional derivative) — storyboard

**Learning goal:** after watching, the viewer can compute a directional derivative by hand in four steps (partials → gradient → unit vector → dot product), the way T-304-CACS final Q4 asks.

**Format:** build it up — one small skill per chapter, each stacked on the last, all on one running example.
**Style:** StoryScene with Hr. Schiffel (theme intro/outro).
**Running example:** f(x, y) = x²·y at the point (3, 1), walking in direction (3, 4).
**Target length:** ~3 minutes including the 16 s theme.

Worked by hand:
- ∂f/∂x = 2xy (freeze y), ∂f/∂y = x² (freeze x).
- ∇f = (2xy, x²); at (3, 1): (6, 9).
- |(3, 4)| = √(9 + 16) = 5, so û = (3/5, 4/5).
- D_û f = (6, 9) · (3/5, 4/5) = 18/5 + 36/5 = 54/5 = 10.8.
- Teaser: walking along ∇f itself gives the steepest slope, |∇f| = √(36 + 81) = √117 ≈ 10.8 — almost exactly what we got, because (3,4) points nearly the same way as (6,9).

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 0 | `Intro` | Theme song, title "How steep is the hill?" | — |
| 1 | `Hook` | Top-down contour map of a hill, a hiker dot, three arrows (uphill, along a contour, diagonal) glowing different colours. | Same spot, three directions, three different slopes. How steep is it in the direction I choose? |
| 2 | `Partials` | f(x,y)=x²y; east arrow + "y frozen", north arrow + "x frozen"; results 2xy and x². | Partial derivative = slope walking east or north; freeze the other variable; it is copied, not differentiated. |
| 3 | `Gradient` | Bracket (2xy, x²) → plug in (3,1) → (6,9); arrow drawn on a grid from the point. | Put the two slopes in a vector: the gradient. It points steepest uphill. |
| 4 | `UnitVector` | Arrow (3,4) with right triangle 3-4-5; arrow shrinks to length 1: (3/5, 4/5). | Only the direction matters, so shrink it to length 1: divide by its length. |
| 5 | `DotProduct` | (6,9)·(3/5,4/5) with connector lines pairing parts; countdown; reveal 18/5 + 36/5 = 54/5. | Multiply matching parts, add: that's the slope in our direction. Your turn → 54/5. |
| 6 | `Recipe` | Four numbered steps (exam recipe); teaser: arrow along the gradient, √117. | The exam recipe; teaser: the steepest slope is the length of the gradient. Theme outro. |

**Misconception to address:** in a partial derivative the frozen variable is copied unchanged (it doesn't turn into 1 or 0 when it multiplies) — scene 2.
**Hook:** three arrows from one spot, three slopes.
**Your-turn moment:** scene 5, 3-second countdown before 54/5.
**Teaser:** walk along the gradient → steepest slope = |∇f|.
