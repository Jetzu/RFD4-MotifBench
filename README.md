# RFD4-Proteina on MotifBench

MotifBench leaderboard submissions for **RFD4-Proteina**: two modes (**indexed**, **unindexed**) × three recycling settings
(`thinking_low`, `thinking_medium` = RFD4 default, `thinking_high`) = six entries. Each entry is a triplicate: 3 independently
generated and evaluated scaffold sets (30 problems × 100 designs each), all submitted; the score is their mean ± SD.

| entry | MotifBench score (mean ± SD, 3 replicates) | rep1 / rep2 / rep3 |
|---|---|---|
| [RFD4-Proteina (indexed, thinking_low)](#indexed-thinking_low) | **53.95 ± 1.00** | 53.28 / 55.10 / 53.47 |
| [RFD4-Proteina (indexed, thinking_medium)](#indexed-thinking_medium) | **55.06 ± 1.35** | 56.61 / 54.18 / 54.38 |
| [RFD4-Proteina (indexed, thinking_high)](#indexed-thinking_high) | **55.28 ± 0.16** | 55.32 / 55.10 / 55.41 |
| [RFD4-Proteina (unindexed, thinking_low)](#unindexed-thinking_low) | **58.64 ± 1.21** | 57.25 / 59.40 / 59.27 |
| [RFD4-Proteina (unindexed, thinking_medium)](#unindexed-thinking_medium) | **60.36 ± 0.87** | 59.75 / 59.98 / 61.36 |
| [RFD4-Proteina (unindexed, thinking_high)](#unindexed-thinking_high) | **60.21 ± 0.57** | 60.87 / 59.86 / 59.90 |

Full method description, per-problem results, comparison with RFD3, recycle-strategy comparison, figures, motif-placement
and chain-break analysis, timing and hardware: **[DETAILS.md](DETAILS.md)**. The six submission texts below are also
available separately in [`submission/`](submission).

## indexed thinking_low

**Entry name:** RFD4-Proteina (indexed, thinking_low)

**MotifBench score: 53.95 ± 1.00** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 53.28 / 55.10 / 53.47). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.67 ± 0.58 | 33.63 ± 1.19 | 0.34 ± 0.02 | 47.03 ± 2.32 |
| 2 | 9.67 ± 0.58 | 6.13 ± 1.17 | 0.36 ± 0.02 | 31.63 ± 1.36 |
| 3 | 9.00 ± 0.00 | 19.40 ± 0.26 | 0.31 ± 0.01 | 58.47 ± 0.46 |
| overall | 28.33 ± 1.15 | 19.72 ± 0.79 | 0.34 ± 0.02 | 45.71 ± 0.43 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 53.28 |
| rep2 | 55.10 |
| rep3 | 53.47 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 10 | 32.80 | 0.34 | 46.40 |
| rep1 | 2 | 10 | 5.10 | 0.37 | 30.90 |
| rep1 | 3 | 9 | 19.60 | 0.32 | 59.00 |
| rep1 | overall | 29 | 19.17 | 0.34 | 45.43 |
| rep2 | 1 | 9 | 35.00 | 0.33 | 49.60 |
| rep2 | 2 | 9 | 7.40 | 0.33 | 30.80 |
| rep2 | 3 | 9 | 19.50 | 0.30 | 58.20 |
| rep2 | overall | 27 | 20.63 | 0.32 | 46.20 |
| rep3 | 1 | 10 | 33.10 | 0.36 | 45.10 |
| rep3 | 2 | 10 | 5.90 | 0.37 | 33.20 |
| rep3 | 3 | 9 | 19.10 | 0.31 | 58.20 |
| rep3 | overall | 29 | 19.37 | 0.35 | 45.50 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_thinking_low_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_low` recycling (`n_recycle_schedule` [[10,4],[10,3],[10,2],[30,1]], 120 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (indexed, thinking_low, 9,000 backbones = 3 × 30 × 100): 10.0 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~4.0 s per backbone including model load and compilation.

## indexed thinking_medium

**Entry name:** RFD4-Proteina (indexed, thinking_medium)

**MotifBench score: 55.06 ± 1.35** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 56.61 / 54.18 / 54.38). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10.00 ± 0.00 | 35.33 ± 1.70 | 0.35 ± 0.01 | 48.53 ± 1.27 |
| 2 | 9.33 ± 0.58 | 6.50 ± 0.26 | 0.36 ± 0.03 | 32.27 ± 1.33 |
| 3 | 9.00 ± 0.00 | 19.67 ± 1.63 | 0.31 ± 0.01 | 58.03 ± 2.51 |
| overall | 28.33 ± 0.58 | 20.50 ± 1.04 | 0.34 ± 0.01 | 46.28 ± 1.68 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 56.61 |
| rep2 | 54.18 |
| rep3 | 54.38 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 10 | 37.30 | 0.35 | 49.90 |
| rep1 | 2 | 10 | 6.30 | 0.38 | 33.80 |
| rep1 | 3 | 9 | 21.50 | 0.31 | 60.90 |
| rep1 | overall | 29 | 21.70 | 0.35 | 48.20 |
| rep2 | 1 | 10 | 34.40 | 0.35 | 48.30 |
| rep2 | 2 | 9 | 6.40 | 0.33 | 31.40 |
| rep2 | 3 | 9 | 19.10 | 0.32 | 57.00 |
| rep2 | overall | 28 | 19.97 | 0.33 | 45.57 |
| rep3 | 1 | 10 | 34.30 | 0.36 | 47.40 |
| rep3 | 2 | 9 | 6.80 | 0.36 | 31.60 |
| rep3 | 3 | 9 | 18.40 | 0.31 | 56.20 |
| rep3 | overall | 28 | 19.83 | 0.34 | 45.07 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_thinking_medium_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_medium` recycling (`n_recycle_schedule` [[5,6],[10,5],[5,4],[10,3],[20,2],[10,1]], 180 trunk passes per design (RFD4 default)), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (indexed, thinking_medium, 9,000 backbones = 3 × 30 × 100): 20.3 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX A5000 / RTX 4090 on a university cluster (TUM).

## indexed thinking_high

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
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (indexed, thinking_high, 9,000 backbones = 3 × 30 × 100): 18.8 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~7.5 s per backbone including model load and compilation.

## unindexed thinking_low

**Entry name:** RFD4-Proteina (unindexed, thinking_low)

**MotifBench score: 58.64 ± 1.21** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 57.25 / 59.40 / 59.27). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.33 ± 0.58 | 35.27 ± 0.64 | 0.34 ± 0.03 | 42.30 ± 0.46 |
| 2 | 9.67 ± 0.58 | 7.50 ± 0.44 | 0.36 ± 0.03 | 22.50 ± 0.66 |
| 3 | 9.00 ± 0.00 | 20.20 ± 1.77 | 0.33 ± 0.02 | 31.37 ± 1.50 |
| overall | 28.00 ± 1.00 | 20.99 ± 0.77 | 0.34 ± 0.02 | 32.05 ± 0.63 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 57.25 |
| rep2 | 59.40 |
| rep3 | 59.27 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 9 | 35.00 | 0.32 | 42.20 |
| rep1 | 2 | 9 | 7.20 | 0.33 | 21.90 |
| rep1 | 3 | 9 | 18.60 | 0.31 | 29.90 |
| rep1 | overall | 27 | 20.27 | 0.32 | 31.33 |
| rep2 | 1 | 9 | 34.80 | 0.33 | 42.80 |
| rep2 | 2 | 10 | 8.00 | 0.37 | 23.20 |
| rep2 | 3 | 9 | 19.90 | 0.34 | 31.30 |
| rep2 | overall | 28 | 20.90 | 0.35 | 32.43 |
| rep3 | 1 | 10 | 36.00 | 0.38 | 41.90 |
| rep3 | 2 | 10 | 7.30 | 0.39 | 22.40 |
| rep3 | 3 | 9 | 22.10 | 0.33 | 32.90 |
| rep3 | overall | 29 | 21.80 | 0.36 | 32.40 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_thinking_low_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_low` recycling (`n_recycle_schedule` [[10,4],[10,3],[10,2],[30,1]], 120 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; designs whose mapping is not one contiguous run per segment get the best-backbone-RMSD contiguous windows (model's segment order kept). No design is filtered out. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (unindexed, thinking_low, 9,000 backbones = 3 × 30 × 100): 9.7 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~3.9 s per backbone including model load and compilation.

## unindexed thinking_medium

**Entry name:** RFD4-Proteina (unindexed, thinking_medium)

**MotifBench score: 60.36 ± 0.87** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 59.75 / 59.98 / 61.36). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.67 ± 0.58 | 36.80 ± 0.96 | 0.35 ± 0.02 | 44.87 ± 0.70 |
| 2 | 9.33 ± 0.58 | 7.73 ± 0.25 | 0.36 ± 0.04 | 23.47 ± 0.76 |
| 3 | 9.00 ± 0.00 | 21.60 ± 0.85 | 0.33 ± 0.01 | 32.73 ± 0.61 |
| overall | 28.00 ± 1.00 | 22.05 ± 0.59 | 0.34 ± 0.02 | 33.69 ± 0.43 |

#### Per replicate (official `overall_summary.csv` of each set)

| Replicate | MotifBench score |
|---|---|
| rep1 | 59.75 |
| rep2 | 59.98 |
| rep3 | 61.36 |

| Replicate | Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|---|
| rep1 | 1 | 10 | 35.70 | 0.36 | 44.80 |
| rep1 | 2 | 10 | 7.70 | 0.40 | 22.60 |
| rep1 | 3 | 9 | 20.70 | 0.33 | 32.20 |
| rep1 | overall | 29 | 21.37 | 0.36 | 33.20 |
| rep2 | 1 | 9 | 37.20 | 0.32 | 44.20 |
| rep2 | 2 | 9 | 7.50 | 0.33 | 24.00 |
| rep2 | 3 | 9 | 22.40 | 0.34 | 33.40 |
| rep2 | overall | 27 | 22.37 | 0.33 | 33.87 |
| rep3 | 1 | 10 | 37.50 | 0.36 | 45.60 |
| rep3 | 2 | 9 | 8.00 | 0.35 | 23.80 |
| rep3 | 3 | 9 | 21.70 | 0.33 | 32.60 |
| rep3 | overall | 28 | 22.40 | 0.34 | 34.00 |

Per-problem numbers of every replicate: `rep{1,2,3}/results/summary_by_problem.csv` in the archive and
`results/` in https://github.com/Jetzu/RFD4-MotifBench.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_thinking_medium_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_medium` recycling (`n_recycle_schedule` [[5,6],[10,5],[5,4],[10,3],[20,2],[10,1]], 180 trunk passes per design (RFD4 default)), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; designs whose mapping is not one contiguous run per segment get the best-backbone-RMSD contiguous windows (model's segment order kept). No design is filtered out. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (unindexed, thinking_medium, 9,000 backbones = 3 × 30 × 100): 20.8 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX A5000 / RTX 4090 on a university cluster (TUM).

## unindexed thinking_high

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
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (unindexed, thinking_high, 9,000 backbones = 3 × 30 × 100): 19.1 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~7.6 s per backbone including model load and compilation.

## Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
