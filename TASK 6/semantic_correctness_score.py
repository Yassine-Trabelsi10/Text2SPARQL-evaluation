import pandas as pd
import json

# =========================
# Load CSV
# =========================
csv_path = "spinach_property_evaluation_with_f1.csv"
df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")

# =========================
# Load JSON
# =========================
json_path = "gpt-5-mini.all.evaluation.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# =========================
# Build mapping: test_id → score
# =========================
score_map = {}

for test_id, content in data.items():
    try:
        score = content["prediction"]["score"]
    except:
        score = None
    score_map[test_id] = score

# =========================
# Function to convert score → True/False
# =========================
def is_correct(test_id):
    score = score_map.get(test_id, None)
    
    if score is None:
        return False
    
    return score >= 0.99  # threshold

# =========================
# Apply to dataframe
# =========================
df["semantic_correct"] = df["test_id"].apply(is_correct)

# Optional: also keep raw score
df["execution_score"] = df["test_id"].map(score_map)

# =========================
# Save new CSV
# =========================
output_path = "spinach_property_evaluation_with_semantic.csv"
df.to_csv(output_path, sep=";", index=False, encoding="utf-8-sig")

print("✅ Done. File saved as:", output_path)