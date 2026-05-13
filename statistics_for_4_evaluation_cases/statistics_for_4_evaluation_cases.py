import pandas as pd
import json
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("spinach_property_evaluation_with_semantic.csv", sep=";", encoding="utf-8-sig")

# Load JSON
with open("gpt-5-mini.all.evaluation.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def to_set(s):
    if pd.isna(s) or str(s).strip() == "":
        return set()
    return set([x.strip() for x in str(s).split(",") if x.strip()])

case_counts = {
    "Same properties / Same result": 0,
    "Different properties / Different result": 0,
    "Same properties / Different result": 0,
    "Different properties / Same result": 0
}

skipped = 0

for _, row in df.iterrows():
    test_id = row["test_id"]

    if test_id not in data:
        continue

    gt = to_set(row["Extracted_properties_str"])
    pred = to_set(row["Predicted_extracted_properties_str"])

    # Skip if BOTH are empty
    if len(gt) == 0 and len(pred) == 0:
        skipped += 1
        continue

    same_properties = (gt == pred)
    score = data[test_id]["prediction"]["score"]
    same_result = (score == 1)

    if same_properties and same_result:
        case_counts["Same properties / Same result"] += 1
    elif not same_properties and not same_result:
        case_counts["Different properties / Different result"] += 1
    elif same_properties and not same_result:
        case_counts["Same properties / Different result"] += 1
    elif not same_properties and same_result:
        case_counts["Different properties / Same result"] += 1

# Print results
print("\nCounts per case:")
for k, v in case_counts.items():
    print(f"{k}: {v}")

print(f"\nSkipped (no properties in both GT & prediction): {skipped}")

# --------------------
# Plot + Save
# --------------------
labels = list(case_counts.keys())
values = list(case_counts.values())
total = sum(values)

percentages = [(v / total) * 100 for v in values]

plt.figure(figsize=(10, 6))
bars = plt.bar(labels, values)

plt.title(f"Distribution of Evaluation Cases (Full Dataset: {total} cases)")
plt.xlabel("Case Type")
plt.ylabel("Number of Queries")
plt.xticks(rotation=25, ha="right")

# Add number + percentage on top
for i, (v, p) in enumerate(zip(values, percentages)):
    plt.text(
        i,
        v + 2,
        f"{v} - {p:.1f}%",
        ha="center",
        fontsize=10
    )

plt.tight_layout()

# Save image
plt.savefig("evaluation_cases_distribution.png", dpi=300, bbox_inches="tight")

plt.show()