# Extra ablations

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}; 10 seeds; features: drop npt.

## Graph depth

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| depth 1 | R-GCN | 0.403 ± 0.005 | 0.790 ± 0.003 | 0.290 ± 0.057 | 0.283 ± 0.026 | 0.545 ± 0.007 |
| depth 2 (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| depth 2 (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| depth 2 (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| depth 3 | R-GCN | 0.392 ± 0.016 | 0.784 ± 0.006 | 0.275 ± 0.067 | 0.265 ± 0.039 | 0.536 ± 0.012 |

## Neighbourhood size K

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| K=5 (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| K=5 (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| K=5 (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| K=1 | R-GCN | 0.389 ± 0.010 | 0.792 ± 0.003 | 0.332 ± 0.050 | 0.294 ± 0.027 | 0.548 ± 0.007 |
| K=1 | LR (+neighbours) | 0.424 ± 0.000 | 0.799 ± 0.000 | 0.433 ± 0.000 | 0.345 ± 0.000 | 0.550 ± 0.000 |
| K=1 | RF (+neighbours) | 0.388 ± 0.003 | 0.807 ± 0.001 | 0.303 ± 0.047 | 0.261 ± 0.024 | 0.570 ± 0.003 |
| K=3 | R-GCN | 0.401 ± 0.010 | 0.791 ± 0.003 | 0.288 ± 0.080 | 0.274 ± 0.039 | 0.543 ± 0.010 |
| K=3 | LR (+neighbours) | 0.435 ± 0.000 | 0.798 ± 0.000 | 0.434 ± 0.000 | 0.355 ± 0.000 | 0.564 ± 0.000 |
| K=3 | RF (+neighbours) | 0.403 ± 0.003 | 0.807 ± 0.001 | 0.361 ± 0.024 | 0.301 ± 0.013 | 0.568 ± 0.006 |
| K=10 | R-GCN | 0.424 ± 0.011 | 0.798 ± 0.003 | 0.351 ± 0.048 | 0.319 ± 0.025 | 0.543 ± 0.010 |
| K=10 | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.416 ± 0.000 | 0.346 ± 0.000 | 0.550 ± 0.000 |
| K=10 | RF (+neighbours) | 0.377 ± 0.001 | 0.808 ± 0.001 | 0.390 ± 0.033 | 0.318 ± 0.020 | 0.570 ± 0.006 |
| K=20 | R-GCN | 0.420 ± 0.011 | 0.798 ± 0.004 | 0.372 ± 0.049 | 0.322 ± 0.023 | 0.552 ± 0.013 |
| K=20 | LR (+neighbours) | 0.428 ± 0.000 | 0.796 ± 0.000 | 0.419 ± 0.000 | 0.339 ± 0.000 | 0.568 ± 0.000 |
| K=20 | RF (+neighbours) | 0.389 ± 0.002 | 0.801 ± 0.000 | 0.399 ± 0.036 | 0.323 ± 0.017 | 0.564 ± 0.006 |

## Temporal constraint (variants marked NON-DEPLOYABLE are diagnostic controls only)

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| past-only (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| past-only (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| past-only (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | R-GCN | 0.403 ± 0.012 | 0.796 ± 0.002 | 0.330 ± 0.042 | 0.290 ± 0.023 | 0.548 ± 0.013 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | LR (+neighbours) | 0.449 ± 0.000 | 0.803 ± 0.000 | 0.422 ± 0.000 | 0.367 ± 0.000 | 0.571 ± 0.000 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | RF (+neighbours) | 0.393 ± 0.002 | 0.810 ± 0.001 | 0.325 ± 0.029 | 0.280 ± 0.017 | 0.568 ± 0.004 |
| future edges + final labels [NON-DEPLOYABLE] | R-GCN | 0.718 ± 0.011 | 0.926 ± 0.004 | 0.655 ± 0.011 | 0.603 ± 0.013 | 0.784 ± 0.008 |
| future edges + final labels [NON-DEPLOYABLE] | LR (+neighbours) | 0.488 ± 0.000 | 0.831 ± 0.000 | 0.482 ± 0.000 | 0.396 ± 0.000 | 0.605 ± 0.000 |
| future edges + final labels [NON-DEPLOYABLE] | RF (+neighbours) | 0.454 ± 0.004 | 0.833 ± 0.001 | 0.476 ± 0.007 | 0.394 ± 0.009 | 0.611 ± 0.004 |

## Change vs reference (paired over seeds)

| variant | model | vs | metric | mean_diff | seeds_lower | n_seeds | p_value |
|---|---|---|---|---|---|---|---|
| depth 1 | R-GCN | depth 2 (reference) | AUPRC | 0.0009 | 3 | 10 | 0.5566 |
| depth 1 | R-GCN | depth 2 (reference) | AUROC | 0.0023 | 1 | 10 | 0.0645 |
| depth 1 | R-GCN | depth 2 (reference) | R20 | 0.0048 | 3 | 10 | 0.4062 |
| depth 3 | R-GCN | depth 2 (reference) | AUPRC | -0.0096 | 6 | 10 | 0.1309 |
| depth 3 | R-GCN | depth 2 (reference) | AUROC | -0.0037 | 8 | 10 | 0.084 |
| depth 3 | R-GCN | depth 2 (reference) | R20 | -0.0039 | 4 | 10 | 0.6094 |
| K=1 | R-GCN | K=5 (reference) | AUPRC | -0.0132 | 9 | 10 | 0.0039 |
| K=1 | R-GCN | K=5 (reference) | AUROC | 0.0037 | 1 | 10 | 0.0488 |
| K=1 | R-GCN | K=5 (reference) | R20 | 0.0084 | 3 | 10 | 0.1602 |
| K=1 | LR (+neighbours) | K=5 (reference) | AUPRC | -0.0021 | 10 | 10 | 0.002 |
| K=1 | LR (+neighbours) | K=5 (reference) | AUROC | 0.004 | 0 | 10 | 0.002 |
| K=1 | LR (+neighbours) | K=5 (reference) | R20 | -0.0091 | 10 | 10 | 0.002 |
| K=1 | RF (+neighbours) | K=5 (reference) | AUPRC | -0.0074 | 10 | 10 | 0.002 |
| K=1 | RF (+neighbours) | K=5 (reference) | AUROC | -0.0 | 5 | 10 | 1.0 |
| K=1 | RF (+neighbours) | K=5 (reference) | R20 | 0.0037 | 1 | 10 | 0.0273 |
| K=3 | R-GCN | K=5 (reference) | AUPRC | -0.0009 | 5 | 10 | 0.8457 |
| K=3 | R-GCN | K=5 (reference) | AUROC | 0.0029 | 2 | 10 | 0.084 |
| K=3 | R-GCN | K=5 (reference) | R20 | 0.0032 | 3 | 10 | 0.6426 |
| K=3 | LR (+neighbours) | K=5 (reference) | AUPRC | 0.0084 | 0 | 10 | 0.002 |
| K=3 | LR (+neighbours) | K=5 (reference) | AUROC | 0.003 | 0 | 10 | 0.002 |
| K=3 | LR (+neighbours) | K=5 (reference) | R20 | 0.0046 | 0 | 10 | 0.002 |
| K=3 | RF (+neighbours) | K=5 (reference) | AUPRC | 0.0076 | 0 | 10 | 0.002 |
| K=3 | RF (+neighbours) | K=5 (reference) | AUROC | 0.0001 | 6 | 10 | 1.0 |
| K=3 | RF (+neighbours) | K=5 (reference) | R20 | 0.0021 | 4 | 10 | 0.5078 |
| K=10 | R-GCN | K=5 (reference) | AUPRC | 0.0222 | 1 | 10 | 0.0059 |
| K=10 | R-GCN | K=5 (reference) | AUROC | 0.0097 | 0 | 10 | 0.002 |
| K=10 | R-GCN | K=5 (reference) | R20 | 0.0032 | 5 | 10 | 0.6445 |
| K=10 | LR (+neighbours) | K=5 (reference) | AUPRC | -0.0 | 10 | 10 | 0.002 |
| K=10 | LR (+neighbours) | K=5 (reference) | AUROC | -0.0005 | 10 | 10 | 0.002 |
| K=10 | LR (+neighbours) | K=5 (reference) | R20 | -0.0091 | 10 | 10 | 0.002 |
| K=10 | RF (+neighbours) | K=5 (reference) | AUPRC | -0.0186 | 10 | 10 | 0.002 |
| K=10 | RF (+neighbours) | K=5 (reference) | AUROC | 0.001 | 2 | 10 | 0.0645 |
| K=10 | RF (+neighbours) | K=5 (reference) | R20 | 0.0037 | 3 | 10 | 0.2422 |
| K=20 | R-GCN | K=5 (reference) | AUPRC | 0.0185 | 1 | 10 | 0.0039 |
| K=20 | R-GCN | K=5 (reference) | AUROC | 0.0098 | 1 | 10 | 0.0039 |
| K=20 | R-GCN | K=5 (reference) | R20 | 0.0121 | 3 | 10 | 0.1094 |
| K=20 | LR (+neighbours) | K=5 (reference) | AUPRC | 0.0018 | 0 | 10 | 0.002 |
| K=20 | LR (+neighbours) | K=5 (reference) | AUROC | 0.0009 | 0 | 10 | 0.002 |
| K=20 | LR (+neighbours) | K=5 (reference) | R20 | 0.0091 | 0 | 10 | 0.002 |
| K=20 | RF (+neighbours) | K=5 (reference) | AUPRC | -0.0073 | 10 | 10 | 0.002 |
| K=20 | RF (+neighbours) | K=5 (reference) | AUROC | -0.0055 | 10 | 10 | 0.002 |
| K=20 | RF (+neighbours) | K=5 (reference) | R20 | -0.0021 | 4 | 10 | 0.4688 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | AUPRC | 0.0009 | 6 | 10 | 1.0 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | AUROC | 0.0084 | 0 | 10 | 0.002 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | R20 | 0.0084 | 2 | 10 | 0.3105 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | AUPRC | 0.0226 | 0 | 10 | 0.002 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | AUROC | 0.0079 | 0 | 10 | 0.002 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | R20 | 0.0114 | 0 | 10 | 0.002 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | AUPRC | -0.0025 | 8 | 10 | 0.0645 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | AUROC | 0.0029 | 0 | 10 | 0.002 |
| future edges allowed, audited labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | R20 | 0.0018 | 3 | 10 | 0.4219 |
| future edges + final labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | AUPRC | 0.3163 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | AUROC | 0.1378 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | R-GCN | past-only (reference) | R20 | 0.2438 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | AUPRC | 0.0617 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | AUROC | 0.0354 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | LR (+neighbours) | past-only (reference) | R20 | 0.0457 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | AUPRC | 0.0585 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | AUROC | 0.0265 | 0 | 10 | 0.002 |
| future edges + final labels [NON-DEPLOYABLE] | RF (+neighbours) | past-only (reference) | R20 | 0.0443 | 0 | 10 | 0.002 |
