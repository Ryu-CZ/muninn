import sys
import unittest

sys.path.append('../')

EMBEDDINGS = [[1.2, 2.3, 4.5], [6.7, 8.2, 9.2]]
DOCS = ["This is a document", "This is another document"]


class SimilarityDBTest(unittest.TestCase):

    @staticmethod
    def create_storage():
        from muninn.database.similarity_db import Settings, VectorStorage
        storage = VectorStorage(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host="localhost",
                chroma_server_http_port="8000",
            ),
            "test_collection",
        )
        return storage

    def test_connect(self):
        storage = self.create_storage()
        self.assertTrue(storage is not None)

    def test_add(self):
        storage = self.create_storage()
        ids = []
        for e, d in zip(EMBEDDINGS, DOCS):
            new_id = storage.add(embedding=e, document=d)
            ids.append(new_id)
        self.assertEquals(len(ids), 2)

    def test_query(self):
        storage = self.create_storage()
        results = [storage.query(embedding=[1.5, 2.0, 4.0], n_results=2)]
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
