# Bone/MSK Evidence-Grounded QA — Đặc tả hệ thống đầy đủ (v3)

### Bệnh viện Chấn thương Chỉnh hình TP.HCM

Đây là **một tài liệu độc lập, đầy đủ**: toàn bộ Stage 0–9 được mô tả chi tiết (nguồn, input/output, công thức, các bước triển khai, tham số, trường hợp đặc biệt, đánh giá), kèm hạ tầng, schema, mã tham chiếu, kế hoạch đánh giá, vận hành, an toàn và đối chiếu với Research Roadmap. Không cần đọc file nào khác.

**Quy ước:**

- `[GIỮ NGUYÊN]` = lấy thẳng từ bài báo gốc, không chỉnh sửa
- `[MỚI]` = tự thiết kế thêm, không có trong bài báo nào
- `[MỞ RỘNG]` = dựa trên ý tưởng gốc của bài báo nhưng có chỉnh sửa/bổ sung để khớp dataset thật
- ✅ đã có cơ chế được thiết kế · 🟡 một phần · ❌ chưa có
- **Mọi tham số số học (trọng số, ngưỡng, k, γ, δ, μ, τ, threshold) là giá trị khởi điểm hợp lý, chưa được kiểm chứng.** Phải tune bằng dev set của bệnh viện và được bác sĩ chuyên khoa phê duyệt. Mã nguồn tham chiếu chưa được chạy kiểm thử.
- "✅ đã có cơ chế" nghĩa là đã có thiết kế, **không** có nghĩa đã được kiểm chứng.

## Mục lục

**Phần A — Tổng quan:** A1 Bối cảnh · A2 Vị trí triển khai theo 4 giai đoạn · A3 Sơ đồ tổng quan · A4 Nguồn bài báo · A5 Hợp đồng dữ liệu giữa các stage · A6 Phạm vi v1/v2 · A7 Nguyên tắc thiết kế

**Phần B — Các Stage:** Stage 0 · 1 · 2 · 3 · 4 · 5 · 6 · 7 · 8 · 9 · Output cuối cùng

**Phần C — Dữ liệu, đánh giá, thí nghiệm:** C1 Nguồn dữ liệu · C2 Question Taxonomy · C3 Schema mẫu QA · C4 Metric theo tầng · C5 Chuỗi thí nghiệm L0–L5 và ablation · C6 Dev/Test set

**Phần D — Vận hành, an toàn, quyền riêng tư**

**Phần E — Đối chiếu Research Roadmap, tồn đọng và quyết định cần chốt**

**Phần F — Phụ lục:** danh mục cờ · bảng Giữ nguyên/Mới · prompt mẫu · test case hồi quy

---

# PHẦN A — TỔNG QUAN

## A1. Bối cảnh và dataset nền

**Dataset:** 1,247 ca lâm sàng

| Pathology | Số ca | Tỉ lệ |
|---|---|---|
| Traumatic | 876 | 70.2% |
| Neoplastic | 241 | 19.3% |
| Inflammatory | 130 | 10.5% |

| Anatomy | Tỉ lệ |
|---|---|
| Chi dưới | 52.8% |
| Chi trên | 31.2% |
| Thân mình | 16.0% |

**Hệ quả thiết kế:**

- Phân bố lệch mạnh về Traumatic, nhưng Neoplastic nhỏ mà rủi ro lâm sàng cao nhất → mọi cơ chế an toàn và mọi báo cáo đánh giá phải **tách theo pathology_class**.
- Dataset chỉ có 3 pathology class, trong khi Research Roadmap liệt kê 8 (xem Phần E, mục E3).
- Dataset là hồ sơ ca bệnh; **chưa có kho guideline/tài liệu ngoài** (xem C1).

## A2. Hệ thống đưa vào người dùng ở giai đoạn nào?

### A2.1 Khuyến nghị

**Giai đoạn 3 (Chẩn đoán xác định & Lập kế hoạch) là chính; Giai đoạn 1 ở phạm vi hẹp. Giai đoạn 2 chỉ là nguồn dữ liệu; Giai đoạn 4 và "Before consultation" hoãn sang v2.** Đây là khuyến nghị thiết kế dựa trên dữ liệu và kiến trúc, **chưa được bác sĩ xác nhận**; cần phỏng vấn 3–5 bác sĩ để xác nhận bước nào họ mất nhiều thời gian tra cứu nhất (xem Stage 0, mục 0.6).

### A2.2 Ánh xạ 4 giai đoạn lâm sàng

| Giai đoạn | Input | Output lâm sàng | Vị trí RAG | Vai trò hệ thống | Stage hoạt động | Phạm vi |
|---|---|---|---|---|---|---|
| **1. Đánh giá lâm sàng ban đầu** | Triệu chứng, lời kể bệnh nhân | Hồ sơ bệnh án sơ bộ, phiếu chỉ định xét nghiệm/chụp chiếu | *During consultation* | Truy xuất guideline, chẩn đoán phân biệt, sàng lọc gãy xương bệnh lý; khi thiếu dữ liệu thì nêu rõ cần bổ sung gì (bác sĩ quyết định) | 3, 4, 5, 6, 9 (+7) | v1 hẹp |
| *(1)* | | | *Before consultation* | Hỗ trợ bệnh nhân tổng hợp triệu chứng | — | v2 |
| **2. Cận lâm sàng & khảo sát** | Phiếu chỉ định | Ảnh, báo cáo CĐHA, xét nghiệm | (thu thập dữ liệu) | Không trả lời; nạp và chuẩn hóa dữ liệu | 2 | Chỉ nạp dữ liệu |
| **3. Chẩn đoán xác định & lập kế hoạch** | Kết quả GĐ1 + GĐ2 | Chẩn đoán xác định, phác đồ, y lệnh | *After tests/imaging*; *After diagnosis* | Nối findings với tri thức bệnh; giải thích bệnh, điều trị, phục hồi, tiên lượng, phòng ngừa | 1–9 (đầy đủ) | **v1 trọng tâm** |
| **4. Quản lý & theo dõi sau điều trị** | Phác đồ, mức độ đáp ứng | Hồ sơ tái khám, điều chỉnh điều trị, chuyển tuyến | *Follow-up* | Theo dõi tiến triển | cần bổ sung | v2 |

### A2.3 Vì sao Giai đoạn 3 là chính

1. Cơ chế cốt lõi (applicability, trích dẫn, quyết định trả lời hay không) cần cả dữ liệu lâm sàng lẫn cận lâm sàng, mà thông tin này đầy đủ nhất ở Giai đoạn 3.
2. Khớp dữ liệu hiện có (hồ sơ + báo cáo CĐHA) → có thể đánh giá lại trên ca đã có kết quả, không cần triển khai trên bệnh nhân thật.
3. Đây là bước cần explanation/citation/uncertainty nhất (rủi ro ảo giác và gán sai nguồn cao nhất).
4. Dễ gán gold evidence và nhãn applicability hơn so với ca đang khám dở.

### A2.4 Vì sao chưa chọn giai đoạn khác

- **Giai đoạn 1:** dữ liệu còn thiếu nên phần lớn đầu ra sẽ là "cần bổ sung thông tin", khó đo hơn; vấn đề thuật ngữ đời thường chưa được xử lý hoàn chỉnh.
- **Giai đoạn 2:** chỉ thu thập dữ liệu, không có chỗ để RAG trả lời.
- **Giai đoạn 4:** cần bộ nhớ theo thời gian và kiểm soát trôi ngữ cảnh; chưa có trong thiết kế.

### A2.5 Ngoại lệ đi sớm

**Stage 3 (red-flag screening)** thuộc Giai đoạn 1 nhưng nên chạy ngay từ v1: chỉ cần tiền sử/tuổi (không cần cận lâm sàng) và xử lý rủi ro lớn nhất của dataset (gãy xương bệnh lý bị nhầm với chấn thương thường). Nó là **lớp cảnh báo an toàn đi kèm**, không phải use case riêng.

### A2.6 Chế độ chạy theo giai đoạn (phase-aware mode) `[MỚI]`

Cùng một pipeline, hành vi khác nhau theo `phase` của yêu cầu:

| | `phase = P1` (During consultation) | `phase = P3` (After tests/diagnosis) |
|---|---|---|
| Dữ liệu sẵn có | Triệu chứng, tiền sử, khám lâm sàng; **chưa có** CĐHA/lab | Lâm sàng + CĐHA + lab (+ chẩn đoán nếu có) |
| Stage 3 | Chạy đầy đủ, có thể trả `indeterminate` do thiếu trường | Chạy đầy đủ |
| Stage 4 | Truy xuất theo entity triệu chứng/vị trí; chẩn đoán phân biệt (`dx`) là chính | Truy xuất đầy đủ theo mọi `qtype` |
| Stage 5 | `match_severity` thường `unknown` → applicability tối đa Partial | Đầy đủ |
| Stage 6 | Gap Analysis tập trung "thiếu thông tin lâm sàng/cận lâm sàng nào" | Gap Analysis cả relevance và applicability |
| Stage 9 | ASK_MORE là nhánh thường gặp; liệt kê thông tin/cận lâm sàng còn thiếu **để bác sĩ cân nhắc, không tự ra phiếu chỉ định** | Ba nhánh đầy đủ |
| Output | Chẩn đoán phân biệt có trích dẫn + danh sách thông tin còn thiếu + red-flag | Câu trả lời đầy đủ theo qtype |

## A3. Sơ đồ tổng quan

```
INPUT: CaseInput (phase, question, patient, presentation, exam, imaging, labs, notes)
   ↓
STAGE 0  Clinical Workflow Positioning (cấu hình phạm vi, phase-aware)       [MỚI]
   ↓
STAGE 1  Ontology-Grounded KG Construction (offline)                          [MỞ RỘNG]
STAGE 2  Multi-Source Document Processing (offline + online)                  [MỞ RỘNG]
   ↓
STAGE 3  Red-Flag Screening Gate                                              [MỚI]
   ↓ (nếu không red-flag; nếu indeterminate vẫn chạy tiếp kèm cờ)
STAGE 4  Hybrid + Graph-Guided Retrieval (hợp nhất Text + Graph)              [GIỮ NGUYÊN + MỚI]
   ↓
STAGE 5  Evidence Evaluation: Relevance + Applicability                       [GIỮ NGUYÊN + MỚI]
   ↓
STAGE 6  Iterative Retrieval-Verification  ⟲ (quay lại Stage 4, T_max = 3)    [GIỮ NGUYÊN + MỞ RỘNG]
   ↓
STAGE 7  Citation-Aware, Applicability-Conditioned Generation                 [MỞ RỘNG]
   ↓
STAGE 8  Step-Level Confidence Scoring + Calibration                          [GIỮ NGUYÊN + MỞ RỘNG]
   ↓
STAGE 9  Decision Gate (3 nhánh, multi-round)                                 [MỞ RỘNG]
   ↓
OUTPUT: Answer + Evidence + Citation + Confidence + Missing Info + Applicability Warning + Evidence Flags + Red-Flag Alert
```

Stage 1 và phần nạp của Stage 2 chạy **offline** (xây tri thức); Stage 3–9 chạy **online** cho mỗi yêu cầu.

## A4. Nguồn bài báo theo stage

| Stage | Bài báo gốc |
|---|---|
| 1 | Clinical Knowledge Graph Construction and Evaluation with Multi-LLMs via Retrieval-Augmented Generation (Das et al., 2025) |
| 2 | CLI-RAG: A Retrieval-Augmented Framework for Clinically Structured and Context-Aware Text Generation |
| 4 | CLI-RAG (luồng Text) + KnowGuard (luồng Graph); phần hợp nhất là `[MỚI]` |
| 5 | KnowGuard (Relevance); Applicability là `[MỚI]` |
| 6, 7 | MedTrust-RAG: Evidence Verification and Trust Alignment for Biomedical Question Answering |
| 8 | Med-PRM: Medical Reasoning Models with Stepwise, Guideline-verified Process Rewards |
| 9 | KnowGuard: Knowledge-Driven Abstention for Multi-Round Clinical Reasoning |
| 0, 3 | Không có — tự thiết kế |

## A5. Hợp đồng dữ liệu giữa các stage

| Từ → Đến | Dữ liệu truyền |
|---|---|
| S1 → S2, S4 | KG (triple có `trust_T`, `reviewed_by_md`, `source_chunks`, `pathology_class`, `anatomy_region`), ontology ID, alias đời thường |
| S2 → S3, S4 | chunk + metadata (`note_type`, `chunk_type`, `section`, `pathology_class`, `anatomy_region`, `entity_ids`, `source_authority`, `applicability_conditions`) |
| S3 → S4 | `RedFlagResult` (true / false / indeterminate + lý do + trường thiếu); nếu `true` thì thoát sớm |
| S4 → S5 | danh sách `EvidenceUnit` + `RetrievalReport` (cờ, coverage, thống kê) |
| S5 → S6, S9 | `p_final`, `s_appl` (Applicable / Partial / NotApplicable) + mã lý do |
| S6 → S4 | `q_{t+1}`, `E_query` cộng dồn (vòng lặp) |
| S6 → S7, S9 | evidence pool đã xác minh + danh sách thông tin còn thiếu (phân loại relevance-gap / applicability-gap) |
| S7 → S8 | các statement có trích dẫn |
| S8 → S9 | `r_total` (đã hiệu chuẩn) + điểm từng bước |
| S9 → OUTPUT | nhánh quyết định + toàn bộ cờ cảnh báo |

## A6. Phạm vi v1 / v2

| Hạng mục | v1 | v2 |
|---|---|---|
| Giai đoạn lâm sàng | GĐ3 (chính), GĐ1 *During consultation* (hẹp) | GĐ1 đầy đủ (kể cả *Before consultation*), GĐ4 |
| Actor | Bác sĩ Cấp cứu / Chấn thương Chỉnh hình | Bệnh nhân, bác sĩ nội cơ xương khớp, CĐHA, PHCN |
| Dữ liệu | Văn bản (EHR, báo cáo CĐHA), lab dạng cấu trúc | Ảnh X-quang/CT/MRI (nhánh multimodal), longitudinal |
| Pathology | Traumatic, Neoplastic, Inflammatory | Mở rộng class khác khi có dữ liệu |
| Ngôn ngữ | Việt–Anh, bác sĩ | Ngôn ngữ bệnh nhân (đời thường) |
| Follow-up, bộ nhớ phiên | Không | Có |

## A7. Nguyên tắc thiết kế xuyên suốt

1. **An toàn trước, đầy đủ sau:** khi không chắc → cảnh báo hoặc hỏi thêm, không đoán.
2. **Hint chỉ là soft boost, không là hard filter** (tránh loại nhầm bằng chứng u bướu).
3. **Mọi bằng chứng trích dẫn được** (`source_ref` thống nhất cho chunk và triple).
4. **Cờ cảnh báo không bao giờ bị ẩn khỏi bác sĩ** (`unreviewed`, `conflict`, `late_neoplastic_signal`…).
5. **Tách theo pathology_class ở mọi bước đánh giá**; nhóm Neoplastic có ngưỡng nghiêm ngặt hơn và review thủ công.
6. **Không thay thế quyết định lâm sàng:** hệ thống đề xuất bằng chứng và nêu giới hạn; bác sĩ quyết định.
7. **Tái lập và kiểm toán:** log đầy đủ điểm, rank, cờ, phiên bản.
8. **Thiếu dữ liệu ≠ không áp dụng được:** giá trị `unknown` được xử lý trung tính có kiểm soát, không biến thành kết luận.

---

# PHẦN B — CÁC STAGE

---

## STAGE 0 — Clinical Workflow Positioning `[MỚI]`

**Nguồn:** Không có — toàn bộ stage này là quyết định nội bộ.

**Ý tưởng chính:** Xác định hệ thống chèn vào đâu trong quy trình khám thật, ai dùng, thông tin nào đi vào, dựa trên phân bố dữ liệu; sau đó **xác nhận bằng khảo sát thực tế**.

**Công thức:** Không áp dụng.

**Input:** phân bố dữ liệu, kết quả phỏng vấn bác sĩ (khi có).
**Output:** cấu hình phạm vi (`phase`, actor, loại câu hỏi hỗ trợ), `CaseInput` schema, bảng luồng thông tin.

### 0.1 Quyết định vị trí chèn (tất cả `[MỚI]`)

1. 70.2% ca là trauma → ưu tiên "After tests/imaging" làm use case chính v1 (Giai đoạn 3).
2. Mở rộng "After diagnosis" (giải thích bệnh, điều trị, phục hồi, tiên lượng, phòng ngừa) vào v1, vì các template ở Stage 7 đã phủ các loại câu hỏi này. *(Bổ sung so với bản trước: bản trước chưa nêu vị trí này.)*
3. Vị trí thứ hai: "During consultation" (Giai đoạn 1) — phân biệt pathological fracture với traumatic fracture thường, chẩn đoán phân biệt.
4. "Before consultation" và "Follow-up" để lại cho v2.
5. Actor chính v1: bác sĩ khoa Cấp cứu/Chấn thương Chỉnh hình. Đây là **chọn phạm vi v1**, không loại bỏ các actor khác (Research Roadmap coi các vai trò là actors, chưa cần chọn end user chính ở bước khảo sát).

### 0.2 Luồng thông tin: mỗi loại thông tin đi vào pipeline ở đâu

| Loại thông tin | Tạo ra bởi | Đi vào pipeline ở | Trạng thái |
|---|---|---|---|
| Triệu chứng / lời kể bệnh nhân | Bệnh nhân, bác sĩ ghi | `CaseInput.presentation`; Stage 3; query ở Stage 4 | ✅ |
| Tiền sử, bệnh nền, thuốc đang dùng | Bác sĩ, EHR | `CaseInput.patient`; Stage 3, 5 (chống chỉ định) | 🟡 (cần nguồn thông tin thuốc) |
| Khám thực thể (vị trí đau, ROM, biến dạng, thần kinh…) | Bác sĩ | `CaseInput.exam`; Stage 5 (`match_severity`) | 🟡 (cần schema có cấu trúc) |
| Hình ảnh + báo cáo CĐHA | Bác sĩ CĐHA | Stage 2 (chunk Findings / Impression); Stage 1 (morphology) | 🟡 (chỉ phần văn bản; ảnh để v2) |
| Xét nghiệm | Labo | Stage 2 (parse dạng bảng → chunk `lab` + hàng cấu trúc) | 🟡 (cần quyết định phạm vi) |
| Ghi chú lâm sàng / EHR | Bác sĩ | Stage 2 | ✅ |
| Guideline / literature / thông tin thuốc | Nguồn ngoài | Stage 2 (nạp), Stage 4 (truy xuất) | ❌ (**nguồn chưa xác định**, xem C1) |
| Kế hoạch điều trị / PHCN / theo dõi | Bác sĩ | Stage 2 (Assessment/Plan) | 🟡 (theo dõi để v2) |

### 0.3 Schema đầu vào `CaseInput` `[MỚI]`

```json
{
  "request_id": "R_0001",
  "phase": "P1",
  "question": "Cần phân biệt gãy xương bệnh lý không?",
  "patient": {
    "age": 54, "sex": "F",
    "comorbidities": [], "current_medications": []
  },
  "presentation": {
    "chief_complaint": "...",
    "onset": "...",
    "mechanism_of_injury": "...",
    "energy_level": "low | moderate | high | unknown",
    "pain_before_event": true,
    "unexplained_weight_loss": null
  },
  "exam": {
    "region": "lower_limb",
    "findings_text": "...",
    "neuro_signs": null
  },
  "imaging_reports": [{"report_id": "...", "findings": "...", "impression": "..."}],
  "labs": [{"test": "...", "value": 0, "unit": "...", "ref_range": "..."}],
  "notes": [{"note_type": "ehr_hpi", "text": "..."}]
}
```

Giá trị `null` / `unknown` nghĩa là **chưa biết**, không phải "không có". Các stage sau phân biệt rõ hai trường hợp này (nguyên tắc A7-8).

### 0.4 Chế độ chạy

Xem A2.6 (phase-aware mode). Stage 0 xuất cấu hình `mode_config` quyết định: Stage nào bật, `threshold` nào dùng, ASK_MORE có phát danh sách thông tin thiếu hay không.

### 0.5 Khoảng trống workflow thực tế mà Stage 0 cần khảo sát

| Câu hỏi | Cách trả lời |
|---|---|
| Bác sĩ phải tìm guideline/literature thủ công ở bước nào? | Phỏng vấn |
| Thông tin bệnh nhân bị phân tán ở đâu? | Phỏng vấn + quan sát |
| Khi nào evidence chung không hợp bệnh nhân cụ thể? | Phỏng vấn; xác nhận cơ chế Stage 5 |
| Khi nào thiếu dữ liệu khiến không kết luận an toàn? | Phỏng vấn; xác nhận cơ chế Stage 6/9 |
| Bước nào cần explanation / citation / uncertainty nhất? | Phỏng vấn; xác nhận vị trí chèn |

### 0.6 Kế hoạch khảo sát (xác nhận hoặc sửa Stage 0) `[MỚI]`

- Phỏng vấn bán cấu trúc bác sĩ: Cấp cứu, Chấn thương Chỉnh hình, Chẩn đoán hình ảnh, Phục hồi chức năng (thêm Nội cơ xương khớp nếu mở rộng phạm vi).
- Quan sát (shadowing) một số ca để vẽ lại luồng thông tin từ tiếp nhận đến theo dõi.
- Cần phê duyệt của bệnh viện/hội đồng đạo đức trước khi quan sát hoặc dùng dữ liệu thật.
- **Tiêu chí đổi hướng:** nếu đa số bác sĩ cho biết điểm mất thời gian tra cứu nhất nằm ở Giai đoạn 1 thay vì Giai đoạn 3, ưu tiên v1 phải được cân nhắc lại.

### 0.7 Đánh giá riêng Stage 0

Không có metric tự động. Tiêu chí: kết quả khảo sát xác nhận (hoặc sửa) vị trí chèn; danh sách `qtype` hỗ trợ ở v1 được bác sĩ đồng ý.

---

## STAGE 1 — Ontology-Grounded Knowledge Graph Construction `[MỞ RỘNG]`

**Nguồn gốc `[GIỮ NGUYÊN]`:** Das et al., 2025.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Dùng 3 LLM đóng vai trò khác nhau để tự động trích xuất, chuẩn hóa và validate Knowledge Graph từ văn bản lâm sàng tự do, không cần gold-standard annotation.

**Input:** chunk từ Stage 2 (văn bản lâm sàng, báo cáo, guideline), ontology Bone/MSK.
**Output:** KG (Neo4j) + bảng provenance chunk ↔ entity ↔ triple + bảng alias (chuyên môn và đời thường).

### 1.1 Công thức

`[GIỮ NGUYÊN]` Trích EAV triple từ văn bản:

$$T_i = f(x_i) = \{(e_j, a_j, v_j)\}$$

`[GIỮ NGUYÊN]` Entropy của giá trị được trích:

$$H(v) = -\sum_t p_t \log p_t$$

`[GIỮ NGUYÊN]` Điểm map vào ontology, với ràng buộc α + β = 1:

$$Score(c, o) = \alpha \cdot sim_{lex}(c, o) + \beta \cdot sim_{sem}(c, o), \qquad \alpha + \beta = 1$$

`[GIỮ NGUYÊN]` Composite trust score (các thành phần R, C, J và λ theo định nghĩa trong bài gốc; **cần đối chiếu lại bài khi triển khai**):

$$T = \lambda_1 \cdot R + \lambda_2 \cdot C + \lambda_3 \cdot J$$

`[MỚI]` Áp dụng riêng cho nhánh Neoplastic: hạ ngưỡng chấp nhận tự động xuống (thực tế: không tự động chấp nhận), tăng tỉ lệ bắt buộc review thủ công bởi bác sĩ, thay vì chỉ dùng một threshold T cố định như bài gốc.

### 1.2 Vai trò 3 LLM `[GIỮ NGUYÊN ý tưởng]`

| Vai trò | Nhiệm vụ | Output |
|---|---|---|
| Extractor | Trích EAV từ chunk | Danh sách `(entity, attribute, value)` |
| Normalizer/Mapper | Chuẩn hóa và map vào ontology (dùng `Score(c,o)`) | `(ont_id, link_score)` |
| Validator | Kiểm tra nhất quán, mâu thuẫn, tính hợp lý lâm sàng | Điểm kiểm định (thành phần của `T`) |

Nên dùng 3 mô hình/prompt khác nhau để tránh lỗi tương quan. Mô hình dùng ở Stage 1 không bắt buộc trùng với mô hình sinh câu trả lời ở Stage 7.

### 1.3 Ontology Bone/MSK (các layer song song) `[MỞ RỘNG]`

Thay SNOMED/RxNorm của bài gốc bằng ontology riêng, gồm **6 layer song song** (không phải chuỗi tuyến tính Disease → Morphology → Pathology):

| Layer | Nội dung | Ví dụ |
|---|---|---|
| Anatomy | Vùng giải phẫu (chi dưới > chi trên > thân mình về mức chi tiết) | xương đùi, cổ xương đùi, cột sống, khớp gối, vai, bàn tay, bàn chân |
| Pathology Class | Nhóm bệnh lý | Traumatic, Neoplastic, Inflammatory (+ các class khác khi có dữ liệu) |
| Disease Entity | Thực thể bệnh | gãy xương, osteosarcoma, viêm khớp dạng thấp… |
| Morphology | Hình thái tổn thương | xem 1.4 |
| Pathophysiology | Cơ chế bệnh | tiêu xương > tạo xương; thoái hóa sụn; nhiễm trùng → phá hủy xương |
| Clinical Phenotype | Triệu chứng, mức độ/giai đoạn, yếu tố nguy cơ, chẩn đoán, điều trị, phục hồi, tiên lượng, phòng ngừa | đau, sưng, hạn chế ROM, yếu cơ… |

### 1.4 Morphology

- `[MỞ RỘNG]` **Gãy xương (Traumatic):** transverse, oblique, spiral, comminuted, impacted, avulsion.
- `[MỚI]` **Tổn thương u bướu / viêm:** bổ sung các morphology mà Research Roadmap nêu (lytic, sclerotic, mixed, cortical destruction, osteophyte, joint-space narrowing…). **Danh sách cụ thể cho Neoplastic và Inflammatory phải do bác sĩ CĐHA/chuyên khoa chốt**, vì chưa có trong thiết kế gốc.
- Morphology là **cầu nối** giữa mô tả CĐHA (văn bản) → ontology → disease → retrieval. (Cầu nối từ **ảnh** thuộc v2.)

### 1.5 Từ vựng quan hệ (relation vocabulary) `[MỞ RỘNG]`

Quan hệ nên thống nhất tên với ontology thực tế; bảng dưới là bộ khởi điểm:

| Quan hệ | Miền → Đích | Dùng cho qtype |
|---|---|---|
| `located_in` | Disease → Anatomy | dx |
| `is_a` | Disease → Pathology Class / Disease → Disease cha | dx |
| `has_morphology` | Disease → Morphology | dx |
| `has_pathophysiology` | Disease → Pathophysiology | rehab/prog, sym |
| `has_phenotype` | Disease → Clinical Phenotype | dx, sym |
| `differential_of` | Disease ↔ Disease | dx |
| `caused_by` | Disease → Cause | sym |
| `risk_factor_of` | Risk factor → Disease | sym, prev |
| `treated_by` | Disease → Treatment | tx |
| `indicated_for` | Treatment → Disease/Condition | tx |
| `contraindicated_in` | Treatment → Condition | tx |
| `requires_imaging` | Disease/Condition → Imaging modality | dx |
| `complication_of` | Complication → Disease/Treatment | rehab/prog |
| `prognosis_of` | Prognostic factor → Disease | rehab/prog |
| `rehab_for` | Rehab method → Disease | rehab/prog |
| `prevented_by` | Disease → Prevention measure | prev `[MỚI]` |

### 1.6 Lớp từ đồng nghĩa (alias) chuyên môn và đời thường `[MỚI]`

Vấn đề: ngôn ngữ đời thường ("giòn xương") khác thuật ngữ chuyên môn ("loãng xương") làm giảm mạnh hiệu quả của retriever truyền thống.

Mỗi node Entity có thêm các trường:

```json
{
  "id": "ONT:Osteoporosis",
  "label_vi": "loãng xương",
  "label_en": "osteoporosis",
  "aliases_vi_formal": ["thưa xương"],
  "aliases_vi_lay": ["giòn xương", "xương yếu"],
  "aliases_abbrev": [],
  "alias_ambiguity": "none | ambiguous",
  "alias_source": "md_curated | mined_from_notes",
  "alias_reviewed_by_md": true
}
```

- Alias đời thường được **khai thác từ ghi chú thực tế** (lời kể bệnh nhân trong EHR) và **bác sĩ duyệt**; không tự suy diễn.
- Alias mơ hồ (một cụm từ có thể ứng với nhiều entity) gắn `alias_ambiguity = ambiguous`; entity linking giữ nhiều ứng viên và dùng ngữ cảnh để phân giải.
- Alias được dùng ở: entity linking (Stage 1, 4), mở rộng truy vấn BM25 (Stage 4), chuẩn hóa văn bản khi nạp (Stage 2, trường `text_norm`).
- Cần thiết ngay ở v1 (lời kể bệnh nhân vẫn xuất hiện trong ghi chú), và sẽ quan trọng hơn ở v2 khi có *Before consultation*.

### 1.7 Triển khai

1. `[GIỮ NGUYÊN]` Trích EAV từ EHR + report, gán kiểu theo schema FHIR-like.
2. `[MỞ RỘNG]` Thay ontology SNOMED/RxNorm bằng ontology Bone/MSK riêng (1.3).
3. `[MỚI]` Phân bổ effort theo tỉ lệ dataset: ưu tiên subgraph Traumatic (70.2%) trước, đầy đủ morphology (1.4) — bài gốc không có bước phân bổ effort theo tỉ lệ dữ liệu.
4. `[MỚI]` Subgraph Neoplastic (19.3%): **bác sĩ chuyên khoa review thủ công toàn bộ relation**, không chỉ dựa vào đồng thuận 3 LLM như bài gốc làm với oncology.
5. `[MỚI]` Anatomy layer ưu tiên độ chi tiết theo tỉ lệ: chi dưới > chi trên > thân mình.
6. `[MỚI]` **Lưu provenance cho mọi triple** (bắt buộc cho Stage 4):
   - `source_chunks`: danh sách `chunk_id` mà triple được trích ra (hợp nhất khi cùng triple xuất hiện ở nhiều chunk)
   - `origin_kind`: `extracted` / `curated` / `ontology`
   - `reviewed_by_md`, `review_required` (luôn `true` với Neoplastic)
   - `pathology_class`, `anatomy_region` gắn trên triple
7. `[MỚI]` Tính sẵn `degree` cho mỗi node (batch job) để phạt hub node ở Stage 4.
8. `[MỚI]` Triple "curated" (bác sĩ nhập tay) và "ontology" không có `source_chunks`; được xử lý bằng verbalize ở Stage 4.
9. `[MỚI]` (Tùy chọn, kiểm tra giấy phép trước) Ánh xạ ontology riêng sang một chuẩn quốc tế (ví dụ SNOMED CT, UMLS, ICD-11, RadLex, FMA) để tăng khả năng tái sử dụng và công bố.

### 1.8 Ngưỡng chấp nhận vào KG `[MỚI]` (giá trị khởi điểm)

| Nhánh | Điều kiện | Hành động |
|---|---|---|
| Traumatic / Inflammatory | `T ≥ 0.80` | Tự chấp nhận (kèm kiểm tra lấy mẫu ngẫu nhiên, khởi điểm ~5% để ước lượng độ chính xác) |
| Traumatic / Inflammatory | `0.60 ≤ T < 0.80` | Vào hàng đợi review của bác sĩ |
| Traumatic / Inflammatory | `T < 0.60` | Loại |
| **Neoplastic** | `T ≥ 0.60` | **Bắt buộc review thủ công** mới được `reviewed_by_md = true`; chưa duyệt thì ở trạng thái `staged` |
| Neoplastic | `T < 0.60` | Loại |

Entropy `H(v)` cao (giá trị trích không chắc chắn) → ưu tiên đưa vào hàng đợi review dù `T` đạt ngưỡng.

### 1.9 Phạm vi pathology class

Dataset chỉ có 3 class. Cần chốt (Phần E):
- **Hướng A (thu hẹp):** phạm vi nghiên cứu = Traumatic / Neoplastic / Inflammatory.
- **Hướng B (giữ rộng):** ontology đủ 8 class (Traumatic, Degenerative, Inflammatory/Autoimmune, Metabolic, Infectious, Neoplastic, Congenital/Developmental, Vascular/Necrotic), chỉ đánh giá trên 3 class có dữ liệu và ghi rõ giới hạn.

Cần kiểm tra lại nhãn: nhóm Inflammatory 10.5% có gồm Infectious (ví dụ osteomyelitis) và Autoimmune (ví dụ viêm khớp dạng thấp) không.

### 1.10 Kiểm tra toàn vẹn (CI/nightly)

- Mọi `source_chunks` tồn tại trong chunk store.
- Mọi `entity_ids` tồn tại trong ontology.
- Mọi triple Neoplastic có `review_required = true`.
- Tỉ lệ triple không có `source_chunks` theo `origin_kind` được báo cáo.
- Không có alias đời thường trỏ đến nhiều entity mà thiếu cờ `ambiguous`.

### 1.11 Đánh giá riêng Stage 1

Chất lượng trích xuất triple (precision/recall trên mẫu bác sĩ chấm); độ chính xác của bước tự chấp nhận (mẫu kiểm tra); **Entity Linking F1** (đo riêng, vì chất lượng luồng Graph ở Stage 4 phụ thuộc trực tiếp vào đây); độ phủ alias đời thường.

---

## STAGE 2 — Multi-Source Document Processing `[MỞ RỘNG]`

**Nguồn gốc `[GIỮ NGUYÊN]`:** CLI-RAG.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Chunk văn bản lâm sàng theo cấu trúc logic (section), dùng retrieval 2 tầng Global → Local để xử lý nhiều loại văn bản cùng lúc.

**Input:** EHR note, báo cáo CĐHA, kết quả xét nghiệm, guideline/tài liệu (PDF, văn bản).
**Output:** chunk store (BM25 + vector + metadata), bảng `chunk_entity`.

### 2.1 Công thức

`[GIỮ NGUYÊN]` Metadata mỗi chunk:

$$chunk = (patient\_id, visit\_date, note\_type, section, local\_index)$$

`[GIỮ NGUYÊN]` Global retrieval:

$$D_{global} = HybridRank(q, Docs_{all\_types})$$

`[GIỮ NGUYÊN]` Local retrieval:

$$D_{local} = HybridRank(q_t, Docs_t)$$

(Việc thực thi retrieval nằm ở Stage 4, mục 4.7.)

### 2.2 Chunking theo loại tài liệu

| Loại | Cách chunk | Nguồn |
|---|---|---|
| EHR note | Hierarchical theo section (HPI, PE, Assessment/Plan); mỗi section là một chunk, section dài được tách với phần chồng lắp nhỏ (khởi điểm ~400 token, chồng ~50) | `[GIỮ NGUYÊN]` |
| Báo cáo CĐHA | Tách **Findings** và **Impression** thành 2 `chunk_type` khác nhau (CLI-RAG phân biệt "diagnostic impressions in radiology reports" khỏi narrative) | `[GIỮ NGUYÊN]` |
| Guideline | Tách theo **đơn vị khuyến cáo**, không theo kích thước cố định; mỗi chunk mang `applicability_conditions`, `evidence_level`, `version`, `published_date` | `[MỚI]` |
| Bảng / sơ đồ trong PDF | Phân tích bố cục, trích bảng thành dạng cấu trúc + caption; hình chỉ có hình thì lưu caption và gắn cờ `figure_only` | `[MỚI]` |
| Xét nghiệm | Parse thành hàng cấu trúc (test, value, unit, ref_range, flag) + một chunk `lab` tóm tắt; chuẩn hóa đơn vị | `[MỚI]` |

### 2.3 Xử lý PDF phức tạp (bảng biểu, sơ đồ) `[MỚI]`

Vấn đề: tri thức cận lâm sàng rải rác dưới định dạng phức tạp; bộ đọc thông thường trích sai.

1. Dùng bộ phân tích bố cục (layout-aware parsing) để tách khối văn bản, bảng, hình.
2. Bảng → lưu dạng cấu trúc (hàng/cột/ô) và bản markdown; giữ liên kết tới caption và trang nguồn.
3. **Kiểm tra mẫu bằng người** (khởi điểm ~5–10% số bảng, ưu tiên bảng số liệu); báo cáo tỉ lệ ô trích sai. Một con số sai trong bảng xét nghiệm hoặc liều thuốc là rủi ro lâm sàng.
4. Số liệu trích từ bảng gắn cờ `parsed_table` để Stage 7 trích dẫn đúng trang/bảng.
5. Nội dung chỉ có trong hình (không có văn bản) không được dùng làm bằng chứng cho đến khi có caption/mô tả được bác sĩ xác nhận.

### 2.4 Metadata mỗi chunk

`[GIỮ NGUYÊN]` `patient_id, visit_date, note_type, section, local_index`.
`[MỚI]` bổ sung:

| Trường | Giá trị | Mục đích |
|---|---|---|
| `chunk_type` | `findings`, `impression`, `narrative`, `guideline_rec`, `lab`, `table`, … | Phân biệt chức năng; ưu tiên trích dẫn |
| `pathology_class` | `traumatic`, `neoplastic`, `inflammatory`, `unknown` | Stage 4 (soft boost), 5, 9 |
| `anatomy_region` | `lower_limb`, `upper_limb`, `trunk`, `unknown` | Stage 4, 5 |
| `entity_ids` | Danh sách ontology ID đã link | Cầu nối chunk ↔ triple (Stage 4) |
| `source_authority` | `guideline`, `review`, `ehr_case`, `other` | `s_pop` ở Stage 5 |
| `applicability_conditions` | Nhóm tuổi, vị trí, mức độ, chống chỉ định mà khuyến cáo áp dụng (chỉ với guideline) | Đầu vào của `s_appl` ở Stage 5 |
| `evidence_level`, `version`, `published_date` | Mức bằng chứng, phiên bản, ngày công bố | `s_pop`, cờ `stale` |
| `language` | `vi`, `en`, `mixed` | Chọn tokenizer/embedding |
| `text`, `text_seg`, `text_norm` | Văn bản gốc; bản đã tách từ tiếng Việt; bản đã chuẩn hóa alias | Hiển thị; BM25; so khớp |

**Quy tắc gán nhãn:** `pathology_class`/`anatomy_region` lấy từ nhãn chuẩn của hồ sơ nếu có; nếu không thì suy từ entity thuộc layer tương ứng; nếu thiếu hoặc mâu thuẫn → `unknown`. **Không đoán.**

### 2.5 Chuẩn hóa văn bản

1. **Tách từ tiếng Việt** (ví dụ underthesea hoặc VnCoreNLP) trước khi lập chỉ mục BM25 → trường `text_seg`. BM25 trên chữ Việt không tách từ kém rõ rệt.
2. **Chuẩn hóa alias:** thay/ghi chú alias đời thường và viết tắt bằng nhãn chuẩn trong `text_norm`; **giữ nguyên** `text` gốc (không ghi đè).
3. Bản ASCII-folded (bỏ dấu) lưu kèm để BM25 chịu được lỗi gõ dấu.
4. Chuẩn hóa viết tắt thường gặp (XQ, CT, MRI…) theo từ điển do bác sĩ duyệt.

### 2.6 Triển khai

1. `[GIỮ NGUYÊN]` EHR note: hierarchical chunking theo section (HPI, PE, Assessment/Plan).
2. `[GIỮ NGUYÊN]` Radiology report: tách Findings / Impression thành 2 `chunk_type`.
3. `[MỚI]` Thêm metadata `pathology_class`, `anatomy_region`, `entity_ids`, `source_authority`, `applicability_conditions` (mục 2.4).
4. `[GIỮ NGUYÊN]` Global retrieval chạy trước, Local retrieval drill-down sau với sub-query riêng theo note type.
5. `[MỚI]` Tách từ tiếng Việt, chuẩn hóa alias (2.5).
6. `[MỚI]` Parse PDF/bảng và xét nghiệm (2.3).
7. `[MỚI]` Khử trùng nội dung gần trùng (cùng nội dung ở nhiều bản ghi), giữ liên kết nguồn.
8. `[MỚI]` Trích `applicability_conditions` cho chunk guideline **khi nạp** (do LLM trích rồi bác sĩ duyệt mẫu), không để LLM đoán lúc truy vấn.

### 2.7 Nạp dữ liệu vào các kho

OpenSearch (BM25 + filter), Qdrant (vector + payload filter), Neo4j (từ Stage 1), PostgreSQL (provenance, audit). Nạp theo giao dịch logic hoặc có cơ chế đối soát để mọi ID luôn khớp (xem Phần C, hạ tầng ở Stage 4).

### 2.8 Đánh giá riêng Stage 2

Độ chính xác parse bảng (mẫu kiểm tra); tỉ lệ chunk có `pathology_class`/`anatomy_region` ≠ `unknown`; độ chính xác gán metadata (mẫu bác sĩ chấm); độ phủ `applicability_conditions` trên chunk guideline.

---

## STAGE 3 — Red-Flag Screening Gate `[MỚI]`

**Nguồn:** Không có — 100% tự thiết kế, không bài nào trong 5 bài tham khảo có cơ chế này.

**Ý tưởng chính:** Trước khi vào vòng lặp RAG thông thường, lọc ngay các ca có dấu hiệu nguy hiểm cần escalate khẩn.

**Input:** `CaseInput` (tiền sử, cơ chế chấn thương, triệu chứng, tuổi, và báo cáo CĐHA nếu có).
**Output:** `RedFlagResult` = `true` / `false` / `indeterminate` + tiêu chí khớp + trường còn thiếu.

### 3.1 Công thức `[MỚI]`

$$RedFlag = criterion_1 \lor criterion_2 \lor \dots \lor criterion_n$$

Mỗi tiêu chí có **ba trạng thái**: `true` / `false` / `unknown` (khi trường dữ liệu chưa có).

- Có ít nhất một tiêu chí `true` → `RedFlag = true`: escalate ngay, bỏ qua Stage 4–9.
- Không tiêu chí nào `true` nhưng có tiêu chí `unknown` → `RedFlag = indeterminate`: **tiếp tục chạy** Stage 4–9 nhưng gắn cờ `redflag_indeterminate` và đưa danh sách trường còn thiếu vào Missing Information; cờ này **chặn nhánh ANSWER_CLEAN** ở Stage 9.
- Tất cả `false` → `RedFlag = false`.

### 3.2 Tiêu chí pathological fracture screening (`[MỚI]`)

Do 19.3% ca là u bướu trộn với 70.2% trauma:

| # | Tiêu chí | Trường dữ liệu |
|---|---|---|
| C1 | Gãy xương không tương xứng với mức năng lượng chấn thương | `energy_level`, có gãy xương |
| C2 | Đau xuất hiện trước khi gãy | `pain_before_event` |
| C3 | Sụt cân không rõ nguyên nhân kèm đau xương | `unexplained_weight_loss`, đau xương |
| C4 | Tuổi trên 40 với gãy xương không điển hình | `age`, mô tả gãy |

Khớp tiêu chí nào → trả cảnh báo khẩn, đề xuất chuyển khám chuyên khoa u bướu xương ngay.

**Lưu ý bắt buộc:**

- Định nghĩa vận hành của các cụm từ "không tương xứng", "không điển hình" **phải do bác sĩ chuyên khoa chốt** bằng quy tắc rõ ràng; thiết kế này chưa định nghĩa.
- Tiêu chí nên được **đo trên dữ liệu thật** (độ nhạy trên nhóm Neoplastic, tỉ lệ dương tính giả trên nhóm Traumatic) trước khi dùng.

### 3.3 Tiêu chí đề xuất để bác sĩ cân nhắc bổ sung `[MỚI — cần duyệt]`

Các dấu hiệu thường được nhắc tới khi nghi ngờ tổn thương ác tính hoặc bệnh lý khác, **đề xuất để bác sĩ quyết định có đưa vào hay không**, không mặc định kích hoạt:

- Tiền sử ung thư.
- Đau về đêm / đau lúc nghỉ.
- Khối u sờ thấy hoặc sưng tăng dần.
- Tổn thương tiêu xương/hủy xương trong báo cáo CĐHA (nếu có).
- Dấu hiệu nhiễm trùng (sốt, sưng nóng đỏ) để xử lý nhánh Inflammatory/Infectious.

### 3.4 Lưới an toàn thứ hai ở Stage 4

Stage 3 là bộ lọc theo luật nên có thể bỏ sót. Nếu Stage 4 phát hiện tín hiệu u bướu mạnh dù `RedFlag = false`, đặt cờ `late_neoplastic_signal` chuyển xuống Stage 5/9 (chặn ANSWER_CLEAN).

### 3.5 Hành vi

| Kết quả | Hành động |
|---|---|
| `true` | Dừng pipeline; trả Red-Flag Alert + tiêu chí khớp + đề xuất chuyển khám chuyên khoa; ghi log |
| `indeterminate` | Chạy tiếp; cờ `redflag_indeterminate`; thêm các trường còn thiếu vào Missing Information |
| `false` | Chạy tiếp bình thường |

### 3.6 Đánh giá riêng Stage 3

- **Độ nhạy (recall)** phát hiện ca u bướu có nguy cơ gãy xương bệnh lý (đánh giá hồi cứu trên nhóm Neoplastic; **cần xác nhận dataset có nhãn gãy xương bệnh lý hay không**).
- Tỉ lệ dương tính giả trên nhóm Traumatic.
- Tỉ lệ `indeterminate` (phản ánh dữ liệu đầu vào thiếu).
- Ưu tiên độ nhạy: bỏ sót ca ác tính nghiêm trọng hơn dương tính giả.

### 3.7 Mở rộng sang escalation tổng quát (v2)

Giai đoạn 4 cần lớp escalation rộng hơn (rủi ro cao hoặc khẩn cấp ngoài gãy xương bệnh lý). Danh mục tình huống và tiêu chí do bác sĩ chuyên khoa định nghĩa; Stage 3 là điểm mở rộng.


---

## STAGE 4 — Hybrid + Graph-Guided Retrieval (hợp nhất luồng Text và luồng Graph) `[GIỮ NGUYÊN + MỚI, ghép 2 bài]`

**Nguồn:**

- Luồng Text `[GIỮ NGUYÊN]` từ CLI-RAG
- Luồng Graph `[GIỮ NGUYÊN]` từ KnowGuard
- Cách hợp nhất 2 luồng `[MỚI]` — 2 bài gốc không làm chung 1 pipeline

**Ý tưởng chính:** Kết hợp text similarity retrieval và graph relation retrieval để bắt được cả free-text evidence lẫn quan hệ có cấu trúc. Hai luồng chạy **song song**, sau đó hợp nhất qua **đơn vị bằng chứng thống nhất** thay vì phép hợp đơn giản.

**Input:** `CaseInput`, `RedFlagResult`, KG, chunk store.
**Output:** ≤ 8 `EvidenceUnit` + `RetrievalReport`.

### 4.1 Vì sao không dùng phép hợp đơn giản `[MỚI]`

Công thức bản đầu `D_candidate = D_text ∪ T_expand` hợp hai loại đối tượng khác bản chất:

| | Luồng Text | Luồng Graph |
|---|---|---|
| Đơn vị | chunk văn bản | triple (h, r, t) |
| Thang điểm | BM25 / cosine / RRF | trust, số hop, độ phổ biến node |
| Ngữ cảnh | đầy đủ câu chữ | gần như không có |
| Trích dẫn được | có | chỉ khi có nguồn gốc |
| Đưa thẳng vào Stage 5 | được | không |

Hợp trực tiếp gây ra: điểm không so sánh được; trùng lặp (cùng một sự thật xuất hiện dưới dạng chunk và triple); triple trơ trọi không trích dẫn được ở Stage 7.

**Giải pháp ba thành phần:** (1) đơn vị bằng chứng thống nhất `EvidenceUnit`; (2) cầu nối provenance hai chiều chunk ↔ triple; (3) fusion trên **rank** (Weighted RRF) thay vì trên điểm thô, cộng bonus đồng thuận.

### 4.2 Kiến trúc

```
CaseInput
  ↓
[4.6] Query Understanding: entity linking (+ alias) · qtype · hints → QueryCtx
  ↓
  ├── [4.7] TEXT  : Global/Local BM25 + Dense → RRF
  └── [4.8] GRAPH : seed → 1/2-hop → lọc trust → path score      (chạy song song, asyncio)
  ↓
[4.9]  Cross-linking: Graph→Text (lifting) · Text→Graph (support) · Verbalize triple mồ côi
  ↓
[4.10] EvidenceUnit pool (khử trùng theo uid)
  ↓
[4.11] Weighted RRF + bonus đồng thuận + soft boost metadata
  ↓
[4.12] Cross-encoder rerank → MMR → context budget → quota an toàn
  ↓
[4.13] Export → Stage 5 (RetrievalReport)
```

### 4.3 Mô hình dữ liệu

**Chunk** `[GIỮ NGUYÊN metadata CLI-RAG + trường MỚI]` — xem Stage 2, mục 2.4. Ví dụ:

```json
{
  "chunk_id": "C_88421",
  "patient_id": "P_000312", "visit_date": "2025-03-14",
  "note_type": "radiology", "section": "Impression", "local_index": 2,
  "chunk_type": "impression",
  "pathology_class": "traumatic", "anatomy_region": "lower_limb",
  "entity_ids": ["ONT:Femur_Neck", "ONT:Transverse_Fracture"],
  "source_authority": "ehr_case", "language": "vi",
  "text": "...", "text_seg": "...", "text_norm": "..."
}
```

**Triple** `[MỞ RỘNG từ Stage 1]`:

```json
{
  "triple_id": "T_000123",
  "head": "ONT:Femur_Neck", "relation": "has_morphology", "tail": "ONT:Transverse_Fracture",
  "trust_T": 0.87, "reviewed_by_md": false, "review_required": false,
  "source_chunks": ["C_88421", "C_90177"],
  "origin_kind": "extracted",
  "pathology_class": "traumatic", "anatomy_region": "lower_limb",
  "ontology_version": "msk-0.3"
}
```

**QueryCtx:**

```python
@dataclass
class LinkedEntity:
    ont_id: str
    mention: str
    link_score: float          # Score(c,o) = α·sim_lex + β·sim_sem   [GIỮ NGUYÊN Stage 1]
    low_conf: bool
    ambiguous: bool = False
    via_lay_alias: bool = False

@dataclass
class QueryCtx:
    q: str
    case_text: str | None
    entities: list[LinkedEntity]
    neoplastic_entities: set[str]        # ont_id thuộc nhánh Neoplastic
    pathology_hint: str | None           # soft
    anatomy_hint: str | None             # soft
    qtype: str                           # 1 trong 11 loại Question Taxonomy
    qtype_group: str                     # dx | tx | rehab | sym | prev | default
    is_differential: bool
    phase: str                           # P1 | P3
    lang: str
    flags: set[str]
```

**EvidenceUnit:** xem mục 4.10.

### 4.4 Hạ tầng lưu trữ

| Thành phần | Công nghệ gợi ý | Vai trò |
|---|---|---|
| Lexical index | OpenSearch / Elasticsearch | BM25, filter metadata |
| Vector index | Qdrant | Dense retrieval, payload filter |
| Graph store | Neo4j | KG, expansion bằng Cypher |
| Metadata / provenance | PostgreSQL | chunk↔entity↔triple, audit |
| Cache | Redis | cache embedding query, kết quả expansion |
| Embedding | bge-m3 hoặc multilingual-e5 (đa ngữ Việt–Anh) | dense |
| Reranker | bge-reranker-v2-m3 | cross-encoder |
| LLM nhỏ | model nội bộ/API | qtype, viết lại sub-query |

Các công nghệ trên chỉ là gợi ý; thay được bằng thành phần tương đương miễn giữ nguyên hợp đồng dữ liệu. **Embedding và reranker chưa được benchmark trên dữ liệu bệnh viện**; cần so sánh 2–3 ứng viên trên dev set.

**OpenSearch mapping (rút gọn):**

```json
{
  "settings": {"analysis": {"analyzer": {"vi_text": {"type": "custom", "tokenizer": "standard",
      "filter": ["lowercase", "asciifolding_keep_original"]}},
    "filter": {"asciifolding_keep_original": {"type": "asciifolding", "preserve_original": true}}}},
  "mappings": {"properties": {
    "chunk_id": {"type": "keyword"},
    "text_seg": {"type": "text", "analyzer": "vi_text"},
    "text_norm": {"type": "text", "analyzer": "vi_text"},
    "note_type": {"type": "keyword"}, "chunk_type": {"type": "keyword"},
    "pathology_class": {"type": "keyword"}, "anatomy_region": {"type": "keyword"},
    "entity_ids": {"type": "keyword"}, "source_authority": {"type": "keyword"},
    "visit_date": {"type": "date"}, "published_date": {"type": "date"}}}
}
```

**Qdrant:**

```python
client.create_collection(collection_name="msk_chunks",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE))
# payload: chunk_id, note_type, chunk_type, pathology_class, anatomy_region,
#          entity_ids, source_authority
# tạo payload index: note_type, pathology_class, anatomy_region
```

**Neo4j:**

```cypher
CREATE CONSTRAINT ent_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE INDEX rel_trust IF NOT EXISTS FOR ()-[r:REL]-() ON (r.trust_T);
// Mọi quan hệ: (:Entity)-[:REL {type, triple_id, trust_T, reviewed_by_md,
//   review_required, pathology_class, anatomy_region}]->(:Entity)
// Node Entity: {id, label_vi, label_en, layer, degree, aliases...}
// layer ∈ {Anatomy, PathologyClass, DiseaseEntity, Morphology, Pathophysiology, ClinicalPhenotype}
```

**PostgreSQL (provenance và audit):**

```sql
CREATE TABLE chunk_entity (chunk_id TEXT, entity_id TEXT, PRIMARY KEY (chunk_id, entity_id));
CREATE INDEX ON chunk_entity (entity_id);
CREATE TABLE triple_source (triple_id TEXT, chunk_id TEXT, PRIMARY KEY (triple_id, chunk_id));
CREATE INDEX ON triple_source (chunk_id);
CREATE TABLE retrieval_audit (
  run_id UUID PRIMARY KEY, ts TIMESTAMPTZ, query TEXT, qtype TEXT, ctx JSONB,
  text_pool JSONB, graph_pool JSONB, fused JSONB, final JSONB,
  flags TEXT[], latency_ms JSONB, versions JSONB);
```

### 4.5 Điều kiện tiên quyết: provenance chunk ↔ triple

Merge chỉ có nghĩa khi có provenance. Nếu KG đã build mà chưa lưu nguồn, phải chạy lại bước ghi nguồn (Stage 1, mục 1.7.6). Kiểm tra toàn vẹn ở Stage 1, mục 1.10.

### 4.6 Query Understanding `[GIỮ NGUYÊN linking + MỚI qtype/hints]`

**a) Entity linking `[GIỮ NGUYÊN công thức]`**

$$Score(c, o) = \alpha \cdot sim_{lex}(c, o) + \beta \cdot sim_{sem}(c, o), \quad \alpha + \beta = 1$$

- Nhận entity nếu `Score ≥ θ_link` (khởi điểm **0.60**).
- `0.45 ≤ Score < θ_link` → giữ với `low_conf = true`; **không** dùng làm seed graph; vẫn dùng cho mở rộng BM25.
- Dưới 0.45 → bỏ.
- Hai ứng viên chênh < 0.05 → giữ cả hai, gắn `ambiguous`; dùng ngữ cảnh ca để phân giải nếu có.
- `[MỚI]` **So khớp thêm với alias đời thường** (Stage 1, mục 1.6): mention "giòn xương" link được tới `ONT:Osteoporosis` (`via_lay_alias = true`). Alias mơ hồ → giữ nhiều ứng viên.

**b) Question type `[MỚI]`**

Phân loại thành 1 trong 11 loại của Question Taxonomy (C2), bằng LLM nhỏ few-shot; đầu ra JSON có `qtype` và `confidence`. `confidence < 0.5` → profile `default`.

| Nhóm | Loại câu hỏi |
|---|---|
| `dx` | Diagnosis, Differential diagnosis |
| `tx` | Treatment, Surgery, Medication |
| `rehab` | Rehabilitation / Physiotherapy, Prognosis |
| `sym` | Symptoms, Causes, Risk factors |
| `prev` | Prevention `[MỚI]` |
| `default` | còn lại / không chắc |

`is_differential = true` khi qtype là Differential diagnosis.

**c) Hints (soft)**

`pathology_hint` và `anatomy_hint` suy từ entity đã link và ngữ cảnh ca. **Chỉ dùng làm boost** (4.11), **không làm hard filter**. Lý do an toàn: nếu hard filter sai (ví dụ ca u bị phân nhầm là trauma), hệ thống sẽ loại đúng bằng chứng cần cho cảnh báo. Thà nhiễu hơn là mù. Ablation A6 đo chi phí của hard filter.

**d) Mở rộng truy vấn cho luồng Text:** thêm nhãn chuẩn (VN/EN) của entity đã link và alias chuyên môn vào truy vấn BM25, tối đa ~6 từ khoá bổ sung. **Không** thêm vào truy vấn dense (tránh lệch embedding).

### 4.7 Luồng Text `[GIỮ NGUYÊN từ CLI-RAG]`

**Công thức**

$$D_{text} = RRF(BM25(q), Dense(q)), \qquad RRF(d)=\sum_{r}\frac{1}{k + rank_r(d)}$$

**Quy trình**

1. **Global:** BM25 và Dense trên mọi note type, mỗi nhánh top `K_g = 40`, RRF với `k = 60`.
2. Lấy 2 `note_type` xuất hiện nhiều nhất trong top-20 của `D_global`.
3. **Local:** với mỗi note type đó, tạo sub-query `q_t` (viết lại theo đặc thù: `radiology` nhấn mạnh hình thái và vị trí; `guideline` nhấn mạnh chỉ định/khuyến cáo), chạy BM25 + Dense có filter `note_type = t`, top `K_l = 20`.
4. Gộp, khử trùng theo `chunk_id`; **giữ nguyên** `rank_bm25`, `rank_dense`, `rank_text` (lấy rank tốt nhất nếu xuất hiện nhiều lần).
5. Soft boost metadata **không** áp ở bước này (để dành cho fusion, tránh áp hai lần).
6. `[MỚI]` Nếu query chứa entity Neoplastic → tăng `K_g` thêm 50% (ưu tiên recall cho nhóm rủi ro cao).

```python
def text_stream(ctx, k_global=40, k_local=20, rrf_k=60):
    bm25_g  = bm25.search(expand_query(ctx), size=k_global)
    dense_g = dense.search(embed(ctx.q), size=k_global)
    D_global = rrf([bm25_g, dense_g], k=rrf_k)
    top_types = top_note_types(D_global[:20], n=2)
    D_local = []
    for t in top_types:
        q_t = rewrite_for_type(ctx.q, t)
        D_local += rrf([bm25.search(q_t, filter={"note_type": t}, size=k_local),
                        dense.search(embed(q_t), filter={"note_type": t}, size=k_local)], k=rrf_k)
    return dedupe(D_global + D_local)   # giữ rank_bm25, rank_dense, rank_text
```

### 4.8 Luồng Graph `[GIỮ NGUYÊN seed/expansion từ KnowGuard + MỚI scoring]`

**Công thức expansion `[GIỮ NGUYÊN]`**

$$T_{expand} = \{(h, r, t) \in G : h \in E_{query} \ \lor\ t \in E_{query}\}$$

**Seed:** `E_query` = entity có `link_score ≥ θ_link` và `low_conf = false`. Rỗng → luồng Graph trả rỗng, cờ `graph_unavailable`.

**Expansion 1-hop**

```cypher
MATCH (h:Entity)-[r:REL]-(t:Entity)
WHERE h.id IN $seeds
  AND r.type IN $allowed_relations
  AND r.trust_T >= $tau
  AND ( r.pathology_class <> 'neoplastic' OR r.reviewed_by_md = true OR $include_unreviewed = true )
  AND t.degree <= $max_degree
RETURN h.id AS seed, r.triple_id AS triple_id, r.type AS rel,
       startNode(r).id AS head, endNode(r).id AS tail,
       r.trust_T AS trust, r.reviewed_by_md AS reviewed,
       r.review_required AS review_required, t.degree AS tdeg
LIMIT $limit
```

**Expansion 2-hop (chỉ khi cần)**

```cypher
MATCH p = (h:Entity)-[r1:REL]-(m:Entity)-[r2:REL]-(t:Entity)
WHERE h.id IN $seeds
  AND r1.type IN $allowed_relations AND r2.type IN $allowed_relations
  AND r1.trust_T >= $tau AND r2.trust_T >= $tau
  AND m.degree <= $max_degree_mid AND t.id <> h.id
RETURN p LIMIT $limit
```

Tham số khởi điểm: `max_degree = 200`, `max_degree_mid = 120`, `limit = 300` (1-hop), `200` (2-hop).

**Quy tắc số hop `[MỚI]`:** mặc định 1 hop; lên 2 hop khi pool 1-hop có < 5 triple hoặc câu hỏi chẩn đoán phân biệt; **không quá 2 hop** (nhiễu tăng nhanh, khó giải thích).

**Whitelist quan hệ theo qtype `[MỚI]`** (tên quan hệ phải trùng ontology; nếu khác thì sửa bảng này, không sửa code):

| Nhóm | Quan hệ cho phép |
|---|---|
| `dx` | `has_morphology`, `located_in`, `differential_of`, `has_phenotype`, `is_a`, `requires_imaging` |
| `tx` | `treated_by`, `indicated_for`, `contraindicated_in` |
| `rehab` | `has_pathophysiology`, `prognosis_of`, `rehab_for`, `complication_of` |
| `sym` | `has_phenotype`, `caused_by`, `risk_factor_of`, `associated_with` |
| `prev` | `prevented_by`, `risk_factor_of` |
| `default` | hợp của các nhóm trên, trừ `is_a` ở hop 2 |

**Ngưỡng trust theo pathology `[MỚI]`** (nối Stage 1):

| Điều kiện | `τ` | Yêu cầu bổ sung |
|---|---|---|
| Traumatic, Inflammatory | 0.70 | — |
| Neoplastic | 0.85 | `reviewed_by_md = true`; hoặc vào kèm cờ `unreviewed` + phạt điểm |
| `pathology_class = unknown` | 0.80 | — |

Mặc định cho triple Neoplastic **chưa duyệt**: vào pool **kèm cờ `unreviewed`** (để Stage 5 hạ applicability và Stage 9 cảnh báo), thay vì loại hẳn, vì loại hẳn có thể làm mất tín hiệu cần cho cảnh báo. Điều khiển bằng `include_unreviewed_neoplastic`.

**Path score `[MỚI]`**

$$s_{graph}(i) = T_i \times \gamma^{(hop_i - 1)} \times \ell(seed_i) \times \frac{1}{\log(2 + \deg(t_i))}$$

- `T_i`: trust của triple (Stage 1). Triple 2-hop: `T_i = min(T_1, T_2)`.
- `γ = 0.6`: phạt theo hop.
- `ℓ(seed_i)`: `link_score` của seed.
- `1/log(2+deg)`: phạt hub node (ví dụ "Gãy xương" nối rất nhiều thứ).
- Neoplastic chưa duyệt: nhân thêm `0.5`.

Giữ top `N_B = 40` triple theo `s_graph`; gán `rank_graph`.

```python
def path_score(tr, cfg, seed_link_score):
    s = tr.trust_T * (cfg.graph.gamma ** (tr.hop - 1)) * seed_link_score \
        * (1.0 / math.log(2 + tr.tail_degree))
    if tr.pathology_class == "neoplastic" and not tr.reviewed_by_md:
        s *= cfg.graph.unreviewed_penalty
    return s

async def graph_stream(ctx, kg, cfg):
    seeds = [e for e in ctx.entities if not e.low_conf and e.link_score >= cfg.entity_linking.theta_link]
    if not seeds:
        ctx.flags.add("graph_unavailable"); return []
    rels = WHITELIST[ctx.qtype_group]
    triples = await kg.expand(seeds=[s.ont_id for s in seeds], hops=1, rels=rels, cfg=cfg)
    triples = [t for t in triples if t.trust_T >= tau_for(t.pathology_class, cfg)]
    if len(triples) < cfg.graph.min_pool_before_2hop or ctx.is_differential:
        t2 = await kg.expand(seeds=[s.ont_id for s in seeds], hops=2, rels=rels, cfg=cfg)
        triples += [t for t in t2 if t.trust_T >= tau_for(t.pathology_class, cfg)]
    link = {s.ont_id: s.link_score for s in seeds}
    for t in triples:
        t.s_graph = path_score(t, cfg, link.get(t.seed, 0.6))
        if t.pathology_class == "neoplastic" and not t.reviewed_by_md:
            t.flags.add("unreviewed")
    triples = dedupe_by_triple_id(triples)
    triples.sort(key=lambda t: -t.s_graph)
    triples = triples[:cfg.graph.top_n]
    for i, t in enumerate(triples, 1): t.rank_graph = i
    return triples
```

### 4.9 Cross-linking `[MỚI]` — phần cốt lõi của việc hợp nhất

| Phép | Mô tả | Mục đích |
|---|---|---|
| **Graph → Text (lifting)** | Mỗi triple được nâng lên các chunk nguồn qua `source_chunks`; chunk chưa có trong luồng Text vẫn vào pool với `origin = {graph}` | Graph bổ sung những gì Text bỏ sót (chunk không khớp từ khoá/embedding nhưng khớp quan hệ) |
| **Text → Graph (support)** | Chunk Text được gắn các triple có **cả hai đầu** nằm trong `entity_ids(chunk) ∪ E_query` (tối đa 5 triple, ưu tiên trust cao) | Xác nhận bằng cấu trúc; cấp `s_coh` cho Stage 5, nguồn trích KG cho Stage 7 |
| **Verbalize** | Triple không có chunk nguồn (curated/ontology) được chuyển thành câu bằng template → unit `triple_only`, `source_ref = KG:<triple_id>` | Mọi bằng chứng đều trích dẫn được |
| **Khử trùng** | Triple đã được một chunk phủ thì bỏ bản `triple_only` | Không đếm đôi |
| **Phát hiện mâu thuẫn** | Cùng cặp (entity, quan hệ) nhưng giá trị ngược (chỉ định vs chống chỉ định) → cờ `conflict` cho cả hai | Stage 5, 9 |

Yêu cầu **cả hai đầu** ở phép Text → Graph là để tránh gắn triple lạc đề.

**Verbalize template**

```python
TEMPLATES = {
  "has_morphology":     "{head} có hình thái {tail}.",
  "located_in":         "{head} nằm ở {tail}.",
  "differential_of":    "{head} cần phân biệt với {tail}.",
  "treated_by":         "{head} được điều trị bằng {tail}.",
  "indicated_for":      "{head} được chỉ định cho {tail}.",
  "contraindicated_in": "{head} chống chỉ định trong {tail}.",
  "has_phenotype":      "{head} có biểu hiện lâm sàng {tail}.",
  "caused_by":          "{head} do {tail}.",
  "risk_factor_of":     "{head} là yếu tố nguy cơ của {tail}.",
  "prognosis_of":       "{head} liên quan đến tiên lượng {tail}.",
  "rehab_for":          "{head} là phương pháp phục hồi cho {tail}.",
  "prevented_by":       "{head} được phòng ngừa bằng {tail}.",
}
FALLBACK = "{head} — {rel} — {tail}."
```

Bác sĩ nên duyệt template của các quan hệ về điều trị và chống chỉ định, vì câu chữ sai ở đây đi thẳng vào prompt.

### 4.10 EvidenceUnit thống nhất `[MỚI]`

```python
@dataclass
class EvidenceUnit:
    uid: str                          # chunk_id hoặc triple_id
    kind: Literal["chunk", "chunk+triples", "triple_only"]
    text_repr: str                    # dùng để rerank + đưa vào prompt
    source_ref: str                   # "DOC:<chunk_id>" | "KG:<triple_id>"
    attached_triples: list[Triple]
    metadata: dict                    # pathology_class, anatomy_region, note_type, section,
                                      # chunk_type, source_authority, evidence_level,
                                      # applicability_conditions, published_date
    origin: set[str]                  # {"text"} | {"graph"} | {"text","graph"}
    rank_bm25: int | None = None
    rank_dense: int | None = None
    rank_graph: int | None = None
    graph_signal: float = 0.0
    fusion_score: float = 0.0
    rerank_score: float | None = None
    flags: set[str] = field(default_factory=set)
```

Một chunk xuất hiện ở cả hai luồng = **một** unit mang đủ tín hiệu; `kind` cập nhật thành `chunk+triples` khi có `attached_triples`.

### 4.11 Fusion `[MỚI]`

Dùng **Weighted RRF** trên rank, vì điểm BM25, cosine và path score không cùng thang đo:

$$F(u) = \sum_{s \in \{bm25,\, dense,\, graph\}} \frac{w_s(qtype)}{k + rank_s(u)} + \delta \cdot \mathbb{1}[origin(u)=\{text, graph\}] + \mu \cdot meta\_match(u)$$

- `k = 60`; `δ = 0.01` (bonus đồng thuận: được cả hai luồng tìm ra); `μ = 0.005` (soft boost metadata).
- Unit vắng mặt ở một luồng → bỏ số hạng đó (không cộng, không phạt).
- `1/(k+rank)` ≈ 0.0163 ở rank 1 và ≈ 0.0083 ở rank 60; `δ`, `μ` cùng bậc nên thực sự ảnh hưởng thứ hạng. Khi tune, kiểm tra để chúng không áp đảo hoặc vô hiệu.

**`meta_match(u) ∈ [0,1]`**

```
meta_match = 0.5 * comp(u.pathology_class, hint.pathology) + 0.5 * comp(u.anatomy_region, hint.anatomy)
comp(val, hint) = 0.5 nếu hint = None | 0.25 nếu val = unknown | 1.0 nếu khớp | 0.0 nếu khác
```

**Unit chỉ từ Graph chưa có rank text:** tính bù — embed `text_repr` so với embed(q) để xếp `rank_dense`; chấm BM25 cục bộ để xếp `rank_bm25`; gắn cờ `dense_backfilled`. Tránh unit graph bị thiệt thòi chỉ vì không có điểm text.

**Trọng số khởi điểm theo qtype**

| Nhóm | `w_bm25` | `w_dense` | `w_graph` |
|---|---|---|---|
| `dx` | 0.8 | 1.0 | **1.4** |
| `tx` | 1.0 | **1.3** | 0.7 |
| `rehab` | 0.9 | 1.2 | 0.9 |
| `sym` | 1.0 | 1.1 | 1.1 |
| `prev` | 1.0 | 1.2 | 0.9 |
| `default` | 1.0 | 1.0 | 1.0 |

Lý do khởi điểm: chẩn đoán dựa nhiều vào quan hệ có cấu trúc (hình thái, vị trí, phân biệt); điều trị dựa nhiều vào văn bản guideline dài. **Đây là giả thuyết cần kiểm chứng bằng ablation, không phải kết luận.**

**Điều chỉnh động:**

- `|graph_pool| < 5` → nhân `w_bm25`, `w_dense` với 1.2; cờ `kg_sparse`.
- `E_query` chứa entity Neoplastic → nhân `w_graph` với 1.15 `[MỚI]` (giả thuyết graph giúp nhiều nhất ở Neoplastic; kiểm chứng ở C5).

**Xử lý mâu thuẫn:** không tự chọn bên nào; giữ cả hai, cờ `conflict`.

### 4.12 Rerank, đa dạng hoá, quota an toàn `[MỚI]`

1. Lấy top `N_rr = 30` theo `F(u)`.
2. **Cross-encoder rerank** giữa `q` (kèm ngữ cảnh ca rút gọn) và `text_repr`; điểm kết hợp:

$$final(u) = 0.5 \cdot norm(F(u)) + 0.5 \cdot norm(rerank(u))$$

   (`norm` = min–max trong pool top-30.)
3. **MMR** (λ = 0.7) chống trùng ý:

$$MMR = \arg\max_{u \notin S}\left[\lambda \cdot final(u) - (1-\lambda)\max_{v\in S} sim(u,v)\right]$$

4. **Context budget:** tối đa `M = 8` unit; mỗi unit kèm tối đa 3 triple.
5. **Quota đại diện:** nếu graph_pool không rỗng → ≥ 2 unit có nguồn graph; nếu `qtype_group = tx` → ≥ 2 unit `guideline` (nếu tồn tại).
6. **Quota an toàn Neoplastic:** nếu top-30 có unit `pathology_class = neoplastic` thì ≥ 1 unit đó phải nằm trong kết quả cuối (kèm cờ); đặt `late_neoplastic_signal` nếu RedFlag đã `false`.

### 4.13 Export sang Stage 5 và Stage 6

```python
@dataclass
class RetrievalReport:
    units: list[EvidenceUnit]
    flags: set[str]     # graph_unavailable, kg_sparse, conflict, unreviewed_present,
                        # late_neoplastic_signal, no_evidence, stale, ambiguous_entity
    coverage: dict      # entity trong E_query nào có / chưa có bằng chứng
    stats: dict         # kích thước pool, tỉ lệ origin, độ trễ từng pha
```

`coverage` cho phép Gap Analysis (Stage 6) nói cụ thể "chưa có bằng chứng cho entity X". Metadata `pathology_class`, `anatomy_region`, `applicability_conditions`, morphology (từ triple `has_morphology`) chuyển nguyên sang Stage 5 để tính `s_appl`.

**Cách điền công thức KnowGuard ở Stage 5:**

| Thành phần | Lấy từ Stage 4 |
|---|---|
| `s_sim` | điểm cross-encoder đã chuẩn hóa (hoặc cosine dense) |
| `s_rel` | LLM-judge relevance (q, unit), tính ở Stage 5 |
| `s_coh` | $\frac{|\{e \in E_{query}: e \in endpoints(attached\_triples(u))\}|}{|E_{query}|}$ (= 0 nếu `E_query` rỗng) |
| `s_pop` | theo `source_authority`/`evidence_level` (xem Stage 5) |

### 4.14 Trường hợp đặc biệt

| Tình huống | Hành vi |
|---|---|
| Không link được entity nào | Text-only; cờ `graph_unavailable` |
| Một luồng timeout/lỗi | Dùng luồng còn lại; cờ `*_stream_failed`; log cảnh báo |
| Cả hai rỗng | Report rỗng + cờ `no_evidence` → Stage 7 phát Negative Knowledge Assertion |
| Hub node bùng nổ | Cắt `degree > max_degree`; phạt `1/log(2+deg)` |
| Text mâu thuẫn triple | Cờ `conflict` cả hai |
| Triple Neoplastic chưa duyệt | Vào kèm `unreviewed` + phạt; không trình bày như bằng chứng đã xác nhận |
| KG thưa / bệnh hiếm | Tăng `w_bm25`, `w_dense` ×1.2; cờ `kg_sparse` |
| Entity mơ hồ | Giữ cả hai ứng viên, cờ `ambiguous_entity` |
| Bằng chứng cũ (quá hạn theo `published_date`) | Cờ `stale`, hạ `s_pop` |
| Câu hỏi trộn Việt–Anh | Embedding đa ngữ; BM25 dùng `text_seg` và bản ASCII-folded |
| Chạy lại ở Stage 6 | Cộng dồn `E_query`, không bỏ seed vòng trước |
| `phase = P1`, chưa có CĐHA | Truy xuất theo triệu chứng/vị trí; không báo lỗi vì thiếu report |

### 4.15 Cấu hình (`config/stage4.yaml`)

```yaml
entity_linking: {theta_link: 0.60, theta_low: 0.45, ambiguity_margin: 0.05}
text:
  rrf_k: 60
  k_global: 40
  k_local: 20
  local_note_types: 2
  neoplastic_recall_boost: 1.5
graph:
  default_hops: 1
  max_hops: 2
  min_pool_before_2hop: 5
  max_degree: 200
  max_degree_mid: 120
  limit_1hop: 300
  limit_2hop: 200
  top_n: 40
  gamma: 0.6
  tau: {traumatic: 0.70, inflammatory: 0.70, neoplastic: 0.85, unknown: 0.80}
  include_unreviewed_neoplastic: true
  unreviewed_penalty: 0.5
fusion:
  k: 60
  delta: 0.01
  mu: 0.005
  weights:
    dx:      {bm25: 0.8, dense: 1.0, graph: 1.4}
    tx:      {bm25: 1.0, dense: 1.3, graph: 0.7}
    rehab:   {bm25: 0.9, dense: 1.2, graph: 0.9}
    sym:     {bm25: 1.0, dense: 1.1, graph: 1.1}
    prev:    {bm25: 1.0, dense: 1.2, graph: 0.9}
    default: {bm25: 1.0, dense: 1.0, graph: 1.0}
  sparse_kg_threshold: 5
  sparse_kg_text_mult: 1.2
  neoplastic_graph_mult: 1.15
rerank: {n_candidates: 30, alpha_fusion: 0.5, mmr_lambda: 0.7, max_units: 8,
         max_triples_per_unit: 3, min_graph_units: 2, min_guideline_units_for_tx: 2}
safety: {keep_one_neoplastic_unit: true, hint_is_soft_only: true}
latency: {budget_ms_total: 3000, budget_ms_text: 1200, budget_ms_graph: 1000}
```

**Quy trình tune:** cố định dev set (C6), không tune trên test set; tune theo thứ tự `theta_link` → `tau` → `gamma` → `weights` → `delta`/`mu` → `mmr_lambda`; mỗi lần đổi một nhóm; mục tiêu tối ưu là **Recall@8 trên Neoplastic** với ràng buộc không giảm quá 2 điểm MRR ở Traumatic (không tối ưu chỉ điểm trung bình); dùng grid search nhỏ hoặc Bayesian cho nhóm `weights` rồi **kiểm lại bằng đánh giá của bác sĩ**.

### 4.16 Mã nguồn tham chiếu (chưa kiểm thử)

Cấu trúc thư mục:

```
stage4/
  config.py  models.py  understand.py  text_stream.py  graph_stream.py
  crosslink.py  fusion.py  rerank.py  verbalize.py  export.py  audit.py  pipeline.py
```

**`fusion.py`**

```python
import math

def weighted_rrf(u, weights, k=60):
    s = 0.0
    if u.rank_bm25  is not None: s += weights["bm25"]  / (k + u.rank_bm25)
    if u.rank_dense is not None: s += weights["dense"] / (k + u.rank_dense)
    if u.rank_graph is not None: s += weights["graph"] / (k + u.rank_graph)
    return s

def meta_match(u, ctx):
    def comp(val, hint):
        if hint is None: return 0.5
        if val in (None, "unknown"): return 0.25
        return 1.0 if val == hint else 0.0
    return 0.5 * comp(u.metadata.get("pathology_class"), ctx.pathology_hint) \
         + 0.5 * comp(u.metadata.get("anatomy_region"),  ctx.anatomy_hint)

def effective_weights(cfg, ctx, graph_pool_size):
    w = dict(cfg.fusion.weights.get(ctx.qtype_group, cfg.fusion.weights["default"]))
    if graph_pool_size < cfg.fusion.sparse_kg_threshold:
        w["bm25"]  *= cfg.fusion.sparse_kg_text_mult
        w["dense"] *= cfg.fusion.sparse_kg_text_mult
        ctx.flags.add("kg_sparse")
    if ctx.neoplastic_entities:
        w["graph"] *= cfg.fusion.neoplastic_graph_mult
    return w

def fuse(units, ctx, cfg, graph_pool_size):
    w = effective_weights(cfg, ctx, graph_pool_size)
    for u in units:
        agree = 1.0 if u.origin == {"text", "graph"} else 0.0
        u.fusion_score = (weighted_rrf(u, w, cfg.fusion.k)
                          + cfg.fusion.delta * agree
                          + cfg.fusion.mu * meta_match(u, ctx))
    return sorted(units, key=lambda x: -x.fusion_score)
```

**`crosslink.py`**

```python
def build_units(text_pool, graph_pool, ctx, kg, store, cfg):
    units = {}
    for c in text_pool:                                           # (a) text -> units
        units[c.chunk_id] = EvidenceUnit(
            uid=c.chunk_id, kind="chunk", text_repr=c.text,
            source_ref=f"DOC:{c.chunk_id}", attached_triples=[],
            metadata=c.metadata, origin={"text"},
            rank_bm25=c.rank_bm25, rank_dense=c.rank_dense)

    orphans = []
    for tr in graph_pool:                                         # (b) graph -> text (lifting)
        if not tr.source_chunks:
            orphans.append(tr); continue
        for cid in tr.source_chunks:
            u = units.get(cid) or store.make_unit_from_chunk(cid)
            u.attached_triples.append(tr)
            u.graph_signal = max(u.graph_signal, tr.s_graph)
            u.origin.add("graph")
            u.rank_graph = min(u.rank_graph or 10**9, tr.rank_graph)
            if "unreviewed" in tr.flags: u.flags.add("unreviewed")
            units[cid] = u

    E = {e.ont_id for e in ctx.entities}                          # (c) text -> graph (support)
    for u in list(units.values()):
        if u.kind == "triple_only": continue
        ents = set(u.metadata.get("entity_ids", [])) | E
        cand = [t for t in kg.triples_among(ents)
                if t.trust_T >= tau_for(t.pathology_class, cfg)]
        cand.sort(key=lambda t: -t.trust_T)
        have = {t.triple_id for t in u.attached_triples}
        for t in cand[:5]:
            if t.triple_id not in have: u.attached_triples.append(t)
        if u.attached_triples: u.kind = "chunk+triples"

    covered = {t.triple_id for u in units.values() for t in u.attached_triples}   # (d) orphans
    for tr in orphans:
        if tr.triple_id in covered: continue
        units[tr.triple_id] = EvidenceUnit(
            uid=tr.triple_id, kind="triple_only", text_repr=verbalize(tr, kg.label),
            source_ref=f"KG:{tr.triple_id}", attached_triples=[tr],
            metadata={"pathology_class": tr.pathology_class,
                      "anatomy_region": tr.anatomy_region, "source_authority": "kg"},
            origin={"graph"}, rank_graph=tr.rank_graph, graph_signal=tr.s_graph)

    detect_conflicts(units.values())          # đặt cờ "conflict"
    backfill_text_ranks(units.values(), ctx)  # cờ "dense_backfilled"
    return list(units.values())
```

**`rerank.py`**

```python
import numpy as np
def minmax(x):
    x = np.asarray(x, float); return (x - x.min()) / (x.max() - x.min() + 1e-9)

def rerank_mmr(ctx, ranked, cfg, cross_encoder, embed):
    top = ranked[:cfg.rerank.n_candidates]
    # [A1: Thống nhất query kèm ngữ cảnh ca rút gọn]
    q_ctx = f"{ctx.q} [Bệnh nhân: {ctx.patient.get('age', '')} tuổi, {ctx.patient.get('sex', '')}, tiền sử: {ctx.patient.get('history', '')}, chẩn đoán/triệu chứng: {ctx.presentation.get('chief_complaint', '')}]" if ctx.patient else ctx.q
    rr = cross_encoder.score([(q_ctx, u.text_repr) for u in top])
    f, r = minmax([u.fusion_score for u in top]), minmax(rr)
    for u, fi, ri, raw in zip(top, f, r, rr):
        u.rerank_score = float(raw)
        u.final = cfg.rerank.alpha_fusion * fi + (1 - cfg.rerank.alpha_fusion) * ri
    vecs = embed([u.text_repr for u in top])
    selected, remaining, lam = [], list(range(len(top))), cfg.rerank.mmr_lambda
    while remaining and len(selected) < cfg.rerank.max_units * 2:
        def mmr(i):
            div = max((cos(vecs[i], vecs[j]) for j in selected), default=0.0)
            return lam * top[i].final - (1 - lam) * div
        best = max(remaining, key=mmr); selected.append(best); remaining.remove(best)
    return enforce_quotas([top[i] for i in selected], top, ctx, cfg)

def enforce_quotas(chosen, pool, ctx, cfg):
    M = cfg.rerank.max_units
    out = chosen[:M]
    has = lambda pred, lst: sum(1 for u in lst if pred(u))
    need = cfg.rerank.min_graph_units - has(lambda u: "graph" in u.origin, out)
    if need > 0:
        out = swap_in(out, [u for u in pool if "graph" in u.origin and u not in out][:need], M)
    if ctx.qtype_group == "tx":
        g = lambda u: u.metadata.get("source_authority") == "guideline"
        need = cfg.rerank.min_guideline_units_for_tx - has(g, out)
        if need > 0: out = swap_in(out, [u for u in pool if g(u) and u not in out][:need], M)
    if cfg.safety.keep_one_neoplastic_unit:
        neo = lambda u: u.metadata.get("pathology_class") == "neoplastic"
        if not has(neo, out):
            cand = [u for u in pool if neo(u)]
            if cand:
                out = swap_in(out, cand[:1], M); ctx.flags.add("late_neoplastic_signal")
    return out[:M]
```

`swap_in(out, extra, M)`: thêm `extra`; nếu vượt `M` thì loại unit có `final` thấp nhất **không** thuộc nhóm đang được quota bảo vệ.

**`pipeline.py`**

```python
import asyncio, time

async def retrieve(case, cfg, deps) -> RetrievalReport:
    t0 = time.perf_counter()
    ctx = await understand(case, cfg, deps)
    text_pool, graph_pool = await asyncio.gather(
        asyncio.wait_for(text_stream(ctx, cfg, deps), cfg.latency.budget_ms_text/1000),
        asyncio.wait_for(graph_stream(ctx, deps.kg, cfg), cfg.latency.budget_ms_graph/1000),
        return_exceptions=True)
    if isinstance(text_pool, Exception):  ctx.flags.add("text_stream_failed");  text_pool = []
    if isinstance(graph_pool, Exception): ctx.flags.add("graph_stream_failed"); graph_pool = []
    if not text_pool and not graph_pool:
        return RetrievalReport(units=[], flags=ctx.flags | {"no_evidence"}, coverage={}, stats={})
    units  = build_units(text_pool, graph_pool, ctx, deps.kg, deps.store, cfg)
    ranked = fuse(units, ctx, cfg, graph_pool_size=len(graph_pool))
    final  = rerank_mmr(ctx, ranked, cfg, deps.cross_encoder, deps.embed)
    report = build_report(final, ctx, graph_pool, text_pool,
                          latency_ms=(time.perf_counter()-t0)*1000)
    await audit(ctx, text_pool, graph_pool, ranked, final, report)
    return report
```

Các hàm phụ cần viết theo hạ tầng thực tế: `dedupe`, `dedupe_by_triple_id`, `top_note_types`, `rewrite_for_type`, `expand_query`, `tau_for`, `swap_in`, `detect_conflicts`, `backfill_text_ranks`, `build_report`, `cos`, `understand`.

### 4.17 Ablation riêng của Stage 4 `[MỚI]`

| Mã | Cấu hình |
|---|---|
| A0 | Text-only (BM25 + Dense, RRF) `[baseline GIỮ NGUYÊN]` |
| A1 | Graph-only (qua lifting để so sánh được) |
| A2 | Hợp đơn giản (không cross-link, không fusion chuẩn hóa) — đúng công thức bản đầu |
| A3 | Cross-link + RRF đều trọng số (w = 1) |
| A4 | Cross-link + Weighted RRF theo qtype + bonus đồng thuận + meta boost **(đề xuất)** |
| A5 | A4 bỏ cross-encoder/MMR |
| A6 | A4 nhưng hint dùng làm hard filter |

**Giả thuyết cần kiểm chứng (chưa phải kết luận):** H1 A4 > A0 về Recall@8 ở Neoplastic và Differential diagnosis; H2 A4 ≥ A3 > A2; H3 A6 < A4 ở Neoplastic (hard filter gây hại); H4 bonus đồng thuận làm tăng Evidence Precision. Kết quả không ủng hộ giả thuyết vẫn là kết quả có giá trị; báo cáo trung thực. Dùng bootstrap (CI 95%) vì nhóm Neoplastic nhỏ.

### 4.18 Hiệu năng và vận hành riêng Stage 4

Ngân sách độ trễ khởi điểm: link + qtype ≤ 300 ms · Text ≤ 1200 ms · Graph ≤ 1000 ms (song song) · cross-link + fusion ≤ 200 ms · rerank + MMR ≤ 500 ms; mục tiêu p95 ≤ 3 s trước khi vào LLM. Tối ưu: cache embedding query và kết quả expansion theo `(seed, qtype, hops)`; tính trước `degree` và inverted index `entity → chunk_ids`; batch hoá cross-encoder; index trên `trust_T`.

### 4.19 Rủi ro riêng Stage 4

1. Chất lượng entity linking quyết định chất lượng luồng Graph (đo Entity Linking F1 riêng).
2. Provenance không đầy đủ làm giảm lifting; nhiều triple mồ côi → phụ thuộc verbalize (chất lượng thấp hơn chunk gốc).
3. Weighted RRF theo qtype là giả thuyết chưa kiểm chứng.
4. Sai lệch gán nhãn `pathology_class` ảnh hưởng `meta_match` và `tau` (vì vậy dùng soft boost và nhãn `unknown`).
5. Ghép CLI-RAG và KnowGuard trong một pipeline là thiết kế riêng của bạn, không có kết quả công bố cho chính tổ hợp này.

---

## STAGE 5 — Evidence Evaluation: Relevance + Applicability `[GIỮ NGUYÊN + MỚI]`

**Nguồn:**

- Relevance `[GIỮ NGUYÊN]` từ KnowGuard
- Applicability `[MỚI]` — hoàn toàn tự thiết kế, không có trong 5 bài tham khảo

**Ý tưởng chính:**

- `[GIỮ NGUYÊN]` Relevance: evidence có liên quan đến câu hỏi không.
- `[MỚI]` Applicability: evidence đúng nói chung nhưng có áp dụng được cho **bệnh nhân cụ thể này** không — khoảng trống mà cả 5 bài đều không giải quyết.
- Phân biệt rõ ba khái niệm: **Relevance** (Stage 5) ≠ **Applicability** (Stage 5) ≠ **Sufficiency** (Stage 6).

**Input:** `RetrievalReport` (EvidenceUnit + cờ), `CaseInput`.
**Output:** với mỗi unit: `p_final`, `s_appl`, mức `Applicable / Partial / NotApplicable`, danh sách **mã lý do**; nhãn tổng hợp cho Stage 6 và 9.

### 5.1 Công thức

`[GIỮ NGUYÊN]` Relevance score (công thức KnowGuard):

$$p_{final} = (w_{sim} \cdot s_{sim} + w_{rel} \cdot s_{rel} + w_{coh} \cdot s_{coh}) \times s_{pop}$$

`[MỚI]` Applicability score:

$$s_{appl} = match\_anatomy \times match\_pathology\_class \times match\_severity$$

Phân loại 3 mức `[MỚI]`: Applicable, Partial, NotApplicable (quy tắc ở 5.3).

### 5.2 Cách điền các thành phần của `p_final` `[MỞ RỘNG — diễn giải triển khai]`

Công thức là nguyên bản; **cách hiện thực hóa từng thành phần dưới đây là diễn giải của thiết kế này**, cần đối chiếu với định nghĩa trong bài gốc khi triển khai.

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| `s_sim` | điểm cross-encoder đã chuẩn hóa [0,1] (hoặc cosine dense) | Từ Stage 4 |
| `s_rel` | LLM-judge relevance (q, unit) ∈ [0,1] | Prompt ở Phụ lục F3; judge khác model sinh ở Stage 7 |
| `s_coh` | tỉ lệ entity trong `E_query` được nối bởi `attached_triples` của unit | Tín hiệu cấu trúc từ Graph (4.13) |
| `s_pop` | độ mạnh nguồn | Bảng dưới |
| `w_sim, w_rel, w_coh` | khởi điểm 0.3 / 0.5 / 0.2 | Tune bằng dev set |

`s_pop` (giá trị khởi điểm): guideline 1.0 · KG curated 0.9 · review 0.85 · KG extracted 0.7 · ehr_case 0.6 · other 0.5; điều chỉnh theo `evidence_level`; cờ `stale` nhân 0.8.

### 5.3 Kiểm tra applicability — quy tắc `[MỚI]`

Bệnh nhân (từ `CaseInput`) so với điều kiện của evidence (từ metadata chunk, `applicability_conditions`, triple `has_morphology`/`contraindicated_in`).

| Thành phần | Cách tính |
|---|---|
| `match_anatomy` | 1: vùng của evidence bao trùm vị trí tổn thương (hoặc evidence không đặc hiệu vùng) · 0.5: cùng vùng lớn khác vùng nhỏ, hoặc evidence/bệnh nhân `unknown` · 0: khác vùng lớn |
| `match_pathology_class` | 1: trùng · 0: khác · 0.5: một bên `unknown` |
| `match_severity` | 1: mức độ nặng/morphology của bệnh nhân nằm trong phạm vi evidence áp dụng · 0.5: không rõ/mơ hồ · 0: ngoài phạm vi |
| **Kiểm tra cứng (hard checks)** | Tuổi ngoài phạm vi (`AGE_OUT_OF_SCOPE`); bệnh nền/thuốc đang dùng chống chỉ định (`CONTRAINDICATED`) → **NotApplicable** bất kể tích số |

**Phân loại mức:**

| Mức | Điều kiện |
|---|---|
| **NotApplicable** | Có thành phần = 0, **hoặc** vi phạm hard check |
| **Applicable** | Cả 3 thành phần = 1, hard check đạt, và không có cờ chặn (`conflict`, `unreviewed`, `stale` nặng) |
| **Partial** | Còn lại (có thành phần 0.5, hoặc có cờ chặn) |

`s_appl` (tích) giữ lại làm điểm liên tục để xếp hạng và giải thích. Phép nhân làm một thành phần = 0 kéo tất cả về 0 — hợp lý cho an toàn; giá trị trung tính 0.5 cho `unknown` nhằm tránh biến "thiếu thông tin" thành "không áp dụng được".

### 5.4 Quy tắc nghiêm ngặt hơn cho Neoplastic `[MỚI]`

- **Applicable** chỉ khi `match_pathology_class = 1` **và** `match_anatomy = 1` **và** mọi triple dùng đều `reviewed_by_md = true`.
- **Partial** cần `match_pathology_class = 1` và `match_anatomy ≥ 0.5`; không đạt → NotApplicable.
- Evidence kèm cờ `unreviewed` → tối đa **Partial**.
- Bệnh nhân `pathology_class = unknown` nhưng evidence Neoplastic → tối đa Partial kèm cảnh báo.

### 5.5 Ảnh hưởng của cờ từ Stage 4 `[MỚI]`

| Cờ | Tác động ở Stage 5 |
|---|---|
| `unreviewed` | Cap Partial (Neoplastic); hạ `p_final` |
| `conflict` | Hạ điểm cả hai bên; ghi mã `CONFLICT`; không Applicable |
| `stale` | Hạ `s_pop` ×0.8 |
| `kg_sparse` | Chỉ thông tin, không hạ điểm |
| `late_neoplastic_signal` | Chuyển nguyên xuống Stage 9 |
| Metadata `unknown` | Applicability tối đa Partial (xem nguyên tắc A7-8) |

### 5.6 Kiểm tra thuốc – bệnh nền đa bước `[MỚI — cần nguồn dữ liệu]`

Khoảng trống Giai đoạn 3: suy luận đa bước đối chiếu tác dụng phụ/chống chỉ định thuốc với bệnh nền.

1. Trích thuốc đang dùng và bệnh nền từ `CaseInput.patient`.
2. Truy xuất thông tin thuốc (chống chỉ định, tác dụng phụ, thận trọng) từ nguồn thuốc đã xác định.
3. Đối chiếu với bệnh nền, tuổi; nếu có xung đột → `CONTRAINDICATED` kèm trích dẫn nguồn thuốc.
4. Kết quả đi vào hard check ở 5.3.

**Điều kiện tiên quyết:** cần một **nguồn thông tin thuốc đã được phê duyệt** (chưa có; xem C1). Thiếu nguồn thì bước này không bật, và Stage 9 phải ghi chú "chưa kiểm tra tương tác thuốc – bệnh nền" khi qtype là `tx` Medication.

### 5.7 Mã lý do (reason codes)

`ANAT_MISMATCH`, `ANAT_PARTIAL`, `PATH_MISMATCH`, `PATH_UNKNOWN`, `SEV_OUT_OF_SCOPE`, `SEV_UNKNOWN`, `AGE_OUT_OF_SCOPE`, `CONTRAINDICATED`, `UNREVIEWED`, `CONFLICT`, `STALE`, `UNKNOWN_PATIENT_FIELD`. Dùng cho giải thích (XAI), Gap Analysis (Stage 6) và cảnh báo (Stage 9).

### 5.8 Output mỗi unit

```json
{
  "uid": "C_20011", "source_ref": "DOC:C_20011",
  "p_final": 0.71,
  "s_appl": 0.5,
  "applicability": "Partial",
  "reason_codes": ["SEV_UNKNOWN", "UNREVIEWED"],
  "missing_patient_fields": ["severity"],
  "flags": ["unreviewed"]
}
```

`missing_patient_fields` cho Stage 6 biết thiếu **thông tin bệnh nhân** nào làm applicability chưa chắc.

### 5.9 Mã tham chiếu

```python
LEVEL_ORDER = {"NotApplicable": 0, "Partial": 1, "Applicable": 2}

def appl_level(unit, case, cfg):
    reasons = []
    ma = match_anatomy(unit, case, reasons)          # 1 / .5 / 0
    mp = match_pathology(unit, case, reasons)
    ms = match_severity(unit, case, reasons)
    hard_fail = hard_checks(unit, case, reasons)     # AGE_OUT_OF_SCOPE, CONTRAINDICATED
    s_appl = ma * mp * ms
    neo = (case.pathology == "neoplastic") or (unit.metadata.get("pathology_class") == "neoplastic")

    if hard_fail or min(ma, mp, ms) == 0:
        level = "NotApplicable"
    elif ma == mp == ms == 1 and not (unit.flags & {"conflict", "unreviewed"}):
        level = "Applicable"
    else:
        level = "Partial"

    if neo:
        reviewed = all(t.reviewed_by_md for t in unit.attached_triples) if unit.attached_triples else True
        if level == "Applicable" and not (mp == 1 and ma == 1 and reviewed): level = "Partial"
        if level == "Partial" and not (mp == 1 and ma >= 0.5): level = "NotApplicable"
        if "unreviewed" in unit.flags and level == "Applicable": level = "Partial"
    return level, s_appl, reasons
```

### 5.10 Triển khai

1. `[GIỮ NGUYÊN]` Relevance scoring dùng nguyên công thức KnowGuard.
2. `[MỚI]` Applicability kiểm tra riêng (5.3): anatomy, pathology_class, morphology/mức độ nặng, tuổi, bệnh nền/thuốc.
3. `[MỚI]` Ngưỡng nghiêm ngặt hơn cho Neoplastic (5.4).
4. `[MỚI]` Cờ Stage 4 tác động điểm (5.5).
5. `[MỚI]` Kết quả Stage 5 là **input bắt buộc** cho Stage 6 và Stage 9 — KnowGuard gốc không có bước nối này.
6. `[MỚI]` Khi mô hình khuyến cáo guideline có `applicability_conditions` cấu trúc (Stage 2, 2.6.8), dùng điều kiện đó để so sánh theo luật; chỉ dùng LLM khi điều kiện chỉ có dạng văn bản tự do, và gắn cờ `llm_applicability`.

### 5.11 Đánh giá riêng Stage 5

Gold label applicability do ≥ 2 bác sĩ gán cho cặp (ngữ cảnh bệnh nhân, evidence), có lý do; đo accuracy, macro-F1 và **ma trận nhầm lẫn**; báo riêng **tỉ lệ NotApplicable bị phân thành Applicable** (lỗi nguy hiểm nhất); độ đồng thuận giữa bác sĩ (Cohen's κ); **counterfactual sensitivity** (C4).

---

## STAGE 6 — Iterative Retrieval-Verification `[GIỮ NGUYÊN + MỞ RỘNG]`

**Nguồn `[GIỮ NGUYÊN]`:** MedTrust-RAG.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Verifier agent kiểm tra evidence pool đã đủ chưa; nếu thiếu, phân tích cụ thể đang thiếu gì (Medical Gap Analysis) rồi tinh chỉnh truy vấn và lặp lại, thay vì retrieve lại từ đầu.

**Input:** evidence pool + `p_final`, `s_appl`, cờ, `coverage`.
**Output:** pool đã xác minh; `GapAnalysis` có cấu trúc; quyết định `retrieve_again | ask_clinician | stop`.

### 6.1 Công thức `[GIỮ NGUYÊN]`

$$q_{t+1} = Augment(q, GapAnalysis_t), \qquad D_{t+1} = Retrieve(q_{t+1})$$

Lặp đến khi verifier xác nhận hợp lệ, hoặc đạt $T_{max} = 3$.

### 6.2 Tiêu chí đủ (sufficiency) `[MỚI]`

Evidence pool được coi là **đủ** khi, với mỗi yếu tố bắt buộc của loại câu hỏi (6.3):

- có ít nhất 1 unit với `s_rel ≥ θ_rel` (khởi điểm 0.6) **và** applicability ≥ Partial;
- câu hỏi `tx` có ≥ 1 unit guideline;
- không còn `conflict` chưa được ghi nhận.

### 6.3 Danh mục yếu tố bắt buộc theo loại câu hỏi `[MỚI — cần bác sĩ duyệt]`

Dùng để kiểm tra **bỏ sót thông tin quan trọng** (một trong bốn dạng ảo giác nguy hiểm):

| Loại | Yếu tố bắt buộc (đề xuất) |
|---|---|
| `dx` | Các chẩn đoán ứng viên; dấu hiệu phân biệt then chốt; **kiểm tra khả năng gãy xương bệnh lý**; thông tin/cận lâm sàng còn thiếu để phân biệt |
| `tx` | Các lựa chọn điều trị; chỉ định và **chống chỉ định cho bệnh nhân này**; nguy cơ/biến chứng; nhu cầu theo dõi |
| `rehab` | Mốc thời gian; hạn chế vận động; yếu tố tiên lượng; dấu hiệu cảnh báo cần tái khám |
| `sym` | Các nguyên nhân/yếu tố nguy cơ chính; dấu hiệu cảnh báo |
| `prev` | Yếu tố nguy cơ có thể thay đổi; biện pháp phòng ngừa; nhóm đối tượng áp dụng |

### 6.4 Gap Analysis — hai loại thiếu `[MỞ RỘNG]`

| Loại | Ví dụ | Xử lý |
|---|---|---|
| **Relevance gap** (thiếu bằng chứng) `[GIỮ NGUYÊN]` | Chưa tìm được guideline đúng bệnh; entity X chưa có bằng chứng (dùng `coverage` của Stage 4) | `q_{t+1}` được augment → quay lại Stage 4 |
| **Applicability gap** (thiếu thông tin bệnh nhân) `[MỚI]` | Thiếu mức độ nặng, vị trí cụ thể, tuổi, bệnh nền, thuốc | **Không** retrieve lại (vô ích); chuyển thành danh sách thông tin cần hỏi → nhánh ASK_MORE ở Stage 9 |
| **Conflict** `[MỚI]` | Chunk A và triple B ngược nhau | Ghi nhận; chuyển Stage 7 trình bày cả hai, Stage 9 cân nhắc |

### 6.5 Định tuyến sau mỗi vòng

```
if sufficient:                       → stop (sang Stage 7)
elif has relevance_gaps and t < T_max and tiến triển:  → retrieve_again
elif has applicability_gaps:         → ask_clinician (chuyển Stage 9 ASK_MORE)
else:                                → stop (không đủ; sang Stage 9 với cờ insufficient)
```

**Điều kiện dừng sớm "không tiến triển":** nếu vòng mới không thêm unit nào có `s_rel ≥ θ_rel` so với vòng trước → dừng, tránh lặp vô ích.

### 6.6 Quy tắc lặp `[MỚI]`

1. **Cộng dồn** `E_query` từ các vòng trước (không bỏ seed cũ); gộp unit mới với pool cũ, khử trùng theo `uid`.
2. Chỉ ghi lại phần chênh lệch trong audit để tái dựng được từng vòng.
3. `T_max = 3` `[GIỮ NGUYÊN]`.

### 6.7 Verifier output (JSON)

```json
{
  "sufficient": false,
  "round": 1,
  "relevance_gaps": [{"entity": "ONT:...", "need": "khuyến cáo điều trị cho ..."}],
  "applicability_gaps": [{"field": "severity", "why": "guideline phân tầng theo mức độ nặng"}],
  "conflicts": [{"a": "DOC:C_1", "b": "KG:T_9", "topic": "chỉ định ..."}],
  "action": "retrieve_again | ask_clinician | stop",
  "augment_query": "..."
}
```

### 6.8 Triển khai

1. `[MỞ RỘNG]` Verifier nhận evidence pool từ Stage 4–5 gồm **cả relevance VÀ applicability** — bài gốc chỉ có relevance/sufficiency.
2. `[MỞ RỘNG]` Gap Analysis phân biệt 2 loại thiếu (6.4).
3. `[MỚI]` Gap Analysis dùng `coverage` để nêu đích danh entity chưa có bằng chứng.
4. `[MỚI]` Danh mục yếu tố bắt buộc (6.3) để phát hiện bỏ sót.
5. `[GIỮ NGUYÊN]` T_max = 3.

### 6.9 Đánh giá riêng Stage 6

Tỉ lệ ca được cải thiện sau mỗi vòng (Recall@8, độ đủ); tỉ lệ dừng do "không tiến triển"; độ chính xác của phân loại hai loại thiếu (bác sĩ chấm mẫu); tỉ lệ bỏ sót yếu tố bắt buộc (bác sĩ chấm).

---

## STAGE 7 — Citation-Aware, Applicability-Conditioned Generation `[MỞ RỘNG]`

**Nguồn gốc `[GIỮ NGUYÊN]`:** MedTrust-RAG.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Mọi câu trả lời bắt buộc gắn nguồn trích dẫn; nếu không đủ bằng chứng thì phát ra tuyên bố từ chối có cấu trúc.

**Input:** evidence pool đã xác minh (kèm `applicability`, cờ), `GapAnalysis`, `qtype`.
**Output:** câu trả lời gồm các **statement** mỗi statement gắn trích dẫn; hoặc Negative Knowledge Assertion.

### 7.1 Công thức `[GIỮ NGUYÊN]`

$$Answer = statement_1[Doc_1] + statement_2[Doc_2] + \dots$$

Nếu evidence không đủ → **Negative Knowledge Assertion**.

### 7.2 Quy tắc sinh

1. `[MỚI]` Khóa trích dẫn `[Doc_i]` lấy từ `source_ref` (`DOC:<chunk_id>` hoặc `KG:<triple_id>`) → mọi bằng chứng đều trích dẫn được, kể cả triple.
2. Mỗi statement chứa **một** khẳng định chính và trích dẫn đúng unit hỗ trợ khẳng định đó. Không đưa kiến thức ngoài pool.
3. Trích bảng/số liệu từ PDF phải kèm trang/bảng nguồn (cờ `parsed_table`).
4. `[MỚI]` **Điều kiện hóa theo applicability** (hiện thực hóa "adapt" trong câu hỏi nghiên cứu cốt lõi):

| Mức của evidence | Cách dùng trong câu trả lời |
|---|---|
| Applicable | Dùng làm cơ sở cho khẳng định chính |
| Partial | Dùng với **điều kiện nêu rõ** ("chỉ khi …", "chưa rõ vì thiếu …") trong mục Lưu ý áp dụng |
| NotApplicable | **Không** dùng làm cơ sở; nếu liên quan thì nêu ngắn gọn "bằng chứng X không áp dụng vì …" để bác sĩ biết vì sao bị loại |

5. `[MỚI]` Cờ trong evidence phải được thể hiện: `unreviewed` → "chưa được bác sĩ chuyên khoa xác nhận"; `conflict` → trình bày **cả hai** phía; `stale` → nêu năm/phiên bản; `redflag_indeterminate` → nêu trường chưa biết.
6. `[MỚI]` Khi `RetrievalReport` có `no_evidence` hoặc Stage 6 kết luận không đủ → phát Negative Knowledge Assertion:

```
Không đủ bằng chứng để trả lời [phần X] vì [lý do: thiếu guideline / thiếu thông tin bệnh nhân / bằng chứng mâu thuẫn].
Cần bổ sung: [danh sách cụ thể].
```

### 7.3 Template citation riêng theo loại câu hỏi `[MỚI]`

Bài gốc MedTrust-RAG dùng 1 format CiteReason chung cho mọi câu hỏi; ở đây phân theo Question Taxonomy:

| Loại câu hỏi | Ưu tiên trích từ |
|---|---|
| Diagnosis / Differential diagnosis | KG (unit có `attached_triples`, Stage 1) |
| Treatment / Surgery / Medication | Guideline text (Stage 2/4) |
| Rehabilitation / Prognosis | Evidence lọc theo `pathology_class` |
| Symptoms / Causes / Risk factors | Kết hợp cả hai nguồn |
| Prevention `[MỚI]` | Guideline + quan hệ `prevented_by`, lọc theo nhóm đối tượng |

### 7.4 Kiểm soát bốn dạng ảo giác nguy hiểm

| Dạng | Biện pháp |
|---|---|
| Suy luận lỗi | Stage 8 chấm từng statement độc lập; statement điểm thấp bị gắn cảnh báo hoặc loại |
| Bỏ sót thông tin quan trọng | Danh mục yếu tố bắt buộc (6.3); câu trả lời phải nêu đủ hoặc ghi rõ "chưa có bằng chứng cho …" |
| Từ chối quá mức | Stage 9 đo tỉ lệ over-refusal và risk–coverage; chỉ ASK_MORE khi thật sự thiếu thông tin hoặc điểm tin cậy thấp |
| Gán sai nguồn trích dẫn | Mỗi statement kiểm tra "unit được trích có thực sự hỗ trợ không" (Stage 8); đo Citation Accuracy |

### 7.5 Văn phong, độ đọc hiểu, đồng cảm `[MỚI]`

Khoảng trống Giai đoạn 3: y khoa có biên độ sai sót tiệm cận không, cần phản hồi dễ đọc và phù hợp người nhận.

- **v1 (bác sĩ):** ngắn gọn, có cấu trúc, thuật ngữ chuyên môn, ưu tiên liệt kê nội dung quyết định (chẩn đoán phân biệt, chỉ định/chống chỉ định, cảnh báo).
- **v2 (bệnh nhân, *Before consultation*/giải thích bệnh):** ngôn ngữ đời thường, giải thích thuật ngữ, giọng điệu phù hợp; không đưa kết luận chẩn đoán xác định.
- Các thuộc tính này **không đo được bằng metric tự động** → đánh giá bằng thang chấm của bác sĩ/người dùng (C4: Likert về độ rõ, độ đọc hiểu, mức phù hợp giọng điệu).

### 7.6 Triển khai

1. `[GIỮ NGUYÊN]` CiteReason + Negative Knowledge Assertion.
2. `[MỚI]` Template citation theo loại câu hỏi (7.3), khóa `source_ref` thống nhất.
3. `[MỚI]` Điều kiện hóa theo applicability (7.2.4) và xử lý cờ (7.2.5).
4. `[MỚI]` Danh mục yếu tố bắt buộc để chống bỏ sót.
5. Prompt mẫu: Phụ lục F3.

### 7.7 Đánh giá riêng Stage 7

Citation Accuracy; Faithfulness (statement được evidence hỗ trợ); Completeness (so với danh mục yếu tố bắt buộc); tỉ lệ statement dựa trên evidence NotApplicable (kỳ vọng 0); thang chấm độ rõ/độ đọc hiểu của bác sĩ.

---

## STAGE 8 — Step-Level Confidence Scoring + Calibration `[GIỮ NGUYÊN công thức + MỞ RỘNG cách validate]`

**Nguồn gốc `[GIỮ NGUYÊN]`:** Med-PRM.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Chấm độ tin cậy từng bước lập luận độc lập, không suy ngược từ đáp án cuối.

**Input:** các statement (Stage 7) + evidence tương ứng.
**Output:** `r_i` từng statement, `r_total`, `r_total` đã hiệu chuẩn.

### 8.1 Công thức `[GIỮ NGUYÊN]`

$$label_i = Judge(Doc, question, groundtruth, step_i)$$

$$r_i = softmax(logit_{correct}, logit_{incorrect})$$

$$r_{total} = \min(r_1, r_2, \dots, r_K)$$

$$Loss = -\sum_{i=1}^{K}\left[label_i \cdot \log(r_i) + (1-label_i)\cdot\log(1-r_i)\right]$$

**Cách hiểu khi triển khai (diễn giải, cần đối chiếu bài gốc):** `label_i` (có dùng `groundtruth`) là nhãn **huấn luyện/hiệu chuẩn**; ở thời điểm suy luận, bộ chấm điểm tạo `r_i` **không có groundtruth**, chỉ dựa vào tài liệu truy xuất và câu hỏi. `r_total = min` nghĩa là chuỗi chỉ tin cậy bằng bước yếu nhất.

### 8.2 Triển khai

1. `[GIỮ NGUYÊN]` Mỗi statement được chấm độc lập bằng **RAG-as-a-Judge**, không nhìn đáp án cuối.
2. `[MỚI]` Mỗi statement kiểm tra hai điều: **đúng so với evidence** và **evidence được trích có thực sự hỗ trợ** (phát hiện gán sai nguồn).
3. `[MỚI]` **Model chấm (judge) tách khỏi model sinh câu trả lời (Stage 7)** để tránh tự chấm chính mình.
4. `[GIỮ NGUYÊN]` Validate bằng chuyên gia thật theo phương pháp luận bài gốc (3 chuyên gia, 180 step-annotation).
5. `[MỚI]` **Điều chỉnh lấy mẫu:** bài gốc lấy mẫu easy/hard theo accuracy threshold của model; ở đây lấy tỉ lệ nhóm Neoplastic **cao hơn tỉ lệ 19.3%** trong dataset (khởi điểm khoảng 30–35% số mẫu validate) vì đây là nhóm rủi ro cao — bài gốc không điều chỉnh theo pathology class.
6. `[MỚI]` Báo cáo độ đồng thuận giữa chuyên gia (Cohen's κ hoặc tương đương) trước khi dùng nhãn để hiệu chuẩn.

### 8.3 Hiệu chuẩn (calibration) `[MỚI]`

`r_total` là điểm của bộ chấm, **chưa được chứng minh là xác suất đúng**. Cần hiệu chuẩn trước khi dùng cho `threshold_conf` ở Stage 9.

1. Bác sĩ gán nhãn đúng/sai (và an toàn/không an toàn) cho từng câu trả lời trên dev set.
2. Fit bộ hiệu chuẩn `r_total → P(đúng)` (ví dụ isotonic regression hoặc Platt scaling) **riêng theo `pathology_class`** hoặc theo nhóm gộp nếu mẫu quá nhỏ.
3. Đo:

$$ECE = \sum_{b=1}^{B} \frac{|S_b|}{N}\,\big|acc(S_b) - conf(S_b)\big|, \qquad Brier = \frac{1}{N}\sum_{i=1}^{N}(p_i - y_i)^2$$

4. **Risk–coverage:** sắp xếp câu trả lời theo độ tin cậy giảm dần; *coverage* = tỉ lệ câu hỏi hệ thống chịu trả lời; *risk* = tỉ lệ trả lời sai trong số đã trả lời. Vẽ đường riêng cho từng class.
5. Nhóm Neoplastic nhỏ (241 ca) → ưu tiên mô hình hiệu chuẩn đơn giản, ít tham số; báo cáo khoảng tin cậy bootstrap; không kết luận mạnh từ chênh lệch nhỏ.

```python
import numpy as np
from sklearn.isotonic import IsotonicRegression

def fit_calibrator(r_dev, y_dev):
    iso = IsotonicRegression(out_of_bounds="clip"); iso.fit(r_dev, y_dev); return iso

def ece(p, y, bins=10):
    p, y = np.asarray(p), np.asarray(y); e = 0.0
    edges = np.linspace(0, 1, bins + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p > lo) & (p <= hi)
        if m.any(): e += m.mean() * abs(y[m].mean() - p[m].mean())
    return e

def brier(p, y): return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))

def risk_coverage(conf, correct):
    order = np.argsort(-np.asarray(conf)); c = np.asarray(correct)[order]
    k = np.arange(1, len(c) + 1)
    return k / len(c), 1 - np.cumsum(c) / k          # coverage, risk

def pick_threshold(conf, correct, max_risk):
    cov, risk = risk_coverage(conf, correct); conf_sorted = np.sort(conf)[::-1]
    ok = np.where(risk <= max_risk)[0]
    return None if len(ok) == 0 else float(conf_sorted[ok.max()])
```

**Mức rủi ro chấp nhận (`max_risk`) cho từng class là quyết định lâm sàng, không phải kỹ thuật.**

### 8.4 Đánh giá riêng Stage 8

Độ chính xác của bộ chấm so với chuyên gia (theo class); ECE, Brier; đường risk–coverage; tỉ lệ statement có trích dẫn sai bị bắt; độ đồng thuận chuyên gia.

---



---

## STAGE 8b — Post-Generation Consistency Verifier 

**Ý tưởng chính:** Lớp chốt chặn kiểm định tính nhất quán và chống ảo giác sau khi sinh (Post-generation verification), nằm giữa Stage 8 (Confidence Scoring) và Stage 9 (Decision Gate). Đóng kín khoảng trống mà MedTrust-RAG và KnowGuard bỏ sót.

**Input:** Câu trả lời nháp từ Stage 7, bằng chứng pool từ Stage 6, bối cảnh bệnh nhân $, ontology $\mathcal{G}$.
**Output:** Phán quyết  $\in$ {PASS, REVISE, INSUFFICIENT} kèm chi tiết trạng thái từng mệnh đề (claim-level status).

### 8b.1 Phân loại 6 trạng thái mệnh đề y khoa (Claim-Level Status)
Mỗi câu khẳng định trong bản nháp được bóc tách và đối soát độc lập với bằng chứng được trích dẫn:
1. **SUPPORTED:** Mệnh đề được chứng minh đầy đủ bởi bằng chứng và phù hợp với bối cảnh bệnh nhân.
2. **MISCITED:** Mệnh đề đúng về mặt y khoa nhưng đoạn tài liệu được gắn số trích dẫn không chứa thông tin này (gán sai nguồn).
3. **UNDER-QUALIFIED:** Mệnh đề đưa ra kết luận khẳng định nhưng bằng chứng gốc có kèm điều kiện hạn chế (ví dụ: chỉ áp dụng khi có suy thận nhẹ hoặc trên 60 tuổi) mà câu trả lời đã bỏ qua.
4. **UNSUPPORTED:** Mệnh đề không tìm thấy bất kỳ căn cứ nào trong kho bằng chứng đã truy xuất (nguy cơ ảo giác thuần túy).
5. **OUT_OF_SCOPE:** Mệnh đề đưa ra chỉ định hoặc can thiệp vượt ngoài phạm vi câu hỏi và dữ liệu lâm sàng cho phép.
6. **CONTRADICTED:** Mệnh đề mâu thuẫn trực tiếp với bằng chứng đã xác minh hoặc vi phạm các quan hệ chống chỉ định trong ontology ().

### 8b.2 Kiểm tra nhất quán Ontology (Ontology Consistency Check)
Tự động đối chiếu các thực thể điều trị/thuốc được đề xuất trong bản nháp với các nút bệnh nền và dị ứng của bệnh nhân trong đồ thị tri thức:
28740	ext{IsViolated} = \exists (	ext{Intervention}, 	ext{contraindicated\_in}, 	ext{Condition}) \in \mathcal{G} \quad 	ext{với } 	ext{Condition} \in u.	ext{conditions}28740
Nếu $	ext{IsViolated} = 	ext{True}$, lập tức chuyển trạng thái mệnh đề sang **CONTRADICTED**.

### 8b.3 Quy tắc định tuyến 3 nhánh (Routing Rules)
- **PASS:** 100% các mệnh đề cốt lõi () đạt  và không có mệnh đề nào bị . Cho phép chuyển thẳng sang Stage 9 để ra quyết định  hoặc .
- **REVISE (Tối đa 1 lần):** Tồn tại mệnh đề bị  hoặc , nhưng thông tin sửa đổi **đã có sẵn trong pool bằng chứng hiện tại**. Kích hoạt Stage 7 viết lại câu trả lời với chỉ thị sửa lỗi cụ thể (prompt constraint).
- **INSUFFICIENT:** Tồn tại mệnh đề ,  hoặc thiếu các yếu tố cốt lõi mà pool bằng chứng hiện tại không thể bù đắp:
  * Nếu số vòng lặp  < T_{\max}$: Định tuyến quay lại **Stage 6 (Gap Analysis)** để tái truy xuất mở rộng.
  * Nếu đã hết số vòng lặp: Chuyển thẳng sang Stage 9 ép buộc vào nhánh **ASK_MORE** (nếu thiếu cận lâm sàng) hoặc **ABSTAIN** (nếu phát hiện mâu thuẫn không thể dung hòa).

## STAGE 9 — Decision Gate (3 nhánh, multi-round) `[MỞ RỘNG]`

**Nguồn gốc `[GIỮ NGUYÊN]`:** KnowGuard.

**Ý tưởng chính `[GIỮ NGUYÊN]`:** Thay vì tự hỏi "tôi tự tin bao nhiêu" (self-assessment), hệ thống chủ động kiểm tra "tôi còn thiếu bằng chứng gì".

**Input:** `RedFlagResult` (S3), cờ (S4), mức applicability của evidence được trích (S5), `GapAnalysis` (S6), `r_total` đã hiệu chuẩn (S8), `round`.
**Output:** một trong ASK_MORE / ANSWER_WITH_WARNING / ANSWER_CLEAN (+ thông tin kèm theo).

### 9.1 Công thức

`[GIỮ NGUYÊN]` Quyết định gốc của KnowGuard — hàm nhị phân 2 nhánh:

$$A_t : K_t \rightarrow \{0, 1\}$$

`[MỚI]` Mở rộng thành 3 nhánh (KnowGuard gốc chỉ có abstain/answer):

| Nhánh | Điều kiện | Nguồn |
|---|---|---|
| **ASK_MORE** | $r_{total} < threshold_{conf}$ **hoặc** evidence chưa đủ (cũng áp dụng khi mọi evidence chính là NotApplicable, xem 9.3) | `[GIỮ NGUYÊN]` (tương đương "abstain") |
| **ANSWER_WITH_WARNING** | $r_{total} \ge threshold_{conf}$ **và** $s_{appl} \in \{Partial\}$ (hoặc có cờ chặn) | `[MỚI]` — hoàn toàn không có trong KnowGuard |
| **ANSWER_CLEAN** | $r_{total} \ge threshold_{conf}$ **và** $s_{appl} = Applicable$, **không** có cờ chặn | `[GIỮ NGUYÊN]` (tương đương "answer") |

### 9.2 Mức applicability tổng hợp

Mức tổng = **mức thấp nhất** trong các unit được trích cho các khẳng định chính (nguyên tắc "mắt xích yếu nhất").

### 9.3 Chính sách NotApplicable `[MỚI — đề xuất, cần bác sĩ duyệt]`

Roadmap bản đầu xếp NotApplicable vào ANSWER_WITH_WARNING. Thiết kế này nhận thấy trả lời dựa trên bằng chứng **không áp dụng được cho bệnh nhân này** có thể gây hại, nên đề xuất cấu hình:

```yaml
not_applicable_policy: ask_more   # ask_more (mặc định đề xuất) | warn (theo roadmap gốc)
```

- `ask_more`: nếu mọi evidence chính là NotApplicable → ASK_MORE (hoặc từ chối nếu hết lượt), kèm lý do và thông tin có thể thay đổi kết luận.
- `warn`: ANSWER_WITH_WARNING với cảnh báo mạnh.

Cần quyết định chính thức (Phần E).

### 9.4 Cờ chặn ANSWER_CLEAN `[MỚI]`

`conflict`, `unreviewed`, `late_neoplastic_signal`, `redflag_indeterminate`, `stale`, `conflict` chưa giải quyết, **hoặc** chưa kiểm tra tương tác thuốc – bệnh nền khi `qtype` là Medication. Các cờ này đẩy kết quả sang ANSWER_WITH_WARNING (hoặc ASK_MORE nếu điểm thấp). `kg_sparse` chỉ là thông tin, không chặn.

### 9.5 Thuật toán quyết định

```python
def decide(s):                       # s: Stage9Input
    if s.redflag == "true":                         return "ESCALATE"        # đã xử lý ở Stage 3
    if "no_evidence" in s.flags:                    return "ASK_MORE" if s.rounds_left else "ABSTAIN"
    thr = THRESHOLD_CONF[s.pathology_class]         # đã hiệu chuẩn theo class (C4, 8.3)
    low_conf = s.r_total_cal < thr
    insufficient = not s.sufficient
    level = s.applicability_overall                 # Applicable | Partial | NotApplicable

    # [B6]: Nếu sau 1 lần REVISE ở Stage 8b mà vẫn không đạt PASS -> buộc ABSTAIN hoặc ASK_MORE
    if getattr(s, 'revise_failed', False):
        return "ABSTAIN"
    if level == "NotApplicable" and cfg.not_applicable_policy == "ask_more":
        return "ASK_MORE" if s.rounds_left else "ABSTAIN"
    if low_conf or insufficient:
        return "ASK_MORE" if s.rounds_left else "ABSTAIN"
    if level == "Applicable" and not (s.flags & BLOCKING_FLAGS):
        return "ANSWER_CLEAN"
    return "ANSWER_WITH_WARNING"
```

`ABSTAIN` là kết thúc an toàn khi hết số vòng: phát Negative Knowledge Assertion kèm danh sách thông tin còn thiếu.

### 9.6 `threshold_conf` theo pathology_class `[MỚI]`

`threshold_conf` hiệu chuẩn riêng theo `pathology_class` bằng đường risk–coverage (8.3). Giá trị minh họa **chỉ để làm khung**, **phải xác định bằng dữ liệu và mức rủi ro bác sĩ chấp nhận**:

| Class | Giá trị minh họa (chưa kiểm chứng) | Hướng |
|---|---|---|
| Traumatic | 0.70 | |
| Inflammatory | 0.75 | |
| Neoplastic | 0.85 | Nghiêm ngặt hơn |
| unknown | 0.80 | |

### 9.7 Nội dung của ASK_MORE `[MỚI]`

- Danh sách **thông tin còn thiếu** có cấu trúc (từ `applicability_gaps` và `missing_information` của Stage 6): trường dữ liệu bệnh nhân, cận lâm sàng/khảo sát có thể làm rõ.
- **Đề xuất để bác sĩ cân nhắc, không phải phiếu chỉ định:** hệ thống nêu thông tin nào sẽ thay đổi kết luận; quyết định chỉ định xét nghiệm/chụp chiếu là của bác sĩ.
- Ở `phase = P1`, đây là nhánh thường gặp nhất.

### 9.8 Multi-round `[MỚI]`

1. Mỗi lượt ASK_MORE → bác sĩ bổ sung thông tin (hoặc hệ thống chạy lại retrieval nếu thiếu relevance) → cập nhật `CaseInput` → chạy lại Stage 3–9.
2. Giới hạn số lượt `max_clinician_rounds` (khởi điểm 2) để tránh vòng lặp vô hạn; hết lượt → ABSTAIN có lý do.
3. Mỗi vòng giữ nguyên ngữ cảnh (`E_query` cộng dồn, thông tin bệnh nhân đã cập nhật) và ghi vào audit.

### 9.9 Triển khai

1. `[MỚI]` `r_total` lấy từ Stage 8 (đã hiệu chuẩn), `s_appl` từ Stage 5 — KnowGuard gốc chỉ dùng evidence pool của chính nó.
2. `[GIỮ NGUYÊN]` Nhánh ASK_MORE hoạt động giống logic abstain gốc.
3. `[MỚI]` ANSWER_WITH_WARNING là đóng góp mới: phân biệt được "đủ tự tin nhưng evidence không áp dụng được trọn vẹn cho bệnh nhân này".
4. `[MỚI]` `threshold_conf` theo `pathology_class` (9.6).
5. `[MỚI]` Cờ Stage 4 tác động quyết định (9.4).
6. `[MỚI]` Chính sách NotApplicable cấu hình được (9.3).

### 9.10 Đánh giá riêng Stage 9

- **Abstention accuracy:** trong các ca ASK_MORE/ABSTAIN, bao nhiêu ca thực sự thiếu thông tin hoặc câu trả lời sẽ sai.
- **Over-refusal rate:** ASK_MORE ở những ca lẽ ra trả lời an toàn được.
- **Đường risk–coverage** theo class.
- **Tỉ lệ ANSWER_CLEAN nhưng sai** (kỳ vọng thấp nhất; mục tiêu an toàn chính).
- So khớp với `expected_decision` trong gold set (C3).

---

## OUTPUT CUỐI CÙNG `[MỚI — tổng hợp lại từ các stage]`

```
Answer                      ← Stage 7 [MỞ RỘNG]
+ Evidence                  ← Stage 4 [GIỮ NGUYÊN + MỚI]
+ Citation                  ← Stage 7 [GIỮ NGUYÊN]
+ Confidence                ← Stage 8 [GIỮ NGUYÊN + MỞ RỘNG] (đã hiệu chuẩn)
+ Missing Information       ← Stage 6 [MỞ RỘNG]
+ Applicability Warning     ← Stage 5 [MỚI]
+ Evidence Flags            ← Stage 4 [MỚI]  (unreviewed · conflict · stale · kg_sparse · late_neoplastic_signal)
+ Red-Flag Alert            ← Stage 3 [MỚI]
```

**Schema JSON đầu ra:**

```json
{
  "request_id": "R_0001", "phase": "P3",
  "decision": "ANSWER_WITH_WARNING",
  "red_flag": {"status": "false", "criteria_matched": [], "unknown_fields": []},
  "answer": [
    {"statement": "...", "citations": ["DOC:C_88421"], "applicability": "Applicable", "r_i": 0.91},
    {"statement": "... (chỉ khi ...)", "citations": ["KG:T_000123"], "applicability": "Partial", "r_i": 0.82}
  ],
  "excluded_evidence": [{"source_ref": "DOC:C_20011", "reason_codes": ["AGE_OUT_OF_SCOPE"]}],
  "confidence": {"r_total_raw": 0.78, "r_total_calibrated": 0.74, "threshold": 0.70},
  "missing_information": [{"field": "severity", "why": "..."}],
  "applicability_warning": "Bằng chứng chỉ áp dụng một phần vì ...",
  "evidence_flags": ["unreviewed", "kg_sparse"],
  "evidence": [{"source_ref": "DOC:C_88421", "p_final": 0.82, "applicability": "Applicable"}],
  "versions": {"ontology": "msk-0.3", "embedding": "...", "reranker": "...", "config": "..."}
}
```

**Hiển thị cho bác sĩ:** các cờ (`unreviewed`, `conflict`, `late_neoplastic_signal`, `redflag_indeterminate`) và Applicability Warning phải hiển thị nổi bật, không được ẩn.


---

# PHẦN C — DỮ LIỆU, ĐÁNH GIÁ, THÍ NGHIỆM

## C1. Nguồn dữ liệu

| Nguồn | Có trong hệ thống? | Vai trò | Ghi chú / quyết định cần chốt |
|---|---|---|---|
| Hồ sơ ca bệnh nội bộ (1,247 ca) | ✅ | EHR, báo cáo CĐHA, xây KG, dev/test | Cần phê duyệt dùng dữ liệu; giả danh hóa `patient_id` |
| Clinical guidelines | ❌ **chưa xác định** | Bằng chứng chính cho `tx`, `dx`, `prev` | Chọn bộ nào (trong nước/quốc tế, ngôn ngữ); bản quyền; phiên bản; ngày công bố; nhóm bệnh nhân áp dụng |
| PubMed / literature | ❌ | Bằng chứng bổ sung | Tiêu chí chọn bài, giấy phép |
| Medical textbooks | ❌ | Kiến thức nền, Pathophysiology | Vấn đề bản quyền |
| Thông tin thuốc | ❌ | Kiểm tra thuốc – bệnh nền (Stage 5.6), qtype Medication | Cần nguồn đã được phê duyệt |
| Medical QA datasets | ❌ | Benchmark, không nhất thiết là KB | |
| Radiology / X-ray datasets | ❌ | Chỉ cần nếu làm nhánh ảnh (v2) | |
| MSK-specific datasets | ❌ | | |

**Đây là tồn đọng lớn nhất.** Stage 4 (`tx`), Stage 5 (`s_pop`), Stage 7 (trích từ guideline) đều giả định kho tri thức ngoài đã tồn tại. Nếu chỉ có hồ sơ ca bệnh, hệ thống trả lời được "ca tương tự" nhưng không trả lời được "guideline khuyến cáo gì".

**Quy tắc nạp guideline `[MỚI]`:**

1. Tách theo đơn vị khuyến cáo.
2. Trích sẵn **điều kiện áp dụng** (nhóm tuổi, vị trí, mức độ, chống chỉ định) thành trường cấu trúc `applicability_conditions` khi nạp (LLM trích, bác sĩ duyệt mẫu); không để LLM đoán lúc truy vấn. Đây là điều kiện để `s_appl` có cơ sở.
3. Lưu `version`, `published_date`, `evidence_level` để gắn cờ `stale` và tính `s_pop`.
4. Kiểm tra giấy phép trước khi nạp.

## C2. Question Taxonomy (11 loại)

| Loại | Nhóm (Stage 4) | Ưu tiên trích dẫn (Stage 7) |
|---|---|---|
| Symptoms | `sym` | Kết hợp KG + guideline |
| Causes | `sym` | Kết hợp |
| Risk factors | `sym` | Kết hợp |
| Diagnosis | `dx` | KG |
| Differential diagnosis | `dx` | KG |
| Treatment | `tx` | Guideline |
| Medication | `tx` | Guideline (+ nguồn thuốc, Stage 5.6) |
| Surgery | `tx` | Guideline |
| Rehabilitation / Physiotherapy | `rehab` | Lọc theo pathology_class |
| Prognosis | `rehab` | Lọc theo pathology_class |
| Prevention | `prev` | Guideline + `prevented_by` |

## C3. Schema mẫu QA / annotation

Các trường theo Research Roadmap: User, Disease, Anatomy, Pathology, Morphology, Pathophysiology, Question intent, Patient context, Evidence, Answer. Bổ sung `applicability`, `expected_decision`, `missing_information` để đo được câu hỏi nghiên cứu cốt lõi `[MỚI]`:

```json
{
  "qa_id": "QA_0001",
  "user_role": "emergency_doctor",
  "phase": "P3",
  "question": "...",
  "question_intent": "differential_diagnosis",
  "patient_context": {
    "age": 54, "sex": "F", "anatomy_region": "lower_limb", "pathology_class": "unknown",
    "morphology": ["transverse"], "severity": null,
    "comorbidities": [], "current_medications": [], "findings_text": "..."
  },
  "disease": "ONT:...", "anatomy": "ONT:...", "pathology": "ONT:...",
  "morphology_ids": ["ONT:..."], "pathophysiology": "ONT:...",
  "gold_evidence": [
    {"ref": "DOC:C_88421", "relevance": 1, "applicability": "Applicable"},
    {"ref": "DOC:C_20011", "relevance": 1, "applicability": "NotApplicable",
     "reason": "guideline cho nhóm tuổi khác"}
  ],
  "gold_answer": "...",
  "expected_decision": "ANSWER_WITH_WARNING",
  "missing_information": ["severity"],
  "annotators": ["MD1", "MD2"], "adjudicated": true
}
```

Cần bác sĩ duyệt schema trước khi gán nhãn hàng loạt.

## C4. Metric theo từng tầng

**Retrieval (Stage 4)**

| Metric | Ghi chú |
|---|---|
| Recall@k (k = 8), Precision@k, MRR, nDCG@8 | So với gold evidence |
| Evidence Precision | Tỉ lệ unit được bác sĩ chấm là hữu ích |
| Graph-only gain | Tỉ lệ unit nhờ Graph mà Text bỏ sót |
| Entity Linking F1 | **Đo riêng trước khi đánh giá cả pipeline**; gồm cả link qua alias đời thường |
| Hard-negative robustness | Hiệu năng trên các văn bản giống bề mặt nhưng thiếu thông tin lâm sàng cốt lõi (nhiễu sau truy xuất); cần đưa mẫu dạng này vào dev set |

**Parse tài liệu (Stage 2):** tỉ lệ ô bảng trích sai (mẫu kiểm tra); tỉ lệ chunk có metadata đầy đủ.

**Applicability (Stage 5)**

| Metric | Ghi chú |
|---|---|
| Accuracy, macro-F1 | 3 mức |
| Ma trận nhầm lẫn | |
| **Tỉ lệ NotApplicable → Applicable** | Lỗi nguy hiểm nhất; báo riêng |
| Cohen's κ giữa bác sĩ | Chất lượng nhãn |
| **Counterfactual sensitivity** | Xem dưới |

**Counterfactual protocol `[MỚI]`:** tạo cặp mẫu chỉ khác **một** thuộc tính bệnh nhân (vùng giải phẫu, tuổi, pathology class, morphology) mà bác sĩ xác nhận nhãn applicability đáng lẽ đổi. Đo *flip rate* (hệ thống có đổi nhãn/quyết định không — kỳ vọng có) và *control stability* (giữ nguyên khi chỉ đổi thuộc tính không liên quan — kỳ vọng giữ). Báo cả hai; tăng độ nhạy mà mất ổn định là thất bại.

**Generation (Stage 7)**

| Metric | Ghi chú |
|---|---|
| Correctness | Bác sĩ chấm hoặc so với gold answer |
| Faithfulness | Statement được evidence hỗ trợ |
| Citation Accuracy | Đoạn trích có thực sự hỗ trợ câu trả lời |
| Completeness | So với danh mục yếu tố bắt buộc (6.3) |
| Tỉ lệ statement dựa trên evidence NotApplicable | Kỳ vọng 0 |

**An toàn y khoa**

| Metric | Ghi chú |
|---|---|
| Hallucination rate; Unsupported claim rate | |
| **Unsafe recommendation rate** | Tỉ lệ khuyến nghị bác sĩ chấm là không an toàn |
| Tỉ lệ ca Neoplastic mất tín hiệu khỏi top-8 | Kỳ vọng thấp |
| Tỉ lệ triple chưa duyệt xuất hiện không có cờ | **Kỳ vọng 0** |

**Uncertainty và quyết định (Stage 8–9)**

| Metric | Ghi chú |
|---|---|
| ECE, Brier | Theo class |
| Risk–coverage | Theo class |
| Abstention accuracy | So với `expected_decision` |
| Over-refusal rate | ASK_MORE không cần thiết |
| Tỉ lệ ANSWER_CLEAN nhưng sai | Mục tiêu an toàn chính |

**Đánh giá bởi con người (XAI, văn phong)**

Thang Likert 1–5 do bác sĩ chấm: độ rõ ràng, độ đọc hiểu, mức phù hợp giọng điệu, mức hữu ích của giải thích "vì sao chọn bằng chứng này"; kèm kiểm tra bác sĩ có hiểu cảnh báo applicability không. Những thuộc tính này không đo được bằng metric tự động.

**Nguyên tắc báo cáo bắt buộc:** mọi metric **tách theo `pathology_class`** (Traumatic / Neoplastic / Inflammatory), `qtype` và `anatomy_region`; kèm bootstrap CI 95%.

## C5. Chuỗi thí nghiệm

### C5.1 Chuỗi tổng (theo Research Roadmap)

`Vanilla RAG → Hybrid RAG → Patient-conditioned RAG → + Evidence Applicability → + Uncertainty/Abstention → + Ontology/KG`

| Cấp | Cấu hình | Stage bật | Thay đổi so với cấp trước |
|---|---|---|---|
| L0 | Vanilla RAG | 2 (chunk) + dense top-k + 7 (sinh có trích dẫn) | — |
| L1 | Hybrid RAG | + BM25, RRF, rerank (Stage 4 luồng Text) | Truy xuất lai |
| L2 | Patient-conditioned RAG | + `case_text` vào query, hint metadata (soft boost), Stage 3 | Điều kiện hóa theo bệnh nhân |
| L3 | + Evidence Applicability | + Stage 5 (`s_appl`) | Lọc/cảnh báo theo applicability |
| L4 | + Uncertainty / Abstention | + Stage 6, 8, 9 | Hiệu chuẩn + 3 nhánh quyết định |
| L5 | + Ontology / KG | + Stage 1, luồng Graph Stage 4 | Thêm tri thức có cấu trúc |

**Lưu ý thứ tự KG:** Research Roadmap đặt KG ở cuối, nhưng Stage 4/5 dùng tín hiệu graph (`s_coh`, `attached_triples`) từ sớm. Để so sánh công bằng, L0–L4 phải chạy được **không cần KG**: `s_coh` nhận giá trị trung tính, không có cờ graph, không có quota graph. L5 mới bật KG.

**Lưu ý về "patient-conditioned":** hiện ngữ cảnh ca đi vào retrieval qua entity link, hint (soft boost) và query của reranker; applicability được chấm **sau** retrieval (Stage 5), chưa phải điều kiện hóa ngay lúc truy xuất. Thí nghiệm L2→L3 giúp làm rõ phần đóng góp của từng cách.

### C5.2 Ablation bên trong L5 (Stage 4)

A0–A6 ở mục 4.17. Mỗi cấp và mỗi ablation báo cáo tách theo `pathology_class` và `qtype`.

## C6. Dev / Test set

- Khoảng **150–200** câu hỏi có gold evidence cho dev; thêm test set riêng, **không động tới khi tune**.
- Phân tầng theo `pathology_class` theo tỉ lệ 70/19/11 **và** quá mẫu Neoplastic (khoảng 40 câu); phân tầng thêm theo `qtype`, `anatomy_region`, `phase`.
- Gold evidence + nhãn applicability + `expected_decision` do bác sĩ gán; ≥ 2 bác sĩ độc lập trên một phần mẫu, tính κ, có bước xử lý bất đồng.
- Có các mẫu **hard negative** (giống bề mặt, thiếu thông tin lâm sàng cốt lõi) và các cặp **counterfactual**.
- Nhóm Neoplastic nhỏ (241 ca) → dùng bootstrap CI, không kết luận mạnh từ chênh lệch nhỏ.

---

# PHẦN D — VẬN HÀNH, AN TOÀN, QUYỀN RIÊNG TƯ

## D1. Hiệu năng và quan sát

Ngân sách độ trễ cho toàn pipeline online cần đo trên dữ liệu thật (Stage 4 có ngân sách riêng, mục 4.18). Giám sát: phân bố `origin` (text/graph/cả hai), tỉ lệ degrade (`graph_unavailable`…), tỉ lệ `kg_sparse`, độ trễ p95, tỉ lệ unit `unreviewed`, tỉ lệ ASK_MORE/ANSWER_WITH_WARNING/ANSWER_CLEAN — **tất cả theo `pathology_class`**.

## D2. Audit và tái lập

Mỗi lần chạy lưu: `CaseInput` đã giả danh hóa, `QueryCtx`, text_pool (id + rank), graph_pool (triple_id + `s_graph`), điểm `F(u)`, `rerank_score`, quyết định MMR và quota, `p_final`, `s_appl` + mã lý do, vòng lặp Stage 6, `r_i`, `r_total` thô và đã hiệu chuẩn, quyết định Stage 9, độ trễ từng pha, **phiên bản** (ontology, embedding, reranker, model sinh, model chấm, cấu hình). Cho phép tái dựng vì sao một bằng chứng được đưa ra hoặc bị loại.

## D3. Quyền riêng tư dữ liệu bệnh nhân

- Giả danh hóa `patient_id`; không đưa định danh trực tiếp vào index hay prompt.
- Không gửi dữ liệu ra dịch vụ bên ngoài bệnh viện khi chưa de-identify và chưa được bệnh viện/hội đồng đạo đức phê duyệt. Kiểm tra quy định hiện hành của Việt Nam và nội quy bệnh viện về dữ liệu y tế.
- Phân quyền truy cập index/KG theo vai trò; ghi log truy cập.
- Khảo sát/quan sát bác sĩ (Stage 0.6) cần phê duyệt trước.

## D4. An toàn lâm sàng

1. **Không thay thế bác sĩ:** đầu ra là bằng chứng hỗ trợ quyết định; ASK_MORE chỉ **đề xuất thông tin cần làm rõ**, không ra chỉ định.
2. Cờ `unreviewed`, `conflict`, `late_neoplastic_signal`, `redflag_indeterminate` và Applicability Warning **phải hiển thị cho bác sĩ**.
3. Thiên lệch phân bố: KG và index nghiêng về Traumatic (70.2%) nên hệ thống có thể kém ở Neoplastic/Inflammatory; vì vậy quota an toàn, ngưỡng nghiêm ngặt, review thủ công và đánh giá tách lớp tồn tại ở mọi tầng.
4. Mọi tiêu chí red-flag, danh mục yếu tố bắt buộc, `threshold_conf`, ngưỡng `tau` do bác sĩ chuyên khoa phê duyệt.

## D5. Kiểm soát thay đổi

Thay đổi ngưỡng, trọng số, ontology, template verbalize hoặc nguồn tri thức cần bác sĩ phụ trách duyệt và chạy lại bộ hồi quy (F4) kèm so sánh trước/sau theo class trước khi đưa vào dùng.

## D6. Rủi ro và hạn chế đã biết

1. Chất lượng entity linking quyết định chất lượng luồng Graph.
2. Provenance không đầy đủ làm giảm lifting.
3. Các tham số số học là giả định ban đầu; Weighted RRF theo qtype là giả thuyết.
4. Sai lệch gán nhãn `pathology_class` ảnh hưởng soft boost và ngưỡng.
5. Nhóm Neoplastic nhỏ → thống kê kém ổn định.
6. LLM-judge (`s_rel`, qtype, Stage 8) có thể sai/thiên lệch; cần hiệu chuẩn bằng nhãn bác sĩ.
7. Độ trễ có thể vượt mục tiêu khi KG lớn hoặc 2-hop.
8. Mã tham chiếu chưa kiểm thử.
9. Chưa có kho guideline ngoài và nguồn thông tin thuốc.
10. Mức độ "adapt" mới ở dạng điều kiện hóa câu trả lời theo applicability; chưa tự động viết lại theo từng nhóm bệnh nhân.
11. Ghép CLI-RAG + KnowGuard là thiết kế riêng, không có kết quả công bố cho chính tổ hợp này.
12. Ca ở Giai đoạn 1 có dữ liệu thiếu → đa số ASK_MORE, khó đo hơn.

---

# PHẦN E — ĐỐI CHIẾU RESEARCH ROADMAP, TỒN ĐỌNG, QUYẾT ĐỊNH

## E1. Cách đọc

✅ = **đã có cơ chế được thiết kế** (chưa kiểm chứng) · 🟡 = một phần · ❌ = chưa có. Cột "Nơi" chỉ stage/mục trong tài liệu này.

Tổng quan:

| Mục Research Roadmap | Mức bao phủ | Tồn đọng chính |
|---|---|---|
| 1. Clinical Workflow & Positioning | 🟡 | Chưa khảo sát thực tế; lab, thuốc chưa có nguồn |
| 2. LLM / Foundation Model | ❌ | Chưa chọn backbone, chưa benchmark |
| 3. Knowledge Representation | 🟡 | 3/8 pathology class; morphology u bướu chưa chốt; chưa căn chỉnh ontology quốc tế |
| 4. RAG | ✅ phần lớn | Guideline corpus; Self-RAG; temporal |
| 5. Uncertainty + XAI + Safety | ✅ thiết kế; 🟡 thực hiện | Chưa chạy hiệu chuẩn; chưa highlight bằng chứng |
| 6. Dataset, Taxonomy, Evaluation | 🟡 | Chưa có corpus ngoài, chưa gán nhãn |

## E2. Ma trận chi tiết

### Mục 1 — Clinical Workflow & Positioning

| Mục | Nơi | Trạng thái | Ghi chú |
|---|---|---|---|
| Khảo sát luồng khám đầy đủ | 0.6 | ❌ | Là hoạt động nghiên cứu; đã có kế hoạch phỏng vấn |
| Registration / Triage | Stage 3 | 🟡 | Chỉ khai thác cho red-flag |
| History taking | Stage 3, 5 | 🟡 | Tiền sử thuốc cần nguồn thuốc |
| Physical examination | Stage 5 (`match_severity`) | 🟡 | `CaseInput.exam` chưa có schema chi tiết |
| Initial assessment & Differential | Stage 4 (`dx`, 2-hop), 6 | ✅ | |
| Diagnostic testing | A2, Stage 2 | 🟡 | Chỉ văn bản; ảnh để v2; lab cần quyết định |
| Interpretation (tổng hợp) | Stage 4 cross-linking, 5 | 🟡 | |
| Diagnosis / severity staging | Stage 1, 5 | 🟡 | Layer Severity/Stage chưa cụ thể |
| Treatment decision | Stage 4 `tx`, 7 | ✅ | |
| Follow-up & monitoring | — | ❌ | Hoãn v2 |
| Referral / escalation | Stage 3, 9 | 🟡 | Chỉ escalation u bướu; mở rộng ở v2 |
| Actors | 0.1 | 🟡 | Chọn phạm vi v1, không loại actor khác |
| Information flow | 0.2 | 🟡 | Bảng đã có; lab/guideline/thuốc còn thiếu |
| Vị trí RAG: Before consultation | — | ❌ | v2 |
| Vị trí RAG: During consultation | A2, Stage 3–6, 9 | ✅ | v1 hẹp |
| Vị trí RAG: After tests/imaging | A2 | ✅ | v1 trọng tâm |
| Vị trí RAG: After diagnosis | A2, 0.1 | ✅ | Đã bổ sung |
| Vị trí RAG: Follow-up | — | ❌ | v2 |
| Evidence chung không hợp bệnh nhân cụ thể | Stage 5 | ✅ | |
| Thiếu dữ liệu không kết luận an toàn | Stage 6, 9 | ✅ | |
| Bước cần citation/uncertainty nhất | — | 🟡 | Chờ khảo sát (0.6) |

### Mục 2 — LLM / Foundation Model

| Mục | Trạng thái | Ghi chú |
|---|---|---|
| General vs Medical LLM; Text-only vs Multimodal; so sánh; shortlist; chọn 2–3 backbone | ❌ | Chưa thực hiện |

Vị trí cần LLM (để chọn backbone có căn cứ):

| Vị trí | Việc LLM làm | Yêu cầu chính |
|---|---|---|
| Stage 1 | 3 LLM: trích xuất / chuẩn hóa / validate | Trích xuất có cấu trúc, tiếng Việt |
| Stage 2 | Trích `applicability_conditions` khi nạp guideline | Chính xác, có cấu trúc |
| Stage 4 | qtype, viết lại sub-query | Nhanh, rẻ |
| Stage 5 | LLM-judge relevance (`s_rel`) | Nhất quán |
| Stage 6 | Verifier + Gap Analysis | Suy luận về thiếu sót |
| Stage 7 | Sinh câu trả lời có trích dẫn | Bám nguồn, ít hallucination |
| Stage 8 | RAG-as-a-Judge | Khác model sinh |

Đề xuất: chọn 2–3 backbone cho generator; **tách riêng** model chấm (Stage 8) khỏi model sinh; benchmark backbone chỉ là thí nghiệm phụ, không phải đóng góp chính.

### Mục 3 — Knowledge Representation

| Mục | Nơi | Trạng thái | Ghi chú |
|---|---|---|---|
| 3.1 Anatomy | Stage 1 | 🟡 | Dataset chỉ 3 vùng lớn; cần chốt mức chi tiết (cột sống, gối, háng, vai, bàn tay, bàn chân) |
| 3.2 Pathology Class | Stage 1.9, E3 | 🟡 | 3/8 class |
| 3.3 Disease Entity | Stage 1 | 🟡 | Phụ thuộc class có dữ liệu |
| 3.4 Morphology | Stage 1.4 | 🟡 | Gãy xương ✅; u bướu/viêm chờ bác sĩ chốt; ảnh để v2 |
| 3.5 Pathophysiology | Stage 1.3 | 🟡 | Chưa nêu nguồn nội dung |
| 3.6 Symptoms | `has_phenotype` | ✅ | |
| 3.6 Severity / Stage / Progression | Stage 5 | 🟡 | Chưa có layer riêng; progression cần dữ liệu theo thời gian |
| 3.6 Risk factors / Diagnosis / Treatment / Rehab / Prognosis | Stage 1.5 | ✅ | |
| 3.6 Prevention | `prevented_by` | ✅ | Đã bổ sung |
| 3.7 Các quan hệ Disease–X | Stage 1.5 | ✅ | |
| 3.7 Khảo sát ontology có sẵn | Stage 1.7.9 | 🟡 | Có bước căn chỉnh tùy chọn, chưa thực hiện |
| Lưu ý "các tầng khác nhau, không tuyến tính" | Stage 1.3 | ✅ | Layer song song |
| Alias đời thường ↔ chuyên môn | Stage 1.6 | ✅ | Đã bổ sung; cần bác sĩ duyệt |

### Mục 4 — RAG

| Mục | Nơi | Trạng thái |
|---|---|---|
| Chunking | Stage 2 | ✅ |
| Embedding / Vector DB / Top-k | Stage 4.4, 4.15 | 🟡 (chưa benchmark) |
| Prompt construction | Stage 7, F3 | 🟡 |
| BM25 / Dense / Hybrid / Reranking | Stage 4 | ✅ |
| Query rewriting | Stage 4.7 | 🟡 (sub-query theo note type; chưa viết lại theo patient context) |
| Multi-query | Stage 4.7 (Global + Local) | 🟡 |
| Adaptive RAG | Stage 4 (weights, hop) | 🟡 (chưa quyết định "có cần retrieve không") |
| Corrective / Iterative RAG | Stage 6 | ✅ |
| Self-RAG | — | ❌ (có thể làm baseline) |
| Agentic RAG | Stage 6 verifier | 🟡 |
| Guideline-based / Evidence-based RAG | Stage 2, 4, 5 | 🟡 (thiếu corpus) |
| Patient-conditioned retrieval | Stage 4.6, 5 | 🟡 (applicability chấm sau retrieval) |
| Temporal / longitudinal | — | ❌ (v2) |
| Ontology-aware / KG-RAG / Entity-guided / Query expansion | Stage 1, 4 | ✅ |

Research question mục 4.5 (knowledge structure có giúp retrieval hơn text similarity?) → ablation A0–A6 (4.17).

### Mục 5 — Uncertainty + XAI + Safety

| Mục | Nơi | Trạng thái |
|---|---|---|
| Relevant? / Đủ? / Conflict? / Match bệnh–bối cảnh? | Stage 5, 6, 4 | ✅ |
| Relevance ≠ Applicability ≠ Sufficiency | Stage 5, 6 | ✅ |
| Patient-conditioned applicability scoring | Stage 5.3 | ✅ thiết kế; cần gold label |
| Hallucination / Unsupported claims | Stage 7, 8 | ✅ |
| Overgeneralization | Stage 5, 9 | ✅ |
| Confidence estimation | Stage 8 | ✅ thiết kế (hiệu chuẩn 8.3) |
| Calibration, ECE, Brier, Selective prediction, Risk–coverage | Stage 8.3, C4 | ✅ thiết kế; chưa chạy |
| Khi nào abstain / ask more / retrieve again | Stage 6, 9 | ✅ |
| Citation & attribution | Stage 7 | ✅ |
| Supporting evidence highlighting | — | ❌ |
| Why this evidence was selected | Audit (D2), reason codes | 🟡 (chưa có giao diện giải thích) |
| Missing information | Stage 6, 9 | ✅ |
| Conflicting evidence | Stage 4, 5, 7 | ✅ |
| Confidence / uncertainty display | Output | 🟡 (phụ thuộc hiệu chuẩn) |

### Mục 6 — Dataset, Taxonomy, Evaluation

| Mục | Nơi | Trạng thái |
|---|---|---|
| Question Taxonomy 11 loại | C2 | ✅ (đã thêm Prevention) |
| Annotation schema | C3 | ✅ đề xuất; cần bác sĩ duyệt |
| Data sources | C1 | ❌ (chưa chọn nguồn ngoài) |
| Recall@k, Precision@k, MRR, nDCG | C4 | ✅ |
| Correctness, Faithfulness, Citation accuracy, Completeness | C4 | ✅ (cần định nghĩa chấm Correctness) |
| Hallucination, Unsupported claim, Unsafe recommendation | C4 | ✅ |
| Calibration, Abstention accuracy, Risk–coverage | C4 | ✅ |
| Applicable vs non-applicable classification | C4 | ✅ |
| Counterfactual sensitivity | C4 | ✅ |

## E3. Lệch phạm vi pathology class

| Class trong Research Roadmap | Có trong dataset? | Ghi chú |
|---|---|---|
| Traumatic | ✅ 70.2% | |
| Neoplastic | ✅ 19.3% | |
| Inflammatory / Autoimmune | ✅ 10.5% | Cần xác nhận có gồm autoimmune hay chỉ viêm |
| Degenerative | ❌ | Ví dụ osteoarthritis không có |
| Metabolic | ❌ | Ví dụ osteoporosis |
| Infectious | ❓ | Có thể nằm trong Inflammatory (ví dụ osteomyelitis) — **cần kiểm tra lại nhãn** |
| Congenital / Developmental | ❌ | |
| Vascular / Necrotic | ❌ | |

Hệ quả: Disease Entity như Osteoarthritis, Osteoporosis **không kiểm thử được trên dữ liệu này**. Chọn Hướng A (thu hẹp 3 class) hoặc Hướng B (ontology 8 class, đánh giá 3 class, ghi rõ giới hạn) — xem Stage 1.9.

## E4. Câu hỏi nghiên cứu cốt lõi → cơ chế

> *Can a RAG system detect when retrieved medical evidence is relevant but not applicable to a specific musculoskeletal patient context, and abstain or adapt its answer accordingly?*

| Thành phần | Cơ chế |
|---|---|
| Evidence is relevant | Stage 4 + Stage 5 (`p_final`) |
| but not applicable to the patient | Stage 5 (`s_appl`, mã lý do, cờ) |
| detect | Phân loại Applicable / Partial / NotApplicable; đo bằng gold label (cần xây) |
| abstain | Stage 9 nhánh ASK_MORE / ABSTAIN |
| adapt | Stage 7 điều kiện hóa câu trả lời theo applicability + Stage 9 ANSWER_WITH_WARNING |

**Mức độ sẵn sàng:** thiết kế đủ để *trả lời* câu hỏi nhưng chưa thể *kiểm chứng* cho đến khi có (1) gold label applicability, (2) corpus bằng chứng ngoài, (3) hiệu chuẩn thực tế trên dữ liệu bệnh viện.

## E5. Tồn đọng còn lại, xếp theo ưu tiên

**Ưu tiên cao (chặn việc kiểm chứng chính)**

| # | Tồn đọng | Cách đóng |
|---|---|---|
| 1 | Chọn nguồn tri thức ngoài (guideline, tài liệu) và nguồn thông tin thuốc | C1 |
| 2 | Chốt phạm vi pathology (3 hay 8 class); kiểm tra nhãn Infectious/Autoimmune; kiểm tra dataset có nhãn gãy xương bệnh lý | E3, Stage 1.9 |
| 3 | Gán gold label applicability + schema QA | C3, C4 |
| 4 | Chạy hiệu chuẩn, risk–coverage, chọn `threshold_conf` | Stage 8.3 |
| 5 | Chọn backbone generator và judge (tách riêng) | E2 mục 2 |
| 6 | Bác sĩ chốt định nghĩa vận hành các tiêu chí red-flag | Stage 3.2 |

**Ưu tiên trung bình**

| # | Tồn đọng | Mục RR |
|---|---|---|
| 7 | Bác sĩ chốt morphology u bướu/viêm và alias đời thường | 3.4 |
| 8 | Căn chỉnh ontology chuẩn quốc tế (kiểm tra giấy phép) | 3.7 |
| 9 | Quyết định lab và thông tin thuốc có vào v1 không | 1.3, 6.1 |
| 10 | Định nghĩa schema `exam` có cấu trúc | 1.1 |
| 11 | Khảo sát workflow thực tế | 1 |
| 12 | Giao diện giải thích "vì sao chọn bằng chứng này" | 5.5 |
| 13 | Định nghĩa chấm Correctness | 6.4 |

**Ưu tiên thấp / hoãn (đã chủ động để v2)**

| # | Tồn đọng | Mục RR |
|---|---|---|
| 14 | Before consultation, Follow-up, bộ nhớ phiên | 1.4 |
| 15 | Temporal / longitudinal | 4.4 |
| 16 | Nhánh ảnh X-quang (multimodal) | 2, 3.4 |
| 17 | Supporting evidence highlighting | 5.5 |
| 18 | Self-RAG, Agentic RAG đầy đủ (baseline so sánh) | 4.3 |
| 19 | Escalation tổng quát ngoài gãy xương bệnh lý | 1.1 |

## E6. Quyết định cần chốt (theo thứ tự nên làm)

1. Phạm vi pathology: Hướng A hay B?
2. Bộ guideline/tài liệu nào sẽ nạp, kèm điều kiện bản quyền; nguồn thông tin thuốc?
3. Ai gán nhãn applicability; mức đồng thuận tối thiểu (κ) chấp nhận được?
4. Mức rủi ro chấp nhận (`max_risk`) cho từng pathology class để chọn `threshold_conf`?
5. `not_applicable_policy`: `ask_more` (đề xuất) hay `warn` (roadmap gốc)?
6. Backbone cho generator và judge (tách riêng)?
7. Lab và thông tin thuốc vào v1 không?
8. Nhánh ảnh vào v1 hay chỉ báo cáo văn bản?
9. Định nghĩa vận hành các tiêu chí red-flag và có bổ sung tiêu chí ở Stage 3.3 không?
10. Danh mục yếu tố bắt buộc theo loại câu hỏi (6.3) có được duyệt không?
11. Ưu tiên v1 có giữ Giai đoạn 3 sau khi khảo sát bác sĩ không?

## E7. Những gì có trong hệ thống nhưng Research Roadmap chưa liệt kê

Nên thêm vào Research Roadmap hoặc ghi rõ là phần mở rộng:

| Thành phần | Lý do |
|---|---|
| Stage 3 Red-Flag Screening Gate (3 trạng thái, `indeterminate`) | Cơ chế an toàn cho gãy xương bệnh lý |
| Quota giữ bằng chứng Neoplastic, cờ `late_neoplastic_signal` | An toàn cho nhóm thiểu số rủi ro cao |
| Provenance chunk ↔ triple | Nền tảng trích dẫn thống nhất Text–Graph |
| Cờ trạng thái bằng chứng (`unreviewed`, `conflict`, `stale`…) | XAI và quyết định |
| Review thủ công KG Neoplastic | Kiểm soát chất lượng tri thức |
| Đánh giá bắt buộc tách theo `pathology_class` | Chống che giấu hiệu năng kém ở nhóm nhỏ |
| Phase-aware mode (P1/P3) | Vận hành ở nhiều giai đoạn lâm sàng |
| Audit log đầy đủ | Tái lập, kiểm toán |

---

# PHẦN F — PHỤ LỤC

## F1. Danh mục cờ (flags)

| Cờ | Ý nghĩa | Ai dùng | Chặn ANSWER_CLEAN? |
|---|---|---|---|
| `redflag_indeterminate` | Có tiêu chí red-flag chưa đánh giá được do thiếu dữ liệu | Stage 6, 9 | Có |
| `late_neoplastic_signal` | Có tín hiệu u bướu dù RedFlag = false | Stage 5, 9 | Có |
| `graph_unavailable` | Không có seed hợp lệ | Stage 6, 7 | Không |
| `graph_stream_failed` / `text_stream_failed` | Luồng lỗi/timeout | Vận hành | Không |
| `kg_sparse` | KG ít triple cho truy vấn | Stage 6 | Không |
| `unreviewed` | Triple Neoplastic chưa được bác sĩ duyệt | Stage 5, 7, 9 | Có |
| `conflict` | Bằng chứng mâu thuẫn | Stage 5, 7, 9 | Có |
| `stale` | Nguồn cũ | Stage 5 | Có |
| `dense_backfilled` | Rank dense tính bù cho unit chỉ từ Graph | Phân tích | Không |
| `ambiguous_entity` | Entity/alias mơ hồ | Stage 6 | Không |
| `parsed_table` | Số liệu trích từ bảng PDF | Stage 7 | Không |
| `llm_applicability` | Applicability do LLM đánh giá (không theo luật cấu trúc) | Stage 5, 9 | Không |
| `no_evidence` | Cả hai luồng rỗng | Stage 7, 9 | — |

## F2. Bảng tổng hợp — cái gì giữ nguyên, cái gì mới

**Stage 0 — Clinical Workflow Positioning**
→ 100% `[MỚI]`.

**Stage 1 — Ontology-Grounded KG Construction**
→ `[GIỮ NGUYÊN]`: công thức EAV, entropy, ontology mapping score, composite trust score; vai trò 3 LLM.
→ `[MỚI]`: ontology Bone/MSK riêng, phân bổ effort theo tỉ lệ, review thủ công Neoplastic, provenance triple, degree node, alias đời thường, morphology u bướu, quan hệ `prevented_by`, ngưỡng chấp nhận vào KG.

**Stage 2 — Multi-Source Document Processing**
→ `[GIỮ NGUYÊN]`: kiến trúc chunking + retrieval 2 tầng, tách Findings/Impression, metadata gốc.
→ `[MỚI]`: metadata `pathology_class`, `anatomy_region`, `entity_ids`, `source_authority`, `applicability_conditions`; tách từ tiếng Việt; chuẩn hóa alias; parse PDF/bảng/xét nghiệm.

**Stage 3 — Red-Flag Screening Gate**
→ 100% `[MỚI]` (gồm trạng thái `indeterminate`).

**Stage 4 — Hybrid + Graph-Guided Retrieval**
→ `[GIỮ NGUYÊN]`: công thức hybrid text (CLI-RAG) và graph expansion (KnowGuard), lấy riêng lẻ.
→ `[MỚI]`: toàn bộ phần hợp nhất — EvidenceUnit, cross-linking 2 chiều, verbalize, Weighted RRF theo qtype, bonus đồng thuận, path score, quota an toàn Neoplastic, cờ cảnh báo, ablation A0–A6.

**Stage 5 — Evidence Evaluation**
→ `[GIỮ NGUYÊN]`: công thức Relevance.
→ `[MỚI]`: Applicability score, quy tắc 3 mức, hard checks, kiểm tra thuốc – bệnh nền, ngưỡng Neoplastic, mã lý do, ảnh hưởng của cờ.

**Stage 6 — Iterative Retrieval-Verification**
→ `[GIỮ NGUYÊN]`: công thức và T_max = 3.
→ `[MỞ RỘNG]`: Gap Analysis 2 loại thiếu, dùng `coverage`, cộng dồn `E_query`, danh mục yếu tố bắt buộc, định tuyến ask_clinician.

**Stage 7 — Citation-Aware Generation**
→ `[GIỮ NGUYÊN]`: CiteReason + Negative Knowledge Assertion.
→ `[MỚI]`: template citation theo loại câu hỏi, khóa `source_ref` thống nhất, điều kiện hóa theo applicability, xử lý cờ, văn phong.

**Stage 8 — Step-Level Confidence Scoring**
→ `[GIỮ NGUYÊN]`: RAG-as-a-Judge, softmax reward, loss, phương pháp validate chuyên gia.
→ `[MỚI]`: lấy mẫu ưu tiên Neoplastic, tách judge khỏi generator, hiệu chuẩn (ECE, Brier, risk–coverage), báo cáo κ.

**Stage 9 — Decision Gate**
→ `[GIỮ NGUYÊN]`: ASK_MORE và ANSWER_CLEAN — tương đương 2 nhánh gốc của KnowGuard.
→ `[MỚI]`: ANSWER_WITH_WARNING, `threshold_conf` theo pathology, cờ chặn ANSWER_CLEAN, `not_applicable_policy`, multi-round có giới hạn, ABSTAIN.

## F3. Prompt mẫu (khung — cần chỉnh theo model và duyệt bởi bác sĩ)

**Phân loại qtype (Stage 4)**

```
Bạn là bộ phân loại câu hỏi lâm sàng cơ xương khớp.
Phân loại câu hỏi vào ĐÚNG MỘT loại:
[Symptoms, Causes, Risk factors, Diagnosis, Differential diagnosis, Treatment,
 Medication, Surgery, Rehabilitation, Prognosis, Prevention]
Nếu không thuộc loại nào, trả "Other".
Trả JSON: {"qtype": "...", "confidence": 0-1}. Chỉ trả JSON.
Câu hỏi: {q}
```

**LLM-judge relevance (Stage 5)**

```
Câu hỏi: {q}
Bằng chứng: {text_repr}
Cho điểm 0-1 mức độ bằng chứng LIÊN QUAN trực tiếp đến câu hỏi (không xét có áp dụng
cho bệnh nhân hay không). Trả JSON: {"s_rel": 0-1, "why": "..."}
```

**Verifier / Gap Analysis (Stage 6)**

```
Câu hỏi: {q}   Loại: {qtype}
Yếu tố bắt buộc: {required_elements}
Bằng chứng (kèm applicability và mã lý do): {units}
Hãy đánh giá: (1) mỗi yếu tố bắt buộc đã có bằng chứng liên quan và áp dụng được chưa;
(2) thiếu BẰNG CHỨNG (relevance gap) hay thiếu THÔNG TIN BỆNH NHÂN (applicability gap);
(3) có mâu thuẫn không. Trả JSON theo schema đã cho (sufficient, relevance_gaps,
applicability_gaps, conflicts, action, augment_query). Không bịa thông tin.
```

**Sinh câu trả lời (Stage 7)**

```
Chỉ dùng bằng chứng được cung cấp. Mỗi câu chỉ chứa một khẳng định và kết thúc bằng
trích dẫn [Doc_i] (source_ref) của đúng đoạn hỗ trợ.
- Evidence "Applicable": dùng làm cơ sở khẳng định chính.
- Evidence "Partial": nêu rõ điều kiện áp dụng/giới hạn.
- Evidence "NotApplicable": KHÔNG dùng làm cơ sở; chỉ nêu ngắn gọn lý do loại.
- Cờ "unreviewed": ghi rõ "chưa được bác sĩ chuyên khoa xác nhận".
- Cờ "conflict": trình bày cả hai phía.
- Nếu không đủ bằng chứng cho một phần: dùng mẫu "Không đủ bằng chứng để trả lời ... vì ...
  Cần bổ sung: ...". Không suy đoán, không thêm kiến thức ngoài bằng chứng.
Cuối câu trả lời liệt kê: Thông tin còn thiếu; Lưu ý áp dụng.
```

**Chấm từng bước (Stage 8)**

```
Câu hỏi: {q}
Bằng chứng: {docs}
Câu cần chấm: "{statement}"  (trích dẫn: {citation})
Không xét câu trả lời cuối. Chỉ xét: (a) câu này có đúng theo bằng chứng không;
(b) đoạn được trích có thực sự hỗ trợ câu này không.
Trả JSON: {"correct": true/false, "supported_by_cited_doc": true/false, "p_correct": 0-1}
```

## F4. Test case hồi quy mẫu

| ID | Tình huống | Kỳ vọng |
|---|---|---|
| TC1 | Gãy cổ xương đùi ngang, hỏi điều trị (P3) | ≥ 2 unit guideline; ≥ 1 unit graph `treated_by`; không cờ cảnh báo; có thể ANSWER_CLEAN nếu đủ điều kiện |
| TC2 | Gãy xương năng lượng thấp, tuổi > 40, hỏi chẩn đoán phân biệt | Red-flag `true` hoặc có unit Neoplastic trong top-8 + `late_neoplastic_signal` |
| TC3 | Entity không link được | `graph_unavailable`; vẫn trả kết quả từ Text |
| TC4 | Triple Neoplastic chưa duyệt khớp truy vấn | Unit kèm `unreviewed`, điểm bị phạt, không ANSWER_CLEAN |
| TC5 | Chunk nói chống chỉ định, triple nói chỉ định | Cả hai có `conflict`, đều có mặt; Stage 7 trình bày cả hai |
| TC6 | KG trả < 5 triple | `kg_sparse`; trọng số text ×1.2 |
| TC7 | Neo4j timeout | `graph_stream_failed`; vẫn trả kết quả Text-only |
| TC8 | Cùng sự thật ở chunk và `triple_only` | Chỉ giữ chunk |
| TC9 | Mention "giòn xương" (alias đời thường) | Link tới `ONT:Osteoporosis` qua alias; `via_lay_alias = true` |
| TC10 | `phase = P1`, chưa có CĐHA, thiếu mức độ nặng | Không lỗi; applicability tối đa Partial; ASK_MORE kèm danh sách thông tin thiếu |
| TC11 | Red-flag có tiêu chí `unknown` | `redflag_indeterminate`; chạy tiếp; không ANSWER_CLEAN |
| TC12 | Mọi evidence chính là NotApplicable | Theo `not_applicable_policy`; mặc định ASK_MORE/ABSTAIN, không ANSWER_CLEAN |
| TC13 | Câu hỏi Prevention | Dùng nhóm `prev`; quan hệ `prevented_by`; có trích dẫn |
| TC14 | Bảng PDF có số liệu | Trích kèm trang/bảng; cờ `parsed_table` |
| TC15 | Cặp counterfactual chỉ đổi vùng giải phẫu | Applicability/quyết định đổi đúng; cặp control đổi thuộc tính không liên quan thì giữ nguyên |
| TC16 | Hết lượt ASK_MORE vẫn thiếu thông tin | ABSTAIN kèm Negative Knowledge Assertion và danh sách thông tin còn thiếu |

---

*Hết tài liệu. Đây là đặc tả thiết kế, không phải kết quả thực nghiệm. Mọi tham số số học là điểm khởi đầu cần tune và kiểm chứng trên dữ liệu thật của bệnh viện; mọi tiêu chí lâm sàng cần bác sĩ chuyên khoa phê duyệt.*
