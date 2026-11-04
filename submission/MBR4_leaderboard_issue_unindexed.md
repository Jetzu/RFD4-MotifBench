# MotifBench leaderboard submission: RFD4-Proteina (unindexed)

**Entry name:** RFD4-Proteina (unindexed)

**MotifBench score:** 59.75 (rep1, designated submission); **60.36 ± 0.87** over 3 independently generated and
evaluated scaffold sets (rep1/rep2/rep3: 59.75 / 59.98 / 61.36)

## 1. Success rate summary (`scripts/summarize_results.sh`, rep1)

| Group | Number_Solved | Mean_Num_Solutions | Mean_Novelty | Mean_Success_rate |
|---|---|---|---|---|
| 1 | 10 | 35.70 | 0.36 | 44.80 |
| 2 | 10 | 7.70 | 0.40 | 22.60 |
| 3 | 9 | 20.70 | 0.33 | 32.20 |
| overall | 29 | 21.37 | 0.36 | 33.20 |

MotifBench score: 59.75

Per problem: `rep1/results/summary_by_problem.csv` in the archive.

## 2. Permanent download link

[10.5281/zenodo.23942848](https://doi.org/10.5281/zenodo.23942848): `MBR4_RFD4_unindexed_MotifBench_submission.zip` with the submitted scaffold sets (rep1-3, MotifBench format), the full
evaluation output (`evaluate_bbs.sh`, 30 problems × 3 replicates), the summaries, the raw RFD4 outputs, the inputs and the scripts.

## 3. How the scaffolds were generated

RFD4-Proteina (RosettaCommons / NVIDIA), source commit `ed63183a`, weights `rfd4-proteina-flow-release-2026-10-19` (HF revision
`a06e2509`), default sampler (60 steps, `thinking_medium` recycling, bf16), no filtering or reranking: all 100 designs per problem
are submitted. All segments of a motif are one input on one chain with native coordinates in one frame. Redesignable motif residues
(UNK) get backbone-only coordinate conditioning and no sequence; all other motif residues get all-atom coordinates and sequence.
Unindexed: one chain of exactly the problem's total length is generated; every motif segment is unindexed (`C_IDX=false`) in its own index group, so RFD4 chooses the position and order of the segments. The placement in `scaffold_info.csv` is read from RFD4's insertion mapping; for the 3.8 % of designs whose mapping is not one contiguous run per segment, the best-backbone-RMSD contiguous windows (model's segment order kept) are used. No design is filtered out.
Full description and figures: https://github.com/Jetzu/RFD4-MotifBench

## 4. Compute resources

Generation (unindexed, 9,000 backbones = 3 × 30 × 100): 20.8 GPU-hours, ~8 s per backbone including compilation, NVIDIA RTX
A5000 / RTX 4090 on a university cluster (TUM).

## 5. Contact

Lukas Gerstung, lukas.gerstung@tum.de
