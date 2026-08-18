import json
import os
from typing import List, Dict, Any
from src.reranking.base import BaseReranker
from src.models import StructuredQuery

class OntologyReranker(BaseReranker):
    def __init__(self, ontology_path: str = "data/ontology/ontology.json"):
        self.ontology = {}
        self.concepts = []
        self.relations = []
        self.load_ontology(ontology_path)

    def load_ontology(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Ontology file not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            self.ontology = json.load(f)
        self.concepts = {c["name"]: c for c in self.ontology.get("concepts", [])}
        self.relations = self.ontology.get("relations", [])
        print(f"Loaded ontology with {len(self.concepts)} concepts and {len(self.relations)} relations.")

    def calculate_scores(self, chunk, structured_query: StructuredQuery):
        boost = 0.0
        penalty = 0.0

        # Nếu chunk truyền vào là Pydantic Object (Chunk class)
        chunk_concepts = getattr(chunk, "concepts", [])
        chunk_id = getattr(chunk, "id", "")

        query_disease = structured_query.disease
        query_anatomy = structured_query.anatomy
        query_state = structured_query.clinical_state.phase
        query_intent = structured_query.intent.primary

        # 1. Chống chỉ định
        contraindicated_concepts = []
        for rel in self.relations:
            if rel["subject"] == query_state and rel["relation"] == "contraindicatedFor":
                contraindicated_concepts.append(rel["object"])

        for concept in chunk_concepts:
            if concept in contraindicated_concepts:
                penalty += 5.0

        # 2. Khớp bệnh lý
        for d in query_disease:
            if d in chunk_concepts:
                boost += 0.3

        # 3. Khớp giải phẫu
        for a in query_anatomy:
            if a in chunk_concepts:
                boost += 0.2
            else:
                for rel in self.relations:
                    if rel["relation"] == "isPartOf" and rel["subject"] in chunk_concepts and rel["object"] == a:
                        boost += 0.15

        # 4. Khớp trạng thái lâm sàng
        if query_state in chunk_concepts:
            boost += 0.4
        
        if query_state == "AcutePostFracture" and "Rest" in chunk_concepts:
            boost += 0.3

        # 5. Khớp ý định
        if query_intent == "rehabilitation" and "Rehabilitation" in chunk_concepts:
            boost += 0.2
        elif query_intent == "safety" and "Safety" in chunk_concepts:
            boost += 0.3

        return boost, penalty

    from langfuse import observe
    @observe(as_type="span", name="Ontology-Reranker")
    def rerank(self, candidates: List[Dict[str, Any]], structured_query: StructuredQuery) -> List[Dict[str, Any]]:
        reranked_results = []
        for cand in candidates:
            chunk = cand["chunk"]
            semantic_score = cand["score"]

            boost, penalty = self.calculate_scores(chunk, structured_query)
            final_score = semantic_score + boost - penalty

            reranked_results.append({
                "chunk": chunk,
                "score": final_score,
                "semantic_score": semantic_score,
                "boost": boost,
                "penalty": penalty
            })

        reranked_results = sorted(reranked_results, key=lambda x: x["score"], reverse=True)
        return reranked_results
