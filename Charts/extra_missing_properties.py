import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Load file
df = pd.read_csv("spinach_property_evaluation_with_labels.csv", sep=";", encoding="utf-8-sig")

# Keep wrong queries only
df0 = df[df["Property_correctness_score"] == 0]

def to_set(s):
    if pd.isna(s) or str(s).strip() == "":
        return set()
    return set([x.strip() for x in str(s).split(",") if x.strip()])

missing_counter = Counter()
extra_counter = Counter()

# Compute missing vs extra
for _, row in df0.iterrows():
    gt = to_set(row["Extracted_properties_str"])
    pred = to_set(row["Predicted_extracted_properties_str"])

    missing_counter.update(gt - pred)
    extra_counter.update(pred - gt)

# Convert to dataframe
missing_df = pd.DataFrame(missing_counter.items(), columns=["property", "missing"])
extra_df = pd.DataFrame(extra_counter.items(), columns=["property", "extra"])

# Merge both
df_all = pd.merge(missing_df, extra_df, on="property", how="outer").fillna(0)

# Load labels
labels_df = pd.read_csv("ALL_wikidata_properties_labels.csv", sep=";", encoding="utf-8-sig")
label_map = dict(zip(labels_df["property"], labels_df["propertyLabel"]))

df_all["label"] = df_all["property"].map(label_map).fillna("UNKNOWN")

# Keep top 10 by total impact
df_all["total"] = df_all["missing"] + df_all["extra"]
df_all = df_all.sort_values("total", ascending=False).head(10)

df_all["display"] = df_all["property"] + " = " + df_all["label"]

# -----------------------------
# Plot grouped bar chart
# -----------------------------
x = range(len(df_all))

plt.figure(figsize=(12,6))

plt.bar(x, df_all["missing"], width=0.4, label="Missing (GT only)")
plt.bar([i + 0.4 for i in x], df_all["extra"], width=0.4, label="Extra (Predicted only)")

plt.xticks([i + 0.2 for i in x], df_all["display"], rotation=45, ha="right")

plt.title("Top Error-Causing Properties (Missing vs Extra)")
plt.ylabel("Count")
plt.legend()

plt.tight_layout()
plt.savefig("extra_missing_properties.png")
plt.show()