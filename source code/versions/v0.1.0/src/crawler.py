import os
import json

def generate_corpus():
    """
    Tạo dữ liệu Corpus tri thức lâm sàng tiếng Anh mẫu về Loãng xương (Osteoporosis)
    và Gãy xẹp đốt sống (Vertebral Fracture).
    Dữ liệu được trích xuất và chuẩn hóa từ các tài liệu AAOS và WHO.
    """
    corpus = [
        {
            "id": "P001",
            "title": "General Physical Activity Guidelines for Osteoporosis",
            "text": "For individuals with osteoporosis, physical activity is essential to maintain bone density and muscle strength. It is recommended to perform weight-bearing aerobic activities such as walking, light jogging, climbing stairs, and tennis. High-impact exercises and resistance training (weightlifting) are highly beneficial for stimulating bone remodeling, provided the patient has no active fractures and stable joint alignment.",
            "concepts": ["Osteoporosis", "LowImpactExercise", "HighImpactExercise", "Rehabilitation"]
        },
        {
            "id": "P002",
            "title": "Acute Vertebral Compression Fracture Conservative Management",
            "text": "During the acute phase of a vertebral compression fracture (typically the first 2 to 6 weeks post-injury), treatment focuses on pain control and bone stabilization. Complete bed rest should be limited to avoid muscle atrophy. Patients must strictly avoid spinal flexion, forward bending, and twisting, as these movements increase anterior column pressure and can cause further vertebral collapse. High-impact exercises, running, and heavy weightlifting are absolutely contraindicated.",
            "concepts": ["VertebralFracture", "AcutePostFracture", "Rest", "HighImpactExercise", "Safety"],
            "contraindications": ["HighImpactExercise"]
        },
        {
            "id": "P003",
            "title": "Post-Acute Rehabilitation after Spinal Fracture",
            "text": "Once the vertebral fracture has healed sufficiently (usually after 6 to 12 weeks), patients can transition to active rehabilitation. Exercises should focus on back extension to strengthen the erector spinae muscles, which helps unload the anterior vertebral bodies. Walking is highly recommended as a low-impact activity to promote mobility. However, high-impact activities and spinal flexion exercises remain contraindicated until bone stability is fully confirmed by imaging.",
            "concepts": ["VertebralFracture", "Stable", "LowImpactExercise", "Rehabilitation"]
        },
        {
            "id": "P004",
            "title": "Bisphosphonates for Postmenopausal Osteoporosis",
            "text": "Bisphosphonates, including alendronate and risedronate, are the primary pharmacological interventions to prevent osteoporotic fractures. They work by inhibiting osteoclast-mediated bone resorption, thereby increasing bone mineral density. Adequate intake of calcium and vitamin D is required to ensure optimal drug efficacy.",
            "concepts": ["Osteoporosis"]
        },
        {
            "id": "P005",
            "title": "Fall Prevention Strategies in Older Adults with Osteoporosis",
            "text": "Fall prevention is a critical component of osteoporosis care to prevent hip and spine fractures. Key recommendations include home safety modifications, vision checks, and balance training. Gentle balance and posture training such as Tai Chi or low-impact exercises are highly recommended to improve stability.",
            "concepts": ["Osteoporosis", "LowImpactExercise", "Safety"]
        }
    ]

    os.makedirs("data/corpus", exist_ok=True)
    output_path = "data/corpus/corpus.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    
    print(f"Generated sample corpus at {output_path} containing {len(corpus)} clinical guidelines.")

if __name__ == "__main__":
    generate_corpus()
