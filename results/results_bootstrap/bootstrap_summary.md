# Bootstrap confidence intervals

Audited chronological test set: 3346 commits, 438 buggy. Moving-block bootstrap (block 50), 1000 valid resamples, 10 seeds averaged per model; hyperparameters {'hidden': 32, 'lr': 0.01, 'dropout': 0.2}. 95% percentile intervals.

## Metrics

| model | metric | estimate | ci_low | ci_high |
|---|---|---|---|---|
| R-GCN | AUPRC | 0.4019 | 0.3404 | 0.4718 |
| R-GCN | AUROC | 0.788 | 0.7652 | 0.8111 |
| R-GCN | R20 | 0.54 | 0.5007 | 0.5787 |
| R-GCN (no edges) | AUPRC | 0.4205 | 0.3509 | 0.4933 |
| R-GCN (no edges) | AUROC | 0.8109 | 0.7888 | 0.8341 |
| R-GCN (no edges) | R20 | 0.5605 | 0.5207 | 0.6053 |
| LR (metrics only) | AUPRC | 0.4313 | 0.3617 | 0.5011 |
| LR (metrics only) | AUROC | 0.802 | 0.7787 | 0.8265 |
| LR (metrics only) | R20 | 0.5502 | 0.5135 | 0.5985 |
| LR (+neighbours) | AUPRC | 0.4264 | 0.3563 | 0.4971 |
| LR (+neighbours) | AUROC | 0.7951 | 0.7704 | 0.8208 |
| LR (+neighbours) | R20 | 0.5594 | 0.518 | 0.606 |
| RF (metrics only) | AUPRC | 0.4082 | 0.3382 | 0.4811 |
| RF (metrics only) | AUROC | 0.8232 | 0.8002 | 0.846 |
| RF (metrics only) | R20 | 0.6068 | 0.5559 | 0.653 |
| RF (+neighbours) | AUPRC | 0.3959 | 0.3245 | 0.4724 |
| RF (+neighbours) | AUROC | 0.8067 | 0.7816 | 0.8317 |
| RF (+neighbours) | R20 | 0.5662 | 0.5119 | 0.6221 |

## Paired differences (same resampled commits)

| difference | metric | estimate | ci_low | ci_high | share_resamples_positive | excludes_zero |
|---|---|---|---|---|---|---|
| R-GCN minus LR (metrics only) | AUPRC | -0.0294 | -0.0552 | -0.0003 | 0.024 | True |
| R-GCN minus LR (metrics only) | AUROC | -0.0139 | -0.0265 | -0.0009 | 0.017 | True |
| R-GCN minus LR (metrics only) | R20 | -0.0103 | -0.0417 | 0.0103 | 0.124 | False |
| R-GCN minus LR (+neighbours) | AUPRC | -0.0245 | -0.0464 | 0.0017 | 0.033 | False |
| R-GCN minus LR (+neighbours) | AUROC | -0.007 | -0.0177 | 0.0042 | 0.124 | False |
| R-GCN minus LR (+neighbours) | R20 | -0.0194 | -0.0502 | 0.0077 | 0.071 | False |
| R-GCN minus RF (metrics only) | AUPRC | -0.0063 | -0.0447 | 0.0311 | 0.379 | False |
| R-GCN minus RF (metrics only) | AUROC | -0.0352 | -0.0501 | -0.0209 | 0.0 | True |
| R-GCN minus RF (metrics only) | R20 | -0.0669 | -0.0947 | -0.0318 | 0.0 | True |
| R-GCN minus RF (+neighbours) | AUPRC | 0.006 | -0.0355 | 0.0459 | 0.597 | False |
| R-GCN minus RF (+neighbours) | AUROC | -0.0187 | -0.0331 | -0.0046 | 0.005 | True |
| R-GCN minus RF (+neighbours) | R20 | -0.0263 | -0.0578 | 0.0088 | 0.064 | False |
| R-GCN (no edges) minus R-GCN | AUPRC | 0.0186 | -0.0136 | 0.0494 | 0.875 | False |
| R-GCN (no edges) minus R-GCN | AUROC | 0.0229 | 0.0111 | 0.0338 | 1.0 | True |
| R-GCN (no edges) minus R-GCN | R20 | 0.0205 | -0.0062 | 0.0505 | 0.938 | False |
| RF (+neighbours) minus RF (metrics only) | AUPRC | -0.0123 | -0.0341 | 0.0116 | 0.164 | False |
| RF (+neighbours) minus RF (metrics only) | AUROC | -0.0165 | -0.0256 | -0.008 | 0.0 | True |
| RF (+neighbours) minus RF (metrics only) | R20 | -0.0406 | -0.0665 | -0.0114 | 0.002 | True |
| LR (+neighbours) minus LR (metrics only) | AUPRC | -0.0049 | -0.0176 | 0.0069 | 0.22 | False |
| LR (+neighbours) minus LR (metrics only) | AUROC | -0.0069 | -0.0133 | -0.001 | 0.012 | True |
| LR (+neighbours) minus LR (metrics only) | R20 | 0.0091 | -0.017 | 0.0277 | 0.645 | False |
