VOICES = {"sam": "am_puck", "ada": "af_heart", "mallory": "am_onyx"}
SPEED = {"sam": 1.0, "ada": 1.0, "mallory": 0.92}
LINES = [
    ("hook", 0.6, "sam", [("Hello? Hello! I just joined this network.", None, ""), ("Is anyone here handing out addresses?", None, "")]),
    ("a1", 0.5, "ada", [("That's me! I can offer you room one hundred. Interested?", None, "")]),
    ("m1", 0.4, "mallory", [("Psst. Or take my room. No questions asked.", None, "")]),
    ("s2", 0.5, "sam", [("Uh... no thanks. I'd like room one hundred, please!", None, "")]),
    ("a2", 0.4, "ada", [("It's yours for twenty-four hours. Here's your key.", None, "")]),
    ("s3", 0.5, "sam", [("Thanks! But what does my room number actually mean?", None, ""), ("And how do letters find me?", None, "")]),
    ("a3", 0.4, "ada", [("Great question. Let's look at how addresses work.", None, "")]),
]
