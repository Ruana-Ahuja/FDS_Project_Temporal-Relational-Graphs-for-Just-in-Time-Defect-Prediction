# Neighbour-feature ablation

Fixed hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}; 10 seeds; metrics: drop npt.

## Feature-group ablation (full past-only graph)

| variant | model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|---|
| all neighbour features (reference) | R-GCN (full graph) | 0.402 ± 0.010 | 0.788 ± 0.003 | 0.311 ± 0.064 | 0.292 ± 0.035 | 0.540 ± 0.013 |
| all neighbour features (reference) | LR | 0.426 ± 0.000 | 0.795 ± 0.000 | 0.410 ± 0.000 | 0.339 ± 0.000 | 0.559 ± 0.000 |
| all neighbour features (reference) | RF | 0.396 ± 0.004 | 0.807 ± 0.001 | 0.343 ± 0.040 | 0.297 ± 0.021 | 0.566 ± 0.005 |
| drop author experience | R-GCN (full graph) | 0.401 ± 0.012 | 0.785 ± 0.007 | 0.369 ± 0.029 | 0.314 ± 0.016 | 0.543 ± 0.009 |
| drop author experience | LR | 0.423 ± 0.000 | 0.796 ± 0.000 | 0.415 ± 0.000 | 0.337 ± 0.000 | 0.559 ± 0.000 |
| drop author experience | RF | 0.418 ± 0.003 | 0.821 ± 0.001 | 0.385 ± 0.064 | 0.331 ± 0.034 | 0.599 ± 0.005 |
| drop degree features | R-GCN (full graph) | 0.392 ± 0.011 | 0.785 ± 0.004 | 0.286 ± 0.098 | 0.276 ± 0.054 | 0.533 ± 0.010 |
| drop degree features | LR | 0.433 ± 0.000 | 0.795 ± 0.000 | 0.418 ± 0.000 | 0.342 ± 0.000 | 0.550 ± 0.000 |
| drop degree features | RF | 0.397 ± 0.002 | 0.802 ± 0.001 | 0.397 ± 0.027 | 0.325 ± 0.013 | 0.558 ± 0.006 |
| drop past-bug ratio | R-GCN (full graph) | 0.397 ± 0.010 | 0.785 ± 0.006 | 0.304 ± 0.076 | 0.285 ± 0.039 | 0.527 ± 0.011 |
| drop past-bug ratio | LR | 0.419 ± 0.000 | 0.799 ± 0.000 | 0.424 ± 0.000 | 0.344 ± 0.000 | 0.555 ± 0.000 |
| drop past-bug ratio | RF | 0.387 ± 0.004 | 0.807 ± 0.001 | 0.295 ± 0.035 | 0.256 ± 0.020 | 0.572 ± 0.006 |
| past-bug ratio only | R-GCN (full graph) | 0.391 ± 0.014 | 0.781 ± 0.006 | 0.337 ± 0.054 | 0.302 ± 0.031 | 0.535 ± 0.005 |
| past-bug ratio only | LR | 0.437 ± 0.000 | 0.798 ± 0.000 | 0.435 ± 0.000 | 0.355 ± 0.000 | 0.571 ± 0.000 |
| past-bug ratio only | RF | 0.417 ± 0.002 | 0.822 ± 0.001 | 0.388 ± 0.023 | 0.326 ± 0.016 | 0.599 ± 0.006 |
| no neighbour features (metrics only) | R-GCN (full graph) | 0.389 ± 0.007 | 0.782 ± 0.002 | 0.312 ± 0.039 | 0.289 ± 0.021 | 0.534 ± 0.008 |
| no neighbour features (metrics only) | LR | 0.431 ± 0.000 | 0.802 ± 0.000 | 0.427 ± 0.000 | 0.358 ± 0.000 | 0.550 ± 0.000 |
| no neighbour features (metrics only) | RF | 0.408 ± 0.003 | 0.823 ± 0.001 | 0.381 ± 0.049 | 0.319 ± 0.036 | 0.607 ± 0.007 |

## Change vs reference (paired over seeds)

| variant | model | metric | mean_diff | seeds_lower | n_seeds | p_value |
|---|---|---|---|---|---|---|
| drop author experience | R-GCN (full graph) | AUPRC | -0.0008 | 5 | 10 | 0.7695 |
| drop author experience | R-GCN (full graph) | AUROC | -0.0033 | 5 | 10 | 0.375 |
| drop author experience | R-GCN (full graph) | R20 | 0.0034 | 5 | 10 | 0.543 |
| drop author experience | LR | AUPRC | -0.003 | 10 | 10 | 0.002 |
| drop author experience | LR | AUROC | 0.0013 | 0 | 10 | 0.002 |
| drop author experience | LR | R20 | 0.0 | 0 | 10 | 1.0 |
| drop author experience | RF | AUPRC | 0.0222 | 0 | 10 | 0.002 |
| drop author experience | RF | AUROC | 0.0147 | 0 | 10 | 0.002 |
| drop author experience | RF | R20 | 0.0324 | 0 | 10 | 0.002 |
| drop degree features | R-GCN (full graph) | AUPRC | -0.01 | 7 | 10 | 0.084 |
| drop degree features | R-GCN (full graph) | AUROC | -0.0027 | 8 | 10 | 0.0645 |
| drop degree features | R-GCN (full graph) | R20 | -0.0068 | 6 | 10 | 0.3164 |
| drop degree features | LR | AUPRC | 0.007 | 0 | 10 | 0.002 |
| drop degree features | LR | AUROC | -0.0002 | 10 | 10 | 0.002 |
| drop degree features | LR | R20 | -0.0091 | 10 | 10 | 0.002 |
| drop degree features | RF | AUPRC | 0.0011 | 2 | 10 | 0.3223 |
| drop degree features | RF | AUROC | -0.0047 | 10 | 10 | 0.002 |
| drop degree features | RF | R20 | -0.0087 | 9 | 10 | 0.0117 |
| drop past-bug ratio | R-GCN (full graph) | AUPRC | -0.0049 | 6 | 10 | 0.4922 |
| drop past-bug ratio | R-GCN (full graph) | AUROC | -0.0032 | 6 | 10 | 0.2324 |
| drop past-bug ratio | R-GCN (full graph) | R20 | -0.013 | 7 | 10 | 0.0488 |
| drop past-bug ratio | LR | AUPRC | -0.0078 | 10 | 10 | 0.002 |
| drop past-bug ratio | LR | AUROC | 0.0037 | 0 | 10 | 0.002 |
| drop past-bug ratio | LR | R20 | -0.0046 | 10 | 10 | 0.002 |
| drop past-bug ratio | RF | AUPRC | -0.0089 | 10 | 10 | 0.002 |
| drop past-bug ratio | RF | AUROC | 0.0006 | 4 | 10 | 0.3223 |
| drop past-bug ratio | RF | R20 | 0.0057 | 2 | 10 | 0.0391 |
| past-bug ratio only | R-GCN (full graph) | AUPRC | -0.0113 | 7 | 10 | 0.0371 |
| past-bug ratio only | R-GCN (full graph) | AUROC | -0.007 | 9 | 10 | 0.0273 |
| past-bug ratio only | R-GCN (full graph) | R20 | -0.0053 | 5 | 10 | 0.3516 |
| past-bug ratio only | LR | AUPRC | 0.0111 | 0 | 10 | 0.002 |
| past-bug ratio only | LR | AUROC | 0.0028 | 0 | 10 | 0.002 |
| past-bug ratio only | LR | R20 | 0.0114 | 0 | 10 | 0.002 |
| past-bug ratio only | RF | AUPRC | 0.0213 | 0 | 10 | 0.002 |
| past-bug ratio only | RF | AUROC | 0.0156 | 0 | 10 | 0.002 |
| past-bug ratio only | RF | R20 | 0.0324 | 0 | 10 | 0.002 |
| no neighbour features (metrics only) | R-GCN (full graph) | AUPRC | -0.0126 | 9 | 10 | 0.0059 |
| no neighbour features (metrics only) | R-GCN (full graph) | AUROC | -0.0059 | 9 | 10 | 0.0039 |
| no neighbour features (metrics only) | R-GCN (full graph) | R20 | -0.0062 | 6 | 10 | 0.3066 |
| no neighbour features (metrics only) | LR | AUPRC | 0.0049 | 0 | 10 | 0.002 |
| no neighbour features (metrics only) | LR | AUROC | 0.0069 | 0 | 10 | 0.002 |
| no neighbour features (metrics only) | LR | R20 | -0.0091 | 10 | 10 | 0.002 |
| no neighbour features (metrics only) | RF | AUPRC | 0.0123 | 0 | 10 | 0.002 |
| no neighbour features (metrics only) | RF | AUROC | 0.0165 | 0 | 10 | 0.002 |
| no neighbour features (metrics only) | RF | R20 | 0.0406 | 0 | 10 | 0.002 |

## Edge label homophily (descriptive; final labels)

| relation | edges | base_rate | P_target_buggy_given_src_buggy_final | P_target_buggy_given_src_buggy_and_known | P_target_buggy_given_src_clean | share_edges_src_known_buggy | P_src_known_buggy_year_matched | P_src_not_known_buggy_year_matched |
|---|---|---|---|---|---|---|---|---|
| same_author | 66855 | 0.2641 | 0.3108 | 0.2678 | 0.23 | 0.0158 | 0.2678 | 0.2357 |
| same_file | 64706 | 0.2641 | 0.2831 | 0.1269 | 0.2177 | 0.1371 | 0.1269 | 0.2395 |
| same_author_same_file | 12721 | 0.2641 | 0.5017 | 0.2835 | 0.2658 | 0.01 | 0.225 | 0.2977 |
| all relations | 144282 | 0.2641 | 0.3132 | 0.1436 | 0.2284 | 0.0696 | 0.1436 | 0.2336 |
