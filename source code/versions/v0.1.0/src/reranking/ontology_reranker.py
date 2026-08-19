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

        chunk_concepts = getattr(chunk, "concepts", [])
        chunk_contras = getattr(chunk, "contraindications", []) or []

        query_disease = structured_query.disease
        query_anatomy = structured_query.anatomy
        query_state = structured_query.clinical_state.phase
        query_intent = structured_query.intent.primary
        query_secondary_intents = structured_query.intent.secondary or []

        # 1. Cơ chế Chống chỉ định (Contraindication Penalty)
        contraindicated_concepts = []
        for rel in self.relations:
            if rel["relation"] == "contraindicatedFor":
                if rel["subject"] == query_state or rel["subject"] in query_disease:
                    contraindicated_concepts.append(rel["object"])

        for concept in chunk_concepts:
            if concept in contraindicated_concepts:
                # Nếu chunk chứa concept bị cấm nhưng KHÔNG nằm trong danh sách cảnh báo cấm của chunk
                # (tức là tài liệu khuyến khích hành vi nguy hiểm)
                if concept not in chunk_contras:
                    penalty += 5.0

        # 2. Khớp Bệnh lý (Disease Match) - Có trọng số tin cậy
        if query_disease:
            disease_matched = any(d in chunk_concepts for d in query_disease)
            if disease_matched:
                boost += 0.60 * structured_query.disease_confidence
            else:
                all_diseases = [name for name, c in self.concepts.items() if c.get("type") == "Disease"]
                if any(d in chunk_concepts for d in all_diseases):
                    penalty += 0.80 * structured_query.disease_confidence

        # 3. Khớp Giải phẫu & Quan hệ phân cấp (Anatomy & isPartOf)
        for a in query_anatomy:
            if a in chunk_concepts:
                boost += 0.25 * structured_query.anatomy_confidence
            else:
                for rel in self.relations:
                    if rel["relation"] == "isPartOf" and rel["subject"] in chunk_concepts and rel["object"] == a:
                        boost += 0.20 * structured_query.anatomy_confidence

        # 4. Khớp Trạng thái lâm sàng (Clinical State Match)
        if query_state != "unknown" and query_state in chunk_concepts:
            boost += 0.40 * structured_query.clinical_state.confidence
        
        # Hỗ trợ các khuyến nghị đặc thù theo Ontology
        for rel in self.relations:
            if rel["relation"] == "recommendedFor" and rel["subject"] == query_state:
                if rel["object"] in chunk_concepts:
                    boost += 0.30 * structured_query.clinical_state.confidence

        # 5. Khớp Ý định người dùng (Intent Match)
        all_intents = [query_intent] + query_secondary_intents
        if "rehabilitation" in all_intents and any(c in chunk_concepts for c in ["Rehabilitation", "LowImpactExercise", "ROMStretching", "WaterExercise"]):
            boost += 0.25 * structured_query.intent.confidence
        if "safety" in all_intents and "Safety" in chunk_concepts:
            boost += 0.30 * structured_query.intent.confidence
        if "medication" in all_intents and any(c in chunk_concepts for c in ["Medication", "AntibioticTherapy", "CalciumIntake"]):
            boost += 0.30 * structured_query.intent.confidence
        if "surgery" in all_intents and "Surgery" in chunk_concepts:
            boost += 0.30 * structured_query.intent.confidence
        if "nutrition" in all_intents and any(c in chunk_concepts for c in ["Nutrition", "CalciumIntake", "Hydration"]):
            boost += 0.25 * structured_query.intent.confidence

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
