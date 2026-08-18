import os
import json
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from src.retrieval.base import BaseRetriever
from src.models import Chunk

class HybridRetriever(BaseRetriever):
    def __init__(self, model_name: str = "neuml/pubmedbert-base-embeddings"):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Chunk] = []
        self.embeddings = []
        self.bm25 = None
        self.tokenized_corpus = []

    def load_corpus(self, corpus_path: str):
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"Corpus file not found at {corpus_path}")
        with open(corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chunks = [Chunk(**item) for item in data]
        print(f"Loaded {len(self.chunks)} chunks from corpus.")

    def build_index(self):
        if not self.chunks:
            raise ValueError("No chunks loaded. Call load_corpus first.")

        # 1. Build Dense Index (Vectors)
        texts = [chunk.text for chunk in self.chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=False)
        self.embeddings = np.array(self.embeddings)
        self.embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)

        # 2. Build Sparse Index (BM25)
        self.tokenized_corpus = [text.lower().split(" ") for text in texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print("Hybrid Index built successfully.")

    def dense_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        query_vector = self.model.encode([query])[0]
        query_vector = query_vector / np.linalg.norm(query_vector)

        similarities = np.dot(self.embeddings, query_vector)
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_indices:
            results.append({
                "chunk": self.chunks[idx],
                "score": float(similarities[idx]),
                "type": "dense"
            })
        return results

    def sparse_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        tokenized_query = query.lower().split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:k]

        max_score = max(scores) if max(scores) > 0 else 1.0

        results = []
        for idx in top_indices:
            results.append({
                "chunk": self.chunks[idx],
                "score": float(scores[idx] / max_score),
                "type": "sparse"
            })
        return results

    from langfuse import observe
    @observe(as_type="span", name="Hybrid-Search")
    def search(self, query: str, k: int = 3, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm lai (Hybrid Search) kết hợp Dense & Sparse
        """
        dense_results = self.dense_search(query, k=len(self.chunks))
        sparse_results = self.sparse_search(query, k=len(self.chunks))

        score_dict = {}
        for res in dense_results:
            chunk_id = res["chunk"].id
            score_dict[chunk_id] = {
                "chunk": res["chunk"],
                "dense_score": res["score"],
                "sparse_score": 0.0
            }
        
        for res in sparse_results:
            chunk_id = res["chunk"].id
            if chunk_id in score_dict:
                score_dict[chunk_id]["sparse_score"] = res["score"]
            else:
                score_dict[chunk_id] = {
                    "chunk": res["chunk"],
                    "dense_score": 0.0,
                    "sparse_score": res["score"]
                }

        hybrid_results = []
        for chunk_id, data in score_dict.items():
            combined_score = alpha * data["dense_score"] + (1 - alpha) * data["sparse_score"]
            hybrid_results.append({
                "chunk": data["chunk"],
                "score": combined_score,
                "dense_score": data["dense_score"],
                "sparse_score": data["sparse_score"]
            })

        hybrid_results = sorted(hybrid_results, key=lambda x: x["score"], reverse=True)[:k]
        return hybrid_results
