# Label-maturity sensitivity

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}; 10 seeds. Same test commits in every variant. The oracle variant is a non-deployable diagnostic.

## Test metrics

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| audited (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| audited (reference) | LR (metrics only) | 0.431 ± 0.000 | 0.802 ± 0.000 | 0.427 ± 0.000 | 0.358 ± 0.000 | 0.550 ± 0.000 |
| audited (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| audited (reference) | RF (metrics only) | 0.408 ± 0.003 | 0.823 ± 0.001 | 0.381 ± 0.049 | 0.319 ± 0.036 | 0.607 ± 0.007 |
| audited (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| buffer 180 days | R-GCN | 0.401 ± 0.012 | 0.787 ± 0.007 | 0.374 ± 0.045 | 0.314 ± 0.026 | 0.544 ± 0.009 |
| buffer 180 days | LR (metrics only) | 0.431 ± 0.000 | 0.803 ± 0.000 | 0.424 ± 0.000 | 0.349 ± 0.000 | 0.557 ± 0.000 |
| buffer 180 days | LR (+neighbours) | 0.429 ± 0.000 | 0.796 ± 0.000 | 0.423 ± 0.000 | 0.345 ± 0.000 | 0.555 ± 0.000 |
| buffer 180 days | RF (metrics only) | 0.421 ± 0.002 | 0.825 ± 0.001 | 0.467 ± 0.012 | 0.381 ± 0.011 | 0.606 ± 0.005 |
| buffer 180 days | RF (+neighbours) | 0.419 ± 0.004 | 0.817 ± 0.001 | 0.441 ± 0.010 | 0.356 ± 0.008 | 0.584 ± 0.004 |
| buffer 365 days | R-GCN | 0.412 ± 0.009 | 0.794 ± 0.006 | 0.418 ± 0.025 | 0.336 ± 0.015 | 0.543 ± 0.006 |
| buffer 365 days | LR (metrics only) | 0.434 ± 0.000 | 0.804 ± 0.000 | 0.424 ± 0.000 | 0.349 ± 0.000 | 0.564 ± 0.000 |
| buffer 365 days | LR (+neighbours) | 0.425 ± 0.000 | 0.794 ± 0.000 | 0.418 ± 0.000 | 0.334 ± 0.000 | 0.550 ± 0.000 |
| buffer 365 days | RF (metrics only) | 0.422 ± 0.003 | 0.824 ± 0.001 | 0.461 ± 0.009 | 0.374 ± 0.009 | 0.598 ± 0.004 |
| buffer 365 days | RF (+neighbours) | 0.424 ± 0.003 | 0.818 ± 0.001 | 0.437 ± 0.008 | 0.355 ± 0.007 | 0.581 ± 0.004 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | R-GCN | 0.413 ± 0.007 | 0.791 ± 0.002 | 0.383 ± 0.045 | 0.327 ± 0.018 | 0.543 ± 0.008 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (metrics only) | 0.432 ± 0.000 | 0.803 ± 0.000 | 0.424 ± 0.000 | 0.347 ± 0.000 | 0.562 ± 0.000 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (+neighbours) | 0.426 ± 0.000 | 0.796 ± 0.000 | 0.418 ± 0.000 | 0.350 ± 0.000 | 0.557 ± 0.000 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (metrics only) | 0.419 ± 0.003 | 0.826 ± 0.001 | 0.386 ± 0.028 | 0.327 ± 0.018 | 0.595 ± 0.006 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (+neighbours) | 0.409 ± 0.004 | 0.812 ± 0.001 | 0.391 ± 0.028 | 0.322 ± 0.011 | 0.569 ± 0.003 |

## Change vs the audited reference (paired over seeds; ignore p-values for deterministic LR)

| variant | model | metric | mean_diff | seeds_higher | n_seeds | p_value |
|---|---|---|---|---|---|---|
| buffer 180 days | R-GCN | AUPRC | -0.0006 | 3 | 10 | 0.6953 |
| buffer 180 days | R-GCN | AUROC | -0.0007 | 5 | 10 | 0.7695 |
| buffer 180 days | R-GCN | R20 | 0.0037 | 5 | 10 | 0.5117 |
| buffer 180 days | LR (metrics only) | AUPRC | 0.0 | 10 | 10 | 0.002 |
| buffer 180 days | LR (metrics only) | AUROC | 0.0009 | 10 | 10 | 0.002 |
| buffer 180 days | LR (metrics only) | R20 | 0.0068 | 10 | 10 | 0.002 |
| buffer 180 days | LR (+neighbours) | AUPRC | 0.0029 | 10 | 10 | 0.002 |
| buffer 180 days | LR (+neighbours) | AUROC | 0.0007 | 10 | 10 | 0.002 |
| buffer 180 days | LR (+neighbours) | R20 | -0.0046 | 0 | 10 | 0.002 |
| buffer 180 days | RF (metrics only) | AUPRC | 0.0129 | 10 | 10 | 0.002 |
| buffer 180 days | RF (metrics only) | AUROC | 0.0015 | 10 | 10 | 0.002 |
| buffer 180 days | RF (metrics only) | R20 | -0.0011 | 3 | 10 | 0.6875 |
| buffer 180 days | RF (+neighbours) | AUPRC | 0.0227 | 10 | 10 | 0.002 |
| buffer 180 days | RF (+neighbours) | AUROC | 0.0103 | 10 | 10 | 0.002 |
| buffer 180 days | RF (+neighbours) | R20 | 0.0183 | 10 | 10 | 0.002 |
| buffer 365 days | R-GCN | AUPRC | 0.01 | 9 | 10 | 0.0273 |
| buffer 365 days | R-GCN | AUROC | 0.006 | 9 | 10 | 0.0488 |
| buffer 365 days | R-GCN | R20 | 0.0032 | 6 | 10 | 0.75 |
| buffer 365 days | LR (metrics only) | AUPRC | 0.0023 | 10 | 10 | 0.002 |
| buffer 365 days | LR (metrics only) | AUROC | 0.0017 | 10 | 10 | 0.002 |
| buffer 365 days | LR (metrics only) | R20 | 0.0137 | 10 | 10 | 0.002 |
| buffer 365 days | LR (+neighbours) | AUPRC | -0.0012 | 0 | 10 | 0.002 |
| buffer 365 days | LR (+neighbours) | AUROC | -0.0011 | 0 | 10 | 0.002 |
| buffer 365 days | LR (+neighbours) | R20 | -0.0091 | 0 | 10 | 0.002 |
| buffer 365 days | RF (metrics only) | AUPRC | 0.0142 | 10 | 10 | 0.002 |
| buffer 365 days | RF (metrics only) | AUROC | 0.0003 | 6 | 10 | 0.375 |
| buffer 365 days | RF (metrics only) | R20 | -0.0089 | 1 | 10 | 0.0117 |
| buffer 365 days | RF (+neighbours) | AUPRC | 0.0283 | 10 | 10 | 0.002 |
| buffer 365 days | RF (+neighbours) | AUROC | 0.0108 | 10 | 10 | 0.002 |
| buffer 365 days | RF (+neighbours) | R20 | 0.0144 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | R-GCN | AUPRC | 0.0109 | 9 | 10 | 0.0039 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | R-GCN | AUROC | 0.0034 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | R-GCN | R20 | 0.0034 | 6 | 10 | 0.707 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (metrics only) | AUPRC | 0.001 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (metrics only) | AUROC | 0.0015 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (metrics only) | R20 | 0.0114 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (+neighbours) | AUPRC | -0.0002 | 0 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (+neighbours) | AUROC | 0.0009 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | LR (+neighbours) | R20 | -0.0023 | 0 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (metrics only) | AUPRC | 0.0104 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (metrics only) | AUROC | 0.0027 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (metrics only) | R20 | -0.0116 | 1 | 10 | 0.0078 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (+neighbours) | AUPRC | 0.0127 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (+neighbours) | AUROC | 0.0054 | 10 | 10 | 0.002 |
| oracle drop of unobservable bugs [NON-DEPLOYABLE] | RF (+neighbours) | R20 | 0.0025 | 7 | 10 | 0.3359 |

## Rows used per variant

```json
{
  "audited (reference)": {
    "train_n": 11708,
    "train_pos_rate_used": 0.2771,
    "unobservable_buggy_still_in_train": 455,
    "val_n": 1672,
    "val_pos_rate_used": 0.0604,
    "test_n": 3346
  },
  "buffer 180 days": {
    "train_n": 10907,
    "train_pos_rate_used": 0.2947,
    "unobservable_buggy_still_in_train": 335,
    "val_n": 1034,
    "val_pos_rate_used": 0.0783,
    "test_n": 3346
  },
  "buffer 365 days": {
    "train_n": 10082,
    "train_pos_rate_used": 0.3095,
    "unobservable_buggy_still_in_train": 259,
    "val_n": 210,
    "val_pos_rate_used": 0.1095,
    "test_n": 3346
  },
  "oracle drop of unobservable bugs [NON-DEPLOYABLE]": {
    "train_n": 11253,
    "train_pos_rate_used": 0.2883,
    "unobservable_buggy_still_in_train": 0,
    "val_n": 1492,
    "val_pos_rate_used": 0.0677,
    "test_n": 3346
  }
}
```
