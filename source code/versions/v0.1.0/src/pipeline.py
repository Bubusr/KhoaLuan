from typing import Dict, Any, List
from langfuse import observe

from src.models import StructuredQuery, Chunk
from src.retrieval.base import BaseRetriever
from src.parser.base import BaseParser
from src.reranking.base import BaseReranker
from src.generation.base import BaseGenerator

class ClinicalRAGPipeline:
    def __init__(
        self,
        retriever: BaseRetriever,
        parser: BaseParser,
        reranker: BaseReranker,
        generator: BaseGenerator
    ):
        self.retriever = retriever
        self.parser = parser
        self.reranker = reranker
        self.generator = generator

    @observe(name="Run Level 0 Vanilla RAG")
    def run_level_0(self, query: str, k: int = 1, history: list = None) -> Dict[str, Any]:
        """
        Level 0 — Vanilla Hybrid RAG (Không trích xuất, không lọc)
        """
        history = history or []
        candidates = self.retriever.search(query, k=k, alpha=0.5)
        answer, decision = self.generator.generate_answer(query, candidates, StructuredQuery(), history=history)
        return {
            "top_candidate": candidates[0] if candidates else None,
            "candidates": candidates,
            "answer": answer,
            "decision": decision
        }

    @observe(name="Run Level 1 Concept RAG")
    def run_level_1(self, query: str, k: int = 1, history: list = None) -> Dict[str, Any]:
        """
        Level 1 — Concept-Filtered RAG (Lọc/Cộng điểm thực thể thô)
        """
        history = history or []
        structured_query = self.parser.parse(query)
        # Lấy tất cả ứng viên để xếp hạng lại
        all_candidates = self.retriever.search(query, k=len(self.retriever.chunks), alpha=0.5)
        
        reranked_l1 = []
        for cand in all_candidates:
            chunk = cand["chunk"]
            semantic_score = cand["score"]
            boost = 0.0
            
            # Cộng điểm thưởng thô nếu khớp bệnh lý hoặc giải phẫu
            for d in structured_query.disease:
                if d in chunk.concepts:
                    boost += 0.4
            for a in structured_query.anatomy:
                if a in chunk.concepts:
                    boost += 0.3
                    
            reranked_l1.append({
                "chunk": chunk,
                "score": semantic_score + boost,
                "semantic_score": semantic_score,
                "boost": boost,
                "penalty": 0.0
            })
            
        reranked_l1 = sorted(reranked_l1, key=lambda x: x["score"], reverse=True)
        top_candidates = reranked_l1[:k]
        
        answer, decision = self.generator.generate_answer(query, top_candidates, structured_query, history=history)
        return {
            "top_candidate": top_candidates[0] if top_candidates else None,
            "candidates": top_candidates,
            "answer": answer,
            "decision": decision,
            "structured_query": structured_query
        }

    @observe(name="Run Level 2 Ontology RAG")
    def run_level_2(self, query: str, k: int = 1, history: list = None) -> Dict[str, Any]:
        """
        Level 2 — Ontology-Guided RAG (sử dụng đầy đủ quan hệ chống chỉ định)
        """
        history = history or []
        structured_query = self.parser.parse(query)
        all_candidates = self.retriever.search(query, k=len(self.retriever.chunks), alpha=0.5)
        
        reranked_l2 = self.reranker.rerank(all_candidates, structured_query)
        top_candidates = reranked_l2[:k]
        
        answer, decision = self.generator.generate_answer(query, top_candidates, structured_query, history=history)
        return {
            "top_candidate": top_candidates[0] if top_candidates else None,
            "candidates": reranked_l2,  # Trả về toàn bộ để debug diagnostics trên UI
            "answer": answer,
            "decision": decision,
            "structured_query": structured_query
        }
