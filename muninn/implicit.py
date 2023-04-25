from dataclasses import dataclass

from . import database, language


@dataclass(slots=True)
class AnalyzedText:
    source: str  # source text
    embedding: list[float]  # categorized text in vector space


class ImplicitMemory:

    def __init__(
            self,
            embedder: language.Embedding,
            storage: database.VectorStorage,
    ):
        self.embedder = embedder
        self.storage = storage

    def analyze(self, text: str) -> AnalyzedText:
        """
        Analyze and categorize text in vector space (embedding)

        :param text: text to categorize,
        :return: container with source text and calculated embedding
        """
        return AnalyzedText(
            source=text,
            embedding=self.embedder.get(text),
        )
