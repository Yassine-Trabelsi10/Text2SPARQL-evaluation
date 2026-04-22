import pandas as pd

# -----------------------------
# 1) Load your CSV
# -----------------------------
df = pd.read_csv("spinach_ground_truth_and_prediction_with_properties.csv", sep=";", encoding="utf-8-sig")

# -----------------------------
# 2) Function to compare properties
# -----------------------------
def compute_score(gt_props, pred_props):
    # Convert to sets
    gt_set = set([p.strip() for p in str(gt_props).split(",") if p.strip()])
    pred_set = set([p.strip() for p in str(pred_props).split(",") if p.strip()])

    # Compare sets (order does NOT matter)
    return 1 if gt_set == pred_set else 0

# -----------------------------
# 3) Apply scoring
# -----------------------------
df["Property_correctness_score"] = df.apply(
    lambda row: compute_score(
        row["Extracted_properties_str"],
        row["Predicted_extracted_properties_str"]
    ),
    axis=1
)

# -----------------------------
# 4) Save final CSV
# -----------------------------
df.to_csv("spinach_property_evaluation.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df.head(10))