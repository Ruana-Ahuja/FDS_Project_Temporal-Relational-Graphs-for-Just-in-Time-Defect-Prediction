import os
import json
import numpy as np
import pandas as pd
from types import SimpleNamespace
from sklearn.preprocessing import StandardScaler
import jit_temporal_audit as j
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

INPUT = "data/HBase_input.csv"
GITMETA = "data/HBase_gitmeta.csv"
MAPPING = "data/HBase_mapping.csv"
OUT = "results_npt_sensitivity"

os.makedirs(OUT, exist_ok=True)

# Load original data and identify originally missing npt values.
raw = j.read_any(INPUT)
missing_map = raw.groupby("transactionid")["npt"].apply(
    lambda x: pd.to_numeric(x, errors="coerce").isna().any()
)

args = SimpleNamespace(input=INPUT, gitmeta=GITMETA, time="committer_ts")
df, info = j.load(args)
missing = (
    df["transactionid"].map(missing_map)
    .fillna(False).astype(float).to_numpy()
)

# Reuse the original graph, labels, split and preprocessing.
ft, label_info = j.label_times(df, MAPPING)
E = j.build_edges(df)
G = j.to_graph(E, len(df))
X, y, ye, S = j.prepare(df, E, ft, "audited")

# A: Original zero-imputed features.
XA = X.copy()

# B: Original features plus a train-standardized missingness indicator.
indicator_scaler = StandardScaler().fit(missing[S["tr"]].reshape(-1, 1))
indicator_scaled = indicator_scaler.transform(
    missing.reshape(-1, 1)
).ravel()
XB = np.column_stack([X, indicator_scaled])

# C: Remove npt (column index 8 in the original feature matrix).
XC = np.delete(X, 8, axis=1)

variants = {
    "A_current_zero_imputation": XA,
    "B_missingness_indicator": XB,
    "C_without_npt": XC,
}

# Fixed settings recovered from the original audit report.
hp = {"hidden": 64, "lr": 0.005, "dropout": 0.2}
seeds = list(range(10))
models = ["R-GCN", "LR", "HGB"]
rows = []

print("Rows:", len(df))
print("Originally missing npt:", int(missing.sum()))
print("Split sizes:", {
    k: int(S[k].sum()) for k in ("tr", "va", "te")
})
print("Fixed R-GCN settings:", hp)
print("Seeds:", seeds)
print("Starting sensitivity experiments...")

for variant_name, Xv in variants.items():
    print("\nVARIANT:", variant_name, "| features:", Xv.shape[1])

    for seed in seeds:
        # R-GCN: best validation-AUPRC checkpoint.
        _, probs, best_epoch = j.train_rgcn(
            Xv, ye, G, S, hp, seed
        )
        metrics = j.eval_probs(y, ye, probs, S)
        rows.append({
            "variant": variant_name,
            "model": "R-GCN",
            "seed": seed,
            "best_epoch": best_epoch,
            **metrics
        })

        # Tabular models use the complete feature matrix,
        # including the same neighbour features.
        cols = list(range(Xv.shape[1]))
        for kind in ("LR", "HGB"):
            probs = j.tabular(Xv, ye, S, kind, cols, seed)
            metrics = j.eval_probs(y, ye, probs, S)
            rows.append({
                "variant": variant_name,
                "model": kind,
                "seed": seed,
                "best_epoch": None,
                **metrics
            })

        print("  completed seed", seed)

# Save individual runs and aggregate summaries.
runs = pd.DataFrame(rows)
runs.to_csv(os.path.join(OUT, "npt_sensitivity_runs.csv"), index=False)

metrics = ["AUPRC", "AUROC", "F1", "MCC", "R20"]
summary = (
    runs.groupby(["variant", "model"])[metrics]
    .agg(["mean", "std"])
)
summary.to_csv(os.path.join(OUT, "npt_sensitivity_summary.csv"))

config = {
    "timestamp": "committer_ts",
    "split": "original chronological audited split",
    "seeds": seeds,
    "rgcn_hyperparameters": hp,
    "models": models,
    "variants": list(variants.keys()),
    "missing_npt_count": int(missing.sum()),
    "training_rows": int(S["tr"].sum()),
    "validation_rows": int(S["va"].sum()),
    "test_rows": int(S["te"].sum()),
    "note": "Fixed-hyperparameter sensitivity analysis; validation-based threshold selection; final test labels used only for final metrics."
}
with open(os.path.join(OUT, "experiment_config.json"), "w") as f:
    json.dump(config, f, indent=2)

print("\nEXPERIMENT COMPLETE")
print("\nSUMMARY (mean and standard deviation):")
for (variant, model), group in runs.groupby(["variant", "model"], sort=False):
    print(f"\n{variant} | {model}")
    for metric in metrics:
        print(
            f"  {metric}: {group[metric].mean():.4f} "
            f"+/- {group[metric].std():.4f}"
        )

print("\nFiles saved in:", OUT)
