"""
bootstrap_ci.py  --  how much of the model differences could be test-sample noise?
(uses jit_temporal_audit.py unchanged)

Run from the project root:
    python3 bootstrap_ci.py --quick     # 3 seeds, 200 resamples
    python3 bootstrap_ci.py             # 10 seeds, 1000 resamples

Final audited configuration (8 metrics + 6 neighbour features, fixed hyperparameters). For every model the
test-set predictions of all seeds are kept. Test commits are then resampled with a MOVING-BLOCK bootstrap
(contiguous blocks of commits, default 50) so that the temporal dependence between neighbouring commits is
respected. In each resample every model's metric is averaged over its seeds, and paired differences use the
SAME resampled commits. The intervals therefore capture test-sample uncertainty, which the seed standard
deviations do not (and LR has no seed variance at all).

Outputs (results_bootstrap/): bootstrap_ci.csv, bootstrap_diff.csv, bootstrap_summary.md
"""
import argparse
import os
from types import SimpleNamespace

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

import jit_temporal_audit as j

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

NAMES = ["AUPRC", "AUROC", "R20"]
MODELS = ["R-GCN", "R-GCN (no edges)", "LR (metrics only)", "LR (+neighbours)",
          "RF (metrics only)", "RF (+neighbours)"]
PAIRS = [("R-GCN", "LR (metrics only)"), ("R-GCN", "LR (+neighbours)"),
         ("R-GCN", "RF (metrics only)"), ("R-GCN", "RF (+neighbours)"),
         ("R-GCN (no edges)", "R-GCN"), ("RF (+neighbours)", "RF (metrics only)"),
         ("LR (+neighbours)", "LR (metrics only)")]


def metrics(yt, pt):
    k = max(1, int(0.2 * len(yt)))
    top = np.argsort(-pt)[:k]
    return np.array([average_precision_score(yt, pt), roc_auc_score(yt, pt), yt[top].sum() / max(yt.sum(), 1)])


def block_indices(n, block, rng):
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, nb, size=nb) * block
    idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])
    return idx[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/HBase_input.csv")
    ap.add_argument("--gitmeta", default="data/HBase_gitmeta.csv")
    ap.add_argument("--mapping", default="data/HBase_mapping.csv")
    ap.add_argument("--outdir", default="results_bootstrap")
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--B", type=int, default=1000, help="bootstrap resamples")
    ap.add_argument("--block", type=int, default=50, help="block length (1 = ordinary bootstrap)")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    hp = dict(hidden=a.hidden, lr=a.lr, dropout=a.dropout)
    seeds = list(range(3 if a.quick else a.seeds))
    B = 200 if a.quick else a.B

    print("Loading data and building the past-only graph...")
    df, _ = j.load(SimpleNamespace(input=a.input, gitmeta=a.gitmeta, time="committer_ts"))
    ft, _ = j.label_times(df, a.mapping)
    n = len(df)
    E = j.build_edges(df)
    G = j.to_graph(E, n)
    X, y, ye, S = j.prepare(df, E, ft, "audited")
    E0 = {r: np.empty((0, 2), dtype=np.int64) for r in j.RELS}
    G0 = j.to_graph(E0, n)
    X0, y0, ye0, S0 = j.prepare(df, E0, ft, "audited")
    metric_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    all_cols = metric_cols + list(range(len(j.BASE), X.shape[1]))
    te = S["te"]
    y_te = y[te]
    print(f"Test commits: {int(te.sum())}, buggy: {int(y_te.sum())}")

    preds = {m: [] for m in MODELS}
    for s in seeds:
        print(f"training seed {s}")
        _, pb, _ = j.train_rgcn(X[:, all_cols], ye, G, S, hp, s)
        preds["R-GCN"].append(pb[te])
        _, pb0, _ = j.train_rgcn(X0[:, all_cols], ye0, G0, S0, hp, s)
        preds["R-GCN (no edges)"].append(pb0[S0["te"]])
        for tag, cols in (("metrics only", metric_cols), ("+neighbours", all_cols)):
            preds[f"RF ({tag})"].append(j.tabular(X, ye, S, "RF", cols, s)[te])
            if s == seeds[0]:                                    # LR is deterministic: one run is enough
                preds[f"LR ({tag})"].append(j.tabular(X, ye, S, "LR", cols, s)[te])

    def seed_avg(model, idx):
        return np.mean([metrics(y_te[idx], P[idx]) for P in preds[model]], axis=0)

    full_idx = np.arange(len(y_te))
    point = {m: seed_avg(m, full_idx) for m in MODELS}

    rng = np.random.default_rng(12345)
    boot = {m: [] for m in MODELS}
    used = 0
    print(f"bootstrapping ({B} resamples, block {a.block})...")
    for b in range(B):
        idx = block_indices(len(y_te), a.block, rng)
        yt = y_te[idx]
        if yt.sum() == 0 or yt.sum() == len(yt):
            continue
        used += 1
        for m in MODELS:
            boot[m].append(seed_avg(m, idx))
        if (b + 1) % 100 == 0:
            print(f"  {b + 1}/{B}")
    boot = {m: np.array(v) for m, v in boot.items()}

    ci_rows = []
    for m in MODELS:
        for k, nm in enumerate(NAMES):
            lo, hi = np.percentile(boot[m][:, k], [2.5, 97.5])
            ci_rows.append(dict(model=m, metric=nm, estimate=round(float(point[m][k]), 4),
                                ci_low=round(float(lo), 4), ci_high=round(float(hi), 4)))
    ci = pd.DataFrame(ci_rows)

    d_rows = []
    for m1, m2 in PAIRS:
        for k, nm in enumerate(NAMES):
            d = boot[m1][:, k] - boot[m2][:, k]
            lo, hi = np.percentile(d, [2.5, 97.5])
            d_rows.append(dict(difference=f"{m1} minus {m2}", metric=nm,
                               estimate=round(float(point[m1][k] - point[m2][k]), 4),
                               ci_low=round(float(lo), 4), ci_high=round(float(hi), 4),
                               share_resamples_positive=round(float((d > 0).mean()), 3),
                               excludes_zero=bool(lo > 0 or hi < 0)))
    diff = pd.DataFrame(d_rows)

    ci.to_csv(os.path.join(a.outdir, "bootstrap_ci.csv"), index=False)
    diff.to_csv(os.path.join(a.outdir, "bootstrap_diff.csv"), index=False)
    md = (f"# Bootstrap confidence intervals\n\nAudited chronological test set: {int(te.sum())} commits, "
          f"{int(y_te.sum())} buggy. Moving-block bootstrap (block {a.block}), {used} valid resamples, "
          f"{len(seeds)} seeds averaged per model; hyperparameters {hp}. 95% percentile intervals.\n\n"
          "## Metrics\n\n" + j.md(ci) + "\n\n## Paired differences (same resampled commits)\n\n" + j.md(diff) + "\n")
    with open(os.path.join(a.outdir, "bootstrap_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()