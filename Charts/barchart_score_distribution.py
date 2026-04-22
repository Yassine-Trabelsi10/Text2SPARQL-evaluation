import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV
df = pd.read_csv("spinach_property_evaluation.csv", sep=";", encoding="utf-8-sig")

# Count values
counts = df["Property_correctness_score"].value_counts().sort_index()

# Compute percentages
percentages = (counts / counts.sum()) * 100

# Plot bar chart
plt.figure()
bars = plt.bar(percentages.index.astype(str), percentages.values)

# Add percentage labels on top
for i, v in enumerate(percentages.values):
    plt.text(i, v + 1, f"{v:.1f}%", ha='center')

# Titles and labels
plt.title("Property Correctness Score Distribution (%)")
plt.xlabel("Score (0 = Incorrect, 1 = Correct)")
plt.ylabel("Percentage")

plt.tight_layout()
plt.savefig("barchart_score_distribution.png")
plt.show()
