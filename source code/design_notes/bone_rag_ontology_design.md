# Ontology-Guided Context-Sensitive RAG for Bone Disease QA

## 1. Research Direction

### Working title

**Ontology-Guided Clinical Applicability Retrieval for Bone Disease Question Answering**

Alternative:

**Context-Sensitive Retrieval-Augmented Generation for Bone and Musculoskeletal Disease QA**

### Core problem

Vanilla RAG thường hoạt động theo:

```text
User Question
    ↓
Embedding / BM25
    ↓
Top-k semantically similar passages
    ↓
LLM
    ↓
Answer
```

Vấn đề là trong medical QA, đặc biệt với bone/musculoskeletal disease:

> **Semantically relevant evidence chưa chắc clinically applicable.**

Ví dụ:

```text
Q1:
A 70-year-old woman has osteoporosis.
What exercise should she do?

Q2:
A 70-year-old woman has osteoporosis and sustained
a vertebral compression fracture 2 weeks ago.
What exercise should she do?
```

Hai câu hỏi có:

- cùng disease;
- gần như cùng wording;
- cùng intent tổng quát là exercise/rehabilitation;

nhưng evidence thích hợp có thể hoàn toàn khác.

Do đó hypothesis chính:

\[
\boxed{
\text{Clinical relevance}
\neq
\text{semantic similarity alone}
}
\]

Và retrieval nên phụ thuộc vào:

\[
\boxed{
Disease + Anatomy + ClinicalState + PatientContext + Intent
}
\]

---

# 2. Why Bone / Musculoskeletal Disease?

Bone and musculoskeletal QA phù hợp với bài toán context-sensitive retrieval vì recommendation thường phụ thuộc mạnh vào:

- anatomical location;
- fracture status;
- post-operative state;
- disease stage;
- mobility / weight-bearing status;
- age;
- risk factors;
- rehabilitation stage;
- treatment history;
- structural stability.

Một evidence có thể đúng về disease nhưng sai về **clinical state**.

Ví dụ:

```text
General osteoporosis exercise guideline
```

có thể không phù hợp cho:

```text
Acute vertebral compression fracture
```

Bone disease cũng thường cần kết hợp:

```text
medicine
+ mechanics
+ anatomy
+ imaging
+ rehabilitation
+ patient state
```

Do đó đây là domain phù hợp để nghiên cứu:

> **Clinical applicability-aware retrieval.**

---

# 3. Main System Architecture

```text
                         USER
                          │
                          ▼
             Raw Natural-Language Query
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        Dense/BM25 Path      Intent & Context Parser
              │                       │
              │                Structured Context
              │                       │
              │                Ontology Normalizer
              │                       │
              │                Ontology Facets
              │                       │
              └───────────┬───────────┘
                          ▼
                  Candidate Retrieval
                          │
                          ▼
              Applicability Reranker
                          │
                          ▼
                  Top-k Evidence
                          │
                          ▼
                    Generator LLM
                          │
                          ▼
                    Draft Answer
                          │
                          ▼
              Clinical Response Verifier
                          │
              ┌───────────┼───────────┐
              │           │           │
             PASS       REVISE      ABSTAIN
              │           │           │
              ▼           └──→ Generator
         Final Answer
```

Ontology được dùng ở ba giai đoạn:

```text
Before Retrieval
→ query normalization

During Retrieval
→ applicability scoring

After Generation
→ consistency / response verification
```

---

# 4. User Query Representation

Không nên biểu diễn query chỉ bằng một vector duy nhất.

Dùng:

\[
Q_c =
(Disease,\ Anatomy,\ Patient,\ ClinicalState,\ Intent)
\]

Ví dụ user hỏi:

> “Mẹ tôi 72 tuổi bị osteoporosis, mới gãy đốt sống 2 tuần, giờ có đi bộ được không?”

Parser có thể output:

```json
{
  "disease": [
    "osteoporosis",
    "vertebral_compression_fracture"
  ],

  "anatomy": [
    "spine",
    "vertebra"
  ],

  "patient": {
    "age": 72,
    "age_group": "older_adult"
  },

  "clinical_state": {
    "phase": "acute_post_fracture",
    "time_since_event": "2_weeks"
  },

  "intent": {
    "primary": "rehabilitation",
    "secondary": [
      "mobility",
      "ambulation_safety"
    ]
  }
}
```

---

# 5. Intent & Context Parser

## 5.1 Purpose

Parser không phải diagnostic model.

Nhiệm vụ:

```text
Natural-language query
      ↓
Structured clinical information need
```

Parser hỗ trợ:

1. xác định user intent;
2. extract disease/anatomy/state;
3. extract patient-specific constraints;
4. normalize colloquial language;
5. xác định clinically decisive information;
6. tạo structured signals cho retriever.

---

## 5.2 Intent Taxonomy

Nên dùng **hierarchical + multi-label intent**.

```text
Clinical Intent
│
├── Disease Understanding
│   ├── definition
│   ├── etiology
│   ├── mechanism
│   ├── risk_factor
│   └── progression
│
├── Symptoms
│   ├── symptom_interpretation
│   └── severity
│
├── Diagnosis
│   ├── differential_diagnosis
│   ├── imaging
│   ├── laboratory_test
│   └── diagnostic_criteria
│
├── Treatment
│   ├── medication
│   ├── surgery
│   ├── conservative_management
│   └── treatment_comparison
│
├── Rehabilitation
│   ├── exercise
│   ├── physiotherapy
│   ├── mobility
│   ├── weight_bearing
│   └── return_to_activity
│
├── Prognosis
│   ├── recovery_time
│   ├── recurrence
│   └── complication_risk
│
├── Prevention
│   ├── fracture_prevention
│   ├── fall_prevention
│   └── lifestyle
│
├── Research / Evidence
│   ├── latest_research
│   ├── evidence_comparison
│   └── mechanism_evidence
│
└── Safety
    ├── contraindication
    ├── emergency_warning
    └── interaction
```

Ví dụ:

```text
"How long after hip surgery can I walk?"
```

có thể là:

```json
{
  "primary_intent": "rehabilitation",
  "secondary_intent": [
    "mobility",
    "prognosis"
  ]
}
```

---

# 6. Extraction Robustness

Parser có thể sai.

Do đó **không dùng parser output làm hard filter ngay**.

Sai parser:

\[
\text{Wrong extraction}
\Rightarrow
\text{wrong ontology mapping}
\Rightarrow
\text{wrong retrieval}
\]

## 6.1 Keep Raw + Structured Query

Giữ đồng thời:

\[
q_{raw}
\]

và:

\[
q_{structured}
\]

Retrieval:

\[
Score(d,q)
=
\alpha S_{semantic}(q_{raw},d)
+
\beta S_{ontology}(q_{structured},d)
\]

Nếu parser sai, raw semantic retrieval vẫn có khả năng cứu.

---

## 6.2 Confidence per Field

Không output:

```json
{
  "fracture": true
}
```

mà:

```json
{
  "fracture": {
    "value": "unknown",
    "confidence": 0.91,
    "status": "unknown"
  }
}
```

Hoặc:

```json
{
  "vertebral_fracture": {
    "value": "possible",
    "confidence": 0.37,
    "status": "inferred"
  }
}
```

Các trạng thái:

```text
explicit
inferred
unknown
```

Quan trọng:

\[
\boxed{
\text{missing information}
\neq
\text{negative information}
}
\]

Không nói surgery không có nghĩa:

```text
post_surgery = false
```

mà nên là:

```text
post_surgery = unknown
```

---

## 6.3 Evidence Span

Mỗi extraction nên có:

```json
{
  "clinical_state": {
    "value": "acute_post_fracture",
    "confidence": 0.97,
    "status": "explicit",
    "evidence_span": "vertebral fracture two weeks ago"
  }
}
```

Điều này giúp:

- audit parser;
- error analysis;
- explainability;
- benchmark extraction accuracy.

---

# 7. Normalized Query

`Normalized query` không thay thế encoder.

Nó là structured/standardized representation của query.

Ví dụ:

```text
"broken back bone"
```

normalize thành:

```text
vertebral fracture
```

```text
"can she walk?"
```

normalize thành:

```text
rehabilitation → mobility → ambulation
```

Raw query:

```text
"Mẹ tôi bị loãng xương, mới gãy lưng 2 tuần, giờ đi bộ được không?"
```

Normalized concepts:

```json
{
  "disease": "osteoporosis",
  "condition": "vertebral_fracture",
  "anatomy": "spine",
  "clinical_state": "acute_post_fracture",
  "intent": "rehabilitation",
  "sub_intent": "ambulation_safety"
}
```

---

# 8. Encoder and Retrieval

## 8.1 Encoder vẫn cần thiết

Raw query vẫn đi qua encoder:

\[
e_q = Encoder(q_{raw})
\]

Document chunk:

\[
e_d = Encoder(d)
\]

Semantic score:

\[
S_{semantic}
=
cos(e_q,e_d)
\]

Có thể kết hợp BM25:

\[
S_{candidate}
=
\alpha S_{dense}
+
\beta S_{BM25}
\]

---

## 8.2 Không nên flatten ontology thành một text query duy nhất

Không nên chỉ làm:

```text
normalized concepts
   ↓
convert to string
   ↓
encoder
   ↓
cosine similarity
```

vì khi đó ontology structure lại bị nén thành một vector.

Tốt hơn:

\[
\boxed{
Dense semantic signal
+
Structured ontology signal
}
\]

---

# 9. Ontology Design

Ontology nên rộng hơn clinical context.

Đề xuất các facet:

```text
Disease
Anatomy
Finding
Symptom
ClinicalState
PatientFactor
Intervention
Mechanism
Intent
EvidenceType
```

Ví dụ:

```text
Disease
├── Osteoporosis
├── Osteoarthritis
├── Osteomyelitis
├── BoneTumor
└── Fracture
    ├── VertebralFracture
    ├── HipFracture
    └── FemoralNeckFracture
```

```text
Anatomy
├── Skeleton
│   ├── Spine
│   │   └── Vertebra
│   └── LowerLimb
│       └── Femur
```

```text
ClinicalState
├── Stable
├── Acute
├── Chronic
├── PostFracture
├── PostOperative
└── RehabilitationPhase
```

```text
Intervention
├── Medication
├── Surgery
├── Exercise
├── Physiotherapy
└── Immobilization
```

```text
Intent
├── Diagnosis
├── Treatment
├── Rehabilitation
├── Prognosis
├── Prevention
├── Mechanism
└── Safety
```

```text
EvidenceType
├── Guideline
├── SystematicReview
├── RCT
├── ObservationalStudy
├── Review
└── ReferenceText
```

---

# 10. Ontology Relations

Core relations:

```text
isA
isPartOf
hasLocation
hasDisease
hasSymptom
hasFinding
hasTreatment
hasClinicalState
hasRiskFactor
recommendedFor
contraindicatedFor
supportsIntent
appliesToPopulation
relatedToMechanism
supportedByEvidence
```

Ví dụ:

```text
FemoralNeck
    isPartOf
ProximalFemur
    isPartOf
Femur
```

Do đó:

```text
query = femoral neck fracture
```

vẫn có thể match document:

```text
proximal femur fracture
```

nhờ ontology distance/hierarchy.

---

# 11. Ontology-Based Query Expansion

User có thể dùng:

```text
broken hip
```

Ontology normalize:

```text
HipFracture
```

và expand có kiểm soát:

```text
FemoralNeckFracture
IntertrochantericFracture
SubtrochantericFracture
```

Không expansion vô hạn.

Chỉ nên expand:

- synonym;
- parent;
- child;
- close anatomical relation;
- relevant intervention relation;
- intent relation.

---

# 12. Bone Domain Knowledge Base

DB không chỉ chứa clinical data.

Nó là:

\[
\boxed{
Bone\ Domain\ Knowledge\ Base
}
\]

Bao gồm:

```text
Clinical knowledge
Scientific knowledge
General medical knowledge
Rehabilitation knowledge
Drug / intervention knowledge
Ontology / terminology
Research papers
Guidelines
Reviews
Trials
Potential multimodal descriptions
```

Ví dụ sources:

```text
PMC Open Access
WHO musculoskeletal rehabilitation resources
AAOS guidelines
systematic reviews
clinical guidelines
selected research papers
trusted medical reference texts
```

---

# 13. DB Schema

Không nên dùng một schema clinical-only.

Core relational schema:

## documents

```text
id
title
source
source_type
publication_date
authors
license
url
```

`source_type`:

```text
guideline
paper
review
clinical_trial
rehab_protocol
drug_reference
reference_text
ontology
patient_case
imaging_report
```

---

## chunks

```text
id
document_id
section
text
embedding
```

---

## concepts

```text
concept_id
name
type
parent_id
```

Ví dụ:

```text
C001 | osteoporosis          | Disease
C002 | vertebral_fracture    | Disease
C003 | spine                 | Anatomy
C004 | rehabilitation        | Intent
C005 | acute_post_fracture   | ClinicalState
```

---

## relations

```text
subject_concept_id
relation_type
object_concept_id
```

Ví dụ:

```text
Vertebra     isPartOf      Spine
Exercise     isA           Intervention
Walking      isA           Ambulation
Ambulation   isA           Mobility
```

---

## chunk_concepts

```text
chunk_id
concept_id
relation
confidence
provenance
```

Ví dụ:

```text
chunk_42 | osteoporosis         | applies_to
chunk_42 | vertebral_fracture   | applies_to
chunk_42 | spine                | has_location
chunk_42 | rehabilitation       | supports_intent
chunk_42 | acute_post_fracture  | applicable_state
```

---

# 14. Recommended Storage Stack

MVP:

```text
PostgreSQL
+ pgvector
+ Python ingestion pipeline
+ OWL / JSON ontology
```

Không cần Neo4j ở giai đoạn đầu.

OWL/ontology file:

```text
bone_ontology.owl
```

có thể là source-of-truth.

Runtime:

```text
OWL
 ↓
Ontology Loader
 ↓
concepts
relations
synonyms
hierarchy
 ↓
PostgreSQL
```

---

# 15. Retrieval Pipeline

## Stage 1 — Candidate Retrieval

Dùng:

```text
Dense retrieval
+
BM25
```

Ví dụ top:

```text
Top-50 / Top-100
```

Dense search vẫn dựa vào raw query.

Có thể thêm normalized-query search nhưng không thay thế raw search.

---

## Stage 2 — Ontology / Applicability Reranking

Ví dụ query:

```text
Disease       = osteoporosis
Fracture      = vertebral_fracture
Anatomy       = spine
State         = acute_post_fracture
Intent        = rehabilitation
Sub-intent    = mobility
```

Dense retrieval:

```text
D1: General osteoporosis exercise
D2: Vertebral fracture rehabilitation
D3: Osteoporosis medication
D4: Fall prevention
```

Semantic scores:

```text
D1 = 0.91
D2 = 0.84
```

Nhưng ontology matching:

```text
D1:
Disease             ✓
Exercise            ✓
Rehabilitation      partial
Acute fracture      ✗
Anatomy             partial
```

```text
D2:
Disease             ✓
Fracture            ✓
Anatomy             ✓
Clinical state      ✓
Rehabilitation      ✓
```

Reranking có thể đảo:

\[
D2 > D1
\]

---

# 16. Applicability Score

Basic:

\[
Score(d,q)
=
\alpha S_{semantic}
+
\beta S_{ontology}
\]

Chi tiết:

\[
S_{ontology}
=
w_D S_D
+
w_A S_A
+
w_S S_S
+
w_P S_P
+
w_I S_I
+
w_E S_E
\]

Trong đó:

- \(S_D\): disease match
- \(S_A\): anatomy match
- \(S_S\): clinical-state match
- \(S_P\): patient/population match
- \(S_I\): intent match
- \(S_E\): evidence/source suitability

Một formulation mạnh hơn:

\[
\boxed{
Score(d,q)
=
S_{semantic}(d,q)
+
\lambda A(d,C_q)
-
\gamma V(d,C_q)
}
\]

Trong đó:

- \(A\): clinical applicability;
- \(V\): ontology / clinical constraint violation.

---

# 17. Confidence-Aware Ontology Scoring

Nếu parser output field confidence \(c_j\):

\[
Score(d,q)
=
\alpha S_{raw}
+
\beta \sum_j c_jS_{ontology,j}
-
\gamma \sum_j c_jV_j
\]

Nếu:

\[
c_j \approx 1
\]

field ảnh hưởng mạnh.

Nếu:

\[
c_j \approx 0
\]

field gần như bị bỏ qua.

Điều này giúp hệ thống degrade gracefully khi parser sai.

---

# 18. Multi-Hypothesis Intent Retrieval

Nếu parser không chắc:

```text
rehabilitation = 0.55
diagnosis      = 0.40
prognosis      = 0.05
```

không cần ép chọn một intent.

Dùng:

\[
P(I|q)
\]

và:

\[
Score(d,q)
=
S_{semantic}
+
\sum_i P(I_i|q)S(d,I_i)
\]

Có thể retrieve theo nhiều intent hypothesis rồi rerank chung.

---

# 19. Knowledge-Type Routing

Intent có thể điều chỉnh loại evidence được ưu tiên.

Ví dụ:

```text
intent = definition
```

boost:

```text
reference text
review
trusted overview
```

```text
intent = treatment recommendation
```

boost:

```text
clinical guideline
systematic review
RCT
```

```text
intent = latest research
```

boost:

```text
recent papers
clinical trials
```

```text
intent = rehabilitation
```

boost:

```text
rehab guideline
physiotherapy protocol
```

Scoring:

\[
Score(d,q)
=
\alpha S_{semantic}
+
\beta S_{concept}
+
\gamma S_{context}
+
\delta S_{intent}
+
\eta S_{source}
\]

---

# 20. Generator LLM

Generator nên được **giữ frozen ở baseline chính**.

Pipeline:

```text
Top-k evidence
+ structured patient/context information
+ question
↓
Frozen LLM
↓
Draft answer
```

Lý do:

Nếu fine-tune generator ngay:

\[
\text{better answer}
\]

khó biết là do:

```text
better retrieval
```

hay:

```text
LLM memorization / adaptation
```

Giữ frozen generator giúp isolate contribution:

\[
\boxed{
Retrieval\ improvement
\rightarrow
QA\ improvement
}
\]

Fine-tuning generator chỉ nên là optional phase.

---

# 21. If Fine-Tuning Is Used

Ưu tiên fine-tune:

```text
Retriever / Reranker
```

trước generator.

Training sample:

```text
Query:
72F, osteoporosis, acute vertebral fracture,
what exercise is appropriate?

Positive:
acute post-fracture rehabilitation evidence

Hard Negative:
general osteoporosis exercise/prevention evidence
```

Train:

\[
(q,d^+,d^-)
\]

để:

\[
Score(q,d^+) > Score(q,d^-)
\]

Đây là đúng contribution:

> same disease/topic, different clinical applicability.

---

# 22. Clinical Response Verifier

Không trả trực tiếp generator output.

Thêm:

\[
\boxed{
Clinical\ Response\ Verifier
}
\]

Pipeline:

```text
Generator
   ↓
Draft Answer
   ↓
Verifier
   ↓
PASS / REVISE / ABSTAIN
```

---

# 23. Verifier Inputs

Verifier nên nhận:

```json
{
  "original_query": "...",

  "parsed_query": {
    "intent": "...",
    "disease": [],
    "anatomy": [],
    "clinical_state": [],
    "patient_context": {}
  },

  "retrieved_evidence": [
    "...",
    "..."
  ],

  "draft_answer": "..."
}
```

---

# 24. Verifier Checks

## 24.1 Groundedness

Check:

\[
Evidence \models Claim
\]

Mỗi claim trong answer phải được retrieved evidence support.

---

## 24.2 Clinical Applicability

Evidence có thể factually đúng nhưng không applicable.

Check:

\[
Applicable(Evidence, PatientContext)?
\]

Ví dụ:

```text
General osteoporosis exercise
```

không mặc định applicable cho:

```text
acute vertebral fracture
```

---

## 24.3 Ontology Consistency

Ví dụ ontology có:

```text
AcutePostFracture
    contraindicatedFor
HighImpactActivity
```

Draft answer nói:

```text
"Start unrestricted high-impact exercise immediately."
```

Verifier flag:

```text
ONTOLOGY_CONTRADICTION
```

---

## 24.4 Citation Verification

Check từng:

\[
Claim_i
\leftrightarrow
Citation_i
\]

Không chỉ check citation có cùng topic.

Phải check:

> citation thật sự support claim.

---

## 24.5 Missing Evidence

Nếu evidence không đủ:

```text
INSUFFICIENT_EVIDENCE
```

Verifier được phép:

\[
\boxed{ABSTAIN}
\]

---

# 25. Verifier Architecture

Không nên chỉ dùng cùng một LLM hỏi:

```text
"Is this answer correct?"
```

Tốt hơn:

```text
             Draft Answer
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Claim     Citation   Ontology
     Checker     Checker    Checker
        │         │         │
        └─────────┼─────────┘
                  ▼
             Decision Logic
                  │
       PASS / REVISE / ABSTAIN
```

Có thể dùng:

- LLM claim decomposition;
- NLI/LLM entailment;
- deterministic ontology rules;
- citation support checker;
- rule-based final decision.

---

# 26. Avoid Infinite Revision

Không:

```text
generate
→ verify
→ regenerate
→ verify
→ ...
```

Nên:

```text
Draft
 ↓
Verify
 ↓
Maximum 1 revision
 ↓
Verify again
 ↓
PASS or ABSTAIN
```

---

# 27. Dataset / Corpus Strategy

Không nhất thiết có một dataset duy nhất tên:

```text
BoneDiseaseKnowledge
```

Nên xây:

\[
\boxed{
BoneContext-RAG
}
\]

gồm:

```text
1. Bone Domain Knowledge Corpus
2. User Questions
3. Patient / Clinical Contexts
4. Positive Evidence
5. Hard Negatives
6. Counterfactual Variants
7. Relevance / Applicability Labels
```

---

# 28. Suggested Knowledge Sources

Main corpus có thể lấy từ:

```text
PMC Open Access bone/MSK subset
+
WHO musculoskeletal rehabilitation resources
+
AAOS / other clinical guidelines
+
selected systematic reviews
+
selected clinical trials
```

Ontology paper có thể dùng như **conceptual schema/reference**, không nhất thiết là corpus.

---

# 29. Dataset Sample Schema

```json
{
  "query_id": "Q001",

  "raw_query": "Can a 72-year-old woman with osteoporosis walk two weeks after a vertebral fracture?",

  "intent": {
    "primary": "rehabilitation",
    "secondary": ["mobility_safety"]
  },

  "clinical_context": {
    "disease": ["osteoporosis"],
    "condition": ["vertebral_fracture"],
    "anatomy": ["spine"],
    "age_group": "older_adult",
    "clinical_state": ["acute_post_fracture"]
  },

  "positive_passage_ids": [
    "P0082"
  ],

  "hard_negative_passage_ids": [
    "P0041"
  ],

  "changed_constraint": null
}
```

Counterfactual:

```json
{
  "query_id": "Q002",

  "parent_query_id": "Q001",

  "raw_query": "Can a 72-year-old woman with osteoporosis exercise if she has no recent fracture?",

  "changed_constraint": {
    "field": "fracture_status",
    "from": "acute_fracture",
    "to": "no_recent_fracture"
  }
}
```

---

# 30. Core Benchmark: Context Sensitivity

Original:

```text
70F
osteoporosis
no fracture
exercise question
```

Expected:

\[
D_{general\ exercise}
>
D_{acute\ rehab}
\]

Counterfactual:

```text
70F
osteoporosis
NEW vertebral fracture
2 weeks ago
same exercise question
```

Expected:

\[
D_{acute\ rehab}
>
D_{general\ exercise}
\]

Test:

\[
\boxed{
Context_1 \rightarrow Context_2
\Rightarrow
Ranking_1 \rightarrow Ranking_2
}
\]

---

# 31. Intent Sensitivity Benchmark

Giữ patient/context giống nhau.

Chỉ đổi intent.

Example:

```text
Q1:
72F with osteoporosis.
What medication should she take?

Q2:
72F with osteoporosis.
What exercises should she perform?
```

Expected ranking phải đổi.

Đánh giá:

\[
\boxed{
Intent\ Sensitivity
}
\]

---

# 32. Clinical-State Sensitivity Benchmark

Giữ disease và intent giống nhau.

Chỉ đổi clinical state.

Example:

```text
Q1:
Osteoporosis — what exercise should she do?

Q2:
Osteoporosis + acute vertebral fracture —
what exercise should she do?
```

Đánh giá:

\[
\boxed{
Clinical\ State\ Sensitivity
}
\]

---

# 33. Parser Robustness Benchmark

Cố tình corruption parser output:

```text
0%
10%
20%
30%
```

So sánh:

```text
Hard ontology filtering
vs
Soft confidence-aware ontology reranking
```

Metric:

\[
\boxed{
Robustness\ to\ Clinical\ Context\ Extraction\ Errors
}
\]

---

# 34. Retrieval Evaluation

Baseline:

```text
R0 = BM25
R1 = Dense
R2 = Dense + BM25
R3 = Dense + Intent
R4 = Dense + Intent + ClinicalState
R5 = Dense + Ontology
R6 = Dense + Ontology + Applicability Reranker
```

Core metrics:

```text
Recall@k
MRR
nDCG@k
Precision@k
```

Task-specific metrics:

```text
Context Sensitivity
Intent Sensitivity
Clinical-State Sensitivity
Applicability Accuracy
Hard-Negative Rejection Rate
```

---

# 35. End-to-End QA Evaluation

So sánh:

```text
No RAG
Vanilla RAG
Patient-conditioned RAG
Ontology-guided RAG
Ontology-guided RAG + Verifier
```

Giữ cùng generator nếu có thể.

Đánh giá:

```text
Factual correctness
Evidence faithfulness
Clinical applicability
Citation correctness
Unsupported claim rate
Unsafe / inapplicable recommendation rate
Abstention quality
```

---

# 36. Ablation Study

Có thể ablate:

```text
- no intent
- no clinical state
- no anatomy
- no ontology hierarchy
- no confidence weighting
- no source-type weighting
- no verifier
```

Mục tiêu:

> Xác định component nào thực sự đóng góp vào retrieval/QA performance.

---

# 37. Thesis Contributions

Có thể định nghĩa contribution thành 3 phần:

## Contribution 1 — Structured Query Representation

\[
\boxed{
Natural\ language
\rightarrow
Intent + Context + Ontology\ concepts
}
\]

---

## Contribution 2 — Clinical Applicability Retrieval

\[
\boxed{
Semantic\ relevance
+
Ontology\ compatibility
+
Clinical\ applicability
}
\]

---

## Contribution 3 — Context-Sensitive Benchmark

\[
\boxed{
Counterfactual\ context\ change
\rightarrow
Expected\ ranking\ change
}
\]

Optional:

## Contribution 4 — Evidence-Grounded Response Verification

\[
\boxed{
Generate
\rightarrow
Verify
\rightarrow
PASS / REVISE / ABSTAIN
}
\]

---

# 38. Recommended MVP

Không cần build hệ thống quá lớn ngay.

## Ontology

7–10 facet chính:

```text
Disease
Anatomy
ClinicalState
PatientFactor
Intervention
Intent
Mechanism
EvidenceType
```

## Relations

```text
isA
isPartOf
hasLocation
hasClinicalState
recommendedFor
contraindicatedFor
supportsIntent
appliesToPopulation
```

## DB

```text
PostgreSQL + pgvector
```

## Retriever

```text
BM25 + Dense
```

## Reranker

```text
SemanticScore
+
OntologyApplicability
```

## Parser

```text
Frozen LLM structured output
```

## Generator

```text
Frozen capable LLM
```

## Verifier

```text
Claim support
+
Ontology consistency
+
Citation support
+
PASS / REVISE / ABSTAIN
```

---

# 39. Recommended Development Order

```text
Phase 1
Build Bone Knowledge Corpus

Phase 2
Build ontology schema

Phase 3
Annotate chunks with concepts

Phase 4
Implement BM25 + Dense baseline

Phase 5
Implement Intent & Context Parser

Phase 6
Implement Ontology Applicability Reranker

Phase 7
Build context-sensitive benchmark

Phase 8
Run retrieval ablations

Phase 9
Add frozen LLM generator

Phase 10
Add response verifier

Phase 11
Run end-to-end QA evaluation

Phase 12
Optional fine-tune retriever/reranker
```

---

# 40. Final Concept

The full research idea can be summarized as:

\[
\boxed{
\text{User Question}
+
\text{Patient / Clinical Context}
\rightarrow
\text{Ontology-Aware Interpretation}
\rightarrow
\text{Applicability-Aware Retrieval}
\rightarrow
\text{Evidence-Grounded Generation}
\rightarrow
\text{Clinical Verification}
}
\]

The key research statement is:

> **A document can be semantically relevant to a bone-disease question while being clinically inapplicable to the user's current state. Therefore, retrieval should model disease, anatomy, patient/context, clinical state, intent, and ontology relations instead of relying only on semantic similarity.**

The central empirical question is:

\[
\boxed{
\text{When a clinically decisive context changes, does the retrieved evidence ranking change appropriately?}
}
\]

That is the main distinction from a standard:

```text
documents
→ embeddings
→ vector DB
→ top-k
→ LLM
```

RAG system.
