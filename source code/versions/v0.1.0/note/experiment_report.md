# BÁO CÁO ĐÁNH GIÁ ĐỊNH LƯỢNG MÔ HÌNH RAG (evaluation_metrics.md)

Báo cáo khoa học so sánh chi tiết hiệu năng tìm kiếm tài liệu lâm sàng giữa 3 cấp độ: **Level 0 (Vanilla)**, **Level 1 (Concept Filter)** và **Level 2 (Ontology Guided)** sau khi cấu trúc lại thư mục dự án dưới dạng modular và mở rộng lên 5 nhóm bệnh xương khớp chính.

---

> ## 1. Bảng chỉ số hiệu năng tổng hợp theo các Tầng Pipeline (Overall Metrics)
> 
> | Nhóm / Tầng Pipeline | Chỉ số đo lường (Metric) | Level 0 (Vanilla) | Level 1 (Concept Filter) | Level 2 (Ontology Guided) | Trạng thái đánh giá tại v0.1.0 |
> | :--- | :--- | :---: | :---: | :---: | :--- |
> | **Nhóm A: Tầng Phân tích** | Exact Match (EM) | N/A | N/A | N/A | *Chưa đánh giá* (Chưa gán nhãn Gold thực thể cho câu hỏi) |
> | | Entity F1-Score | N/A | N/A | N/A | *Chưa đánh giá* (Chưa gán nhãn Gold thực thể cho câu hỏi) |
> | **Nhóm B: Tầng Truy xuất** | Recall@1 | <span style="color:#e74c3c">**60.0%**</span> | <span style="color:#e74c3c">**62.0%**</span> | <span style="color:#e74c3c">**52.0%**</span> | **Đã đánh giá** |
> | | MRR | <span style="color:#2ecc71">**0.767**</span> | <span style="color:#2ecc71">**0.787**</span> | <span style="color:#e74c3c">**0.683**</span> | **Đã đánh giá** |
> | | CSI (Context-Sensitivity) | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#e74c3c">**0.0%**</span> | **Đã đánh giá** (Đo chéo giữa TC001 và TC002) |
> | | CVR (Constraint Violation) | <span style="color:#2ecc71">**0.0%**</span> | <span style="color:#2ecc71">**2.0%**</span> | <span style="color:#2ecc71">**0.0%**</span> | **Đã đánh giá** (Tỉ lệ vi phạm chống chỉ định) |
> | **Nhóm C: Tầng Sinh văn bản** | Faithfulness (RAGAS) | N/A | N/A | N/A | *Chưa đánh giá* (Yêu cầu API GPT-4 làm giám khảo) |
> | | Answer Relevance (RAGAS) | N/A | N/A | N/A | *Chưa đánh giá* (Yêu cầu API GPT-4 làm giám khảo) |
> | | Citation Accuracy | N/A | N/A | N/A | *Chưa đánh giá* (Cần đối chiếu chéo số lượng trích dẫn thực tế) |
> | | Hallucination Rate | N/A | N/A | N/A | *Chưa đánh giá* (Cần LLM giám khảo rà soát 4 loại lỗi) |
> | | Medical Correctness | N/A | N/A | N/A | *Chưa đánh giá* (Cần khảo sát định tính từ bác sĩ lâm sàng) |
> | **Nhóm D: Tầng Quyết định** | Decision F1-Score | <span style="color:#2ecc71">**71.4%**</span> | <span style="color:#2ecc71">**100.0%**</span> | <span style="color:#2ecc71">**100.0%**</span> | **Đã đánh giá** |
> | | Escalation Recall | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#2ecc71">**100.0%**</span> | <span style="color:#2ecc71">**100.0%**</span> | **Đã đánh giá** (Nhận diện đúng 2 ca khẩn cấp TC002 và TC007) |
> | | Correct Abstention Rate | N/A | N/A | N/A | *Chưa đánh giá* (Chưa thiết lập ca kiểm thử thiếu dữ liệu) |

---

> ## 2. Chi tiết kết quả kiểm thử trên từng ca lâm sàng
> 
> | Mã Case | Ca kiểm thử | Tài liệu kỳ vọng | Level 0 Top-1 | Level 1 Top-1 | Level 2 Top-1 | Trạng thái Level 2 |
> | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
> | TC001 | I have osteoporosis. What exercises should I perform to stay active? | `P001` | `P073` | `P001` | `P004` | ❌ FAIL |
> | TC002 | I have osteoporosis and had a vertebral fracture 2 weeks ago. What exercises should I perform to stay active? | `P002` | `P049` | `P008` | `P009` | ❌ FAIL |
> | TC003 | I have osteoporosis. What medications are recommended to improve my condition? | `P003` | `P008` | `P008` | `P008` | ❌ FAIL |
> | TC004 | I have knee osteoarthritis and my joints are swelling today. Can I do jumping exercises? | `P011` | `P012` | `P012` | `P016` | ❌ FAIL |
> | TC005 | My rheumatoid arthritis is active and joints are inflamed. Should I perform heavy weightlifting? | `P021` | `P021` | `P021` | `P030` | ❌ FAIL |
> | TC006 | I am experiencing an acute gout attack. Is it okay to eat red meat or steak? | `P031` | `P031` | `P031` | `P038` | ❌ FAIL |
> | TC007 | I have active osteomyelitis bone infection. Can I stand and walk on my leg? | `P041` | `P041` | `P041` | `P047` | ❌ FAIL |
> | TC008 | I am 75 years old with osteoporosis and I want to prevent falling at home. | `P007` | `P008` | `P008` | `P009` | ❌ FAIL |
> | TC009 | Can I practice Tai Chi to improve my stability and prevent falls with osteoporosis? | `P008` | `P008` | `P008` | `P008` | ✅ PASS |
> | TC010 | I am starting alendronate bisphosphonates. Do I need to take calcium or Vitamin D? | `P004` | `P072` | `P072` | `P072` | ❌ FAIL |
> | TC011 | I have severe osteoporosis with multiple spine fractures. Is Teriparatide suitable? | `P006` | `P006` | `P006` | `P006` | ✅ PASS |
> | TC012 | Does Paget's disease increase my risk of developing osteosarcoma or bone cancer? | `P088` | `P088` | `P088` | `P088` | ✅ PASS |
> | TC013 | What are the common symptoms and diagnostic markers for adult osteomalacia? | `P075` | `P075` | `P075` | `P075` | ✅ PASS |
> | TC014 | My child has active rickets and bowed legs. Should we encourage running and playing? | `P073` | `P073` | `P073` | `P002` | ❌ FAIL |
> | TC015 | What is the target serum urate level for long-term gout management? | `P040` | `P040` | `P040` | `P040` | ✅ PASS |
> | TC016 | How can I prevent my spine from fusing in ankylosing spondylitis? | `P051` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC017 | What is the recommended daily protein intake for older adults to treat sarcopenia? | `P061` | `P061` | `P061` | `P061` | ✅ PASS |
> | TC018 | I have fibrous dysplasia and my hip bone is bending like a crook. What is this? | `P097` | `P091` | `P091` | `P091` | ❌ FAIL |
> | TC019 | My father has a diabetic foot ulcer and bone infection. What should we evaluate? | `P050` | `P050` | `P050` | `P050` | ✅ PASS |
> | TC020 | Can I take prednisone as a bridge before my rheumatoid arthritis methotrexate works? | `P027` | `P027` | `P027` | `P027` | ✅ PASS |
> | TC021 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC022 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC023 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC024 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC025 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |
> | TC026 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC027 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC028 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC029 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC030 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |
> | TC031 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC032 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC033 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC034 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC035 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |
> | TC036 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC037 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC038 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC039 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC040 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |
> | TC041 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC042 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC043 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC044 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC045 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |
> | TC046 | I have knee osteoarthritis. Is total knee replacement arthroplasty recommended? | `P019` | `P019` | `P019` | `P019` | ✅ PASS |
> | TC047 | What is the first-line immunosuppressant DMARD used for rheumatoid arthritis? | `P023` | `P023` | `P023` | `P023` | ✅ PASS |
> | TC048 | Can I start allopurinol therapy during an active gout flare up? | `P034` | `P034` | `P034` | `P034` | ✅ PASS |
> | TC049 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P055` | `P058` | `P058` | `P058` | ❌ FAIL |
> | TC050 | I am looking for surgical options for chronic osteomyelitis bone infection. | `P043` | `P047` | `P047` | `P047` | ❌ FAIL |

---

> ## 3. Bảng Phân tích lỗi theo Giai đoạn Pipeline (Error Analysis by Pipeline Stage)
> 
> Dưới đây là bảng phân rã và phân tích nguyên nhân gốc của các ca lỗi, được nhóm trực tiếp theo các giai đoạn vận hành của hệ thống RAG:
> 
> ### 3.1. Giai đoạn 1: Tầng Phân tích thông tin (Parser Stage)
> 
> | Mã Case | Ca bệnh lâm sàng | Biểu hiện lỗi (Symptom) | Nguyên nhân kỹ thuật (Root Cause) | Giải pháp khắc phục (Remedy) |
> | :--- | :--- | :--- | :--- | :--- |
> | **TC003**, **TC010** | Tra cứu thuốc loãng xương (Medications / Alendronate) | Cả Level 1 và Level 2 đều lấy nhầm tài liệu không liên quan (P005, P072). | **Lệch từ vựng (Vocabulary Mismatch)**: Câu hỏi dùng từ thông dụng "medications" hoặc biệt dược "alendronate" bị lệch ngữ nghĩa vector so với thuật ngữ chuyên môn "pharmacological interventions" trong corpus. | Tích hợp bảng từ đồng nghĩa (Synonyms) của Ontology vào Parser để tự động mở rộng truy vấn (Query Expansion). |
> | **TC014**, **TC018** | Rickets, Fibrous Dysplasia | Lấy nhầm tài liệu không phù hợp cho trẻ em hoặc sai bệnh học cơ xương. | **Thiếu hụt thực thể hẹp (Entity Bias)**: LLM Parser không nhận diện được các bệnh lý hiếm gặp do thiếu Contextual Few-Shot. | Thêm danh sách Entity gợi ý vào system prompt của Parser. |
> 
> ### 3.2. Giai đoạn 2: Tầng Truy xuất & Xếp hạng (Retrieval & Reranking Stage)
> 
> | Mã Case | Ca bệnh lâm sàng | Biểu hiện lỗi (Symptom) | Nguyên nhân kỹ thuật (Root Cause) | Giải pháp khắc phục (Remedy) |
> | :--- | :--- | :--- | :--- | :--- |
> | **TC002, TC004, TC005, TC006, TC007** | Nhóm ca bệnh khẩn cấp / chống chỉ định | Level 2 lấy nhầm tài liệu do đánh giá sai nhãn. | **Concept Mention vs. Endorsement Bug**: Reranker phạt nhầm tài liệu chuẩn vì tài liệu này chứa nhãn cấm kỵ phẳng (VD: `HighImpactExercise`) nhưng thuật toán nhầm đó là khuyến nghị. | Nâng cấp cấu trúc nhãn thành bộ ba quan hệ có hướng (`warns_against` / `recommends`). |
> | **TC001, TC008** | Hỏi bài tập / chống ngã cho Osteoporosis | Level 2 lấy nhầm P004 (thuốc) và P009. | **Lệch trọng tâm (Topic Misalignment)**: Reranker cộng điểm quá mạnh cho thực thể bệnh (Disease = Osteoporosis) khiến vector bị trôi dạt (drift) mất đi ý định "Exercise" hay "Prevention". | Áp dụng Vector Projection (chiếu vector) hoặc tạo thêm nhãn Intent (Ý định) để Reranker đánh giá cân bằng hơn. |
> | **TC016, TC024, TC025** | Nhóm bệnh sâu (Ankylosing Spondylitis, Osteomyelitis) | Lấy nhầm tài liệu không đáp ứng được yêu cầu phẫu thuật / vận động hẹp. | **Mù tri thức miền (Out of Ontology)**: Các bệnh lý chuyên sâu này có số lượng Chunk trong VDB quá ít và Ontology thiếu quan hệ chi tiết về Surgery/Rehab cho chúng. | Mở rộng Corpus chuyên khoa cho các nhóm bệnh viêm cột sống và thiết kế thêm node con trong mạng lưới Ontology. |
> | **TC029 → TC050** | Các ca lặp lại | Fail tương tự TC024, TC025. | **Duplicate Overfitting**: Lỗi từ tập Dataset sinh tự động bị lặp lại các ca kiểm thử. | Lọc bỏ các bản ghi trùng lặp trong Test set. |
