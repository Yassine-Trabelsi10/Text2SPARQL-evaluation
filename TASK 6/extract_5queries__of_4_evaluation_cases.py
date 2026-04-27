import pandas as pd
import json

# Load CSV
df = pd.read_csv("spinach_property_evaluation_with_semantic.csv", sep=";", encoding="utf-8-sig")

# Load JSON
with open("gpt-5-mini.all.evaluation.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def to_set(s):
    if pd.isna(s) or str(s).strip() == "":
        return set()
    return set([x.strip() for x in str(s).split(",") if x.strip()])

cases = {
    "same_prop_same_result": [],
    "diff_prop_diff_result": [],
    "same_prop_diff_result": [],
    "diff_prop_same_result": []
}

skipped_no_properties = []

for _, row in df.iterrows():
    test_id = row["test_id"]

    if test_id not in data:
        continue

    gt = to_set(row["Extracted_properties_str"])
    pred = to_set(row["Predicted_extracted_properties_str"])

    # ✅ CHANGE HERE: use AND instead of OR
    if len(gt) == 0 and len(pred) == 0:
        skipped_no_properties.append(test_id)
        continue

    same_properties = (gt == pred)

    score = data[test_id]["prediction"]["score"]
    same_result = (score == 1)

    if same_properties and same_result:
        cases["same_prop_same_result"].append(test_id)
    elif not same_properties and not same_result:
        cases["diff_prop_diff_result"].append(test_id)
    elif same_properties and not same_result:
        cases["same_prop_diff_result"].append(test_id)
    elif not same_properties and same_result:
        cases["diff_prop_same_result"].append(test_id)

# Print skipped count
print(f"Skipped rows with no properties (both empty): {len(skipped_no_properties)}")

# Print 5 examples per case
for k, v in cases.items():
    print(f"\n{k.upper()}:")
    print(v[:5])