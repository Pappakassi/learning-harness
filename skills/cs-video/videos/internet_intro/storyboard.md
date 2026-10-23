# How the Internet moves your data (beginner intro to TSAM) — storyboard

**Learning goal:** after watching, a complete beginner can explain the journey of a web
request: the data is cut into packets, wrapped in layers (HTTP, TCP, IP, Ethernet), forwarded
router by router using the destination IP (with TTL counting down), and made reliable by TCP's
SEQ/ACK numbers. They can also work out the next ACK number for a simple exchange, which is the
2023 exam's question 2.

**Format:** *build it up*: start from the naive picture (one wire, the whole page sent in one go)
and fix it one layer at a time.

**Running example:** a laptop in Akureyri asks a web server in Reykjavík for a page.
- The page is 3,000 bytes. With at most 1,500 bytes per packet (MTU), it is cut into 2 packets
  (shown as 1,500 + 1,500); a photo of 3 MB would be about 2,000 packets.
- Addresses: laptop 10.0.0.5, port 51000; server 130.208.240.8, port 80 (HTTP).
- Routing: laptop → R1 (Akureyri) → R2 or R3 → R4 (Reykjavík) → server.
  TTL leaves the laptop at 64: R1 → 63, R2 → 62, R4 → 61.
- TCP trace (byte numbers start at 1, like the exam):
  1. Browser sends a 500-byte request: SEQ 1 (bytes 1–500).
  2. Server answers with 1,200 bytes: SEQ 1, ACK 501 ("got 1–500, send 501 next").
  3. Your turn: browser's ACK = 1 + 1,200 = **1201**.
  4. Browser's next 600-byte request: SEQ 501, ACK 1201.

**Target length:** ~3.5 minutes.

| # | Scene | On screen | Narration (gist) |
|---|-------|-----------|------------------|
| 1 | `Hook` | Laptop (Akureyri) left, server (Reykjavík) right, a cloud of unknown machines between. Click → page appears. Then title. | You click a link; in a few hundredths of a second the page is there, through machines that have never heard of you. How? |
| 2 | `Packets` | Misconception: one big block on a single wire. It splits into 1,500-byte packets which take different routes through a router graph and arrive out of order. | No private wire. Data is cut into packets, each travels on its own, shared with everyone else. |
| 3 | `Layers` | Build an envelope inside an envelope: HTTP data → TCP (ports, SEQ) → IP (addresses, TTL) → Ethernet (next box). Each label pops in with its one job. | Each layer adds a header with one job. The cheat-sheet stack, shown as nested envelopes. |
| 4 | `Routing` | Router graph again; packet hops, a router "reads" only the IP header and checks its table. TTL chip counts 64→63→62→61. Then a loop between two routers: TTL hits 0, packet dropped. | Routers forward hop by hop on destination IP. TTL stops packets circling forever. |
| 5 | `Tcp` | Two timelines (browser / server). SEQ 1, 500 bytes → ACK 501. Server sends 1,200 bytes. Your-turn countdown: what ACK? → 1201. Then a lost packet → timeout → resend. Small UDP card. | TCP numbers every byte; ACK = next byte I expect. Lost data is resent. UDP skips it. |
| 6 | `Recap` | Four bullets; teaser: many senders flood one link, gauge goes red → "Next: congestion control". | Recap the journey; next: what happens when everyone sends at once. |

**Misconception to address:** "there's a direct wire between me and the website, and the page
travels in one piece" (scene 2). Second, smaller one: ACK means "the next byte I expect", not
"the last byte I got" (scene 5).

**Hook:** scene 1 question. **Your turn:** scene 5, ACK after 1,200 bytes. **Teaser:** scene 6, congestion.
