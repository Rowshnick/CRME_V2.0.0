# CRME Statistical Evaluation Engine v2

**Generated:** 2026-07-19T08:21:12.913970+00:00

## Governance

- Canonical evidence mutated: **NO**
- Read-only ingestion: **YES**
- Synthetic inference from single run: **NO**

## Evaluation Runs: 1

| Run ID | Dataset | Scenario | Configuration | Source |
|---|---|---|---|---|
| canonical-baseline-001 | crme_internal | canonical_evaluation | crme | canonical_evaluation_summary |

## Descriptive Statistics

| Metric | n | Mean | Median | Min | Max | Std |
|---|---:|---:|---:|---:|---:|---:|
| CES | 1 | 57.7100 | 57.7100 | 57.7100 | 57.7100 | N/A |
| KGQ | 1 | 40.0000 | 40.0000 | 40.0000 | 40.0000 | N/A |
| MCS | 1 | 47.5000 | 47.5000 | 47.5000 | 47.5000 | N/A |
| RRS | 1 | 43.3300 | 43.3300 | 43.3300 | 43.3300 | N/A |
| SRS | 1 | 100.0000 | 100.0000 | 100.0000 | 100.0000 | N/A |

## Bootstrap Confidence Intervals

Bootstrap intervals are descriptive when repeated observations are available. A single observation does not support valid inferential uncertainty estimation.

| Metric | Mean | Lower | Upper | Confidence |
|---|---:|---:|---:|---:|
| CES | 57.7100 | 57.7100 | 57.7100 | 0.95 |
| KGQ | 40.0000 | 40.0000 | 40.0000 | 0.95 |
| MCS | 47.5000 | 47.5000 | 47.5000 | 0.95 |
| RRS | 43.3300 | 43.3300 | 43.3300 | 0.95 |
| SRS | 100.0000 | 100.0000 | 100.0000 | 0.95 |

## Statistical Interpretation

The current engine separates descriptive analysis from inferential claims. A single canonical evaluation run is treated as a point estimate and does not justify statistical significance claims.

**Status:** `DESCRIPTIVE_ANALYSIS_READY`