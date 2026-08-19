# BÁO CÁO ĐÁNH GIÁ ĐỊNH LƯỢNG MÔ HÌNH RAG (evaluation_metrics.md)

Báo cáo khoa học so sánh chi tiết hiệu năng tìm kiếm tài liệu lâm sàng giữa các mốc thực nghiệm: **E0 (No RAG)**, **E1 (Dense)**, **E2 (Sparse)**, **E3 (Vanilla Hybrid)**, **E4 (Ontology Guided)** và **E5 (Full Proposed System với Guardrail A/A/E)** trên 50 ca kiểm thử lâm sàng chuyên sâu.

---

> ## 1. Bảng Ma trận Thực nghiệm Đối chứng Triệt tiêu (Ablation Matrix E0 -> E5)
> 
> | Mốc Thực nghiệm (Exp) | Tầng Truy xuất (Retrieval) | Tầng Tri thức (Ontology) | Tầng Sinh & Quyết định (LLM & Safety) | Recall@1 | MRR | Context Sensitivity (CSI) | Tỉ lệ vi phạm chống chỉ định (CVR) | Decision F1 | Escalation Recall |
> | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | **E0** | `—` (No RAG) | ❌ Không | `Base LLM` | 0.0% | 0.000 | 0.0% | 100.0% *(Ảo giác)* | N/A | 0.0% |
> | **E1** | `Dense` (*PubMedBERT*) | ❌ Không | `Base LLM` | <span style="color:#2ecc71">**80.0%**</span> | <span style="color:#2ecc71">**0.871**</span> | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#2ecc71">**2.0%**</span> | <span style="color:#e74c3c">**29.1%**</span> | <span style="color:#2ecc71">**75.0%**</span> |
> | **E2** | `Sparse` (*BM25*) | ❌ Không | `Base LLM` | <span style="color:#2ecc71">**80.0%**</span> | <span style="color:#2ecc71">**0.833**</span> | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#2ecc71">**0.0%**</span> | <span style="color:#e74c3c">**29.1%**</span> | <span style="color:#2ecc71">**75.0%**</span> |
> | **E3** | `Hybrid` (*BM25 + Dense*) | ❌ Không | `Base LLM` | <span style="color:#2ecc71">**82.0%**</span> | <span style="color:#2ecc71">**0.855**</span> | <span style="color:#e74c3c">**0.0%**</span> | <span style="color:#2ecc71">**0.0%**</span> | <span style="color:#e74c3c">**29.1%**</span> | <span style="color:#2ecc71">**75.0%**</span> |
> | **E4** | `Hybrid` (*BM25 + Dense*) |  **Có Ontology Reranker** | `Base LLM` | <span style="color:#2ecc71">**84.0%**</span> | <span style="color:#2ecc71">**0.877**</span> | <span style="color:#2ecc71">**100.0%**</span> | <span style="color:#2ecc71">**0.0%**</span> | <span style="color:#e74c3c">**29.1%**</span> | <span style="color:#2ecc71">**75.0%**</span> |
> | **E5 (Proposed)** | `Hybrid` (*BM25 + Dense*) |  **Có Ontology Reranker** | **Base LLM + Guardrail `A/A/E`** | <span style="color:#2ecc71">**84.0%**</span> | <span style="color:#2ecc71">**0.877**</span> | <span style="color:#2ecc71">**100.0%**</span> | <span style="color:#2ecc71">**0.0%**</span> | <span style="color:#2ecc71">**90.9%**</span> | <span style="color:#2ecc71">**75.0%**</span> |

---

> ## 2. Chi tiết kết quả kiểm thử trên từng ca lâm sàng (50 Test Cases)
> 
> | Mã Case | Ca kiểm thử | Tài liệu kỳ vọng | E1 (Dense) Top-1 | E2 (Sparse) Top-1 | E3 (Hybrid) Top-1 | E4/E5 (Ontology) Top-1 | Trạng thái E5 |
> | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
> | TC001 | I am a 70-year-old woman with osteoporosis and no fractures. What exercises should I perform to stay active? | `P0001` | `P0001` | `P0001` | `P0001` | `P0001` | ✅ PASS |
> | TC002 | I am a 70-year-old woman with osteoporosis and sustained a vertebral compression fracture 2 weeks ago. What exercises should I perform to stay active? | `P0002` | `P0001` | `P0001` | `P0001` | `P0002` | ✅ PASS |
> | TC003 | I have knee osteoarthritis and my joints are stable. What low-impact aerobic exercises are recommended? | `P0009` | `P0010` | `P0001` | `P0010` | `P0009` | ✅ PASS |
> | TC004 | I have knee osteoarthritis and my joints are swelling today with an acute flare-up. Can I do jumping exercises? | `P0010` | `P0010` | `P0010` | `P0010` | `P0010` | ✅ PASS |
> | TC005 | I have rheumatoid arthritis in stable remission. Can I do low-impact walking and cycling? | `P0015` | `P0015` | `P0015` | `P0015` | `P0015` | ✅ PASS |
> | TC006 | My rheumatoid arthritis is active and joints are inflamed with severe synovitis. Should I perform heavy weightlifting? | `P0016` | `P0016` | `P0016` | `P0016` | `P0016` | ✅ PASS |
> | TC007 | I am looking for surgical options and sequestrectomy for chronic osteomyelitis bone infection. | `P0030` | `P0030` | `P0030` | `P0030` | `P0030` | ✅ PASS |
> | TC008 | I have active osteomyelitis bone infection with bone suppuration. Can I stand and walk on my leg? | `P0028` | `P0028` | `P0028` | `P0028` | `P0029` | ❌ FAIL |
> | TC009 | How can I prevent my spine from fusing in ankylosing spondylitis with daily stretching? | `P0034` | `P0034` | `P0034` | `P0034` | `P0034` | ✅ PASS |
> | TC010 | Why is heavy weightlifting and contact sports contraindicated in advanced ankylosing spondylitis with bamboo spine? | `P0035` | `P0035` | `P0035` | `P0035` | `P0035` | ✅ PASS |
> | TC011 | I am a 72-year-old woman with osteoporosis. What pharmacological bisphosphonate medications should I take? | `P0003` | `P0003` | `P0001` | `P0001` | `P0001` | ❌ FAIL |
> | TC012 | I am a 72-year-old woman with osteoporosis. How can I modify my home environment to prevent falls? | `P0006` | `P0001` | `P0001` | `P0001` | `P0007` | ❌ FAIL |
> | TC013 | I have knee osteoarthritis. What oral NSAID medications are recommended to manage joint inflammation and pain? | `P0011` | `P0011` | `P0011` | `P0011` | `P0011` | ✅ PASS |
> | TC014 | I have knee osteoarthritis. When is total knee replacement arthroplasty surgery indicated? | `P0013` | `P0013` | `P0013` | `P0013` | `P0013` | ✅ PASS |
> | TC015 | What is the first-line immunosuppressant DMARD medication used for rheumatoid arthritis? | `P0017` | `P0017` | `P0017` | `P0017` | `P0017` | ✅ PASS |
> | TC016 | What are the indications for surgical synovectomy joint lining removal in rheumatoid arthritis? | `P0021` | `P0021` | `P0021` | `P0021` | `P0021` | ✅ PASS |
> | TC017 | I am experiencing an acute gout attack. Is it okay to eat red meat, organ meats, or seafood? | `P0022` | `P0022` | `P0022` | `P0022` | `P0022` | ✅ PASS |
> | TC018 | Can I start allopurinol urate-lowering medication therapy during an active gout flare up? | `P0024` | `P0024` | `P0024` | `P0024` | `P0024` | ✅ PASS |
> | TC019 | What is the recommended daily protein intake for older adults to treat sarcopenia? | `P0039` | `P0039` | `P0039` | `P0039` | `P0039` | ✅ PASS |
> | TC020 | What progressive resistance training exercises help build muscle mass in sarcopenia? | `P0040` | `P0040` | `P0040` | `P0040` | `P0040` | ✅ PASS |
> | TC021 | I have knee osteoarthritis and active peptic ulcer disease. Can I take oral NSAID painkillers? | `P0051` | `P0051` | `P0051` | `P0051` | `P0051` | ✅ PASS |
> | TC022 | I have knee osteoarthritis and stage 4 chronic kidney disease. What pain relief is safe without oral NSAIDs? | `P0052` | `P0011` | `P0052` | `P0052` | `P0052` | ✅ PASS |
> | TC023 | I am having an acute gout attack and have chronic kidney disease. Why are colchicine and NSAIDs contraindicated? | `P0053` | `P0053` | `P0053` | `P0053` | `P0053` | ✅ PASS |
> | TC024 | I have severe osteoporosis and stage 5 renal failure. Why are bisphosphonates contraindicated? | `P0054` | `P0054` | `P0054` | `P0054` | `P0054` | ✅ PASS |
> | TC025 | I have osteoporosis and end-stage hip osteoarthritis. How can I exercise without high impact loading? | `P0055` | `P0055` | `P0055` | `P0055` | `P0055` | ✅ PASS |
> | TC026 | I have joint pain. What medicine should I take? | `P0011` | `P0051` | `P0009` | `P0009` | `P0009` | ❌ FAIL |
> | TC027 | My leg is swollen and hurts today. Can I exercise? | `P0010` | `P0015` | `P0048` | `P0048` | `P0015` | ❌ FAIL |
> | TC028 | I have severe back pain. Should I have surgery or take pills? | `P0002` | `P0790` | `P0013` | `P0045` | `P0013` | ❌ FAIL |
> | TC029 | I have severe osteoporosis with multiple spine fractures. Is Teriparatide suitable? | `P0005` | `P0005` | `P0005` | `P0005` | `P0005` | ✅ PASS |
> | TC030 | Can I practice Tai Chi to improve my stability and prevent falls with osteoporosis? | `P0007` | `P0007` | `P0007` | `P0007` | `P0007` | ✅ PASS |
> | TC031 | I am starting alendronate bisphosphonates. Do I need to take calcium or Vitamin D? | `P0004` | `P0004` | `P0004` | `P0004` | `P0004` | ✅ PASS |
> | TC032 | Can estrogen hormone replacement therapy prevent bone loss in postmenopausal osteoporosis? | `P0008` | `P0008` | `P0008` | `P0008` | `P0008` | ✅ PASS |
> | TC033 | Are intra-articular corticosteroid injections effective for rapid knee osteoarthritis pain relief? | `P0012` | `P0012` | `P0012` | `P0012` | `P0012` | ✅ PASS |
> | TC034 | How much does weight loss reduce mechanical joint load in knee osteoarthritis? | `P0014` | `P0014` | `P0014` | `P0014` | `P0014` | ✅ PASS |
> | TC035 | Why do I need to take folic acid together with methotrexate for rheumatoid arthritis? | `P0018` | `P0017` | `P0019` | `P0017` | `P0017` | ❌ FAIL |
> | TC036 | Can I take prednisone as a bridge before my rheumatoid arthritis methotrexate works? | `P0019` | `P0017` | `P0019` | `P0019` | `P0019` | ✅ PASS |
> | TC037 | Are JAK inhibitors like tofacitinib effective for moderate to severe rheumatoid arthritis? | `P0020` | `P0020` | `P0020` | `P0020` | `P0020` | ✅ PASS |
> | TC038 | How quickly should colchicine be taken after an acute gout attack starts? | `P0023` | `P0023` | `P0024` | `P0023` | `P0023` | ✅ PASS |
> | TC039 | What is the target serum urate level for long-term gout management? | `P0025` | `P0025` | `P0025` | `P0025` | `P0025` | ✅ PASS |
> | TC040 | Can probenecid uricosuric medication help lower uric acid in chronic gout? | `P0026` | `P0026` | `P0026` | `P0026` | `P0026` | ✅ PASS |
> | TC041 | What are the indications for surgical removal of gouty tophi? | `P0027` | `P0027` | `P0027` | `P0027` | `P0027` | ✅ PASS |
> | TC042 | Why is hyperbaric oxygen therapy used as an adjunctive treatment for osteomyelitis? | `P0031` | `P0031` | `P0031` | `P0031` | `P0031` | ✅ PASS |
> | TC043 | What care is required for vertebral osteomyelitis spinal infection? | `P0032` | `P0028` | `P0032` | `P0032` | `P0032` | ✅ PASS |
> | TC044 | My father has a diabetic foot ulcer and bone infection. What should we evaluate? | `P0033` | `P0033` | `P0033` | `P0033` | `P0033` | ✅ PASS |
> | TC045 | Are TNF inhibitor biologics like adalimumab effective for ankylosing spondylitis spine stiffness? | `P0036` | `P0036` | `P0034` | `P0035` | `P0034` | ❌ FAIL |
> | TC046 | I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness? | `P0037` | `P0037` | `P0037` | `P0037` | `P0037` | ✅ PASS |
> | TC047 | What sleeping position and mattress is recommended for ankylosing spondylitis postural alignment? | `P0038` | `P0038` | `P0038` | `P0038` | `P0038` | ✅ PASS |
> | TC048 | Can creatine supplementation combined with exercise improve muscle gains in sarcopenia? | `P0041` | `P0041` | `P0041` | `P0041` | `P0041` | ✅ PASS |
> | TC049 | How is nutritional rickets in children treated with high-dose Vitamin D therapy? | `P0042` | `P0042` | `P0042` | `P0042` | `P0042` | ✅ PASS |
> | TC050 | I have fibrous dysplasia and my hip bone is bending like a shepherd crook. What surgical management is needed? | `P0050` | `P0050` | `P0050` | `P0050` | `P0050` | ✅ PASS |

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
