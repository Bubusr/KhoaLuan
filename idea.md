Chủ đề Khoá luận: "Phát triển mô hình hỏi đáp tin cậy bệnh lý về xương dựa trên mô hình ngôn ngữ lớn và truy xuất tăng cường sinh nội dung dựa trên văn bản"

Ngôn ngữ: Tiếng Việt + chuẩn Academic (Mục đích: Khoá luận --> Mục tiêu cao hơn: Xuất bản bài báo khoa học)
Văn phong: Xoáy bao quanh luận điểm, các ý phụ chỉ nên làm rõ và mở rộng từ luận điểm và mang tính logic cao
Các nội dung bên trong được diễn giải lại từ các bài báo gốc - có citation.

---

# DÀN Ý CHI TIẾT CHƯƠNG 1: TỔNG QUAN NGHIÊN CỨU

*(Cấu trúc chuẩn hóa: Đã ẩn phần Khoảng trống nghiên cứu, cập nhật mục Các thách thức của bài toán)*

### 1.1. Bối cảnh nghiên cứu

**Thực trạng tiếp cận thông tin y khoa (Góc nhìn thực tiễn):**
Trong bối cảnh y học hiện đại, khối lượng kiến thức lâm sàng và phác đồ điều trị chuyên khoa cơ xương khớp (thoái hóa khớp, thoát vị đĩa đệm, loãng xương, chấn thương chỉnh hình) gia tăng nhanh chóng.
* **Đối với nhân viên y tế và sinh viên y khoa:** Việc tra cứu thông tin chính xác từ sách giáo khoa hay các cơ sở dữ liệu y sinh (như PubMed) đòi hỏi nhiều thời gian, ảnh hưởng tới tốc độ ra quyết định lâm sàng.
* **Đối với bệnh nhân:** Xu hướng tự tra cứu triệu chứng trên Internet phổ biến nhưng tiềm ẩn tình trạng "nhiễu loạn thông tin", thiếu kiểm chứng, dễ dẫn tới sai lầm nguy hiểm trong tự điều trị.

**Sự tiến hóa của các hệ thống Hỏi đáp Y khoa (Medical QA) & Điểm nghẽn công nghệ:**
* **Thế hệ 1 & 2:** Hệ thống chuyên gia dựa trên luật (Rule-based) `[Bài báo 1, 2]` và truy xuất dựa trên từ khóa (BM25). Hạn chế: Cứng nhắc, không hiểu được ngữ nghĩa câu hỏi tự nhiên của người bệnh.
* **Thế hệ 3:** Mô hình Ngôn ngữ Lớn (LLM) dựa trên kiến trúc Transformer `[Vaswani et al., 2017]` giải quyết bài toán giao tiếp tự nhiên nhưng vấp phải rào cản chí mạng: **Hiện tượng ảo giác (Hallucination)** và thiếu khả năng trích dẫn bằng chứng y khoa.
* **Thế hệ 4 (Nền tảng hiện đại):** Kiến trúc Truy xuất Tăng cường Sinh nội dung (RAG - Retrieval-Augmented Generation) `[Lewis et al., 2020; Karpukhin et al., 2020]` buộc LLM sinh câu trả lời dựa trên văn bản ngữ cảnh thực tế được truy xuất, mở ra hướng đi cho trợ lý y tế tin cậy.

### 1.2. Động lực nghiên cứu

**1.2.1. Ý nghĩa khoa học:**
* Nhu cầu thúc đẩy việc ứng dụng các mô hình RAG tiên tiến vào xử lý ngôn ngữ tự nhiên trong miền y tế chuyên sâu.
* Nhu cầu khảo sát và đánh giá khả năng vận hành, giới hạn thực tế của các đường ống RAG tiêu chuẩn trên ngữ liệu y khoa phức tạp trước khi phát triển các kiến trúc cải tiến tiếp theo.

**1.2.2. Ý nghĩa thực tiễn:**
* Nhu cầu cấp thiết hỗ trợ bác sĩ, nhân viên y tế tra cứu phác đồ điều trị bệnh lý về xương chuẩn xác, giảm tải thời gian tìm kiếm thông tin trong môi trường lâm sàng áp lực cao `[Bài báo 12]`.
* Nhu cầu cấp bách định hướng hành vi chăm sóc sức khỏe cộng đồng, bảo vệ người bệnh khỏi rủi ro tự điều trị sai lầm bằng một kênh tư vấn y khoa tin cậy có trích dẫn nguồn minh bạch `[Bài báo 13]`.

---
*(Khoảng trống nghiên cứu - Đã ẩn tạm thời theo yêu cầu)*
---

### 1.3. Phát biểu bài toán và Khung kiến trúc RAG căn bản (Standard RAG Framework)

**Phát biểu bài toán dưới góc độ toán học:**
Cho tập ngữ liệu tri thức y khoa xương khớp đã kiểm chứng $\mathcal{D} = \{d_1, d_2, \dots, d_n\}$. Khi nhận được truy vấn $q$ từ người dùng:
1. **Truy xuất ngữ cảnh (Retrieval):** Tìm tập ngữ cảnh $\mathcal{C} \subset \mathcal{D}$ gồm $k$ đoạn văn bản liên quan nhất tới $q$.
2. **Sinh nội dung (Generation):** LLM sinh ra câu trả lời $a$ dựa trên cặp $(q, \mathcal{C})$ sao cho cực đại hóa xác suất $P(a \mid q, \mathcal{C})$.
3. **Ràng buộc:** Cực đại hóa độ trung thực (Faithfulness) của $a$ so với $\mathcal{C}$, giảm thiểu tối đa hiện tượng ảo giác (Minimizing Hallucination).

**Khung kiến trúc RAG cổ điển (Standard Baseline RAG Pipeline):**
Hệ thống gồm hai giai đoạn chính:
* **Giai đoạn Offline (Lập chỉ mục tri thức):** Thu thập văn bản y khoa Xương khớp $\rightarrow$ Tiền xử lý & Cắt nhỏ (Cleaning & Chunking) $\rightarrow$ Nhúng vector (Embedding) $\rightarrow$ Lưu trữ & Lập chỉ mục trong Vector DB.
* **Giai đoạn Online (Suy luận thời gian thực):** Truy vấn $q \rightarrow$ Mã hóa $q$ $\rightarrow$ Truy xuất $k$ đoạn ngữ cảnh $\mathcal{C}$ $\rightarrow$ Ghép Prompt ngữ cảnh $\rightarrow$ LLM sinh câu trả lời $a$ kèm trích dẫn $\rightarrow$ Output.

### 1.4. Các thách thức của bài toán (Challenges of Medical RAG)

Quá trình xây dựng một hệ thống RAG chuyên biệt và tin cậy cho miền bệnh lý cơ xương khớp đối mặt với 4 nhóm thách thức cốt lõi:
1. **Giới hạn của bộ truy xuất trước rào cản thuật ngữ và nhiễu ngữ nghĩa `[MIRAGE, RAG-X]`:** Thuật ngữ y khoa phức tạp khiến BM25 bỏ sót tài liệu, trong khi Dense Retrieval dễ vấp phải hiện tượng nhiễu sau truy xuất (vớt tài liệu liên quan ngữ nghĩa nhưng thiếu thông tin lâm sàng cốt lõi).
2. **Đứt gãy ngữ cảnh và Năng lực suy luận y khoa đa bước `[i-MedRAG, RAG-X]`:** Truy vấn y khoa cần suy luận đa bước (bệnh lý $\rightarrow$ thuốc $\rightarrow$ tác dụng phụ trên bệnh nền). RAG đơn luồng làm đứt gãy mạch logic này, dẫn đến thiếu thông tin cốt lõi hoặc lạc lối trong tài liệu dài.
3. **Xung đột tri thức và 4 Dạng ảo giác y khoa `[MedTrust-RAG]`:** Mâu thuẫn giữa tri thức truy xuất và tri thức ẩn trong tham số LLM phát sinh 4 dạng ảo giác nguy hiểm: Suy luận lỗi (*Faulty Reasoning*), Bỏ sót thông tin (*Missing Answer*), Từ chối quá mức (*Over-Refusal*), Gán sai nguồn (*Misattribution*).
4. **Sự khắt khe trong tiêu chuẩn an toàn và đánh giá lâm sàng `[JMIR AI 2024]`:** Đòi hỏi khắt khe về Độ chính xác y khoa (*Medical Accuracy*), Độ an toàn (*Clinical Safety*), Khả năng đọc hiểu (*Readability*) và Sự đồng cảm (*Empathy*).

### 1.5. Đóng góp của nghiên cứu (Expected Contributions)

1. **Chuẩn hóa Khung hệ thống RAG cho Y khoa:** Đề xuất và cài đặt thành công quy trình RAG tiêu chuẩn làm mốc so sánh (Baseline) cho dữ liệu chuyên sâu về các bệnh lý về xương.
2. **Xây dựng Bộ dữ liệu & Bộ câu hỏi đánh giá chuyên ngành:** Thu thập bộ ngữ liệu y khoa chuẩn và thiết lập tập câu hỏi thực nghiệm y khoa.
3. **Thực nghiệm & Đánh giá hệ thống:** Thực hiện đánh giá thực nghiệm toàn diện trên kiến trúc RAG đề xuất nhằm đo lường khả năng giảm thiểu hiện tượng ảo giác, nâng cao độ trung thực và độ tin cậy của câu trả lời.

---

### PHẦN A: DANH SÁCH TÀI LIỆU THAM KHẢO

1. **[Bài báo 1]** L. L. E. & cộng sự. *"A rule-based clinical decision model to support interpretation of multiple data in health examinations."* International Journal of Medical Informatics.
2. **[Bài báo 2]** *"A Hybrid AI and Rule-Based Decision Support System for Disease Diagnosis and Management Using Labs."* IEEE / arXiv.
3. **[Vaswani et al., 2017]** Vaswani, A., et al. *"Attention is all you need."* Advances in Neural Information Processing Systems, 30.
4. **[Karpukhin et al., 2020]** Karpukhin, V., et al. *"Dense passage retrieval for open-domain question answering."* arXiv:2004.04906.
5. **[Lewis et al., 2020]** Lewis, P., et al. *"Retrieval-augmented generation for knowledge-intensive NLP tasks."* NeurIPS, 33, 9459-9474.
6. **[Gao et al., 2023]** Gao, Y., et al. *"Retrieval-augmented generation for large language models: A survey."* arXiv:2312.10997.
7. **[Microsoft, 2024]** Edge, D., et al. *"From local to global: A graph rag approach to query-focused summarization."* arXiv:2404.16130.
8. **[Xiong et al., 2024]** Xiong, G., Jin, Q., et al. *"Benchmarking Retrieval-Augmented Generation for Medicine."* ACL Findings / arXiv:2411.09213.
9. **[MedRAG, 2024]** Xiong, G., et al. *"MedRAG: Towards Reliable Medical Question Answering with Retrieval-Augmented Generation."* arXiv:2404.14746.
10. **[i-MedRAG]** *"Improving Retrieval-Augmented Generation in Medicine with Iterative Follow-up Questions."*
11. **[MedTrust-RAG]** *"MedTrust-RAG: Evidence Verification and Trust Alignment for Biomedical Question Answering."*
12. **[Bài báo 12]** *"Evaluating retrieval augmented generation and ChatGPT's accuracy on orthopaedic examination assessment questions."* Annals of Joint.
13. **[Bài báo 13]** *"Development and Evaluation of a Retrieval-augmented Generation Chatbot for Orthopedic and Trauma Surgery Patient Education."* JMIR AI.