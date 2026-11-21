# Ablation results

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}; 10 seeds; one chronological audited split.

## A. Feature ablation

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| drop npt (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| drop npt (reference) | LR (metrics only) | 0.431 ± 0.000 | 0.802 ± 0.000 | 0.427 ± 0.000 | 0.358 ± 0.000 | 0.550 ± 0.000 |
| drop npt (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| drop npt (reference) | RF (metrics only) | 0.408 ± 0.003 | 0.823 ± 0.001 | 0.381 ± 0.049 | 0.319 ± 0.036 | 0.607 ± 0.007 |
| drop npt (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| drop fix (keep npt) | R-GCN | 0.412 ± 0.009 | 0.795 ± 0.003 | 0.299 ± 0.080 | 0.287 ± 0.045 | 0.545 ± 0.010 |
| drop fix (keep npt) | LR (metrics only) | 0.433 ± 0.000 | 0.805 ± 0.000 | 0.438 ± 0.000 | 0.351 ± 0.000 | 0.555 ± 0.000 |
| drop fix (keep npt) | LR (+neighbours) | 0.429 ± 0.000 | 0.798 ± 0.000 | 0.421 ± 0.000 | 0.345 ± 0.000 | 0.564 ± 0.000 |
| drop fix (keep npt) | RF (metrics only) | 0.410 ± 0.003 | 0.822 ± 0.001 | 0.358 ± 0.036 | 0.302 ± 0.021 | 0.601 ± 0.006 |
| drop fix (keep npt) | RF (+neighbours) | 0.400 ± 0.005 | 0.808 ± 0.001 | 0.372 ± 0.045 | 0.311 ± 0.020 | 0.566 ± 0.005 |
| drop fix + npt | R-GCN | 0.411 ± 0.007 | 0.793 ± 0.004 | 0.252 ± 0.040 | 0.267 ± 0.025 | 0.543 ± 0.010 |
| drop fix + npt | LR (metrics only) | 0.432 ± 0.000 | 0.804 ± 0.000 | 0.420 ± 0.000 | 0.350 ± 0.000 | 0.555 ± 0.000 |
| drop fix + npt | LR (+neighbours) | 0.428 ± 0.000 | 0.797 ± 0.000 | 0.414 ± 0.000 | 0.341 ± 0.000 | 0.564 ± 0.000 |
| drop fix + npt | RF (metrics only) | 0.411 ± 0.004 | 0.822 ± 0.001 | 0.356 ± 0.021 | 0.303 ± 0.013 | 0.605 ± 0.006 |
| drop fix + npt | RF (+neighbours) | 0.396 ± 0.003 | 0.806 ± 0.001 | 0.336 ± 0.053 | 0.289 ± 0.030 | 0.561 ± 0.004 |

## B. Graph ablation (features: drop npt)

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| full graph (reference) | R-GCN | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| full graph (reference) | LR (metrics only) | 0.431 ± 0.000 | 0.802 ± 0.000 | 0.427 ± 0.000 | 0.358 ± 0.000 | 0.550 ± 0.000 |
| full graph (reference) | LR (+neighbours) | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| full graph (reference) | RF (metrics only) | 0.408 ± 0.003 | 0.823 ± 0.001 | 0.381 ± 0.049 | 0.319 ± 0.036 | 0.607 ± 0.007 |
| full graph (reference) | RF (+neighbours) | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| remove same_author | R-GCN | 0.411 ± 0.015 | 0.795 ± 0.008 | 0.322 ± 0.057 | 0.296 ± 0.033 | 0.551 ± 0.013 |
| remove same_author | LR (+neighbours) | 0.432 ± 0.000 | 0.798 ± 0.000 | 0.428 ± 0.000 | 0.353 ± 0.000 | 0.559 ± 0.000 |
| remove same_author | RF (+neighbours) | 0.400 ± 0.003 | 0.809 ± 0.001 | 0.354 ± 0.060 | 0.302 ± 0.033 | 0.562 ± 0.004 |
| remove same_file | R-GCN | 0.404 ± 0.005 | 0.789 ± 0.003 | 0.336 ± 0.021 | 0.305 ± 0.013 | 0.546 ± 0.009 |
| remove same_file | LR (+neighbours) | 0.420 ± 0.000 | 0.800 ± 0.000 | 0.427 ± 0.000 | 0.345 ± 0.000 | 0.559 ± 0.000 |
| remove same_file | RF (+neighbours) | 0.385 ± 0.004 | 0.806 ± 0.001 | 0.254 ± 0.022 | 0.230 ± 0.016 | 0.570 ± 0.004 |
| remove same_author_same_file | R-GCN | 0.398 ± 0.007 | 0.789 ± 0.002 | 0.320 ± 0.050 | 0.303 ± 0.026 | 0.536 ± 0.007 |
| remove same_author_same_file | LR (+neighbours) | 0.424 ± 0.000 | 0.796 ± 0.000 | 0.422 ± 0.000 | 0.345 ± 0.000 | 0.559 ± 0.000 |
| remove same_author_same_file | RF (+neighbours) | 0.395 ± 0.003 | 0.806 ± 0.001 | 0.331 ± 0.049 | 0.292 ± 0.025 | 0.563 ± 0.004 |
| remove all edges | R-GCN | 0.421 ± 0.010 | 0.811 ± 0.002 | 0.360 ± 0.031 | 0.322 ± 0.017 | 0.561 ± 0.008 |
| remove all edges | LR (+neighbours) | 0.427 ± 0.000 | 0.799 ± 0.000 | 0.432 ± 0.000 | 0.358 ± 0.000 | 0.555 ± 0.000 |
| remove all edges | RF (+neighbours) | 0.390 ± 0.003 | 0.806 ± 0.001 | 0.326 ± 0.077 | 0.278 ± 0.046 | 0.570 ± 0.009 |
| shuffled edges (past-only) | R-GCN | 0.400 ± 0.010 | 0.787 ± 0.004 | 0.363 ± 0.056 | 0.311 ± 0.022 | 0.544 ± 0.011 |
| shuffled edges (past-only) | LR (+neighbours) | 0.419 ± 0.001 | 0.799 ± 0.000 | 0.423 ± 0.002 | 0.342 ± 0.003 | 0.555 ± 0.002 |
| shuffled edges (past-only) | RF (+neighbours) | 0.390 ± 0.005 | 0.810 ± 0.002 | 0.289 ± 0.036 | 0.256 ± 0.023 | 0.572 ± 0.005 |
| single-relation GCN (merged edges) | GCN (single relation) | 0.413 ± 0.008 | 0.791 ± 0.009 | 0.307 ± 0.057 | 0.296 ± 0.028 | 0.545 ± 0.003 |

## Change vs reference (paired over seeds, headline metrics)

| variant | model | vs | metric | mean_diff | seeds_lower | n_seeds | p_value |
|---|---|---|---|---|---|---|---|
| drop fix (keep npt) | R-GCN | R-GCN @ drop npt (reference) | AUPRC | 0.0101 | 1 | 10 | 0.0195 |
| drop fix (keep npt) | R-GCN | R-GCN @ drop npt (reference) | AUROC | 0.0068 | 0 | 10 | 0.002 |
| drop fix (keep npt) | R-GCN | R-GCN @ drop npt (reference) | R20 | 0.0053 | 4 | 10 | 0.3711 |
| drop fix (keep npt) | LR (metrics only) | LR (metrics only) @ drop npt (reference) | AUPRC | 0.0014 | 0 | 10 | 0.002 |
| drop fix (keep npt) | LR (metrics only) | LR (metrics only) @ drop npt (reference) | AUROC | 0.0032 | 0 | 10 | 0.002 |
| drop fix (keep npt) | LR (metrics only) | LR (metrics only) @ drop npt (reference) | R20 | 0.0046 | 0 | 10 | 0.002 |
| drop fix (keep npt) | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | AUPRC | 0.0031 | 0 | 10 | 0.002 |
| drop fix (keep npt) | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | AUROC | 0.0032 | 0 | 10 | 0.002 |
| drop fix (keep npt) | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | R20 | 0.0046 | 0 | 10 | 0.002 |
| drop fix (keep npt) | RF (metrics only) | RF (metrics only) @ drop npt (reference) | AUPRC | 0.0022 | 2 | 10 | 0.1934 |
| drop fix (keep npt) | RF (metrics only) | RF (metrics only) @ drop npt (reference) | AUROC | -0.0011 | 10 | 10 | 0.002 |
| drop fix (keep npt) | RF (metrics only) | RF (metrics only) @ drop npt (reference) | R20 | -0.0059 | 8 | 10 | 0.0117 |
| drop fix (keep npt) | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | AUPRC | 0.0043 | 2 | 10 | 0.1602 |
| drop fix (keep npt) | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | AUROC | 0.0017 | 0 | 10 | 0.002 |
| drop fix (keep npt) | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | R20 | 0.0002 | 5 | 10 | 0.7852 |
| drop fix + npt | R-GCN | R-GCN @ drop npt (reference) | AUPRC | 0.0095 | 2 | 10 | 0.0098 |
| drop fix + npt | R-GCN | R-GCN @ drop npt (reference) | AUROC | 0.0048 | 0 | 10 | 0.002 |
| drop fix + npt | R-GCN | R-GCN @ drop npt (reference) | R20 | 0.0027 | 4 | 10 | 0.2988 |
| drop fix + npt | LR (metrics only) | LR (metrics only) @ drop npt (reference) | AUPRC | 0.0012 | 0 | 10 | 0.002 |
| drop fix + npt | LR (metrics only) | LR (metrics only) @ drop npt (reference) | AUROC | 0.0021 | 0 | 10 | 0.002 |
| drop fix + npt | LR (metrics only) | LR (metrics only) @ drop npt (reference) | R20 | 0.0046 | 0 | 10 | 0.002 |
| drop fix + npt | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | AUPRC | 0.0015 | 0 | 10 | 0.002 |
| drop fix + npt | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | AUROC | 0.0024 | 0 | 10 | 0.002 |
| drop fix + npt | LR (+neighbours) | LR (+neighbours) @ drop npt (reference) | R20 | 0.0046 | 0 | 10 | 0.002 |
| drop fix + npt | RF (metrics only) | RF (metrics only) @ drop npt (reference) | AUPRC | 0.0024 | 4 | 10 | 0.2324 |
| drop fix + npt | RF (metrics only) | RF (metrics only) @ drop npt (reference) | AUROC | -0.0009 | 7 | 10 | 0.0488 |
| drop fix + npt | RF (metrics only) | RF (metrics only) @ drop npt (reference) | R20 | -0.0018 | 6 | 10 | 0.4297 |
| drop fix + npt | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | AUPRC | -0.0002 | 5 | 10 | 1.0 |
| drop fix + npt | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | AUROC | -0.0009 | 8 | 10 | 0.1055 |
| drop fix + npt | RF (+neighbours) | RF (+neighbours) @ drop npt (reference) | R20 | -0.0055 | 7 | 10 | 0.0234 |
| remove same_author | R-GCN | R-GCN @ full graph (reference) | AUPRC | 0.0087 | 4 | 10 | 0.1934 |
| remove same_author | R-GCN | R-GCN @ full graph (reference) | AUROC | 0.0072 | 2 | 10 | 0.0645 |
| remove same_author | R-GCN | R-GCN @ full graph (reference) | R20 | 0.0107 | 2 | 10 | 0.1309 |
| remove same_author | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUPRC | 0.0054 | 0 | 10 | 0.002 |
| remove same_author | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUROC | 0.0028 | 0 | 10 | 0.002 |
| remove same_author | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | R20 | 0.0 | 0 | 10 | 1.0 |
| remove same_author | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUPRC | 0.0043 | 2 | 10 | 0.0195 |
| remove same_author | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUROC | 0.0027 | 0 | 10 | 0.002 |
| remove same_author | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | R20 | -0.0041 | 8 | 10 | 0.0391 |
| remove same_file | R-GCN | R-GCN @ full graph (reference) | AUPRC | 0.0025 | 3 | 10 | 0.4316 |
| remove same_file | R-GCN | R-GCN @ full graph (reference) | AUROC | 0.0008 | 4 | 10 | 0.4922 |
| remove same_file | R-GCN | R-GCN @ full graph (reference) | R20 | 0.0064 | 3 | 10 | 0.334 |
| remove same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUPRC | -0.006 | 10 | 10 | 0.002 |
| remove same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUROC | 0.0045 | 0 | 10 | 0.002 |
| remove same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | R20 | 0.0 | 0 | 10 | 1.0 |
| remove same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUPRC | -0.0113 | 10 | 10 | 0.002 |
| remove same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUROC | -0.0007 | 6 | 10 | 0.375 |
| remove same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | R20 | 0.0039 | 3 | 10 | 0.1836 |
| remove same_author_same_file | R-GCN | R-GCN @ full graph (reference) | AUPRC | -0.0043 | 6 | 10 | 0.4316 |
| remove same_author_same_file | R-GCN | R-GCN @ full graph (reference) | AUROC | 0.0008 | 4 | 10 | 0.7695 |
| remove same_author_same_file | R-GCN | R-GCN @ full graph (reference) | R20 | -0.0037 | 5 | 10 | 0.4922 |
| remove same_author_same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUPRC | -0.0023 | 10 | 10 | 0.002 |
| remove same_author_same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUROC | 0.0007 | 0 | 10 | 0.002 |
| remove same_author_same_file | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | R20 | 0.0 | 0 | 10 | 1.0 |
| remove same_author_same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUPRC | -0.0006 | 5 | 10 | 0.7695 |
| remove same_author_same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUROC | -0.0006 | 7 | 10 | 0.2324 |
| remove same_author_same_file | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | R20 | -0.0027 | 5 | 10 | 0.2969 |
| remove all edges | R-GCN | R-GCN @ full graph (reference) | AUPRC | 0.0186 | 0 | 10 | 0.002 |
| remove all edges | R-GCN | R-GCN @ full graph (reference) | AUROC | 0.0229 | 0 | 10 | 0.002 |
| remove all edges | R-GCN | R-GCN @ full graph (reference) | R20 | 0.0205 | 0 | 10 | 0.002 |
| remove all edges | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUPRC | 0.0006 | 0 | 10 | 0.002 |
| remove all edges | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUROC | 0.0041 | 0 | 10 | 0.002 |
| remove all edges | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | R20 | -0.0046 | 10 | 10 | 0.002 |
| remove all edges | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUPRC | -0.0062 | 9 | 10 | 0.0059 |
| remove all edges | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUROC | -0.0008 | 8 | 10 | 0.1055 |
| remove all edges | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | R20 | 0.0037 | 3 | 10 | 0.2656 |
| shuffled edges (past-only) | R-GCN | R-GCN @ full graph (reference) | AUPRC | -0.0016 | 5 | 10 | 0.9219 |
| shuffled edges (past-only) | R-GCN | R-GCN @ full graph (reference) | AUROC | -0.0013 | 6 | 10 | 0.6953 |
| shuffled edges (past-only) | R-GCN | R-GCN @ full graph (reference) | R20 | 0.0037 | 5 | 10 | 0.7695 |
| shuffled edges (past-only) | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUPRC | -0.0074 | 10 | 10 | 0.002 |
| shuffled edges (past-only) | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | AUROC | 0.0036 | 0 | 10 | 0.002 |
| shuffled edges (past-only) | LR (+neighbours) | LR (+neighbours) @ full graph (reference) | R20 | -0.0046 | 10 | 10 | 0.002 |
| shuffled edges (past-only) | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUPRC | -0.0064 | 9 | 10 | 0.0371 |
| shuffled edges (past-only) | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | AUROC | 0.0031 | 0 | 10 | 0.002 |
| shuffled edges (past-only) | RF (+neighbours) | RF (+neighbours) @ full graph (reference) | R20 | 0.0059 | 1 | 10 | 0.0156 |
| single-relation GCN (merged edges) | GCN (single relation) | R-GCN @ full graph (reference) | AUPRC | 0.0108 | 3 | 10 | 0.0273 |
| single-relation GCN (merged edges) | GCN (single relation) | R-GCN @ full graph (reference) | AUROC | 0.0026 | 2 | 10 | 0.4316 |
| single-relation GCN (merged edges) | GCN (single relation) | R-GCN @ full graph (reference) | R20 | 0.0055 | 4 | 10 | 0.332 |
