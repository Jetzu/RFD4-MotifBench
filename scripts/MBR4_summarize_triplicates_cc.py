# Origin: cc
# Purpose: Aggregate official MotifBench summaries of 3 replicate sets per mode (indexed / unindexed) into mean +- SD tables.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""
Reads, for every <mode>_rep<r>, the files written by the official scripts/summarize_results.sh:
  results_<mode>_rep<r>/summary_by_problem.csv and overall_summary.csv ("MotifBench score: X" line).
Also recomputes the per-problem MotifBench score with the official bootstrap (write_overall_summary.py:
50-of-100 subsample x1000, alpha 5) from esm_successful_backbones/diversity_cluster.tsv, seeded here
so the per-problem table is reproducible (the official script is unseeded; its overall score is
reported as written).

Outputs (to --out): MBR4_overall_by_set.csv, MBR4_overall_mean_sd.csv, MBR4_by_problem.csv,
MBR4_by_group_mean_sd.csv
"""
import argparse
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd


def load_successes_and_cluster(fn):
    if not os.path.isfile(fn):
        return []
    out = []
    for line in open(fn):
        if "assist" in line:
            continue
        cluster, bb = line.split()
        out.append((int(bb[:-4].split("_")[-1]), int(cluster[:-4].split("_")[-1])))
    return out


def mb_score(n, n_max=50, alpha=5):
    return 100 * ((n_max + alpha) / n_max) * n / (n + alpha)


def mb_bootstrap(sc, rng, n_sub=1000, size=50):
    vals = []
    for _ in range(n_sub):
        idx = set(rng.choice(100, size, replace=False).tolist())
        vals.append(mb_score(len({c for b, c in sc if b in idx}), n_max=size))
    return float(np.mean(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-dir", required=True)
    ap.add_argument("--test-cases", default=os.path.join(os.environ.get("MOTIFBENCH_DIR", "."), "test_cases.csv"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    ev, out = Path(a.eval_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tc = pd.read_csv(a.test_cases)
    group = {f"{i + 1:02d}_{p}": g for i, (p, g) in enumerate(zip(tc.pdb_id, tc.group))}
    rows, prob_rows, grp_rows = [], [], []
    rng = np.random.default_rng(0)
    for mode in ("indexed", "unindexed"):
        for r in range(1, a.reps + 1):
            d = ev / f"results_{mode}_rep{r}"
            ov = d / "overall_summary.csv"
            if not ov.exists():
                continue
            txt = ov.read_text()
            score = float(re.search(r"MotifBench score:\s*([\d.]+)", txt).group(1))
            g = pd.read_csv(ov, nrows=4)
            overall = g[g.Group.astype(str) == "overall"].iloc[0]
            rows.append(dict(mode=mode, rep=r, MotifBench_score=score,
                             Number_Solved=overall.Number_Solved,
                             Mean_Num_Solutions=overall.Mean_Num_Solutions,
                             Mean_Novelty=overall.Mean_Novelty,
                             Mean_Success_rate=overall.Mean_Success_rate))
            for _, gr in g.iterrows():
                grp_rows.append(dict(mode=mode, rep=r, **gr.to_dict()))
            bp = pd.read_csv(d / "summary_by_problem.csv")
            for _, p in bp.iterrows():
                sc = load_successes_and_cluster(d / p.Problem / "esm_successful_backbones" / "diversity_cluster.tsv")
                prob_rows.append(dict(mode=mode, rep=r, problem=p.Problem, group=group[p.Problem],
                                      Num_Solutions=p.Num_Solutions, Novelty=p.Novelty,
                                      Success_Rate=p.Success_Rate, Num_Evaluated=p.Num_Evaluated,
                                      MB_score_bootstrap=mb_bootstrap(sc, rng)))
    by_set = pd.DataFrame(rows)
    by_set.to_csv(out / "MBR4_overall_by_set.csv", index=False, float_format="%.3f")
    agg = by_set.groupby("mode").agg(["mean", "std", "count"]).drop(columns="rep")
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    agg.to_csv(out / "MBR4_overall_mean_sd.csv", float_format="%.3f")
    probs = pd.DataFrame(prob_rows)
    wide = probs.pivot_table(index=["problem", "group"], columns=["mode"],
                             values=["Num_Solutions", "Success_Rate", "MB_score_bootstrap"],
                             aggfunc=["mean", "std"])
    wide.columns = ["_".join(c) for c in wide.columns]
    wide.reset_index().to_csv(out / "MBR4_by_problem.csv", index=False, float_format="%.2f")
    probs.to_csv(out / "MBR4_by_problem_long.csv", index=False, float_format="%.3f")
    grp = pd.DataFrame(grp_rows).drop(columns="rep").groupby(["mode", "Group"]).agg(["mean", "std"])
    grp.columns = [f"{a}_{b}" for a, b in grp.columns]
    grp.to_csv(out / "MBR4_by_group_mean_sd.csv", float_format="%.3f")
    print(by_set.to_string(index=False))
    print(agg.to_string())


if __name__ == "__main__":
    main()
