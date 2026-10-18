# Distance vector routing at node B — storyboard

**Learning goal:** the viewer can fill in a node's routing table from its neighbours'
distance vectors using D_B(y) = min over neighbours v of { c(B,v) + D_v(y) }, and
pick the right next hop.

**Format:** *build it up* — B starts knowing only its own links, receives three
claims, then works out each destination one column at a time.

**Running example (the exercise):** neighbours A (cost 4), C (cost 2), E (cost 6).
Vectors [D(A), D(B), D(C), D(D), D(E), D(F)]:
- A: [0, 4, 6, 20, 13, 5]
- C: [5, 2, 0, 3, 10, 1]
- E: [13, 6, 10, 7, 0, 8]

**Worked answers (checked in code):**

| Dest | via A | via C | via E | Cost | Next hop |
|---|---|---|---|---|---|
| A | 4+0=4 | 2+5=7 | 6+13=19 | 4 | A |
| C | 4+6=10 | 2+0=2 | 6+10=16 | 2 | C |
| D | 4+20=24 | 2+3=5 | 6+7=13 | 5 | C |
| E | 4+13=17 | 2+10=12 | 6+0=6 | 6 | E |
| F | 4+5=9 | 2+1=3 | 6+8=14 | 3 | C |

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 1 | `Hook` | B alone in a fog of dots, a packet "to F" with a "?". Then "cheapest route: 3, via C". | B has never seen F, yet in a minute it'll know the cheapest route. How? |
| 2 | `Gossip` | B's three links appear; D, F ghosted. Neighbours' vectors pop up as speech bubbles, then fly into a table. | Neighbours gossip their distances. |
| 3 | `FirstRace` | Race bars to D (link cost + claim, same speed). C finishes first at 5. | Picture first: race the three routes. |
| 4 | `Rule` | Bellman–Ford formula with braces; two trap cards. | What you watched has a name. Two traps. |
| 5 | `Races` | Quick races for A, C, E filling the table; F is "your turn" with a 3-second countdown, then the reveal. | One race per destination; viewer predicts F. |
| 6 | `Payoff` | Map with D, F behind C; packets stream along every route. | B learned it all from gossip. |
| 7 | `Teaser` | C–D link breaks; B and C ping-pong rising guesses 5→7→…→15. | Count to infinity, next video. |

**Hook:** "B has never seen F, yet will know the cheapest route." **Your turn:** F. **Teaser:** count to infinity
(in this network it stops at C = 15 / B = 13 because B's route via E costs 13).

**Misconceptions:** forgetting to add the link cost to the neighbour's number; writing the
destination itself as the next hop for non-neighbours (D, F).
