import sys
import unittest

sys.path.append('../')

DOCS = ["This is a document", "This is another document"]


class VectorDBTest(unittest.TestCase):

    @staticmethod
    def create_storage():
        from muninn.weave.vector import ContextStorage
        storage = ContextStorage(collection="test_collection")
        return storage

    def test_connect(self):
        storage = self.create_storage()
        self.assertTrue(storage is not None)

    def test_add(self):
        storage = self.create_storage()
        for i, d in enumerate(DOCS):
            storage.add(i, d)
        self.assertEqual(len(DOCS), storage.collection.count())

    def test_get(self):
        from muninn.weave.vector import Record
        storage = self.create_storage()
        for i, d in enumerate(DOCS):
            storage.add(i, d)
        result = storage.get(0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Record)
        result_none = storage.get(-1)
        self.assertIsNone(result_none)

    def test_query(self):
        from muninn.weave.vector import Similar
        storage = self.create_storage()
        for i, d in enumerate(DOCS):
            storage.add(i, d)
        results = storage.similar_to("some document", n_results=2)
        self.assertTrue(results)
        self.assertIsInstance(results, tuple)
        self.assertIsInstance(results[0], Similar)


if __name__ == '__main__':
    unittest.main()
