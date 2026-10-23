VOICES = {"sam": "am_puck", "ada": "af_heart", "mallory": "am_onyx"}
SPEED = {"sam": 1.0, "ada": 1.0, "mallory": 0.95}
LINES = [
    ("hook", 0.8, "ada", [("Sam, I'm trying to join your game server, but it just times out.", None, "")]),
    ("s1", 0.5, "sam", [("Weird. My laptop's address is one-nine-two, one-six-eight, one, thirty.", "Weird. My laptop's address is 192.168.1.30.", ""), ("Just connect to that.", None, "")]),
    ("a2", 0.5, "ada", [("That's a private address. Millions of homes use exactly the same one!", None, "")]),
    ("s2", 0.4, "sam", [("Then how do I reach anything on the Internet at all?", None, "")]),
    ("a3", 0.5, "ada", [("Your router speaks for the whole house.", None, ""), ("And it only lets in replies to things you asked for.", None, "")]),
    ("s3", 0.5, "sam", [("So how do I let you in?", None, "")]),
    ("a4", 0.4, "ada", [("Let's look at NAT, and a few ways around it.", None, "")]),
]
