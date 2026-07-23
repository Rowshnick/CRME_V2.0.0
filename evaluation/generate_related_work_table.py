import os
import csv


OUTPUT_DIR = "evaluation/results"

os.makedirs(OUTPUT_DIR, exist_ok=True)


table_data = [
    [
        "Approach",
        "Semantic\nRepresentation",
        "Temporal\nContext",
        "Decision\nHistory",
        "Artifact\nProvenance",
        "Research\nLifecycle"
    ],
    [
        "Knowledge Management Systems",
        "✓",
        "✗",
        "✗",
        "△",
        "△"
    ],
    [
        "Scientific Workflow Systems",
        "△",
        "✗",
        "✗",
        "✓",
        "△"
    ],
    [
        "Knowledge Graph Approaches",
        "✓",
        "△",
        "✗",
        "△",
        "✗"
    ],
    [
        "Provenance Systems",
        "△",
        "△",
        "✗",
        "✓",
        "✗"
    ],
    [
        "AI Memory Systems",
        "✓",
        "✓",
        "△",
        "✗",
        "✗"
    ],
    [
        "CRME",
        "✓",
        "✓",
        "✓",
        "✓",
        "✓"
    ]
]


# -------------------------
# Generate CSV
# -------------------------

csv_path = os.path.join(
    OUTPUT_DIR,
    "related_work_comparison_table.csv"
)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(table_data)


# -------------------------
# Generate LaTeX Table
# -------------------------

latex_path = os.path.join(
    OUTPUT_DIR,
    "related_work_comparison_table.tex"
)


latex = r"""
\begin{table}[ht]
\centering
\caption{Comparison of Existing Research Memory Related Approaches}
\label{tab:related_work_comparison}

\begin{tabular}{lccccc}
\hline
Approach &
Semantic &
Temporal &
Decision &
Artifact &
Research \\

&
Representation &
Context &
History &
Provenance &
Lifecycle \\

\hline

"""


for row in table_data[1:]:

    latex += (
        row[0]
        + " & "
        + " & ".join(row[1:])
        + r" \\"
        + "\n"
    )


latex += r"""
\hline
\end{tabular}
\end{table}
"""


with open(
    latex_path,
    "w",
    encoding="utf-8"
) as f:
    f.write(latex)


print("Generated:")
print(csv_path)
print(latex_path)

