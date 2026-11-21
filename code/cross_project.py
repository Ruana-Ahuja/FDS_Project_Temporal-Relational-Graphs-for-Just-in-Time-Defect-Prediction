"""
cross_project.py  --  replicate the main findings on ANOTHER project (uses jit_temporal_audit.py unchanged)

Example (adapt the three paths to where your Hadoop files are):
    python3 cross_project.py --name Hadoop \
        --input other_projects/Hadoop/Hadoop_input.csv \
        --gitmeta other_projects/Hadoop/Hadoop_gitmeta.csv \
        --mapping other_projects/Hadoop/Hadoop_mapping.csv --check_only      # fast file/format check
    python3 cross_project.py --name Hadoop ... --quick                        # 3 seeds
    python3 cross_project.py --name Hadoop ...                                # 10 seeds

Same protocol and same fixed hyperparameters as the HBase study (hidden 32, lr 0.01, dropout 0.2,
chronological 70/10/20 split, 8 metrics with npt dropped + 6 neighbour/author features). The
hyperparameters are NOT re-tuned on the new project.

Conditions
  audited                   labels as known at each cutoff (our protocol)
  audited, no edges         R-GCN with all edges removed (graph ablation)
  leaky                     chronological split with final labels everywhere
  random split              random 70/10/20 split, final labels (the usual published setup)

Outputs (results_cross_<name>/): cross_runs.csv, cross_summary.csv, cross_paired.csv,
cross_audit.json, cross_summary.md
"""
import argparse
import json
import os
import sys
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
NEED_INPUT = ["transactionid", "bug"] + j.BASE
NEED_META = ["transactionid", "commit", "author_email", "author_ts", "committer_ts", "files_git"]


def preflight(a):
    ok = True
    for path, need, label in ((a.input, NEED_INPUT, "input"), (a.gitmeta, NEED_META, "gitmeta")):
        if not os.path.exists(path):
            print(f"[missing file] {label}: {path}")
            ok = False
            continue
        cols = list(j.read_any(path).head(0).columns)
        miss = [c for c in need if c not in cols]
        if miss:
            print(f"[{label}] missing columns: {miss}\n  columns found: {cols[:40]}")
            ok = False
    if not os.path.exists(a.mapping):
        print(f"[missing file] mapping: {a.mapping}")
        ok = False
    if not ok:
        print("\nPreflight failed. Send me the lines above and the header line of each file.")
        sys.exit(1)


def paired(runs, ca, ma, cb, mb, label):
    """Paired over seeds: (ca, ma) minus (cb, mb)."""
    rows = []
    A = runs[(runs.condition == ca) & (runs.model == ma)].sort_values("seed")
    B = runs[(runs.condition == cb) & (runs.model == mb)].sort_values("seed")
    if A.empty or B.empty:
        return rows
    for m in HEADLINE:
        d = A[m].values - B[m].values
        try:
            pv = float(wilcoxon(A[m].values, B[m].values).pvalue)
        except Exception:
            pv = float("nan")
        rows.append(dict(comparison=label, metric=m, mean_diff=round(float(d.mean()), 4),
                         seeds_first_higher=int((d > 0).sum()), n_seeds=len(d), p_value=round(pv, 4)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--gitmeta", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--check_only", action="store_true", help="validate files, print audit stats, then stop")
    ap.add_argument("--end_date", default=None, help="YYYY-MM-DD: drop commits after this date (right-censoring)")
    a = ap.parse_args()
    outdir = a.outdir or f"results_cross_{a.name}"
    os.makedirs(outdir, exist_ok=True)
    hp = dict(hidden=a.hidden, lr=a.lr, dropout=a.dropout)
    seeds = list(range(3 if a.quick else a.seeds))

    preflight(a)
    print(f"Loading {a.name}...")
    df, info = j.load(SimpleNamespace(input=a.input, gitmeta=a.gitmeta, time="committer_ts"))
    ft, linfo = j.label_times(df, a.mapping)
    if a.end_date:
        # Drop the most recent commits (right-censoring: their bugs have not been found yet).
        # Label times were computed on the full history, so labels of the kept commits are unchanged.
        end_ts = (pd.Timestamp(a.end_date) - pd.Timestamp("1970-01-01")).total_seconds()
        keep = df["_t"].values <= end_ts
        print(f"Truncated to commits on or before {a.end_date}: kept {int(keep.sum())} of {len(keep)}")
        df, ft = df[keep].reset_index(drop=True), ft[keep]
    n, tt = len(df), df["_t"].values
    E = j.build_edges(df)
    G = j.to_graph(E, n)
    viol = {r: int(((E[r][:, 0] >= E[r][:, 1]) | (tt[E[r][:, 0]] >= tt[E[r][:, 1]])).sum()) if len(E[r]) else 0
            for r in j.RELS}
    assert sum(viol.values()) == 0, "future or same-time edge found"
    X, y, ye, S = j.prepare(df, E, ft, "audited")
    audit = {
        "project": a.name, "end_date": a.end_date, "data": info, "label_times": linfo, "commits_used": n,
        "edges_per_relation": {r: int(len(E[r])) for r in j.RELS},
        "total_edges": int(sum(len(E[r]) for r in j.RELS)), "future_edge_violations": viol,
        "split_sizes": {k: int(S[k].sum()) for k in ("tr", "va", "te")},
        "pos_rate_final": {k: round(float(y[S[k]].mean()), 4) for k in ("tr", "va", "te")},
        "pos_rate_known_at_cutoff": {k: round(float(ye[S[k]].mean()), 4) for k in ("tr", "va", "te")},
        "train_buggy_relabelled_clean": int(((y == 1) & (ye == 0) & S["tr"]).sum()),
        "order_ok": bool(tt[S["tr"]].max() < tt[S["va"]].min() and tt[S["va"]].max() < tt[S["te"]].min()),
        "fixed_hyperparameters": hp, "seeds": seeds,
    }
    pos = (y == 1) & np.isfinite(ft)
    if pos.any():
        delay = (ft[pos] - tt[pos]) / 86400
        audit["bug_label_delay_days"] = {"median": round(float(np.median(delay)), 1),
                                         "p90": round(float(np.percentile(delay, 90)), 1)}
    print(json.dumps(audit, indent=2, default=str))
    with open(os.path.join(outdir, "cross_audit.json"), "w") as f:
        json.dump(audit, f, indent=2, default=str)

    share_fallback = linfo["buggy_without_matched_fix"] / max(linfo["buggy_commits"], 1)
    if share_fallback > 0.2:
        print(f"\nWARNING: {share_fallback:.0%} of buggy commits have no matched fix commit in this project's data; "
              "their label time falls back to +90 days. Tell me and we will discuss.")
    if a.check_only:
        print("\nCheck finished. Nothing was trained.")
        return

    metric_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    nb0 = len(j.BASE)
    E0 = {r: np.empty((0, 2), dtype=np.int64) for r in j.RELS}       # no edges
    G0 = j.to_graph(E0, n)
    X0, y0, ye0, S0 = j.prepare(df, E0, ft, "audited")

    rows = []

    def run(cond, Xc, yc, yec, Sc, Gc, seed, tabular=True, rgcn_name="R-GCN"):
        all_cols = metric_cols + list(range(nb0, Xc.shape[1]))
        base = dict(condition=cond, seed=seed)
        _, pb, ep = j.train_rgcn(Xc[:, all_cols], yec, Gc, Sc, hp, seed)
        rows.append(dict(base, model=rgcn_name, best_epoch=ep, **j.eval_probs(yc, yec, pb, Sc)))
        if tabular:
            for kind in ("LR", "RF"):
                for tag, cols in (("metrics only", metric_cols), ("+neighbours", all_cols)):
                    p = j.tabular(Xc, yec, Sc, kind, cols, seed)
                    rows.append(dict(base, model=f"{kind} ({tag})", best_epoch=None, **j.eval_probs(yc, yec, p, Sc)))

    cache = {}
    for s in seeds:
        print(f"\n=== seed {s} ===")
        print("  audited")
        run("audited", X, y, ye, S, G, s)
        print("  audited, no edges")
        run("audited, no edges", X0, y0, ye0, S0, G0, s, tabular=False)
        if "leaky" not in cache:
            cache["leaky"] = j.prepare(df, E, ft, "leaky")
        Xl, yl, yel, Sl = cache["leaky"]
        print("  leaky")
        run("leaky", Xl, yl, yel, Sl, G, s)
        Xr, yr, yer, Sr = j.prepare(df, E, ft, "leaky", "random", s)
        print("  random split")
        run("random split", Xr, yr, yer, Sr, G, s)

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(outdir, "cross_runs.csv"), index=False)
    g = runs.groupby(["condition", "model"], sort=False)[METRICS].agg(["mean", "std"])
    summ = pd.DataFrame({"condition": [i[0] for i in g.index], "model": [i[1] for i in g.index]})
    for m in METRICS:
        summ[m] = [f"{g[(m, 'mean')][k]:.3f} ± {0 if np.isnan(g[(m, 'std')][k]) else g[(m, 'std')][k]:.3f}"
                   for k in g.index]
    g.columns = [f"{m}_{s}" for m, s in g.columns]
    g.reset_index().to_csv(os.path.join(outdir, "cross_summary.csv"), index=False)

    pr = []
    for other in ("LR (metrics only)", "LR (+neighbours)", "RF (metrics only)", "RF (+neighbours)"):
        pr += paired(runs, "audited", "R-GCN", "audited", other, f"audited: R-GCN minus {other}")
    pr += paired(runs, "audited, no edges", "R-GCN", "audited", "R-GCN", "R-GCN: no edges minus full graph")
    for model in ("R-GCN", "LR (+neighbours)", "RF (+neighbours)", "LR (metrics only)", "RF (metrics only)"):
        pr += paired(runs, "leaky", model, "audited", model, f"{model}: leaky minus audited")
    for model in ("R-GCN", "LR (+neighbours)", "RF (+neighbours)"):
        pr += paired(runs, "random split", model, "audited", model, f"{model}: random split minus audited")
    paired_df = pd.DataFrame(pr)
    paired_df.to_csv(os.path.join(outdir, "cross_paired.csv"), index=False)

    md = (f"# Cross-project replication: {a.name}\n\nFixed hyperparameters {hp} (not re-tuned); {len(seeds)} seeds. "
          "The random-split test set differs from the chronological one, so compare AUROC and within-protocol "
          "changes, not AUPRC levels.\n\n## Test metrics\n\n" + j.md(summ) +
          "\n\n## Paired comparisons (ignore p-values for deterministic LR)\n\n" + j.md(paired_df) +
          "\n\n## Audit statistics\n\n```json\n" + json.dumps(audit, indent=2, default=str) + "\n```\n")
    with open(os.path.join(outdir, "cross_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", outdir)


if __name__ == "__main__":
    main()