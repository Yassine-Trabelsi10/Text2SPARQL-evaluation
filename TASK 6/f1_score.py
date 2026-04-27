import pandas as pd

df = pd.read_csv("spinach_property_evaluation_with_labels.csv", sep=";", encoding="utf-8-sig")

def to_set(s):
    if pd.isna(s) or str(s).strip() == "":
        return set()
    return set([x.strip() for x in str(s).split(",") if x.strip()])

def property_precision(gt_props, pred_props):
    gt = to_set(gt_props)
    pred = to_set(pred_props)

    if len(pred) == 0:
        return 1.0 if len(gt) == 0 else 0.0

    return len(gt & pred) / len(pred)

def property_recall(gt_props, pred_props):
    gt = to_set(gt_props)
    pred = to_set(pred_props)

    if len(gt) == 0:
        return 1.0

    return len(gt & pred) / len(gt)

def property_f1(gt_props, pred_props):
    p = property_precision(gt_props, pred_props)
    r = property_recall(gt_props, pred_props)

    if p + r == 0:
        return 0.0

    return 2 * p * r / (p + r)

df["Property_precision"] = df.apply(
    lambda row: property_precision(
        row["Extracted_properties_str"],
        row["Predicted_extracted_properties_str"]
    ),
    axis=1
)

df["Property_recall"] = df.apply(
    lambda row: property_recall(
        row["Extracted_properties_str"],
        row["Predicted_extracted_properties_str"]
    ),
    axis=1
)

df["Property_f1_score"] = df.apply(
    lambda row: property_f1(
        row["Extracted_properties_str"],
        row["Predicted_extracted_properties_str"]
    ),
    axis=1
)

df["Property_f1_percent"] = (df["Property_f1_score"] * 100).round(2)

df.to_csv("spinach_property_evaluation_with_f1.csv", sep=";", index=False, encoding="utf-8-sig")

print(df[[
    "test_id",
    "Extracted_properties_str",
    "Predicted_extracted_properties_str",
    "Property_precision",
    "Property_recall",
    "Property_f1_percent"
]].head(10))