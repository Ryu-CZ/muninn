import uuid
from typing import Optional, Iterable

import chromadb
import chromadb.utils.embedding_functions
from chromadb.api.types import GetResult
from chromadb.config import Settings

DEFAULT_COLLECTION = "human_context"

__all__ = (
    "GetResult",
    "Settings",
    "VectorStorage",
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

    def __init__(
            self,
            setting: chromadb.config.Settings,
            collection_name: Optional[str] = None,
    ) -> None:
        self.client = chromadb.Client(setting)
        self.collection = self.client.get_or_create_collection(
            name=collection_name or DEFAULT_COLLECTION,
        )

    def get(self, *doc_ids) -> GetResult:
        """
        Find document(s) by id(s)

        :param doc_ids: document ids
        :return: matched documents
        """
        return self.collection.get(ids=doc_ids)

    def query(self, embeddings: list[float], n_results=7) -> Iterable[str]:
        """
        FInd similar document

        :param embeddings: search docs near this vector
        :param n_results: max limit returned doc number
        :return: documents
        """
        result = self.collection.query(query_embeddings=embeddings, n_results=n_results, include=("documents",))
        return (d for d in result["documents"])

    def add(self, embedding: list[float], document: str) -> None:
        """
        Insert embedded document. Skip if it is duplicate.

        :param embedding: embedding of given document
        :param document: insert this text
        """
        doc_hash = hash(document)

        # detect duplicate
        suspect_duplicates = self.collection.query(
            query_embeddings=embedding,
            where={"doc_hash": doc_hash},
            n_results=512,
        )
        if suspect_duplicates and (document in suspect_duplicates["documents"]):
            return

        self.collection.add(
            ids=uuid.uuid4().hex,
            embeddings=embedding,
            metadatas={"doc_hash": doc_hash},
            documents=document,
        )
