# Origin: cc
# Purpose: Build the MotifBench submission packages (scaffolds, full evaluation, summaries) per mode/replicate and a README with results + methods + compute.
"""
Layout written to --out (deliverables/):
  submission_<mode>/rep<r>/MBR4_scaffolds_<mode>_rep<r>.zip   {case}/{case}_{i}.pdb + scaffold_info.csv
  submission_<mode>/rep<r>/MBR4_evaluation_<mode>_rep<r>.tar.gz  full Scaffold-Lab output per case
  submission_<mode>/rep<r>/summary_by_problem.csv, overall_summary.csv   (official summarize_results.sh)
  summary/ (triplicate tables, from MBR4_summarize_triplicates_cc.py)
  MBR4_README_submission.md
"""
import argparse
import re
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pandas as pd

MODES = ("indexed", "unindexed")


def zip_scaffolds(src, dst):
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for case_dir in sorted(Path(src).glob("[0-9][0-9]_*")):
            for f in sorted(case_dir.iterdir()):
                if f.suffix == ".pdb" or f.name == "scaffold_info.csv":
                    z.write(f, f"scaffolds/{case_dir.name}/{f.name}")


def gen_gpu_hours(job):
    try:
        out = subprocess.run(["sacct", "-j", str(job), "-X", "-n", "--format=ElapsedRaw,NodeList"],
                             capture_output=True, text=True).stdout
        secs = [int(l.split()[0]) for l in out.splitlines() if l.strip()]
        return sum(secs) / 3600, len(secs)
    except Exception:  # noqa: BLE001
        return float("nan"), 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-dir", required=True)
    ap.add_argument("--eval-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gen-job", default="621780")
    a = ap.parse_args()
    gen, ev, out = Path(a.gen_dir), Path(a.eval_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for mode in MODES:
        for r in (1, 2, 3):
            d = out / f"submission_{mode}" / f"rep{r}"
            d.mkdir(parents=True, exist_ok=True)
            zip_scaffolds(gen / f"scaffolds_{mode}_rep{r}", d / f"MBR4_scaffolds_{mode}_rep{r}.zip")
            res = ev / f"results_{mode}_rep{r}"
            with tarfile.open(d / f"MBR4_evaluation_{mode}_rep{r}.tar.gz", "w:gz") as t:
                t.add(res, arcname=f"evaluation_{mode}_rep{r}")
            for f in ("summary_by_problem.csv", "overall_summary.csv"):
                shutil.copy(res / f, d / f"MBR4_{f}")
            txt = (res / "overall_summary.csv").read_text()
            score = float(re.search(r"MotifBench score:\s*([\d.]+)", txt).group(1))
            qc = pd.read_csv(gen / f"scaffolds_{mode}_rep{r}" / "MBR4_qc.tsv", sep="\t", header=None,
                             names=["case", "i", "placement", "rmsd", "repair", "src"])
            rows.append(dict(mode=mode, rep=r, score=score, n_pdb=len(qc),
                             n_repaired=int(qc.repair.fillna("").astype(str).str.startswith("window").sum()),
                             median_design_motif_rmsd=float(qc.rmsd.median())))
    gpu_h, n_tasks = gen_gpu_hours(a.gen_job)
    summ = out / "summary"
    mean_sd = pd.read_csv(summ / "MBR4_overall_mean_sd.csv")
    by_group = pd.read_csv(summ / "MBR4_by_group_mean_sd.csv")
    sets = pd.DataFrame(rows)
    sets.to_csv(summ / "MBR4_sets_qc.csv", index=False, float_format="%.3f")

    def fmt(mode, col):
        m = mean_sd[mean_sd["mode"] == mode]
        return f"{m[col + '_mean'].iloc[0]:.2f} ± {m[col + '_std'].iloc[0]:.2f}"

    lines = ["# RFD4-Proteina on MotifBench v1 (30 problems) — indexed and unindexed", "",
             "## Results (official MotifBench score; mean ± SD over 3 independently generated and evaluated scaffold sets)", "",
             "| Mode | MotifBench score | Problems solved | Mean unique solutions | Mean novelty | Mean success rate (%) |",
             "|---|---|---|---|---|---|"]
    for mode in MODES:
        lines.append(f"| {mode} | {fmt(mode, 'MotifBench_score')} | {fmt(mode, 'Number_Solved')} | "
                     f"{fmt(mode, 'Mean_Num_Solutions')} | {fmt(mode, 'Mean_Novelty')} | {fmt(mode, 'Mean_Success_rate')} |")
    lines += ["", "Per replicate:", "", "| Mode | Rep | Score | PDBs | Unindexed placements repaired | Median design motif bb RMSD (Å) |",
              "|---|---|---|---|---|---|"]
    for _, s in sets.iterrows():
        lines.append(f"| {s['mode']} | {s.rep} | {s.score:.2f} | {s.n_pdb} | {s.n_repaired} | {s.median_design_motif_rmsd:.3f} |")
    lines += ["", "Per-group tables: `summary/MBR4_by_group_mean_sd.csv`; per problem: `summary/MBR4_by_problem.csv`.", "",
              "## How the scaffolds were generated", "",
              "- Model: RFD4-Proteina (RosettaCommons/NVIDIA), source commit ed63183a, weights bundle HF revision a06e2509 "
              "(`rfd4-proteina-flow-release-2026-10-19`), default sampler (60 steps, `thinking_medium` recycling, bf16), "
              "no metrics/oracles, no filtering or reranking: every generated design is submitted (100 per problem).",
              "- Inputs: MotifBench motif PDBs; all motif segments placed on one chain. Residues MotifBench marks as "
              "redesignable get backbone-only (N, CA, C, O) coordinate conditioning and no sequence; all other motif "
              "residues get all-atom coordinate + sequence conditioning. Segment-length ranges and total lengths: "
              "ExpertGuess contigs (`in/rfd3_jsons`, same as the RFD3 ExpertGuess run).",
              "- **Indexed**: per design, every scaffold-gap length is sampled uniformly within its contig range subject to "
              "the MotifBench total length; motif segments are indexed in contig order.",
              "- **Unindexed**: one chain of exactly the MotifBench length is generated; every motif segment is unindexed "
              "(`C_IDX=false`) in its own index group (internal offsets kept), so the model chooses position and order "
              "of the segments. Motif placement for `scaffold_info.csv` is read from the model's insertion mapping "
              "(`is_unindexed_insertion`, `annotation_src-index-group`); designs whose mapping is not one contiguous run "
              "per segment are assigned the best-RMSD contiguous windows keeping the model's segment order "
              "(counts in the table above; such designs typically fail evaluation).",
              f"- Compute (generation): {gpu_h:.1f} GPU-hours over {n_tasks} jobs (RTX A5000 / RTX 5090 / RTX 4090, "
              "university cluster), ~7 s per design including compilation.",
              "", "## Evaluation", "",
              "Official MotifBench pipeline (`scripts/evaluate_bbs.sh` → Scaffold-Lab `motif_refolding.py`, ProteinMPNN "
              "8 sequences/backbone T=0.1, ESMFold, Foldseek clustering + novelty vs PDB) and `scripts/summarize_results.sh`, "
              "unchanged settings (`inference.force_motif_AA_type=True`). Run partly on the cluster (first indexed problems) and "
              "mostly on Modal L40S GPUs with the identical conda environment; only the working directory and the number of "
              "Foldseek threads differ. Triplicates here are 3 independently GENERATED sets (seeds 1-3; indexed also "
              "re-sampled layouts), each evaluated once.", "",
              "## Files", "",
              "- `submission_<mode>/rep<r>/MBR4_scaffolds_<mode>_rep<r>.zip` — submitted scaffolds (`{case}_{i}.pdb`, "
              "1-indexed, chain A, + `scaffold_info.csv`).",
              "- `.../MBR4_evaluation_<mode>_rep<r>.tar.gz` — full evaluation output; `MBR4_summary_by_problem.csv`, "
              "`MBR4_overall_summary.csv` — official summaries (copies; original names inside the evaluation tarball).",
              "- For a single leaderboard entry per mode, submit rep1 and quote the triplicate mean ± SD.", ""]
    (out / "MBR4_README_submission.md").write_text("\n".join(lines))
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
