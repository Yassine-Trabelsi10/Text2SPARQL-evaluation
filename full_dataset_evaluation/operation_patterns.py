# pip install pandas openpyxl matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import re

df = pd.read_excel("zero_few_shot_with_reasoning_tokens_fixed.xlsx")

GT_QUERY_COL = "SPARQL query"
PRED_QUERY_COL = "Predicted SPARQL query"

OPERATIONS = {
    "TRIPLE_PATTERNS": None,
    "FILTER": r"\bFILTER\b",
    "FILTER_NOT_EXISTS": r"\bFILTER\s+NOT\s+EXISTS\b",
    "OPTIONAL": r"\bOPTIONAL\b",
    "UNION": r"\bUNION\b",
    "ORDER_BY": r"\bORDER\s+BY\b",
    "GROUP_BY": r"\bGROUP\s+BY\b",
    "HAVING": r"\bHAVING\b",
    "LIMIT": r"\bLIMIT\b",
    "DISTINCT": r"\bDISTINCT\b",
    "COUNT": r"\bCOUNT\s*\(",
    "SERVICE": r"\bSERVICE\b",
    "VALUES": r"\bVALUES\b",
    "BIND": r"\bBIND\b",
    "MINUS": r"\bMINUS\b"
}

def clean_query(q):
    if pd.isna(q):
        return ""
    q = str(q)
    q = re.sub(r"#.*", "", q)
    return q

def count_regex(query, pattern):
    query = clean_query(query)
    return len(re.findall(pattern, query, flags=re.IGNORECASE))

def remove_prefix_declarations(query):
    return re.sub(
        r"\bPREFIX\s+[A-Za-z][\w-]*:\s*<[^>]*>\s*",
        " ",
        query,
        flags=re.IGNORECASE
    )

def remove_service_label_block(query):
    return re.sub(
        r"SERVICE\s+wikibase:label\s*\{.*?\}",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

def count_triple_patterns(query):
    query = clean_query(query)
    query = remove_prefix_declarations(query)
    query = remove_service_label_block(query)

    query = re.sub(r"\bFILTER\s+NOT\s+EXISTS\s*\{.*?\}", " ", query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r"\bFILTER\s*\([^)]*\)", " ", query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r"\bBIND\s*\([^)]*\)", " ", query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r"\bVALUES\s+\?\w+\s*\{[^}]*\}", " ", query, flags=re.IGNORECASE | re.DOTALL)

    subject = r"(?:\?[A-Za-z_]\w*|wd:[A-Za-z0-9_]+|_:[A-Za-z0-9_]+)"
    predicate = r"(?:[A-Za-z][\w-]*:[A-Za-z0-9_]+(?:\s*[/*+|]\s*[A-Za-z][\w-]*:[A-Za-z0-9_]+|\s*[+*])*)"
    object_ = r"(?:\?[A-Za-z_]\w*|wd:[A-Za-z0-9_]+|[A-Za-z][\w-]*:[A-Za-z0-9_]+|\".*?\"(?:@\w+)?|\d+(?:\.\d+)?)"

    triple_pattern = re.compile(
        subject + r"\s+" + predicate + r"\s+" + object_,
        flags=re.IGNORECASE | re.DOTALL
    )

    return len(triple_pattern.findall(query))

rows = []

for operation, pattern in OPERATIONS.items():

    if operation == "TRIPLE_PATTERNS":
        gt_count = df[GT_QUERY_COL].apply(count_triple_patterns).sum()
        pred_count = df[PRED_QUERY_COL].apply(count_triple_patterns).sum()
    else:
        gt_count = df[GT_QUERY_COL].apply(lambda q: count_regex(q, pattern)).sum()
        pred_count = df[PRED_QUERY_COL].apply(lambda q: count_regex(q, pattern)).sum()

    rows.append({
        "operation": operation,
        "ground_truth_count": int(gt_count),
        "predicted_count": int(pred_count),
        "difference_pred_minus_gt": int(pred_count - gt_count),
        "absolute_difference": int(abs(pred_count - gt_count))
    })

summary_df = pd.DataFrame(rows)

summary_df.to_excel(
    "sparql_operation_summary.xlsx",
    index=False
)

plot_df = summary_df.copy()

x = range(len(plot_df))
width = 0.4

plt.figure(figsize=(15, 7))

plt.bar(
    [i - width / 2 for i in x],
    plot_df["ground_truth_count"],
    width=width,
    label="Ground-truth queries"
)

plt.bar(
    [i + width / 2 for i in x],
    plot_df["predicted_count"],
    width=width,
    label="Predicted queries"
)

plt.xticks(x, plot_df["operation"], rotation=45, ha="right")
plt.ylabel("Frequency")
plt.title("SPARQL Operation and Triple Pattern Comparison")
plt.legend()
plt.tight_layout()

plt.savefig("sparql_operation_pattern_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

diff_df = summary_df.sort_values(
    by="absolute_difference",
    ascending=False
).head(10)

plt.figure(figsize=(12, 6))

plt.barh(
    diff_df["operation"],
    diff_df["difference_pred_minus_gt"]
)

plt.axvline(0, linewidth=1)

plt.xlabel("Difference: predicted count - ground-truth count")
plt.ylabel("SPARQL pattern")
plt.title("Top SPARQL Operation Differences Between Predicted and Ground-Truth Queries")

plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig("top_operation_differences.png", dpi=300, bbox_inches="tight")
plt.close()

print("Done")