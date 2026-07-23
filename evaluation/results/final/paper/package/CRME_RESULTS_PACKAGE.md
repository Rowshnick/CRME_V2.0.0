# CRME Results and Evidence Package

This package was automatically assembled from the canonical CRME evaluation evidence and paper-generation artifacts.

---

# Results

The CRME evaluation pipeline was conducted across two datasets using five evaluation metrics.

The comparative evaluation identified SRCB_v1 as the best-performing dataset across all reported metrics.

- **MCS**: 47.5
- **SRS**: 100
- **KGQ**: 40.0
- **RRS**: 43.33
- **CES**: 57.71

These measurements establish the baseline performance profile used for subsequent component-level ablation analysis.

---

# Ablation Study

The ablation analysis evaluated the contribution of four architectural components under five configurations.

The decisions component exhibited the largest aggregate degradation, followed by relations, sessions, and artifacts.

## Component Ranking

1. **decisions** — aggregate degradation of 52.08
2. **relations** — aggregate degradation of 50.0
3. **sessions** — aggregate degradation of 20.83
4. **artifacts** — aggregate degradation of 9.38

These results support comparative component contribution analysis. They should not be interpreted as definitive causal estimates of architectural importance.

---

# Statistical Analysis

The current evaluation package reports descriptive baseline metrics and component-level degradation values.

- **MCS**: 47.5
- **SRS**: 100
- **KGQ**: 40.0
- **RRS**: 43.33
- **CES**: 57.71

No inferential statistical test, confidence interval, or hypothesis test is currently included in the evidence package.

Accordingly, the present results should be interpreted as descriptive and comparative rather than as statistically significant evidence of superiority over a baseline.

---

# Evidence-Backed Discussion

The largest observed aggregate degradation was associated with the **decisions** component (52.08).

The lowest observed aggregate degradation was associated with the **artifacts** component (9.38).

Together, these results indicate heterogeneous component contribution within the evaluated CRME architecture.

However, the observed ranking should be interpreted as an empirical comparative result rather than a definitive causal decomposition.

---

# Threats to Validity

Several limitations should be considered when interpreting the reported findings.

First, the current evidence package does not include inferential statistical testing or confidence interval estimation.

Second, the ablation results provide comparative evidence of component contribution but do not establish definitive causal importance.

Third, the reported evaluation is based on the currently available datasets and evaluation configurations. Generalization to other datasets and research workflows requires further validation.

---

# Reproducibility

All reported results are derived from stored CRME evaluation artifacts.

The evaluation pipeline preserves the relationship between raw evidence, aggregated summaries, paper tables, figures, and claim-level evidence.

The Q1 consistency audit completed with overall status `PASS`.

Raw evaluation outputs are preserved and are not modified by the paper generation layer.

---

## Tables and Figures

The following LaTeX tables and figure data are available for direct integration into the target manuscript.

### Tables

- `tables/baseline_metrics.tex`
- `tables/ablation_results.tex`
- `tables/component_ranking.tex`

### Figures

- `figures/component_contribution_ranking.png`
- `figures/component_contribution.csv`

---

## Evidence Status

The package is generated from stored evaluation evidence and audited paper artifacts.

Unsupported claims are not promoted to established findings.

Ablation results are interpreted as comparative contribution evidence rather than definitive causal estimates.
