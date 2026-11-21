"""
make_gitmeta.py  --  build <Project>_gitmeta.csv from a git clone, in the same layout as HBase_gitmeta.csv

Columns written (same order as HBase_gitmeta.csv):
    transactionid, commit, author_email, author_name, author_ts, committer_ts, n_files_git, files_git
files_git = files touched by the commit, joined with ';'. Timestamps are Unix seconds.

Usage:
    git clone --filter=blob:none --no-checkout https://github.com/apache/hadoop.git other_projects/hadoop_repo
    python3 make_gitmeta.py --repo other_projects/hadoop_repo [other_projects/second_clone ...] \
        --commits other_projects/Hadoop_commitsID.csv --out other_projects/Hadoop_gitmeta.csv

The commit list is the dataset's <Project>_commitsID.csv (columns: commit, transactionid).
Only commits listed there are written. Commits missing from the clone are counted and reported.
"""
import argparse
import subprocess
import sys

import pandas as pd

RS, US = "\x1e", "\x1f"          # record / unit separators, safe against any text in names or paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, nargs="+", help="path(s) to git clone(s); commits are looked up in each in turn")
    ap.add_argument("--commits", required=True, help="<Project>_commitsID.csv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    ids = pd.read_csv(a.commits, sep=r"\s+", engine="python", dtype=str)
    ids.columns = [c.strip().lower() for c in ids.columns]
    if not {"commit", "transactionid"} <= set(ids.columns):
        sys.exit(f"Expected columns 'commit' and 'transactionid' in {a.commits}, found {list(ids.columns)}")
    tid = dict(zip(ids["commit"], ids["transactionid"]))
    print(f"Commits requested: {len(tid)}")

    rows = {}

    def read_repo(repo):
        cmd = ["git", "-C", repo, "log", "--all", "--no-renames", "--name-only",
               f"--format={RS}%H{US}%ae{US}%an{US}%at{US}%ct"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        cur = None

        def close(rec):
            if rec and rec["commit"] in tid and rec["commit"] not in rows:
                files = [f for f in rec["files"] if f]
                rows[rec["commit"]] = dict(
                    transactionid=int(tid[rec["commit"]]), commit=rec["commit"],
                    author_email=rec["ae"], author_name=rec["an"],
                    author_ts=rec["at"], committer_ts=rec["ct"],
                    n_files_git=len(files), files_git=";".join(files))

        for line in proc.stdout:
            line = line.rstrip("\n")
            if line.startswith(RS):
                close(cur)
                h, ae, an, at, ct = line[1:].split(US)
                cur = dict(commit=h, ae=ae, an=an, at=at, ct=ct, files=[])
            elif cur is not None and line:
                cur["files"].append(line)
        close(cur)
        proc.wait()
        if proc.returncode != 0:
            sys.exit(f"git log failed for {repo}; check that it is a git clone")

    for repo in a.repo:
        before = len(rows)
        read_repo(repo)
        print(f"{repo}: {len(rows) - before} new commits matched (total {len(rows)} of {len(tid)})")

    out = pd.DataFrame(list(rows.values())).sort_values("transactionid")
    cols = ["transactionid", "commit", "author_email", "author_name", "author_ts",
            "committer_ts", "n_files_git", "files_git"]
    out[cols].to_csv(a.out, index=False)

    missing = len(tid) - len(out)
    print(f"Commits found in the clone: {len(out)}   missing: {missing} ({missing / max(len(tid), 1):.1%})")
    print(f"Commits with no file list (merges etc.): {(out.n_files_git == 0).sum()}")
    print("Wrote", a.out)
    if missing / max(len(tid), 1) > 0.05:
        print("WARNING: more than 5% of commits are missing from the clone; tell me before continuing.")


if __name__ == "__main__":
    main()