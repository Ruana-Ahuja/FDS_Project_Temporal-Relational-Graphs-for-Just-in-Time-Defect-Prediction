"""
ablation_extra.py  --  the remaining mandatory ablations (uses jit_temporal_audit.py unchanged)

Run from the project root:
    python ablation_extra.py --quick     # 3 seeds, smoke test
    python ablation_extra.py             # 10 seeds

Feature set everywhere = drop npt (8 metrics) + the 6 neighbour/author features, same as the
final configuration. Hyperparameters are FIXED (hidden 32, lr 0.01, dropout 0.2).

Group "depth"          R-GCN with 1, 2 (reference) and 3 message-passing layers (oversmoothing check)
Group "neighbourhood"  K = max past neighbours per author / per file: 1, 3, 5 (reference), 10, 20
Group "temporal"       past-only (reference) vs two NON-DEPLOYABLE controls:
                         (a) neighbours may come from the future, audited labels
                         (b) neighbours may come from the future AND final labels are used everywhere
                       These controls are diagnostics only and must be labelled as such in the paper.

Outputs (results_ablation_extra/):
    extra_runs.csv, extra_summary.csv, extra_delta.csv, extra_summary.md, extra_audit.json
"""
import argparse
import json
import os
from types import SimpleNamespace

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import wilcoxon
from sklearn.metrics import average_precision_score

import jit_temporal_audit as j

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

METRICS = ["AUPRC", "AUROC", "F1", "MCC", "R20"]
HEADLINE = ["AUPRC", "AUROC", "R20"]
REFS = {"depth": "depth 2 (reference)",
        "neighbourhood": "K=5 (reference)",
        "temporal": "past-only (reference)"}


# ----------------------------- model with variable depth ---------------------
class RGCNDepth(nn.Module):
    """Same layer definition as jit_temporal_audit.RGCN, but with a configurable number of layers."""

    def __init__(self, din, h, nr, p, depth):
        super().__init__()
        dims = [din] + [h] * depth
        self.selfs = nn.ModuleList([nn.Linear(dims[l], dims[l + 1]) for l in range(depth)])
        self.rels = nn.ModuleList([
            nn.ModuleList([nn.Linear(dims[l], dims[l + 1], bias=False) for _ in range(nr)])
            for l in range(depth)])
        self.out, self.p = nn.Linear(h, 1), p

    def forward(self, x, G):
        h = F.dropout(x, self.p, self.training)
        for selfl, rl in zip(self.selfs, self.rels):
            z = selfl(h)
            for (src, dst, inv), W in zip(G, rl):
                z = z + torch.zeros_like(z).index_add_(0, dst, W(h)[src]) * inv
            h = F.dropout(torch.relu(z), self.p, self.training)
        return self.out(h).squeeze(1)


def train_depth(X, ye, G, S, hp, seed, depth, epochs=j.EPOCHS):
    """Best-validation-AUPRC checkpoint, exactly as j.train_rgcn. Returns (probabilities, best epoch)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    Xt = torch.tensor(X, dtype=torch.float32)
    yt = torch.tensor(ye, dtype=torch.float32)
    tr, va = torch.tensor(S["tr"]), S["va"]
    model = RGCNDepth(X.shape[1], hp["hidden"], len(j.RELS), hp["dropout"], depth)
    opt = torch.optim.Adam(model.parameters(), lr=hp["lr"], weight_decay=j.WD)
    pr = max(ye[S["tr"]].mean(), 1e-6)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((1 - pr) / pr)))
    best_v, best_p, best_ep = -1, None, 0
    for ep in range(epochs):
        model.train()
        opt.zero_grad()
        lossf(model(Xt, G)[tr], yt[tr]).backward()
        opt.step()
        model.eval()
        with torch.no_grad():
            p = torch.sigmoid(model(Xt, G)).numpy()
        v = average_precision_score(ye[va], p[va])             # validation ONLY
        if v > best_v:
            best_v, best_p, best_ep = v, p.copy(), ep
    return best_p, best_ep


# ----------------------------- graph variants --------------------------------
def build_edges_k(df, k):
    """Past-only edges with neighbourhood size k (reuses j.build_edges; restores j.K_PRED)."""
    old = j.K_PRED
    j.K_PRED = k
    try:
        return j.build_edges(df)
    finally:
        j.K_PRED = old


def build_edges_future_allowed(df, k):
    """NON-DEPLOYABLE CONTROL. Each commit is linked to its k nearest commits (by time order)
    by the same author / touching the same file, on EITHER side in time. Future commits are allowed."""
    n = len(df)
    auth = df["_auth"].values
    files = [set(f for f in str(s).split(";") if f and f != "nan") for s in df["files_git"].values]
    ga, gf = {}, {}
    for i in range(n):                       # df is sorted by time, so lists are time-ordered
        ga.setdefault(auth[i], []).append(i)
        for f in files[i]:
            gf.setdefault(f, []).append(i)

    def nearest(group, p, k):
        out, d = [], 1
        while len(out) < k:
            added = False
            if p - d >= 0:
                out.append(group[p - d]); added = True
            if len(out) < k and p + d < len(group):
                out.append(group[p + d]); added = True
            if not added:
                break
            d += 1
        return out

    na = [set() for _ in range(n)]
    nf = [set() for _ in range(n)]
    for lst in ga.values():
        for p, i in enumerate(lst):
            na[i].update(nearest(lst, p, k))
    for lst in gf.values():
        for p, i in enumerate(lst):
            nf[i].update(nearest(lst, p, k))

    E = {r: [] for r in j.RELS}
    for i in range(n):
        pa = na[i] - {i}
        pf = nf[i] - {i}
        if len(pf) > k:
            pf = set(sorted(pf, key=lambda x: abs(x - i))[:k])
        both = pa & pf
        E["same_author_same_file"] += [(s, i) for s in both]
        E["same_author"] += [(s, i) for s in pa - both]
        E["same_file"] += [(s, i) for s in pf - both]
    return {r: np.array(E[r], dtype=np.int64).reshape(-1, 2) for r in j.RELS}


def count_violations(E, times):
    return {r: int(((times[E[r][:, 0]] >= times[E[r][:, 1]]).sum())) if len(E[r]) else 0 for r in j.RELS}


# ----------------------------- runner ----------------------------------------
def run_variant(rows, group, variant, data, ref_cols, nb_cols, seed, hp, depth=2, tabular=True):
    X, y, ye, S, G = data
    all_cols = ref_cols + nb_cols
    base = dict(group=group, variant=variant, seed=seed)
    pb, ep = train_depth(X[:, all_cols], ye, G, S, hp, seed, depth)
    rows.append(dict(base, model="R-GCN", best_epoch=ep, **j.eval_probs(y, ye, pb, S)))
    if tabular:
        for kind in ("LR", "RF"):
            p = j.tabular(X, ye, S, kind, all_cols, seed)
            rows.append(dict(base, model=f"{kind} (+neighbours)", best_epoch=None, **j.eval_probs(y, ye, p, S)))


def summarise(runs):
    g = runs.groupby(["group", "variant", "model"], sort=False)[METRICS].agg(["mean", "std"])
    flat = pd.DataFrame(index=g.index)
    for m in METRICS:
        flat[m + "_mean"] = g[(m, "mean")]
        flat[m + "_std"] = g[(m, "std")]
    return flat.reset_index()


def deltas(runs):
    rows = []
    for group, ref in REFS.items():
        sub = runs[runs.group == group]
        for variant in sub.variant.unique():
            if variant == ref:
                continue
            for model in sub[sub.variant == variant].model.unique():
                a = sub[(sub.variant == variant) & (sub.model == model)].sort_values("seed")
                b = sub[(sub.variant == ref) & (sub.model == model)].sort_values("seed")
                if a.empty or b.empty:
                    continue
                for m in HEADLINE:
                    d = a[m].values - b[m].values
                    try:
                        pv = float(wilcoxon(a[m].values, b[m].values).pvalue)
                    except Exception:
                        pv = float("nan")
                    rows.append(dict(group=group, variant=variant, model=model, vs=ref, metric=m,
                                     mean_diff=round(float(d.mean()), 4), seeds_lower=int((d < 0).sum()),
                                     n_seeds=len(d), p_value=round(pv, 4)))
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
    ap.add_argument("--outdir", default="results_ablation_extra")
    ap.add_argument("--hidden", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--dropout", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    hp = dict(hidden=a.hidden, lr=a.lr, dropout=a.dropout)
    seeds = list(range(3 if a.quick else a.seeds))
    K_REF = j.K_PRED                                   # 5
    K_LIST = [1, 3, K_REF, 10, 20]

    print("Loading data...")
    df, info = j.load(SimpleNamespace(input=a.input, gitmeta=a.gitmeta, time="committer_ts"))
    ft, linfo = j.label_times(df, a.mapping)
    n, times = len(df), df["_t"].values
    ref_cols = [i for i, c in enumerate(j.BASE) if c != "npt"]
    nb_start = len(j.BASE)

    audit = {"data": info, "commits_used": n, "fixed_hyperparameters": hp, "seeds": seeds,
             "reference_feature_columns": [j.BASE[i] for i in ref_cols], "graphs": {}}

    # ---------- precompute every graph / feature matrix once (deterministic) ----------
    data = {}
    for k in K_LIST:
        E = build_edges_k(df, k)
        viol = count_violations(E, times)
        assert sum(viol.values()) == 0, f"future edge in past-only graph K={k}"
        X, y, ye, S = j.prepare(df, E, ft, "audited")
        data[("K", k)] = (X, y, ye, S, j.to_graph(E, n))
        audit["graphs"][f"past-only K={k}"] = {"edges": {r: int(len(E[r])) for r in j.RELS}, "violations": viol}
        print(f"  K={k}: {sum(len(E[r]) for r in j.RELS)} edges")
    nb_cols = list(range(nb_start, data[("K", K_REF)][0].shape[1]))

    print("Building non-deployable future-allowed graph...")
    Ef = build_edges_future_allowed(df, K_REF)
    vf = count_violations(Ef, times)
    audit["graphs"]["future-allowed K=5 (NON-DEPLOYABLE)"] = {
        "edges": {r: int(len(Ef[r])) for r in j.RELS}, "edges_pointing_from_same_or_later_time": vf}
    Gf = j.to_graph(Ef, n)
    Xa, ya, yea, Sa = j.prepare(df, Ef, ft, "audited")
    Xl, yl, yel, Sl = j.prepare(df, Ef, ft, "leaky")
    data["future_audited"] = (Xa, ya, yea, Sa, Gf)
    data["future_leaky"] = (Xl, yl, yel, Sl, Gf)

    rows = []
    for s in seeds:
        print(f"\n=== seed {s} ===")
        # ---- depth ----
        for depth in (1, 2, 3):
            name = "depth 2 (reference)" if depth == 2 else f"depth {depth}"
            print("  [depth]", name)
            run_variant(rows, "depth", name, data[("K", K_REF)], ref_cols, nb_cols, s, hp,
                        depth=depth, tabular=(depth == 2))
        ref_rows = [r for r in rows if r["group"] == "depth" and r["variant"] == "depth 2 (reference)" and r["seed"] == s]
        for r in ref_rows:                                 # reuse the reference instead of retraining
            rows.append(dict(r, group="neighbourhood", variant="K=5 (reference)"))
            rows.append(dict(r, group="temporal", variant="past-only (reference)"))
        # ---- neighbourhood size ----
        for k in K_LIST:
            if k == K_REF:
                continue
            print(f"  [K] K={k}")
            run_variant(rows, "neighbourhood", f"K={k}", data[("K", k)], ref_cols, nb_cols, s, hp)
        # ---- non-deployable temporal controls ----
        print("  [temporal] future edges, audited labels")
        run_variant(rows, "temporal", "future edges allowed, audited labels [NON-DEPLOYABLE]",
                    data["future_audited"], ref_cols, nb_cols, s, hp)
        print("  [temporal] future edges, final labels")
        run_variant(rows, "temporal", "future edges + final labels [NON-DEPLOYABLE]",
                    data["future_leaky"], ref_cols, nb_cols, s, hp)

    runs = pd.DataFrame(rows)
    runs.to_csv(os.path.join(a.outdir, "extra_runs.csv"), index=False)
    summary = summarise(runs)
    summary.to_csv(os.path.join(a.outdir, "extra_summary.csv"), index=False)
    delta = deltas(runs)
    delta.to_csv(os.path.join(a.outdir, "extra_delta.csv"), index=False)
    with open(os.path.join(a.outdir, "extra_audit.json"), "w") as f:
        json.dump(audit, f, indent=2, default=str)

    md = (f"# Extra ablations\n\nFixed hyperparameters {hp}; {len(seeds)} seeds; features: drop npt.\n\n"
          "## Graph depth\n\n" + j.md(fmt_table(summary, "depth")) +
          "\n\n## Neighbourhood size K\n\n" + j.md(fmt_table(summary, "neighbourhood")) +
          "\n\n## Temporal constraint (variants marked NON-DEPLOYABLE are diagnostic controls only)\n\n" +
          j.md(fmt_table(summary, "temporal")) +
          "\n\n## Change vs reference (paired over seeds)\n\n" + j.md(delta.drop(columns=["group"])) + "\n")
    with open(os.path.join(a.outdir, "extra_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print("Outputs in", a.outdir)


if __name__ == "__main__":
    main()