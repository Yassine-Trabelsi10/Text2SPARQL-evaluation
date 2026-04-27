import pandas as pd

# Load your CSV
df = pd.read_csv("spinach_property_evaluation_with_semantic.csv", sep=";", encoding="utf-8-sig")

# Selected examples per case
selected_cases = {
    "SAME_PROP_SAME_RESULT": ["test_0", "test_4", "test_34", "test_69", "test_75"],
    "DIFF_PROP_DIFF_RESULT": ["test_1", "test_3", "test_6", "test_7", "test_8"],
    "SAME_PROP_DIFF_RESULT": ["test_2", "test_5", "test_9", "test_11", "test_17"],
    "DIFF_PROP_SAME_RESULT": ["test_16", "test_29", "test_37", "test_54", "test_61"]
}

rows = []

# Keep order: case by case
for case_type, test_ids in selected_cases.items():
    for test_id in test_ids:
        match = df[df["test_id"] == test_id].copy()

        if not match.empty:
            match["case_type"] = case_type
            rows.append(match)
        else:
            print(f"Warning: {test_id} not found in CSV")

# Combine all selected rows
df_selected = pd.concat(rows, ignore_index=True)

# Save new file
df_selected.to_csv("selected_4_cases_examples.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df_selected[["test_id", "case_type"]])