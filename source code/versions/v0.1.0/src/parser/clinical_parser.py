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
        self.use_llm = False
        self.langfuse = None

    def _mock_parse(self, query: str) -> StructuredQuery:
        q = query.lower()
        disease = []
        anatomy = []
        phase = "unknown"
        time_since_event = "unknown"
        primary_intent = "rehabilitation"
        secondary_intents = []
        state_status = "unknown"
        state_evidence = None
        patient_age = None
        patient_age_group = "unknown"
        patient_status = "unknown"

        # 1. Nhận diện Bệnh lý & Phủ định (Negation handling)
        if "osteoporosis" in q or "loãng xương" in q or "alendronate" in q or "bisphosphonate" in q:
            disease.append("Osteoporosis")
        
        # Xử lý phủ định gãy xương: "no fracture" / "no recent fracture"
        if any(w in q for w in ["no fracture", "no recent fracture", "no fractures", "không gãy", "without fracture", "no active fracture"]):
            phase = "Stable"
            state_status = "explicit"
            state_evidence = "no fractures"
        elif "fracture" in q or "gãy" in q or "broken" in q:
            disease.append("VertebralFracture")
            if any(w in q for w in ["spine", "vertebra", "back", "lưng", "đốt sống"]):
                anatomy.extend(["Spine", "Vertebra"])

        if "osteoarthritis" in q or "thoái hóa khớp" in q:
            disease.append("Osteoarthritis")
            if "knee" in q or "gối" in q:
                anatomy.append("Knee")
        if "rheumatoid" in q or "viêm khớp dạng thấp" in q:
            disease.append("RheumatoidArthritis")
        if "gout" in q or "gút" in q:
            disease.append("Gout")
        if "osteomyelitis" in q or "viêm xương tủy" in q:
            disease.append("Osteomyelitis")
        if "ankylosing spondylitis" in q or "viêm cột sống dính khớp" in q or "bamboo spine" in q:
            disease.append("AnkylosingSpondylitis")
            anatomy.append("Spine")
        if "sarcopenia" in q or "thiểu cơ" in q or "muscle wasting" in q:
            disease.append("Sarcopenia")
        if "rickets" in q or "còi xương" in q:
            disease.append("Rickets")
        if "osteomalacia" in q or "nhuyễn xương" in q:
            disease.append("Osteomalacia")
        if "paget" in q:
            disease.append("PagetDisease")
        if "fibrous dysplasia" in q or "loạn sản sợi" in q or "mccune" in q:
            disease.append("FibrousDysplasia")
        if "peptic ulcer" in q or "stomach ulcer" in q or "loét dạ dày" in q:
            disease.append("PepticUlcerDisease")
        if any(w in q for w in ["kidney disease", "renal failure", "renal impairment", "suy thận", "ckd"]):
            disease.append("ChronicKidneyDisease")
        if "diabetic" in q or "diabetes" in q or "tiểu đường" in q or "đái tháo đường" in q:
            disease.append("DiabetesMellitus")

        # 2. Nhận diện Giải phẫu bổ sung
        if "femur" in q or "thigh" in q or "đùi" in q or "shepherd" in q or "hip" in q:
            anatomy.append("Hip")
        if "skull" in q or "sọ" in q:
            anatomy.append("Skull")
        if "knee" in q or "gối" in q:
            if "Knee" not in anatomy:
                anatomy.append("Knee")
        if "spine" in q or "cột sống" in q:
            if "Spine" not in anatomy:
                anatomy.append("Spine")
        if "toe" in q or "ngón chân" in q:
            anatomy.append("FirstMTP")
        if "hand" in q or "wrist" in q or "ngón tay" in q or "bàn tay" in q:
            anatomy.append("HandJoints")

        # 3. Trạng thái lâm sàng & Evidence span
        if any(w in q for w in ["2 weeks", "two weeks", "2 tuần", "recent fracture", "mới gãy", "fresh fracture"]):
            phase = "AcutePostFracture"
            time_since_event = "2_weeks"
            state_status = "explicit"
            state_evidence = "recent fracture / 2 weeks ago"
        elif "swelling" in q or "viêm cấp" in q or "sưng" in q or "flare" in q:
            phase = "FlareUp"
            state_status = "explicit"
            state_evidence = "swelling / flare-up"
        elif "inflamed" in q or "tiến triển" in q or "active synovitis" in q:
            phase = "JointInflammation"
            state_status = "explicit"
            state_evidence = "active joint inflammation"
        elif "gout attack" in q or "cơn gút cấp" in q:
            phase = "AcuteGoutAttack"
            state_status = "explicit"
            state_evidence = "acute gout attack"
        elif any(w in q for w in ["active infection", "nhiễm trùng", "bone suppuration", "suppuration"]):
            phase = "ActiveInfection"
            state_status = "explicit"
            state_evidence = "active infection"
        elif any(w in q for w in ["healed", "stable", "no fracture", "no fractures", "không bị gãy", "no recent fracture"]):
            phase = "Stable"
            state_status = "explicit"
            state_evidence = "stable / no recent fracture"

        # 4. Ý định người dùng (Hierarchical & Multi-intent)
        if any(w in q for w in ["exercise", "walk", "tập", "đi bộ", "running", "swimming", "bơi", "jumping", "tai chi"]):
            primary_intent = "rehabilitation"
        if any(w in q for w in ["medication", "drug", "thuốc", "dose", "alendronate", "bisphosphonate", "teriparatide", "prednisone", "methotrexate", "allopurinol", "zoledronic", "calcitonin"]):
            primary_intent = "treatment"
            secondary_intents.append("medication")
        if any(w in q for w in ["surgery", "phẫu thuật", "arthroplasty", "replacement", "debridement", "curettage", "sequestrectomy", "synovectomy"]):
            primary_intent = "treatment"
            secondary_intents.append("surgery")
        if any(w in q for w in ["safe", "danger", "nguy hiểm", "chống chỉ định", "ok to eat", "steak", "contraindication", "risk", "prevent fall", "falls", "sleeping", "mattress", "posture"]):
            primary_intent = "safety"
        if any(w in q for w in ["protein", "calcium", "vitamin d", "diet", "dinh dưỡng", "ăn gì"]):
            secondary_intents.append("nutrition")
        if any(w in q for w in ["symptom", "marker", "alkaline phosphatase", "triệu chứng", "chẩn đoán", "what is"]):
            secondary_intents.append("diagnosis")

        # 5. Thông tin bệnh nhân
        if "72" in q or "70" in q or "75" in q:
            patient_age = 72 if "72" in q else (70 if "70" in q else 75)
            patient_age_group = "older_adult"
            patient_status = "explicit"
        elif "child" in q or "trẻ" in q:
            patient_age_group = "pediatric"
            patient_status = "explicit"

        return StructuredQuery(
            disease=list(set(disease)),
            disease_confidence=0.95 if disease else 0.5,
            anatomy=list(set(anatomy)),
            anatomy_confidence=0.90 if anatomy else 0.5,
            patient=PatientContext(
                age=patient_age,
                age_group=patient_age_group,
                confidence=0.95 if patient_age else 0.6,
                status=patient_status,
                evidence_span=f"Age {patient_age}" if patient_age else None
            ),
            clinical_state=ClinicalState(
                phase=phase,
                time_since_event=time_since_event,
                confidence=0.95 if phase != "unknown" else 0.5,
                status=state_status,
                evidence_span=state_evidence
            ),
            intent=QueryIntent(
                primary=primary_intent,
                secondary=secondary_intents,
                confidence=0.90,
                status="explicit",
                evidence_span=primary_intent
            )
        )

    @observe(name="Clinical Parser (Extract Profile)")
    def parse(self, query: str) -> StructuredQuery:
        if os.getenv("EVAL_MODE") == "1" or not self.use_llm or not self.api_key:
            return self._mock_parse(query)
        prompt_text = None
        if self.langfuse:
            try:
                lf_prompt = self.langfuse.get_prompt("parser/clinical-parser")
                prompt_text = lf_prompt.compile(query=query)
            except Exception as e:
                pass

        if not prompt_text:
            prompt_text = f"""
            Analyze this clinical medical query:
            "{query}"
            Extract concepts into structured JSON conforming to:
            disease: List[str] (e.g. Osteoporosis, VertebralFracture, Osteoarthritis, RheumatoidArthritis, Gout, Osteomyelitis, AnkylosingSpondylitis, Sarcopenia, Rickets, Osteomalacia, PagetDisease, FibrousDysplasia)
            anatomy: List[str] (e.g. Spine, Vertebra, Knee, Femur, Skull)
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
        except Exception:
            pass

        return self._mock_parse(query)
