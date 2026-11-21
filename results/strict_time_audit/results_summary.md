# Results

## Temporal audit (D)
```json
{
  "data": {
    "share_rows_ns==ndev==exp": 1.0,
    "nan_feature_cells": 33,
    "rows_input": 16726,
    "rows_after_merge": 16726,
    "dropped_no_time": 0,
    "time_source": "committer_ts"
  },
  "label_times": {
    "mapping_pairs": 32160,
    "pairs_with_fix_in_data": 32160,
    "buggy_commits": 4418,
    "buggy_without_matched_fix": 0
  },
  "commits_used": 16726,
  "edges_per_relation": {
    "same_author": 66384,
    "same_file": 64719,
    "same_author_same_file": 12637
  },
  "future_edge_violations": {
    "same_author": 0,
    "same_file": 0,
    "same_author_same_file": 0
  },
  "history_feature_checks": {
    "nf_vs_git_file_count": 0.994,
    "npt_vs_past_only_count": 0.352,
    "npt_vs_all_time_count": 0.379
  },
  "tabular_models_run": [
    "LR",
    "RF"
  ],
  "random_split_note": "random 70/10/20 split per seed, final labels (no label-time relabelling), same past-only graph",
  "tr_n": 11708,
  "tr_pos_rate_final_labels": 0.3159,
  "tr_pos_rate_known_at_cutoff": 0.2771,
  "va_n": 1672,
  "va_pos_rate_final_labels": 0.1681,
  "va_pos_rate_known_at_cutoff": 0.0604,
  "te_n": 3346,
  "te_pos_rate_final_labels": 0.1309,
  "te_pos_rate_known_at_cutoff": 0.1309,
  "train_cutoff": "2016-03-02 09:04:19",
  "test_cutoff": "2017-05-02 21:05:54",
  "order_ok": true,
  "scaler_fit_rows": 11708,
  "bug_label_delay_days": {
    "median": 186.2,
    "p90": 946.5
  },
  "train_buggy_labels_not_yet_known_at_train_cutoff": 455,
  "bug_rate_by_year_final_labels": {
    "2007": 0.88,
    "2008": 0.589,
    "2009": 0.277,
    "2010": 0.335,
    "2011": 0.308,
    "2012": 0.333,
    "2013": 0.301,
    "2014": 0.251,
    "2015": 0.209,
    "2016": 0.179,
    "2017": 0.188,
    "2018": 0.122,
    "2019": 0.037
  },
  "feature_availability": {
    "ns,nm,nf,entropy,la,ld,lt,fix,npt": "change metrics of the commit / history before it: available at commit time",
    "graph edges": "only earlier commits (asserted: 0 future edges)",
    "author experience (prior)": "count of EARLIER commits by the same author",
    "neighbour past-bug ratio": "counts a neighbour as buggy only if its first fixing commit is dated <= the target commit",
    "training/validation labels": "relabelled to what was known at the train / test cutoff (fix not yet committed => clean)",
    "scaler": "fit on training rows only",
    "test set": "never used for any checkpoint, threshold or hyperparameter choice"
  },
  "best_hyperparameters": {
    "hidden": 64,
    "lr": 0.005,
    "dropout": 0.2
  },
  "mean_best_epoch": 57.333333333333336
}
```

## Test metrics, chronological 70/10/20, 3 seeds (E)

| model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|
| R-GCN (A) final epoch, thr 0.5 [original] | 0.398 ± 0.012 | 0.787 ± 0.004 | 0.428 ± 0.011 | 0.333 ± 0.013 | 0.533 ± 0.009 |
| R-GCN (B) best-val checkpoint, thr 0.5 | 0.413 ± 0.004 | 0.790 ± 0.003 | 0.430 ± 0.004 | 0.334 ± 0.005 | 0.543 ± 0.006 |
| R-GCN (C) best-val ckpt + val threshold [ours] | 0.413 ± 0.004 | 0.790 ± 0.003 | 0.298 ± 0.023 | 0.306 ± 0.019 | 0.543 ± 0.006 |
| LR (metrics only) | 0.431 ± 0.000 | 0.803 ± 0.000 | 0.436 ± 0.000 | 0.350 ± 0.000 | 0.553 ± 0.000 |
| LR (+neighbour feats) | 0.430 ± 0.000 | 0.797 ± 0.000 | 0.420 ± 0.000 | 0.348 ± 0.000 | 0.559 ± 0.000 |
| RF (metrics only) | 0.409 ± 0.005 | 0.822 ± 0.001 | 0.373 ± 0.038 | 0.312 ± 0.026 | 0.602 ± 0.003 |
| RF (+neighbour feats) | 0.404 ± 0.001 | 0.810 ± 0.001 | 0.290 ± 0.043 | 0.273 ± 0.028 | 0.566 ± 0.012 |

## Paired Wilcoxon, (C) vs (A)

| comparison | metric | mean_diff | p_value |
|---|---|---|---|
| C vs A | AUPRC | 0.0145 | 0.5 |
| C vs A | MCC | -0.0268 | 0.5 |
| C vs A | F1 | -0.1296 | 0.25 |

## Split and label-leakage impact, 3 seeds (D)

| model | AUPRC | AUROC | F1 | MCC | R20 |
|---|---|---|---|---|---|
| R-GCN | chrono, audited labels | 0.413 ± 0.004 | 0.790 ± 0.003 | 0.298 ± 0.023 | 0.307 ± 0.018 | 0.544 ± 0.005 |
| LR (metrics) | chrono, audited labels | 0.431 ± 0.000 | 0.803 ± 0.000 | 0.436 ± 0.000 | 0.350 ± 0.000 | 0.553 ± 0.000 |
| LR (+neigh) | chrono, audited labels | 0.430 ± 0.000 | 0.797 ± 0.000 | 0.420 ± 0.000 | 0.348 ± 0.000 | 0.559 ± 0.000 |
| RF (metrics) | chrono, audited labels | 0.409 ± 0.005 | 0.822 ± 0.001 | 0.373 ± 0.038 | 0.312 ± 0.026 | 0.602 ± 0.003 |
| RF (+neigh) | chrono, audited labels | 0.404 ± 0.001 | 0.810 ± 0.001 | 0.290 ± 0.043 | 0.273 ± 0.028 | 0.566 ± 0.012 |
| R-GCN | chrono, leaky labels | 0.447 ± 0.005 | 0.815 ± 0.004 | 0.449 ± 0.010 | 0.358 ± 0.011 | 0.570 ± 0.003 |
| LR (metrics) | chrono, leaky labels | 0.434 ± 0.000 | 0.805 ± 0.000 | 0.444 ± 0.000 | 0.350 ± 0.000 | 0.562 ± 0.000 |
| LR (+neigh) | chrono, leaky labels | 0.463 ± 0.000 | 0.820 ± 0.000 | 0.464 ± 0.000 | 0.375 ± 0.000 | 0.591 ± 0.000 |
| RF (metrics) | chrono, leaky labels | 0.413 ± 0.005 | 0.827 ± 0.001 | 0.471 ± 0.004 | 0.385 ± 0.007 | 0.600 ± 0.002 |
| RF (+neigh) | chrono, leaky labels | 0.445 ± 0.001 | 0.831 ± 0.001 | 0.469 ± 0.003 | 0.382 ± 0.003 | 0.600 ± 0.004 |
| R-GCN | random split, final labels | 0.719 ± 0.015 | 0.854 ± 0.007 | 0.650 ± 0.002 | 0.524 ± 0.002 | 0.555 ± 0.006 |
| LR (metrics) | random split, final labels | 0.601 ± 0.015 | 0.793 ± 0.010 | 0.588 ± 0.010 | 0.424 ± 0.010 | 0.484 ± 0.010 |
| LR (+neigh) | random split, final labels | 0.650 ± 0.016 | 0.827 ± 0.007 | 0.617 ± 0.013 | 0.467 ± 0.018 | 0.516 ± 0.005 |
| RF (metrics) | random split, final labels | 0.649 ± 0.020 | 0.829 ± 0.005 | 0.615 ± 0.008 | 0.461 ± 0.004 | 0.512 ± 0.006 |
| RF (+neigh) | random split, final labels | 0.706 ± 0.020 | 0.852 ± 0.008 | 0.646 ± 0.005 | 0.509 ± 0.008 | 0.543 ± 0.009 |

## AUPRC change vs chrono-audited (paired Wilcoxon; deterministic LR gives a trivial p)

| model | comparison | AUPRC_diff | p_value |
|---|---|---|---|
| R-GCN | chrono, leaky labels vs chrono, audited labels | 0.0338 | 0.25 |
| R-GCN | random split, final labels vs chrono, audited labels | 0.3057 | 0.25 |
| LR (metrics) | chrono, leaky labels vs chrono, audited labels | 0.0027 | 0.25 |
| LR (metrics) | random split, final labels vs chrono, audited labels | 0.1698 | 0.25 |
| LR (+neigh) | chrono, leaky labels vs chrono, audited labels | 0.0326 | 0.25 |
| LR (+neigh) | random split, final labels vs chrono, audited labels | 0.2198 | 0.25 |
| RF (metrics) | chrono, leaky labels vs chrono, audited labels | 0.0041 | 1.0 |
| RF (metrics) | random split, final labels vs chrono, audited labels | 0.2399 | 0.25 |
| RF (+neigh) | chrono, leaky labels vs chrono, audited labels | 0.0414 | 0.25 |
| RF (+neigh) | random split, final labels vs chrono, audited labels | 0.3022 | 0.25 |
