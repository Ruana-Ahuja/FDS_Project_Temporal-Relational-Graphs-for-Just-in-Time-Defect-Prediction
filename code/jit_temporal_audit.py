"""
CodeGuard-lite (refined): D. temporal-validity audit  +  E. validation-driven training

Run from the project root:
  python jit_temporal_audit.py --input data/HBase_input.csv --gitmeta data/HBase_gitmeta.csv \
         --mapping data/HBase_mapping.csv --quick
Outputs go to ./results (override with --outdir).

D: edges are past-only (asserted); scaler is train-only; and every LABEL is used only as it
   would have been KNOWN at the cutoff: a commit counts as buggy only after its first
   bug-fixing commit (from HBase_mapping.csv) exists. 'leaky' mode (final labels everywhere)
   is run beside it to quantify the effect.
E: grid search, best-validation-AUPRC checkpoint, validation-calibrated threshold.
   The test set never influences any checkpoint, threshold or hyperparameter choice.
"""
import argparse, json, os, re, warnings, itertools
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F
from scipy.stats import wilcoxon, spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score, f1_score, matthews_corrcoef
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_sample_weight
warnings.filterwarnings("ignore")

BASE = ["ns", "nm", "nf", "entropy", "la", "ld", "lt", "fix", "npt"]   # 9 non-duplicate metrics
RELS = ["same_author", "same_file", "same_author_same_file"]
K_PRED = 5                    # max past neighbours per author / per file
FALLBACK_DAYS = 90            # only for buggy commits with no matched fix commit
GRID = dict(hidden=[32, 64], lr=[1e-2, 5e-3], dropout=[0.2, 0.5])
EPOCHS, WD = 100, 1e-4


def read_any(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        sep = "\t" if "\t" in f.readline() else ","
    return pd.read_csv(path, sep=sep)


# ------------------------------ data -----------------------------------------
def load(a):
    inp, meta = read_any(a.input), read_any(a.gitmeta)
    info = {}
    # evidence that the dataset's "developer history" columns are duplicates of other columns
    if all(c in inp.columns for c in ["ns", "ndev", "exp"]):
        info["share_rows_ns==ndev==exp"] = round(float(((inp.ns == inp.ndev) & (inp.ns == inp.exp)).mean()), 4)
    inp = inp.loc[:, ~inp.columns.str.startswith("Unnamed")]
    df = inp.merge(meta[["transactionid", "commit", "author_email", "author_ts", "committer_ts", "files_git"]],
                   on="transactionid", how="inner")

    # clean numeric feature columns (fill 0, NOT a global median: that would itself leak)
    for c in BASE:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    info["nan_feature_cells"] = int(df[BASE].isna().sum().sum())
    df[BASE] = df[BASE].fillna(0)

    if a.time == "commitdate":
        dt = pd.to_datetime(df["commitdate"], format="%d-%m-%Y %H:%M", errors="coerce")
        df["_t"] = (dt - pd.Timestamp("1970-01-01")).dt.total_seconds()
    else:
        df["_t"] = pd.to_numeric(df[a.time], errors="coerce")
    info.update(rows_input=len(inp), rows_after_merge=len(df), dropped_no_time=int(df["_t"].isna().sum()),
                time_source=a.time)
    df = df[df["_t"].notna()].sort_values("_t", kind="mergesort").reset_index(drop=True)
    df["_y"] = df["bug"].astype(str).str.lower().isin(["1", "1.0", "true"]).astype(int)
    df["fix"] = pd.to_numeric(df["fix"], errors="coerce").fillna(0).astype(float)
    # author identity = local part of the email (same person often appears under several domains)
    df["_auth"] = df["author_email"].astype(str).str.lower().str.split("@").str[0]
    return df, info


def label_times(df, mapping_path):
    """ft[i] = time at which commit i's 'buggy' label first becomes known (earliest fixing commit)."""
    tmap = dict(zip(df["commit"], df["_t"]))
    first, n_pairs, n_found = {}, 0, 0
    for line in open(mapping_path, encoding="utf-8", errors="ignore"):
        tok = re.split(r"\s+", line.strip().strip('"').strip())
        if len(tok) < 2 or tok[0].lower().startswith("fix"):
            continue
        fix, intro = tok[0], tok[1]; n_pairs += 1
        if fix in tmap:
            n_found += 1; first[intro] = min(first.get(intro, np.inf), tmap[fix])
    ft = df["commit"].map(first).astype(float).to_numpy(copy=True)
    t, pos = df["_t"].values, df["_y"].values == 1
    miss = pos & np.isnan(ft)
    ft[miss] = t[miss] + FALLBACK_DAYS * 86400
    ft[~pos] = np.inf                                   # clean commits never become buggy
    ft = np.where(pos, np.maximum(ft, t), ft)           # a label cannot be known before the commit exists
    return ft, dict(mapping_pairs=n_pairs, pairs_with_fix_in_data=n_found,
                    buggy_commits=int(pos.sum()), buggy_without_matched_fix=int(miss.sum()))


def build_edges(df):
    """Build strictly past-only edges using timestamp-batched histories.

    Commits that share a timestamp are processed as one batch: every commit in the
    batch sees only history from strictly earlier timestamps, and the history is
    updated only after the whole batch has been processed. This avoids both
    same-timestamp edges and same-timestamp commits crowding out older neighbours."""

    n = len(df)
    auth = df["_auth"].values
    times = df["_t"].values

    files = [
        set(f for f in str(s).split(";") if f and f != "nan")
        for s in df["files_git"].values
    ]

    last_a, last_f = {}, {}
    E = {r: [] for r in RELS}

    order = np.argsort(times, kind="stable")
    sorted_times = times[order]

    boundaries = np.r_[
        0,
        np.flatnonzero(np.diff(sorted_times) != 0) + 1,
        n
    ]

    for start, end in zip(boundaries[:-1], boundaries[1:]):
        batch = order[start:end]

        for i in batch:
            pa = set(last_a.get(auth[i], []))

            pf = set()
            for f in files[i]:
                pf.update(last_f.get(f, []))

            if len(pf) > K_PRED:
                # tie-break on index so equal timestamps resolve identically in every run
                pf = set(sorted(
                    pf, key=lambda j: (times[j], j)
                )[-K_PRED:])

            both = pa & pf

            E["same_author_same_file"].extend(
                (j, i) for j in both
            )
            E["same_author"].extend(
                (j, i) for j in pa - both
            )
            E["same_file"].extend(
                (j, i) for j in pf - both
            )

        # Update history only after processing the entire batch.
        for i in batch:
            lst = last_a.setdefault(auth[i], [])
            lst.append(i)
            del lst[:-K_PRED]

            for f in files[i]:
                lst = last_f.setdefault(f, [])
                lst.append(i)
                del lst[:-K_PRED]

    # sorted so the edge order (and hence float summation order in the GNN) is identical in every run
    return {
        r: np.array(sorted(E[r]), dtype=np.int64).reshape(-1, 2)
        for r in RELS
    }


def history_checks(df):
    """Evidence that dataset history features (nf, npt) use only information available at commit time."""
    files = [set(f for f in str(s).split(";") if f and f != "nan") for s in df["files_git"]]
    tot = {}
    for fs in files:
        for f in fs:
            tot[f] = tot.get(f, 0) + 1
    past, p_past, p_all = {}, np.zeros(len(df)), np.zeros(len(df))
    for i, fs in enumerate(files):
        p_past[i] = sum(past.get(f, 0) for f in fs)
        p_all[i] = sum(tot[f] for f in fs)
        for f in fs:
            past[f] = past.get(f, 0) + 1
    r = lambda x, z: round(float(spearmanr(x, z).correlation), 3)
    return {"nf_vs_git_file_count": r(df["nf"], [len(x) for x in files]),
            "npt_vs_past_only_count": r(df["npt"], p_past),
            "npt_vs_all_time_count": r(df["npt"], p_all)}


def prepare(df, E, ft, mode, split="chrono", seed=0):
    """mode='audited': labels as known at each cutoff / at the target commit's time.
       mode='leaky'  : final labels everywhere (what a careless pipeline does).
       split='random': random 70/10/20 split per seed (the base paper's setup); always uses
                       final labels, because 'label known at cutoff' has no meaning without a cutoff."""
    n, tt, y = len(df), df["_t"].values, df["_y"].values.astype(int)
    i_tr, i_va = int(0.7 * n), int(0.8 * n)
    if split == "random":
        mode = "leaky"
        perm = np.random.RandomState(seed).permutation(n)
        tr, va, te = np.zeros(n, bool), np.zeros(n, bool), np.zeros(n, bool)
        tr[perm[:i_tr]], va[perm[i_tr:i_va]], te[perm[i_va:]] = True, True, True
        ttr = tva = float("nan")
    else:
        ttr, tva = tt[i_tr], tt[i_va]
        tr, va, te = tt < ttr, (tt >= ttr) & (tt < tva), tt >= tva
    ye = y.copy()
    if mode == "audited":
        ye[tr] = ((y == 1) & (ft < ttr))[tr]        # labels known when training starts
        ye[va] = ((y == 1) & (ft < tva))[va]        # labels known when testing starts
    allE = np.vstack([E[r] for r in RELS]); s, d = allE[:, 0], allE[:, 1]
    known = (y[s] == 1) & ((ft[s] < tt[d]) if mode == "audited" else True)   # fix must be STRICTLY earlier
    num = np.bincount(d, weights=known.astype(float), minlength=n); den = np.bincount(d, minlength=n)
    deg = [np.log1p(np.bincount(E[r][:, 1], minlength=n)) for r in RELS]

    # past-only author experience: number of commits by the same author with a STRICTLY
    # earlier timestamp (same-timestamp commits are processed as one batch).
    seen = {}
    prior = np.zeros(n)

    order = np.argsort(tt, kind="stable")
    sorted_times = tt[order]

    boundaries = np.r_[
        0,
        np.flatnonzero(np.diff(sorted_times) != 0) + 1,
        n
    ]

    authors = df["_auth"].values

    for start, end in zip(boundaries[:-1], boundaries[1:]):
        batch = order[start:end]

        for i in batch:
            prior[i] = seen.get(authors[i], 0)

        for i in batch:
            au = authors[i]
            seen[au] = seen.get(au, 0) + 1

    nb = np.column_stack(deg + [num / np.maximum(den, 1), np.log1p(den), prior])
    raw = np.column_stack([df[BASE].astype(float).values, nb])
    raw = np.sign(raw) * np.log1p(np.abs(raw))
    X = StandardScaler().fit(raw[tr]).transform(raw)          # TRAIN-ONLY statistics
    return X, y, ye, dict(tr=tr, va=va, te=te, ttr=ttr, tva=tva)


# ------------------------------ models ---------------------------------------
class RGCN(nn.Module):
    def __init__(self, din, h, nr, p):
        super().__init__()
        self.s1, self.s2 = nn.Linear(din, h), nn.Linear(h, h)
        self.r1 = nn.ModuleList([nn.Linear(din, h, bias=False) for _ in range(nr)])
        self.r2 = nn.ModuleList([nn.Linear(h, h, bias=False) for _ in range(nr)])
        self.out, self.p = nn.Linear(h, 1), p

    def layer(self, x, G, selfl, rl):
        h = selfl(x)
        for (src, dst, inv), W in zip(G, rl):
            h = h + torch.zeros_like(h).index_add_(0, dst, W(x)[src]) * inv
        return torch.relu(h)

    def forward(self, x, G):
        x = F.dropout(x, self.p, self.training)
        h = F.dropout(self.layer(x, G, self.s1, self.r1), self.p, self.training)
        h = self.layer(h, G, self.s2, self.r2)
        return self.out(F.dropout(h, self.p, self.training)).squeeze(1)


def to_graph(E, n):
    G = []
    for r in RELS:
        e = torch.as_tensor(E[r], dtype=torch.long)
        deg = torch.bincount(e[:, 1], minlength=n).clamp(min=1).float().unsqueeze(1)
        G.append((e[:, 0], e[:, 1], 1.0 / deg))
    return G


def train_rgcn(X, ye, G, S, hp, seed, epochs=EPOCHS):
    """Returns probabilities of (final-epoch model, best-validation-AUPRC checkpoint, best epoch)."""
    torch.manual_seed(seed); np.random.seed(seed)
    Xt, yt, tr, va = torch.tensor(X, dtype=torch.float32), torch.tensor(ye, dtype=torch.float32), torch.tensor(S["tr"]), S["va"]
    model = RGCN(X.shape[1], hp["hidden"], len(RELS), hp["dropout"])
    opt = torch.optim.Adam(model.parameters(), lr=hp["lr"], weight_decay=WD)
    pr = max(ye[S["tr"]].mean(), 1e-6)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((1 - pr) / pr)))
    best_v, best_p, best_ep = -1, None, 0
    for ep in range(epochs):
        model.train(); opt.zero_grad()
        lossf(model(Xt, G)[tr], yt[tr]).backward(); opt.step()
        model.eval()
        with torch.no_grad():
            p = torch.sigmoid(model(Xt, G)).numpy()
        v = average_precision_score(ye[va], p[va])            # validation ONLY
        if v > best_v:
            best_v, best_p, best_ep = v, p.copy(), ep
    return p, best_p, best_ep


# ----------------------------- evaluation ------------------------------------
def pick_threshold(yv, pv):
    c = np.unique(np.quantile(pv, np.linspace(0.02, 0.98, 200)))
    return float(c[int(np.argmax([f1_score(yv, pv >= x, zero_division=0) for x in c]))])


def eval_probs(y, ye, p, S, thr=None):
    if thr is None:
        thr = pick_threshold(ye[S["va"]], p[S["va"]])           # validation labels only
    yt, pt = y[S["te"]], p[S["te"]]                              # test: final (true) labels
    k = max(1, int(0.2 * len(yt))); top = np.argsort(-pt)[:k]; pred = pt >= thr
    return dict(AUPRC=average_precision_score(yt, pt), AUROC=roc_auc_score(yt, pt),
                F1=f1_score(yt, pred, zero_division=0), MCC=matthews_corrcoef(yt, pred),
                R20=yt[top].sum() / max(yt.sum(), 1), thr=thr)


def tabular(X, ye, S, kind, cols, seed):
    """Train a tabular baseline using training rows only."""
    Xs = X[:, cols]

    if kind == "LR":
        m = LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000
        )
    elif kind == "RF":
        m = RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=seed
        )
    else:
        raise ValueError(f"Unsupported tabular model: {kind}")

    m.fit(Xs[S["tr"]], ye[S["tr"]])

    p = np.zeros(len(ye))
    mk = S["va"] | S["te"]
    p[mk] = m.predict_proba(Xs[mk])[:, 1]
    return p


def md(df):
    return "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n" + \
        "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.values)


def agg(rows):
    d = pd.DataFrame(rows); g = d.groupby("model", sort=False)[["AUPRC", "AUROC", "F1", "MCC", "R20"]].agg(["mean", "std"])
    t = pd.DataFrame({"model": g.index})
    for m in ["AUPRC", "AUROC", "F1", "MCC", "R20"]:
        t[m] = [f"{g[(m,'mean')][k]:.3f} ± {g[(m,'std')][k]:.3f}" for k in g.index]
    return d, t.reset_index(drop=True)


def wil(d, a, b, m):
    x, z = (d[d.model == k].sort_values("seed")[m].values for k in (a, b))
    try:
        return wilcoxon(x, z).pvalue
    except Exception:
        return float("nan")


# ------------------------------- main ----------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--gitmeta", required=True)
    ap.add_argument("--mapping", required=True); ap.add_argument("--quick", action="store_true")
    ap.add_argument("--time", default="committer_ts", choices=["committer_ts", "author_ts", "commitdate"])
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    out = lambda f: os.path.join(a.outdir, f)
    seeds = list(range(3 if a.quick else 10))
    TAB = ["LR", "RF"]  # tabular baselines
    df, info = load(a); n = len(df); tt = df["_t"].values
    ft, linfo = label_times(df, a.mapping)
    E = build_edges(df); G = to_graph(E, n)
    ts = lambda x: str(pd.to_datetime(x, unit="s"))

    # ===================== D. TEMPORAL AUDIT =====================
    audit = {"data": info, "label_times": linfo, "commits_used": n}
    # strict check: a source commit must be at a STRICTLY earlier time than its target
    viol = {r: int(((E[r][:, 0] >= E[r][:, 1]) | (tt[E[r][:, 0]] >= tt[E[r][:, 1]])).sum()) for r in RELS}
    audit["edges_per_relation"] = {r: int(len(E[r])) for r in RELS}
    audit["future_edge_violations"] = viol
    assert sum(viol.values()) == 0, "future edge found"
    audit["history_feature_checks"] = history_checks(df)
    audit["tabular_models_run"] = TAB
    audit["random_split_note"] = "random 70/10/20 split per seed, final labels (no label-time relabelling), same past-only graph"
    X, y, ye, S = prepare(df, E, ft, "audited")
    for k in ["tr", "va", "te"]:
        audit[f"{k}_n"] = int(S[k].sum())
        audit[f"{k}_pos_rate_final_labels"] = round(float(y[S[k]].mean()), 4)
        audit[f"{k}_pos_rate_known_at_cutoff"] = round(float(ye[S[k]].mean()), 4)
    audit["train_cutoff"], audit["test_cutoff"] = ts(S["ttr"]), ts(S["tva"])
    audit["order_ok"] = bool(tt[S["tr"]].max() < tt[S["va"]].min() and tt[S["va"]].max() < tt[S["te"]].min())
    audit["scaler_fit_rows"] = int(S["tr"].sum())
    pos = (y == 1) & np.isfinite(ft); delay = (ft[pos] - tt[pos]) / 86400
    audit["bug_label_delay_days"] = {"median": round(float(np.median(delay)), 1), "p90": round(float(np.percentile(delay, 90)), 1)}
    audit["train_buggy_labels_not_yet_known_at_train_cutoff"] = int(((y == 1) & (ft >= S["ttr"]) & S["tr"]).sum())
    yr = pd.Series(y, index=pd.to_datetime(tt, unit="s").year).groupby(level=0).mean().round(3)
    audit["bug_rate_by_year_final_labels"] = {int(k): float(v) for k, v in yr.items()}
    audit["feature_availability"] = {
        "ns,nm,nf,entropy,la,ld,lt,fix,npt": "change metrics of the commit / history before it: available at commit time",
        "graph edges": "only strictly earlier commits (asserted: 0 future or same-timestamp edges)",
        "author experience (prior)": "count of commits by the same author with a strictly earlier timestamp",
        "neighbour past-bug ratio": "counts a neighbour as buggy only if its first fixing commit is dated strictly before the target commit",
        "training/validation labels": "relabelled to what was known at the train / test cutoff (fix not yet committed => clean)",
        "scaler": "fit on training rows only",
        "test set": "never used for any checkpoint, threshold or hyperparameter choice"}

    # ===================== E. TUNING ON VALIDATION =====================
    best, best_v = None, -1
    for h, lr, p in itertools.product(GRID["hidden"], GRID["lr"], GRID["dropout"]):
        hp = dict(hidden=h, lr=lr, dropout=p)
        v = np.mean([average_precision_score(ye[S["va"]], train_rgcn(X, ye, G, S, hp, s)[1][S["va"]]) for s in (100, 101)])
        print(f"tune {hp} val AUPRC={v:.3f}")
        if v > best_v:
            best, best_v = hp, v
    print("best:", best); audit["best_hyperparameters"] = best

    # ===================== E. MAIN RESULTS =====================
    rows, eps = [], []
    base_cols, all_cols = list(range(len(BASE))), list(range(X.shape[1]))
    for s in seeds:
        pf, pb, ep = train_rgcn(X, ye, G, S, best, s); eps.append(ep)
        rows.append(dict(model="R-GCN (A) final epoch, thr 0.5 [original]", seed=s, **eval_probs(y, ye, pf, S, 0.5)))
        rows.append(dict(model="R-GCN (B) best-val checkpoint, thr 0.5", seed=s, **eval_probs(y, ye, pb, S, 0.5)))
        rows.append(dict(model="R-GCN (C) best-val ckpt + val threshold [ours]", seed=s, **eval_probs(y, ye, pb, S)))
        for kind in TAB:
            rows.append(dict(model=f"{kind} (metrics only)", seed=s, **eval_probs(y, ye, tabular(X, ye, S, kind, base_cols, s), S)))
            rows.append(dict(model=f"{kind} (+neighbour feats)", seed=s, **eval_probs(y, ye, tabular(X, ye, S, kind, all_cols, s), S)))
    d, table = agg(rows); d.to_csv(out("results_runs.csv"), index=False)
    A, B, C = list(d.model.unique())[:3]
    stat = pd.DataFrame([dict(comparison="C vs A", metric=m,
                              mean_diff=round(float(d[d.model == C][m].mean() - d[d.model == A][m].mean()), 4),
                              p_value=round(wil(d, C, A, m), 4)) for m in ["AUPRC", "MCC", "F1"]])

    # ===================== D. LEAKY vs AUDITED LABELS =====================
    conds = [("chrono, audited labels", "chrono", "audited"),
             ("chrono, leaky labels", "chrono", "leaky"),
             ("random split, final labels", "random", "leaky")]
    sens = []
    for label, split, mode in conds:
        for s in seeds:
            X2, y2, ye2, S2 = prepare(df, E, ft, mode, split, s)
            c_base, c_all = list(range(len(BASE))), list(range(X2.shape[1]))
            _, pb, _ = train_rgcn(X2, ye2, G, S2, best, s)
            sens.append(dict(model=f"R-GCN | {label}", name="R-GCN", cond=label, seed=s, **eval_probs(y2, ye2, pb, S2)))
            for kind in TAB:
                for tag, cols in ((" (metrics)", c_base), (" (+neigh)", c_all)):
                    sens.append(dict(model=f"{kind}{tag} | {label}", name=f"{kind}{tag}", cond=label, seed=s,
                                     **eval_probs(y2, ye2, tabular(X2, ye2, S2, kind, cols, s), S2)))
        print("done:", label)
    ds, sens_t = agg(sens); ds.to_csv(out("results_split_impact.csv"), index=False)
    rows_st = []
    for nm_ in ds["name"].unique():
        sub = ds[ds.name == nm_]
        a_ = sub[sub.cond == conds[0][0]].sort_values("seed")["AUPRC"].values
        for lab in (conds[1][0], conds[2][0]):
            b_ = sub[sub.cond == lab].sort_values("seed")["AUPRC"].values
            try:
                pv = wilcoxon(b_, a_).pvalue
            except Exception:
                pv = float("nan")
            rows_st.append(dict(model=nm_, comparison=f"{lab} vs {conds[0][0]}",
                                AUPRC_diff=round(float(b_.mean() - a_.mean()), 4), p_value=round(float(pv), 4)))
    split_stat = pd.DataFrame(rows_st)

    audit["mean_best_epoch"] = float(np.mean(eps))
    json.dump(audit, open(out("audit_report.json"), "w"), indent=2, default=str)
    rep = ("# Results\n\n## Temporal audit (D)\n```json\n" + json.dumps(audit, indent=2, default=str) +
           f"\n```\n\n## Test metrics, chronological 70/10/20, {len(seeds)} seeds (E)\n\n" + md(table) +
           "\n\n## Paired Wilcoxon, (C) vs (A)\n\n" + md(stat) +
           f"\n\n## Split and label-leakage impact, {len(seeds)} seeds (D)\n\n" + md(sens_t) +
           "\n\n## AUPRC change vs chrono-audited (paired Wilcoxon; deterministic LR gives a trivial p)\n\n" + md(split_stat) + "\n")
    open(out("results_summary.md"), "w", encoding="utf-8").write(rep); print(rep)


if __name__ == "__main__":
    main()