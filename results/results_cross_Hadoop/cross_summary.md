# Cross-project replication: Hadoop

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2} (not re-tuned); 10 seeds. The random-split test set differs from the chronological one, so compare AUROC and within-protocol changes, not AUPRC levels.

## Test metrics

| condition | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| audited | R-GCN | 0.130 ± 0.012 | 0.591 ± 0.016 | 0.051 ± 0.038 | 0.004 ± 0.033 | 0.273 ± 0.036 |
| audited | LR (metrics only) | 0.156 ± 0.000 | 0.636 ± 0.000 | 0.059 ± 0.000 | 0.015 ± 0.000 | 0.364 ± 0.000 |
| audited | LR (+neighbours) | 0.137 ± 0.000 | 0.646 ± 0.000 | 0.050 ± 0.000 | -0.023 ± 0.000 | 0.299 ± 0.000 |
| audited | RF (metrics only) | 0.238 ± 0.006 | 0.697 ± 0.007 | 0.113 ± 0.023 | 0.152 ± 0.027 | 0.452 ± 0.015 |
| audited | RF (+neighbours) | 0.235 ± 0.007 | 0.692 ± 0.006 | 0.208 ± 0.029 | 0.191 ± 0.016 | 0.413 ± 0.016 |
| audited, no edges | R-GCN | 0.177 ± 0.008 | 0.701 ± 0.012 | 0.048 ± 0.031 | 0.022 ± 0.029 | 0.406 ± 0.012 |
| leaky | R-GCN | 0.183 ± 0.010 | 0.646 ± 0.018 | 0.212 ± 0.057 | 0.131 ± 0.036 | 0.377 ± 0.043 |
| leaky | LR (metrics only) | 0.181 ± 0.000 | 0.712 ± 0.000 | 0.187 ± 0.000 | 0.103 ± 0.000 | 0.416 ± 0.000 |
| leaky | LR (+neighbours) | 0.176 ± 0.000 | 0.723 ± 0.000 | 0.137 ± 0.000 | 0.051 ± 0.000 | 0.429 ± 0.000 |
| leaky | RF (metrics only) | 0.198 ± 0.005 | 0.708 ± 0.004 | 0.185 ± 0.015 | 0.117 ± 0.011 | 0.474 ± 0.020 |
| leaky | RF (+neighbours) | 0.228 ± 0.007 | 0.730 ± 0.006 | 0.218 ± 0.017 | 0.164 ± 0.014 | 0.495 ± 0.017 |
| random split | R-GCN | 0.217 ± 0.054 | 0.705 ± 0.045 | 0.253 ± 0.074 | 0.179 ± 0.071 | 0.453 ± 0.079 |
| random split | LR (metrics only) | 0.270 ± 0.044 | 0.810 ± 0.021 | 0.305 ± 0.102 | 0.248 ± 0.094 | 0.569 ± 0.036 |
| random split | LR (+neighbours) | 0.269 ± 0.046 | 0.800 ± 0.018 | 0.300 ± 0.083 | 0.235 ± 0.071 | 0.531 ± 0.032 |
| random split | RF (metrics only) | 0.368 ± 0.049 | 0.829 ± 0.022 | 0.372 ± 0.043 | 0.312 ± 0.041 | 0.606 ± 0.043 |
| random split | RF (+neighbours) | 0.371 ± 0.049 | 0.833 ± 0.024 | 0.396 ± 0.030 | 0.342 ± 0.030 | 0.631 ± 0.046 |

## Paired comparisons (ignore p-values for deterministic LR)

| comparison | metric | mean_diff | seeds_first_higher | n_seeds | p_value |
|---|---|---|---|---|---|
| audited: R-GCN minus LR (metrics only) | AUPRC | -0.0266 | 0 | 10 | 0.002 |
| audited: R-GCN minus LR (metrics only) | AUROC | -0.0441 | 0 | 10 | 0.002 |
| audited: R-GCN minus LR (metrics only) | R20 | -0.0909 | 0 | 10 | 0.002 |
| audited: R-GCN minus LR (+neighbours) | AUPRC | -0.0074 | 2 | 10 | 0.1055 |
| audited: R-GCN minus LR (+neighbours) | AUROC | -0.0545 | 0 | 10 | 0.002 |
| audited: R-GCN minus LR (+neighbours) | R20 | -0.026 | 2 | 10 | 0.0625 |
| audited: R-GCN minus RF (metrics only) | AUPRC | -0.1084 | 0 | 10 | 0.002 |
| audited: R-GCN minus RF (metrics only) | AUROC | -0.106 | 0 | 10 | 0.002 |
| audited: R-GCN minus RF (metrics only) | R20 | -0.1792 | 0 | 10 | 0.002 |
| audited: R-GCN minus RF (+neighbours) | AUPRC | -0.1055 | 0 | 10 | 0.002 |
| audited: R-GCN minus RF (+neighbours) | AUROC | -0.101 | 0 | 10 | 0.002 |
| audited: R-GCN minus RF (+neighbours) | R20 | -0.1403 | 0 | 10 | 0.002 |
| R-GCN: no edges minus full graph | AUPRC | 0.0469 | 10 | 10 | 0.002 |
| R-GCN: no edges minus full graph | AUROC | 0.1092 | 10 | 10 | 0.002 |
| R-GCN: no edges minus full graph | R20 | 0.1338 | 10 | 10 | 0.002 |
| R-GCN: leaky minus audited | AUPRC | 0.0535 | 10 | 10 | 0.002 |
| R-GCN: leaky minus audited | AUROC | 0.0544 | 10 | 10 | 0.002 |
| R-GCN: leaky minus audited | R20 | 0.1039 | 10 | 10 | 0.002 |
| LR (+neighbours): leaky minus audited | AUPRC | 0.039 | 10 | 10 | 0.002 |
| LR (+neighbours): leaky minus audited | AUROC | 0.0768 | 10 | 10 | 0.002 |
| LR (+neighbours): leaky minus audited | R20 | 0.1299 | 10 | 10 | 0.002 |
| RF (+neighbours): leaky minus audited | AUPRC | -0.0071 | 3 | 10 | 0.1309 |
| RF (+neighbours): leaky minus audited | AUROC | 0.0376 | 10 | 10 | 0.002 |
| RF (+neighbours): leaky minus audited | R20 | 0.0818 | 10 | 10 | 0.002 |
| LR (metrics only): leaky minus audited | AUPRC | 0.0247 | 10 | 10 | 0.002 |
| LR (metrics only): leaky minus audited | AUROC | 0.0765 | 10 | 10 | 0.002 |
| LR (metrics only): leaky minus audited | R20 | 0.0519 | 10 | 10 | 0.002 |
| RF (metrics only): leaky minus audited | AUPRC | -0.0406 | 0 | 10 | 0.002 |
| RF (metrics only): leaky minus audited | AUROC | 0.011 | 10 | 10 | 0.002 |
| RF (metrics only): leaky minus audited | R20 | 0.0221 | 8 | 10 | 0.0078 |
| R-GCN: random split minus audited | AUPRC | 0.0871 | 10 | 10 | 0.002 |
| R-GCN: random split minus audited | AUROC | 0.1138 | 10 | 10 | 0.002 |
| R-GCN: random split minus audited | R20 | 0.1801 | 10 | 10 | 0.002 |
| LR (+neighbours): random split minus audited | AUPRC | 0.1316 | 10 | 10 | 0.002 |
| LR (+neighbours): random split minus audited | AUROC | 0.1539 | 10 | 10 | 0.002 |
| LR (+neighbours): random split minus audited | R20 | 0.232 | 10 | 10 | 0.002 |
| RF (+neighbours): random split minus audited | AUPRC | 0.1362 | 10 | 10 | 0.002 |
| RF (+neighbours): random split minus audited | AUROC | 0.1409 | 10 | 10 | 0.002 |
| RF (+neighbours): random split minus audited | R20 | 0.2183 | 10 | 10 | 0.002 |

## Audit statistics

```json
{
  "project": "Hadoop",
  "end_date": "2011-12-31",
  "data": {
    "share_rows_ns==ndev==exp": 1.0,
    "nan_feature_cells": 71,
    "rows_input": 10509,
    "rows_after_merge": 10509,
    "dropped_no_time": 0,
    "time_source": "committer_ts"
  },
  "label_times": {
    "mapping_pairs": 1954,
    "pairs_with_fix_in_data": 1954,
    "buggy_commits": 548,
    "buggy_without_matched_fix": 0
  },
  "commits_used": 4009,
  "edges_per_relation": {
    "same_author": 15239,
    "same_file": 14713,
    "same_author_same_file": 4155
  },
  "total_edges": 34107,
  "future_edge_violations": {
    "same_author": 0,
    "same_file": 0,
    "same_author_same_file": 0
  },
  "split_sizes": {
    "tr": 2806,
    "va": 401,
    "te": 802
  },
  "pos_rate_final": {
    "tr": 0.087,
    "va": 0.0898,
    "te": 0.096
  },
  "pos_rate_known_at_cutoff": {
    "tr": 0.0495,
    "va": 0.0125,
    "te": 0.096
  },
  "train_buggy_relabelled_clean": 105,
  "order_ok": true,
  "fixed_hyperparameters": {
    "hidden": 32,
    "lr": 0.01,
    "dropout": 0.2
  },
  "seeds": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9
  ],
  "bug_label_delay_days": {
    "median": 238.7,
    "p90": 910.9
  }
}
```
