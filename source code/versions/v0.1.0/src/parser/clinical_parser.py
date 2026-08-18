import os
import json
import google.generativeai as genai
from langfuse import observe
from langfuse import Langfuse
from src.parser.base import BaseParser
from src.models import StructuredQuery, PatientContext, ClinicalState, QueryIntent

def _call_g4f_llm(prompt_text: str) -> str:
    """Gọi mô hình ngôn ngữ miễn phí qua g4f (OperaAria provider)."""
    import g4f
    response = g4f.ChatCompletion.create(
        model="",
        provider=g4f.Provider.OperaAria,
        messages=[{"role": "user", "content": prompt_text}],
    )
    return response


class ClinicalParser(BaseParser):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # --- Temporarily disabled Gemini, force using g4f ---
        # if self.api_key:
        #     genai.configure(api_key=self.api_key)
        #     self.model = genai.GenerativeModel("gemini-3.6-flash")
        #     self.use_llm = True
        #     print("Gemini API configured for Clinical Parser.")
        # else:
        self.use_llm = False
        print("Gemini disabled by user. Forcing g4f fallback for Clinical Parser.")

        # Khởi tạo Langfuse Client nếu có cấu hình
        self.langfuse = None
        if False: # os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            # Đồng bộ host nếu cần
            if False: # os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
                os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_BASE_URL")
            try:
                self.langfuse = Langfuse()
                print("Langfuse Prompt Management initialized in Clinical Parser.")
            except Exception as e:
                print(f"Failed to initialize Langfuse client: {e}")

    def _mock_parse(self, query: str) -> StructuredQuery:
        q = query.lower()
        disease = []
        anatomy = []
        phase = "unknown"
        time_since_event = "unknown"
        primary_intent = "rehabilitation"

        # 1. Bệnh lý
        if "osteoporosis" in q or "loãng xương" in q:
            disease.append("Osteoporosis")
        if "fracture" in q or "gãy" in q or "broken" in q:
            disease.append("VertebralFracture")
            if any(w in q for w in ["spine", "vertebra", "back", "lưng", "đốt sống"]):
                anatomy.append("Spine")
                anatomy.append("Vertebra")
        if "osteoarthritis" in q or "thoái hóa khớp" in q:
            disease.append("Osteoarthritis")
            if "knee" in q or "gối" in q:
                anatomy.append("Knee")
        if "rheumatoid" in q or "viêm khớp dạng thấp" in q:
            disease.append("RheumatoidArthritis")
        if "gout" in q or "gút" in q:
            disease.append("Gout")
        if "osteomyelitis" in q or "viêm xương tủy" in q or "infection" in q:
            disease.append("Osteomyelitis")

        # 2. Giai đoạn lâm sàng
        if any(w in q for w in ["2 weeks", "two weeks", "2 tuần", "mới", "recent"]):
            phase = "AcutePostFracture"
            time_since_event = "2_weeks"
        elif "swelling" in q or "viêm cấp" in q or "sưng" in q:
            phase = "FlareUp"
        elif "inflamed" in q or "tiến triển" in q:
            phase = "JointInflammation"
        elif "gout attack" in q or "cơn gút cấp" in q:
            phase = "AcuteGoutAttack"
        elif "active" in q or "nhiễm trùng" in q:
            phase = "ActiveInfection"
        elif "healed" in q or "stable" in q or "no fracture" in q or "không bị gãy" in q:
            phase = "Stable"

        # 3. Ý định
        if any(w in q for w in ["exercise", "walk", "tập", "đi bộ", "perform", "weightlifting", "jumping"]):
            primary_intent = "rehabilitation"
        elif any(w in q for w in ["safe", "danger", "nguy hiểm", "chống chỉ định", "ok to eat", "steak"]):
            primary_intent = "safety"

        return StructuredQuery(
            disease=disease,
            anatomy=anatomy,
            patient=PatientContext(age=72 if "72" in q else None, age_group="older_adult" if "72" in q or "mẹ" in q else "unknown"),
            clinical_state=ClinicalState(phase=phase, time_since_event=time_since_event),
            intent=QueryIntent(primary=primary_intent)
        )

    @observe(name="Clinical Parser (Extract Profile)")
    def parse(self, query: str) -> StructuredQuery:
        prompt_text = None
        # Thử lấy prompt từ Langfuse Cloud
        if self.langfuse:
            try:
                lf_prompt = self.langfuse.get_prompt("parser/clinical-parser")
                prompt_text = lf_prompt.compile(query=query)
            except Exception as e:
                print(f"Failed to fetch prompt 'parser/clinical-parser' from Langfuse ({e}). Fallback to local prompt.")

        # Nếu lỗi hoặc không có Langfuse, dùng prompt offline mặc định
        if not prompt_text:
            prompt_text = f"""
            Analyze this clinical medical query:
            "{query}"
            Extract concepts into structured JSON conforming to:
            disease: List[str] (e.g. Osteoporosis, VertebralFracture, Osteoarthritis, RheumatoidArthritis, Gout, Osteomyelitis)
            anatomy: List[str] (e.g. Spine, Vertebra, Knee)
            clinical_state: {{
                phase: str (e.g. AcutePostFracture, FlareUp, JointInflammation, AcuteGoutAttack, ActiveInfection, Stable, unknown)
            }}
            intent: {{
                primary: str (e.g. rehabilitation, safety, treatment)
            }}
            """

        try:
            if self.use_llm:
                response = self.model.generate_content(
                    prompt_text,
                    generation_config={"response_mime_type": "application/json"},
                    request_options={"timeout": 10},
                )
                data = json.loads(response.text.strip())
                return StructuredQuery(**data)
            else:
                raise Exception("Gemini LLM disabled (no API key). Using g4f fallback.")
        except Exception as e:
            print(f"LLM parsing failed ({e}). Trying g4f fallback...")

        try:
            g4f_response = _call_g4f_llm(
                prompt_text + "\n\nReturn ONLY valid JSON, no extra text."
            )
            import re
            json_match = re.search(r'\{.*\}', g4f_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return StructuredQuery(**data)
        except Exception as g4f_err:
            print(f"g4f parsing failed ({g4f_err}).")

        return self._mock_parse(query)
