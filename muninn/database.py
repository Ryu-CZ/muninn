from typing import Optional

from annoy import AnnoyIndex

DEFAULT_NUM_TREES = 10


def build_annoy_index(embeddings: list[float], texts: str, num_trees: Optional[int] = None):
    num_trees = num_trees or DEFAULT_NUM_TREES
    dimension = len(embeddings[0])
    index = AnnoyIndex(dimension, 'angular')

    for i, embedding in enumerate(embeddings):
        index.add_item(i, embedding)

    index.build(num_trees)

    return index, texts


def search_annoy_index(index, texts, query_embedding, num_results=5):
    nearest_indices, distances = index.get_nns_by_vector(query_embedding, num_results, include_distances=True)
    nearest_texts = [texts[i] for i in nearest_indices]

    return list(zip(nearest_texts, distances))
