import typing
import chromadb
from sentence_transformers import SentenceTransformer

Embedding = typing.Union[typing.Sequence[float], typing.Sequence[int]]


class GetResult(typing.TypedDict):
    ids: list[str]
    embeddings: list[Embedding]
    # noinspection SpellCheckingInspection
    metadatas: list[typing.Mapping[str, typing.Union[str, int, float, bool]]]


class QueryResult(typing.TypedDict):
    ids: list[str]
    embeddings: list[Embedding]
    # noinspection SpellCheckingInspection
    metadatas: list[typing.Mapping[str, typing.Union[str, int, float, bool]]]
    distances: list[list[float]]


class Contexter:
    _client: chromadb.Client
    _embedder: SentenceTransformer
    # noinspection SpellCheckingInspection
    SIM_INCLUDE: list[typing.Literal] = ["embeddings", "metadatas", "distances"]
    # noinspection SpellCheckingInspection
    GET_INCLUDE: list[typing.Literal] = ["embeddings", "metadatas", ]

    def __init__(
            self,
            collection: str = "contexter",
            embedding_model: str = "thenlper/gte-large",
    ) -> None:
        self._embedder = SentenceTransformer(embedding_model)
        self._client = chromadb.Client()
        self.collection = self._client.get_or_create_collection(collection)

    def add(self, id_: int, content: str, meta_data: typing.Optional[dict] = None) -> None:
        self.collection.add(
            embeddings=self._embedder.encode(content, normalize_embeddings=True),
            metadatas=[meta_data] if meta_data is not None else None,
            ids=[str(id_), ]
        )

    def get(self, id_: int) -> GetResult:
        # noinspection PyTypeChecker
        return self.collection.get(str(id_), include=self.GET_INCLUDE)

    def similar_to(self, content: str, where: typing.Optional[dict] = None) -> QueryResult:
        # noinspection PyTypeChecker
        return self.collection.query(
            query_embeddings=self._embedder.encode(content, normalize_embeddings=True),
            include=self.SIM_INCLUDE,
            where=where
        )
