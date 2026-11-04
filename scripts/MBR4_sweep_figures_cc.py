# Origin: cc
# Purpose: Compare RFD4 recycle strategies (thinking_low / medium / high) on MotifBench for indexed and unindexed: tables + figures in the RFD3/RFD4 write-up style.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""Medium = N002/N003 sets, low/high = N005 sets (same inputs, seeds, layouts). Official per-replicate scores are read
from each overall_summary.csv; the per-problem panels use the same seeded leaderboard bootstrap as
MBR4_motifbench_figures_up.py. SD with ddof=1 over the 3 generation replicates.
Usage: python MBR4_sweep_figures_cc.py --out <dir>"""
import os
import argparse
import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

P = Path(os.environ["MBR4_ROOT"]) / "runs"
MED = P / "MBR4_N003_motifbench-evaluation-of-rfd4-scaffolds"
SWEEP = P / "MBR4_N005_rfd4-recycle-strategy-sweep-thinking-low"
STRATS = [("thinking_low", "_low", SWEEP), ("thinking_medium", "", MED), ("thinking_high", "_high", SWEEP)]
# ordinal (low -> high): one hue, light -> dark, per mode
RAMP = {"indexed": ["#8fd3b5", "#1baf7a", "#0b6b48"], "unindexed": ["#f7cf7a", "#eda100", "#9a6400"]}
INK, GRID, SURFACE = "#3a3a38", "#e1e0d9", "#fcfcfb"
RNG_SEED = 42


def clusters(path):
    if not path.is_file():
        return []
    out = []
    for line in open(path):
        if "assist" in line:
            continue
        c, b = line.split()
        out.append((int(b[:-4].split("_")[-1]), int(c[:-4].split("_")[-1])))
    return out


def boot(sc, rng, n_sub=1000, size=50, alpha=5):
    if not sc:
        return 0.0
    v = []
    for _ in range(n_sub):
        idx = set(rng.choice(100, size, replace=False).tolist())
        n = len({c for b, c in sc if b in idx})
        v.append(100 * ((size + alpha) / size) * n / (n + alpha))
    return float(np.mean(v))


def msd(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1))


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=INK, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    data, overall = {}, []
    for mode in ("indexed", "unindexed"):
        for strat, suf, base in STRATS:
            rng = np.random.default_rng(RNG_SEED)
            per, off, solved, uniq, sr = {}, [], [], [], []
            for r in (1, 2, 3):
                d = base / f"results_{mode}_rep{r}{suf}"
                off.append(float(re.search(r"MotifBench score:\s*([\d.]+)", (d / "overall_summary.csv").read_text()).group(1)))
                rows = list(csv.DictReader(open(d / "summary_by_problem.csv")))
                solved.append(sum(int(x["Num_Solutions"]) > 0 for x in rows))
                uniq.append(np.mean([int(x["Num_Solutions"]) for x in rows]))
                sr.append(np.mean([float(x["Success_Rate"]) for x in rows]))
                for x in rows:
                    p = x["Problem"]
                    e = per.setdefault(p, {"n": [], "sr": [], "score": []})
                    e["n"].append(int(x["Num_Solutions"]))
                    e["sr"].append(float(x["Success_Rate"]))
                    e["score"].append(boot(clusters(d / p / "esm_successful_backbones" / "diversity_cluster.tsv"), rng))
            data[(mode, strat)] = per
            overall.append(dict(mode=mode, strategy=strat, official=msd(off), reps=off, solved=msd(solved),
                                uniq=msd(uniq), sr=msd(sr)))
    problems = sorted(data[("indexed", "thinking_medium")], key=lambda p: int(p[:2]))
    with open(out / "MBR4_sweep_overall.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "strategy", "mb_score_mean", "mb_score_sd", "rep_scores", "solved_mean", "unique_mean",
                    "unique_sd", "success_rate_mean", "success_rate_sd"])
        for o in overall:
            w.writerow([o["mode"], o["strategy"], f"{o['official'][0]:.2f}", f"{o['official'][1]:.2f}",
                        "/".join(f"{x:.2f}" for x in o["reps"]), f"{o['solved'][0]:.2f}", f"{o['uniq'][0]:.2f}",
                        f"{o['uniq'][1]:.2f}", f"{o['sr'][0]:.2f}", f"{o['sr'][1]:.2f}"])
    with open(out / "MBR4_sweep_per_problem.csv", "w", newline="") as f:
        w = csv.writer(f)
        keys = [(m, s) for m in ("indexed", "unindexed") for s, _, _ in STRATS]
        w.writerow(["problem"] + [f"{m} {s} {k}" for m, s in keys for k in ("success_rate", "unique", "mb_score")])
        for p in problems:
            row = [p]
            for k in keys:
                for q in ("sr", "n", "score"):
                    row.append(f"{np.mean(data[k][p][q]):.2f}")
            w.writerow(row)

    # ---- figure 1: overall (score, unique solutions, success rate) by mode x strategy
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, key, lab in zip(axs, ("official", "uniq", "sr"),
                            ("MotifBench score (official)", "Mean unique solutions per problem", "Mean success rate (%)")):
        for j, mode in enumerate(("indexed", "unindexed")):
            for i, (strat, _, _) in enumerate(STRATS):
                o = next(x for x in overall if x["mode"] == mode and x["strategy"] == strat)
                xpos = j * 1.2 + (i - 1) * 0.3
                ax.bar(xpos, o[key][0], 0.3, color=RAMP[mode][i], edgecolor=SURFACE, linewidth=1.0, zorder=3,
                       label=f"{mode} {strat.replace('thinking_', '')}" if key == "official" else None)
                ax.errorbar(xpos, o[key][0], yerr=o[key][1], fmt="none", ecolor=INK, capsize=2, zorder=4)
                ax.text(xpos, o[key][0] + o[key][1] + 0.8, f"{o[key][0]:.1f}", ha="center", fontsize=7, color=INK)
        ax.set_xticks([0, 1.2])
        ax.set_xticklabels(["indexed", "unindexed"])
        ax.set_title(lab, loc="left", fontsize=11)
        style(ax)
    axs[0].legend(frameon=False, fontsize=8, loc="lower left", ncol=2)
    fig.suptitle("RFD4-Proteina recycle strategy (thinking_low / medium / high), mean ± SD over 3 generation replicates",
                 fontsize=10, color=INK)
    plt.tight_layout()
    fig.savefig(out / "MBR4_fig_sweep_overall.png", dpi=150, facecolor="white")
    plt.close(fig)

    # ---- figure 2: per-problem MotifBench score, one panel per mode
    fig, axs = plt.subplots(2, 1, figsize=(15, 9))
    x = np.arange(len(problems)) * 1.2
    for ax, mode in zip(axs, ("indexed", "unindexed")):
        for i, (strat, _, _) in enumerate(STRATS):
            m = [np.mean(data[(mode, strat)][p]["score"]) for p in problems]
            s = [np.std(data[(mode, strat)][p]["score"], ddof=1) for p in problems]
            xi = x + (i - 1) * 0.28
            ax.bar(xi, m, 0.28, color=RAMP[mode][i], edgecolor=SURFACE, linewidth=1.0, zorder=3,
                   label=strat.replace("thinking_", "thinking "))
            ax.errorbar(xi, m, yerr=s, fmt="none", ecolor=INK, elinewidth=1.0, capsize=2, zorder=4)
        ax.set_xticks(x)
        ax.set_xticklabels(problems, rotation=90, fontsize=8)
        ax.set_ylim(0, 112)
        ax.set_ylabel("MotifBench score")
        ax.set_title(f"RFD4 {mode}: MotifBench score per problem (bootstrap)", loc="left", fontsize=11)
        ax.legend(frameon=False, fontsize=9, loc="upper right", ncol=3)
        style(ax)
    plt.tight_layout()
    fig.savefig(out / "MBR4_fig_sweep_per_problem.png", dpi=150, facecolor="white")
    plt.close(fig)
    for o in overall:
        print(f"{o['mode']:10s} {o['strategy']:16s} score {o['official'][0]:6.2f} ± {o['official'][1]:.2f} "
              f"reps {o['reps']} solved {o['solved'][0]:.1f} uniq {o['uniq'][0]:.2f} SR {o['sr'][0]:.2f}")


if __name__ == "__main__":
    main()
