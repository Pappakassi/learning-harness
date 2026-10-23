# TSAM: Home networks (storyboard)

**Learning goal:** after watching, the viewer can list the private ranges, trace a NAT translation with the 2023 exam's numbers, explain why a router reboot breaks connections, the end-to-end problem and its fixes (port forwarding, UPnP, hole punching, relays), and the four-AP lecture-hall problem and rogue APs.

**Format:** cartoon cold open (Sam, Ada, sometimes Mallory; `open/`) that poses the problem, then a Manim
explanation (`video.py`) in short chapters, each with its own title and visual change. Details and
calculations are kept light: this is an introduction before working the past exams.

**Hook:** Ada can't reach Sam's game server; his router only lets replies in.
**Your turn:** which device gets the reply to 14.11.12.144:62000 (192.168.1.30:51000).
**Teaser:** every packet passes through strangers: trust.

Scenes: see `SCENES` in `video.py`; dialogue in `open/lines.py`.
