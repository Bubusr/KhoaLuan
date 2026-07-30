# Second

## THỰC TRẠNG

Trong những năm gần đây, mô hình ngôn ngữ lớn đã đạt kết quả cao trên các bộ dữ liệu hỏi–đáp y khoa. Chẳng hạn, Med-PaLM 2 đạt độ chính xác tối đa **86,5% trên MedQA**, đồng thời được các bác sĩ chuyên khoa đánh giá cao trong một số thử nghiệm hỏi–đáp thực tế. Tuy nhiên, chính nghiên cứu này cũng cho thấy mô hình vẫn gặp khó khăn với câu trả lời dài, tình huống lâm sàng phức tạp và các quy trình thực tế; kết quả cao trên câu hỏi dạng thi trắc nghiệm chưa đồng nghĩa với khả năng sử dụng an toàn trong chăm sóc bệnh nhân.

### 1. Hạn chế của LLM y khoa truyền thống

LLM thông thường sinh câu trả lời chủ yếu dựa trên kiến thức đã được mã hóa trong tham số mô hình. Cách tiếp cận này tồn tại ba hạn chế chính:

- Kiến thức có thể không còn cập nhật khi hướng dẫn lâm sàng thay đổi.
- Mô hình không biết rõ nguồn nào hỗ trợ cho câu trả lời.
- Mô hình có thể sinh thông tin nghe hợp lý nhưng sai, còn gọi là hallucination.

WHO cảnh báo rằng các mô hình sinh trong y tế có thể tạo ra nội dung sai, không chính xác, thiên lệch hoặc không đầy đủ. Những lỗi này có thể gây hại nếu người bệnh hoặc nhân viên y tế sử dụng kết quả để đưa ra quyết định. WHO cũng đề cập đến các rủi ro về quyền riêng tư, an ninh mạng và **automation bias**, tức người dùng quá tin vào hệ thống và bỏ qua những lỗi đáng lẽ có thể phát hiện.

Vì vậy, một Medical QA LLM không nên chỉ tạo câu trả lời dựa trên kiến thức ghi nhớ sẵn, đặc biệt đối với các câu hỏi về thuốc, chống chỉ định, chẩn đoán hoặc xử trí tình huống nguy cơ cao.

### 2. RAG đang trở thành hướng tiếp cận phổ biến

Retrieval-Augmented Generation được sử dụng để khắc phục một phần các hạn chế trên. Thay vì yêu cầu LLM tự nhớ toàn bộ kiến thức, hệ thống trước tiên truy xuất các đoạn liên quan từ kho tri thức y khoa, sau đó đưa các đoạn này vào prompt để làm căn cứ sinh câu trả lời.

Benchmark MIRAGE đánh giá 41 tổ hợp giữa kho tài liệu, retriever và LLM trên **7.663 câu hỏi từ năm bộ dữ liệu y khoa**. Kết quả cho thấy MedRAG có thể cải thiện độ chính xác của các LLM được đánh giá lên đến **18 điểm phần trăm** so với chỉ sử dụng chain-of-thought. Nghiên cứu cũng cho thấy việc kết hợp nhiều nguồn tài liệu và nhiều phương pháp truy xuất thường hiệu quả hơn chỉ dùng một nguồn hoặc một retriever.

Một nghiên cứu năm 2025 áp dụng RAG cho đánh giá tiền phẫu đã thử nghiệm 10 LLM trên 14 tình huống lâm sàng. Cấu hình GPT-4 kết hợp hướng dẫn quốc tế đạt độ chính xác **96,4%**, cao hơn mức **86,6%** của câu trả lời do con người tạo ra trong phạm vi thử nghiệm đó. Hệ thống cũng cho kết quả nhất quán hơn và không ghi nhận hallucination trong tập đánh giá cụ thể này. Tuy nhiên, nghiên cứu chỉ tập trung vào một miền hẹp với các tình huống được thiết kế tương đối rõ ràng, do đó chưa thể suy rộng thành khả năng thay thế bác sĩ trong thực tế.

### 3. RAG không loại bỏ hoàn toàn hallucination

RAG chỉ tạo ra câu trả lời tốt khi tài liệu được truy xuất chính xác và phù hợp. Nếu retriever lấy nhầm tài liệu, đưa vào thông tin cũ, thiếu bằng chứng hoặc chứa nội dung sai, LLM vẫn có thể tạo ra câu trả lời không chính xác. Khi đó, RAG thậm chí có thể làm câu trả lời sai trở nên thuyết phục hơn vì nó có vẻ được hỗ trợ bởi “bằng chứng”.

Benchmark MedRGB cho thấy các mô hình RAG hiện tại còn hạn chế khi xử lý:

- Tài liệu truy xuất chứa nhiễu.
- Thông tin sai hoặc mâu thuẫn.
- Bằng chứng không đủ để trả lời.
- Nhiều đoạn tài liệu cần được tổng hợp cùng lúc.
- Trường hợp mô hình cần nhận biết rằng không nên trả lời.

Nghiên cứu này nhận định rằng các mô hình thương mại và mã nguồn mở hiện tại vẫn xử lý chưa tốt nhiễu và thông tin sai trong retrieved context.

Ngoài ra, độ tin cậy còn giảm trong hội thoại nhiều lượt. Một nghiên cứu năm 2026 thực hiện cùng một truy vấn 100 lần cho thấy tỷ lệ hallucination của hệ thống RAG tăng từ **5% khi không có lịch sử hội thoại lên 40% khi có 10 lượt trao đổi trước đó**. Nguyên nhân được chỉ ra là lịch sử hội thoại tích lũy có thể gây lệch ngữ cảnh và làm mô hình ưu tiên sai thông tin.

Kết quả này đặc biệt liên quan đến pipeline của bài toán, vì hệ thống sử dụng cả **patient context** và **chat history**. Do đó, lịch sử hội thoại không nên được đưa toàn bộ vào prompt một cách trực tiếp mà cần được tóm tắt, lọc và viết lại thành truy vấn độc lập.

### 4. Khó khăn về dữ liệu và đánh giá

Một hệ thống Medical QA RAG phụ thuộc mạnh vào chất lượng của kho tri thức. Trong thực tế, tài liệu y khoa có thể:

- Đến từ nhiều nguồn và có cấu trúc không đồng nhất.
- Có bảng, sơ đồ hoặc nội dung khó trích xuất từ PDF.
- Dùng thuật ngữ và tên thuốc khác nhau.
- Có nhiều phiên bản hoặc đã hết hiệu lực.
- Khác nhau giữa hướng dẫn quốc tế và quy trình tại từng bệnh viện.
- Chứa thông tin mâu thuẫn giữa các tổ chức hoặc thời điểm ban hành.

Do đó, việc chỉ chia tài liệu thành chunk và đưa vào Vector Database là chưa đủ. Mỗi chunk cần có metadata về nguồn, chuyên khoa, ngày ban hành, phiên bản, phạm vi áp dụng và trạng thái hiệu lực. Nghiên cứu về RAG tiền phẫu cũng nhấn mạnh rằng hệ thống có thể thích ứng với hướng dẫn địa phương, nhưng cần cải thiện tính đầy đủ của tài liệu, xử lý sơ đồ và duy trì cơ chế con người kiểm tra trước khi sử dụng trong quy trình lâm sàng.

Bên cạnh đó, các độ đo thông thường như BLEU, ROUGE hoặc độ tương đồng văn bản không đủ để đánh giá một câu trả lời y khoa. Một hệ thống có thể diễn đạt khác đáp án chuẩn nhưng vẫn đúng về mặt lâm sàng; ngược lại, một câu trả lời có độ tương đồng cao vẫn có thể chứa một chi tiết nguy hiểm. Vì vậy, cần đánh giá riêng:

- Chất lượng truy xuất.
- Độ chính xác y khoa.
- Groundedness và faithfulness.
- Tính đầy đủ.
- Độ chính xác của trích dẫn.
- Khả năng abstain khi thiếu bằng chứng.
- Khả năng escalate trong tình huống nguy cơ cao.
- Độ ổn định qua nhiều lần chạy và nhiều lượt hội thoại.

### 5. Khoảng trống mà bài toán cần giải quyết

Từ thực trạng trên, vấn đề hiện nay không còn chỉ là tạo một chatbot có thể trả lời câu hỏi y khoa. Nhu cầu thực tế là xây dựng một hệ thống có khả năng:

1. Truy xuất đúng tài liệu y khoa phù hợp với câu hỏi và bối cảnh bệnh nhân.
2. Sinh câu trả lời dựa trên bằng chứng thay vì chỉ dựa vào kiến thức nội tại của LLM.
3. Cung cấp nguồn trích dẫn có thể kiểm tra.
4. Nhận biết khi bằng chứng không đủ hoặc mâu thuẫn.
5. Từ chối trả lời thay vì phỏng đoán.
6. Chuyển câu hỏi cho bác sĩ đối với các tình huống nguy cơ cao.
7. Duy trì độ ổn định khi cuộc hội thoại kéo dài.
8. Bảo vệ dữ liệu cá nhân và hạn chế việc lộ thông tin bệnh nhân.

Vì vậy, pipeline gồm **hybrid retrieval, Medical QA LLM, quality assurance và bộ quyết định Answer–Abstain–Escalate** là phù hợp với khoảng trống hiện tại. Trong bối cảnh y tế, hệ thống nên được xác định là công cụ hỗ trợ truy xuất và tổng hợp thông tin, không phải một hệ thống tự chủ thay thế bác sĩ. WHO và các nghiên cứu triển khai lâm sàng đều nhấn mạnh sự cần thiết của giám sát, đánh giá rủi ro và cơ chế human-in-the-loop.

## BÀI TOÁN

## 1. Input của bài toán

### Input dùng để huấn luyện

- **Kho tri thức y khoa** $K$:
    - Tài liệu y khoa
    - Hướng dẫn lâm sàng
    - Phác đồ điều trị
    - Câu hỏi–đáp đã được chuyên gia xác nhận
- **Bộ dữ liệu QA**:

$$
D={(q_i,p_i,h_i,y_i^*)}_{i=1}^{N}
$$

Trong đó:

- ($q_i$): câu hỏi y khoa
- ($p_i$): thông tin hoặc bối cảnh bệnh nhân
- ($h_i$): lịch sử hội thoại
- ($y_i^*$): câu trả lời chuẩn do chuyên gia hoặc dữ liệu chuẩn cung cấp

Sau khi truy xuất, một mẫu dùng để fine-tune có dạng:

$$
(q_i,p_i,h_i,C_i,y_i^*)
$$

với ($C_i$) là tập các đoạn tài liệu liên quan lấy từ Vector Database.

### Input khi inference

Khi người dùng sử dụng hệ thống, đầu vào là:

$X=(q,p,h,K)$

Trong đó:

- ($q$): câu hỏi hiện tại
- ($p$): thông tin bệnh nhân được phép sử dụng
- ($h$): lịch sử hội thoại
- ($K$): kho tri thức y khoa đã được lập chỉ mục trong Vector Database

---

## 2. Output của bài toán

Hệ thống không chỉ xuất một câu trả lời, mà đưa ra một trong ba quyết định:

$O=(\hat y,d)$

Trong đó:

- ($\hat y$): câu trả lời được LLM sinh ra
- ($d$): quyết định cuối cùng

$$
d\in{\text{Answer},\text{Abstain},\text{Escalate}}
$$

Ý nghĩa:

- **Answer**: cung cấp câu trả lời khi có đủ bằng chứng và đạt yêu cầu an toàn.
- **Abstain**: từ chối trả lời khi thiếu dữ liệu, độ tin cậy thấp hoặc không tìm thấy tài liệu phù hợp.
- **Escalate**: chuyển đến bác sĩ hoặc chuyên gia khi câu hỏi có nguy cơ cao, khẩn cấp hoặc vượt khả năng hệ thống.

Output nên kèm theo:

- Bằng chứng y khoa được truy xuất
- Nguồn trích dẫn
- Mức độ tin cậy
- Cảnh báo hoặc khuyến nghị gặp chuyên gia khi cần

## 3. Các ẩn cần tìm

“Ẩn cần tìm” của bài toán có thể chia thành hai nhóm.

### 3.1. Tham số cần học trong training

#### Tham số của mô hình truy xuất

$$
\phi
$$

Tham số ($\phi$) quyết định cách biểu diễn câu hỏi và tài liệu trong không gian embedding, từ đó xác định tài liệu nào liên quan.

Hàm đánh giá độ liên quan có thể viết:

$$
s_{\phi}(q,c)
$$

với (c) là một chunk trong kho tri thức.

#### Tham số của LLM

$$
\theta
$$

LLM học phân phối:

$$
P_{\theta}(y\mid q,p,h,C)
$$

Tức là xác suất sinh câu trả lời ($y$), dựa trên câu hỏi, bối cảnh bệnh nhân, lịch sử hội thoại và bằng chứng được truy xuất.

#### Tham số hoặc ngưỡng của bộ kiểm tra chất lượng

$$
\psi
$$

Tham số ($\psi$) dùng để quyết định câu trả lời có:

- Bám sát bằng chứng hay không
- Có chứa nội dung không an toàn hay không
- Có đủ độ tin cậy để trả lời hay không
- Có cần chuyển cho chuyên gia hay không

### 3.2. Các biến trung gian cần suy ra khi inference

Trong mỗi truy vấn, hệ thống phải suy ra:

- Ý định y khoa của người dùng ($m$)
- Các thực thể y khoa ($e$), như triệu chứng, thuốc, bệnh hoặc thời gian
- Query embedding ($z_q$)
- Tập bằng chứng liên quan ($C^*$)
- Câu trả lời nháp ($\tilde y$)
- Điểm groundedness, safety và confidence
- Quyết định cuối cùng ($d$)

Biến trung gian quan trọng nhất là:

$$
C^*=\operatorname{TopK}{c\in K}s{\phi}(q,c)
$$

Đây là tập Top-(K) đoạn tài liệu được hệ thống xác định là liên quan nhất.

---

## 4. Nguyên lý của bài toán

Bài toán hoạt động theo nguyên lý **Retrieval-Augmented Generation**, kết hợp truy xuất tri thức với khả năng sinh ngôn ngữ của LLM.

### Bước 1: Hiểu và chuẩn hóa câu hỏi

Từ câu hỏi, bối cảnh bệnh nhân và lịch sử hội thoại, hệ thống:

- Kiểm tra input
- Viết lại câu hỏi độc lập với lịch sử
- Xác định ý định
- Trích xuất thực thể y khoa

Kết quả là truy vấn đã xử lý:

$$
q' = f_{\text{preprocess}}(q,p,h)
$$

### Bước 2: Truy xuất bằng chứng y khoa

Câu hỏi được chuyển thành embedding:

$$
z_q=E_{\phi}(q')
$$

Sau đó hệ thống truy xuất kết hợp:

- **Dense retrieval**: dựa trên độ tương đồng ngữ nghĩa
- **Sparse retrieval**: dựa trên từ khóa, chẳng hạn BM25

Điểm tổng hợp có thể biểu diễn:

$$
s(q,c)=\alpha s_{\text{dense}}(q,c) +(1-\alpha)s_{\text{sparse}}(q,c)
$$

Hệ thống chọn các chunk có điểm cao nhất:

$$
C^*=\operatorname{TopK}_{c\in K}s(q,c)
$$

### Bước 3: Xây dựng prompt

Prompt cuối cùng được tạo từ:

$$
P=\operatorname{Concat} (I_{\text{safety}},q',p,h,C^*)
$$

Trong đó:

- ($I_{\text{safety}}$): hướng dẫn an toàn
- ($q'$): câu hỏi đã xử lý
- ($p$): bối cảnh bệnh nhân
- ($h$): lịch sử hội thoại
- ($C^*$): bằng chứng y khoa được truy xuất

### Bước 4: Sinh câu trả lời

Medical QA LLM sinh câu trả lời dựa trên prompt:

$$
\tilde y\arg\max_y P_{\theta}(y\mid q',p,h,C^*)
$$

Điểm quan trọng là LLM không chỉ trả lời từ kiến thức đã học trong tham số, mà phải ưu tiên bằng chứng từ Vector Database.

### Bước 5: Kiểm tra chất lượng và an toàn

Câu trả lời nháp được đánh giá theo các tiêu chí:

- **Relevance**: có trả lời đúng câu hỏi không
- **Groundedness**: có được hỗ trợ bởi bằng chứng không
- **Faithfulness**: có thêm thông tin không tồn tại trong tài liệu không
- **Medical safety**: có nguy cơ gây hại không
- **Completeness**: có bỏ sót thông tin quan trọng không
- **Confidence**: hệ thống có đủ chắc chắn không

Quyết định cuối cùng:

$d=g_{\psi}(q,C^*,\tilde y)$

Ví dụ:

$$
d= \begin{cases} \text{Answer}, & \text{nếu đủ bằng chứng và an toàn}\\ \text{Abstain}, & \text{nếu thiếu bằng chứng hoặc confidence thấp}\\ \text{Escalate}, & \text{nếu phát hiện tình huống nguy cơ cao} \end{cases}
$$

---

## 5. Nguyên lý training

### Huấn luyện retriever

Retriever được học để:

- Đưa câu hỏi gần với chunk liên quan
- Đưa câu hỏi xa các chunk không liên quan

Một dạng loss thường dùng:

$$
\mathcal L_{\text{ret}} \log \frac{\exp(s_{\phi} q,c^+))} {\exp(s_{\phi}(q,c^+)) +\sum_{c^-}\exp(s_{\phi}(q,c^-))}
$$

Trong đó:

- ($c^+$): chunk đúng
- ($c^-$): chunk không liên quan hoặc hard negative

### Fine-tune LLM

Từ câu hỏi, context truy xuất và câu trả lời chuẩn, LLM được huấn luyện để sinh câu trả lời đúng:

$$
\mathcal L_{\text{gen}} \sum_t \log P_{\theta} \left( y_t^* \mid y_{<t}^*,q,p,h,C \right)
$$

### Hàm mục tiêu tổng hợp

Toàn bộ hệ thống có thể được tối ưu bằng:

$$
\mathcal L \lambda_{\text{ret}}\mathcal L_{\text{ret}} + \lambda_{\text{gen}}\mathcal L_{\text{gen}} + \lambda_{\text{safe}}\mathcal L_{\text{safe}}
$$

Trong đó:

- ($\mathcal L_{\text{ret}}$): lỗi truy xuất
- ($\mathcal L_{\text{gen}}$): lỗi sinh câu trả lời
- ($\mathcal L_{\text{safe}}$): lỗi liên quan đến an toàn, hallucination và quyết định abstain/escalate

---

## 6. Phát biểu bài toán hoàn chỉnh

> Cho một câu hỏi y khoa, bối cảnh bệnh nhân, lịch sử hội thoại và một kho tri thức y khoa đã được kiểm chứng, hệ thống cần truy xuất các bằng chứng liên quan nhất, sử dụng LLM để tạo câu trả lời bám sát bằng chứng, sau đó đánh giá độ chính xác, tính nhất quán và mức độ an toàn để quyết định trả lời, từ chối trả lời hoặc chuyển câu hỏi đến chuyên gia y tế.
> 

Có thể biểu diễn toàn bộ bài toán bằng ánh xạ:

$$
F_{\phi,\theta,\psi}: (q,p,h,K) \longrightarrow (C^*,\hat y,d)
$$

Trong đó mục tiêu cuối cùng không đơn thuần là sinh câu trả lời hay, mà là:

$$
\boxed{ \text{Trả lời đúng} + \text{bám sát tài liệu} + \text{an toàn} + \text{biết từ chối khi không  chắc chắn}}
$$

## PIPELINE

## Training

https://excalidraw.com/#json=43eR95hZKc1FgU1ZsCVR_,3pA7OlETVKwUk0mfT61lLQ

## Bước 1 — Data Ingestion & Preprocessing

### Medical Knowledge / Clinical Guidelines

Thu thập dữ liệu từ:

- Giáo trình và tài liệu y khoa
- Hướng dẫn lâm sàng
- Phác đồ chẩn đoán, điều trị
- Các câu hỏi–đáp đã được kiểm chứng

Đây là nguồn tri thức mà hệ thống sẽ sử dụng để xây dựng kho RAG.

### Raw Medical Knowledge

Lưu trữ tài liệu y khoa ở dạng ban đầu như PDF, Word, HTML hoặc dữ liệu từ cơ sở dữ liệu.

### Text Extraction & Cleaning

Thực hiện:

- Trích xuất văn bản từ tài liệu
- Loại bỏ header, footer, ký tự lỗi và nội dung trùng lặp
- Chuẩn hóa thuật ngữ, đơn vị và định dạng
- Loại bỏ hoặc ẩn thông tin nhận dạng bệnh nhân
- Kiểm tra nguồn và phiên bản tài liệu

**Đầu ra:** văn bản y khoa sạch và có thể xử lý.

### Chunking & Metadata Annotation

Chia tài liệu dài thành các đoạn nhỏ gọi là **chunk**.

Mỗi chunk được gắn metadata như:

- Tên tài liệu
- Chuyên khoa
- Chủ đề hoặc bệnh lý
- Ngày ban hành
- Phiên bản
- Tổ chức phát hành
- Số trang hoặc vị trí trong tài liệu
- Mức độ tin cậy của nguồn

**Đầu ra:** các chunk có đủ thông tin để truy xuất và trích dẫn.

### Processed Chunks

Tập hợp các chunk y khoa đã được làm sạch, chia nhỏ và gắn metadata.

---

## Bước 2 — Knowledge Indexing

### Embedding Model

Chuyển mỗi chunk từ văn bản thành một vector số biểu diễn ý nghĩa ngữ nghĩa của đoạn văn.

Ví dụ, các đoạn cùng nói về “triệu chứng viêm phổi” sẽ có vector gần nhau trong không gian embedding.

### Vector Database

Lưu trữ:

- Vector của từng chunk
- Nội dung chunk
- Metadata
- Thông tin nguồn trích dẫn

Vector Database cho phép tìm nhanh các đoạn có nội dung gần với câu hỏi.

**Đầu ra:** kho tri thức y khoa đã được lập chỉ mục.

> Bước này là **xây dựng kho RAG**, chưa phải fine-tune LLM.
> 

---

## Bước 3 — Retrieval Dataset Creation

### Training QA Pairs

Bộ dữ liệu gồm:

- Câu hỏi y khoa
- Bối cảnh bệnh nhân, nếu có
- Câu trả lời chuẩn
- Tài liệu hoặc bằng chứng chuẩn, nếu có

### Generate Queries

Chuẩn hóa hoặc tạo các truy vấn dùng để huấn luyện, ví dụ:

- Viết lại câu hỏi theo nhiều cách
- Tạo câu hỏi từ tài liệu
- Bổ sung câu hỏi nối tiếp từ lịch sử hội thoại
- Tạo câu hỏi khó hoặc câu hỏi không đủ thông tin

### Retrieve Top-K Relevant Chunks

Với mỗi câu hỏi:

1. Chuyển câu hỏi thành embedding.
2. Truy vấn Vector Database.
3. Kết hợp dense retrieval và sparse retrieval.
4. Chọn K chunk liên quan nhất.
5. Có thể rerank để đưa bằng chứng tốt nhất lên đầu.

**Đầu ra:** tập bằng chứng được truy xuất cho từng câu hỏi.

### RAG Training Examples

Ghép thành một mẫu huấn luyện hoàn chỉnh:

```
System instruction
+ Question
+ Patient context
+ Chat history
+ Retrieved medical evidence
→ Ground-truth answer
```

Mỗi mẫu dạy mô hình cách:

- Đọc bằng chứng
- Trả lời dựa trên bằng chứng
- Trích dẫn nguồn
- Không bịa thêm thông tin
- Từ chối khi bằng chứng không đủ
- Chuyển chuyên gia trong trường hợp nguy cơ cao

---

## Bước 4 — LLM Fine-tuning

### Base LLM

Mô hình ngôn ngữ nền chưa được chuyên biệt hoàn toàn cho bài toán Medical QA.

### Supervised Fine-tuning — SFT

Huấn luyện mô hình bằng các RAG training examples.

Mô hình học cách:

- Hiểu câu hỏi y khoa
- Sử dụng context được truy xuất
- Ưu tiên bằng chứng hơn kiến thức nhớ sẵn
- Sinh câu trả lời đúng cấu trúc
- Trích dẫn tài liệu
- Thể hiện độ không chắc chắn
- Chọn Answer, Abstain hoặc Escalate

### Medical QA LLM

Mô hình sau fine-tuning, được sử dụng trong pipeline inference.

> Nếu embedding model cũng cần học, nên bổ sung một bước riêng là **Retriever Fine-tuning**. Sau khi retriever thay đổi, phải tạo lại embedding và cập nhật Vector Database.
> 

---

## Bước 5 — Evaluation

### Retrieval Evaluation

Kiểm tra hệ thống có tìm đúng bằng chứng không.

Có thể đánh giá bằng:

- Recall@K
- Precision@K
- MRR
- nDCG
- Tỷ lệ tài liệu chuẩn xuất hiện trong Top-K

### Generation Evaluation

Kiểm tra câu trả lời của LLM:

- Có đúng nội dung không
- Có trả lời đúng câu hỏi không
- Có bám sát bằng chứng không
- Có hallucination không
- Có trích dẫn đúng nguồn không
- Có an toàn về mặt y khoa không

### End-to-End QA Evaluation

Đánh giá toàn bộ chuỗi:

```
Question
→ Retrieval
→ Prompt
→ LLM answer
→ Quality filter
→ Final decision
```

Kiểm tra cả ba đầu ra:

- Trả lời đúng khi đủ bằng chứng
- Abstain đúng khi thiếu bằng chứng
- Escalate đúng khi có nguy cơ cao

### Output của training

Training pipeline tạo ra:

- Vector Database
- Bộ RAG training examples
- Medical QA LLM đã fine-tune
- Các ngưỡng quality/safety
- Kết quả đánh giá
- Model checkpoint tốt nhất

## Inference

https://excalidraw.com/#json=5UPF3-qdmHqjIQju9mvk8,0keQUILNgGLDwokTPoGpSA

## Bước 1 — Query Understanding & Preprocessing

### User Question

Câu hỏi hiện tại của người dùng.

### Patient Context

Thông tin liên quan đến bệnh nhân như:

- Tuổi
- Giới tính
- Triệu chứng
- Tiền sử bệnh
- Thuốc đang dùng
- Dị ứng
- Kết quả xét nghiệm

Chỉ sử dụng những dữ liệu cần thiết và được phép sử dụng.

### Chat History

Lịch sử hội thoại giúp hệ thống hiểu các câu nối tiếp như:

> “Thuốc đó có tác dụng phụ gì?”
> 

### Input Validation

Kiểm tra đầu vào:

- Có trống hoặc lỗi định dạng không
- Có chứa dữ liệu không hợp lệ không
- Có dấu hiệu cấp cứu hoặc nguy cơ cao không
- Có yêu cầu ngoài phạm vi hệ thống không
- Có chứa dữ liệu nhạy cảm cần xử lý không

### Query Rewriting / History Condensation

Viết lại câu hỏi thành một truy vấn độc lập, đầy đủ ngữ cảnh.

Ví dụ:

```
“Thuốc đó có tác dụng phụ gì?”
```

được viết lại thành:

```
“Các tác dụng phụ thường gặp của amoxicillin ở bệnh nhân 35 tuổi là gì?”
```

### Medical Intent & Entity Extraction

Xác định:

- Ý định: hỏi triệu chứng, thuốc, chẩn đoán, điều trị hay tiên lượng
- Tên bệnh
- Tên thuốc
- Triệu chứng
- Liều lượng
- Thời gian
- Bộ phận cơ thể
- Yếu tố nguy cơ

### Processed Query

Câu hỏi cuối cùng đã được chuẩn hóa để đưa sang retrieval.

---

## Bước 2 — Retrieval

### Query Embedding

Chuyển processed query thành vector bằng cùng embedding model đã dùng khi lập chỉ mục tài liệu.

### Vector Database

Kho chứa các chunk y khoa đã được lập chỉ mục từ training pipeline.

### Hybrid Retrieval — Dense + Sparse

Kết hợp hai cách tìm kiếm:

- **Dense retrieval:** tìm theo ý nghĩa ngữ nghĩa
- **Sparse retrieval:** tìm theo từ khóa và thuật ngữ chính xác

Ví dụ, sparse retrieval hữu ích với tên thuốc hoặc mã bệnh; dense retrieval hữu ích khi người dùng diễn đạt khác với tài liệu.

### Retrieve Top-K Relevant Chunks

Lấy các đoạn tài liệu có điểm liên quan cao nhất.

Nên bổ sung:

- Lọc theo metadata
- Loại bỏ chunk hết hiệu lực
- Ưu tiên hướng dẫn mới và đáng tin cậy
- Rerank các kết quả
- Kiểm tra mức độ đủ bằng chứng

### Retrieved Evidence / Context

Tập bằng chứng cuối cùng được chuyển sang bước tạo prompt, bao gồm:

- Nội dung chunk
- Nguồn tài liệu
- Ngày hoặc phiên bản
- Điểm liên quan
- Metadata cần thiết để trích dẫn

---

## Bước 3 — Prompt Construction

### System Safety Instruction

Định nghĩa quy tắc cho mô hình:

- Chỉ trả lời dựa trên bằng chứng
- Không tự tạo chẩn đoán chắc chắn khi thiếu dữ liệu
- Không tự ý thay thế bác sĩ
- Không tạo liều thuốc ngoài tài liệu
- Phải chỉ ra khi thông tin chưa đủ
- Phải chuyển chuyên gia khi có dấu hiệu nguy hiểm

### Question + Patient Context + History

Đưa vào prompt:

- Câu hỏi đã chuẩn hóa
- Thông tin bệnh nhân liên quan
- Phần lịch sử hội thoại cần thiết

### Retrieved Medical Evidence

Đưa các chunk đã truy xuất vào prompt và đánh dấu rõ nguồn của từng chunk.

### Final Prompt

Prompt cuối cùng có dạng:

```
System safety instruction
+ Processed question
+ Relevant patient context
+ Condensed chat history
+ Retrieved medical evidence
+ Required answer format
```

---

## Bước 4 — Answer Generation

### Medical QA LLM

Mô hình đã fine-tune đọc final prompt và sinh câu trả lời.

### Draft Answer

Câu trả lời nháp có thể gồm:

- Câu trả lời chính
- Giải thích
- Bằng chứng hỗ trợ
- Trích dẫn nguồn
- Cảnh báo
- Mức độ không chắc chắn

Draft answer chưa được gửi ngay cho người dùng mà phải qua Quality Check.

---

## Bước 5 — Quality Check

### Quality Assurance

Kiểm tra câu trả lời theo các tiêu chí:

- **Relevance:** có trả lời đúng câu hỏi không
- **Groundedness:** có được bằng chứng hỗ trợ không
- **Faithfulness:** có thêm thông tin ngoài context không
- **Citation:** trích dẫn có đúng tài liệu không
- **Completeness:** có bỏ sót cảnh báo quan trọng không
- **Safety:** có nguy cơ gây hại không
- **Confidence:** có đủ chắc chắn để trả lời không
- **Consistency:** có mâu thuẫn với bệnh sử hoặc tài liệu không

### Filter

Bộ lọc quyết định một trong ba nhánh.

#### Answer

Chọn khi:

- Có bằng chứng đủ mạnh
- Câu trả lời bám sát tài liệu
- Không phát hiện rủi ro nghiêm trọng
- Trích dẫn hợp lệ

#### Abstain

Chọn khi:

- Không tìm được bằng chứng phù hợp
- Các nguồn mâu thuẫn nhau
- Câu hỏi thiếu thông tin
- Mức độ tin cậy thấp
- Câu hỏi nằm ngoài phạm vi hệ thống

Ví dụ:

> “Tôi chưa có đủ thông tin đáng tin cậy để trả lời câu hỏi này.”
> 

#### Escalate

Chọn khi:

- Có dấu hiệu cấp cứu
- Cần khám trực tiếp
- Liên quan đến quyết định điều trị nguy cơ cao
- Có khả năng phản ứng thuốc nghiêm trọng
- Cần bác sĩ đánh giá hồ sơ đầy đủ

## MONG MUỐN ĐÓNG GÓP

Đóng góp chính của đề tài không nên được mô tả đơn giản là **“ứng dụng LLM và RAG vào hỏi–đáp y khoa”**, vì RAG đã là một kỹ thuật phổ biến. Điểm đóng góp nên nằm ở cách bạn **thiết kế, chuyên biệt hóa và kiểm soát toàn bộ hệ thống cho miền y khoa**.

### Đóng góp cốt lõi

> Đề tài hướng đến xây dựng một hệ thống hỏi–đáp y khoa dựa trên LLM và RAG có khả năng truy xuất bằng chứng từ nguồn tri thức đáng tin cậy, sinh câu trả lời bám sát tài liệu và tự động lựa chọn giữa ba hành động: trả lời, từ chối trả lời hoặc chuyển đến chuyên gia, nhằm giảm hallucination và nâng cao độ an toàn trong quá trình hỗ trợ người dùng.
> 

## Các đóng góp cụ thể

### 2. Thiết kế cơ chế truy xuất phù hợp với dữ liệu y khoa

Đề tài kết hợp:

- **Dense retrieval** để tìm theo ngữ nghĩa
- **Sparse retrieval** để tìm chính xác tên bệnh, thuốc, xét nghiệm và thuật ngữ chuyên môn

Luồng truy xuất:

```
Câu hỏi đã xử lý
→ Query embedding
→ Hybrid retrieval
→ Lấy Top-K chunk
→ Lọc hoặc xếp hạng bằng chứng
```

Đóng góp mong muốn là nâng cao khả năng tìm đúng bằng chứng, đặc biệt khi câu hỏi của người dùng không sử dụng cùng cách diễn đạt với tài liệu chuyên môn.

---

### 4. Đề xuất cơ chế an toàn Answer–Abstain–Escalate

Một đóng góp nổi bật của hệ thống là không bắt buộc LLM phải trả lời mọi câu hỏi.

Sau khi sinh câu trả lời nháp, hệ thống đánh giá:

- Độ liên quan
- Độ chính xác y khoa
- Groundedness
- Faithfulness
- Độ đầy đủ của bằng chứng
- Độ chính xác của trích dẫn
- Mức độ rủi ro
- Độ tin cậy

Sau đó đưa ra một trong ba quyết định:

$$
d\in{\text{Answer},\text{Abstain},\text{Escalate}}
$$

- **Answer:** bằng chứng đầy đủ và câu trả lời an toàn.
- **Abstain:** bằng chứng thiếu, mâu thuẫn hoặc độ tin cậy thấp.
- **Escalate:** tình huống có nguy cơ cao hoặc cần bác sĩ đánh giá.

Điểm đóng góp ở đây là biến hệ thống từ một chatbot “luôn cố trả lời” thành một hệ thống có khả năng tự nhận biết giới hạn.

---

### 5. Đánh giá hệ thống theo nhiều tầng

Đề tài không chỉ đánh giá câu trả lời cuối cùng mà đánh giá riêng từng thành phần.

#### Đánh giá retrieval

- Recall@K
- Precision@K
- MRR
- nDCG
- Tỷ lệ tìm thấy tài liệu chuẩn

#### Đánh giá generation

- Độ chính xác y khoa
- Relevance
- Faithfulness
- Groundedness
- Citation correctness
- Hallucination rate

#### Đánh giá end-to-end

- Tỷ lệ trả lời đúng
- Tỷ lệ abstain đúng
- Tỷ lệ phát hiện trường hợp cần escalate
- Tỷ lệ câu trả lời nguy hiểm
- Độ ổn định trong hội thoại nhiều lượt

Đóng góp này giúp xác định lỗi đến từ retriever, LLM hay quality filter, thay vì chỉ đo một chỉ số tổng quát.

---

## Điểm mới nên nhấn mạnh

Điểm mới của đề tài có thể được trình bày theo công thức:

$$
\boxed{\text{Medical knowledge grounding} + \text{Hybrid retrieval} + \text{Context-aware generation} + \text{Safety-aware decision}}
$$

Trong đó, phần có khả năng tạo khác biệt lớn nhất là:

> **Cơ chế kiểm soát câu trả lời dựa trên chất lượng bằng chứng và mức độ rủi ro để quyết định Answer, Abstain hoặc Escalate.**
> 

## Đoạn viết cho báo cáo

> Đề tài mong muốn đóng góp một kiến trúc hỏi–đáp y khoa dựa trên LLM và RAG, trong đó câu trả lời được tạo ra từ các bằng chứng truy xuất trong kho tri thức y khoa đã được kiểm chứng. Hệ thống kết hợp truy xuất dense và sparse nhằm cải thiện khả năng tìm kiếm các đoạn tài liệu liên quan, đồng thời sử dụng dữ liệu gồm câu hỏi, bối cảnh bệnh nhân, lịch sử hội thoại và bằng chứng truy xuất để chuyên biệt hóa mô hình ngôn ngữ cho bài toán Medical QA. Bên cạnh khả năng sinh câu trả lời, đề tài đề xuất lớp kiểm tra chất lượng và an toàn nhằm đánh giá mức độ bám sát bằng chứng, độ chính xác của trích dẫn, độ tin cậy và mức độ rủi ro. Từ đó, hệ thống có thể lựa chọn trả lời, từ chối trả lời hoặc chuyển đến chuyên gia thay vì luôn tạo ra một câu trả lời. Đề tài cũng xây dựng quy trình đánh giá theo ba cấp độ gồm retrieval, generation và end-to-end, qua đó xác định rõ hiệu quả cũng như hạn chế của từng thành phần trong hệ thống.
> 

## Lưu ý khi tuyên bố đóng góp

Không nên xem các nội dung sau là đóng góp mới nếu chỉ sử dụng lại:

- Dùng Vector Database
- Dùng embedding
- Dùng một LLM có sẵn
- Dùng RAG cơ bản
- Dùng SFT thông thường

Đóng góp thật sự cần nằm ở ít nhất một trong các yếu tố:

- Bộ dữ liệu hoặc kho tri thức y khoa riêng
- Phương pháp truy xuất được tối ưu
- Cách tạo RAG training examples
- Cơ chế kiểm tra groundedness và safety
- Chính sách Answer–Abstain–Escalate
- Bộ tiêu chí và kết quả thực nghiệm chứng minh hệ thống tốt hơn baseline.

## RELATED WORKS

**“Integrating Fine-Tuning and Retrieval-Augmented Generation for Healthcare AI Systems: A Scoping Review” — Collaco et al., 2026**

## 1. Mục tiêu của paper

Paper khảo sát các hệ thống y tế kết hợp đồng thời:

- **Fine-tuning — FT:** giúp LLM học thuật ngữ, kiểu suy luận và hành vi chuyên biệt cho miền y khoa.
- **Retrieval-Augmented Generation — RAG:** truy xuất kiến thức bên ngoài, cập nhật và có thể kiểm chứng tại thời điểm inference.

Ý tưởng cốt lõi là:

FT học caˊch xử lyˊ baˋi toaˊn y khoa+RAG cung caˆˊp ba˘ˋng chứng cập nhật\boxed{
\text{FT học cách xử lý bài toán y khoa}
+
\text{RAG cung cấp bằng chứng cập nhật}
}

FT học caˊch xử lyˊ baˋi toaˊn y khoa+RAG cung caˆˊp ba˘ˋng chứng cập nhật

LLM thông thường dễ hallucination, thiếu kiến thức chuyên sâu và có kiến thức tĩnh. FT cải thiện khả năng chuyên môn nhưng tốn tài nguyên, có nguy cơ catastrophic forgetting và vẫn không cập nhật kiến thức liên tục. RAG cung cấp kiến thức mới và nguồn truy xuất nhưng có thể không tạo được năng lực suy luận chuyên ngành sâu. Vì vậy, hai phương pháp được xem là bổ sung cho nhau.

---

## 2. Điều kiện để được xem là hệ thống FT + RAG thật sự

Paper định nghĩa một hệ thống hybrid FT + RAG phải đáp ứng đủ ba điều kiện:

1. **LLM phải được cập nhật tham số**, bằng full fine-tuning hoặc PEFT như LoRA, QLoRA.
2. **Retrieval phải được sử dụng tại inference**, để lấy kiến thức ngoài và đưa vào prompt.
3. FT và RAG phải nằm trong cùng một pipeline end-to-end và được đánh giá như một hệ thống tích hợp.

Vì vậy:

```
Dùng RAG để tạo dữ liệu huấn luyện
→ Sau đó inference chỉ dùng LLM
```

thì **chưa được paper xem là hệ thống FT + RAG đầy đủ**.

Kiến trúc đúng là:

```
Training:
Medical dataset
→ Fine-tune LLM

Inference:
Clinical query
→ Retrieve Top-K từ Vector Database
→ Prompt augmentation
→ Fine-tuned Medical LLM
→ Answer
```

Hình 1 của paper cũng mô tả hai nhánh hoạt động song song: nhánh fine-tuning tạo Healthcare LLM chuyên biệt, trong khi nhánh RAG truy xuất Top-K chunk từ kho tri thức và đưa chúng vào mô hình khi suy luận.

---

## 3. Phương pháp khảo sát

Nhóm tác giả tìm kiếm trên PubMed, IEEE Xplore, Google Scholar và Embase, tuân theo PRISMA-ScR và hướng dẫn của Joanna Briggs Institute.

Quy trình chọn bài:

```
326 bài ban đầu
→ 266 bài sau loại trùng
→ 38 bài được đọc toàn văn
→ Chỉ 7 bài đáp ứng đủ tiêu chí FT + RAG
```

Nhiều bài bị loại vì:

- Chỉ dùng RAG mà không fine-tune LLM
- Chỉ fine-tune mà không retrieval khi inference
- Không thuộc y tế
- Không có đánh giá thực nghiệm

Việc chỉ tìm được **7 nghiên cứu phù hợp** cho thấy FT + RAG tích hợp trong y tế vẫn là một hướng khá mới và chưa có nhiều bằng chứng thực nghiệm.

---

## 4. Các kỹ thuật được sử dụng

### Fine-tuning

Phần lớn nghiên cứu không full fine-tune toàn bộ mô hình mà sử dụng:

- LoRA
- QLoRA
- Federated LoRA
- LoRA kết hợp reinforcement learning
- LoRA kết hợp DPO
- RAG-aware fine-tuning

PEFT được ưu tiên vì:

- Ít tốn GPU và bộ nhớ hơn
- Dễ triển khai ở bệnh viện
- Dễ cập nhật theo chuyên khoa
- Không cần huấn luyện lại toàn bộ LLM

### RAG

Các kiến trúc retrieval rất đa dạng:

- **Dense RAG:** dùng embedding và Vector Database
- **Hybrid RAG:** kết hợp sparse và dense
- **Hierarchical RAG:** tìm ở cấp tài liệu rồi đến đoạn nhỏ
- **Multimodal RAG:** truy xuất văn bản và ảnh y khoa
- **Federated RAG:** truy xuất từ nhiều tổ chức mà không chia sẻ dữ liệu gốc
- **Knowledge-graph RAG:** truy xuất theo thực thể và quan hệ y khoa

Dense RAG thường được dùng cho Medical QA. Hybrid retrieval phù hợp với QA sinh học và tóm tắt hồ sơ. Hierarchical và multimodal retrieval được sử dụng cho báo cáo lâm sàng, ảnh y khoa và các bài toán phức tạp hơn.

---

## 5. Các ứng dụng được khảo sát

Bảy nghiên cứu bao phủ những nhiệm vụ sau:

- Medical chatbot và Medical QA
- Biomedical QA
- Tóm tắt hội thoại bác sĩ–bệnh nhân thành SOAP note
- Sinh báo cáo thử nghiệm lâm sàng
- Medical visual question answering
- Sinh báo cáo X-quang, nhãn khoa và bệnh lý
- Hỗ trợ quyết định lâm sàng
- Truy xuất liên tổ chức có bảo vệ quyền riêng tư

Các base model phổ biến gồm LLaMA, Mistral, Gemma, Phi, Qwen, DeepSeek và LLaVA-Med.

---

## 6. Kết quả chính

Nhìn chung, các hệ thống FT + RAG được báo cáo có lợi thế về:

- Độ chính xác
- Factual consistency
- Khả năng xử lý kiến thức y khoa chưa xuất hiện trong training
- Groundedness
- Giảm hallucination
- Sự ưu tiên của chuyên gia
- Khả năng triển khai trong môi trường tài nguyên hạn chế

Một số kết quả tiêu biểu:

- Medical chatbot dùng Mistral-7B đạt tối đa khoảng **57% exact-match accuracy** trên benchmark trắc nghiệm.
- CLINICSUM được chuyên gia lâm sàng ưu tiên trong **61%** so sánh cặp.
- MMed-RAG báo cáo cải thiện factual accuracy khoảng **18,5% cho Medical VQA** và **69,1% cho report generation** so với baseline tương ứng.
- Một hệ thống multimodal RAG–LLM giảm hallucination xuống khoảng **6%**, thấp hơn hơn 40% so với prompt-only baseline, đồng thời giảm thời gian soạn báo cáo khoảng **75%**.

Tuy nhiên, các số liệu này đến từ các mô hình, dataset và nhiệm vụ khác nhau nên không thể xem là một bảng xếp hạng trực tiếp. Kết luận “FT + RAG tốt hơn” hiện vẫn chủ yếu mang tính định hướng vì số nghiên cứu còn ít và thiết kế đánh giá không đồng nhất.

---

## 7. Hạn chế của nghiên cứu hiện tại

Paper chỉ ra ba khoảng trống lớn.

### Bằng chứng còn ít

Chỉ có bảy nghiên cứu đáp ứng tiêu chí hybrid FT + RAG thật sự. Vì vậy chưa thể khẳng định cấu hình nào luôn tốt nhất.

### Đánh giá thiếu thống nhất

Các nghiên cứu dùng nhiều metric khác nhau như:

- Accuracy
- BLEU, ROUGE
- BERTScore
- F1, AUROC
- Hallucination rate
- Đánh giá chuyên gia

Nhiều nghiên cứu chưa đánh giá đầy đủ:

- Safety
- Bias
- Robustness
- Privacy
- Hiệu quả dài hạn
- Khả năng triển khai trong workflow bệnh viện

### Khó xác định lỗi nằm ở retriever hay generator

Một đáp án sai có thể do:

```
Retriever lấy sai tài liệu
```

hoặc:

```
Retriever lấy đúng
→ LLM hiểu hoặc sử dụng sai bằng chứng
```

Do đó, paper đề nghị phải đánh giá riêng:

```
Retrieval:
Recall, precision, evidence relevance

Generation:
Correctness, faithfulness, hallucination, safety

End-to-end:
Clinical usefulness và workflow impact
```

---

## 8. Hướng nghiên cứu tương lai

Paper đề xuất tập trung vào:

- **RAG-aware fine-tuning:** huấn luyện LLM cách sử dụng và lọc retrieved context.
- **Adaptive retrieval:** tự quyết định có cần retrieval và cần bao nhiêu chunk.
- **Clinician-in-the-loop:** bác sĩ tham gia đánh giá và hiệu chỉnh.
- **Uncertainty quantification:** mô hình phải thể hiện khi không chắc chắn.
- **Automated provenance tracking:** tự động theo dõi nguồn của từng kết luận.
- **Federated FT và federated retrieval:** khai thác dữ liệu nhiều bệnh viện mà không chia sẻ dữ liệu thô.
- **Standardized evaluation:** xây bộ đánh giá thống nhất về retrieval, generation, safety và clinical utility.
- **Workflow integration và governance:** tích hợp với hệ thống bệnh viện, quản lý phiên bản và trách nhiệm khi mô hình sai.

Paper nhấn mạnh rằng nghiên cứu tương lai không nên chỉ chạy theo tăng vài điểm accuracy, mà cần làm cho hệ thống **an toàn, có thể quản trị, bảo trì và triển khai thực tế**.

---

# Liên hệ trực tiếp với pipeline của bạn

Pipeline hiện tại của bạn phù hợp với kiến trúc paper:

```
Training:
Medical QA pairs
+ Retrieved context
→ LoRA/QLoRA fine-tuning
→ Medical QA LLM

Inference:
Question + patient context + chat history
→ Hybrid retrieval từ Vector Database
→ Prompt augmentation
→ Fine-tuned Medical QA LLM
→ Quality check
→ Answer / Abstain / Escalate
```

Điểm cần bảo đảm là **Vector Database phải tiếp tục được sử dụng khi inference**, không chỉ dùng để tạo RAG training examples.

So với các hệ thống trong survey, đề tài của bạn bổ sung một lớp an toàn rõ ràng hơn:

Answer  ∣  Abstain  ∣  Escalate\text{Answer}
\;|\;
\text{Abstain}
\;|\;
\text{Escalate}

Answer∣Abstain∣Escalate

Đây có thể là phần đóng góp chính, đặc biệt nếu bạn chứng minh được cơ chế này:

- Giảm trả lời khi bằng chứng không đủ
- Giảm hallucination nguy hiểm
- Phát hiện tốt tình huống cần bác sĩ
- Vẫn duy trì tỷ lệ trả lời hữu ích ở mức phù hợp

## Tóm tắt một đoạn dùng trong báo cáo

> Collaco và cộng sự khảo sát các hệ thống tích hợp fine-tuning và Retrieval-Augmented Generation trong y tế. Fine-tuning giúp mô hình học thuật ngữ, hành vi và năng lực suy luận chuyên biệt, trong khi RAG cung cấp kiến thức bên ngoài cập nhật, minh bạch và có thể truy xuất nguồn. Trong số 326 công trình ban đầu, chỉ bảy nghiên cứu đáp ứng đầy đủ tiêu chí gồm cập nhật tham số mô hình, sử dụng retrieval tại inference và đánh giá kiến trúc FT + RAG end-to-end. Các nghiên cứu chủ yếu sử dụng PEFT như LoRA hoặc QLoRA, kết hợp với dense, hybrid, hierarchical, multimodal hoặc federated RAG. Kết quả bước đầu cho thấy kiến trúc hybrid có thể cải thiện độ chính xác, factual grounding và khả năng giảm hallucination trong các nhiệm vụ như Medical QA, tóm tắt lâm sàng, sinh báo cáo và hỗ trợ quyết định. Tuy nhiên, số lượng nghiên cứu còn hạn chế, phương pháp đánh giá chưa thống nhất và thiếu các đánh giá đầy đủ về safety, privacy, bias và hiệu quả trong workflow thực tế. Vì vậy, các hướng cần tiếp tục nghiên cứu gồm RAG-aware fine-tuning, adaptive retrieval, đánh giá riêng retriever và generator, clinician-in-the-loop và quản trị hệ thống khi triển khai lâm sàng.
>