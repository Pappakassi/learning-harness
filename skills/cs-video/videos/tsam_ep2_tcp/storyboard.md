# TSAM: TCP up close (storyboard)

**Learning goal:** after watching, the viewer can explain the three-way handshake and FIN close, why sequence numbers start random, what the receive window and Win=0 mean (2023 exam Q2), and how silly window syndrome and Nagle's algorithm work.

**Format:** cartoon cold open (Sam, Ada, sometimes Mallory; `open/`) that poses the problem, then a Manim
explanation (`video.py`) in short chapters, each with its own title and visual change. Details and
calculations are kept light: this is an introduction before working the past exams.

**Hook:** Sam throws parcels faster than Ada can unpack them; her basket fills (Win = 0).
**Your turn:** the window after 1200 bytes arrive and the app reads 600 of a 2000-byte buffer (1400).
**Teaser:** the routers in between can fill up too (congestion).

Scenes: see `SCENES` in `video.py`; dialogue in `open/lines.py`.
