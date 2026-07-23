# Evidence-Backed Manuscript: CRME

## Abstract

This manuscript presents an evidence-backed evaluation of the Cognitive Research Memory Engine (CRME), a structured research-memory architecture designed to organize and preserve research evidence, sessions, decisions, relations, and artifacts.

The evaluation was conducted across 2 datasets using 5 evaluation metrics and was followed by component-level ablation analysis.

The comparative evaluation identified SRCB_v1 as the best-performing dataset across the reported metrics.

The ablation analysis indicated heterogeneous component contribution, with the decisions component exhibiting the largest aggregate degradation and the artifacts component exhibiting the lowest observed degradation.

The findings are interpreted as descriptive and comparative evidence. No inferential statistical test or confidence interval was included in the current evidence package; therefore, claims of statistical significance or definitive causal importance are not established.

## 1. Introduction

Modern research workflows generate heterogeneous forms of information, including experimental results, project decisions, sessions, relationships, and digital artifacts.

Without structured memory mechanisms, important research context can become fragmented across sessions and tools.

CRME addresses this problem through a structured research-memory architecture intended to preserve and organize research evidence while maintaining traceability between raw evaluation outputs and higher-level research artifacts.

The present evaluation focuses on the empirical evidence currently available for the system. The objective is to establish a reproducible baseline and characterize the relative contribution of evaluated architectural components without overstating the available evidence.

## 2. Evaluation Design

The evaluation used 2 datasets and 5 evaluation metrics.

The evaluation pipeline consisted of four stages:

1. Experiment execution
2. Dataset comparison
3. Component ablation analysis
4. Statistical and descriptive evidence aggregation

The evaluated metrics were:

- `MCS`
- `SRS`
- `KGQ`
- `RRS`
- `CES`

## 3. Results

The comparative evaluation identified SRCB_v1 as the best-performing dataset across all reported metrics.

The resulting baseline performance profile was:

- **MCS**: 47.5
- **SRS**: 100
- **KGQ**: 40
- **RRS**: 43.33
- **CES**: 57.71

These results establish the descriptive baseline used for the subsequent component-level ablation analysis.

## 4. Ablation Study

The ablation analysis evaluated 4 architectural components under 5 configurations.

The decisions component exhibited the largest observed aggregate degradation, whereas the artifacts component exhibited the lowest observed aggregate degradation.

### Component Ranking

1. **decisions** — aggregate degradation of 52.08
2. **relations** — aggregate degradation of 50
3. **sessions** — aggregate degradation of 20.83
4. **artifacts** — aggregate degradation of 9.38

The observed ranking supports comparative component contribution analysis. It should not be interpreted as a definitive causal decomposition of architectural importance.

## 5. Statistical Analysis

The current evidence package contains descriptive baseline metrics and component-level degradation values.

- **MCS**: 47.5
- **SRS**: 100
- **KGQ**: 40
- **RRS**: 43.33
- **CES**: 57.71

No inferential statistical test, confidence interval, or hypothesis test is currently included in the evidence package.

Accordingly, the present findings should be interpreted as descriptive and comparative rather than as statistically significant evidence of superiority over a baseline system.

## 6. Discussion

The results indicate heterogeneous contribution across the evaluated CRME components.

The decisions component showed the largest observed aggregate degradation (52.08), whereas artifacts showed the lowest observed aggregate degradation (9.38).

This pattern suggests that the evaluated components do not contribute equally to the measured performance profile.

However, the observed ranking should be understood as empirical comparative evidence rather than definitive causal estimates.

## 7. Threats to Validity

Several limitations should be considered when interpreting the reported findings.

First, the current evidence package does not include inferential statistical testing or confidence interval estimation.

Second, the ablation results provide comparative evidence of component contribution but do not establish definitive causal importance.

Third, the reported evaluation is based on the currently available datasets and evaluation configurations.

Generalization to other datasets and research workflows requires further validation.

## 8. Reproducibility

All reported results are derived from stored CRME evaluation artifacts.

The evaluation pipeline preserves the relationship between raw evidence, aggregated summaries, paper tables, figures, and claim-level evidence.

The Q1 consistency audit completed with overall status `PASS`.

Raw evaluation outputs are preserved and are not modified by the paper generation layer.

## 9. Evidence Governance

The manuscript generation process is constrained by the available evaluation evidence.

Unsupported claims are not promoted to established findings.

Ablation results are interpreted as comparative contribution evidence rather than definitive causal estimates.

Claims of statistical significance are not made in the absence of inferential statistical evidence.

## 10. Conclusion

This evidence-backed evaluation establishes a reproducible descriptive baseline for CRME across the currently evaluated datasets and metrics.

The comparative and ablation results indicate heterogeneous observed contribution across the evaluated architectural components.

The current evidence supports comparative conclusions about the evaluated configurations, while stronger claims regarding statistical superiority or definitive causal importance require additional experimental and inferential validation.

## Evidence Artifacts

- `evaluation/results/final/evaluation_summary.json`
- `evaluation/results/final/paper/claim_audit/claim_evidence_matrix.json`
- `evaluation/results/final/paper/consistency_audit/q1_consistency_audit.json`
- `evaluation/results/final/paper/figures/component_contribution.csv`
- `evaluation/results/final/paper/figures/component_contribution_ranking.png`