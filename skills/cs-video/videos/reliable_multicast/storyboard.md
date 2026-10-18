# Why TCP-style reliability breaks for multicast — storyboard

**Learning goal:** the viewer can name and explain the main problems (ACK implosion,
state/buffering, no single timeout, retransmission, congestion control, membership)
that appear when TCP's SEQ/ACK reliability is applied to a large multicast group,
and name the standard fixes.

**Format:** *misconception first.* Take the obvious plan ("just add TCP's ACKs to
multicast"), run it, and watch each part of it fail as the group grows.

**Running example:** one sender, two routers, six receivers (A–F) in a multicast
tree. Numbers scale up to 10,000 receivers at 1,000 packets/s for the maths.

**Numbers (checked):**
- ACK traffic: 10,000 × 1,000 = 10⁷ ACKs/s × 64 bytes × 8 ≈ 5.1 Gbit/s
- P(someone lost it) = 1 − (1 − p)ᴺ, p = 1%: N=10 → 10%, N=100 → 63%, N=1000 → ≈100%

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 1 | `TcpPair` | Sender ↔ receiver. SEQ 1–3 travel right, ACKs travel back. State card next to sender: sequence numbers, ACKs, send buffer, timeout (RTT), congestion window. | TCP's reliability lives in state the sender keeps for exactly one receiver. |
| 2 | `MulticastTree` | Tree: sender → 2 routers → 6 hosts. One packet leaves the sender, routers copy it, all 6 hosts get it. Question callout. | Multicast: send once, routers copy. What if we bolt TCP's ACKs onto this? |
| 3 | `AckImplosion` | All 6 hosts send ACKs at once; they converge, the sender's link turns red. Then the maths: 10,000 × 1,000 = 10,000,000 ACKs/s ≈ 5 Gbit/s. | Every receiver ACKs every packet; N ACKs pile onto one sender. |
| 4 | `SlowestReceiver` | Send buffer (packets 1–8) and three receivers' ACK progress (8, 7, 3). Buffer can only free up to 3. Then an RTT line: 40 ms vs 500 ms with one timeout that fits neither. | Sender must hold data until the slowest receiver ACKs; memory grows with N, one stalled host blocks everyone, and no single timeout fits. |
| 5 | `SomeoneLost` | Plot of 1 − 0.99ᴺ, marker at N=100 → 63%. Then the two bad options for resending (to all: duplicates; to each: unicast again) and congestion control throttling to the worst link. | With many receivers, someone almost always lost each packet. |
| 6 | `Fixes` | Membership note, then three fix cards: NACKs with suppression, hierarchical ACK aggregation / local repair, forward error correction; plus "or leave it to the app (RTP over UDP)". Recap line. | How real protocols get around it. |

**Misconception to address:** "multicast is just TCP sent to many people" — the
reliability machinery is per-pair and does not scale with N.
