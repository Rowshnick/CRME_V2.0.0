import os
import matplotlib.pyplot as plt


os.makedirs("evaluation/results", exist_ok=True)

columns = [
    "Approach",
    "Semantic\nRepresentation",
    "Temporal\nContext",
    "Decision\nTraceability",
    "Artifact\nProvenance",
    "Research\nLifecycle"
]

rows = [
    ["Knowledge Management\nSystems", "✓", "—", "—", "△", "△"],
    ["Scientific Workflow\nSystems", "△", "—", "—", "✓", "△"],
    ["Knowledge Graph\nApproaches", "✓", "△", "—", "△", "—"],
    ["Provenance\nSystems", "△", "△", "—", "✓", "—"],
    ["AI Memory\nSystems", "✓", "✓", "△", "—", "—"],
    ["CRME", "✓", "✓", "✓", "✓", "✓"],
]


fig, ax = plt.subplots(figsize=(12, 4.8))

ax.axis("off")

table = ax.table(
    cellText=rows,
    colLabels=columns,
    cellLoc="center",
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)


# Highlight CRME row
for i in range(len(columns)):
    table[(6, i)].set_text_props(weight="bold")


plt.title(
    "Comparison of Existing Approaches and CRME",
    fontsize=14,
    weight="bold",
    pad=20
)

plt.tight_layout()

output = "evaluation/results/related_work_comparison_table.png"

plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight"
)

print("Generated:", output)

