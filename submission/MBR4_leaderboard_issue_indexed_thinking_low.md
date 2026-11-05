# MotifBench leaderboard submission: RFD4-Proteina (indexed, thinking_low)

**Entry name:** RFD4-Proteina (indexed, thinking_low)

**MotifBench score: 53.95 ± 1.00** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 53.28 / 55.10 / 53.47). All three sets are submitted.

## 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.67 ± 0.58 | 33.63 ± 1.19 | 0.34 ± 0.02 | 47.03 ± 2.32 |
| 2 | 9.67 ± 0.58 | 6.13 ± 1.17 | 0.36 ± 0.02 | 31.63 ± 1.36 |
| 3 | 9.00 ± 0.00 | 19.40 ± 0.26 | 0.31 ± 0.01 | 58.47 ± 0.46 |
| overall | 28.33 ± 1.15 | 19.72 ± 0.79 | 0.34 ± 0.02 | 45.71 ± 0.43 |

### Per replicate (official `overall_summary.csv` of each set)

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

## 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_thinking_low_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_low` recycling (`n_recycle_schedule` [[10,4],[10,3],[10,2],[30,1]], 120 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation (indexed, thinking_low, 9,000 backbones = 3 × 30 × 100): 10.0 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~4.0 s per backbone including model load and compilation.

## 5. Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
