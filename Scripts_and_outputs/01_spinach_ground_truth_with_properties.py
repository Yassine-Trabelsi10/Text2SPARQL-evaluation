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

rows = []

# Load JSONL file line by line
with open("test.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        item = json.loads(line)

        test_id = item.get("id")  # ✅ important
        question = item.get("question")
        sparql_query = item.get("sparql", "")

        extracted_properties = ", ".join(extract_properties(sparql_query))

        rows.append({
            "test_id": test_id,
            "Question": question,
            "SPARQL query": sparql_query,
            "Extracted_properties_str": extracted_properties
        })

# Create dataframe
df_final = pd.DataFrame(rows)

# Save CSV
df_final.to_csv("spinach_ground_truth_with_properties.csv", sep=";", index=False, encoding="utf-8-sig")

print("Done.")
print(df_final.head(10))