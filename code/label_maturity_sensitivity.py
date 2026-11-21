"""
label_maturity_sensitivity.py  --  how much do the not-yet-observable training labels matter?
(uses jit_temporal_audit.py unchanged)

Run from the project root:
    python3 label_maturity_sensitivity.py --quick     # 3 seeds
    python3 label_maturity_sensitivity.py             # 10 seeds

Our protocol relabels the buggy training commits whose fix did not exist yet at the cutoff (455 on HBase)
as clean. This script compares it with alternatives. Features, graph, test set and hyperparameters are
identical in every variant; only WHICH training/validation commits are used changes.

  audited (reference)        our protocol: unobservable bugs are treated as clean
  buffer 180 days            DEPLOYABLE: drop training and validation commits committed within the last
                             180 days before the cutoff (their labels are still immature)
  buffer 365 days            same, 365 days
  oracle drop                NON-DEPLOYABLE diagnostic: drop exactly the commits that are buggy-but-unobservable.
                             It uses knowledge of future labels to choose rows, so it is an optimistic upper bound
                             on removing label noise, not something a deployed system could do.

Outputs (results_label_maturity/): maturity_runs.csv, maturity_delta.csv, maturity_audit.json, maturity_summary.md
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
REF = "audited (reference)"
ORACLE = "oracle drop of unobservable bugs [NON-DEPLOYABLE]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/HBase_input.csv")
    ap.add_argument("--gitmeta", default="data/HBase_gitmeta.csv")
    ap.add_argument("--mapping", default="data/HBase_mapping.csv")
    ap.add_argument("--outdir", default="results_label_maturity")
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
    n, t = len(df), df["_t"].values
    E = j.build_edges(df)
    G = j.to_graph(E, n)
    X, y, ye, S = j.prepare(df, E, ft, "audited")
    metric_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    all_cols = metric_cols + list(range(len(j.BASE), X.shape[1]))
    unobs = (y == 1) & (ye == 0)                      # buggy but label not observable at the cutoff
    day = 86400.0

    variants = {
        REF: (S["tr"], S["va"]),
        "buffer 180 days": (S["tr"] & (t < S["ttr"] - 180 * day), S["va"] & (t < S["tva"] - 180 * day)),
        "buffer 365 days": (S["tr"] & (t < S["ttr"] - 365 * day), S["va"] & (t < S["tva"] - 365 * day)),
        ORACLE: (S["tr"] & ~unobs, S["va"] & ~unobs),
    }

    audit = {"fixed_hyperparameters": hp, "seeds": seeds, "variants": {}}
    for name, (tr2, va2) in variants.items():
        audit["variants"][name] = {
            "train_n": int(tr2.sum()), "train_pos_rate_used": round(float(ye[tr2].mean()), 4),
            "unobservable_buggy_still_in_train": int((unobs & tr2).sum()),
            "val_n": int(va2.sum()), "val_pos_rate_used": round(float(ye[va2].mean()), 4),
            "test_n": int(S["te"].sum()),
        }
        print(name, audit["variants"][name])

    rows = []
    for s in seeds:
        print(f"\n=== seed {s} ===")
        for name, (tr2, va2) in variants.items():
            print("  ", name)
            S2 = dict(S, tr=tr2, va=va2)
            base = dict(variant=name, seed=s)
            _, pb, ep = j.train_rgcn(X[:, all_cols], ye, G, S2, hp, s)
            rows.append(dict(base, model="R-GCN", best_epoch=ep, **j.eval_probs(y, ye, pb, S2)))
            for kind in ("LR", "RF"):
                for tag, cols in (("metrics only", metric_cols), ("+neighbours", all_cols)):
                    p = j.tabular(X, ye, S2, kind, cols, s)
                    rows.append(dict(base, model=f"{kind} ({tag})", best_epoch=None, **j.eval_probs(y, ye, p, S2)))

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(a.outdir, "maturity_runs.csv"), index=False)

    g = runs.groupby(["variant", "model"], sort=False)[METRICS].agg(["mean", "std"])
    table = pd.DataFrame({"variant": [i[0] for i in g.index], "model": [i[1] for i in g.index]})
    for m in METRICS:
        table[m] = [f"{g[(m, 'mean')][k]:.3f} ± {0 if np.isnan(g[(m, 'std')][k]) else g[(m, 'std')][k]:.3f}"
                    for k in g.index]

    drows = []
    for variant in runs.variant.unique():
        if variant == REF:
            continue
        for model in runs[runs.variant == variant].model.unique():
            A = runs[(runs.variant == variant) & (runs.model == model)].sort_values("seed")
            B = runs[(runs.variant == REF) & (runs.model == model)].sort_values("seed")
            for m in HEADLINE:
                d = A[m].values - B[m].values
                try:
                    pv = float(wilcoxon(A[m].values, B[m].values).pvalue)
                except Exception:
                    pv = float("nan")
                drows.append(dict(variant=variant, model=model, metric=m, mean_diff=round(float(d.mean()), 4),
                                  seeds_higher=int((d > 0).sum()), n_seeds=len(d), p_value=round(pv, 4)))
    delta = pd.DataFrame(drows)
    delta.to_csv(os.path.join(a.outdir, "maturity_delta.csv"), index=False)
    with open(os.path.join(a.outdir, "maturity_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    md = (f"# Label-maturity sensitivity\n\nFixed hyperparameters {hp}; {len(seeds)} seeds. Same test commits in every "
          "variant. The oracle variant is a non-deployable diagnostic.\n\n## Test metrics\n\n" + j.md(table) +
          "\n\n## Change vs the audited reference (paired over seeds; ignore p-values for deterministic LR)\n\n" +
          j.md(delta) + "\n\n## Rows used per variant\n\n```json\n" + json.dumps(audit["variants"], indent=2) + "\n```\n")
    with open(os.path.join(a.outdir, "maturity_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()