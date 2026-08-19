from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FacetField(BaseModel):
    value: Any = None
    confidence: float = 1.0
    status: str = "explicit"  # explicit, inferred, unknown
    evidence_span: Optional[str] = None

class PatientContext(BaseModel):
    age: Optional[int] = None
    age_group: Optional[str] = "unknown"
    confidence: float = 1.0
    status: str = "unknown"
    evidence_span: Optional[str] = None

class ClinicalState(BaseModel):
    phase: str = "unknown"  # e.g., AcutePostFracture, Stable, Chronic, FlareUp, ActiveInfection, etc.
    time_since_event: str = "unknown"
    confidence: float = 1.0
    status: str = "unknown"
    evidence_span: Optional[str] = None

class QueryIntent(BaseModel):
    primary: str = "rehabilitation"  # e.g., rehabilitation, safety, diagnosis, treatment
    secondary: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    status: str = "explicit"
    evidence_span: Optional[str] = None

class StructuredQuery(BaseModel):
    disease: List[str] = Field(default_factory=list)
    disease_confidence: float = 1.0
    anatomy: List[str] = Field(default_factory=list)
    anatomy_confidence: float = 1.0
    patient: PatientContext = Field(default_factory=PatientContext)
    clinical_state: ClinicalState = Field(default_factory=ClinicalState)
    intent: QueryIntent = Field(default_factory=QueryIntent)

class Chunk(BaseModel):
    id: str
    title: str
    text: str
    concepts: List[str] = Field(default_factory=list)
    contraindications: Optional[List[str]] = None
    source_type: Optional[str] = "Guideline"
    evidence_level: Optional[str] = "High"
    target_population: Optional[str] = "Adults"

class Candidate(BaseModel):
    chunk: Chunk
    score: float
    semantic_score: float
    boost: float = 0.0
    penalty: float = 0.0
