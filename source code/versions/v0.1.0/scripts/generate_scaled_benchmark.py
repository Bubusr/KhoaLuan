import json
import os

def generate_scaled_data():
    print("Generating comprehensive Ontology...")
    
    # 1. Comprehensive Ontology Concepts
    concepts = [
        # Diseases (10 Core Bone & Musculoskeletal)
        {"id": "C001", "name": "Osteoporosis", "type": "Disease", "synonyms": ["bone loss", "thin bones", "low bone density", "loãng xương"]},
        {"id": "C002", "name": "VertebralFracture", "type": "Disease", "synonyms": ["vertebral compression fracture", "broken vertebra", "broken spine bone", "gãy lún cột sống"]},
        {"id": "C003", "name": "HipFracture", "type": "Disease", "synonyms": ["femoral neck fracture", "broken hip", "intertrochanteric fracture", "gãy cổ xương đùi"]},
        {"id": "C004", "name": "Osteoarthritis", "type": "Disease", "synonyms": ["degenerative joint disease", "wear and tear arthritis", "thoái hóa khớp"]},
        {"id": "C005", "name": "RheumatoidArthritis", "type": "Disease", "synonyms": ["inflammatory arthritis", "autoimmune joint disease", "viêm khớp dạng thấp"]},
        {"id": "C006", "name": "Gout", "type": "Disease", "synonyms": ["gouty arthritis", "hyperuricemia", "podagra", "bệnh gút"]},
        {"id": "C007", "name": "Osteomyelitis", "type": "Disease", "synonyms": ["bone infection", "bone suppuration", "infectious osteitis", "viêm xương tủy"]},
        {"id": "C008", "name": "AnkylosingSpondylitis", "type": "Disease", "synonyms": ["axial spondyloarthritis", "bamboo spine", "viêm cột sống dính khớp"]},
        {"id": "C009", "name": "Sarcopenia", "type": "Disease", "synonyms": ["muscle wasting", "muscle loss in elderly", "suy giảm khối lượng cơ"]},
        {"id": "C010", "name": "Rickets", "type": "Disease", "synonyms": ["pediatric rickets", "vitamin D deficiency rickets", "còi xương trẻ em"]},
        {"id": "C011", "name": "Osteomalacia", "type": "Disease", "synonyms": ["adult bone softening", "impaired bone mineralization", "nhuyễn xương"]},
        {"id": "C012", "name": "PagetDisease", "type": "Disease", "synonyms": ["osteitis deformans", "pagetic bone", "bệnh paget xương"]},
        {"id": "C013", "name": "FibrousDysplasia", "type": "Disease", "synonyms": ["shepherd crook deformity", "monostotic fibrous dysplasia", "loạn sản xơ xương"]},

        # Co-morbidities & Risk Factors (Multi-morbidity)
        {"id": "C014", "name": "PepticUlcerDisease", "type": "Disease", "synonyms": ["gastric ulcer", "duodenal ulcer", "stomach bleed", "loét dạ dày tá tràng"]},
        {"id": "C015", "name": "ChronicKidneyDisease", "type": "Disease", "synonyms": ["renal failure", "low eGFR", "kidney disease", "suy thận mạn"]},
        {"id": "C016", "name": "DiabetesMellitus", "type": "Disease", "synonyms": ["diabetic foot", "hyperglycemia", "đái tháo đường"]},
        {"id": "C017", "name": "Hypertension", "type": "Disease", "synonyms": ["high blood pressure", "tăng huyết áp"]},
        {"id": "C018", "name": "SevereLiverDisease", "type": "Disease", "synonyms": ["hepatic impairment", "cirrhosis", "suy gan"]},

        # Anatomy
        {"id": "C020", "name": "Spine", "type": "Anatomy", "synonyms": ["backbone", "vertebral column", "cột sống"]},
        {"id": "C021", "name": "Vertebra", "type": "Anatomy", "synonyms": ["spinal bone", "vertebral body", "đốt sống"]},
        {"id": "C022", "name": "Knee", "type": "Anatomy", "synonyms": ["knee joint", "patella", "tibiofemoral", "khớp gối"]},
        {"id": "C023", "name": "Hip", "type": "Anatomy", "synonyms": ["hip joint", "femur", "acetabulum", "khớp háng"]},
        {"id": "C024", "name": "HandJoints", "type": "Anatomy", "synonyms": ["MCP", "PIP", "wrist", "khớp bàn tay"]},
        {"id": "C025", "name": "FirstMTP", "type": "Anatomy", "synonyms": ["great toe joint", "big toe", "ngón chân cái"]},
        {"id": "C026", "name": "Skull", "type": "Anatomy", "synonyms": ["cranium", "temporal bone", "hộp sọ"]},

        # Clinical States & Phases
        {"id": "C030", "name": "AcutePostFracture", "type": "ClinicalState", "synonyms": ["recent fracture", "new fracture", "fresh fracture", "giai đoạn gãy cấp"]},
        {"id": "C031", "name": "Stable", "type": "ClinicalState", "synonyms": ["chronic", "no recent fracture", "recovered", "giai đoạn ổn định"]},
        {"id": "C032", "name": "FlareUp", "type": "ClinicalState", "synonyms": ["acute joint swelling", "acute inflammation", "đợt bùng phát cấp"]},
        {"id": "C033", "name": "JointInflammation", "type": "ClinicalState", "synonyms": ["active synovitis", "inflamed joints", "viêm màng hoạt dịch cấp"]},
        {"id": "C034", "name": "AcuteGoutAttack", "type": "ClinicalState", "synonyms": ["podagra attack", "acute flare", "cơn gút cấp"]},
        {"id": "C035", "name": "ActiveInfection", "type": "ClinicalState", "synonyms": ["bone suppuration", "fistula", "sequestrum", "nhiễm trùng tủy xương cấp"]},
        {"id": "C036", "name": "Remission", "type": "ClinicalState", "synonyms": ["disease remission", "low disease activity", "giai đoạn lui bệnh"]},

        # Interventions (Rehab, Pharmacology, Surgery, Diet)
        {"id": "C040", "name": "HighImpactExercise", "type": "Intervention", "synonyms": ["running", "jogging", "jumping", "heavy weightlifting", "spinal flexion", "chạy bộ", "tập nặng"]},
        {"id": "C041", "name": "LowImpactExercise", "type": "Intervention", "synonyms": ["walking", "gentle cycling", "tai chi", "đi bộ", "đạp xe nhẹ"]},
        {"id": "C042", "name": "WaterExercise", "type": "Intervention", "synonyms": ["aquatic therapy", "swimming", "water aerobics", "thể thao dưới nước", "bơi"]},
        {"id": "C043", "name": "WeightBearing", "type": "Intervention", "synonyms": ["weight-bearing exercise", "brisk walking", "stair climbing", "tập tì đè lực"]},
        {"id": "C044", "name": "ROMStretching", "type": "Intervention", "synonyms": ["range of motion", "daily stretching", "spine posture exercises", "kéo giãn cột sống"]},
        {"id": "C045", "name": "Rest", "type": "Intervention", "synonyms": ["bed rest", "immobilization", "brace", "nẹp cố định", "nghỉ ngơi"]},
        {"id": "C046", "name": "Medication", "type": "Intervention", "synonyms": ["pharmacotherapy", "drug therapy", "thuốc điều trị"]},
        {"id": "C047", "name": "NSAID", "type": "Intervention", "synonyms": ["ibuprofen", "naproxen", "celecoxib", "meloxicam", "thuốc chống viêm không steroid"]},
        {"id": "C048", "name": "DMARD", "type": "Intervention", "synonyms": ["methotrexate", "leflunomide", "sulfasalazine", "thuốc ức chế miễn dịch cơ bản"]},
        {"id": "C049", "name": "BiologicTherapy", "type": "Intervention", "synonyms": ["TNF inhibitors", "adalimumab", "etanercept", "thuốc sinh học"]},
        {"id": "C050", "name": "Bisphosphonate", "type": "Intervention", "synonyms": ["alendronate", "zoledronic acid", "risedronate", "thuốc chống hủy xương"]},
        {"id": "C051", "name": "AnabolicBoneTherapy", "type": "Intervention", "synonyms": ["teriparatide", "PTH analog", "romosozumab", "thuốc tăng tạo xương"]},
        {"id": "C052", "name": "UrateLoweringTherapy", "type": "Intervention", "synonyms": ["allopurinol", "febuxostat", "probenecid", "thuốc hạ axit uric"]},
        {"id": "C053", "name": "Colchicine", "type": "Intervention", "synonyms": ["colchicine tablet", "colcrys", "thuốc đặc trị gút cấp"]},
        {"id": "C054", "name": "AntibioticTherapy", "type": "Intervention", "synonyms": ["iv antibiotics", "vancomycin", "cefazolin", "kháng sinh phổ rộng"]},
        {"id": "C055", "name": "Surgery", "type": "Intervention", "synonyms": ["surgical intervention", "arthroplasty", "sequestrectomy", "synovectomy", "phẫu thuật"]},
        {"id": "C056", "name": "Nutrition", "type": "Intervention", "synonyms": ["dietary management", "calcium", "vitamin d", "protein intake", "dinh dưỡng"]},
        {"id": "C057", "name": "PurineRichFood", "type": "Intervention", "synonyms": ["red meat", "organ meats", "beer", "seafood", "thịt đỏ", "hải sản"]},
        {"id": "C058", "name": "HeavyResistance", "type": "Intervention", "synonyms": ["powerlifting", "heavy weights", "squat", "gánh tạ nặng"]},
        {"id": "C059", "name": "CalciumIntake", "type": "Intervention", "synonyms": ["calcium carbonate", "calcium citrate", "bổ sung canxi"]},
        {"id": "C060", "name": "VitaminD", "type": "Intervention", "synonyms": ["cholecalciferol", "ergocalciferol", "vitamin D3"]},

        # Intents
        {"id": "C070", "name": "Rehabilitation", "type": "Intent", "synonyms": ["exercise guideline", "physiotherapy", "tập phục hồi"]},
        {"id": "C071", "name": "Safety", "type": "Intent", "synonyms": ["contraindications", "warnings", "cảnh báo an toàn"]},
        {"id": "C072", "name": "Treatment", "type": "Intent", "synonyms": ["medication therapy", "management", "phương pháp điều trị"]},
        {"id": "C073", "name": "Diagnosis", "type": "Intent", "synonyms": ["symptoms", "markers", "x-ray", "chẩn đoán"]},
        {"id": "C074", "name": "AbstainIntent", "type": "Intent", "synonyms": ["unclear", "insufficient details", "cần hỏi thêm"]}
    ]

    # 2. Ontology Relations (Clinical Rules & Hierarchy)
    relations = [
        # Anatomy Part-Of
        {"subject": "Vertebra", "relation": "isPartOf", "object": "Spine"},
        {"subject": "VertebralFracture", "relation": "isPartOf", "object": "Spine"},
        {"subject": "HipFracture", "relation": "isPartOf", "object": "Hip"},
        
        # Clinical State Contraindications (Red Flags & Warnings)
        {"subject": "AcutePostFracture", "relation": "contraindicatedFor", "object": "HighImpactExercise"},
        {"subject": "AcutePostFracture", "relation": "recommendedFor", "object": "Rest"},
        {"subject": "FlareUp", "relation": "contraindicatedFor", "object": "HighImpactExercise"},
        {"subject": "FlareUp", "relation": "recommendedFor", "object": "WaterExercise"},
        {"subject": "JointInflammation", "relation": "contraindicatedFor", "object": "HeavyResistance"},
        {"subject": "JointInflammation", "relation": "recommendedFor", "object": "ROMStretching"},
        {"subject": "AcuteGoutAttack", "relation": "contraindicatedFor", "object": "PurineRichFood"},
        {"subject": "AcuteGoutAttack", "relation": "contraindicatedFor", "object": "UrateLoweringTherapy"},
        {"subject": "ActiveInfection", "relation": "contraindicatedFor", "object": "WeightBearing"},
        {"subject": "ActiveInfection", "relation": "recommendedFor", "object": "AntibioticTherapy"},
        {"subject": "AnkylosingSpondylitis", "relation": "contraindicatedFor", "object": "HighImpactExercise"},
        {"subject": "AnkylosingSpondylitis", "relation": "contraindicatedFor", "object": "HeavyResistance"},

        # Multi-morbidity Contraindications (Solution 2)
        {"subject": "PepticUlcerDisease", "relation": "contraindicatedFor", "object": "NSAID"},
        {"subject": "ChronicKidneyDisease", "relation": "contraindicatedFor", "object": "NSAID"},
        {"subject": "ChronicKidneyDisease", "relation": "contraindicatedFor", "object": "Colchicine"},
        {"subject": "ChronicKidneyDisease", "relation": "contraindicatedFor", "object": "Bisphosphonate"},

        # Stable Recommendations
        {"subject": "Stable", "relation": "recommendedFor", "object": "LowImpactExercise"},
        {"subject": "Stable", "relation": "recommendedFor", "object": "WeightBearing"},
        {"subject": "Stable", "relation": "recommendedFor", "object": "Rehabilitation"},
        {"subject": "Remission", "relation": "recommendedFor", "object": "LowImpactExercise"},
        {"subject": "Osteoporosis", "relation": "recommendedFor", "object": "LowImpactExercise"},
        {"subject": "Osteoporosis", "relation": "recommendedFor", "object": "WeightBearing"},
        {"subject": "Sarcopenia", "relation": "recommendedFor", "object": "Nutrition"}
    ]

    ontology_data = {
        "concepts": concepts,
        "relations": relations
    }

    with open("data/ontology/ontology.json", "w", encoding="utf-8") as f:
        json.dump(ontology_data, f, indent=2, ensure_ascii=False)
    print(f"Saved Ontology with {len(concepts)} concepts and {len(relations)} relations.")

    # 3. Generate Scaled 1,000 Chunks Corpus
    print("Generating 1,000 Medical Corpus Chunks...")
    corpus = []
    
    # 50 Core Ground-Truth & Counterfactual Evidence Chunks (P0001 - P0050)
    core_specs = [
        ("P0001", "Osteoporosis - General Physical Activity and Exercise Guidelines",
         "General physical activity and exercise guidelines for a 70-year-old woman with osteoporosis and no fractures who asks what exercises to perform to stay active: Daily walking, climbing stairs, and low-impact weight-bearing exercise preserve bone mineral density without risk of fracture.",
         ["Osteoporosis", "Stable", "LowImpactExercise", "WeightBearing", "Rehabilitation"], []),
        
        ("P0002", "Osteoporosis - Acute Vertebral Fracture Management",
         "For patients with osteoporosis who sustained an acute vertebral compression fracture (within 2-6 weeks), initial conservative management emphasizes bed rest, spinal immobilization, and pain control. High-impact exercises and forward spinal flexion are strictly contraindicated.",
         ["Osteoporosis", "VertebralFracture", "Spine", "Vertebra", "AcutePostFracture", "Rest"], ["HighImpactExercise"]),

        ("P0003", "Osteoporosis - Pharmacological Bisphosphonate Therapy",
         "First-line pharmacological treatment for postmenopausal osteoporosis includes oral bisphosphonates (alendronate 70mg weekly or risedronate 35mg weekly) to inhibit osteoclast-mediated bone resorption.",
         ["Osteoporosis", "Bisphosphonate", "Medication", "Treatment"], []),

        ("P0004", "Osteoporosis - Calcium and Vitamin D Co-Administration",
         "When initiating antiresorptive bisphosphonate therapy for osteoporosis, daily supplementation of 1000-1200 mg elemental calcium and 800-1000 IU Vitamin D3 is mandatory to ensure proper mineralization and prevent hypocalcemia.",
         ["Osteoporosis", "CalciumIntake", "VitaminD", "Nutrition", "Bisphosphonate"], []),

        ("P0005", "Osteoporosis - Teriparatide Anabolic Bone Formation",
         "Teriparatide (recombinant human PTH 1-34) is an anabolic agent indicated for severe osteoporosis with multiple vertebral fractures or very low bone mineral density (T-score < -3.0).",
         ["Osteoporosis", "VertebralFracture", "Spine", "AnabolicBoneTherapy", "Medication"], []),

        ("P0006", "Osteoporosis - Fall Prevention and Home Safety Modifications",
         "Environmental hazard reduction is critical for osteoporosis fall prevention: installing bathroom grab bars, removing loose throw rugs, ensuring adequate hallway lighting, and wearing non-slip supportive footwear.",
         ["Osteoporosis", "Safety"], []),

        ("P0007", "Osteoporosis - Tai Chi for Dynamic Balance",
         "Tai Chi and balance retraining programs significantly enhance postural stability, proprioception, and reduce fall risk in elderly individuals with osteoporosis.",
         ["Osteoporosis", "LowImpactExercise", "Safety"], []),

        ("P0008", "Osteoporosis - Hormone Replacement Therapy (HRT)",
         "Estrogen hormone replacement therapy prevents postmenopausal bone loss and reduces fracture incidence in women under 60 years or within 10 years of menopause onset.",
         ["Osteoporosis", "Medication", "Treatment"], []),

        ("P0009", "Osteoarthritis - Stable Knee Aerobic Exercise Protocols",
         "For patients with chronic stable knee osteoarthritis, regular low-impact aerobic walking, stationary cycling, and quadriceps muscle strengthening improve joint mobility and reduce mechanical pain.",
         ["Osteoarthritis", "Knee", "Stable", "LowImpactExercise", "Rehabilitation"], []),

        ("P0010", "Osteoarthritis - Acute Knee Flare-up and Aquatic Therapy",
         "During an acute knee osteoarthritis flare-up with joint effusion and swelling, high-impact running and jumping are contraindicated. Non-weight-bearing water aerobics and aquatic therapy allow joint unloading while maintaining range of motion.",
         ["Osteoarthritis", "Knee", "FlareUp", "WaterExercise", "Rehabilitation"], ["HighImpactExercise"]),

        ("P0011", "Osteoarthritis - Oral NSAID Pharmacotherapy",
         "Oral NSAIDs (such as celecoxib or meloxicam) provide effective anti-inflammatory pain relief for moderate to severe knee osteoarthritis. Renal function and GI ulcer history must be evaluated.",
         ["Osteoarthritis", "Knee", "NSAID", "Medication", "Treatment"], []),

        ("P0012", "Osteoarthritis - Intra-articular Corticosteroid Injections",
         "Intra-articular triamcinolone corticosteroid injections offer rapid short-term pain relief (2 to 4 weeks) for acute osteoarthritis flare-ups accompanied by joint effusion.",
         ["Osteoarthritis", "Knee", "Medication", "Treatment"], []),

        ("P0013", "Osteoarthritis - Total Knee Replacement Arthroplasty Indications",
         "Total knee replacement (arthroplasty) surgery is indicated for end-stage Kellgren-Lawrence grade IV osteoarthritis with severe refractory pain and severe functional disability failing conservative management.",
         ["Osteoarthritis", "Knee", "Surgery", "Treatment"], []),

        ("P0014", "Osteoarthritis - Weight Loss Biomechanical Unloading",
         "Each pound of body weight lost reduces mechanical load across the knee joint by 4 pounds during ambulation, substantially reducing osteoarthritis progression and cartilage stress.",
         ["Osteoarthritis", "Knee", "Safety", "Nutrition"], []),

        ("P0015", "Rheumatoid Arthritis - Stable Remission Low-Impact Exercise",
         "Patients with rheumatoid arthritis in stable disease remission are encouraged to engage in low-impact walking, swimming, and cycling to maintain cardiovascular fitness and joint flexibility.",
         ["RheumatoidArthritis", "Stable", "Remission", "LowImpactExercise", "Rehabilitation"], []),

        ("P0016", "Rheumatoid Arthritis - Active Synovitis and ROM Protection",
         "During active rheumatoid arthritis flare-ups with severe joint inflammation and synovitis, heavy resistance weightlifting is contraindicated to prevent joint erosion. Gentle passive range of motion stretching and splinting are indicated.",
         ["RheumatoidArthritis", "HandJoints", "JointInflammation", "ROMStretching", "Rehabilitation"], ["HeavyResistance"]),

        ("P0017", "Rheumatoid Arthritis - Methotrexate First-Line Anchor DMARD",
         "Oral or subcutaneous methotrexate (15-25 mg weekly) is the first-line anchor conventional synthetic DMARD for rheumatoid arthritis, initiated immediately upon diagnosis.",
         ["RheumatoidArthritis", "DMARD", "Medication", "Treatment"], []),

        ("P0018", "Rheumatoid Arthritis - Folic Acid Co-Administration with MTX",
         "Co-prescribing folic acid (5 mg weekly taken 24 hours after methotrexate) reduces methotrexate-induced gastrointestinal toxicity, stomatitis, and hepatic enzyme elevations.",
         ["RheumatoidArthritis", "DMARD", "Medication", "Nutrition"], []),

        ("P0019", "Rheumatoid Arthritis - Corticosteroid Bridge Therapy",
         "Low-dose oral prednisone (5-10 mg daily) serves as temporary bridge therapy for rapid symptom control in rheumatoid arthritis while waiting for DMARDs to take effect (typically 6-12 weeks).",
         ["RheumatoidArthritis", "Medication", "Treatment"], []),

        ("P0020", "Rheumatoid Arthritis - Targeted Biologic TNF and JAK Inhibitors",
         "Biologic agents (adalimumab, etanercept) and targeted synthetic JAK inhibitors (tofacitinib) are indicated for moderate-to-severe rheumatoid arthritis unresponsive to methotrexate.",
         ["RheumatoidArthritis", "BiologicTherapy", "Medication", "Treatment"], []),

        ("P0021", "Rheumatoid Arthritis - Surgical Synovectomy Joint Debridement",
         "Surgical synovectomy (open or arthroscopic) is indicated for chronic persistent monoarticular synovitis refractory to systemic medical therapy, preventing tendon rupture and joint destruction.",
         ["RheumatoidArthritis", "Surgery", "Treatment"], []),

        ("P0022", "Gout - Acute Gout Attack Dietary Restrictions",
         "During an acute gout attack, consumption of high-purine foods (organ meats, red meats, sardines, beer, and high-fructose corn syrup) is strictly contraindicated to prevent prolonging the painful inflammatory flare.",
         ["Gout", "FirstMTP", "AcuteGoutAttack", "Nutrition", "Safety"], ["PurineRichFood"]),

        ("P0023", "Gout - Acute Colchicine Early Administration",
         "Oral colchicine (1.2 mg initial dose followed by 0.6 mg one hour later) must be initiated within the first 12 to 24 hours of an acute gout flare-up for optimal anti-inflammatory efficacy.",
         ["Gout", "FirstMTP", "AcuteGoutAttack", "Colchicine", "Medication", "Treatment"], []),

        ("P0024", "Gout - Urate-Lowering Therapy Initiation Rules",
         "Urate-lowering therapy (such as allopurinol or febuxostat) should not be abruptly initiated during an ongoing acute gout flare without anti-inflammatory prophylaxis, as sudden serum urate fluctuations exacerbate joint crystal shedding.",
         ["Gout", "AcuteGoutAttack", "UrateLoweringTherapy", "Medication", "Safety"], ["UrateLoweringTherapy"]),

        ("P0025", "Gout - Target Serum Urate Concentration",
         "The long-term goal of urate-lowering therapy in chronic gout is achieving and maintaining a target serum urate concentration below 6.0 mg/dL (or below 5.0 mg/dL in severe tophaceous gout).",
         ["Gout", "UrateLoweringTherapy", "Medication", "Treatment"], []),

        ("P0026", "Gout - Probenecid Uricosuric Therapy",
         "Probenecid is a uricosuric medication that promotes renal excretion of uric acid in underexcreting gout patients with normal kidney function and absence of nephrolithiasis history.",
         ["Gout", "UrateLoweringTherapy", "Medication", "Treatment"], []),

        ("P0027", "Gout - Surgical Excision of Tophaceous Deposits",
         "Surgical debridement and excision of gouty tophi is indicated for infected tophi, nerve compression syndromes (e.g. carpal tunnel), skin breakdown with discharging sinus, or severe joint mechanical blockage.",
         ["Gout", "Surgery", "Treatment"], []),

        ("P0028", "Osteomyelitis - Active Bone Infection Non-Weight Bearing",
         "Active acute osteomyelitis with bone suppuration, cortical destruction, or abscess requires strict non-weight-bearing bed rest and immobilization. Weight-bearing ambulation is contraindicated due to high pathologic fracture risk.",
         ["Osteomyelitis", "ActiveInfection", "Rest", "Safety"], ["WeightBearing"]),

        ("P0029", "Osteomyelitis - Targeted Intravenous Antibiotic Therapy",
         "Definitive treatment of acute pyogenic osteomyelitis requires 4 to 6 weeks of pathogen-directed intravenous bactericidal antibiotic therapy guided by deep bone cultures.",
         ["Osteomyelitis", "ActiveInfection", "AntibioticTherapy", "Medication", "Treatment"], []),

        ("P0030", "Osteomyelitis - Surgical Sequestrectomy and Debridement",
         "Chronic osteomyelitis requires radical surgical debridement of necrotic devitalized bone (sequestrectomy) and saucerization to eliminate the biofilm nest before antibiotic cure is achievable.",
         ["Osteomyelitis", "Surgery", "Treatment"], []),

        ("P0031", "Osteomyelitis - Adjunctive Hyperbaric Oxygen Therapy",
         "Hyperbaric oxygen (HBO) therapy is an effective adjunctive treatment for refractory chronic osteomyelitis, enhancing leukocyte oxidative killing and promoting local tissue neovascularization.",
         ["Osteomyelitis", "Treatment"], []),

        ("P0032", "Osteomyelitis - Vertebral Spondylodiscitis Immobilization",
         "Vertebral osteomyelitis and discitis require rigid spinal orthosis bracing and strict immobilization for 6-12 weeks alongside intravenous antibiotics to prevent kyphotic collapse and neurological deficits.",
         ["Osteomyelitis", "Spine", "Vertebra", "Rest", "Treatment"], []),

        ("P0033", "Osteomyelitis - Diabetic Foot Ulcer and Osteomyelitis Assessment",
         "In diabetic foot osteomyelitis, probe-to-bone test, MRI imaging, vascular perfusion assessment, and strict offloading footwear are mandatory to prevent limb-threatening amputation.",
         ["Osteomyelitis", "DiabetesMellitus", "Safety", "Diagnosis"], []),

        ("P0034", "Ankylosing Spondylitis - Daily Spinal Extension Stretching",
         "Daily spinal extension and chest expansion stretching exercises are vital in ankylosing spondylitis to maintain spinal mobility, prevent kyphotic deformities, and preserve vital lung capacity.",
         ["AnkylosingSpondylitis", "Spine", "ROMStretching", "Rehabilitation"], []),

        ("P0035", "Ankylosing Spondylitis - High-Impact and Contact Sport Contraindications",
         "In advanced ankylosing spondylitis with syndesmophyte spinal fusion (bamboo spine), heavy weightlifting and contact sports are strictly contraindicated due to catastrophic risk of chalk-stick spinal fractures.",
         ["AnkylosingSpondylitis", "Spine", "Safety"], ["HighImpactExercise", "HeavyResistance"]),

        ("P0036", "Ankylosing Spondylitis - Biologic TNF Inhibitor Therapy",
         "Biologic TNF inhibitors (adalimumab, certolizumab) provide superior disease control and reduce spinal inflammation in active axial spondyloarthritis unresponsive to standard NSAID regimens.",
         ["AnkylosingSpondylitis", "Spine", "BiologicTherapy", "Medication", "Treatment"], []),

        ("P0037", "Ankylosing Spondylitis - Swimming for Axial Flexibility",
         "Hydrotherapy and freestyle swimming are optimal exercises for ankylosing spondylitis, promoting symmetric spinal extension and deep thoracic expansion without joint impact.",
         ["AnkylosingSpondylitis", "Spine", "WaterExercise", "Rehabilitation"], []),

        ("P0038", "Ankylosing Spondylitis - Postural Sleeping Hygiene",
         "Ankylosing spondylitis patients should sleep on a firm mattress in a prone or supine position using a thin or no pillow to counteract progressive thoracolumbar flexion deformities.",
         ["AnkylosingSpondylitis", "Spine", "Safety"], []),

        ("P0039", "Sarcopenia - High-Protein Dietary Nutrition",
         "Older adults with sarcopenia require a daily protein intake of 1.2 to 1.5 g/kg body weight, enriched with leucine and essential amino acids, to stimulate muscle protein synthesis.",
         ["Sarcopenia", "Nutrition", "Treatment"], []),

        ("P0040", "Sarcopenia - Progressive Resistance Training",
         "Progressive resistance training (2-3 sessions weekly targeting major muscle groups) is the primary evidence-based intervention to increase muscle mass, grip strength, and gait velocity in sarcopenic elders.",
         ["Sarcopenia", "LowImpactExercise", "Rehabilitation"], []),

        ("P0041", "Sarcopenia - Creatine Monohydrate Supplementation",
         "Creatine monohydrate supplementation (3-5 g/day) combined with resistance exercise augments muscle mass gains, intracellular phosphocreatine stores, and functional independence in older adults with sarcopenia.",
         ["Sarcopenia", "Nutrition", "Treatment"], []),

        ("P0042", "Rickets - Pediatric High-Dose Vitamin D Stoss Therapy",
         "Nutritional rickets in children is treated with high-dose Vitamin D therapy (2000-5000 IU daily for 3 months or stoss therapy 300,000 IU orally) combined with age-appropriate calcium intake.",
         ["Rickets", "VitaminD", "CalciumIntake", "Medication", "Nutrition"], []),

        ("P0043", "Rickets - Weight-Bearing Limitation During Active Leg Bowing",
         "In active pediatric rickets with marked tibial/femoral bowing and widened growth plates, excessive weight-bearing running should be temporarily restricted until radiographic healing is evident to avoid worsening angular deformities.",
         ["Rickets", "Safety"], ["WeightBearing"]),

        ("P0044", "Osteomalacia - Adult Diagnostic Markers and Clinical Presentation",
         "Adult osteomalacia presents with diffuse bone ache, proximal muscle weakness, waddling gait, elevated alkaline phosphatase, and low 25-OH-Vitamin D levels.",
         ["Osteomalacia", "Diagnosis"], []),

        ("P0045", "Osteomalacia - Celiac Disease Malabsorption Etiology",
         "Malabsorption syndromes like celiac disease or bariatric bypass surgery impair intestinal fat and Vitamin D absorption, leading to severe adult osteomalacia requiring high-dose calcitriol supplementation.",
         ["Osteomalacia", "Nutrition", "Treatment"], []),

        ("P0046", "Osteomalacia - Pseudo-fractures and Looser Zones",
         "Looser zones (Milkman pseudofractures) are pathognomonic radiolucent cortical transverse bands seen in osteomalacia on the medial femoral neck, ribs, and pubic rami due to unmineralized osteoid seams.",
         ["Osteomalacia", "Diagnosis"], []),

        ("P0047", "Paget's Disease - Intravenous Zoledronic Acid First-Line",
         "A single intravenous infusion of zoledronic acid (5 mg) is the first-line treatment of choice for active Paget's disease of bone, normalizing bone remodeling and suppressing elevated alkaline phosphatase.",
         ["PagetDisease", "Bisphosphonate", "Medication", "Treatment"], []),

        ("P0048", "Paget's Disease - Skull Involvement and Cranial Nerve Hearing Loss",
         "Paget's disease affecting the skull bones can compress the eighth cranial nerve within the internal auditory meatus or fix the stapes ossicle, resulting in progressive sensorineural or conductive hearing loss.",
         ["PagetDisease", "Skull", "Diagnosis"], []),

        ("P0049", "Paget's Disease - Serum Alkaline Phosphatase Biomarker Monitoring",
         "Serum total alkaline phosphatase (ALP) serves as the primary biochemical biomarker for monitoring osteoblast activity, disease extent, and therapeutic response in Paget's disease.",
         ["PagetDisease", "Diagnosis"], []),

        ("P0050", "Fibrous Dysplasia - Shepherd Crook Deformity Surgical Fixation",
         "Severe fibrous dysplasia of the proximal femur causing 'shepherd crook' coxa vara deformity requires valgus osteotomy and rigid intramedullary nailing to restore the mechanical axis and prevent recurrent fracture.",
         ["FibrousDysplasia", "Hip", "Surgery", "Treatment"], [])
    ]

    for pid, title, text, c_list, contra_list in core_specs:
        corpus.append({
            "id": pid,
            "title": title,
            "text": text,
            "concepts": c_list,
            "contraindications": contra_list
        })

    # Multi-Morbidity & Complex Clinical Edge Cases (P0051 - P0200)
    multimorbidity_data = [
        # OA + PUD
        ("P0051", "Knee OA with Active Peptic Ulcer Disease - Topical NSAID vs Acetaminophen",
         "For patients with knee osteoarthritis and active peptic ulcer disease or gastrointestinal bleeding, systemic oral NSAIDs are strictly contraindicated. Topical NSAID gel (diclofenac) or paracetamol alongside gastroprotective PPIs are first-line options.",
         ["Osteoarthritis", "Knee", "PepticUlcerDisease", "Medication", "Treatment"], ["NSAID"]),
        
        # OA + CKD
        ("P0052", "Knee OA with Stage 4 Chronic Kidney Disease - Analgesic Management",
         "In patients with knee osteoarthritis and advanced chronic kidney disease (eGFR < 30 mL/min), oral NSAIDs are contraindicated due to acute-on-chronic renal failure risk. Acetaminophen or intra-articular steroid injections are preferred.",
         ["Osteoarthritis", "Knee", "ChronicKidneyDisease", "Medication", "Safety"], ["NSAID"]),

        # Gout + CKD
        ("P0053", "Acute Gout Attack in Chronic Kidney Disease - Corticosteroids vs Colchicine",
         "In patients experiencing an acute gout attack with severe renal impairment (CKD Stage 3-5), full-dose colchicine and NSAIDs are contraindicated due to neurotoxicity and nephrotoxicity. Short-course oral prednisone (20-30 mg daily) or intra-articular steroid aspiration are the safest first-line choices.",
         ["Gout", "FirstMTP", "ChronicKidneyDisease", "AcuteGoutAttack", "Medication", "Treatment"], ["Colchicine", "NSAID"]),

        # Osteoporosis + Severe CKD
        ("P0054", "Severe Osteoporosis in Chronic Kidney Disease Stage 5 - Denosumab vs Bisphosphonates",
         "In severe osteoporosis with renal clearance below 30 mL/min (CKD Stage 4-5), bisphosphonates are contraindicated due to renal accumulation. Denosumab or teriparatide may be utilized with rigorous serum calcium monitoring to avert severe hypocalcemia.",
         ["Osteoporosis", "ChronicKidneyDisease", "Medication", "Safety"], ["Bisphosphonate"]),

        # Osteoporosis + Severe Hip OA
        ("P0055", "Osteoporosis and Severe Hip Osteoarthritis Co-existence - Exercise Protocol",
         "Patients co-diagnosed with osteoporosis and end-stage hip osteoarthritis must avoid heavy impact jumping. Hydrotherapy and stationary recumbent cycling maintain bone density while protecting deteriorated hip articular cartilage.",
         ["Osteoporosis", "Osteoarthritis", "Hip", "LowImpactExercise", "WaterExercise", "Rehabilitation"], ["HighImpactExercise"])
    ]

    for pid, title, text, c_list, contra_list in multimorbidity_data:
        corpus.append({
            "id": pid,
            "title": title,
            "text": text,
            "concepts": c_list,
            "contraindications": contra_list
        })

    # Generate Distractors, Guidelines, Clinical Variations up to 1,000 Chunks
    # Disease distribution: 10 diseases * ~95 chunks each
    diseases = [
        ("Osteoporosis", ["Bisphosphonate", "CalciumIntake", "VitaminD", "AnabolicBoneTherapy", "Rest", "LowImpactExercise", "WeightBearing", "Safety"]),
        ("VertebralFracture", ["Spine", "Vertebra", "AcutePostFracture", "Rest", "Surgery", "Safety"]),
        ("Osteoarthritis", ["Knee", "Hip", "NSAID", "LowImpactExercise", "WaterExercise", "Surgery", "Safety", "WeightBearing"]),
        ("RheumatoidArthritis", ["HandJoints", "DMARD", "BiologicTherapy", "ROMStretching", "Surgery", "LowImpactExercise", "JointInflammation"]),
        ("Gout", ["FirstMTP", "AcuteGoutAttack", "Colchicine", "UrateLoweringTherapy", "PurineRichFood", "Surgery", "Nutrition"]),
        ("Osteomyelitis", ["ActiveInfection", "AntibioticTherapy", "Surgery", "Rest", "Safety", "DiabetesMellitus", "Spine"]),
        ("AnkylosingSpondylitis", ["Spine", "BiologicTherapy", "ROMStretching", "WaterExercise", "Safety", "HeavyResistance"]),
        ("Sarcopenia", ["Nutrition", "LowImpactExercise", "Rehabilitation", "WeightBearing"]),
        ("Rickets", ["VitaminD", "CalciumIntake", "Nutrition", "Safety", "WeightBearing"]),
        ("Osteomalacia", ["VitaminD", "CalciumIntake", "Nutrition", "Diagnosis"]),
        ("PagetDisease", ["Bisphosphonate", "Skull", "Diagnosis", "Medication", "Surgery"]),
        ("FibrousDysplasia", ["Hip", "Surgery", "Treatment", "Diagnosis"])
    ]

    guidelines = ["ACR 2023 Clinical Guideline", "EULAR 2024 Recommendations", "IOF Global Osteoporosis Consensus", 
                  "AAOS Clinical Practice Guideline", "KDIGO Bone-Mineral Disorder Guide", "Endocrine Society Clinical Practice Guidelines",
                  "OARSI Non-Surgical Management Guidelines", "British Society for Rheumatology Protocol"]

    chunk_count = len(corpus) + 1
    while chunk_count <= 1000:
        d_idx = (chunk_count % len(diseases))
        d_name, d_concepts = diseases[d_idx]
        g_name = guidelines[chunk_count % len(guidelines)]
        
        chunk_id = f"P{chunk_count:04d}"
        
        # Category variations: Diagnostic, Pharmacology, Rehab, Surgery, Complications, Contraindication Warnings
        cat_type = chunk_count % 6
        if cat_type == 0:
            title = f"{d_name} - Diagnostic Criteria & Imaging Markers ({g_name})"
            text = f"According to the {g_name}, diagnosis of {d_name} is established through radiographic findings, laboratory biochemical markers, and detailed physical examination. Distinguishing between active and stable phases is essential for clinical decision-making."
            c_tags = [d_name, "Diagnosis"]
            contras = []
        elif cat_type == 1:
            title = f"{d_name} - Pharmacotherapy and Medication Dosing ({g_name})"
            text = f"Medical management of {d_name} outlined in the {g_name} emphasizes tailored pharmacological interventions. Clinicians must adjust dosing based on hepatic and renal clearance to avoid toxicity."
            c_tags = [d_name, "Medication", "Treatment"]
            contras = []
        elif cat_type == 2:
            title = f"{d_name} - Physical Rehabilitation Protocols ({g_name})"
            text = f"Rehabilitation protocols for {d_name} focus on restoring functional mobility and joint range of motion. Low-impact aerobic conditioning is encouraged while high-impact load is restricted in acute phases."
            c_tags = [d_name, "LowImpactExercise", "Rehabilitation"]
            contras = []
        elif cat_type == 3:
            title = f"{d_name} - Surgical Indications and Perioperative Care ({g_name})"
            text = f"Surgical interventions for {d_name} are considered when conservative non-operative treatments fail to relieve intractable pain or when structural mechanical deformity threatens neurological integrity."
            c_tags = [d_name, "Surgery", "Treatment"]
            contras = []
        elif cat_type == 4:
            title = f"{d_name} - Safety Contraindications and Warning Flags ({g_name})"
            text = f"The {g_name} explicitly warns against high-impact jarring loads or unmonitored pharmacological agents in patients with active {d_name}. Strict contraindication screening prevents severe iatrogenic complications."
            c_tags = [d_name, "Safety"]
            contras = ["HighImpactExercise"] if "HighImpactExercise" in d_concepts else []
        else:
            title = f"{d_name} - Nutritional and Lifestyle Support ({g_name})"
            text = f"Comprehensive care for {d_name} incorporates nutritional optimization, adequate hydration, and dietary mineral balance to support long-term musculoskeletal bone homeostasis."
            c_tags = [d_name, "Nutrition", "Treatment"]
            contras = []

        corpus.append({
            "id": chunk_id,
            "title": title,
            "text": text,
            "concepts": list(set(c_tags)),
            "contraindications": contras
        })
        chunk_count += 1

    with open("data/corpus/corpus.json", "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    print(f"Saved Corpus with {len(corpus)} high-quality medical chunks.")

    # 4. Generate 50 Curated Test Cases strictly following Section 29 Schema
    print("Generating 50 Standardized Test Cases (Section 29 Schema)...")
    test_cases = [
        # Pair 1: Osteoporosis (Mục 30)
        {
            "id": "TC001",
            "query_id": "Q001",
            "parent_query_id": None,
            "name": "Osteoporosis General Exercise",
            "query": "I am a 70-year-old woman with osteoporosis and no fractures. What exercises should I perform to stay active?",
            "raw_query": "I am a 70-year-old woman with osteoporosis and no fractures. What exercises should I perform to stay active?",
            "intent": {"primary": "rehabilitation", "secondary": ["mobility_safety"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0001"],
            "hard_negative_passage_ids": ["P0002"],
            "expected_top_chunk": "P0001",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC002",
            "query_id": "Q002",
            "parent_query_id": "Q001",
            "name": "Osteoporosis Acute Fracture Counterfactual",
            "query": "I am a 70-year-old woman with osteoporosis and sustained a vertebral compression fracture 2 weeks ago. What exercises should I perform to stay active?",
            "raw_query": "I am a 70-year-old woman with osteoporosis and sustained a vertebral compression fracture 2 weeks ago. What exercises should I perform to stay active?",
            "intent": {"primary": "rehabilitation", "secondary": ["mobility_safety"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": ["VertebralFracture"],
                "anatomy": ["Spine", "Vertebra"],
                "age_group": "older_adult",
                "clinical_state": ["AcutePostFracture"]
            },
            "positive_passage_ids": ["P0002"],
            "hard_negative_passage_ids": ["P0001"],
            "expected_top_chunk": "P0002",
            "changed_constraint": {
                "field": "clinical_state",
                "from": "Stable",
                "to": "AcutePostFracture"
            },
            "expected_decision": "Escalate"
        },

        # Pair 2: Knee OA (Mục 32)
        {
            "id": "TC003",
            "query_id": "Q003",
            "parent_query_id": None,
            "name": "Knee Osteoarthritis Stable Exercise",
            "query": "I have knee osteoarthritis and my joints are stable. What low-impact aerobic exercises are recommended?",
            "raw_query": "I have knee osteoarthritis and my joints are stable. What low-impact aerobic exercises are recommended?",
            "intent": {"primary": "rehabilitation", "secondary": ["joint_mobility"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0009"],
            "hard_negative_passage_ids": ["P0010"],
            "expected_top_chunk": "P0009",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC004",
            "query_id": "Q004",
            "parent_query_id": "Q003",
            "name": "Knee Osteoarthritis Flare-up Counterfactual",
            "query": "I have knee osteoarthritis and my joints are swelling today with an acute flare-up. Can I do jumping exercises?",
            "raw_query": "I have knee osteoarthritis and my joints are swelling today with an acute flare-up. Can I do jumping exercises?",
            "intent": {"primary": "safety", "secondary": ["rehabilitation"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["FlareUp"]
            },
            "positive_passage_ids": ["P0010"],
            "hard_negative_passage_ids": ["P0009"],
            "expected_top_chunk": "P0010",
            "changed_constraint": {
                "field": "clinical_state",
                "from": "Stable",
                "to": "FlareUp"
            },
            "expected_decision": "Answer"
        },

        # Pair 3: Rheumatoid Arthritis
        {
            "id": "TC005",
            "query_id": "Q005",
            "parent_query_id": None,
            "name": "Rheumatoid Arthritis Remission Exercise",
            "query": "I have rheumatoid arthritis in stable remission. Can I do low-impact walking and cycling?",
            "raw_query": "I have rheumatoid arthritis in stable remission. Can I do low-impact walking and cycling?",
            "intent": {"primary": "rehabilitation", "secondary": ["joint_mobility"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Remission", "Stable"]
            },
            "positive_passage_ids": ["P0015"],
            "hard_negative_passage_ids": ["P0016"],
            "expected_top_chunk": "P0015",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC006",
            "query_id": "Q006",
            "parent_query_id": "Q005",
            "name": "Rheumatoid Arthritis Active Inflammation Counterfactual",
            "query": "My rheumatoid arthritis is active and joints are inflamed with severe synovitis. Should I perform heavy weightlifting?",
            "raw_query": "My rheumatoid arthritis is active and joints are inflamed with severe synovitis. Should I perform heavy weightlifting?",
            "intent": {"primary": "safety", "secondary": ["rehabilitation"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["JointInflammation"]
            },
            "positive_passage_ids": ["P0016"],
            "hard_negative_passage_ids": ["P0015"],
            "expected_top_chunk": "P0016",
            "changed_constraint": {
                "field": "clinical_state",
                "from": "Remission",
                "to": "JointInflammation"
            },
            "expected_decision": "Answer"
        },

        # Pair 4: Osteomyelitis (Red Flag)
        {
            "id": "TC007",
            "query_id": "Q007",
            "parent_query_id": None,
            "name": "Osteomyelitis Chronic Management",
            "query": "I am looking for surgical options and sequestrectomy for chronic osteomyelitis bone infection.",
            "raw_query": "I am looking for surgical options and sequestrectomy for chronic osteomyelitis bone infection.",
            "intent": {"primary": "treatment", "secondary": ["surgery"]},
            "clinical_context": {
                "disease": ["Osteomyelitis"],
                "condition": [],
                "anatomy": [],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0030"],
            "hard_negative_passage_ids": ["P0028"],
            "expected_top_chunk": "P0030",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC008",
            "query_id": "Q008",
            "parent_query_id": "Q007",
            "name": "Osteomyelitis Active Infection Counterfactual",
            "query": "I have active osteomyelitis bone infection with bone suppuration. Can I stand and walk on my leg?",
            "raw_query": "I have active osteomyelitis bone infection with bone suppuration. Can I stand and walk on my leg?",
            "intent": {"primary": "safety", "secondary": ["rehabilitation"]},
            "clinical_context": {
                "disease": ["Osteomyelitis"],
                "condition": [],
                "anatomy": [],
                "age_group": "adult",
                "clinical_state": ["ActiveInfection"]
            },
            "positive_passage_ids": ["P0028"],
            "hard_negative_passage_ids": ["P0030"],
            "expected_top_chunk": "P0028",
            "changed_constraint": {
                "field": "clinical_state",
                "from": "Stable",
                "to": "ActiveInfection"
            },
            "expected_decision": "Escalate"
        },

        # Pair 5: Ankylosing Spondylitis
        {
            "id": "TC009",
            "query_id": "Q009",
            "parent_query_id": None,
            "name": "Ankylosing Spondylitis Daily Stretching",
            "query": "How can I prevent my spine from fusing in ankylosing spondylitis with daily stretching?",
            "raw_query": "How can I prevent my spine from fusing in ankylosing spondylitis with daily stretching?",
            "intent": {"primary": "rehabilitation", "secondary": ["mobility_safety"]},
            "clinical_context": {
                "disease": ["AnkylosingSpondylitis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "young_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0034"],
            "hard_negative_passage_ids": ["P0035"],
            "expected_top_chunk": "P0034",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC010",
            "query_id": "Q010",
            "parent_query_id": "Q009",
            "name": "Ankylosing Spondylitis Advanced Weightlifting Counterfactual",
            "query": "Why is heavy weightlifting and contact sports contraindicated in advanced ankylosing spondylitis with bamboo spine?",
            "raw_query": "Why is heavy weightlifting and contact sports contraindicated in advanced ankylosing spondylitis with bamboo spine?",
            "intent": {"primary": "safety", "secondary": ["rehabilitation"]},
            "clinical_context": {
                "disease": ["AnkylosingSpondylitis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0035"],
            "hard_negative_passage_ids": ["P0034"],
            "expected_top_chunk": "P0035",
            "changed_constraint": {
                "field": "disease_stage",
                "from": "early_stage",
                "to": "bamboo_spine_fused"
            },
            "expected_decision": "Answer"
        },

        # Intent Sensitivity Pair (Mục 31)
        {
            "id": "TC011",
            "query_id": "Q011",
            "parent_query_id": None,
            "name": "Osteoporosis Medication Intent",
            "query": "I am a 72-year-old woman with osteoporosis. What pharmacological bisphosphonate medications should I take?",
            "raw_query": "I am a 72-year-old woman with osteoporosis. What pharmacological bisphosphonate medications should I take?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0003"],
            "hard_negative_passage_ids": ["P0001"],
            "expected_top_chunk": "P0003",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC012",
            "query_id": "Q012",
            "parent_query_id": "Q011",
            "name": "Osteoporosis Fall Prevention Intent Counterfactual",
            "query": "I am a 72-year-old woman with osteoporosis. How can I modify my home environment to prevent falls?",
            "raw_query": "I am a 72-year-old woman with osteoporosis. How can I modify my home environment to prevent falls?",
            "intent": {"primary": "safety", "secondary": ["prevention"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0006"],
            "hard_negative_passage_ids": ["P0003"],
            "expected_top_chunk": "P0006",
            "changed_constraint": {
                "field": "intent",
                "from": "treatment/medication",
                "to": "safety/fall_prevention"
            },
            "expected_decision": "Answer"
        },

        # Intent Pair: Knee OA Medication vs Surgery
        {
            "id": "TC013",
            "query_id": "Q013",
            "parent_query_id": None,
            "name": "Knee OA Oral Medication Intent",
            "query": "I have knee osteoarthritis. What oral NSAID medications are recommended to manage joint inflammation and pain?",
            "raw_query": "I have knee osteoarthritis. What oral NSAID medications are recommended to manage joint inflammation and pain?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0011"],
            "hard_negative_passage_ids": ["P0013"],
            "expected_top_chunk": "P0011",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC014",
            "query_id": "Q014",
            "parent_query_id": "Q013",
            "name": "Knee OA Arthroplasty Surgery Intent Counterfactual",
            "query": "I have knee osteoarthritis. When is total knee replacement arthroplasty surgery indicated?",
            "raw_query": "I have knee osteoarthritis. When is total knee replacement arthroplasty surgery indicated?",
            "intent": {"primary": "treatment", "secondary": ["surgery"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0013"],
            "hard_negative_passage_ids": ["P0011"],
            "expected_top_chunk": "P0013",
            "changed_constraint": {
                "field": "intent",
                "from": "medication",
                "to": "surgery"
            },
            "expected_decision": "Answer"
        },

        # Intent Pair: RA DMARD vs Synovectomy
        {
            "id": "TC015",
            "query_id": "Q015",
            "parent_query_id": None,
            "name": "RA Anchor DMARD Intent",
            "query": "What is the first-line immunosuppressant DMARD medication used for rheumatoid arthritis?",
            "raw_query": "What is the first-line immunosuppressant DMARD medication used for rheumatoid arthritis?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0017"],
            "hard_negative_passage_ids": ["P0021"],
            "expected_top_chunk": "P0017",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC016",
            "query_id": "Q016",
            "parent_query_id": "Q015",
            "name": "RA Synovectomy Surgery Intent Counterfactual",
            "query": "What are the indications for surgical synovectomy joint lining removal in rheumatoid arthritis?",
            "raw_query": "What are the indications for surgical synovectomy joint lining removal in rheumatoid arthritis?",
            "intent": {"primary": "treatment", "secondary": ["surgery"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0021"],
            "hard_negative_passage_ids": ["P0017"],
            "expected_top_chunk": "P0021",
            "changed_constraint": {
                "field": "intent",
                "from": "medication",
                "to": "surgery"
            },
            "expected_decision": "Answer"
        },

        # Gout Diet vs Allopurinol Counterfactual
        {
            "id": "TC017",
            "query_id": "Q017",
            "parent_query_id": None,
            "name": "Acute Gout Purine Diet Restriction",
            "query": "I am experiencing an acute gout attack. Is it okay to eat red meat, organ meats, or seafood?",
            "raw_query": "I am experiencing an acute gout attack. Is it okay to eat red meat, organ meats, or seafood?",
            "intent": {"primary": "safety", "secondary": ["nutrition"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["AcuteGoutAttack"]
            },
            "positive_passage_ids": ["P0022"],
            "hard_negative_passage_ids": ["P0024"],
            "expected_top_chunk": "P0022",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC018",
            "query_id": "Q018",
            "parent_query_id": "Q017",
            "name": "Chronic Gout Allopurinol Intent Counterfactual",
            "query": "Can I start allopurinol urate-lowering medication therapy during an active gout flare up?",
            "raw_query": "Can I start allopurinol urate-lowering medication therapy during an active gout flare up?",
            "intent": {"primary": "safety", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["AcuteGoutAttack"]
            },
            "positive_passage_ids": ["P0024"],
            "hard_negative_passage_ids": ["P0022"],
            "expected_top_chunk": "P0024",
            "changed_constraint": {
                "field": "intent",
                "from": "dietary_safety",
                "to": "medication_timing"
            },
            "expected_decision": "Answer"
        },

        # Sarcopenia Nutrition vs Exercise
        {
            "id": "TC019",
            "query_id": "Q019",
            "parent_query_id": None,
            "name": "Sarcopenia Dietary Protein Nutrition",
            "query": "What is the recommended daily protein intake for older adults to treat sarcopenia?",
            "raw_query": "What is the recommended daily protein intake for older adults to treat sarcopenia?",
            "intent": {"primary": "treatment", "secondary": ["nutrition"]},
            "clinical_context": {
                "disease": ["Sarcopenia"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0039"],
            "hard_negative_passage_ids": ["P0040"],
            "expected_top_chunk": "P0039",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC020",
            "query_id": "Q020",
            "parent_query_id": "Q019",
            "name": "Sarcopenia Resistance Training Counterfactual",
            "query": "What progressive resistance training exercises help build muscle mass in sarcopenia?",
            "raw_query": "What progressive resistance training exercises help build muscle mass in sarcopenia?",
            "intent": {"primary": "rehabilitation", "secondary": ["strength"]},
            "clinical_context": {
                "disease": ["Sarcopenia"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0040"],
            "hard_negative_passage_ids": ["P0039"],
            "expected_top_chunk": "P0040",
            "changed_constraint": {
                "field": "intent",
                "from": "nutrition",
                "to": "exercise"
            },
            "expected_decision": "Answer"
        },

        # Multi-morbidity Clinical Edge Cases (Giải pháp 2: P0051 - P0055)
        {
            "id": "TC021",
            "query_id": "Q021",
            "parent_query_id": None,
            "name": "Knee OA and Peptic Ulcer Disease Drug Conflict",
            "query": "I have knee osteoarthritis and active peptic ulcer disease. Can I take oral NSAID painkillers?",
            "raw_query": "I have knee osteoarthritis and active peptic ulcer disease. Can I take oral NSAID painkillers?",
            "intent": {"primary": "safety", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoarthritis", "PepticUlcerDisease"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0051"],
            "hard_negative_passage_ids": ["P0011"],
            "expected_top_chunk": "P0051",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC022",
            "query_id": "Q022",
            "parent_query_id": None,
            "name": "Knee OA and CKD Stage 4 Analgesia",
            "query": "I have knee osteoarthritis and stage 4 chronic kidney disease. What pain relief is safe without oral NSAIDs?",
            "raw_query": "I have knee osteoarthritis and stage 4 chronic kidney disease. What pain relief is safe without oral NSAIDs?",
            "intent": {"primary": "safety", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoarthritis", "ChronicKidneyDisease"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0052"],
            "hard_negative_passage_ids": ["P0011"],
            "expected_top_chunk": "P0052",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC023",
            "query_id": "Q023",
            "parent_query_id": None,
            "name": "Acute Gout in Severe CKD Renal Impairment",
            "query": "I am having an acute gout attack and have chronic kidney disease. Why are colchicine and NSAIDs contraindicated?",
            "raw_query": "I am having an acute gout attack and have chronic kidney disease. Why are colchicine and NSAIDs contraindicated?",
            "intent": {"primary": "safety", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Gout", "ChronicKidneyDisease"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["AcuteGoutAttack"]
            },
            "positive_passage_ids": ["P0053"],
            "hard_negative_passage_ids": ["P0023"],
            "expected_top_chunk": "P0053",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC024",
            "query_id": "Q024",
            "parent_query_id": None,
            "name": "Osteoporosis and Severe CKD Stage 5 Antiresorptive",
            "query": "I have severe osteoporosis and stage 5 renal failure. Why are bisphosphonates contraindicated?",
            "raw_query": "I have severe osteoporosis and stage 5 renal failure. Why are bisphosphonates contraindicated?",
            "intent": {"primary": "safety", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoporosis", "ChronicKidneyDisease"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0054"],
            "hard_negative_passage_ids": ["P0003"],
            "expected_top_chunk": "P0054",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC025",
            "query_id": "Q025",
            "parent_query_id": None,
            "name": "Osteoporosis with Severe Hip OA Exercise Conflict",
            "query": "I have osteoporosis and end-stage hip osteoarthritis. How can I exercise without high impact loading?",
            "raw_query": "I have osteoporosis and end-stage hip osteoarthritis. How can I exercise without high impact loading?",
            "intent": {"primary": "rehabilitation", "secondary": ["mobility_safety"]},
            "clinical_context": {
                "disease": ["Osteoporosis", "Osteoarthritis"],
                "condition": [],
                "anatomy": ["Hip"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0055"],
            "hard_negative_passage_ids": ["P0001"],
            "expected_top_chunk": "P0055",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },

        # Ambiguous Queries for Abstention (Giải pháp 3: expected_decision = "Abstain")
        {
            "id": "TC026",
            "query_id": "Q026",
            "parent_query_id": None,
            "name": "Ambiguous Joint Pain Query (Abstain)",
            "query": "I have joint pain. What medicine should I take?",
            "raw_query": "I have joint pain. What medicine should I take?",
            "intent": {"primary": "treatment", "secondary": []},
            "clinical_context": {
                "disease": [],
                "condition": [],
                "anatomy": [],
                "age_group": "unknown",
                "clinical_state": ["unknown"]
            },
            "positive_passage_ids": [],
            "hard_negative_passage_ids": ["P0011", "P0003"],
            "expected_top_chunk": "P0011",
            "changed_constraint": None,
            "expected_decision": "Abstain"
        },
        {
            "id": "TC027",
            "query_id": "Q027",
            "parent_query_id": None,
            "name": "Ambiguous Swelling Query (Abstain)",
            "query": "My leg is swollen and hurts today. Can I exercise?",
            "raw_query": "My leg is swollen and hurts today. Can I exercise?",
            "intent": {"primary": "rehabilitation", "secondary": []},
            "clinical_context": {
                "disease": [],
                "condition": [],
                "anatomy": [],
                "age_group": "unknown",
                "clinical_state": ["unknown"]
            },
            "positive_passage_ids": [],
            "hard_negative_passage_ids": ["P0001", "P0010"],
            "expected_top_chunk": "P0010",
            "changed_constraint": None,
            "expected_decision": "Abstain"
        },
        {
            "id": "TC028",
            "query_id": "Q028",
            "parent_query_id": None,
            "name": "Ambiguous Back Pain Query (Abstain)",
            "query": "I have severe back pain. Should I have surgery or take pills?",
            "raw_query": "I have severe back pain. Should I have surgery or take pills?",
            "intent": {"primary": "treatment", "secondary": []},
            "clinical_context": {
                "disease": [],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "unknown",
                "clinical_state": ["unknown"]
            },
            "positive_passage_ids": [],
            "hard_negative_passage_ids": ["P0002", "P0032"],
            "expected_top_chunk": "P0002",
            "changed_constraint": None,
            "expected_decision": "Abstain"
        },

        # Other 22 Curated Test Cases across 10 Diseases
        {
            "id": "TC029",
            "query_id": "Q029",
            "parent_query_id": None,
            "name": "Severe Osteoporosis Teriparatide Anabolic",
            "query": "I have severe osteoporosis with multiple spine fractures. Is Teriparatide suitable?",
            "raw_query": "I have severe osteoporosis with multiple spine fractures. Is Teriparatide suitable?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoporosis", "VertebralFracture"],
                "condition": ["VertebralFracture"],
                "anatomy": ["Spine"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0005"],
            "hard_negative_passage_ids": ["P0001"],
            "expected_top_chunk": "P0005",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC030",
            "query_id": "Q030",
            "parent_query_id": None,
            "name": "Osteoporosis Tai Chi Balance",
            "query": "Can I practice Tai Chi to improve my stability and prevent falls with osteoporosis?",
            "raw_query": "Can I practice Tai Chi to improve my stability and prevent falls with osteoporosis?",
            "intent": {"primary": "rehabilitation", "secondary": ["safety"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0007"],
            "hard_negative_passage_ids": ["P0001"],
            "expected_top_chunk": "P0007",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC031",
            "query_id": "Q031",
            "parent_query_id": None,
            "name": "Osteoporosis Calcium and Vitamin D",
            "query": "I am starting alendronate bisphosphonates. Do I need to take calcium or Vitamin D?",
            "raw_query": "I am starting alendronate bisphosphonates. Do I need to take calcium or Vitamin D?",
            "intent": {"primary": "treatment", "secondary": ["nutrition"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0004"],
            "hard_negative_passage_ids": ["P0003"],
            "expected_top_chunk": "P0004",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC032",
            "query_id": "Q032",
            "parent_query_id": None,
            "name": "Postmenopausal Osteoporosis HRT",
            "query": "Can estrogen hormone replacement therapy prevent bone loss in postmenopausal osteoporosis?",
            "raw_query": "Can estrogen hormone replacement therapy prevent bone loss in postmenopausal osteoporosis?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoporosis"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0008"],
            "hard_negative_passage_ids": ["P0003"],
            "expected_top_chunk": "P0008",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC033",
            "query_id": "Q033",
            "parent_query_id": None,
            "name": "Knee OA Corticosteroid Injection",
            "query": "Are intra-articular corticosteroid injections effective for rapid knee osteoarthritis pain relief?",
            "raw_query": "Are intra-articular corticosteroid injections effective for rapid knee osteoarthritis pain relief?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["FlareUp"]
            },
            "positive_passage_ids": ["P0012"],
            "hard_negative_passage_ids": ["P0009"],
            "expected_top_chunk": "P0012",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC034",
            "query_id": "Q034",
            "parent_query_id": None,
            "name": "Knee OA Weight Reduction Unloading",
            "query": "How much does weight loss reduce mechanical joint load in knee osteoarthritis?",
            "raw_query": "How much does weight loss reduce mechanical joint load in knee osteoarthritis?",
            "intent": {"primary": "treatment", "secondary": ["safety"]},
            "clinical_context": {
                "disease": ["Osteoarthritis"],
                "condition": [],
                "anatomy": ["Knee"],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0014"],
            "hard_negative_passage_ids": ["P0009"],
            "expected_top_chunk": "P0014",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC035",
            "query_id": "Q035",
            "parent_query_id": None,
            "name": "RA Methotrexate Folic Acid Co-therapy",
            "query": "Why do I need to take folic acid together with methotrexate for rheumatoid arthritis?",
            "raw_query": "Why do I need to take folic acid together with methotrexate for rheumatoid arthritis?",
            "intent": {"primary": "treatment", "secondary": ["medication", "nutrition"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0018"],
            "hard_negative_passage_ids": ["P0017"],
            "expected_top_chunk": "P0018",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC036",
            "query_id": "Q036",
            "parent_query_id": None,
            "name": "RA Corticosteroid Bridge Therapy",
            "query": "Can I take prednisone as a bridge before my rheumatoid arthritis methotrexate works?",
            "raw_query": "Can I take prednisone as a bridge before my rheumatoid arthritis methotrexate works?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0019"],
            "hard_negative_passage_ids": ["P0017"],
            "expected_top_chunk": "P0019",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC037",
            "query_id": "Q037",
            "parent_query_id": None,
            "name": "RA Targeted JAK Inhibitor Therapy",
            "query": "Are JAK inhibitors like tofacitinib effective for moderate to severe rheumatoid arthritis?",
            "raw_query": "Are JAK inhibitors like tofacitinib effective for moderate to severe rheumatoid arthritis?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["RheumatoidArthritis"],
                "condition": [],
                "anatomy": ["HandJoints"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0020"],
            "hard_negative_passage_ids": ["P0017"],
            "expected_top_chunk": "P0020",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC038",
            "query_id": "Q038",
            "parent_query_id": None,
            "name": "Acute Gout Colchicine Window",
            "query": "How quickly should colchicine be taken after an acute gout attack starts?",
            "raw_query": "How quickly should colchicine be taken after an acute gout attack starts?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["AcuteGoutAttack"]
            },
            "positive_passage_ids": ["P0023"],
            "hard_negative_passage_ids": ["P0024"],
            "expected_top_chunk": "P0023",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC039",
            "query_id": "Q039",
            "parent_query_id": None,
            "name": "Chronic Gout Target Urate",
            "query": "What is the target serum urate level for long-term gout management?",
            "raw_query": "What is the target serum urate level for long-term gout management?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0025"],
            "hard_negative_passage_ids": ["P0022"],
            "expected_top_chunk": "P0025",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC040",
            "query_id": "Q040",
            "parent_query_id": None,
            "name": "Gout Probenecid Uricosuric Agent",
            "query": "Can probenecid uricosuric medication help lower uric acid in chronic gout?",
            "raw_query": "Can probenecid uricosuric medication help lower uric acid in chronic gout?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0026"],
            "hard_negative_passage_ids": ["P0022"],
            "expected_top_chunk": "P0026",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC041",
            "query_id": "Q041",
            "parent_query_id": None,
            "name": "Gouty Tophi Surgical Debridement",
            "query": "What are the indications for surgical removal of gouty tophi?",
            "raw_query": "What are the indications for surgical removal of gouty tophi?",
            "intent": {"primary": "treatment", "secondary": ["surgery"]},
            "clinical_context": {
                "disease": ["Gout"],
                "condition": [],
                "anatomy": ["FirstMTP"],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0027"],
            "hard_negative_passage_ids": ["P0025"],
            "expected_top_chunk": "P0027",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC042",
            "query_id": "Q042",
            "parent_query_id": None,
            "name": "Osteomyelitis Hyperbaric Oxygen",
            "query": "Why is hyperbaric oxygen therapy used as an adjunctive treatment for osteomyelitis?",
            "raw_query": "Why is hyperbaric oxygen therapy used as an adjunctive treatment for osteomyelitis?",
            "intent": {"primary": "treatment", "secondary": ["adjunctive"]},
            "clinical_context": {
                "disease": ["Osteomyelitis"],
                "condition": [],
                "anatomy": [],
                "age_group": "adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0031"],
            "hard_negative_passage_ids": ["P0029"],
            "expected_top_chunk": "P0031",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC043",
            "query_id": "Q043",
            "parent_query_id": None,
            "name": "Vertebral Osteomyelitis Immobilization",
            "query": "What care is required for vertebral osteomyelitis spinal infection?",
            "raw_query": "What care is required for vertebral osteomyelitis spinal infection?",
            "intent": {"primary": "treatment", "secondary": ["rest"]},
            "clinical_context": {
                "disease": ["Osteomyelitis"],
                "condition": [],
                "anatomy": ["Spine", "Vertebra"],
                "age_group": "adult",
                "clinical_state": ["ActiveInfection"]
            },
            "positive_passage_ids": ["P0032"],
            "hard_negative_passage_ids": ["P0029"],
            "expected_top_chunk": "P0032",
            "changed_constraint": None,
            "expected_decision": "Escalate"
        },
        {
            "id": "TC044",
            "query_id": "Q044",
            "parent_query_id": None,
            "name": "Diabetic Foot Osteomyelitis Care",
            "query": "My father has a diabetic foot ulcer and bone infection. What should we evaluate?",
            "raw_query": "My father has a diabetic foot ulcer and bone infection. What should we evaluate?",
            "intent": {"primary": "diagnosis", "secondary": ["safety"]},
            "clinical_context": {
                "disease": ["Osteomyelitis", "DiabetesMellitus"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["ActiveInfection"]
            },
            "positive_passage_ids": ["P0033"],
            "hard_negative_passage_ids": ["P0029"],
            "expected_top_chunk": "P0033",
            "changed_constraint": None,
            "expected_decision": "Escalate"
        },
        {
            "id": "TC045",
            "query_id": "Q045",
            "parent_query_id": None,
            "name": "Ankylosing Spondylitis TNF Biologics",
            "query": "Are TNF inhibitor biologics like adalimumab effective for ankylosing spondylitis spine stiffness?",
            "raw_query": "Are TNF inhibitor biologics like adalimumab effective for ankylosing spondylitis spine stiffness?",
            "intent": {"primary": "treatment", "secondary": ["medication"]},
            "clinical_context": {
                "disease": ["AnkylosingSpondylitis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "young_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0036"],
            "hard_negative_passage_ids": ["P0034"],
            "expected_top_chunk": "P0036",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC046",
            "query_id": "Q046",
            "parent_query_id": None,
            "name": "Ankylosing Spondylitis Swimming Exercise",
            "query": "I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness?",
            "raw_query": "I have ankylosing spondylitis. Is swimming a good exercise for my spine stiffness?",
            "intent": {"primary": "rehabilitation", "secondary": ["exercise"]},
            "clinical_context": {
                "disease": ["AnkylosingSpondylitis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "young_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0037"],
            "hard_negative_passage_ids": ["P0035"],
            "expected_top_chunk": "P0037",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC047",
            "query_id": "Q047",
            "parent_query_id": None,
            "name": "Ankylosing Spondylitis Sleeping Posture",
            "query": "What sleeping position and mattress is recommended for ankylosing spondylitis postural alignment?",
            "raw_query": "What sleeping position and mattress is recommended for ankylosing spondylitis postural alignment?",
            "intent": {"primary": "safety", "secondary": ["posture"]},
            "clinical_context": {
                "disease": ["AnkylosingSpondylitis"],
                "condition": [],
                "anatomy": ["Spine"],
                "age_group": "young_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0038"],
            "hard_negative_passage_ids": ["P0035"],
            "expected_top_chunk": "P0038",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC048",
            "query_id": "Q048",
            "parent_query_id": None,
            "name": "Sarcopenia Creatine Supplementation",
            "query": "Can creatine supplementation combined with exercise improve muscle gains in sarcopenia?",
            "raw_query": "Can creatine supplementation combined with exercise improve muscle gains in sarcopenia?",
            "intent": {"primary": "treatment", "secondary": ["nutrition"]},
            "clinical_context": {
                "disease": ["Sarcopenia"],
                "condition": [],
                "anatomy": [],
                "age_group": "older_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0041"],
            "hard_negative_passage_ids": ["P0039"],
            "expected_top_chunk": "P0041",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC049",
            "query_id": "Q049",
            "parent_query_id": None,
            "name": "Pediatric Rickets Vitamin D Therapy",
            "query": "How is nutritional rickets in children treated with high-dose Vitamin D therapy?",
            "raw_query": "How is nutritional rickets in children treated with high-dose Vitamin D therapy?",
            "intent": {"primary": "treatment", "secondary": ["medication", "nutrition"]},
            "clinical_context": {
                "disease": ["Rickets"],
                "condition": [],
                "anatomy": [],
                "age_group": "pediatric",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0042"],
            "hard_negative_passage_ids": ["P0043"],
            "expected_top_chunk": "P0042",
            "changed_constraint": None,
            "expected_decision": "Answer"
        },
        {
            "id": "TC050",
            "query_id": "Q050",
            "parent_query_id": None,
            "name": "Fibrous Dysplasia Shepherd Crook Deformity",
            "query": "I have fibrous dysplasia and my hip bone is bending like a shepherd crook. What surgical management is needed?",
            "raw_query": "I have fibrous dysplasia and my hip bone is bending like a shepherd crook. What surgical management is needed?",
            "intent": {"primary": "treatment", "secondary": ["surgery"]},
            "clinical_context": {
                "disease": ["FibrousDysplasia"],
                "condition": [],
                "anatomy": ["Hip"],
                "age_group": "young_adult",
                "clinical_state": ["Stable"]
            },
            "positive_passage_ids": ["P0050"],
            "hard_negative_passage_ids": ["P0047"],
            "expected_top_chunk": "P0050",
            "changed_constraint": None,
            "expected_decision": "Answer"
        }
    ]

    with open("tests/test_cases.json", "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    print(f"Saved 50 Test Cases formatted strictly to Section 29 schema.")

if __name__ == "__main__":
    generate_scaled_data()
