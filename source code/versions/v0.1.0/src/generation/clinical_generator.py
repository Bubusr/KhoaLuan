import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Tuple

from langfuse import observe, Langfuse
from src.generation.base import BaseGenerator
from src.models import StructuredQuery

def _call_g4f_llm(prompt_text: str) -> str:
    """Gọi mô hình ngôn ngữ miễn phí qua g4f (OperaAria provider)."""
    import g4f
    response = g4f.ChatCompletion.create(
        model="",
        provider=g4f.Provider.OperaAria,
        messages=[{"role": "user", "content": prompt_text}],
    )
    return response

class ClinicalGenerator(BaseGenerator):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # --- Temporarily disabled Gemini, force using g4f ---
        # if self.api_key:
        #     genai.configure(api_key=self.api_key)
        #     self.model = genai.GenerativeModel("gemini-3.6-flash")
        #     self.use_llm = True
        #     print("Gemini API configured for Clinical Generator.")
        # else:
        self.use_llm = False
        print("Gemini disabled by user. Forcing g4f fallback for Clinical Generator.")

        # Khởi tạo Langfuse Client nếu có cấu hình
        self.langfuse = None
        if False: # os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            # Đồng bộ host nếu cần
            if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
                os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_BASE_URL")
            try:
                self.langfuse = Langfuse()
                print("Langfuse Prompt Management initialized in Clinical Generator.")
            except Exception as e:
                print(f"Failed to initialize Langfuse client: {e}")

    def evaluate_decision(self, query: str, chunks: List[Dict[str, Any]], structured_query: StructuredQuery) -> str:
        q = query.lower()
        state = structured_query.clinical_state.phase
        
        # 1. ESCALATE: Các tình huống nguy kịch cao (Red Flags)
        is_emergency = any(w in q for w in ["severe pain", "cannot walk", "paralysis", "đau dữ dội", "không đi được", "liệt", "ulcer", "fever", "suppuration"])
        
        # Ca 1: Gãy xương cấp tính (Acute fracture / Red flag)
        if state == "AcutePostFracture" or (("fracture" in q or "gãy" in q) and any(w in q for w in ["2 week", "two week", "recent", "acute", "mới"])):
            return "Escalate"
            
        # Ca 2: Nhiễm trùng xương tiến triển (Osteomyelitis / Diabetic foot ulcer / Spondylodiscitis)
        if state == "ActiveInfection" or ("osteomyelitis" in q and any(w in q for w in ["infection", "ulcer", "suppuration", "vertebral", "foot"])):
            return "Escalate"
            
        # 2. OFF-TOPIC: Câu hỏi không liên quan y khoa → trả lời bình thường
        medical_keywords = [
            # English
            "pain", "bone", "joint", "fracture", "disease", "treatment", "therapy",
            "exercise", "medication", "symptom", "surgery", "doctor", "clinic",
            "gout", "arthritis", "osteo", "muscle", "spine", "knee", "hip", "foot",
            "infection", "fever", "swelling", "drug", "vitamin", "calcium",
            # Vietnamese
            "đau", "xương", "khớp", "gãy", "bệnh", "điều trị", "thuốc", "triệu chứng",
            "tập", "phẫu thuật", "bác sĩ", "gút", "viêm", "cơ", "cột sống", "sưng",
            "nhiễm trùng", "vitamin", "canxi", "loãng", "thoái hóa",
        ]
        # 2. ABSTAIN: Câu hỏi mơ hồ thiếu dữ kiện bệnh lý, giải phẫu hoặc tài liệu độ tin cậy thấp
        has_disease = bool(structured_query.disease)
        has_anatomy = bool(structured_query.anatomy)
        is_state_known = (state != "unknown")

        # Nếu là câu hỏi y khoa nhưng hoàn toàn không xác định được bệnh và giải phẫu -> Không thể kê đơn/tư vấn an toàn
        if not has_disease and not has_anatomy and not is_state_known:
            return "Abstain"

        if not chunks or chunks[0]["score"] < 0.40:
            return "Abstain"

        return "Answer"

    def _mock_generate(self, query: str, chunks: List[Dict[str, Any]], structured_query: StructuredQuery, decision: str, history: List[Dict] = None) -> str:
        # Tự động detect ngôn ngữ chính bằng thư viện langdetect
        try:
            from langdetect import detect
            lang = detect(query)
            is_vietnamese = (lang == "vi")
        except Exception:
            is_vietnamese = False

        if decision == "Escalate":
            if structured_query.clinical_state.phase == "ActiveInfection":
                return (
                    "[Clinical Decision: ESCALATE]\n"
                    + ("CẢNH BÁO: Nhiễm trùng xương đang hoạt động (Osteomyelitis) là bệnh nhiễm trùng xương nghiêm trọng. "
                       "Tì lực lên chi bị ảnh hưởng có nguy cơ gãy xương bệnh lý cực kỳ cao. "
                       "Vui lòng tham khảo ý kiến bác sĩ phẫu thuật chỉnh hình ngay lập tức và hạn chế tì đè lực cho đến khi độ ổn định của xương được xác nhận."
                       if is_vietnamese else
                       "WARNING: Active osteomyelitis is a severe bone infection. Putting weight on the affected limb "
                       "poses an extremely high risk of pathological bone fracture. Please consult an orthopedic surgeon "
                       "immediately and restrict weight-bearing until bone stability is confirmed.")
                )
            return (
                "[Clinical Decision: ESCALATE]\n"
                + ("CẢNH BÁO: Vì bạn bị gãy xương cột sống gần đây (trong vòng 2-6 tuần), việc thực hiện các bài tập "
                   "mà không có sự giám sát trực tiếp sẽ có nguy cơ cao làm lún xẹp cột sống thêm. "
                   "Vui lòng tham khảo ý kiến chuyên gia cột sống hoặc nhà vật lý trị liệu ngay lập tức trước khi thử bất kỳ hoạt động thể chất nào."
                   if is_vietnamese else
                   "WARNING: Since you have a recent vertebral fracture (within the last 2-6 weeks), performing exercises "
                   "without direct supervision poses a high risk of further spinal collapse. Please consult a spine specialist "
                   "or physical therapist immediately before attempting any physical activity.")
            )
        elif decision == "Abstain":
            return (
                "[Clinical Decision: ABSTAIN]\n"
                + ("Xin lỗi, cơ sở dữ liệu y tế đã xác minh không chứa đủ bằng chứng lâm sàng để trả lời câu hỏi của bạn một cách an toàn. "
                   "Vui lòng tham khảo ý kiến của chuyên gia y tế để được hướng dẫn."
                   if is_vietnamese else
                   "I apologize, but the verified medical database does not contain sufficient clinical evidence "
                   "to answer your question safely. Please consult a healthcare professional for guidance.")
            )
        else:
            top_chunk = chunks[0]["chunk"]
            chunk_id = getattr(top_chunk, "id", "")
            chunk_text = getattr(top_chunk, "text", "")
            
            if chunk_id == "P001":
                return (
                    "[Clinical Decision: ANSWER]\n"
                    + ("Để chăm sóc loãng xương chung, các hoạt động aerobic chịu lực (đi bộ, chạy bộ nhẹ) "
                       "và tập kháng lực được khuyến nghị để duy trì mật độ xương, với điều kiện không có gãy xương đang hoạt động."
                       if is_vietnamese else
                       "For general osteoporosis care, weight-bearing aerobic activities (walking, light jogging) "
                       "and resistance training are recommended to maintain bone density, provided there are no active fractures.")
                )
            elif chunk_id == "P003":
                return (
                    "[Clinical Decision: ANSWER]\n"
                    + ("Đối với phục hồi chức năng sau gãy xương cột sống (6-12 tuần), khuyến nghị tập duỗi lưng và đi bộ. "
                       "Tránh gập cột sống cho đến khi độ ổn định của xương được xác nhận hoàn toàn."
                       if is_vietnamese else
                       "For post-acute spinal fracture rehab (6-12 weeks), back extensions and walking are recommended. "
                       "Avoid spinal flexion until full bone stability is verified.")
                )
            elif chunk_id == "P006":
                return (
                    "[Clinical Decision: ANSWER]\n"
                    + ("Đối với thoái hóa khớp gối, các bài tập dưới nước tác động thấp như bơi lội và thể dục nhịp điệu dưới nước rất được khuyến khích. "
                       "Tránh nhảy tác động cao hoặc squat nặng trong các đợt bùng phát."
                       if is_vietnamese else
                       "For knee osteoarthritis, low-impact water exercises like swimming and water aerobics are highly recommended. "
                       "Avoid high-impact jumping or heavy squats during flare-ups.")
                )
            elif chunk_id == "P007":
                return (
                    "[Clinical Decision: ANSWER]\n"
                    + ("Trong các đợt bùng phát viêm khớp dạng thấp đang hoạt động, hãy ưu tiên kéo giãn phạm vi chuyển động. "
                       "Chống chỉ định tập kháng lực nặng để ngăn ngừa tổn thương khớp."
                       if is_vietnamese else
                       "During active rheumatoid arthritis flare-ups, prioritize range-of-motion stretching. "
                       "Heavy resistance training is contraindicated to prevent joint damage.")
                )
            elif chunk_id == "P008":
                return (
                    "[Clinical Decision: ANSWER]\n"
                    + ("Đối với cơn gút cấp, tập trung vào việc nghỉ ngơi khớp và bổ sung nhiều nước. "
                       "Nghiêm ngặt tránh các thực phẩm giàu purine như thịt đỏ và hải sản."
                       if is_vietnamese else
                       "For an acute gout attack, focus on joint rest and high hydration. "
                       "Strictly avoid purine-rich foods like red meat and seafood.")
                )
            else:
                if is_vietnamese:
                    try:
                        from deep_translator import GoogleTranslator
                        translated_text = GoogleTranslator(source='en', target='vi').translate(chunk_text)
                        return f"[Clinical Decision: ANSWER]\n{translated_text}"
                    except Exception as e:
                        print(f"Failed to translate mock response: {e}")
                        return f"[Clinical Decision: ANSWER]\n[Bản dịch tài liệu]: {chunk_text}"
                else:
                    return f"[Clinical Decision: ANSWER]\n{chunk_text}"

    @observe(name="Clinical Generator (Response & Decision)")
    def generate_answer(self, query: str, chunks: List[Dict[str, Any]], structured_query: StructuredQuery, history: List[Dict] = None) -> Tuple[str, str]:
        decision = self.evaluate_decision(query, chunks, structured_query)
        history = history or []
        
        # Tự động detect ngôn ngữ chính bằng thư viện langdetect
        try:
            from langdetect import detect
            lang = detect(query)
            is_vietnamese = (lang == "vi")
        except Exception:
            is_vietnamese = False

        if decision == "Escalate":
            if structured_query.clinical_state.phase == "ActiveInfection":
                answer = (
                    "[Clinical Decision: ESCALATE]\n"
                    + ("CẢNH BÁO: Phát hiện nhiễm trùng xương đang tiến triển (Osteomyelitis). Tì lực lên chi bị ảnh hưởng có nguy cơ gãy xương rất cao. "
                       "Không đứng hoặc đi lại trên chân bị bệnh. Vui lòng đến cơ sở y tế khẩn cấp ngay lập tức."
                       if is_vietnamese else
                       "WARNING: Active osteomyelitis infection detected. Weight-bearing poses a high risk of bone fracture. "
                       "Do not stand or walk on the leg. Please seek emergency medical care immediately.")
                )
            else:
                answer = (
                    "[Clinical Decision: ESCALATE]\n"
                    + ("CẢNH BÁO: Bạn đang có gãy xương cột sống gần đây hoặc các triệu chứng khẩn cấp. "
                       "Chúng tôi không thể cung cấp hướng dẫn tự xử lý vì nguy cơ rất cao. "
                       "Vui lòng đến gặp bác sĩ hoặc phòng cấp cứu ngay lập tức."
                       if is_vietnamese else
                       "WARNING: You have indicated a recent spinal fracture or emergency symptoms. "
                       "We cannot provide specific self-management instructions because it poses a high risk. "
                       "Please escalate this situation and consult a medical doctor or visit an emergency room immediately.")
                )
            return answer, decision

        if decision == "Abstain":
            answer = (
                "[Clinical Decision: ABSTAIN]\n"
                + ("Xin lỗi, tôi không tìm thấy đủ bằng chứng lâm sàng trong hướng dẫn y tế đã được xác minh để trả lời câu hỏi của bạn một cách an toàn. "
                   "Vui lòng tham khảo ý kiến của nhân viên y tế."
                   if is_vietnamese else
                   "I apologize, but I cannot find sufficient clinical evidence in the verified medical guidelines "
                   "to answer your question safely.")
            )
            return answer, decision

        # Kiểm tra câu hỏi off-topic (không phải y khoa)
        medical_keywords = [
            "pain", "bone", "joint", "fracture", "disease", "treatment", "therapy",
            "exercise", "medication", "symptom", "surgery", "doctor", "clinic",
            "gout", "arthritis", "osteo", "muscle", "spine", "knee", "hip", "foot",
            "infection", "fever", "swelling", "drug", "vitamin", "calcium",
            "đau", "xương", "khớp", "gãy", "bệnh", "điều trị", "thuốc", "triệu chứng",
            "tập", "phẫu thuật", "bác sĩ", "gút", "viêm", "cơ", "cột sống", "sưng",
            "nhiễm trùng", "vitamin", "canxi", "loãng", "thoái hóa",
        ]
        is_medical = any(kw in query.lower() for kw in medical_keywords)

        if not is_medical:
            if os.getenv("EVAL_MODE") == "1":
                return "Mock Off-Topic Response", decision
            # Câu hỏi thông thường → gọi g4f trực tiếp như một chatbot bình thường
            try:
                g4f_answer = _call_g4f_llm(query)
                return g4f_answer.strip(), decision
            except Exception as e:
                print(f"g4f off-topic failed ({e}).")
                return ("Xin chào! Tôi là trợ lý y khoa chuyên về bệnh xương khớp. Bạn có câu hỏi nào về sức khỏe xương khớp không?"
                        if is_vietnamese else
                        "Hello! I am a medical assistant specializing in bone and joint conditions. Do you have any questions about bone health?"), decision

        context_str = ""
        for i, res in enumerate(chunks):
            chunk = res["chunk"]
            context_str += f"Guideline [{chunk.id}] - {chunk.title}:\n{chunk.text}\n\n"

        prompt_text = None
        # Thử lấy prompt từ Langfuse Cloud
        if self.langfuse:
            try:
                lf_prompt = self.langfuse.get_prompt("generator/clinical-generator")
                prompt_text = lf_prompt.compile(
                    query=query,
                    disease=str(structured_query.disease),
                    anatomy=str(structured_query.anatomy),
                    clinical_state=structured_query.clinical_state.phase,
                    context=context_str
                )
            except Exception as e:
                print(f"Failed to fetch prompt 'generator/clinical-generator' from Langfuse ({e}). Fallback to local prompt.")

        # Nếu lỗi hoặc không có Langfuse, dùng prompt offline mặc định
        if not prompt_text:
            # Dựng đoạn lịch sử hội thoại (nếu có)
            history_str = ""
            if history:
                history_lines = []
                for msg in history[-6:]:  # Giữ tối đa 3 lượt hỏi-đáp gần nhất
                    role = "Patient" if msg["role"] == "user" else "Assistant"
                    history_lines.append(f"{role}: {msg['content']}")
                history_str = "\n".join(history_lines)

            prompt_text = f"""
            You are a clinical medical QA assistant. Answer the patient's question based ONLY on the provided verified guidelines.
            Consider the conversation history below to understand the patient's context before answering.

            IMPORTANT: Detect the language of the patient's query and respond in THE SAME LANGUAGE.
            - If the query is in Vietnamese → answer in Vietnamese
            - If the query is in English → answer in English
            - Always keep medical terms accurate regardless of language

            --- Conversation History ---
            {history_str if history_str else "(No prior conversation)"}
            ----------------------------

            Current Patient Query: "{query}"
            
            Extracted Patient Context:
            - Disease: {structured_query.disease}
            - Anatomy: {structured_query.anatomy}
            - Clinical State: {structured_query.clinical_state.phase}

            Verified Medical Guidelines:
            {context_str}

            Draft a clear, professional, and safe answer in the SAME LANGUAGE as the patient's query. Prefix the answer with '[Clinical Decision: ANSWER]'.
            """

        try:
            if self.use_llm and self.api_key:
                response = self.model.generate_content(prompt_text, request_options={"timeout": 10})
                return response.text.strip(), decision
            else:
                return self._mock_generate(query, chunks, structured_query, decision, history), decision
        except Exception as e:
            return self._mock_generate(query, chunks, structured_query, decision, history), decision
