import sys
import unittest
import logging
sys.path.append('../')

DOCS = ["This is a document", "This is another document"]

logger = logging.getLogger("test")
logger.level = logging.DEBUG
logger.addHandler(logging.StreamHandler(sys.stdout))


class VectorDBTest(unittest.TestCase):

    @staticmethod
    def create_storage():
        from muninn.weave.vector import ContextStorage
        storage = ContextStorage(collection="test_collection")
        logger.debug(f"create_storage - storage={storage}")
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
        self.assertTrue(storage.collection.count())
        result = storage.get(0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Record)
        logger.debug(f"test_get - result={result}")
        result_none = storage.get(-1)
        self.assertIsNone(result_none)

    def test_query(self):
        from muninn.weave.vector import Similar
        storage = self.create_storage()
        for i, d in enumerate(DOCS):
            storage.add(i, d)
        results = storage.similar_to(DOCS[0], n_results=len(DOCS))
        self.assertTrue(results)
        self.assertIsInstance(results, tuple)
        self.assertIsInstance(results[0], Similar)
        logger.debug(f"test_query - results={results}")
        # results are ordered and same text is embedded to same vector
        self.assertAlmostEqual(results[0].distance, 0, delta=0.05)
        self.assertLessEqual(len(DOCS), storage.collection.count())
        more_results = storage.similar_to(DOCS[0], n_results=storage.collection.count() + 2)
        self.assertTrue(results)
        logger.debug(f"test_query - more_results={more_results}")


if __name__ == '__main__':
    unittest.main()
