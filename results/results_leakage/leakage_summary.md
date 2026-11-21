# Leakage comparison

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}; 10 seeds; features: drop npt + neighbour features.

Conditions 1 and 2 share the same test commits. Condition 3 uses a different (random) test set.

## Test metrics

| condition | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| chrono, audited labels (ours) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| chrono, audited labels (ours) | LR (metrics only) | 0.431 ± 0.000 | 0.802 ± 0.000 | 0.427 ± 0.000 | 0.358 ± 0.000 | 0.550 ± 0.000 |
| chrono, audited labels (ours) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| chrono, audited labels (ours) | RF (metrics only) | 0.408 ± 0.003 | 0.823 ± 0.001 | 0.381 ± 0.049 | 0.319 ± 0.036 | 0.607 ± 0.007 |
| chrono, audited labels (ours) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| chrono, leaky labels | R-GCN | 0.450 ± 0.006 | 0.817 ± 0.002 | 0.453 ± 0.009 | 0.363 ± 0.011 | 0.573 ± 0.009 |
| chrono, leaky labels | LR (metrics only) | 0.433 ± 0.000 | 0.805 ± 0.000 | 0.444 ± 0.000 | 0.350 ± 0.000 | 0.566 ± 0.000 |
| chrono, leaky labels | LR (+neighbours) | 0.461 ± 0.000 | 0.821 ± 0.000 | 0.466 ± 0.000 | 0.377 ± 0.000 | 0.596 ± 0.000 |
| chrono, leaky labels | RF (metrics only) | 0.417 ± 0.003 | 0.829 ± 0.001 | 0.476 ± 0.004 | 0.389 ± 0.006 | 0.602 ± 0.006 |
| chrono, leaky labels | RF (+neighbours) | 0.444 ± 0.004 | 0.831 ± 0.001 | 0.473 ± 0.004 | 0.387 ± 0.006 | 0.597 ± 0.005 |
| random split, final labels | R-GCN | 0.712 ± 0.013 | 0.853 ± 0.006 | 0.650 ± 0.008 | 0.523 ± 0.009 | 0.553 ± 0.011 |
| random split, final labels | LR (metrics only) | 0.602 ± 0.014 | 0.796 ± 0.007 | 0.585 ± 0.011 | 0.423 ± 0.016 | 0.483 ± 0.010 |
| random split, final labels | LR (+neighbours) | 0.653 ± 0.012 | 0.830 ± 0.006 | 0.620 ± 0.009 | 0.472 ± 0.011 | 0.513 ± 0.008 |
| random split, final labels | RF (metrics only) | 0.658 ± 0.012 | 0.838 ± 0.007 | 0.621 ± 0.018 | 0.473 ± 0.026 | 0.516 ± 0.011 |
| random split, final labels | RF (+neighbours) | 0.711 ± 0.011 | 0.858 ± 0.005 | 0.648 ± 0.009 | 0.516 ± 0.014 | 0.547 ± 0.009 |

## Change vs chrono, audited labels (paired over seeds; ignore p-values for deterministic LR)

| condition | model | vs | metric | mean_diff | seeds_higher | n_seeds | p_value |
|---|---|---|---|---|---|---|---|
| chrono, leaky labels | R-GCN | chrono, audited labels (ours) | AUPRC | 0.0477 | 10 | 10 | 0.002 |
| chrono, leaky labels | R-GCN | chrono, audited labels (ours) | AUROC | 0.0292 | 10 | 10 | 0.002 |
| chrono, leaky labels | R-GCN | chrono, audited labels (ours) | R20 | 0.0333 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (metrics only) | chrono, audited labels (ours) | AUPRC | 0.0021 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (metrics only) | chrono, audited labels (ours) | AUROC | 0.0026 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (metrics only) | chrono, audited labels (ours) | R20 | 0.016 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (+neighbours) | chrono, audited labels (ours) | AUPRC | 0.0349 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (+neighbours) | chrono, audited labels (ours) | AUROC | 0.0259 | 10 | 10 | 0.002 |
| chrono, leaky labels | LR (+neighbours) | chrono, audited labels (ours) | R20 | 0.0365 | 10 | 10 | 0.002 |
| chrono, leaky labels | RF (metrics only) | chrono, audited labels (ours) | AUPRC | 0.0089 | 10 | 10 | 0.002 |
| chrono, leaky labels | RF (metrics only) | chrono, audited labels (ours) | AUROC | 0.0058 | 10 | 10 | 0.002 |
| chrono, leaky labels | RF (metrics only) | chrono, audited labels (ours) | R20 | -0.005 | 1 | 10 | 0.0312 |
| chrono, leaky labels | RF (+neighbours) | chrono, audited labels (ours) | AUPRC | 0.0484 | 10 | 10 | 0.002 |
| chrono, leaky labels | RF (+neighbours) | chrono, audited labels (ours) | AUROC | 0.0243 | 10 | 10 | 0.002 |
| chrono, leaky labels | RF (+neighbours) | chrono, audited labels (ours) | R20 | 0.0311 | 10 | 10 | 0.002 |
| random split, final labels | R-GCN | chrono, audited labels (ours) | AUPRC | 0.3101 | 10 | 10 | 0.002 |
| random split, final labels | R-GCN | chrono, audited labels (ours) | AUROC | 0.0654 | 10 | 10 | 0.002 |
| random split, final labels | R-GCN | chrono, audited labels (ours) | R20 | 0.0131 | 6 | 10 | 0.084 |
| random split, final labels | LR (metrics only) | chrono, audited labels (ours) | AUPRC | 0.1702 | 10 | 10 | 0.002 |
| random split, final labels | LR (metrics only) | chrono, audited labels (ours) | AUROC | -0.0061 | 2 | 10 | 0.0273 |
| random split, final labels | LR (metrics only) | chrono, audited labels (ours) | R20 | -0.0669 | 0 | 10 | 0.002 |
| random split, final labels | LR (+neighbours) | chrono, audited labels (ours) | AUPRC | 0.2269 | 10 | 10 | 0.002 |
| random split, final labels | LR (+neighbours) | chrono, audited labels (ours) | AUROC | 0.0347 | 10 | 10 | 0.002 |
| random split, final labels | LR (+neighbours) | chrono, audited labels (ours) | R20 | -0.0464 | 0 | 10 | 0.002 |
| random split, final labels | RF (metrics only) | chrono, audited labels (ours) | AUPRC | 0.2496 | 10 | 10 | 0.002 |
| random split, final labels | RF (metrics only) | chrono, audited labels (ours) | AUROC | 0.0145 | 10 | 10 | 0.002 |
| random split, final labels | RF (metrics only) | chrono, audited labels (ours) | R20 | -0.0906 | 0 | 10 | 0.002 |
| random split, final labels | RF (+neighbours) | chrono, audited labels (ours) | AUPRC | 0.3154 | 10 | 10 | 0.002 |
| random split, final labels | RF (+neighbours) | chrono, audited labels (ours) | AUROC | 0.0512 | 10 | 10 | 0.002 |
| random split, final labels | RF (+neighbours) | chrono, audited labels (ours) | R20 | -0.0192 | 1 | 10 | 0.0039 |

## Label statistics per condition

```json
{
  "chrono, audited labels (ours)": {
    "train_n": 11708,
    "val_n": 1672,
    "test_n": 3346,
    "train_pos_rate_used_for_training": 0.2771,
    "val_pos_rate_used_for_threshold": 0.0604,
    "test_pos_rate_final_labels": 0.1309,
    "train_buggy_relabelled_clean": 455
  },
  "chrono, leaky labels": {
    "train_n": 11708,
    "val_n": 1672,
    "test_n": 3346,
    "train_pos_rate_used_for_training": 0.3159,
    "val_pos_rate_used_for_threshold": 0.1681,
    "test_pos_rate_final_labels": 0.1309,
    "train_buggy_relabelled_clean": 0
  },
  "random split, final labels": {
    "train_n": 11708,
    "val_n": 1672,
    "test_n": 3346,
    "train_pos_rate_used_for_training": 0.2675,
    "val_pos_rate_used_for_threshold": 0.2506,
    "test_pos_rate_final_labels": 0.2591,
    "train_buggy_relabelled_clean": 0
  }
}
```
