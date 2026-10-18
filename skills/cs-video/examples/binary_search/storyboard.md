# Binary search — storyboard

**Learning goal:** after watching, the viewer can run binary search by hand with `lo`, `mid`, `hi`, and explain why it takes about log₂(n) steps.

**Format:** problem → key idea → worked trace with code → why it's fast → recap
**Running example:** `[3, 8, 12, 17, 21, 26, 31, 40, 44, 52]`, target `31` (index 6)
**Target length:** ~2.5 minutes

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 1 | `Problem` | Title. Sorted array appears. A single pointer scans left to right, 7 checks to reach 31. Counter shows checks. | Find 31. Checking one by one took 7 checks; on a million items it could take a million. |
| 2 | `KeyIdea` | Array. Check the middle (21). Left half fades out with a red strike. Callout: "One comparison throws away half." | Because it's sorted, one comparison at the middle tells us which half can't contain the target. |
| 3 | `Trace` | Array on the left with `lo`/`mid`/`hi` pointers, code on the right with line highlight. Four iterations: mid=4 (21<31 → lo=5), mid=7 (40>31 → hi=6), mid=5 (26<31 → lo=6), mid=6 (found). Step counter. | Walk through the loop line by line, narrating each comparison and which pointer moves. |
| 4 | `WhyFast` | Column of halvings: 1,000,000 → 500,000 → … → 1 with a step count reaching 20. Then `steps ≈ log₂(n)` and a small table n vs steps. | Each step halves what's left; halving a million down to one takes about 20 steps — that's log base 2. |
| 5 | `Recap` | Three bullets revealed one at a time. | Sorted input; keep lo and hi, check mid; O(log n). |

**Misconception to address:** binary search only works on sorted data (said in scenes 2 and 5).
