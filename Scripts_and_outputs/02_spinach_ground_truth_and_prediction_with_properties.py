import pandas as pd
import re
import json

# Regex: extract only direct Wikidata properties like wdt:P31, wdt:P212
pattern = r'wdt:(P\d+)'

def extract_properties(query):
    if not query:
        return []
    props = re.findall(pattern, str(query))

    # remove duplicates while keeping order
    seen = set()
    ordered = []
    for p in props:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    return ordered

# -----------------------------
# 1) Load your existing CSV
# -----------------------------
df = pd.read_csv("spinach_ground_truth_with_properties.csv", sep=";", encoding="utf-8-sig")

# -----------------------------
# 2) Load evaluation JSON
# -----------------------------
with open("gpt-5-mini.all.evaluation.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# -----------------------------
# 3) Build mapping: test_id -> predicted query
# -----------------------------
predicted_query_map = {}
predicted_properties_map = {}

for test_id, content in eval_data.items():
    predicted_query = content.get("prediction", {}).get("sparql", "")
    predicted_query_map[test_id] = predicted_query
    predicted_properties_map[test_id] = ", ".join(extract_properties(predicted_query))

# -----------------------------
# 4) Add the 2 new columns
# -----------------------------
df["Predicted SPARQL query"] = df["test_id"].map(predicted_query_map)
df["Predicted_extracted_properties_str"] = df["test_id"].map(predicted_properties_map)

# -----------------------------
# 5) Save updated CSV
# -----------------------------
df.to_csv("spinach_ground_truth_and_prediction_with_properties.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df.head(10))