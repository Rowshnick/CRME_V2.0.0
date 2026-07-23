## Table 1. Benchmark Comparison
| Method | KOS | DTS | RSR |
|---|---:|---:|---:|
| Flat File Memory | 0.0 | 0.0 | 0.0 |
| Structured Documentation | 0.4 | 0.5 | 0.6 |
| CRME | 1.0 | 1.0 | 1.0 |

## Table 2. Ablation Study
| Variant | CRT | KOS | DTS | RSR |
|---|---:|---:|---:|---:|
| CRME-Full | 5.0 | 1.0 | 1.0 | 1.0 |
| CRME-NoGraph | 5.0 | 0.0 | 1.0 | 1.0 |
| CRME-NoSession | 0 | 1.0 | 1.0 | 1.0 |
| CRME-NoArtifact | 5.0 | 1.0 | 1.0 | 0 |

## Table 3. Scalability Evaluation
| Dataset | Objects | Sessions | Relations | Mean Time(s) | Std |
|---|---:|---:|---:|---:|---:|
| Small | 50 | 10 | 100 | 8.43e-06 | 8.4e-07 |
| Medium | 500 | 100 | 1000 | 0.00016264 | 0.00017825 |
| Large | 5000 | 1000 | 10000 | 0.00079439 | 1.36e-05 |
