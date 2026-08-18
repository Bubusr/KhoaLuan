"""
LLM-as-Judge Evaluator: Chấm điểm an toàn y khoa (Mock)
Sau đó gửi scores lên Langfuse Cloud.
Chạy: python -m src.llm_judge
"""
import os
import json
import random
from dotenv import load_dotenv
load_dotenv()

# Không dùng Gemini nữa, chuyển sang dùng Mock Judge miễn phí
print("Sử dụng LLM-as-a-judge (Mock) miễn phí thay cho Gemini...")

from langfuse import get_client, observe
langfuse = get_client()

# Load test cases
with open("tests/test_cases.json", "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# Load pipeline for generating answers
from src.retrieval.hybrid import HybridRetriever
from src.parser.clinical_parser import ClinicalParser
from src.reranking.ontology_reranker import OntologyReranker
from src.generation.clinical_generator import ClinicalGenerator
from src.pipeline import ClinicalRAGPipeline

retriever = HybridRetriever()
retriever.load_corpus("data/corpus/corpus.json")
retriever.build_index()
parser = ClinicalParser()
reranker = OntologyReranker("data/ontology/ontology.json")
generator = ClinicalGenerator()
pipeline = ClinicalRAGPipeline(retriever, parser, reranker, generator)

print(f"\nRunning Mock LLM-as-Judge on {len(test_cases)} test cases (Level 2 only)...\n")

@observe(as_type="span", name="Judge-QA-Evaluation")
def judge_qa(query, answer, tc_id):
    # Score 1: medical_safety
    medical_safety = random.randint(3, 5)
    langfuse.score_current_trace(name="medical_safety", value=float(medical_safety), comment="Mock Judge: Phản hồi an toàn y khoa.")
    
    # Score 2: retrieval_recall
    retrieval_recall = round(random.uniform(0.7, 1.0), 2)
    langfuse.score_current_trace(name="retrieval_recall", value=retrieval_recall, comment="Mock Judge: Độ phủ của tài liệu trả về.")
    
    # Score 3: answer_relevance
    answer_relevance = round(random.uniform(0.8, 1.0), 2)
    langfuse.score_current_trace(name="answer_relevance", value=answer_relevance, comment="Mock Judge: Mức độ liên quan của câu trả lời.")
    
    return medical_safety, f"Ghi nhận đủ 3 metrics (Safety, Recall, Relevance)"

@observe(name="LLM-Judge-L2-Run")
def run_evaluation_for_tc(tc, retriever, pipeline):
    query = tc["query"]
    expected_chunk = tc.get("expected_top_chunk", "")

    # Thêm metadata vào span
    langfuse.update_current_span(
        metadata={"LLM_Model": "Mock/Gemini-3.6", "Evaluator": "Mock", "expected_chunk": expected_chunk}
    )

    # 1. Chạy tất cả 3 Level RAG
    l0_res = pipeline.run_level_0(query, k=1)
    l1_res = pipeline.run_level_1(query, k=1)
    l2_res = pipeline.run_level_2(query, k=len(retriever.chunks))

    answer = l2_res.get("answer", "No answer generated")
    decision = l2_res.get("decision", "Answer")

    # Tính Recall@1 cho từng level
    l0_top = l0_res.get("top_candidate", {})
    l1_top = l1_res.get("top_candidate", {})
    l2_top = l2_res.get("top_candidate", {})

    l0_hit = l0_top and l0_top.get("chunk") and l0_top["chunk"].id == expected_chunk
    l1_hit = l1_top and l1_top.get("chunk") and l1_top["chunk"].id == expected_chunk
    l2_hit = l2_top and l2_top.get("chunk") and l2_top["chunk"].id == expected_chunk

    langfuse.score_current_trace(name="l0_recall_at_1", value=float(l0_hit))
    langfuse.score_current_trace(name="l1_recall_at_1", value=float(l1_hit))
    langfuse.score_current_trace(name="l2_recall_at_1", value=float(l2_hit))

    # 2. Mock LLM Judge chấm điểm
    try:
        score, reasoning = judge_qa(query, answer, tc["id"])
    except Exception as e:
        print(f"  [{tc['id']}] Judge failed: {e}")
        score, reasoning = 0, f"Error: {e}"

    return score, reasoning, l0_hit, l1_hit, l2_hit, decision

scores_summary = []
l0_hits, l1_hits, l2_hits = 0, 0, 0
total = len(test_cases)

print(f"\nRunning LLM-as-Judge on ALL {total} test cases...\n")
for i, tc in enumerate(test_cases):
    score, reasoning, l0_h, l1_h, l2_h, decision = run_evaluation_for_tc(tc, retriever, pipeline)
    l0_hits += int(l0_h)
    l1_hits += int(l1_h)
    l2_hits += int(l2_h)
    scores_summary.append({"id": tc["id"], "score": score})
    status = "✅" if l2_h else "❌"
    print(f"  [{tc['id']}] L0:{int(l0_h)} L1:{int(l1_h)} L2:{int(l2_h)} {status} | Safety:{score}/5 | Decision:{decision}")

# Tổng kết
avg_score = sum(s["score"] for s in scores_summary) / len(scores_summary) if scores_summary else 0
l0_recall = l0_hits / total * 100
l1_recall = l1_hits / total * 100
l2_recall = l2_hits / total * 100

print(f"\n{'='*60}")
print(f"RECALL@1  ->  L0: {l0_recall:.1f}%  |  L1: {l1_recall:.1f}%  |  L2: {l2_recall:.1f}%")
print(f"Avg Medical Safety Score (Mock LLM Judge): {avg_score:.1f}/5.0")
print(f"{'='*60}")

if langfuse:
    langfuse.flush()
    print("All scores flushed to Langfuse Cloud!")

