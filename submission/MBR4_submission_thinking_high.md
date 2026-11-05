# MotifBench leaderboard submission: RFD4-Proteina, thinking_high

Two entries with RFD4-Proteina's `thinking_high` recycling setting (300 trunk passes per design): indexed and unindexed motif scaffolding.
Each entry is a triplicate: 3 independently generated and evaluated scaffold sets (30 problems × 100 designs each), all
submitted; the score is their mean ± SD.

| entry | MotifBench score (mean ± SD, 3 replicates) | rep1 / rep2 / rep3 |
|---|---|---|
| RFD4-Proteina (indexed, thinking_high) | **55.28 ± 0.16** | 55.32 / 55.10 / 55.41 |
| RFD4-Proteina (unindexed, thinking_high) | **60.21 ± 0.57** | 60.87 / 59.86 / 59.90 |

## Indexed (thinking_high)

**Entry name:** RFD4-Proteina (indexed, thinking_high)

**MotifBench score: 55.28 ± 0.16** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 55.32 / 55.10 / 55.41). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.33 ± 0.58 | 34.60 ± 0.46 | 0.34 ± 0.03 | 48.23 ± 0.96 |
| 2 | 10.00 ± 0.00 | 6.70 ± 0.10 | 0.37 ± 0.01 | 32.63 ± 0.68 |
| 3 | 9.00 ± 0.00 | 18.47 ± 0.75 | 0.31 ± 0.01 | 58.20 ± 0.50 |
| overall | 28.33 ± 0.58 | 19.92 ± 0.31 | 0.34 ± 0.01 | 46.35 ± 0.33 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 55.32 |
| rep2 | 55.10 |
| rep3 | 55.41 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 9 | 34.50 | 0.31 | 49.10 |
| rep1 | 2 | 10 | 6.70 | 0.38 | 32.40 |
| rep1 | 3 | 9 | 19.20 | 0.32 | 58.70 |
| rep1 | overall | 28 | 20.13 | 0.33 | 46.73 |
| rep2 | 1 | 10 | 35.10 | 0.37 | 48.40 |
| rep2 | 2 | 10 | 6.60 | 0.37 | 32.10 |
| rep2 | 3 | 9 | 18.50 | 0.30 | 58.20 |
| rep2 | overall | 29 | 20.07 | 0.35 | 46.23 |
| rep3 | 1 | 9 | 34.20 | 0.33 | 47.20 |
| rep3 | 2 | 10 | 6.80 | 0.37 | 33.40 |
| rep3 | 3 | 9 | 17.70 | 0.31 | 57.70 |
| rep3 | overall | 28 | 19.57 | 0.34 | 46.10 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_thinking_high_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_high` recycling (`n_recycle_schedule` [[10,9],[10,8],[10,5],[20,3],[10,2]], 300 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

### 4. Compute resources

Generation (indexed, thinking_high, 9,000 backbones = 3 × 30 × 100): 18.8 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~7.5 s per backbone including model load and compilation.

## Unindexed (thinking_high)

**Entry name:** RFD4-Proteina (unindexed, thinking_high)

**MotifBench score: 60.21 ± 0.57** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 60.87 / 59.86 / 59.90). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.67 ± 0.58 | 35.60 ± 0.56 | 0.35 ± 0.03 | 44.23 ± 1.35 |
| 2 | 10.00 ± 0.00 | 7.47 ± 0.25 | 0.37 ± 0.01 | 24.80 ± 0.96 |
| 3 | 9.00 ± 0.00 | 22.07 ± 1.33 | 0.32 ± 0.01 | 34.30 ± 2.10 |
| overall | 28.67 ± 0.58 | 21.71 ± 0.40 | 0.35 ± 0.01 | 34.44 ± 0.77 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 60.87 |
| rep2 | 59.86 |
| rep3 | 59.90 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 10 | 36.20 | 0.37 | 42.90 |
| rep1 | 2 | 10 | 7.50 | 0.36 | 25.50 |
| rep1 | 3 | 9 | 21.30 | 0.32 | 33.80 |
| rep1 | overall | 29 | 21.67 | 0.35 | 34.07 |
| rep2 | 1 | 10 | 35.10 | 0.35 | 44.20 |
| rep2 | 2 | 10 | 7.70 | 0.37 | 25.20 |
| rep2 | 3 | 9 | 23.60 | 0.32 | 36.60 |
| rep2 | overall | 29 | 22.13 | 0.35 | 35.33 |
| rep3 | 1 | 9 | 35.50 | 0.32 | 45.60 |
| rep3 | 2 | 10 | 7.20 | 0.37 | 23.70 |
| rep3 | 3 | 9 | 21.30 | 0.33 | 32.50 |
| rep3 | overall | 28 | 21.33 | 0.34 | 33.93 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_thinking_high_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_high` recycling (`n_recycle_schedule` [[10,9],[10,8],[10,5],[20,3],[10,2]], 300 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; designs whose mapping is not one contiguous run per segment get the best-backbone-RMSD contiguous windows (model's segment order kept). No design is filtered out. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

### 4. Compute resources

Generation (unindexed, thinking_high, 9,000 backbones = 3 × 30 × 100): 19.1 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~7.6 s per backbone including model load and compilation.

## Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
