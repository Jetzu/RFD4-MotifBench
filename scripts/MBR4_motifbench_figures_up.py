# Origin: up (adapted from L. Kleiter, RFD3/Plotting/plot_unindexed_fixed_vs_expertguess_fixed.py)
# Purpose: MotifBench figures + tables for RFD4-Proteina (indexed/unindexed, 3 replicates) vs post-bugfix RFD3 (ExpertGuess/Unindexed, 3 replicates), in the style of the RFD3-MotifBench GitHub write-ups.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""Same bootstrap as the leaderboard (write_overall_summary.py: 50/100 subsample x1000, N_max=50, alpha=5),
seeded (RNG_SEED) so per-problem numbers are reproducible. Overall score per replicate = mean over the 30
problems; reported as mean +- SD (ddof=1) across the 3 independent GENERATION replicates.

Usage: python MBR4_motifbench_figures_up.py --out <dir>
Writes: MBR4_fig_rfd4_indexed_vs_unindexed.png, MBR4_fig_rfd4_vs_rfd3_per_problem.png,
        MBR4_fig_overall_and_groups.png, MBR4_fig_unique_solutions_by_redesign.png,
        MBR4_per_problem_all_pipelines.csv, MBR4_overall_all_pipelines.csv
"""
import os
import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

P = Path(os.environ["MBR4_ROOT"])
E = P / "runs/MBR4_N003_motifbench-evaluation-of-rfd4-scaffolds"
K = Path(os.environ["RFD3_RESULTS_DIR"])
# Fixed categorical order (dataviz reference palette slots 1-4, validated light mode: all checks PASS,
# contrast WARN for slots 3-4 -> values also given as tables/CSV). Colour follows the pipeline in every figure.
PIPELINES = [
    ("RFD3 ExpertGuess (fixed)", K / "ExpertGuess_Fixed", ["results", "results_seed_1", "results_seed_2"], "#2a78d6"),
    ("RFD3 Unindexed (fixed)", K / "Unindexed_Fixed", ["results_rep1", "results_rep2", "results_rep3"], "#eb6834"),
    ("RFD4 indexed", E, ["results_indexed_rep1", "results_indexed_rep2", "results_indexed_rep3"], "#1baf7a"),
    ("RFD4 unindexed", E, ["results_unindexed_rep1", "results_unindexed_rep2", "results_unindexed_rep3"], "#eda100"),
]
RNG_SEED = 42
INK = "#3a3a38"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
GROUP = {**{f"{i:02d}": 1 for i in range(1, 11)}, **{f"{i:02d}": 2 for i in range(11, 21)},
         **{f"{i:02d}": 3 for i in range(21, 31)}}


def load_successes_and_cluster(path):
    if not path.is_file():
        return []
    out = []
    for line in open(path):
        if "assist" in line:
            continue
        cluster, bb = line.split()
        out.append((int(bb[:-4].split("_")[-1]), int(cluster[:-4].split("_")[-1])))
    return out


def bootstrap_score(sc, rng, n_sub=1000, size=50, alpha=5):
    if not sc:
        return 0.0
    vals = []
    for _ in range(n_sub):
        idx = set(rng.choice(100, size, replace=False).tolist())
        n = len({c for b, c in sc if b in idx})
        vals.append(100 * ((size + alpha) / size) * n / (n + alpha))
    return float(np.mean(vals))


def load_pipeline(base, reps):
    rng = np.random.default_rng(RNG_SEED)
    out = {}
    for rep in reps:
        for row in csv.DictReader(open(base / rep / "summary_by_problem.csv")):
            p = row["Problem"]
            d = out.setdefault(p, {"n": [], "sr": [], "nov": [], "score": []})
            d["n"].append(int(row["Num_Solutions"]))
            d["sr"].append(float(row["Success_Rate"]))
            d["nov"].append(float(row["Novelty"]))
            d["score"].append(bootstrap_score(
                load_successes_and_cluster(base / rep / p / "esm_successful_backbones" / "diversity_cluster.tsv"), rng))
    return out


def msd(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=INK, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def grouped_bars(ax, problems, series, names, key, ylabel, title, ylim=None, legend_loc="upper right"):
    n = len(names)
    x = np.arange(len(problems)) * 1.2
    unit = 0.86 / n
    for i, name in enumerate(names):
        col = dict((p[0], p[3]) for p in PIPELINES)[name]
        m = [series[name][p][key][0] for p in problems]
        s = [series[name][p][key][1] for p in problems]
        xi = x + (i - (n - 1) / 2) * unit
        ax.bar(xi, m, unit, color=col, label=name, zorder=3, edgecolor=SURFACE, linewidth=1.0)
        ax.errorbar(xi, m, yerr=s, fmt="none", ecolor=INK, elinewidth=1.0, capsize=2, zorder=4)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xticks(x)
    ax.set_xticklabels(problems, rotation=90, fontsize=8)
    ax.legend(frameon=False, loc=legend_loc, fontsize=9)
    style(ax)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = {name: load_pipeline(base, reps) for name, base, reps, _ in PIPELINES}
    problems = sorted(set.intersection(*(set(d) for d in data.values())), key=lambda p: int(p[:2]))
    assert len(problems) == 30, problems
    series = {name: {p: {k: msd(data[name][p][k]) for k in ("n", "sr", "nov", "score")} for p in problems}
              for name in data}
    # overall per replicate -> mean +- SD
    overall = {}
    for name, _, reps, _ in PIPELINES:
        per_rep = [np.mean([data[name][p]["score"][r] for p in problems]) for r in range(len(reps))]
        solved = [sum(data[name][p]["n"][r] > 0 for p in problems) for r in range(len(reps))]
        uniq = [np.mean([data[name][p]["n"][r] for p in problems]) for r in range(len(reps))]
        sr = [np.mean([data[name][p]["sr"][r] for p in problems]) for r in range(len(reps))]
        overall[name] = dict(score=msd(per_rep), solved=msd(solved), uniq=msd(uniq), sr=msd(sr), per_rep=per_rep)
        for g in (1, 2, 3):
            gp = [p for p in problems if GROUP[p[:2]] == g]
            overall[name][f"g{g}_uniq"] = msd([np.mean([data[name][p]["n"][r] for p in gp]) for r in range(len(reps))])
            overall[name][f"g{g}_score"] = msd([np.mean([data[name][p]["score"][r] for p in gp]) for r in range(len(reps))])
            overall[name][f"g{g}_solved"] = msd([sum(data[name][p]["n"][r] > 0 for p in gp) for r in range(len(reps))])

    # ---- tables
    with open(out / "MBR4_per_problem_all_pipelines.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["problem", "group"] + [f"{n} {k} {s}" for n, *_ in PIPELINES
                                           for k in ("success_rate", "unique_solutions", "mb_score") for s in ("mean", "sd")])
        for p in problems:
            row = [p, GROUP[p[:2]]]
            for n, *_ in PIPELINES:
                for k in ("sr", "n", "score"):
                    row += [f"{series[n][p][k][0]:.2f}", f"{series[n][p][k][1]:.2f}"]
            w.writerow(row)
    with open(out / "MBR4_overall_all_pipelines.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pipeline", "mb_score_mean", "mb_score_sd", "rep_scores", "solved_mean", "solved_sd",
                    "mean_unique_solutions", "sd", "mean_success_rate", "sd"]
                   + [f"group{g}_{k}" for g in (1, 2, 3) for k in ("solved", "unique", "score")])
        for n, *_ in PIPELINES:
            o = overall[n]
            w.writerow([n, f"{o['score'][0]:.2f}", f"{o['score'][1]:.2f}", "/".join(f"{x:.2f}" for x in o["per_rep"]),
                        f"{o['solved'][0]:.2f}", f"{o['solved'][1]:.2f}", f"{o['uniq'][0]:.2f}", f"{o['uniq'][1]:.2f}",
                        f"{o['sr'][0]:.2f}", f"{o['sr'][1]:.2f}"]
                       + [f"{o[f'g{g}_{k}'][0]:.2f}" for g in (1, 2, 3) for k in ("solved", "uniq", "score")])

    def score_box(ax, names):
        txt = "\n".join(f"{n}: {overall[n]['score'][0]:.2f} ± {overall[n]['score'][1]:.2f}" for n in names)
        ax.text(0.98, 0.95, "Overall MotifBench score\n" + txt, transform=ax.transAxes, ha="right", va="top",
                fontsize=9, color=INK, bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE, edgecolor="#c3c2b7"))

    def three_panel(names, fname, subtitle):
        fig, axs = plt.subplots(3, 1, figsize=(15, 14))
        grouped_bars(axs[0], problems, series, names, "sr", "Success rate (%)", "Success rate per problem", (0, 105))
        grouped_bars(axs[1], problems, series, names, "n", "Unique solutions", "Number of unique solutions per problem")
        grouped_bars(axs[2], problems, series, names, "score", "MotifBench score",
                     "Official MotifBench score per problem (bootstrap)", (0, 100 + 9 * len(names) + 10),
                     legend_loc="upper left")
        axs[2].set_yticks(range(0, 101, 20))
        score_box(axs[2], names)
        fig.suptitle(subtitle, fontsize=9, y=0.995, color=INK, wrap=True)
        plt.tight_layout(rect=(0, 0, 1, 0.975))
        fig.savefig(out / fname, dpi=150, facecolor="white")
        plt.close(fig)

    note = ("Bars = mean of 3 independent GENERATION replicates (100 designs/problem each), error bars = SD (ddof=1). "
            "MotifBench score = official leaderboard bootstrap (50/100 subsample x1000, N_max=50), seeded.")
    three_panel(["RFD4 indexed", "RFD4 unindexed"], "MBR4_fig_rfd4_indexed_vs_unindexed.png",
                "RFD4-Proteina: indexed (MotifBench example contigs, gap lengths sampled per design) vs unindexed "
                "(RFD4 places the motif segments itself).\n" + note)
    three_panel([p[0] for p in PIPELINES], "MBR4_fig_rfd4_vs_rfd3_per_problem.png",
                "RFD4-Proteina vs post-bugfix RFD3 (L. Kleiter / B. Trippe triplicates), same contigs, same MotifBench "
                "install.\n" + note)

    # ---- overall + per-group
    names = [p[0] for p in PIPELINES]
    cols = [p[3] for p in PIPELINES]
    fig, axs = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw=dict(width_ratios=[1, 2]))
    m = [overall[n]["score"][0] for n in names]
    s = [overall[n]["score"][1] for n in names]
    axs[0].bar(range(4), m, 0.7, color=cols, edgecolor=SURFACE, linewidth=1.0, zorder=3)
    axs[0].errorbar(range(4), m, yerr=s, fmt="none", ecolor=INK, capsize=3, zorder=4)
    for i, (mm, ss) in enumerate(zip(m, s)):
        axs[0].text(i, mm + ss + 1.2, f"{mm:.1f} ± {ss:.1f}", ha="center", fontsize=9, color=INK)
    axs[0].set_xticks(range(4))
    axs[0].set_xticklabels([n.replace(" (", "\n(") for n in names], fontsize=8)
    axs[0].set_ylabel("MotifBench score")
    axs[0].set_title("Overall MotifBench score (mean ± SD, 3 replicates)", loc="left", fontsize=11)
    axs[0].set_ylim(0, max(m) + 12)
    style(axs[0])
    x = np.arange(3) * 1.2
    unit = 0.86 / 4
    for i, n in enumerate(names):
        gm = [overall[n][f"g{g}_uniq"][0] for g in (1, 2, 3)]
        gs = [overall[n][f"g{g}_uniq"][1] for g in (1, 2, 3)]
        xi = x + (i - 1.5) * unit
        axs[1].bar(xi, gm, unit, color=cols[i], label=n, edgecolor=SURFACE, linewidth=1.0, zorder=3)
        axs[1].errorbar(xi, gm, yerr=gs, fmt="none", ecolor=INK, capsize=2, zorder=4)
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(["Group 1 (01-10)\n1 segment", "Group 2 (11-20)\n2 segments", "Group 3 (21-30)\n3+ segments"])
    axs[1].set_ylabel("Mean unique solutions per problem")
    axs[1].set_title("Unique solutions by MotifBench group", loc="left", fontsize=11)
    axs[1].legend(frameon=False, fontsize=9)
    style(axs[1])
    plt.tight_layout()
    fig.savefig(out / "MBR4_fig_overall_and_groups.png", dpi=150, facecolor="white")
    plt.close(fig)

    # ---- unique solutions sorted by % of motif redesigned (small multiples instead of a second y-axis)
    seg = json.load(open(P / "in/specs/seg_map.json"))
    pct = {p: 100 * len(seg[p]["redesign"]) / sum(s["length"] for s in seg[p]["segments"]) for p in problems}
    order = sorted(problems, key=lambda p: (pct[p], int(p[:2])))
    fig, (a0, a1) = plt.subplots(2, 1, figsize=(15, 8), sharex=True, gridspec_kw=dict(height_ratios=[1, 3]))
    xx = np.arange(len(order)) * 1.2
    a0.plot(xx, [pct[p] for p in order], color="#4a3aa6", lw=2, marker="o", ms=5)
    a0.set_ylabel("% motif\nredesigned")
    a0.set_ylim(-5, 108)
    a0.set_title("Unique solutions per problem, sorted by % of motif residues redesigned (MotifBench UNK)",
                 loc="left", fontsize=11)
    style(a0)
    grouped_bars(a1, order, series, names, "n", "Unique solutions (/100)", "", legend_loc="upper left")
    a1.set_xticks(xx)
    plt.tight_layout()
    fig.savefig(out / "MBR4_fig_unique_solutions_by_redesign.png", dpi=150, facecolor="white")
    plt.close(fig)

    for n in names:
        o = overall[n]
        print(f"{n:26s} score {o['score'][0]:6.2f} ± {o['score'][1]:.2f}  reps {['%.2f' % v for v in o['per_rep']]}  "
              f"solved {o['solved'][0]:.1f}  uniq {o['uniq'][0]:.2f}  SR {o['sr'][0]:.2f}")


if __name__ == "__main__":
    main()
