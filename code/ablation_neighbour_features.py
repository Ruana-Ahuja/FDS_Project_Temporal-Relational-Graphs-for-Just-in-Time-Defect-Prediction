"""
ablation_neighbour_features.py  --  which neighbour-derived feature (if any) matters, and does the
graph contain label signal at all?  (uses jit_temporal_audit.py unchanged)

Run from the project root:
    python ablation_neighbour_features.py --quick     # 3 seeds
    python ablation_neighbour_features.py             # 10 seeds

Part 1  Feature-group ablation on the FULL past-only graph, 8 metrics (npt dropped) plus a subset of
        the six neighbour-derived features:
            degree features        = log in-degree per relation (3) + log total in-degree (1)
            past-bug ratio         = share of in-neighbours known to be buggy at the target commit's time
            author experience      = number of strictly earlier commits by the same author
        Models: R-GCN (full graph), LR, RF. Fixed hyperparameters (hidden 32, lr 0.01, dropout 0.2).

Part 2  Edge label homophily per relation (descriptive, final labels): is a commit more likely to be
        buggy when its in-neighbour is buggy? Also reported using only neighbours whose bug label was
        already KNOWN at the target commit's time (the part a deployed model could use).

Outputs (results_neighbour_features/):
    nbfeat_runs.csv, nbfeat_summary.csv, nbfeat_delta.csv, homophily.csv, nbfeat_summary.md
"""
import argparse
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
REF = "all neighbour features (reference)"

# offsets inside the 6 neighbour columns: [deg_author, deg_file, deg_both, past_bug_ratio, log1p(total_in_deg), author_exp]
GROUPS = {
    REF: [0, 1, 2, 3, 4, 5],
    "drop author experience": [0, 1, 2, 3, 4],
    "drop degree features": [3, 5],
    "drop past-bug ratio": [0, 1, 2, 4, 5],
    "past-bug ratio only": [3],
    "no neighbour features (metrics only)": [],
}


def homophily(df, E, y, ft):
    """Descriptive label homophily per relation.

    The bug rate falls over the years, and edges whose source is 'known buggy' at the target's time
    are concentrated in later years, so raw comparisons with the global base rate are confounded by
    era. The two *_year_matched columns compare, within each target year, edges whose source is known
    buggy with edges whose source is not (clean or still unknown), re-weighted to the known-buggy
    edges' year mix. This is the contrast a deployed model could actually use."""
    tt = df["_t"].values
    year = pd.to_datetime(tt, unit="s").year.values
    base = float(y.mean())
    rows = []
    for r in j.RELS + ["all relations"]:
        e = np.vstack([E[x] for x in j.RELS]) if r == "all relations" else E[r]
        s, d = e[:, 0], e[:, 1]
        ys, yd = y[s] == 1, y[d] == 1
        known = ys & (ft[s] < tt[d])          # source's bug label already known when target is committed
        yrs = year[d]

        def rate(mask):
            return round(float(yd[mask].mean()), 4) if mask.any() else float("nan")

        num_k = num_n = w = 0.0
        for yr in np.unique(yrs[known]):
            m = yrs == yr
            k_, n_ = m & known, m & ~known
            if k_.sum() < 20 or n_.sum() < 20:
                continue
            num_k += k_.sum() * yd[k_].mean()
            num_n += k_.sum() * yd[n_].mean()
            w += k_.sum()

        rows.append(dict(relation=r, edges=int(len(e)), base_rate=round(base, 4),
                         P_target_buggy_given_src_buggy_final=rate(ys),
                         P_target_buggy_given_src_buggy_and_known=rate(known),
                         P_target_buggy_given_src_clean=rate(~ys),
                         share_edges_src_known_buggy=round(float(known.mean()), 4),
                         P_src_known_buggy_year_matched=round(num_k / w, 4) if w else float("nan"),
                         P_src_not_known_buggy_year_matched=round(num_n / w, 4) if w else float("nan")))
    return pd.DataFrame(rows)


def summarise(runs):
    g = runs.groupby(["variant", "model"], sort=False)[METRICS].agg(["mean", "std"])
    flat = pd.DataFrame(index=g.index)
    for m in METRICS:
        flat[m + "_mean"] = g[(m, "mean")]
        flat[m + "_std"] = g[(m, "std")]
    return flat.reset_index()


def deltas(runs):
    rows = []
    for variant in runs.variant.unique():
        if variant == REF:
            continue
        for model in runs[runs.variant == variant].model.unique():
            a = runs[(runs.variant == variant) & (runs.model == model)].sort_values("seed")
            b = runs[(runs.variant == REF) & (runs.model == model)].sort_values("seed")
            for m in HEADLINE:
                d = a[m].values - b[m].values
                try:
                    pv = float(wilcoxon(a[m].values, b[m].values).pvalue)
                except Exception:
                    pv = float("nan")
                rows.append(dict(variant=variant, model=model, metric=m, mean_diff=round(float(d.mean()), 4),
                                 seeds_lower=int((d < 0).sum()), n_seeds=len(d), p_value=round(pv, 4)))
    return pd.DataFrame(rows)


def fmt_table(summary):
    out = pd.DataFrame({"variant": summary.variant, "model": summary.model})
    for m in METRICS:
        out[m] = [f"{a:.3f} ± {0 if np.isnan(b) else b:.3f}"
                  for a, b in zip(summary[m + "_mean"], summary[m + "_std"])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/HBase_input.csv")
    ap.add_argument("--gitmeta", default="data/HBase_gitmeta.csv")
    ap.add_argument("--mapping", default="data/HBase_mapping.csv")
    ap.add_argument("--outdir", default="results_neighbour_features")
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--homophily_only", action="store_true", help="only compute the edge homophily table (fast)")
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
    X, y, ye, S = j.prepare(df, E, ft, "audited")
    metric_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    nb0 = len(j.BASE)
    assert X.shape[1] == nb0 + 6, "unexpected feature count"

    hom = homophily(df, E, y, ft)
    hom.to_csv(os.path.join(a.outdir, "homophily.csv"), index=False)
    print(hom.to_string(index=False))
    if a.homophily_only:
        return

    rows = []
    for s in seeds:
        print(f"\n=== seed {s} ===")
        for name, offs in GROUPS.items():
            cols = metric_cols + [nb0 + o for o in offs]
            print("  ", name)
            base = dict(variant=name, seed=s)
            _, pb, ep = j.train_rgcn(X[:, cols], ye, G, S, hp, s)
            rows.append(dict(base, model="R-GCN (full graph)", best_epoch=ep, **j.eval_probs(y, ye, pb, S)))
            for kind in ("LR", "RF"):
                p = j.tabular(X, ye, S, kind, cols, s)
                rows.append(dict(base, model=kind, best_epoch=None, **j.eval_probs(y, ye, p, S)))

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(a.outdir, "nbfeat_runs.csv"), index=False)
    summary = summarise(runs)
    summary.to_csv(os.path.join(a.outdir, "nbfeat_summary.csv"), index=False)
    delta = deltas(runs)
    delta.to_csv(os.path.join(a.outdir, "nbfeat_delta.csv"), index=False)

    md = (f"# Neighbour-feature ablation\n\nFixed hyperparameters {hp}; {len(seeds)} seeds; metrics: drop npt.\n\n"
          "## Feature-group ablation (full past-only graph)\n\n" + j.md(fmt_table(summary)) +
          "\n\n## Change vs reference (paired over seeds)\n\n" + j.md(delta) +
          "\n\n## Edge label homophily (descriptive; final labels)\n\n" + j.md(hom) + "\n")
    with open(os.path.join(a.outdir, "nbfeat_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()