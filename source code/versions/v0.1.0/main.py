import os
import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from src.retrieval.hybrid import HybridRetriever
from src.parser.clinical_parser import ClinicalParser
from src.reranking.ontology_reranker import OntologyReranker
from src.generation.clinical_generator import ClinicalGenerator
from src.pipeline import ClinicalRAGPipeline

def run_experiment():
    print("==================================================")
    print("STARTING PORTED MODULAR RAG EXPERIMENT")
    print("==================================================")

    # 1. Khởi tạo các cấu phần rời rạc
    retriever = HybridRetriever()
    retriever.load_corpus("data/corpus/corpus.json")
    retriever.build_index()

    parser = ClinicalParser()
    reranker = OntologyReranker("data/ontology/ontology.json")
    generator = ClinicalGenerator()

    # 2. Ráp nối vào bộ điều hợp Pipeline
    pipeline = ClinicalRAGPipeline(retriever, parser, reranker, generator)

    # 3. Tải các ca kiểm thử
    with open("tests/test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results = []

    for tc in test_cases:
        query_id = tc["id"]
        query_name = tc["name"]
        query_text = tc["query"]
        expected_chunk = tc["expected_top_chunk"]
        
        print(f"\n>>> running Case: {query_id} - {query_name}")

        # Chạy thử nghiệm 3 Levels qua Pipeline Orchestrator
        l0_res = pipeline.run_level_0(query_text, k=1)
        l1_res = pipeline.run_level_1(query_text, k=1)
        l2_res = pipeline.run_level_2(query_text, k=1)

        l0_chunk_id = l0_res["top_candidate"]["chunk"].id
        l1_chunk_id = l1_res["top_candidate"]["chunk"].id
        l2_chunk_id = l2_res["top_candidate"]["chunk"].id

        results.append({
            "TC_ID": query_id,
            "Query": query_text,
            "Expected": expected_chunk,
            "L0_Retrieved": l0_chunk_id,
            "L1_Retrieved": l1_chunk_id,
            "L2_Retrieved": l2_chunk_id,
            "L0_Decision": l0_res["decision"],
            "L1_Decision": l1_res["decision"],
            "L2_Decision": l2_res["decision"],
            "L2_Answer": l2_res["answer"]
        })

    # Xuất báo cáo
    df = pd.DataFrame(results)
    print("\n==================================================")
    print("EXPERIMENT COMPLETED!")
    print("==================================================")
    print(df[["TC_ID", "L0_Retrieved", "L1_Retrieved", "L2_Retrieved", "L2_Decision"]])

if __name__ == "__main__":
    run_experiment()
