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
| 1 | `Setup` | Weighted graph: B in the middle, links to A (4), C (2), E (6). D and F as faded "?" nodes. Each neighbour sends its vector as a coloured packet to B; the vectors land as rows of a grid. | B only knows its own links. Its neighbours tell it how far they are from everyone. |
| 2 | `Rule` | Bellman–Ford formula, then in words: "link cost + what the neighbour claims". Two misconception chips: "don't forget the link cost" and "next hop ≠ destination". | The rule, and the two classic mistakes. |
| 3 | `Compute` | Vector grid (rows A, C, E with +4/+2/+6 tags) left; routing table right. Per destination: column lights up, three sum chips appear, the smallest glows green, its number flies into the table. A and D in detail, C/E/F quicker. | One column at a time: add, compare, keep the smallest. |
| 4 | `Result` | Graph again: D and F revealed behind C; packets stream B→C→D and B→C→F; final table beside it. Recap line. | C is the next hop for three destinations, because C is cheap to reach and close to D and F. |

**Misconceptions:** forgetting to add the link cost to the neighbour's number; writing the
destination itself as the next hop for non-neighbours (D, F).
