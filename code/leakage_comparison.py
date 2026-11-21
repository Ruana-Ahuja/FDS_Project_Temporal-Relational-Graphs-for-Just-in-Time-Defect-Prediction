"""
leakage_comparison.py  --  quantitative leakage evidence with the FINAL configuration
(uses jit_temporal_audit.py unchanged)

Run from the project root:
    python leakage_comparison.py --quick     # 3 seeds
    python leakage_comparison.py             # 10 seeds

Same graph, same features (8 metrics, npt dropped, + 6 neighbour/author features) and the same fixed
hyperparameters in every condition. Only the labels / split change:

  1. chrono, audited labels   labels as they were KNOWN at each cutoff; neighbour bug-ratio counts a
                              neighbour as buggy only once its fixing commit exists   (our protocol)
  2. chrono, leaky labels     same chronological split, but FINAL labels in training/validation and in
                              the neighbour bug-ratio (what a careless pipeline does)
  3. random split, final      random 70/10/20 split per seed with final labels (the base paper's setup)

Conditions 1 and 2 share the same test commits, so their difference isolates label leakage.
Condition 3 has a different test set (random commits from all years), so compare it only qualitatively.

Outputs (results_leakage/):
    leakage_runs.csv, leakage_summary.csv, leakage_delta.csv, leakage_audit.json, leakage_summary.md
"""
import argparse
import json
import os
from types import SimpleNamespace

import numpy as np
import pandas as pd
import torch
from scipy.stats import wilcoxon

import jit_temporal_audit as j

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

METRICS = ["AUPRC", "AUROC", "F1", "MCC", "R20"]
HEADLINE = ["AUPRC", "AUROC", "R20"]
CONDS = [("chrono, audited labels (ours)", "chrono", "audited"),
         ("chrono, leaky labels", "chrono", "leaky"),
         ("random split, final labels", "random", "leaky")]
REF = CONDS[0][0]


def summarise(runs):
    g = runs.groupby(["condition", "model"], sort=False)[METRICS].agg(["mean", "std"])
    flat = pd.DataFrame(index=g.index)
    for m in METRICS:
        flat[m + "_mean"] = g[(m, "mean")]
        flat[m + "_std"] = g[(m, "std")]
    return flat.reset_index()


def deltas(runs):
    rows = []
    for cond, _, _ in CONDS[1:]:
        for model in runs[runs.condition == cond].model.unique():
            a = runs[(runs.condition == cond) & (runs.model == model)].sort_values("seed")
            b = runs[(runs.condition == REF) & (runs.model == model)].sort_values("seed")
            for m in HEADLINE:
                d = a[m].values - b[m].values
                try:
                    pv = float(wilcoxon(a[m].values, b[m].values).pvalue)
                except Exception:
                    pv = float("nan")
                rows.append(dict(condition=cond, model=model, vs=REF, metric=m,
                                 mean_diff=round(float(d.mean()), 4), seeds_higher=int((d > 0).sum()),
                                 n_seeds=len(d), p_value=round(pv, 4)))
    return pd.DataFrame(rows)


def fmt_table(summary):
    out = pd.DataFrame({"condition": summary.condition, "model": summary.model})
    for m in METRICS:
        out[m] = [f"{a:.3f} ± {0 if np.isnan(b) else b:.3f}"
                  for a, b in zip(summary[m + "_mean"], summary[m + "_std"])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/HBase_input.csv")
    ap.add_argument("--gitmeta", default="data/HBase_gitmeta.csv")
    ap.add_argument("--mapping", default="data/HBase_mapping.csv")
    ap.add_argument("--outdir", default="results_leakage")
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    hp = dict(hidden=a.hidden, lr=a.lr, dropout=a.dropout)
    seeds = list(range(3 if a.quick else a.seeds))

    print("Loading data and building the past-only graph...")
    df, _ = j.load(SimpleNamespace(input=a.input, gitmeta=a.gitmeta, time="committer_ts"))
    ft, _ = j.label_times(df, a.mapping)
    n = len(df)
    E = j.build_edges(df)
    G = j.to_graph(E, n)
    metric_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    nb0 = len(j.BASE)

    rows, audit, cache = [], {"fixed_hyperparameters": hp, "seeds": seeds, "conditions": {}}, {}
    for label, split, mode in CONDS:
        print("\n###", label)
        for s in seeds:
            key = (split, mode)
            if split == "chrono" and key in cache:           # deterministic: compute once
                X, y, ye, S = cache[key]
            else:
                X, y, ye, S = j.prepare(df, E, ft, mode, split, s)
                if split == "chrono":
                    cache[key] = (X, y, ye, S)
            if s == seeds[0]:
                audit["conditions"][label] = {
                    "train_n": int(S["tr"].sum()), "val_n": int(S["va"].sum()), "test_n": int(S["te"].sum()),
                    "train_pos_rate_used_for_training": round(float(ye[S["tr"]].mean()), 4),
                    "val_pos_rate_used_for_threshold": round(float(ye[S["va"]].mean()), 4),
                    "test_pos_rate_final_labels": round(float(y[S["te"]].mean()), 4),
                    "train_buggy_relabelled_clean": int(((y == 1) & (ye == 0) & S["tr"]).sum()),
                }
            all_cols = metric_cols + list(range(nb0, X.shape[1]))
            base = dict(condition=label, seed=s)
            _, pb, ep = j.train_rgcn(X[:, all_cols], ye, G, S, hp, s)
            rows.append(dict(base, model="R-GCN", best_epoch=ep, **j.eval_probs(y, ye, pb, S)))
            for kind in ("LR", "RF"):
                for tag, cols in (("metrics only", metric_cols), ("+neighbours", all_cols)):
                    p = j.tabular(X, ye, S, kind, cols, s)
                    rows.append(dict(base, model=f"{kind} ({tag})", best_epoch=None, **j.eval_probs(y, ye, p, S)))
            print(f"  seed {s} done")

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(a.outdir, "leakage_runs.csv"), index=False)
    summary = summarise(runs)
    summary.to_csv(os.path.join(a.outdir, "leakage_summary.csv"), index=False)
    delta = deltas(runs)
    delta.to_csv(os.path.join(a.outdir, "leakage_delta.csv"), index=False)
    with open(os.path.join(a.outdir, "leakage_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    md = (f"# Leakage comparison\n\nFixed hyperparameters {hp}; {len(seeds)} seeds; features: drop npt + neighbour features.\n\n"
          "Conditions 1 and 2 share the same test commits. Condition 3 uses a different (random) test set.\n\n"
          "## Test metrics\n\n" + j.md(fmt_table(summary)) +
          "\n\n## Change vs chrono, audited labels (paired over seeds; ignore p-values for deterministic LR)\n\n" +
          j.md(delta) +
          "\n\n## Label statistics per condition\n\n```json\n" + json.dumps(audit["conditions"], indent=2) + "\n```\n")
    with open(os.path.join(a.outdir, "leakage_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()