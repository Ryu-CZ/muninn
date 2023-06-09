import uuid
from dataclasses import dataclass
from typing import Optional, Iterable, List, TypeVar

import chromadb
import chromadb.api
import chromadb.utils.embedding_functions
from chromadb.api.types import GetResult, Include, ID, Embedding, Document, Metadata, QueryResult
from chromadb.config import Settings

__all__ = (
    "MatchedResult",
    "Settings",
    "VectorStorage",
)

_T = TypeVar("_T")

QUERY_KEYS = ["ids", "embeddings", "documents", "metadatas", "distances"]
DEFAULT_COLLECTION = "human_context"
DOCS_ONLY: Include = ["documents", ]


@dataclass
class MatchedResult:
    ids: Optional[List[ID]]
    embeddings: Optional[List[Embedding]]
    documents: Optional[List[Document]]
    # noinspection SpellCheckingInspection
    metadatas: Optional[List[Metadata]]
    distances: Optional[List[float]]


def first_or_none(array: Optional[List[_T]]) -> Optional[_T]:
    """
    Get first element of array or none

    :param array: optional array
    :return: None or first element
    """
    if not array:
        return None
    return array[0]


def first(query_result: QueryResult | GetResult) -> MatchedResult:
    """
    Get first result from multiset

    :param query_result: original result of query with many sets
    :return: get first set from multiset
    """
    return MatchedResult(
        *(first_or_none(query_result.get(key)) for key in QUERY_KEYS)
    )


class VectorStorage:
    """
    Simplified chromadb client for embedded texts.

    similarity_storage = VectorStorage(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host="localhost",
            chroma_server_http_port="8000"
        )
    )
    """
    client: chromadb.Client
    collection: chromadb.api.Collection

    def __init__(
            self,
            setting: chromadb.config.Settings,
            collection_name: Optional[str] = None,
    ) -> None:
        """
        Set up database client config.

        :param setting: data container of storage settings server/local
        :param collection_name: name for this memory
        """
        collection_name = collection_name or DEFAULT_COLLECTION
        self.client = chromadb.Client(setting)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def get(self, doc_id: ID) -> MatchedResult:
        """
        Find document by id.

        :param doc_id: document ids
        :return: matched documents
        """
        return first(self.collection.get(ids=doc_id))

    def query(self, embedding: list[float], n_results: int = 17) -> Iterable[Document]:
        """
        Find similar document.

        :param embedding: search docs near this vector
        :param n_results: max limit returned doc number
        :return: documents
        """
        result = first(
            self.collection.query(
                query_embeddings=embedding,
                n_results=n_results,
                include=DOCS_ONLY,
            )
        )
        return result.documents

    def add(self, embedding: Embedding, document: Document) -> ID:
        """
        Insert embedded document. Skip if it is duplicate.

        :param embedding: embedding of given document
        :param document: insert this text
        :return: document id
        """
        doc_hash = hash(document)
        # detect duplicate
        # noinspection PyBroadException
        try:
            suspect_duplicates = first(
                self.collection.query(
                    query_embeddings=embedding,
                    where={"doc_hash": doc_hash},
                    include=["documents"],
                )
            )
        except Exception:
            # cannot be handled other way then exception because chroma does not use its own for rest api
            suspect_duplicates = None
        if suspect_duplicates and document in suspect_duplicates:
            index = suspect_duplicates.documents.index(document)
            return suspect_duplicates.ids[index]
        # create new
        new_doc_id = uuid.uuid4().hex
        self.collection.add(
            ids=new_doc_id,
            embeddings=embedding,
            metadatas={"doc_hash": doc_hash},
            documents=document,
        )
        return new_doc_id
