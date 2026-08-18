# Kiến trúc & Cấu trúc Hệ thống - Version 0.1.0 (structure.md)

Tài liệu này ghi lại chi tiết cấu trúc thư mục, kiến trúc tổng thể, mô hình nhúng (embeddings), kho lưu trữ và mô hình LLM được sử dụng trong phiên bản đầu tiên (**v0.1.0**) của hệ thống Ontology-Guided Context-Sensitive RAG.

---

## 1. Cấu trúc thư mục dự án (Directory Structure - v0.1.0 Relocated)

```text
/Users/apple/KhoaLuan_TH/
├── venv/                            # Môi trường ảo Python
├── README.md                        # Hướng dẫn điều hướng chính (Root)
├── design_notes/                    # Thư mục chứa tài liệu thiết kế nghiên cứu
│   ├── structure.md                 # File cấu trúc & kiến trúc này
│   ├── dataset_design_and_report.md # Thiết kế & báo cáo tập dữ liệu
│   ├── bone_rag_ontology_design.md  # Thiết kế chi tiết đồ thị Ontology
│   └── evaluation_design.md         # Tài liệu thiết kế chỉ số đánh giá
└── versions/
    └── v0.1.0/                      # Thư mục phiên bản gốc v0.1.0
        ├── data/                    # Dữ liệu phục vụ RAG
        │   ├── ontology/
        │   │   └── ontology.json    # Đồ thị tri thức Ontology y khoa
        │   └── corpus/
        │       └── corpus.json      # Ngữ liệu nguồn gán nhãn thực thể
        ├── src/                     # Mã nguồn Modular RAG
        │   ├── __init__.py
        │   ├── models.py            # Khai báo cấu trúc dữ liệu Pydantic
        │   ├── pipeline.py          # Bộ điều phối Pipeline RAG
        │   ├── evaluator.py         # Module đánh giá hiệu năng tự động
        │   ├── retrieval/
        │   │   └── hybrid.py        # Tìm kiếm lai Dense + Sparse (BM25)
        │   ├── parser/
        │   │   └── clinical_parser.py # Phân tích cú pháp & Kế thừa ngữ cảnh
        │   ├── reranking/
        │   │   └── ontology_reranker.py # Xếp hạng lại theo Ontology
        │   └── generation/
        │       └── clinical_generator.py # Sinh câu trả lời lâm sàng
        ├── tests/
        │   └── test_cases.json      # 7 ca lâm sàng kiểm thử đối chứng
        ├── note/                    # Tài liệu học thuật của v0.1.0
        │   ├── changelog.md         # Nhật ký thay đổi & nguồn dữ liệu
        │   ├── experiment_report.md # Báo cáo kết quả định lượng tổng hợp
        │   └── future_research_directions.md # Định hướng nghiên cứu mở rộng
        ├── app.py                   # Flask Web Sandbox (Session-linked)
        ├── main.py                  # Script kích hoạt bộ đánh giá
        ├── requirements.txt         # Quản lý thư viện phụ thuộc
        ├── .env                     # Cấu hình API key thực tế

        └── .env.example             # Biến môi trường mẫu
```

---

## 2. Kiến trúc hệ thống tổng thể (Overall Architecture)

Kiến trúc phiên bản v0.1.0 được mô tả theo sơ đồ dòng chảy dữ liệu dưới đây:

```text
                           [ Câu hỏi bệnh nhân ]
                                     │
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
        [ Hybrid Retrieval ]                  [ Intent & Context Parser ]
      (BM25 + Cosine Similarity)              (Trích xuất ngữ cảnh y tế)
                  │                                     │
                  ▼                                     ▼
       [ Candidate Chunks (Top-N) ]            [ Structured Query (JSON) ]
                  │                                     │
                  └──────────────────┬──────────────────┘
                                     ▼
                        [ Ontology-Guided Reranker ]
                     (Tính toán điểm phù hợp & phạt phạt
                       nặng các vi phạm chống chỉ định)
                                     │
                                     ▼
                         [ Top-1 Selected Chunk ]
                                     │
                                     ▼
                            [ LLM Generator ]
                                     │
                                     ▼
                            [ Câu trả lời cuối ]
```

---

## 3. Các thành phần kỹ thuật chi tiết

### 3.1. Mô hình nhúng chuyên khoa (Embeddings Model)
* **Tên mô hình**: `neuml/pubmedbert-base-embeddings`
* **Loại**: Cục bộ (Local) - tải từ Hugging Face Hub và chạy trực tiếp local qua thư viện `sentence-transformers`.
* **Đặc tính**: Được fine-tune trực tiếp trên tập dữ liệu PubMed khổng lồ gồm các tiêu đề và tóm tắt bài báo y sinh chuyên khoa.
* **Kích thước vector**: 768 chiều.
* **Mục đích**: Nhúng các đoạn văn bản (chunks) và câu hỏi bệnh nhân sang dạng vector không gian ngữ nghĩa y khoa chuyên sâu.

### 3.2. Kho lưu trữ dữ liệu (Storage Location)
* **Phương án lưu trữ**: **Local JSON files** kết hợp cấu trúc mảng **Numpy** trong RAM để chạy tìm kiếm trực tiếp.
* **Chi tiết**:
  * Đồ thị Ontology và các đoạn dữ liệu tri thức (Corpus) được lưu trữ dưới định dạng `.json` tại `data/ontology/` và `data/corpus/`.
  * Khi khởi động ứng dụng, `src/database.py` sẽ nạp file JSON này vào RAM, chuyển đổi các chunk văn bản thành vector embeddings, lưu trữ dưới dạng `numpy.ndarray` để tính toán độ tương đồng cosine nhanh mà không cần dựng daemon DB nặng.

### 3.3. Mô hình sinh ngôn ngữ (LLM used)
* **Tên mô hình**: `gemini-1.5-flash` (qua SDK `google-generativeai`).
* **Cơ chế dự phòng (Fallback)**: Nếu không cấu hình `GEMINI_API_KEY`, hệ thống tự động kích hoạt **Rule-based Mock Parser & Generator** dựa trên dữ liệu so khớp mẫu để bảo đảm chương trình luôn chạy thông suốt local không lỗi kết nối.
* **Mục đích**: 
  * Trích xuất các thực thể và trạng thái của bệnh nhân từ câu hỏi thô.
  * Tổng hợp tài liệu y văn để sinh ra câu trả lời cuối cùng bằng tiếng Anh chuyên ngành.
