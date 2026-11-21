"""Paired Wilcoxon tests: R-GCN vs each tabular baseline, per metric, over seeds.

Run from the project root:
    python paired_tests.py results_final_batched_edges/final_runs.csv
Writes paired_tests.csv next to the input file.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

path = sys.argv[1] if len(sys.argv) > 1 else "results_final_batched_edges/final_runs.csv"
runs = pd.read_csv(path)
runs["name"] = runs["model"] + " | " + runs["feature_set"]

REF = "R-GCN | 8_metrics_plus_neighbours"
METRICS = ["AUPRC", "AUROC", "R20"]          # threshold-free headline metrics
rows = []
for other in runs["name"].unique():
    if other == REF:
        continue
    for m in METRICS:
        a = runs[runs.name == REF].sort_values("seed")[m].values
        b = runs[runs.name == other].sort_values("seed")[m].values
        d = a - b
        try:
            p = float(wilcoxon(a, b).pvalue)
        except Exception:
            p = float("nan")
        rows.append(dict(
            comparison=f"R-GCN vs {other}",
            metric=m,
            mean_diff=round(float(d.mean()), 4),
            seeds_rgcn_higher=int((d > 0).sum()),
            n_seeds=len(d),
            p_value=round(p, 4),
        ))

out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv(os.path.join(os.path.dirname(path) or ".", "paired_tests.csv"), index=False)