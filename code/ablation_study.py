"""
ablation_study.py  --  ablations for CodeGuard-lite (uses jit_temporal_audit.py unchanged)

Run from the project root (same place as final_no_npt.py):
    python ablation_study.py            # 10 seeds
    python ablation_study.py --quick    # 3 seeds, for a smoke test

Part A  Feature ablation (reviewer: "final configuration not fully audited")
        drop npt (reference) | drop fix (keep npt) | drop fix + npt
        Models: R-GCN, LR, RF, each metrics-only and +neighbour features.
Part B  Graph ablation (reviewer: "mandatory ablations"), feature set = drop npt
        full graph (reference) | remove each relation | remove all edges |
        shuffled edges (past-only, in-degree preserving) | single-relation GCN
        Neighbour features are RECOMPUTED from the modified edges, so the tabular
        "+neighbour" models see the same modified graph as the R-GCN.

Hyperparameters are FIXED to the configuration selected on validation in your final run
(hidden 32, lr 0.01, dropout 0.2) for every variant, so differences come from the ablation,
not from re-tuning. The test set is never used for any selection.

Outputs (results_ablation/):
    ablation_runs.csv     one row per (group, variant, model, seed)
    ablation_summary.csv  mean/std over seeds
    ablation_delta.csv    change vs the group's reference, paired over seeds
    ablation_summary.md   readable tables
    audit_report_final.json  edge counts / violations / splits from THIS run
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
REF_FEATURE = "drop npt (reference)"
REF_GRAPH = "full graph (reference)"


# ----------------------------- graph variants --------------------------------
def empty_edges():
    return np.empty((0, 2), dtype=np.int64)


def drop_relations(E, rels):
    return {r: (empty_edges() if r in rels else E[r]) for r in j.RELS}


def shuffle_edges(E, times, rng):
    """Replace every source by a random STRICTLY earlier commit.

    Keeps each target's in-degree per relation and the past-only property,
    but destroys who is connected to whom. `times` must be sorted ascending
    (j.load sorts by time)."""
    out = {}
    for r in j.RELS:
        e = E[r]
        if len(e) == 0:
            out[r] = empty_edges()
            continue
        dst = e[:, 1]
        k = np.searchsorted(times, times[dst], side="left")   # commits with t < t[dst]
        src = np.floor(rng.random(len(e)) * k).astype(np.int64)
        out[r] = np.column_stack([src, dst])
    return out


def merge_relations(E):
    """All edges in one relation -> homogeneous GCN-style message passing."""
    allE = np.vstack([E[r] for r in j.RELS])
    merged = {r: empty_edges() for r in j.RELS}
    merged[j.RELS[0]] = allE
    return merged


def count_violations(E, times):
    return {r: int(((E[r][:, 0] >= E[r][:, 1]) | (times[E[r][:, 0]] >= times[E[r][:, 1]])).sum())
            if len(E[r]) else 0 for r in j.RELS}


# ----------------------------- model runner ----------------------------------
def run_models(rows, group, variant, X, y, ye, S, G, metric_cols, nb_cols, seed, hp,
               tabular_metrics_only=True, tabular_neigh=True, rgcn=True, rgcn_name="R-GCN"):
    all_cols = metric_cols + nb_cols
    base = dict(group=group, variant=variant, seed=seed)
    if rgcn:
        _, pb, ep = j.train_rgcn(X[:, all_cols], ye, G, S, hp, seed)     # best-val-AUPRC checkpoint
        rows.append(dict(base, model=rgcn_name, best_epoch=ep, **j.eval_probs(y, ye, pb, S)))
    for kind in ("LR", "RF"):
        if tabular_metrics_only:
            p = j.tabular(X, ye, S, kind, metric_cols, seed)
            rows.append(dict(base, model=f"{kind} (metrics only)", best_epoch=None, **j.eval_probs(y, ye, p, S)))
        if tabular_neigh:
            p = j.tabular(X, ye, S, kind, all_cols, seed)
            rows.append(dict(base, model=f"{kind} (+neighbours)", best_epoch=None, **j.eval_probs(y, ye, p, S)))


# ----------------------------- summaries -------------------------------------
def summarise(runs):
    g = runs.groupby(["group", "variant", "model"], sort=False)[METRICS].agg(["mean", "std"])
    flat = pd.DataFrame(index=g.index)
    for m in METRICS:
        flat[m + "_mean"] = g[(m, "mean")]
        flat[m + "_std"] = g[(m, "std")]
    return flat.reset_index()


def deltas(runs):
    rows = []
    for group, ref in (("feature", REF_FEATURE), ("graph", REF_GRAPH)):
        sub = runs[runs.group == group]
        for variant in sub.variant.unique():
            if variant == ref:
                continue
            for model in sub[sub.variant == variant].model.unique():
                ref_model = "R-GCN" if model.startswith("GCN") else model
                a = sub[(sub.variant == variant) & (sub.model == model)].sort_values("seed")
                b = sub[(sub.variant == ref) & (sub.model == ref_model)].sort_values("seed")
                if a.empty or b.empty:
                    continue
                for m in HEADLINE:
                    d = a[m].values - b[m].values
                    try:
                        pv = float(wilcoxon(a[m].values, b[m].values).pvalue)
                    except Exception:
                        pv = float("nan")
                    rows.append(dict(group=group, variant=variant, model=model, vs=f"{ref_model} @ {ref}",
                                     metric=m, mean_diff=round(float(d.mean()), 4),
                                     seeds_lower=int((d < 0).sum()), n_seeds=len(d), p_value=round(pv, 4)))
    return pd.DataFrame(rows)


def fmt_table(summary, group):
    s = summary[summary.group == group]
    out = pd.DataFrame({"variant": s.variant, "model": s.model})
    for m in METRICS:
        out[m] = [f"{a:.3f} ± {0 if np.isnan(b) else b:.3f}" for a, b in zip(s[m + "_mean"], s[m + "_std"])]
    return out


# ----------------------------- main ------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/HBase_input.csv")
    ap.add_argument("--gitmeta", default="data/HBase_gitmeta.csv")
    ap.add_argument("--mapping", default="data/HBase_mapping.csv")
    ap.add_argument("--outdir", default="results_ablation")
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
    df, info = j.load(SimpleNamespace(input=a.input, gitmeta=a.gitmeta, time="committer_ts"))
    ft, linfo = j.label_times(df, a.mapping)
    n, times = len(df), df["_t"].values
    assert np.all(np.diff(times) >= 0), "frame must be sorted by time"
    E = j.build_edges(df)
    G = j.to_graph(E, n)
    X, y, ye, S = j.prepare(df, E, ft, "audited")
    n_metric = len(j.BASE)
    nb_cols = list(range(n_metric, X.shape[1]))
    assert X.shape[1] == n_metric + 6, f"unexpected feature count {X.shape[1]}"

    # ---- audit evidence generated by THIS script (single source for report numbers) ----
    viol = count_violations(E, times)
    assert sum(viol.values()) == 0, "future edge in the original graph"
    audit = {
        "data": info, "label_times": linfo, "commits_used": n,
        "edges_per_relation": {r: int(len(E[r])) for r in j.RELS},
        "total_edges": int(sum(len(E[r]) for r in j.RELS)),
        "future_edge_violations": viol,
        "split_sizes": {k: int(S[k].sum()) for k in ("tr", "va", "te")},
        "pos_rate_final": {k: round(float(y[S[k]].mean()), 4) for k in ("tr", "va", "te")},
        "pos_rate_known_at_cutoff": {k: round(float(ye[S[k]].mean()), 4) for k in ("tr", "va", "te")},
        "train_buggy_labels_not_yet_known": int(((y == 1) & (ft >= S["ttr"]) & S["tr"]).sum()),
        "order_ok": bool(times[S["tr"]].max() < times[S["va"]].min() and times[S["va"]].max() < times[S["te"]].min()),
        "scaler_fit_rows": int(S["tr"].sum()),
        "fixed_hyperparameters": hp, "seeds": seeds,
    }

    # ---- feature sets (column indices into X) ----
    def metric_cols(drop):
        return [i for i, c in enumerate(j.BASE) if c not in drop]

    feature_sets = {
        REF_FEATURE: metric_cols({"npt"}),
        "drop fix (keep npt)": metric_cols({"fix"}),
        "drop fix + npt": metric_cols({"fix", "npt"}),
    }
    audit["feature_sets"] = {k: [j.BASE[i] for i in v] for k, v in feature_sets.items()}

    rows = []
    ref_cols = feature_sets[REF_FEATURE]
    rng_master = np.random.RandomState(12345)

    for s in seeds:
        print(f"\n=== seed {s} ===")

        # ---------- Part A: feature ablation ----------
        for name, mcols in feature_sets.items():
            print("  [A]", name)
            run_models(rows, "feature", name, X, y, ye, S, G, mcols, nb_cols, s, hp)

        # ---------- Part B: graph ablation (feature set = drop npt) ----------
        # reference = Part A reference rows, relabelled (avoids retraining)
        for r in [r for r in rows if r["group"] == "feature" and r["variant"] == REF_FEATURE and r["seed"] == s]:
            rows.append(dict(r, group="graph", variant=REF_GRAPH))

        variants = [(f"remove {rel}", drop_relations(E, {rel})) for rel in j.RELS]
        variants.append(("remove all edges", drop_relations(E, set(j.RELS))))
        variants.append(("shuffled edges (past-only)", shuffle_edges(E, times, np.random.RandomState(rng_master.randint(1 << 30)))))

        for name, E2 in variants:
            print("  [B]", name)
            if "shuffled" in name:
                assert sum(count_violations(E2, times).values()) == 0, "shuffle created a future edge"
            X2, y2, ye2, S2 = j.prepare(df, E2, ft, "audited")      # neighbour features follow the new edges
            G2 = j.to_graph(E2, n)
            run_models(rows, "graph", name, X2, y2, ye2, S2, G2, ref_cols, nb_cols, s, hp,
                       tabular_metrics_only=False)

        # single-relation GCN: same features as the reference, merged message passing
        print("  [B] single-relation GCN")
        Gm = j.to_graph(merge_relations(E), n)
        run_models(rows, "graph", "single-relation GCN (merged edges)", X, y, ye, S, Gm, ref_cols, nb_cols, s, hp,
                   tabular_metrics_only=False, tabular_neigh=False, rgcn_name="GCN (single relation)")

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(a.outdir, "ablation_runs.csv"), index=False)
    summary = summarise(runs)
    summary.to_csv(os.path.join(a.outdir, "ablation_summary.csv"), index=False)
    delta = deltas(runs)
    delta.to_csv(os.path.join(a.outdir, "ablation_delta.csv"), index=False)
    with open(os.path.join(a.outdir, "audit_report_final.json"), "w") as f:
        json.dump(audit, f, indent=2, default=str)

    md = ("# Ablation results\n\n"
          f"Fixed hyperparameters {hp}; {len(seeds)} seeds; one chronological audited split.\n\n"
          "## A. Feature ablation\n\n" + j.md(fmt_table(summary, "feature")) +
          "\n\n## B. Graph ablation (features: drop npt)\n\n" + j.md(fmt_table(summary, "graph")) +
          "\n\n## Change vs reference (paired over seeds, headline metrics)\n\n" +
          j.md(delta.drop(columns=["group"])) + "\n")
    with open(os.path.join(a.outdir, "ablation_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()