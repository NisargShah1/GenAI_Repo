import math
import re
from typing import List, Dict, Tuple

class SimpleVectorSearch:
    def __init__(self):
        pass

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, extract alphanumeric words
        return re.findall(r'\w+', text.lower())

    def _get_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        total = len(tokens)
        if total == 0:
            return {}
        return {k: v / total for k, v in tf.items()}

    def compute_similarity(self, query: str, document: str) -> float:
        query_tokens = self._tokenize(query)
        doc_tokens = self._tokenize(document)
        if not query_tokens or not doc_tokens:
            return 0.0

        q_tf = self._get_tf(query_tokens)
        d_tf = self._get_tf(doc_tokens)

        # Dot product
        dot_product = 0.0
        for token, val in q_tf.items():
            if token in d_tf:
                dot_product += val * d_tf[token]

        # Cosine length normalization
        q_len = math.sqrt(sum(v*v for v in q_tf.values()))
        d_len = math.sqrt(sum(v*v for v in d_tf.values()))

        if q_len == 0 or d_len == 0:
            return 0.0

        return dot_product / (q_len * d_len)

    def retrieve(self, query: str, documents: List[Tuple[int, str]], top_k: int = 3) -> List[int]:
        """
        Given a query and list of (doc_id, text) tuples,
        returns the ids of the top_k most similar documents.
        """
        scores = []
        for doc_id, text in documents:
            score = self.compute_similarity(query, text)
            scores.append((doc_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, score in scores[:top_k] if score > 0.05]
