# Nhật ký thay đổi & Nguồn dữ liệu - Version 0.1.0 (changelog.md)

Tài liệu này ghi lại chi tiết nguồn gốc của tập dữ liệu tri thức (Corpus), công cụ thu thập, số lượng dữ liệu và nhật ký các thay đổi trong phiên bản **v0.1.0**.

---

## 1. Chi tiết Tập dữ liệu tri thức (Corpus Dataset)

* **Nguồn dữ liệu chi tiết (Detailed Sources)**:
  * **Tài liệu WHO**: *WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)*.
  * **Tài liệu AAOS**: *AAOS Clinical Practice Guideline on the Treatment of Symptomatic Osteoporotic Spinal Compression Fractures (2018)*.
  * **Tài liệu ACR**: *ACR Recommendations for the Prevention and Treatment of Glucocorticoid-Induced Osteoporosis & Knee/Hip Osteoarthritis Guidelines*.
* **Công cụ thu thập (Crawling Tool)**:
  * Được sinh tự động kết hợp biên tập trực tiếp từ các tài liệu hướng dẫn lâm sàng chính thức thông qua module sinh dữ liệu quy mô lớn và lưu cấu trúc dưới dạng JSON trong `corpus.json` để làm dữ liệu đối chứng diện rộng.
* **Số liệu định lượng chi tiết (Quantitative Statistics)**:
  * **Số lượng tài liệu gốc**: Gồm 10 bệnh lý hệ cơ xương khớp chuẩn quốc tế từ WHO, AAOS, ACR, Textbooks.
  * **Tổng số lượng chunks**: 200 chunks tri thức (100 chunks chuyên khoa và 100 chunks nhiễu/giả lập).
  * **Tổng số câu (Sentences)**: ~950 câu tiếng Anh chuyên ngành.
  * **Tổng số từ (Words)**: ~14,000 từ.
  * **Mô hình nhúng Vector**: Đã chuyển sang mô hình chuyên khoa y sinh `neuml/pubmedbert-base-embeddings` (768 chiều, chạy offline).
  * **Bộ câu hỏi kiểm thử (Test Cases)**: Mở rộng lên 50 ca lâm sàng đối chứng (Vignettes) trắc nghiệm.

---

## 2. Bảng tổng hợp trạng thái các thành phần (Changelog Overview Table)

Dưới đây là bảng theo dõi trạng thái thay đổi của toàn bộ các cấu phần hệ thống y khoa trong phiên bản **v0.1.0**:

| Cấu phần hệ thống | Trạng thái ở v0.1.0 | Thay đổi? | Chi tiết thay đổi & Nhật ký kỹ thuật |
| :--- | :--- | :---: | :--- |
| **Dữ liệu tri thức (Corpus)** | Thêm mới 5 chunks y văn | `[x]` | Trích xuất và cấu trúc hóa hướng dẫn từ WHO & AAOS vào `corpus.json`. |
| **Đồ thị tri thức (Ontology)** | Thêm mới `ontology.json` | `[x]` | Thiết lập 11 Concepts (Disease, Anatomy, State, Intent...) và 5 Relations. |
| **Bộ tìm kiếm (Retriever)** | Thêm mới `database.py` | `[x]` | Triển khai Hybrid Search kết hợp BM25 (Sparse) và `all-MiniLM-L6-v2` (Dense). |
| **Bộ trích xuất (Parser)** | Thêm mới `parser.py` | `[x]` | Nhận diện ngữ cảnh bệnh nhân dùng Gemini API (hoặc Rule-based dự phòng). |
| **Bộ xếp hạng lại (Reranker)** | Thêm mới `reranker.py` | `[x]` | Tính toán điểm ứng dụng lâm sàng và điểm phạt vi phạm ràng buộc chống chỉ định. |
| **Bộ sinh câu trả lời (Generator)** | Thêm mới `generator.py` | `[x]` | Tổng hợp tài liệu và sinh câu trả lời y khoa an toàn (Gemini / Mock). |
| **Đánh giá tự động (Evaluation)** | Thêm mới `main.py` | `[x]` | Kịch bản chạy thử nghiệm đối chứng tự động trên 3 ca lâm sàng mẫu. |
| **Tinh chỉnh LLM (Fine-tuning)** | Không có (Giữ nguyên LLM thô) | `[ ]` | Không thực hiện fine-tune (SFT, DPO, GRPO) để đảm bảo cô lập biến số tìm kiếm. |
| **Lưu trữ dữ liệu (Storage)** | Dạng file JSON cục bộ | `[x]` | Lưu trữ ontology và corpus bằng file JSON cục bộ, xử lý truy vấn trực tiếp trên RAM. |

---

## 3. Nhật ký thay đổi chi tiết (Detailed Changelog)

Đây là phiên bản sơ khai đầu tiên của hệ thống Baseline. Các tính năng và module đã được xây dựng gồm có:

* **Đồ thị Ontology mẫu (`ontology.json`)**:
  Định nghĩa 11 thực thể (Concepts) phân nhóm theo các facets (Disease, Anatomy, ClinicalState, Intervention, Intent) và 5 quan hệ cốt lõi (isPartOf, contraindicatedFor, recommendedFor...).
* **Module Tìm kiếm lai (`database.py`)**:
  Tích hợp tìm kiếm lai Sparse (BM25Okapi) và Dense (Cosine Similarity qua mô hình `all-MiniLM-L6-v2`) với công thức kết hợp điểm tuyến tính (Linear Combination score blending).
* **Bộ trích xuất ngữ cảnh (`parser.py`)**:
  Cho phép trích xuất tự động ngữ cảnh lâm sàng bằng mô hình Gemini 1.5 Flash (hoặc chạy luật dự phòng dựa trên từ khóa y khoa nếu không có API Key).
* **Bộ xếp hạng lại y khoa (`reranker.py`)**:
  Xây dựng thuật toán Reranker dựa trên ontology đầu tiên. Cộng điểm thưởng cho các tài liệu khớp Anatomy/Disease/Intent/ClinicalState và áp dụng điểm phạt cực nặng (`penalty += 5.0`) đối với các tài liệu chứa hoạt động bị chống chỉ định đối với bệnh nhân.
* **Kịch bản kiểm thử đối chứng (`main.py`)**:
  Chạy thử nghiệm so sánh trực tiếp kết quả đầu ra giữa Level 0 (Vanilla) và Level 2 (Ontology-Guided RAG) trên 3 test cases lâm sàng nhạy context.

