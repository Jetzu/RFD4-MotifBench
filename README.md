# RFD4-Proteina on MotifBench

MotifBench leaderboard submissions for **RFD4-Proteina** in two modes, **indexed** and **unindexed**, each as 3 independently
generated and evaluated scaffold sets (30 problems × 100 designs).

| entry | MotifBench score (rep1, submitted) | mean ± SD over 3 replicates |
|---|---|---|
| RFD4-Proteina (indexed) | 56.61 | 55.06 ± 1.35 |
| RFD4-Proteina (unindexed) | 59.75 | 60.36 ± 0.87 |

Full method description, per-problem results, comparison with RFD3, figures, motif-placement and chain-break analysis,
timing and hardware: **[DETAILS.md](DETAILS.md)**. The two submission texts below are also available separately in
[`submission/`](submission).

## Indexed

**Entry name:** RFD4-Proteina (indexed)

**MotifBench score:** 56.61 (rep1, designated submission); **55.06 ± 1.35** over 3 independently generated and
evaluated scaffold sets (rep1/rep2/rep3: 56.61 / 54.18 / 54.38)

### 1. Success rate summary (`scripts/summarize_results.sh`, rep1)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10 | 37.30 | 0.35 | 49.90 |
| 2 | 10 | 6.30 | 0.38 | 33.80 |
| 3 | 9 | 21.50 | 0.31 | 60.90 |
| overall | 29 | 21.70 | 0.35 | 48.20 |

MotifBench score: 56.61

Per problem: `rep1/results/summary_by_problem.csv` in the archive.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_MotifBench_submission.zip` with the submitted scaffold sets (rep1-3, MotifBench format), the full
evaluation output (`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), default sampler (60 steps, `thinking_medium` recycling, bf16), no filtering or reranking: all 100 designs per problem
are submitted. All segments of a motif are one input on one chain with native coordinates in one frame. Redesignable motif residues
(UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get all-atom coordinates and sequence.
Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (indexed, 9,000 backbones = 3 × 30 × 100): 20.3 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX
A5000 / RTX 4090 on a university cluster (TUM).

## Unindexed

**Entry name:** RFD4-Proteina (unindexed)

**MotifBench score:** 59.75 (rep1, designated submission); **60.36 ± 0.87** over 3 independently generated and
evaluated scaffold sets (rep1/rep2/rep3: 59.75 / 59.98 / 61.36)

### 1. Success rate summary (`scripts/summarize_results.sh`, rep1)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10 | 35.70 | 0.36 | 44.80 |
| 2 | 10 | 7.70 | 0.40 | 22.60 |
| 3 | 9 | 20.70 | 0.33 | 32.20 |
| overall | 29 | 21.37 | 0.36 | 33.20 |

MotifBench score: 59.75

Per problem: `rep1/results/summary_by_problem.csv` in the archive.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_MotifBench_submission.zip` with the submitted scaffold sets (rep1-3, MotifBench format), the full
evaluation output (`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

### 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), default sampler (60 steps, `thinking_medium` recycling, bf16), no filtering or reranking: all 100 designs per problem
are submitted. All segments of a motif are one input on one chain with native coordinates in one frame. Redesignable motif residues
(UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get all-atom coordinates and sequence.
Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; for the 3.8 % of designs whose mapping is not one contiguous run per segment, the best-backbone-RMSD contiguous windows (model's segment order kept) are used. No design is filtered out.
Full description and figures: [DETAILS.md](DETAILS.md)

### 4. Compute resources

Generation (unindexed, 9,000 backbones = 3 × 30 × 100): 20.8 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX
A5000 / RTX 4090 on a university cluster (TUM).

## Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
