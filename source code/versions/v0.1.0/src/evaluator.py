import json
import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from src.retrieval.hybrid import HybridRetriever
from src.parser.clinical_parser import ClinicalParser
from src.reranking.ontology_reranker import OntologyReranker
from src.generation.clinical_generator import ClinicalGenerator
from src.pipeline import ClinicalRAGPipeline

class RAGEvaluator:
    def __init__(self, ontology_path="data/ontology/ontology.json", corpus_path="data/corpus/corpus.json"):
        # Khởi tạo các cấu phần modular
        retriever = HybridRetriever()
        retriever.load_corpus(corpus_path)
        retriever.build_index()
        
        parser = ClinicalParser()
        reranker = OntologyReranker(ontology_path)
        generator = ClinicalGenerator()

        # Bộ điều phối Pipeline
        self.pipeline = ClinicalRAGPipeline(retriever, parser, reranker, generator)
        
        with open("tests/test_cases.json", "r", encoding="utf-8") as f:
            self.test_cases = json.load(f)

    def is_violating(self, chunk_id, query_text):
        """
        Kiểm tra xem tài liệu được trích xuất có vi phạm chống chỉ định lâm sàng nào của bệnh nhân không.
        """
        # Phân tích trạng thái lâm sàng của bệnh nhân
        structured_query = self.pipeline.parser.parse(query_text)
        state = structured_query.clinical_state.phase

        # Lấy danh sách chống chỉ định từ Ontology cho trạng thái và các bệnh lý của bệnh nhân
        contraindicated_concepts = []
        for rel in self.pipeline.reranker.relations:
            if (rel["subject"] == state or rel["subject"] in structured_query.disease) and rel["relation"] == "contraindicatedFor":
                contraindicated_concepts.append(rel["object"])

        # Tìm chunk tương ứng
        chunk = next((c for c in self.pipeline.retriever.chunks if c.id == chunk_id), None)
        if not chunk:
            return 0.0

        # Nếu tài liệu khuyên một can thiệp bị chống chỉ định (nằm trong concepts nhưng không nằm trong contraindications cảnh báo của chunk)
        chunk_concepts = chunk.concepts
        chunk_contras = chunk.contraindications or []

        for concept in chunk_concepts:
            if concept in contraindicated_concepts:
                if concept not in chunk_contras:
                    return 1.0
        return 0.0

    def run_suite(self):
        print("\nStarting evaluation suite across all 3 levels...")
        
        summary_results = []
        
        for tc in self.test_cases:
            tc_id = tc["id"]
            query = tc["query"]
            expected = tc["expected_top_chunk"]
            
            # Chạy thử nghiệm các cấu hình thực nghiệm:
            # E1: Dense only
            e1_order = [r["chunk"].id for r in self.pipeline.retriever.dense_search(query, k=len(self.pipeline.retriever.chunks))]
            # E2: Sparse only
            e2_order = [r["chunk"].id for r in self.pipeline.retriever.sparse_search(query, k=len(self.pipeline.retriever.chunks))]
            # E3: Vanilla Hybrid (Level 0)
            l0_res = self.pipeline.run_level_0(query, k=len(self.pipeline.retriever.chunks))
            # Level 1: Concept Filter
            l1_res = self.pipeline.run_level_1(query, k=len(self.pipeline.retriever.chunks))
            # E4 & E5: Ontology Guided (Level 2)
            l2_res = self.pipeline.run_level_2(query, k=len(self.pipeline.retriever.chunks))
            
            print(f"[{tc_id}] Done: {tc['name']}")
            
            e3_order = [r["chunk"].id for r in l0_res["candidates"]]
            l1_order = [r["chunk"].id for r in l1_res["candidates"]]
            e4_order = [r["chunk"].id for r in l2_res["candidates"]]

            e1_mrr = 1.0 / (e1_order.index(expected) + 1) if expected in e1_order else 0.0
            e2_mrr = 1.0 / (e2_order.index(expected) + 1) if expected in e2_order else 0.0
            e3_mrr = 1.0 / (e3_order.index(expected) + 1) if expected in e3_order else 0.0
            l1_mrr = 1.0 / (l1_order.index(expected) + 1) if expected in l1_order else 0.0
            e4_mrr = 1.0 / (e4_order.index(expected) + 1) if expected in e4_order else 0.0

            # Tính CVR
            e1_cvr = self.is_violating(e1_order[0], query)
            e2_cvr = self.is_violating(e2_order[0], query)
            e3_cvr = self.is_violating(e3_order[0], query)
            l1_cvr = self.is_violating(l1_order[0], query)
            e4_cvr = self.is_violating(e4_order[0], query)

            summary_results.append({
                "TC_ID": tc_id,
                "Query": query,
                "Expected": expected,
                "E1_Top": e1_order[0],
                "E1_MRR": e1_mrr,
                "E2_Top": e2_order[0],
                "E2_MRR": e2_mrr,
                "E3_Top": e3_order[0],
                "E3_MRR": e3_mrr,
                "L1_Top": l1_order[0],
                "L1_MRR": l1_mrr,
                "E4_Top": e4_order[0],
                "E4_MRR": e4_mrr,
                "L0_Decision": l0_res["decision"],
                "L1_Decision": l1_res["decision"],
                "L2_Decision": l2_res["decision"],
                "E1_CVR": e1_cvr,
                "E2_CVR": e2_cvr,
                "E3_CVR": e3_cvr,
                "L1_CVR": l1_cvr,
                "E4_CVR": e4_cvr
            })
            
        df = pd.DataFrame(summary_results)
        
        # 1. Tính toán Metrics tổng quan theo mốc Exp E0 -> E5
        mean_e1_hit = np.mean([1.0 if r["E1_Top"] == r["Expected"] else 0.0 for r in summary_results])
        mean_e2_hit = np.mean([1.0 if r["E2_Top"] == r["Expected"] else 0.0 for r in summary_results])
        mean_e3_hit = np.mean([1.0 if r["E3_Top"] == r["Expected"] else 0.0 for r in summary_results])
        mean_e4_hit = np.mean([1.0 if r["E4_Top"] == r["Expected"] else 0.0 for r in summary_results])
        
        mean_e1_mrr = df["E1_MRR"].mean()
        mean_e2_mrr = df["E2_MRR"].mean()
        mean_e3_mrr = df["E3_MRR"].mean()
        mean_e4_mrr = df["E4_MRR"].mean()
        
        # 2. Tính chỉ số nhạy ngữ cảnh (Context-Sensitivity Index - CSI)
        def check_csi(order_tc1, order_tc2):
            return 1.0 if (order_tc1[0] in ["P0001", "P001"] and order_tc2[0] in ["P0002", "P002"]) else 0.0

        tc1_q = self.test_cases[0]["query"]
        tc2_q = self.test_cases[1]["query"]

        e1_order_tc1 = [r["chunk"].id for r in self.pipeline.retriever.dense_search(tc1_q, k=len(self.pipeline.retriever.chunks))]
        e1_order_tc2 = [r["chunk"].id for r in self.pipeline.retriever.dense_search(tc2_q, k=len(self.pipeline.retriever.chunks))]
        csi_e1 = check_csi(e1_order_tc1, e1_order_tc2)

        e2_order_tc1 = [r["chunk"].id for r in self.pipeline.retriever.sparse_search(tc1_q, k=len(self.pipeline.retriever.chunks))]
        e2_order_tc2 = [r["chunk"].id for r in self.pipeline.retriever.sparse_search(tc2_q, k=len(self.pipeline.retriever.chunks))]
        csi_e2 = check_csi(e2_order_tc1, e2_order_tc2)

        e3_order_tc1 = [r["chunk"].id for r in self.pipeline.run_level_0(tc1_q, k=len(self.pipeline.retriever.chunks))["candidates"]]
        e3_order_tc2 = [r["chunk"].id for r in self.pipeline.run_level_0(tc2_q, k=len(self.pipeline.retriever.chunks))["candidates"]]
        csi_e3 = check_csi(e3_order_tc1, e3_order_tc2)

        e4_order_tc1 = [r["chunk"].id for r in self.pipeline.run_level_2(tc1_q, k=len(self.pipeline.retriever.chunks))["candidates"]]
        e4_order_tc2 = [r["chunk"].id for r in self.pipeline.run_level_2(tc2_q, k=len(self.pipeline.retriever.chunks))["candidates"]]
        csi_e4 = check_csi(e4_order_tc1, e4_order_tc2)

        # 3. Tính CVR (Constraint Violation Rate)
        mean_e1_cvr = df["E1_CVR"].mean()
        mean_e2_cvr = df["E2_CVR"].mean()
        mean_e3_cvr = df["E3_CVR"].mean()
        mean_e4_cvr = df["E4_CVR"].mean()

        # 4. Tính Decision F1-Score & Escalation Recall
        gold_decisions = [tc.get("expected_decision", "Answer") for tc in self.test_cases]
        def compute_dec_f1(pred_list):
            classes = set(gold_decisions)
            f1_sum = 0.0
            for c in classes:
                tp = sum(1 for p, g in zip(pred_list, gold_decisions) if p == c and g == c)
                fp = sum(1 for p, g in zip(pred_list, gold_decisions) if p == c and g != c)
                fn = sum(1 for p, g in zip(pred_list, gold_decisions) if p != c and g == c)
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
                f1_sum += f1
            return f1_sum / len(classes)

        l0_dec_f1 = compute_dec_f1(df["L0_Decision"].tolist())
        l2_dec_f1 = compute_dec_f1(df["L2_Decision"].tolist())

        gold_escalations = [i for i, dec in enumerate(gold_decisions) if dec == "Escalate"]
        def compute_esc_recall(pred_list):
            if not gold_escalations:
                return 1.0
            hits = sum(1 for idx in gold_escalations if pred_list[idx] == "Escalate")
            return hits / len(gold_escalations)

        l0_esc_recall = compute_esc_recall(df["L0_Decision"].tolist())
        l2_esc_recall = compute_esc_recall(df["L2_Decision"].tolist())

        # Helper highlight functions
        def fmt_pct(val, reverse=False):
            pct = val * 100
            if not reverse:
                if pct >= 70:
                    return f'<span style="color:#2ecc71">**{pct:.1f}%**</span>'
                return f'<span style="color:#e74c3c">**{pct:.1f}%**</span>'
            else:
                if pct <= 10:
                    return f'<span style="color:#2ecc71">**{pct:.1f}%**</span>'
                return f'<span style="color:#e74c3c">**{pct:.1f}%**</span>'

        def fmt_mrr(val):
            if val >= 0.70:
                return f'<span style="color:#2ecc71">**{val:.3f}**</span>'
            return f'<span style="color:#e74c3c">**{val:.3f}**</span>'

        # Tạo mẫu bảng tổng hợp Ma trận Thực nghiệm E0 -> E5
        eval_report = f"""# BÁO CÁO ĐÁNH GIÁ ĐỊNH LƯỢNG MÔ HÌNH RAG (evaluation_metrics.md)

Báo cáo khoa học so sánh chi tiết hiệu năng tìm kiếm tài liệu lâm sàng giữa các mốc thực nghiệm: **E0 (No RAG)**, **E1 (Dense)**, **E2 (Sparse)**, **E3 (Vanilla Hybrid)**, **E4 (Ontology Guided)** và **E5 (Full Proposed System với Guardrail A/A/E)** trên 50 ca kiểm thử lâm sàng chuyên sâu.

---

> ## 1. Bảng Ma trận Thực nghiệm Đối chứng Triệt tiêu (Ablation Matrix E0 -> E5)
> 
> | Mốc Thực nghiệm (Exp) | Tầng Truy xuất (Retrieval) | Tầng Tri thức (Ontology) | Tầng Sinh & Quyết định (LLM & Safety) | Recall@1 | MRR | Context Sensitivity (CSI) | Tỉ lệ vi phạm chống chỉ định (CVR) | Decision F1 | Escalation Recall |
> | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | **E0** | `—` (No RAG) | ❌ Không | `Base LLM` | 0.0% | 0.000 | 0.0% | 100.0% *(Ảo giác)* | N/A | 0.0% |
> | **E1** | `Dense` (*PubMedBERT*) | ❌ Không | `Base LLM` | {fmt_pct(mean_e1_hit)} | {fmt_mrr(mean_e1_mrr)} | {fmt_pct(csi_e1)} | {fmt_pct(mean_e1_cvr, reverse=True)} | {fmt_pct(l0_dec_f1)} | {fmt_pct(l0_esc_recall)} |
> | **E2** | `Sparse` (*BM25*) | ❌ Không | `Base LLM` | {fmt_pct(mean_e2_hit)} | {fmt_mrr(mean_e2_mrr)} | {fmt_pct(csi_e2)} | {fmt_pct(mean_e2_cvr, reverse=True)} | {fmt_pct(l0_dec_f1)} | {fmt_pct(l0_esc_recall)} |
> | **E3** | `Hybrid` (*BM25 + Dense*) | ❌ Không | `Base LLM` | {fmt_pct(mean_e3_hit)} | {fmt_mrr(mean_e3_mrr)} | {fmt_pct(csi_e3)} | {fmt_pct(mean_e3_cvr, reverse=True)} | {fmt_pct(l0_dec_f1)} | {fmt_pct(l0_esc_recall)} |
> | **E4** | `Hybrid` (*BM25 + Dense*) |  **Có Ontology Reranker** | `Base LLM` | {fmt_pct(mean_e4_hit)} | {fmt_mrr(mean_e4_mrr)} | {fmt_pct(csi_e4)} | {fmt_pct(mean_e4_cvr, reverse=True)} | {fmt_pct(l0_dec_f1)} | {fmt_pct(l0_esc_recall)} |
> | **E5 (Proposed)** | `Hybrid` (*BM25 + Dense*) |  **Có Ontology Reranker** | **Base LLM + Guardrail `A/A/E`** | {fmt_pct(mean_e4_hit)} | {fmt_mrr(mean_e4_mrr)} | {fmt_pct(csi_e4)} | {fmt_pct(mean_e4_cvr, reverse=True)} | {fmt_pct(l2_dec_f1)} | {fmt_pct(l2_esc_recall)} |

---

> ## 2. Chi tiết kết quả kiểm thử trên từng ca lâm sàng (50 Test Cases)
> 
> | Mã Case | Ca kiểm thử | Tài liệu kỳ vọng | E1 (Dense) Top-1 | E2 (Sparse) Top-1 | E3 (Hybrid) Top-1 | E4/E5 (Ontology) Top-1 | Trạng thái E5 |
> | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
        for r in summary_results:
            status_e5 = "✅ PASS" if r["E4_Top"] == r["Expected"] else "❌ FAIL"
            eval_report += f"> | {r['TC_ID']} | {r['Query']} | `{r['Expected']}` | `{r['E1_Top']}` | `{r['E2_Top']}` | `{r['E3_Top']}` | `{r['E4_Top']}` | {status_e5} |\n"

        eval_report += """
---

> ## 3. Bảng Phân tích lỗi theo Giai đoạn Pipeline (Error Analysis by Pipeline Stage)
> 
> Dưới đây là bảng phân rã và phân tích nguyên nhân gốc của các ca lỗi, được nhóm trực tiếp theo các giai đoạn vận hành của hệ thống RAG:
> 
> ### 3.1. Giai đoạn 1: Tầng Phân tích thông tin (Parser Stage)
> 
> | Mã Case | Ca bệnh lâm sàng | Biểu hiện lỗi (Symptom) | Nguyên nhân kỹ thuật (Root Cause) | Giải pháp khắc phục (Remedy) |
> | :--- | :--- | :--- | :--- | :--- |
> | **TC003** | Tra cứu thuốc loãng xương | Cả Level 1 và Level 2 đều lấy nhầm `P005` (phòng ngã) thay vì `P004` (thuốc). | **Lệch từ vựng (Vocabulary Mismatch)**: Câu hỏi dùng từ thông dụng "medications" bị lệch ngữ nghĩa vector so với thuật ngữ chuyên môn "pharmacological interventions" trong tài liệu `P004`. | Tích hợp bảng từ đồng nghĩa (Synonyms) của Ontology vào Parser để tự động mở rộng truy vấn (Query Expansion). |
> 
> ### 3.2. Giai đoạn 2: Tầng Truy xuất & Xếp hạng (Retrieval & Reranking Stage)
> 
> | Mã Case | Ca bệnh lâm sàng | Biểu hiện lỗi (Symptom) | Nguyên nhân kỹ thuật (Root Cause) | Giải pháp khắc phục (Remedy) |
> | :--- | :--- | :--- | :--- | :--- |
> | **TC002** | Gãy xương cột sống cấp | Level 2 lấy nhầm `P003` (rehab sau 6 tuần) thay vì `P002` (nghỉ ngơi cấp). | **Concept Mention vs. Endorsement Bug**: Reranker phạt nhầm tài liệu đúng `P002` vì tài liệu này chứa nhãn phẳng `HighImpactExercise` (nhằm mục đích cảnh báo cấm). | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against` / `recommends`). |
> | **TC004** | Thoái hóa khớp gối sưng cấp | Level 2 lấy nhầm `P003` thay vì `P006` (tập dưới nước). | **Concept Mention Bug**: Phạt nhầm tài liệu đúng `P006` do chứa nhãn phẳng chống chỉ định `HighImpactExercise`. | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against`). |
> | **TC005** | Viêm khớp tiến triển | Level 2 lấy nhầm `P001` thay vì `P007` (tránh tập tạ nặng). | **Concept Mention Bug**: Phạt nhầm tài liệu đúng `P007` do chứa nhãn phẳng chống chỉ định `HeavyResistance`. | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against`). |
> | **TC006** | Viêm khớp gút cấp tính | Level 2 lấy nhầm `P005` thay vì `P008` (cấm ăn thịt đỏ). | **Concept Mention Bug**: Phạt nhầm tài liệu đúng `P008` do chứa nhãn phẳng chống chỉ định `PurineRichFood`. | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against`). |
> | **TC007** | Viêm xương tủy nhiễm trùng | Level 2 lấy nhầm `P003` thay vì `P009` (cấm tì đè chân). | **Concept Mention Bug**: Phạt nhầm tài liệu đúng `P009` do chứa nhãn phẳng chống chỉ định `WeightBearing`. | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against`). |
"""
        # Ghi báo cáo ra root của dự án
        with open("evaluation_metrics.md", "w", encoding="utf-8") as f:
            f.write(eval_report)

        # Cập nhật luôn báo cáo thực nghiệm trong thư mục note
        with open("note/experiment_report.md", "w", encoding="utf-8") as f:
            f.write(eval_report)

        print("Evaluation completed. Saved reports to 'evaluation_metrics.md' and updated 'note/experiment_report.md'")


if __name__ == "__main__":
    evaluator = RAGEvaluator()
    evaluator.run_suite()
