# TSAM: Speed & traffic jams (storyboard)

**Learning goal:** after watching, the viewer can tell bandwidth, latency, jitter and loss apart, say why satellite differs from fibre, describe slow start, timeout vs triple duplicate ACK, the AIMD sawtooth, ECN and TCP starvation by UDP.

**Format:** cartoon cold open (Sam, Ada, sometimes Mallory; `open/`) that poses the problem, then a Manim
explanation (`video.py`) in short chapters, each with its own title and visual change. Details and
calculations are kept light: this is an introduction before working the past exams.

**Hook:** Sam lags out of his game while Ada downloads 40 GB; the router jams.
**Your turn:** 1 TB: 100 Mb/s link vs a pigeon (22 h vs 3.5 h); new ssthresh and cwnd after a timeout at 16 (8 and 1).
**Teaser:** what is an address, really?

Scenes: see `SCENES` in `video.py`; dialogue in `open/lines.py`.
