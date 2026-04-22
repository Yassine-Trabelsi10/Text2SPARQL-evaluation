import pandas as pd

# -----------------------------
# 1) Load the 7-column evaluation CSV
# -----------------------------
df_eval = pd.read_csv("spinach_property_evaluation.csv", sep=";", encoding="utf-8-sig")

# -----------------------------
# 2) Load the property mapping CSV
#    Must contain: property, propertyLabel
# -----------------------------
df_props = pd.read_csv("ALL_wikidata_properties_labels.csv", sep=";", encoding="utf-8-sig")

# Build dictionary: P279 -> subclass of
property_label_map = dict(zip(df_props["property"], df_props["propertyLabel"]))

# -----------------------------
# 3) Function to merge GT + predicted properties
#    and convert them to Pxxx=label
# -----------------------------
def build_property_label_column(gt_props, pred_props):
    gt_list = [p.strip() for p in str(gt_props).split(",") if p.strip()]
    pred_list = [p.strip() for p in str(pred_props).split(",") if p.strip()]

    # combine and keep distinct while preserving order
    seen = set()
    combined = []
    for p in gt_list + pred_list:
        if p not in seen:
            seen.add(p)
            combined.append(p)

    # convert to "P279=subclass of"
    labeled = []
    for p in combined:
        label = property_label_map.get(p, "UNKNOWN")
        labeled.append(f"{p}={label}")

    return ", ".join(labeled)

# -----------------------------
# 4) Add the new 8th column
# -----------------------------
df_eval["All_properties_with_labels"] = df_eval.apply(
    lambda row: build_property_label_column(
        row["Extracted_properties_str"],
        row["Predicted_extracted_properties_str"]
    ),
    axis=1
)

# -----------------------------
# 5) Save final CSV
# -----------------------------
df_eval.to_csv("spinach_property_evaluation_with_labels.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df_eval.head(10))