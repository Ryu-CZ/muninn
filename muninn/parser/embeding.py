import os
from pprint import pprint

import openai
from dotenv import load_dotenv

load_dotenv(override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

ANALYZER_ADA = "text-embedding-ada-002"
OPEN_API_KEY = os.environ.get("OPENAI_API_KEY")
OPEN_API_ORG_KEY = os.environ.get("OPEN_API_ORG_KEY")

input_to_analyze = "Valji owns Berserker sword"
response = openai.Embedding.create(
    input=input_to_analyze,
    model=ANALYZER_ADA,
)
pprint(response["data"][-1]["embedding"])
