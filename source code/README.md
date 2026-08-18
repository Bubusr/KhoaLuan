# Ontology-Guided Context-Sensitive RAG for Bone Disease QA

Dự án nghiên cứu thử nghiệm hệ thống RAG định hướng Ontology nhằm tối ưu hóa khả năng tìm kiếm nhạy ngữ cảnh lâm sàng (Context-sensitive Retrieval) cho các bệnh lý xương khớp.

<div style="padding: 16px; border: 2px solid #ef4444; border-radius: 8px; background-color: rgba(239, 68, 68, 0.05); margin-bottom: 20px;">
  <strong style="color: #ef4444; font-size: 1.1rem; display: block; margin-bottom: 8px;">THÔNG BÁO QUAN TRỌNG VỀ THỬ NGHIỆM PHIÊN BẢN (VERSION v0.1.0)</strong>
  <ul style="margin-left: 20px; line-height: 1.6; color: #f3f4f6;">
    <li><strong>Quy mô thực hiện (Scope)</strong>: Kiểm thử đối chứng trên 7 ca lâm sàng mẫu (Vignettes) trích xuất từ 9 đoạn ngữ liệu chuẩn y văn (WHO, AAOS, ACR) gán nhãn thực thể.</li>
    <li><strong>Các cấp độ RAG khả dụng</strong>: Hỗ trợ đầy đủ 3 mức độ so sánh đối chứng: <strong>Level 0 (Vanilla)</strong>, <strong>Level 1 (Concept Filter)</strong>, và <strong>Level 2 (Ontology Guided)</strong>.</li>
    <li><strong>Công cụ LLM sử dụng</strong>: Sử dụng model <code>gemini-3.6-flash</code> (cho Parser &amp; Generator). Có cơ chế dự phòng 2 tầng: <strong>g4f (OperaAria, miễn phí)</strong> → <em>Rule-based Mock</em> tự động khi Gemini API không khả dụng hoặc quá thời gian chờ (Timeout: 10s).</li>
    <li><strong>Bộ truy xuất & Lưu trữ Vector (Retriever & VDB)</strong>:
      <ul>
        <li>Nhúng vector cục bộ bằng model chuyên khoa y sinh <code>neuml/pubmedbert-base-embeddings</code> (768 chiều, chạy offline).</li>
        <li>Lưu trữ Vector VDB dưới dạng in-memory (Numpy array) nạp trực tiếp từ file ngữ liệu nguồn <a href="versions/v0.1.0/data/corpus/corpus.json">data/corpus/corpus.json</a>.</li>
        <li>Phương thức truy xuất (Retriever): Sử dụng công thức lai (Hybrid Search) kết hợp giữa điểm Cosine Similarity (Dense) và BM25 (Sparse).</li>
      </ul>
    </li>
    <li><strong>Lưu trữ & Truy vấn Ontology</strong>: Không sử dụng Graph DB phức tạp (như Neo4j), Ontology được thiết lập và truy vấn cục bộ dạng JSON tại file <a href="versions/v0.1.0/data/ontology/ontology.json">data/ontology/ontology.json</a>, tuân thủ đúng kiến trúc sơ đồ cấu trúc trong tài liệu thiết kế <a href="design_notes/dataset_design_and_report.md">dataset_design_and_report.md</a> và <a href="design_notes/bone_rag_ontology_design.md">bone_rag_ontology_design.md</a>.</li>
    <li><strong>Giám sát & Tracing (Observability)</strong>: Tích hợp hệ thống giám sát <strong>Langfuse</strong> hỗ trợ vẽ sơ đồ cây thực thi chi tiết (Parser &rarr; Retriever &rarr; Generator) và tự động liên kết mạch hội thoại (Session-linked Tracing) theo từng phiên chat thông qua cấu hình khóa tại file <code>.env</code>.</li>
    <li><strong>Kiến trúc mã nguồn</strong>: Đã được tái cấu trúc hoàn toàn dưới dạng <strong>Modular RAG</strong> (Parser, Retriever, Reranker, Generator nằm biệt lập trong thư mục <a href="versions/v0.1.0/src/">versions/v0.1.0/src/</a>).</li>
  </ul>
</div>

---

## 1. Định nghĩa các Cấp độ thử nghiệm (RAG Levels)

Để thực hiện đánh giá đối chứng hiệu quả của việc đưa Ontology vào kiến trúc tìm kiếm, hệ thống được thiết lập theo **3 Cấp độ (Levels)** từ cơ bản đến nâng cao:

### Mức 0 — Vanilla Hybrid RAG (Level 0)
* **Định nghĩa**: Hệ thống RAG thông thường tìm kiếm trực tiếp dựa trên sự tương đồng văn bản.
* **Cơ chế hoạt động**: 
  1. Câu hỏi tự nhiên của người dùng được tìm kiếm lai (Hybrid Search) kết hợp giữa độ tương đồng vector ngữ nghĩa (**Dense Cosine Similarity**) và tần suất từ khóa (**Sparse BM25**).
  2. Hệ thống lấy ra các đoạn văn bản (chunks) có điểm số kết hợp cao nhất.
  3. Gửi trực tiếp thông tin thô này tới LLM để sinh câu trả lời.
* **Đặc điểm**: Không phân tích ngữ cảnh bệnh nhân, không áp dụng luật y tế, dễ bỏ qua các chống chỉ định lâm sàng.

### Mức 1 — Concept-Filtered RAG (Level 1)
* **Định nghĩa**: Hệ thống RAG kết hợp lọc cứng thực thể y khoa (Entity Filtering).
* **Cơ chế hoạt động**:
  1. Sử dụng một mô hình Parser để trích xuất các khái niệm chính trong câu hỏi (ví dụ: Tên bệnh: `Osteoporosis`, Vùng giải phẫu: `Spine`).
  2. Lọc cứng (Hard Filter) hoặc ưu tiên cộng điểm trực tiếp cho những tài liệu tri thức chứa chính xác các khái niệm này trong cơ sở dữ liệu.
* **Đặc điểm**: Giảm thiểu việc lấy lệch chủ đề bệnh lý, nhưng chưa xử lý được các quan hệ logic phức tạp giữa các thực thể và trạng thái của bệnh nhân.

### Mức 2 — Ontology-Guided RAG (Level 2)
* **Định nghĩa**: Hệ thống RAG định hướng bởi đồ thị Ontology y khoa và luật ràng buộc lâm sàng.
* **Cơ chế hoạt động**:
  1. **Trích xuất ngữ cảnh (Parsing)**: Parser phân tích câu hỏi ra cấu trúc đầy đủ gồm: *Disease, Anatomy, Clinical State, Patient Context, Intent*.
  2. **Tìm kiếm lai ứng viên (Candidate Retrieval)**: Chạy tìm kiếm lai để lấy ra tập tài liệu tiềm năng.
  3. **Xếp hạng lại theo Ontology (Reranking)**: Reranker tính toán điểm thích ứng lâm sàng thông qua quan hệ trên đồ thị Ontology (`ontology.json`):
     * **Cộng điểm thưởng (Boost)**: Nếu tài liệu phù hợp với độ tuổi bệnh nhân, giai đoạn hồi phục và mục đích hỏi.
     * **Phạt điểm cực nặng (Penalty)**: Nếu tài liệu chứa các chỉ định bị chống chỉ định đối với trạng thái hiện tại của bệnh nhân (ví dụ: bệnh nhân đang bị gãy xương cấp tính mà tài liệu khuyên tập thể dục cường độ mạnh).
  4. **Sinh câu trả lời (Safe Generation)**: LLM sinh câu trả lời dựa trên tài liệu đã lọc an toàn.

---

## 2. Cấu trúc dự án & Vị trí Tài liệu (Directory Layout)

*   **Mã nguồn và Cơ sở dữ liệu v0.1.0**: Toàn bộ code chạy baseline được tổ chức modular và đóng gói bên trong [versions/v0.1.0/](versions/v0.1.0/).
*   **Tài liệu thiết kế nghiên cứu (Mục Design notes)**:
    *   [structure.md](design_notes/structure.md): Mô tả cấu trúc & kiến trúc hệ thống.
    *   [dataset_design_and_report.md](design_notes/dataset_design_and_report.md): Thiết kế & báo cáo tập dữ liệu (9 chunks).
    *   [bone_rag_ontology_design.md](design_notes/bone_rag_ontology_design.md): Sơ đồ thiết kế đồ thị tri thức Ontology.
    *   [evaluation_design.md](design_notes/evaluation_design.md): Các chỉ số và kịch bản thiết kế kiểm thử.
*   **Nhật ký và Báo cáo phiên bản (v0.1.0/note/)**:
    *   [changelog.md](versions/v0.1.0/note/changelog.md): Nhật ký thay đổi và nguồn gốc học thuật.
    *   [experiment_report.md](versions/v0.1.0/note/experiment_report.md): Báo cáo chỉ số định lượng baseline thực tế.


---

## 3. Hướng dẫn sử dụng & Chạy thử nghiệm

### Thiết lập môi trường ảo
Kích hoạt môi trường và cài đặt các gói phụ thuộc (thực hiện từ thư mục gốc của dự án):
```bash
# Kích hoạt venv
source venv/bin/activate

# Cài đặt thư viện phụ thuộc
pip install -r versions/v0.1.0/requirements.txt
```

### Thiết lập cấu hình biến môi trường
Mở file [versions/v0.1.0/.env](versions/v0.1.0/.env) và điền các API Key của bạn (như `GEMINI_API_KEY`, các khóa giám sát `LANGFUSE_PUBLIC_KEY` & `LANGFUSE_SECRET_KEY`).

### Chạy thử nghiệm đối chứng (Terminal CLI)
Di chuyển vào thư mục phiên bản và chạy script chính để mô phỏng tìm kiếm, đánh giá và sinh câu trả lời đối chứng trên 7 ca lâm sàng mẫu:
```bash
cd versions/v0.1.0
../../venv/bin/python3 main.py
```
*Kết quả đánh giá định lượng sẽ tự động lưu và cập nhật tại file [versions/v0.1.0/evaluation_metrics.md](versions/v0.1.0/evaluation_metrics.md).*

### Khởi chạy giao diện Chat Sandbox (Web UI)
Khởi chạy server Flask phục vụ giao diện chat trực quan tích hợp giám sát Langfuse (chạy từ thư mục phiên bản):
```bash
cd versions/v0.1.0
../../venv/bin/python3 app.py
```
*Sau khi chạy, hãy truy cập đường dẫn [http://127.0.0.1:5000/](http://127.0.0.1:5000/) trên trình duyệt để thử nghiệm chat đa phiên, kế thừa ngữ cảnh, và quan sát sơ đồ trace tự động.*

