# MotifBench leaderboard submission: RFD4-Proteina (indexed)

**Entry name:** RFD4-Proteina (indexed)

**MotifBench score: 55.06 ± 1.35** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 56.61 / 54.18 / 54.38). All three sets are submitted.

## 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10.00 ± 0.00 | 35.33 ± 1.70 | 0.35 ± 0.01 | 48.53 ± 1.27 |
| 2 | 9.33 ± 0.58 | 6.50 ± 0.26 | 0.36 ± 0.03 | 32.27 ± 1.33 |
| 3 | 9.00 ± 0.00 | 19.67 ± 1.63 | 0.31 ± 0.01 | 58.03 ± 2.51 |
| overall | 28.33 ± 0.58 | 20.50 ± 1.04 | 0.34 ± 0.01 | 46.28 ± 1.68 |

Per replicate: `rep{1,2,3}/results/summary_by_problem.csv` and `overall_summary.csv` in the archive.

## 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full
evaluation output (`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), default sampler (60 steps, `thinking_medium` recycling, bf16), no filtering or reranking: all 100 designs per problem
are submitted. All segments of a motif are one input on one chain with native coordinates in one frame. Redesignable motif residues
(UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get all-atom coordinates and sequence.
Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation (indexed, 9,000 backbones = 3 × 30 × 100): 20.3 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX
A5000 / RTX 4090 on a university cluster (TUM).

## 5. Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
