import os

import openai
from dotenv import load_dotenv

load_dotenv(override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

FACT_EXTRACTOR_PROMPT = (
    "You are text analyzer. Your task is a table listing the only important facts from Input. Split each complicated "
    "fact into multiple elemental facts."
    "Output format is: |Object1|Predicate1|Subject1|-|Object2|Predicate2|Subject2|-\n\n"
    "Example 2:"
    "\n-Input: "
    "\nRrrr: My name is Rrrr Snoreshort. I am 25 years old gnome with short beard. My Equipment:I use short "
    "sword with shield in melee combat. I own bed roll. I placed rest of my  equipment into my backpack. "
    "It contains: 2 magical scroll and supplies like food, water and torch."
    "\n-Output:"
    "\n|Rrrr|is|25 years old|-|Rrrr|is|gnome|-|Rrrr|has|short beard|-|Rrrr|uses|short sword|-|Rrrr|uses|shield|-"
    "|Rrrr|owns|bed roll|-|Rrrr|has|backpack|-|Rrrr's backpack|contains|2 unidentified magical scrolls|-"
    "|Rrrr's backpack|contains|food|-|Rrrr's backpack|contains|water|-|Rrrr's backpack|contains|2 torches|"
    "\n\nExample 2 (no facts):\n"
    "-Input: \nToday I had a nice day.\n"
    "-Output:"
    "\n\nInput: {text}"
    "Output:\n"
)
target_text = "Valji> My abilities are: Shield Bash: I can use your shield to strike your enemy and stun them for a short period of time.Precise Strike: I have the ability to aim your attacks more accurately, giving you a better chance of hitting your target.Surprising strength: I can double my damage to enemies who have never fought me before. Endurance: I have increased stamina and I can endure physical challenges for longer periods of time."

task = FACT_EXTRACTOR_PROMPT.format(text=target_text)

response = openai.Completion.create(
    model="text-davinci-002",
    prompt=task,
    temperature=0,
    max_tokens=180,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)
