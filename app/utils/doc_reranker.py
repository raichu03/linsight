from sentence_transformers import CrossEncoder
from typing import List, Dict, Tuple
from collections import defaultdict

class DocReranker:
    """
    A class for reranking documents using multiple CrossEncoder models,
    combining their scores with Reciprocal Rank Fusion (RRF), and
    ordering the reranked documents in a specific pattern.
    """
    def __init__(self):
        """
        Initializes the ProductionReranker with specified CrossEncoder models.

        Args:
            model_names (List[str]): A list of Hugging Face model names for CrossEncoders.
                                      All models should have the same architecture for consistent scoring.
            rrf_k (int): The constant 'k' for the Reciprocal Rank Fusion formula.
                         A common value is 60.
        """
        model_1 = 'cross-encoder/ms-marco-MiniLM-L-12-v2'
        model_2  = 'cross-encoder/ms-marco-TinyBERT-L-6'
        model_names = [model_1, model_2]

        self.models = [CrossEncoder(model_name) for model_name in model_names]
        self.rrf_k = 60

    def _get_ranks(self, query: str, docs: List[str], model_index: int) -> Dict[str, int]:
        """
        Internal method to get a dictionary of document ranks for a given model.
        """
        query_doc_pairs = [(query, doc) for doc in docs]
        scores = self.models[model_index].predict(query_doc_pairs)

        ranked_docs_with_scores = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

        doc_to_rank = {doc: i + 1 for i, (doc, _) in enumerate(ranked_docs_with_scores)}
        return doc_to_rank

    def rerank(self, query: str, docs: List[str]) -> List[Tuple[str, float]]:
        """
        Reranks a list of documents based on a query using all initialized models
        and combines their scores with Reciprocal Rank Fusion (RRF).

        Args:
            query (str): The search query.
            docs (List[str]): A list of retrieved document texts to be reranked.

        Returns:
            List[Tuple[str, float]]: A list of tuples, where each tuple
                                  contains (document_text, rrf_score),
                                  sorted by 'rrf_score' in descending order.
        """

        all_model_ranks: List[Dict[str, int]] = []
        for i, _ in enumerate(self.models):
            all_model_ranks.append(self._get_ranks(query, docs, i))

        rrf_scores = defaultdict(float)
        for doc in docs:
            for model_ranks in all_model_ranks:
                rank = model_ranks.get(doc)
                if rank is not None:
                    rrf_scores[doc] += 1.0 / (self.rrf_k + rank)

        final_ranked_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return final_ranked_results

    def order_reranked_results(self, reranked_results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """
        Orders the reranked documents in a specific pattern:
        odd-indexed elements followed by reversed even-indexed elements.

        Args:
            reranked_results (List[Tuple[str, float]]): The list of reranked documents
                                                      (document_text, rrf_score) from the rerank method.

        Returns:
            List[Tuple[str, float]]: The reordered list of documents.
        """
        if not reranked_results:
            return []

        odd_indexed_elements = []
        even_indexed_elements = []

        for i, item in enumerate(reranked_results):
            if i % 2 == 0:
                odd_indexed_elements.append(item)
            else: 
                even_indexed_elements.append(item)

        even_indexed_elements.reverse()

        reordered_list = odd_indexed_elements + even_indexed_elements
        return reordered_list

    def get_reranked_and_ordered_results(self, query: str, docs: List[str]) -> List[Tuple[str, float]]:
        """
        Performs reranking and then applies the specific ordering to the results.

        Args:
            query (str): The search query.
            docs (List[str]): A list of retrieved document texts to be reranked.

        Returns:
            List[Tuple[str, float]]: The final list of reranked and specifically ordered documents.
        """
        reranked = self.rerank(query, docs)
        ordered = self.order_reranked_results(reranked)
        return ordered