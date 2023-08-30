import typing
from dataclasses import dataclass

import chromadb
import chromadb.api.types
from sentence_transformers import SentenceTransformer


@dataclass(slots=True)
class Record:
    """One record of chronicle id with embedding"""
    id: str
    embedding: chromadb.api.types.Embedding
    metadata: typing.Mapping[str, typing.Union[str, int, float, bool]]


@dataclass(slots=True)
class Similar(Record):
    """Record similar to other record"""
    distance: float


# noinspection SpellCheckingInspection
def parse_similar(result: chromadb.QueryResult) -> tuple[Similar, ...]:
    """
    Parse query result to use object representation rather than bundle of multi vectors.

    :param result: {"ids":["1", ], "embeddings"[[1, 2.2, ...], ], "metadatas":[], "distances"[0.22, ]}
    :return: parsed Similar Records
    """

    return tuple(
        Similar(*rec)
        for rec in zip(
            result["ids"][0],
            result["embeddings"][0],
            result["metadatas"][0],
            result["distances"][0]
        )
    )


class ContextStorage:
    """Store embedding of facts for similarity context search"""
    _client: chromadb.Client
    _embedder: SentenceTransformer
    # noinspection SpellCheckingInspection
    SIM_INCLUDE: list[typing.Literal] = ["embeddings", "metadatas", "distances"]
    # noinspection SpellCheckingInspection
    GET_INCLUDE: list[typing.Literal] = ["embeddings", "metadatas", ]

    # noinspection SpellCheckingInspection
    def __init__(
            self,
            collection: str = "contexter",
            embedding_model: str = "thenlper/gte-large",
    ) -> None:
        self._embedder = SentenceTransformer(embedding_model)
        self._client = chromadb.Client()
        self.collection = self._client.get_or_create_collection(collection)

    def add(
            self,
            id_: int,
            content: str,
            metadata: typing.Optional[dict] = None,
    ) -> None:
        """
        Store new content embedding

        :param id_: fact row id
        :param content: fact to categorize, vectorized with embedding
        :param metadata: optional meta-data
        """
        self.collection.add(
            embeddings=self._embedder.encode(content, normalize_embeddings=True).tolist(),
            metadatas=[metadata] if metadata is not None else None,
            ids=[str(id_), ]
        )

    def get(self, id_: int) -> Record | None:
        """
        Get one embedding record by id.

        :param id_: row id of facts db
        :return: found record, None if there is no record
        """
        row = self.collection.get(str(id_), include=self.GET_INCLUDE)
        if not row["ids"]:
            return None
        # noinspection SpellCheckingInspection
        return Record(row["ids"][0], row["embeddings"][0], row["metadatas"][0])

    def similar_to(
            self,
            content: str,
            n_results: int = 10,
            where: typing.Optional[dict] = None
    ) -> tuple[Similar, ...]:
        """
        Search similar records to given content sample.

        :param content: find records similar to this sample
        :param n_results: limit results count
        :param where: additional filtering
        :return: similar records
        """
        result = self.collection.query(
            query_embeddings=[self._embedder.encode(content, normalize_embeddings=True).tolist()],
            include=self.SIM_INCLUDE,
            n_results=n_results,
            where=where,
        )
        if not result["ids"][0]:
            return tuple()
        return parse_similar(result)
