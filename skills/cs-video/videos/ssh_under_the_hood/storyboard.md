# How SSH works under the hood (with Hr. Schiffel): storyboard

**Learning goal:** the viewer can explain SSH's three jobs (secrecy, server authenticity, user authentication) and the
order they happen: TCP :22, version strings, Diffie-Hellman key exchange, host key + known_hosts, public-key login
(signature over session data), multiplexed channels, local port forwarding (-L).

**Format:** StoryScene style; theme intro, 6 chapters, outro.
**Hook:** one `ssh hinni@server.ru.is` line, crossing café WiFi, ISP and backbone. Gnome: "Strangers! Like Mallory."
**Your turn:** the host key changed next week: why? (reinstall, or a man-in-the-middle)
**Teaser/close:** "Secret, authentic, and you are you. Three problems, one protocol."
