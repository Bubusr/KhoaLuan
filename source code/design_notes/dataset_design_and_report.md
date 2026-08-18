# Thiết kế & Báo cáo Chi tiết Dữ liệu RAG Lâm sàng (dataset_design_and_report.md)

Tài liệu này tích hợp toàn diện phương pháp luận thiết kế, quy trình xây dựng và báo cáo số liệu định lượng thực tế của **Ngữ liệu nguồn (Corpus)** và **Bộ dữ liệu kiểm thử (Clinical QA)** trong hệ sinh thái RAG y khoa.

---

## 1. Thiết kế cấu trúc Dữ liệu trong RAG Lâm sàng

Một hệ thống RAG phục vụ y khoa yêu cầu hai tập dữ liệu hoạt động song song để đảm bảo tính chính xác và an toàn:

```text
  [1. Ngữ liệu Nguồn (Corpus)]             [2. Dữ liệu đối chứng (Evaluation QA)]
  (Sách giáo khoa, Phác đồ chuẩn)          (Ca bệnh giả định, Câu hỏi kiểm thử)
              │                                              │
              ▼                                              ▼
     [ Vector Database ] ◄─────────────────────────── [ RAG Evaluator ]
```

1.  **Ngữ liệu nguồn (Corpus)**: Đóng vai trò là "bộ nhớ tri thức". Đây là căn cứ y văn duy nhất mà hệ thống RAG được phép tham chiếu để sinh câu trả lời, loại bỏ tối đa hiện tượng ảo giác (hallucination).
2.  **Bộ câu hỏi đối chứng (Clinical QA Dataset)**: Đóng vai trò là "bộ đề thi". Chứa các ca lâm sàng giả định thực tế kèm đáp án chuẩn từ chuyên gia để đánh giá chất lượng RAG qua các mức độ an toàn.

---

## 2. Quy trình 4 bước Xây dựng Dataset (Construction Pipeline)

```text
  [Thu thập PDF] ──► [Chunking Khuyến nghị] ──► [Dán nhãn Ontology] ──► [Sinh ca bệnh QA]
```

*   **Bước 1: Thu thập và số hóa tài liệu**: Tải các tài liệu phác đồ điều trị từ các nguồn uy tín quốc tế (WHO, AAOS, ACR) và Bộ Y tế Việt Nam, trích xuất văn bản bảo toàn cấu trúc bảng biểu.
*   **Bước 2: Phân đoạn (Chunking) theo Khuyến nghị**:
    *   *Kích thước phân đoạn (Chunk Size)*: Trung bình dao động từ **50 đến 100 tokens** (khoảng 40 đến 80 từ) cho mỗi chunk. Kích thước này tối ưu tuyệt đối cho giới hạn đầu vào của PubMedBERT (512 tokens), đảm bảo không có từ nào bị cắt cụt.
    *   *Độ chồng lấp (Chunk Overlap)*: Thiết lập **chồng lấp 1 câu (1-Sentence Overlap)** (khoảng 10-20 tokens). Đây là thiết kế tiêu chuẩn trong RAG y tế (Medical RAG) nhằm bảo toàn tính liên tục của lập luận lâm sàng và bối cảnh y khoa giữa các phân đoạn kề nhau thuộc cùng một tài liệu hướng dẫn.
*   **Bước 3: Gán nhãn thực thể y khoa (Ontology Tagging)**: Gán siêu dữ liệu (metadata) y khoa cho từng chunk bao gồm: Bệnh lý (`disease`), Vùng giải phẫu (`anatomy`), Trạng thái lâm sàng (`clinical_state`), và danh sách Chống chỉ định tương ứng (`contraindications`).
*   **Bước 4: Tạo bộ câu hỏi đối chứng (Clinical QA Generation)**: Sử dụng phương pháp **LLM-assisted Case Generation** để sinh các ca bệnh giả định dưới dạng câu hỏi tự nhiên của bệnh nhân. Sau đó, các câu hỏi này được kiểm duyệt và hiệu chỉnh thủ công bởi bác sĩ/chuyên gia để đảm bảo chất lượng y khoa.

## 3. Báo cáo Chi tiết và Định lượng Ngữ liệu nguồn (Corpus Report)

### 3.1. Nguồn gốc y văn quốc tế
Dữ liệu ngữ liệu được tuyển chọn chuyên khoa từ các bộ tài liệu hướng dẫn lâm sàng trực tuyến uy tín nhất:
1.  **Tổ chức Y tế Thế giới (WHO)**: [WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)](https://www.who.int/publications/i/item/9789240015128) - Hướng dẫn vận động cho người có bệnh lý mãn tính.
2.  **Hiệp hội Phẫu thuật Chấn thương Chỉnh hình Hoa Kỳ (AAOS)**: [AAOS Clinical Practice Guideline on Spinal Compression Fractures (2018)](https://www.aaos.org/globalassets/quality-and-practice-resources/spinal-compression-fractures/vcfcpg.pdf) - Phác đồ điều trị bảo tồn sau gãy xương cột sống.
3.  **Hiệp hội Thấp khớp học Hoa Kỳ (ACR)**: [ACR Clinical Practice Guidelines (2020)](https://rheumatology.org/clinical-practice-guidelines) - Các khuyến nghị điều trị thoái hóa khớp gối, viêm khớp dạng thấp và gút cấp tính.

### 3.2. Số liệu định lượng của Corpus (v0.1.0)
*   **Tổng số Chunks**: 200 tài liệu y văn lâm sàng được chuẩn hóa (gồm 100 chunks chuyên khoa cho 10 bệnh lý chính và 100 chunks nhiễu/giả lập).
*   **Tổng số câu chuyên ngành**: ~950 câu.
*   **Tổng số từ**: ~14,000 từ.
*   **Các bệnh lý bổ sung mở rộng**: Ngoài 5 bệnh lý cơ bản, corpus đã được bổ sung thêm 5 bệnh xương khớp chuyên khoa sâu gồm: *Viêm cột sống dính khớp (Ankylosing Spondylitis), Teo cơ (Sarcopenia), Còi xương & Nhuyễn xương (Rickets & Osteomalacia), Bệnh Paget xương (Paget's Disease), và Loạn sản xơ xương (Fibrous Dysplasia)*.

### Bảng danh sách chi tiết các Chunk tri thức tiêu biểu (P001 - P020):

| Mã Chunk | Tên tài liệu nguồn (Title) | Nguồn trích xuất | Số câu | Số từ | Từ khóa Ontology gán nhãn | Chống chỉ định (Contraindications) |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| [**P001**](../versions/v0.1.0/data/corpus/corpus.json#L2-L12) | General Physical Activity Guidelines for Osteoporosis | [WHO (2020)](https://www.who.int/publications/i/item/9789240015128) | 4 | 63 | `Osteoporosis`, `LowImpactExercise`, `HighImpactExercise`, `Rehabilitation` | Không có |
| [**P002**](../versions/v0.1.0/data/corpus/corpus.json#L13-L27) | Acute Vertebral Compression Fracture Conservative Management | [AAOS (2018)](https://www.aaos.org/globalassets/quality-and-practice-resources/spinal-compression-fractures/vcfcpg.pdf) | 5 | 71 | `VertebralFracture`, `AcutePostFracture`, `Rest`, `HighImpactExercise`, `Safety` | `HighImpactExercise` |
| [**P003**](../versions/v0.1.0/data/corpus/corpus.json#L28-L38) | Post-Acute Rehabilitation after Spinal Fracture | [AAOS (2018)](https://www.aaos.org/globalassets/quality-and-practice-resources/spinal-compression-fractures/vcfcpg.pdf) | 5 | 77 | `VertebralFracture`, `Stable`, `LowImpactExercise`, `Rehabilitation` | Không có |
| [**P004**](../versions/v0.1.0/data/corpus/corpus.json#L39-L46) | Bisphosphonates for Postmenopausal Osteoporosis | [AAOS (2018)](https://www.aaos.org/globalassets/quality-and-practice-resources/spinal-compression-fractures/vcfcpg.pdf) | 4 | 55 | `Osteoporosis`, `Medication` | Không có |
| [**P005**](../versions/v0.1.0/data/corpus/corpus.json#L47-L56) | Fall Prevention Strategies in Older Adults with Osteoporosis | [WHO (2020)](https://www.who.int/publications/i/item/9789240015128) | 5 | 76 | `Osteoporosis`, `LowImpactExercise`, `Safety` | Không có |
| [**P006**](../versions/v0.1.0/data/corpus/corpus.json#L57-L72) | Osteoarthritis Knee Exercise Guidelines | [ACR (2020)](https://rheumatology.org/clinical-practice-guidelines) | 4 | 67 | `Osteoarthritis`, `Knee`, `FlareUp`, `WaterExercise`, `HighImpactExercise`, `Safety` | `HighImpactExercise` |
| [**P007**](../versions/v0.1.0/data/corpus/corpus.json#L73-L87) | Rheumatoid Arthritis Active Phase Management | [ACR (2020)](https://rheumatology.org/clinical-practice-guidelines) | 4 | 64 | `RheumatoidArthritis`, `JointInflammation`, `ROMStretching`, `HeavyResistance`, `Safety` | `HeavyResistance` |
| [**P008**](../versions/v0.1.0/data/corpus/corpus.json#L88-L102) | Conservative Management of Acute Gouty Arthritis | [ACR (2020)](https://rheumatology.org/clinical-practice-guidelines) | 4 | 60 | `Gout`, `AcuteGoutAttack`, `Hydration`, `PurineRichFood`, `Safety` | `PurineRichFood` |
| [**P009**](../versions/v0.1.0/data/corpus/corpus.json#L103-L117) | Clinical Management of Osteomyelitis bone infection | Textbook | 4 | 72 | `Osteomyelitis`, `ActiveInfection`, `AntibioticTherapy`, `WeightBearing`, `Safety` | `WeightBearing` |
| [**P010**](../versions/v0.1.0/data/corpus/corpus.json#L118-L124) | Denosumab Therapy for Severe Osteoporosis | Textbook | 3 | 48 | `Osteoporosis`, `Medication` | Không có |
| [**P011**](../versions/v0.1.0/data/corpus/corpus.json#L125-L131) | Teriparatide and Bone Anabolic Therapy | Textbook | 3 | 45 | `Osteoporosis`, `Medication` | Không có |
| [**P012**](../versions/v0.1.0/data/corpus/corpus.json#L132-L138) | NSAIDs and Pain Relief in Osteoarthritis | Textbook | 3 | 49 | `Osteoarthritis`, `JointInflammation` | Không có |
| [**P013**](../versions/v0.1.0/data/corpus/corpus.json#L139-L145) | Intra-articular Corticosteroid Injections | Textbook | 3 | 46 | `Osteoarthritis`, `JointInflammation` | Không có |
| [**P014**](../versions/v0.1.0/data/corpus/corpus.json#L146-L152) | Methotrexate and DMARDs for Rheumatoid Arthritis | Textbook | 3 | 47 | `RheumatoidArthritis` | Không có |
| [**P015**](../versions/v0.1.0/data/corpus/corpus.json#L153-L159) | Biologic Agents for Refractory Rheumatoid Arthritis | Textbook | 3 | 48 | `RheumatoidArthritis` | Không có |
| [**P016**](../versions/v0.1.0/data/corpus/corpus.json#L160-L166) | Allopurinol for Long-term Gout Management | Textbook | 3 | 49 | `Gout` | Không có |
| [**P017**](../versions/v0.1.0/data/corpus/corpus.json#L167-L173) | Surgical Interventions for Osteomyelitis | Textbook | 3 | 45 | `Osteomyelitis`, `ActiveInfection` | Không có |
| [**P018**](../versions/v0.1.0/data/corpus/corpus.json#L174-L180) | Kyphoplasty and Vertebroplasty for Spine Fractures | Textbook | 3 | 46 | `VertebralFracture` | Không có |
| [**P019**](../versions/v0.1.0/data/corpus/corpus.json#L181-L187) | Dietary Calcium and Vitamin D Intake for Bone Health | Textbook | 3 | 45 | `Osteoporosis` | Không có |
| [**P020**](../versions/v0.1.0/data/corpus/corpus.json#L188-L194) | Resistance Training and Muscle Strengthening | Textbook | 3 | 46 | `LowImpactExercise` | Không có |

*Ghi chú: Toàn bộ 180 chunks còn lại (từ P021 đến P200) được lưu trữ và lập chỉ mục đầy đủ tại file cơ sở dữ liệu hệ thống.*

---

## 4. Ý nghĩa thực tiễn đối chứng trong Đánh giá An toàn

Tập dữ liệu này được cấu trúc có chủ đích làm **Dữ liệu đối chứng kiểm thử (Vignettes)** để kiểm nghiệm tính an toàn lâm sàng. Việc đan xen giữa các khuyến nghị tập nặng cho bệnh nhân ổn định (`P001`) và các chống chỉ định nghiêm ngặt của bệnh nhân trong giai đoạn cấp tính (`P002`, `P006`, `P007`, `P008`, `P009`) bắt buộc hệ thống RAG phải phân tích ngữ cảnh thật chính xác để không đưa ra lời khuyên sai lầm gây nguy hại trực tiếp đến sức khỏe của bệnh nhân.
