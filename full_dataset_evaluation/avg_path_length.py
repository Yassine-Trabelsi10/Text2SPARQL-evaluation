# pip install pandas openpyxl matplotlib networkx

import pandas as pd
import matplotlib.pyplot as plt
import re
import networkx as nx

# =========================
# 1) Load dataset
# =========================
df = pd.read_excel("zero_few_shot_with_reasoning_tokens_fixed(4).xlsx")

GT_QUERY_COL = "SPARQL query"
PRED_QUERY_COL = "Predicted SPARQL query"

# =========================
# 2) Cleaning functions
# =========================
def clean_query(q):
    if pd.isna(q):
        return ""
    q = str(q)
    q = re.sub(r"#.*", "", q)
    return q

def remove_prefix_declarations(query):
    return re.sub(
        r"\bPREFIX\s+[A-Za-z][\w-]*:\s*<[^>]*>\s*",
        " ",
        query,
        flags=re.IGNORECASE
    )

def remove_non_graph_blocks(query):
    query = re.sub(
        r"SERVICE\s+wikibase:label\s*\{.*?\}",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

    query = re.sub(
        r"\bFILTER\s+NOT\s+EXISTS\s*\{.*?\}",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

    query = re.sub(
        r"\bFILTER\s*\([^)]*\)",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

    query = re.sub(
        r"\bBIND\s*\([^)]*\)",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

    query = re.sub(
        r"\bVALUES\s+\?\w+\s*\{[^}]*\}",
        " ",
        query,
        flags=re.IGNORECASE | re.DOTALL
    )

    return query

# =========================
# 3) Extract triple patterns
# =========================
def extract_triple_patterns(query):
    query = clean_query(query)
    query = remove_prefix_declarations(query)
    query = remove_non_graph_blocks(query)

    subject = r"(?:\?[A-Za-z_]\w*|wd:[A-Za-z0-9_]+|_:[A-Za-z0-9_]+)"
    predicate = r"(?:[A-Za-z][\w-]*:[A-Za-z0-9_]+(?:\s*[/*+|]\s*[A-Za-z][\w-]*:[A-Za-z0-9_]+|\s*[+*])*)"
    object_ = r"(?:\?[A-Za-z_]\w*|wd:[A-Za-z0-9_]+|[A-Za-z][\w-]*:[A-Za-z0-9_]+|\".*?\"(?:@\w+)?|\d+(?:\.\d+)?)"

    triple_pattern = re.compile(
        f"({subject})\\s+({predicate})\\s+({object_})",
        flags=re.IGNORECASE | re.DOTALL
    )

    triples = []

    for s, p, o in triple_pattern.findall(query):
        triples.append((s.strip(), p.strip(), o.strip()))

    return triples

# =========================
# 4) Compute path metrics
# =========================
def compute_path_metrics(query):
    triples = extract_triple_patterns(query)

    if len(triples) == 0:
        return {
            "num_triples": 0,
            "avg_path_length": 0,
            "max_path_length": 0,
            "num_1_hop_paths": 0,
            "num_2_hop_paths": 0,
            "num_3_plus_hop_paths": 0
        }

    graph = nx.Graph()

    for s, p, o in triples:
        graph.add_edge(s, o, property=p)

    path_lengths = []

    for component in nx.connected_components(graph):
        subgraph = graph.subgraph(component)
        lengths = dict(nx.all_pairs_shortest_path_length(subgraph))
        nodes = list(subgraph.nodes())

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                src = nodes[i]
                tgt = nodes[j]

                if tgt in lengths[src]:
                    path_lengths.append(lengths[src][tgt])

    if len(path_lengths) == 0:
        return {
            "num_triples": len(triples),
            "avg_path_length": 1,
            "max_path_length": 1,
            "num_1_hop_paths": len(triples),
            "num_2_hop_paths": 0,
            "num_3_plus_hop_paths": 0
        }

    return {
        "num_triples": len(triples),
        "avg_path_length": sum(path_lengths) / len(path_lengths),
        "max_path_length": max(path_lengths),
        "num_1_hop_paths": sum(1 for x in path_lengths if x == 1),
        "num_2_hop_paths": sum(1 for x in path_lengths if x == 2),
        "num_3_plus_hop_paths": sum(1 for x in path_lengths if x >= 3)
    }

# =========================
# 5) Apply analysis per query
# =========================
rows = []

for _, row in df.iterrows():
    test_id = row.get("test_id", "")

    gt_metrics = compute_path_metrics(row[GT_QUERY_COL])
    pred_metrics = compute_path_metrics(row[PRED_QUERY_COL])

    rows.append({
        "test_id": test_id,

        "gt_num_triples": gt_metrics["num_triples"],
        "pred_num_triples": pred_metrics["num_triples"],

        "gt_avg_path_length": gt_metrics["avg_path_length"],
        "pred_avg_path_length": pred_metrics["avg_path_length"],
        "diff_avg_path_length": pred_metrics["avg_path_length"] - gt_metrics["avg_path_length"],

        "gt_max_path_length": gt_metrics["max_path_length"],
        "pred_max_path_length": pred_metrics["max_path_length"],
        "diff_max_path_length": pred_metrics["max_path_length"] - gt_metrics["max_path_length"],

        "gt_1_hop_paths": gt_metrics["num_1_hop_paths"],
        "pred_1_hop_paths": pred_metrics["num_1_hop_paths"],

        "gt_2_hop_paths": gt_metrics["num_2_hop_paths"],
        "pred_2_hop_paths": pred_metrics["num_2_hop_paths"],

        "gt_3_plus_hop_paths": gt_metrics["num_3_plus_hop_paths"],
        "pred_3_plus_hop_paths": pred_metrics["num_3_plus_hop_paths"]
    })

path_df = pd.DataFrame(rows)

# =========================
# 6) Global summary
# =========================
summary_df = pd.DataFrame([
    {
        "metric": "average_path_length",
        "ground_truth": path_df["gt_avg_path_length"].mean(),
        "predicted": path_df["pred_avg_path_length"].mean(),
        "difference_pred_minus_gt": path_df["pred_avg_path_length"].mean() - path_df["gt_avg_path_length"].mean()
    },
    {
        "metric": "average_max_path_length",
        "ground_truth": path_df["gt_max_path_length"].mean(),
        "predicted": path_df["pred_max_path_length"].mean(),
        "difference_pred_minus_gt": path_df["pred_max_path_length"].mean() - path_df["gt_max_path_length"].mean()
    },
    {
        "metric": "total_1_hop_paths",
        "ground_truth": path_df["gt_1_hop_paths"].sum(),
        "predicted": path_df["pred_1_hop_paths"].sum(),
        "difference_pred_minus_gt": path_df["pred_1_hop_paths"].sum() - path_df["gt_1_hop_paths"].sum()
    },
    {
        "metric": "total_2_hop_paths",
        "ground_truth": path_df["gt_2_hop_paths"].sum(),
        "predicted": path_df["pred_2_hop_paths"].sum(),
        "difference_pred_minus_gt": path_df["pred_2_hop_paths"].sum() - path_df["gt_2_hop_paths"].sum()
    },
    {
        "metric": "total_3_plus_hop_paths",
        "ground_truth": path_df["gt_3_plus_hop_paths"].sum(),
        "predicted": path_df["pred_3_plus_hop_paths"].sum(),
        "difference_pred_minus_gt": path_df["pred_3_plus_hop_paths"].sum() - path_df["gt_3_plus_hop_paths"].sum()
    }
])

# =========================
# 7) Save Excel file
# =========================
with pd.ExcelWriter("sparql_path_length_analysis.xlsx") as writer:
    path_df.to_excel(writer, sheet_name="per_query_path_lengths", index=False)
    summary_df.to_excel(writer, sheet_name="global_summary", index=False)

# =========================
# 8) Graph 1: Average path length comparison
# =========================
plt.figure(figsize=(7, 5))

plt.bar(
    ["Ground Truth", "Predicted"],
    [
        path_df["gt_avg_path_length"].mean(),
        path_df["pred_avg_path_length"].mean()
    ]
)

plt.ylabel("Average path length")
plt.title("Average SPARQL Path Length Comparison")
plt.tight_layout()

plt.savefig("average_path_length_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

# =========================
# 9) Graph 2: Hop length distribution
# =========================
hop_df = pd.DataFrame({
    "hop_category": ["1-hop", "2-hop", "3+ hop"],
    "ground_truth": [
        path_df["gt_1_hop_paths"].sum(),
        path_df["gt_2_hop_paths"].sum(),
        path_df["gt_3_plus_hop_paths"].sum()
    ],
    "predicted": [
        path_df["pred_1_hop_paths"].sum(),
        path_df["pred_2_hop_paths"].sum(),
        path_df["pred_3_plus_hop_paths"].sum()
    ]
})

x = range(len(hop_df))
width = 0.4

plt.figure(figsize=(8, 5))

plt.bar(
    [i - width / 2 for i in x],
    hop_df["ground_truth"],
    width=width,
    label="Ground Truth"
)

plt.bar(
    [i + width / 2 for i in x],
    hop_df["predicted"],
    width=width,
    label="Predicted"
)

plt.xticks(x, hop_df["hop_category"])
plt.ylabel("Number of paths")
plt.title("SPARQL Hop-Length Distribution")
plt.legend()
plt.tight_layout()

plt.savefig("hop_length_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

print("Done")
print("Created:")
print("- sparql_path_length_analysis.xlsx")
print("- average_path_length_comparison.png")
print("- hop_length_distribution.png")