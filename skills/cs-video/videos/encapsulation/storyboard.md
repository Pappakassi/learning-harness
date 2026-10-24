# Envelopes inside envelopes (encapsulation), with Hr. Schiffel: storyboard

**Learning goal:** the viewer can explain encapsulation: each layer (HTTP, TCP, IP, Ethernet) wraps the data in a header
with one job; on the wire it is one byte row (58 bytes of headers for a 15-byte request); routers replace only the link
envelope and lower the TTL; the receiver unwraps layer by layer back up the stack.

**Format:** StoryScene; theme intro, Hook, 5 chapters, recap + outro. Camera pulls back as envelopes grow; camera follows the
packet hop by hop.
**Hook:** a "naked" GET /index.html with three unanswered questions. Gnome: "It will catch its death out there!"
**Your turn:** which envelopes does a router open? (Ethernet and IP)
