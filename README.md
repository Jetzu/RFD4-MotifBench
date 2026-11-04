# RFD4-Proteina on MotifBench

MotifBench leaderboard submissions for **RFD4-Proteina** in two modes, **indexed** and **unindexed**. Each entry is a
triplicate: 3 independently generated and evaluated scaffold sets (30 problems × 100 designs each), all submitted;
the score is their mean ± SD.

| entry | MotifBench score (mean ± SD, 3 replicates) | rep1 / rep2 / rep3 |
|---|---|---|
| RFD4-Proteina (indexed) | **55.06 ± 1.35** | 56.61 / 54.18 / 54.38 |
| RFD4-Proteina (unindexed) | **60.36 ± 0.87** | 59.75 / 59.98 / 61.36 |

Full method description, per-problem results, comparison with RFD3, figures, motif-placement and chain-break analysis,
timing and hardware: **[DETAILS.md](DETAILS.md)**. The two submission texts below are also available separately in
[`submission/`](submission).

## Indexed

**Entry name:** RFD4-Proteina (indexed)

**MotifBench score: 55.06 ± 1.35** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 56.61 / 54.18 / 54.38). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10.00 ± 0.00 | 35.33 ± 1.70 | 0.35 ± 0.01 | 48.53 ± 1.27 |
| 2 | 9.33 ± 0.58 | 6.50 ± 0.26 | 0.36 ± 0.03 | 32.27 ± 1.33 |
| 3 | 9.00 ± 0.00 | 19.67 ± 1.63 | 0.31 ± 0.01 | 58.03 ± 2.51 |
| overall | 28.33 ± 0.58 | 20.50 ± 1.04 | 0.34 ± 0.01 | 46.28 ± 1.68 |

Per replicate: `rep{1,2,3}/results/summary_by_problem.csv` and `overall_summary.csv` in the archive.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full
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

**MotifBench score: 60.36 ± 0.87** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 59.75 / 59.98 / 61.36). All three sets are submitted.

### 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.67 ± 0.58 | 36.80 ± 0.96 | 0.35 ± 0.02 | 44.87 ± 0.70 |
| 2 | 9.33 ± 0.58 | 7.73 ± 0.25 | 0.36 ± 0.04 | 23.47 ± 0.76 |
| 3 | 9.00 ± 0.00 | 21.60 ± 0.85 | 0.33 ± 0.01 | 32.73 ± 0.61 |
| overall | 28.00 ± 1.00 | 22.05 ± 0.59 | 0.34 ± 0.02 | 33.69 ± 0.43 |

Per replicate: `rep{1,2,3}/results/summary_by_problem.csv` and `overall_summary.csv` in the archive.

### 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full
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
