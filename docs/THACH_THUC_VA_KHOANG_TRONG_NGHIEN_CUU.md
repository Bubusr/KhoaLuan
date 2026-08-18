# TỔNG HỢP THÁCH THỨC VÀ KHOẢNG TRỐNG NGHIÊN CỨU
## Hệ thống Hỏi–Đáp Y khoa Tin cậy dựa trên RAG chuyên biệt cho các Bệnh lý về Xương

---

## PHẦN 1: CÁC THÁCH THỨC CỐT LÕI CỦA BÀI TOÁN

Quá trình xây dựng một hệ thống RAG chuyên biệt và tin cậy cho tập dữ liệu về các bệnh lý về xương phải đối mặt với **04 nhóm thách thức cốt lõi**, được phân rã theo 4 giai đoạn trong luồng vận hành hệ thống:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             CÁC THÁCH THỨC THEO GIAI ĐOẠN                               │
└──────────────────────────────────────────────────────────────────────────────────────────┘
           │                                                                  │
           ▼                                                                  ▼
┌───────────────────────────────────────┐          ┌───────────────────────────────────────┐
│ (1) Giai đoạn Xây dựng Dữ liệu        │          │ (2) Giai đoạn Truy xuất Tri thức      │
│ Tính phi cấu trúc & Mâu thuẫn dữ liệu │          │ Rào cản Thuật ngữ & Nhiễu ngữ nghĩa   │
└───────────────────────────────────────┘          └───────────────────────────────────────┘
           │                                                                  │
           ▼                                                                  ▼
┌───────────────────────────────────────┐          ┌───────────────────────────────────────┐
│ (3) Giai đoạn Suy diễn & Sinh văn bản │          │ (4) Giai đoạn Đánh giá Lâm sàng       │
│ Đứt gãy Ngữ cảnh & Ảo giác Đa bước    │          │ An toàn Lâm sàng & Chỉ số Đo lường    │
└───────────────────────────────────────┘          └───────────────────────────────────────┘
```

---

### (1) Giai đoạn Xây dựng và Tiền xử lý Dữ liệu: Thách thức từ tính phi cấu trúc, đa dạng và mâu thuẫn của dữ liệu y khoa thực tế

- **Sự đa dạng về định dạng và tính phi cấu trúc của dữ liệu:** 
  Tri thức y học về các bệnh lý về xương nằm rải rác trong các phác đồ điều trị, giáo trình chuyên khoa và báo cáo thực nghiệm dưới dạng tệp PDF. Dữ liệu này chứa mật độ cao các bảng biểu phức tạp, sơ đồ phân loại chấn thương gãy xương hoặc cây quyết định chẩn đoán lâm sàng, gây rào cản lớn cho các bộ trích xuất văn bản tự động.
- **Sự phức tạp và bất đồng về thuật ngữ y khoa và tên thuốc:** 
  Tồn tại sự bất đồng lớn giữa tên gốc hóa học, tên thương mại của thuốc điều trị xương khớp, từ viết tắt lâm sàng và ngôn ngữ diễn đạt đời thường của người bệnh (ví dụ: *"giòn xương"*, *"lục khục khớp"* vs. *"loãng xương"*, *"thoái hóa khớp"*).
- **Xung đột tri thức theo thời gian và cấp độ áp dụng:** 
  Dữ liệu y khoa thường có sự mâu thuẫn giữa phác đồ cũ đã hết hiệu lực và phác đồ mới vừa cập nhật. Đồng thời, tồn tại sự mâu thuẫn hoặc khác biệt giữa Hướng dẫn lâm sàng quốc tế và Quy trình điều trị thực tế tại từng bệnh viện ở Việt Nam.

---

### (2) Giai đoạn Truy xuất Tri thức: Giới hạn của các bộ truy xuất trước rào cản thuật ngữ và nhiễu ngữ nghĩa

- **Bất đồng ngôn ngữ giữa truy vấn người dùng và tài liệu tri thức:** 
  Sự lệch pha lớn giữa câu hỏi tiếng Việt/từ ngữ đời thường của người bệnh và các nguồn tài liệu tham khảo chuẩn quốc tế bằng tiếng Anh (hoặc tài liệu chứa từ viết tắt chuyên khoa).
- **Hạn chế của các thuật toán truy xuất theo từ khóa truyền thống:** 
  Các thuật toán truy xuất theo từ khóa truyền thống thường gặp hiện tượng bỏ sót tài liệu liên quan do không thể nhận diện sự tương đồng ngữ nghĩa khi truy vấn của người dùng khác biệt với thuật ngữ chính thống trong văn bản y học *(MedRAG)*.
- **Hiện tượng Nhiễu sau truy xuất (Post-Retrieval Noise):** 
  Phương pháp truy xuất biểu diễn ngữ nghĩa (vector embedding) tuy cải thiện khả năng tra cứu theo ngữ cảnh nhưng lại dễ vấp phải rào cản nhiễu sau truy xuất *(MIRAGE, MedRGB)*: trích xuất các đoạn văn bản có độ tương đồng biểu diễn bề mặt cao (như cùng đề cập đến một nhóm thuốc) nhưng lại thiếu hụt những thông tin lâm sàng mang tính quyết định (như chống chỉ định hoặc liều lượng áp dụng cho bệnh nhân có bệnh nền), dẫn đến sự sai lệch ngữ cảnh đầu vào *(MedTrust-RAG)*.

---

### (3) Giai đoạn Suy diễn và Sinh câu trả lời: Đứt gãy ngữ cảnh và các rủi ro ảo giác trong suy luận y khoa đa bước

- **Đứt gãy mạch logic trong suy luận y khoa đa bước (Multi-hop Reasoning):** 
  Một truy vấn y khoa lâm sàng thường đòi hỏi phải tổng hợp cùng lúc nhiều đoạn tài liệu từ nhiều nguồn khác nhau (xác định phác đồ điều trị chuẩn $\to$ sàng lọc danh sách chỉ định thuốc $\to$ đối chiếu tác dụng phụ đối với bệnh lý đi kèm) *(IMedRAG)*. Việc chia nhỏ tài liệu thành các đoạn độc lập (chunking) làm thất lạc thông tin liên kết chéo, khiến mô hình ngôn ngữ lớn tiếp nhận ngữ cảnh thiếu hụt hoặc bị nhiễu loạn giữa tập tài liệu trích xuất có độ dài lớn.
- **Biến động ngữ cảnh do tích lũy lịch sử hội thoại (Chat History Drift):** 
  Trong các cuộc trao đổi nhiều lượt, việc đưa trực tiếp toàn bộ lịch sử hội thoại vào câu lệnh tăng cường gây ra hiện tượng trôi ngữ cảnh, làm tăng mạnh tỷ lệ ảo giác khi hội thoại kéo dài do lịch sử trao đổi làm sai lệch trọng tâm truy vấn gốc.
- **Xung đột tri thức và 04 dạng Ảo giác Y khoa nguy hiểm:** 
  Khi ngữ cảnh trích xuất chứa thông tin mâu thuẫn, thiếu bằng chứng hoặc trái với tri thức ghi nhớ sẵn trong mô hình, 4 dạng ảo giác nguy hiểm sẽ xuất hiện *(MedTrust-RAG, MIRAGE)*:
  - *Suy luận lỗi ($\mathcal{H}_F$):* Mô hình kết nối sai logic giữa triệu chứng lâm sàng và phương pháp điều trị.
  - *Bỏ sót thông tin ($\mathcal{H}_M$):* Mô hình tóm tắt quá mức, làm mất các cảnh báo lâm sàng quan trọng hoặc các chống chỉ định y khoa nghiêm trọng.
  - *Từ chối quá mức ($\mathcal{H}_O$):* Mô hình từ chối trả lời mặc dù dữ liệu ngữ cảnh đã cung cấp đầy đủ thông tin bằng chứng.
  - *Gán sai nguồn trích dẫn ($\mathcal{H}_A$):* Mô hình đưa ra câu trả lời nhưng đính kèm trích dẫn tới đoạn văn bản không chứa thông tin chứng minh.

---

### (4) Giai đoạn Đánh giá và Kiểm định Lâm sàng: Sự khắt khe trong tiêu chuẩn an toàn lâm sàng và giới hạn của các bộ chỉ số tự động

- **Biên độ sai sót trong y tế tiệm cận bằng không:** 
  Biên độ chấp nhận sai sót trong y tế gần như bằng không *(WHO, MedTrust-RAG)*. Nếu bộ truy xuất lấy nhầm tài liệu cũ hoặc chứa nội dung mâu thuẫn, mô hình ngôn ngữ lớn sẽ sinh ra phản hồi sai nhưng lại có vẻ vô cùng thuyết phục vì được bảo chứng bởi "bằng chứng".
- **Rào cản nhận biết ranh giới từ chối (Abstain):** 
  Hệ thống cần có khả năng tự nhận biết ranh giới bằng chứng để chủ động "từ chối" trả lời khi thiếu thông tin, thay vì cố gắng đưa ra phỏng đoán nguy hiểm cho tính mạng người bệnh.
- **Khả năng đọc hiểu, sự đồng cảm và giới hạn của các bộ chỉ số tự động:** 
  Phản hồi y khoa cần tính đồng cảm và khả năng đọc hiểu cao đối với người bệnh *(JMIR AI)*, đây là điều mà các bộ chỉ số đo lường tự động truyền thống (như BLEU, ROUGE hoặc độ tương đồng văn bản) hoàn toàn không thể đánh giá được.

---

## PHẦN 2: CÁC KHOẢNG TRỐNG NGHIÊN CỨU

Từ việc phân tích thực trạng và 04 nhóm thách thức nêu trên, đề tài xác định **04 khoảng trống nghiên cứu cốt lõi**:

### Khoảng trống 1: Khảo sát ranh giới vận hành và điểm nghẽn ảo giác của quy trình RAG Mô hình cơ sở (Standard RAG Baseline) trên ngữ liệu y khoa chuyên sâu
- **Thực trạng:** Các nghiên cứu hiện nay thường vội vã đề xuất các mô hình RAG nâng cao phức tạp mà chưa có các nghiên cứu thực nghiệm đánh giá định lượng bài bản ranh giới năng lực và điểm nghẽn cốt lõi của quy trình RAG Mô hình cơ sở khi đối mặt với dữ liệu nhiễu và thông tin mâu thuẫn.
- **Khoảng trống:** Chưa có công trình khảo sát chi tiết ranh giới vận hành, mức độ chịu tải và điểm nghẽn phát sinh ảo giác của RAG Mô hình cơ sở khi triển khai trên tập ngữ liệu phác đồ điều trị các bệnh lý về xương (loãng xương, thoái hóa khớp, gãy xương, viêm xương) tại Việt Nam.

### Khoảng trống 2: Thiếu cơ chế kiểm soát an toàn chủ động (Trả lời – Từ chối – Chuyển chuyên gia) cho hệ thống RAG Y tế
- **Thực trạng:** Các hệ thống RAG truyền thống vận hành theo cơ chế cố gắng trả lời mọi câu hỏi, dẫn đến rủi ro bịa đặt thông tin khi thiếu bằng chứng hoặc phỏng đoán nguy hiểm đối với các ca bệnh nguy cơ cao.
- **Khoảng trống:** Thiếu một lớp kiểm soát an toàn chủ động giúp hệ thống đưa ra một trong ba quyết định:
  - *Trả lời (Answer):* Cung cấp câu trả lời khi có đủ bằng chứng và đạt yêu cầu an toàn lâm sàng.
  - *Từ chối (Abstain):* Tự động từ chối trả lời khi thiếu dữ liệu, độ tin cậy thấp hoặc không tìm thấy tài liệu phù hợp.
  - *Chuyển chuyên gia (Escalate):* Chủ động nhận biết và chuyển câu hỏi cho bác sĩ đối với các tình huống chấn thương gãy xương nguy cơ cao, khẩn cấp hoặc vượt khả năng xử lý.

### Khoảng trống 3: Khắc phục đứt gãy ngữ cảnh bằng đường ống Truy xuất lai kết hợp Chuẩn hóa thuật ngữ song ngữ
- **Thực trạng:** Tài liệu chuyên khoa về bệnh lý về xương chứa mật độ thông tin cao, cấu trúc không đồng nhất và sự mâu thuẫn thuật ngữ. Kỹ thuật truy xuất biểu diễn ngữ nghĩa đơn thuần dễ làm đứt gãy ngữ cảnh gốc và thất bại khi người dùng đặt câu hỏi bằng tiếng Việt hoặc từ ngữ đời thường nhưng tài liệu lại ở dạng tiếng Anh/chuẩn hóa y khoa.
- **Khoảng trống:** Chưa tối ưu hóa đường ống truy xuất kết hợp (truy xuất biểu diễn ngữ nghĩa + truy xuất theo từ khóa) tích hợp bước chuẩn hóa thuật ngữ y khoa song ngữ (Việt–Anh, Đời thường–Chuyên môn) dành riêng cho tập tài liệu phác đồ bệnh lý về xương.

### Khoảng trống 4: Xây dựng Khung đánh giá nhiều tầng độc lập chuyên biệt cho RAG Y khoa
- **Thực trạng:** Khác với các hệ thống hỏi đáp thông thường, ứng dụng y khoa đòi hỏi từng luận điểm phải được chứng thực trực tiếp từ văn bản tham chiếu. Việc chỉ đánh giá câu trả lời tổng thể khiến nghiên cứu không thể xác định nguyên nhân sai sót xuất phát từ bộ truy xuất hay bộ sinh.
- **Khoảng trống:** Thiếu một khung đánh giá phân rã nhiều tầng độc lập:
  1. *Tầng Truy xuất (Retrieval Tier):* Đo lường Độ chính xác ngữ cảnh, Độ phủ ngữ cảnh, $\text{Recall}@k$, $\text{MRR}$.
  2. *Tầng Sinh văn bản (Generation Tier):* Đo lường Độ trung thực tri thức, Độ tương quan câu trả lời, Độ chính xác trích dẫn.
  3. *Tầng An toàn Lâm sàng (Clinical Safety Tier):* Đo lường Tỷ lệ ảo giác, Tính đầy đủ lâm sàng, Tỷ lệ từ chối đúng và Tỷ lệ chuyển chuyên gia kịp thời.

---

## PHẦN 3: TỔNG KẾT ĐÓNG GÓP HƯỚNG TỚI CỦA ĐỀ TÀI

$$
\boxed{\text{Gắn kết Tri thức Y khoa} + \text{Khảo sát RAG Mô hình cơ sở} + \text{Truy xuất lai Song ngữ} + \text{Đánh giá An toàn Nhiều tầng}}
$$

- **Ý nghĩa Khoa học:** Thiết lập mốc thực nghiệm Mô hình cơ sở chuẩn mực, khảo sát ranh giới vận hành và phân tích định lượng 4 dạng ảo giác ($\mathcal{H}_F, \mathcal{H}_M, \mathcal{H}_O, \mathcal{H}_A$) của quy trình RAG Tiêu chuẩn trên ngữ liệu chuyên khoa Bệnh lý về Xương tại Việt Nam.
- **Ý nghĩa Thực tiễn:** Hỗ trợ bác sĩ và nhân viên y tế tra cứu phác đồ điều trị nhanh chóng; bảo vệ người bệnh và cộng đồng trước thực trạng nhiễu loạn thông tin y tế trên mạng Internet nhờ cơ chế trích dẫn minh bạch và phản hồi an toàn.
