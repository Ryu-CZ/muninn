from dataclasses import dataclass

from . import database, language


@dataclass(slots=True)
class AnalyzedText:
    source: str  # source text
    embedding: list[float]  # categorized text in vector space
    episodic_id: str


class Episodic:
    """Episodic memory"""

    def __init__(
            self,
            embedder: language.Embedding,
            storage: database.VectorStorage,
    ) -> None:
        """
        Construct episodic memory

        :param embedder: categorize text to vector space
        :param storage: vector database
        """
        self.embedder = embedder
        self.storage = storage

    def analyze(self, text: str) -> list[float]:
        """
        Analyze and categorize text in vector space (embedding)

        :param text: text to categorize
        :return: calculated embedding
        """
        return self.embedder.get(text)

    def add(self, text: str) -> AnalyzedText:
        """
        Remember this text to be found by similarity of context.

        :param text: text to remember
        :return: analyzed text
        """
        embedding = self.analyze(text)
        episodic_id = self.storage.add(embedding=embedding, document=text)
        return AnalyzedText(
            source=text,
            embedding=embedding,
            episodic_id=episodic_id
        )
