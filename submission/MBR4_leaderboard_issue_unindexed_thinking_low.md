# MotifBench leaderboard submission: RFD4-Proteina (unindexed, thinking_low)

**Entry name:** RFD4-Proteina (unindexed, thinking_low)

**MotifBench score: 58.64 ± 1.21** (mean ± SD over 3 independently generated and evaluated scaffold sets of 30 × 100
designs; rep1 / rep2 / rep3: 57.25 / 59.40 / 59.27). All three sets are submitted.

## 1. Success rate summary (`scripts/summarize_results.sh`, mean ± SD over rep1-3)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 9.33 ± 0.58 | 35.27 ± 0.64 | 0.34 ± 0.03 | 42.30 ± 0.46 |
| 2 | 9.67 ± 0.58 | 7.50 ± 0.44 | 0.36 ± 0.03 | 22.50 ± 0.66 |
| 3 | 9.00 ± 0.00 | 20.20 ± 1.77 | 0.33 ± 0.02 | 31.37 ± 1.50 |
| overall | 28.00 ± 1.00 | 20.99 ± 0.77 | 0.34 ± 0.02 | 32.05 ± 0.63 |

### Per replicate (official `overall_summary.csv` of each set)

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

## 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_thinking_low_MotifBench_submission.zip` with the three submitted scaffold sets (rep1-3, MotifBench format), the full evaluation output
(`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), sampler with 60 steps and `thinking_low` recycling (`n_recycle_schedule` [[10,4],[10,3],[10,2],[30,1]], 120 trunk passes per design), bf16, no filtering or
reranking: all 100 designs per problem are submitted. All segments of a motif are one input on one chain with native coordinates in
one frame. Redesignable motif residues (UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get
all-atom coordinates and sequence. Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; designs whose mapping is not one contiguous run per segment get the best-backbone-RMSD contiguous windows (model's segment order kept). No design is filtered out. The three thinking settings use identical inputs, seeds and (indexed) gap layouts.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation (unindexed, thinking_low, 9,000 backbones = 3 × 30 × 100): 9.7 GPU-hours on NVIDIA L40S (Modal cloud, one process per GPU), ~3.9 s per backbone including model load and compilation.

## 5. Contact

- Lukas Gerstung, lukas.gerstung@tum.de
- Lorenz Kleiter, lorenz.kleiter@tum.de
