# Origin: cc
# Purpose: Generate the MotifBench leaderboard-issue text per mode directly from the official summary CSVs (no hand-typed numbers).
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
import os
import csv
import re
from pathlib import Path

D = Path(os.environ["MBR4_ROOT"]) / "deliverables"
GPUH = {"indexed": 20.3, "unindexed": 20.8}  # sacct 621780 ElapsedRaw, tasks 0-8 / 9-17
MODE_TXT = {
    "indexed": ("Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, "
                "gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length."),
    "unindexed": ("Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed "
                  "(`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement "
                  "in `scaffold_info.csv` is read from RFD4's insertion mapping; for the 3.8 % of designs whose mapping is not "
                  "one contiguous run per segment, the best-backbone-RMSD contiguous windows (model's segment order kept) are "
                  "used. No design is filtered out."),
}
for mode in ("indexed", "unindexed"):
    scores = []
    for r in (1, 2, 3):
        t = (D / f"submission_{mode}/rep{r}/MBR4_overall_summary.csv").read_text()
        scores.append(float(re.search(r"MotifBench score:\s*([\d.]+)", t).group(1)))
    mean = sum(scores) / 3
    sd = (sum((s - mean) ** 2 for s in scores) / 2) ** 0.5
    rows = list(csv.reader(open(D / f"submission_{mode}/rep1/MBR4_overall_summary.csv")))
    table = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
    table += ["| " + " | ".join(r) + " |" for r in rows[1:] if r and not r[0].startswith("MotifBench")]
    txt = f"""# MotifBench leaderboard submission: RFD4-Proteina ({mode})

**Entry name:** RFD4-Proteina ({mode})

**MotifBench score:** {scores[0]:.2f} (rep1, designated submission); **{mean:.2f} ± {sd:.2f}** over 3 independently generated and
evaluated scaffold sets (rep1/rep2/rep3: {scores[0]:.2f} / {scores[1]:.2f} / {scores[2]:.2f})

## 1. Success rate summary (`scripts/summarize_results.sh`, rep1)

{chr(10).join(table)}

MotifBench score: {scores[0]:.2f}

Per problem: `rep1/results/summary_by_problem.csv` in the archive.

## 2. Permanent download link

`<Zenodo DOI>`: `MBR4_RFD4_{mode}_MotifBench_submission.zip` with the submitted scaffold sets (rep1-3, MotifBench format), the full
evaluation output (`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), default sampler (60 steps, `thinking_medium` recycling, bf16), no filtering or reranking: all 100 designs per problem
are submitted. All segments of a motif are one input on one chain with native coordinates in one frame. Redesignable motif residues
(UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get all-atom coordinates and sequence.
{MODE_TXT[mode]}
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation ({mode}, 9,000 backbones = 3 × 30 × 100): {GPUH[mode]:.1f} GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX
A5000 / RTX 4090 on a university cluster (TUM).

## 5. Contact

Lukas Gerstung, lukas.gerstung@tum.de
"""
    (D / f"MBR4_leaderboard_issue_{mode}.md").write_text(txt)
    print(mode, scores, f"{mean:.2f} ± {sd:.2f}")
