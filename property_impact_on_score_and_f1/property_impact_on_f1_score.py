import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

df = pd.read_csv("spinach_property_evaluation_with_semantic.csv", sep=";", encoding="utf-8-sig")

def to_set(s):
    if pd.isna(s) or str(s).strip() == "":
        return set()
    return set(x.strip() for x in str(s).split(",") if x.strip())

def to_dict(s):
    d = {}
    if pd.isna(s):
        return d
    for item in str(s).split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            d[k.strip()] = v.strip()
    return d

property_labels = {}
for _, row in df.iterrows():
    property_labels.update(to_dict(row["All_properties_with_labels"]))

stats = defaultdict(lambda: {
    "frequency": 0,
    "missing_exec_scores": [],
    "extra_exec_scores": [],
    "missing_f1_scores": [],
    "extra_f1_scores": []
})

for _, row in df.iterrows():
    gt = to_set(row["Extracted_properties_str"])
    pred = to_set(row["Predicted_extracted_properties_str"])

    exec_score = float(row["execution_score"])
    f1_score = float(row["Property_f1_score"])

    missing = gt - pred
    extra = pred - gt

    for p in gt:
        stats[p]["frequency"] += 1

    for p in missing:
        stats[p]["missing_exec_scores"].append(exec_score)
        stats[p]["missing_f1_scores"].append(f1_score)

    for p in extra:
        stats[p]["extra_exec_scores"].append(exec_score)
        stats[p]["extra_f1_scores"].append(f1_score)

def impact(scores):
    if len(scores) == 0:
        return 0
    return 1 - (sum(scores) / len(scores))

rows = []

for p, values in stats.items():
    label = property_labels.get(p, "UNKNOWN")

    missing_exec = impact(values["missing_exec_scores"])
    extra_exec = impact(values["extra_exec_scores"])

    rows.append({
        "property": p,
        "label": label,
        "display_name": f"{p} = {label}",
        "frequency": values["frequency"],

        "missing_exec_impact": missing_exec,
        "extra_exec_impact": extra_exec,

        "missing_f1_impact": impact(values["missing_f1_scores"]),
        "extra_f1_impact": impact(values["extra_f1_scores"]),

        # temporary value ONLY for sorting (not saved)
        "_sort_value": missing_exec + extra_exec
    })

impact_df = pd.DataFrame(rows)

# Sort using temp column
impact_df = impact_df.sort_values(by="_sort_value", ascending=False)

# ❌ REMOVE the temp column before saving
impact_df = impact_df.drop(columns=["_sort_value"])

impact_df.to_excel("property_impact_exec_and_f1.xlsx", index=False)

# =========================
# GRAPH (unchanged)
# =========================
top = impact_df.head(15)

x = range(len(top))
width = 0.2

plt.figure(figsize=(16, 8))

plt.bar(
    [i - 1.5 * width for i in x],
    top["missing_exec_impact"],
    width=width,
    label="Execution impact when missing"
)

plt.bar(
    [i - 0.5 * width for i in x],
    top["extra_exec_impact"],
    width=width,
    label="Execution impact when extra"
)

plt.bar(
    [i + 0.5 * width for i in x],
    -top["missing_f1_impact"],
    width=width,
    label="F1 impact when missing"
)

plt.bar(
    [i + 1.5 * width for i in x],
    -top["extra_f1_impact"],
    width=width,
    label="F1 impact when extra"
)

plt.axhline(0, color="black", linewidth=1)

plt.xticks(x, top["display_name"], rotation=45, ha="right")
plt.ylabel("Impact score")
plt.title("Property Impact on Execution Score and F1 Score")

plt.legend()
plt.tight_layout()

plt.savefig("property_impact_exec_and_f1.png", dpi=300, bbox_inches="tight")
plt.show()