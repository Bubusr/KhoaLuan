from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PatientContext(BaseModel):
    age: Optional[int] = None
    age_group: Optional[str] = "unknown"

class ClinicalState(BaseModel):
    phase: str = "unknown"  # e.g., AcutePostFracture, Stable, Chronic
    time_since_event: str = "unknown"

class QueryIntent(BaseModel):
    primary: str = "rehabilitation"  # e.g., rehabilitation, safety, diagnosis, treatment
    secondary: List[str] = []

class StructuredQuery(BaseModel):
    disease: List[str] = []
    anatomy: List[str] = []
    patient: PatientContext = Field(default_factory=PatientContext)
    clinical_state: ClinicalState = Field(default_factory=ClinicalState)
    intent: QueryIntent = Field(default_factory=QueryIntent)

class Chunk(BaseModel):
    id: str
    title: str
    text: str
    concepts: List[str] = []
    contraindications: Optional[List[str]] = None

class Candidate(BaseModel):
    chunk: Chunk
    score: float
    semantic_score: float
    boost: float = 0.0
    penalty: float = 0.0
