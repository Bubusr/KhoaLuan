import re
import json

with open("note/experiment_report.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

test_cases = []
in_table = False
for line in lines:
    if line.startswith("> | TC001 |"):
        in_table = True
    
    if in_table:
        if line.startswith("> | TC"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                tc_id = parts[1]
                query = parts[2]
                expected = parts[3].replace("`", "")
                
                decision = "Answer"
                if tc_id in ["TC002", "TC007"]:
                    decision = "Escalate"
                    
                test_cases.append({
                    "id": tc_id,
                    "name": "Generated " + tc_id,
                    "query": query,
                    "expected_top_chunk": expected,
                    "expected_decision": decision,
                    "description": "Auto-generated from experiment_report.md"
                })
        elif line.startswith("> ###") or line.startswith("---"):
            if len(test_cases) >= 50:
                break

with open("tests/test_cases.json", "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=2)

print(f"Generated {len(test_cases)} test cases.")
