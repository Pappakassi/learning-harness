# How email works under the hood (with Hr. Schiffel): storyboard

**Learning goal:** the viewer can trace an email from app to inbox: SMTP submission (587), MX lookup in DNS,
server-to-server SMTP on port 25 (the text dialogue, STARTTLS), envelope vs headers (Bcc, spoofing),
base64 attachments, SPF/DKIM/DMARC, and IMAP vs POP3.

**Format:** StoryScene style (black, camera moves, Hr. Schiffel reacts and speaks). Theme intro, 7 chapters, outro.
**Running example:** hinni@ru.is → yuki@example.jp, subject "Tómas's birthday".
**Hook:** "You press send; a second later it's in Tokyo. How?" Gnome: "Gnomes. Obviously."
**Your turn:** envelope says mallory@evil.example, letter says ceo@yourbank.com: which does the app show? (the letter)
**Teaser:** next time, SSH.
