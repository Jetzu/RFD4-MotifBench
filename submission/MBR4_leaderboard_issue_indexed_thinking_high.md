# MotifBench leaderboard submission: RFD4-Proteina (indexed, thinking_high)

**Entry name:** RFD4-Proteina (indexed, thinking_high)

**MotifBench score: 55.28 ± 0.16** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 55.32 / 55.10 / 55.41). All three sets are submitted.

## 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.33 ± 0.58 | 34.60 ± 0.46 | 0.34 ± 0.03 | 48.23 ± 0.96 |
| 2 | 10.00 ± 0.00 | 6.70 ± 0.10 | 0.37 ± 0.01 | 32.63 ± 0.68 |
| 3 | 9.00 ± 0.00 | 18.47 ± 0.75 | 0.31 ± 0.01 | 58.20 ± 0.50 |
| overall | 28.33 ± 0.58 | 19.92 ± 0.31 | 0.34 ± 0.01 | 46.35 ± 0.33 |

### Per replicate (official `overall_summary.csv` of each set)

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

## 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_indexed_thinking_high_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_high` recycling (`n_recycle_schedule` [[10,9],[10,8],[10,5],[20,3],[10,2]], 300 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Motif segments placed with MotifBench's reference contigs (`example/contig_specifications.csv`); per design, gap lengths are sampled uniformly inside the contig ranges subject to the problem's total length. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation (indexed, thinking_high, 9,000 backbones = 3 × 30 × 100): 18.8 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~7.5 s per backbone including model load and compilation.

## 5. Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
