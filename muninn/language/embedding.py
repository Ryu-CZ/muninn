import os
from typing import Optional

import openai
from dotenv import load_dotenv

load_dotenv(override=True)
openai.api_key = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = "text-embedding-ada-002"


class Embedding:
    """
    OpenAI embedding calculator.

    It stores setting to reduce passing model and key with each call of get embedding.
    Configure once and call many times.
    """

    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            org_key: Optional[str] = None,
    ) -> None:
        """Set up client and parse API keys"""
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.org_key = org_key or os.environ.get("OPEN_API_ORG_KEY")
        if not self.api_key:
            print("OPEN_API_KEY is not set, please set your key with environment variable")

    def get(self, text: str) -> list[float]:
        """
        Calculate embedding vector with open api

        :param text: text to calculate embedding for
        :return: embedding vector representing text topics
        """
        response = openai.Embedding.create(
            input=text,
            model=self.model,
            api_key=self.api_key,
            organization=self.org_key,
        )
        return response["data"][-1]["embedding"]
