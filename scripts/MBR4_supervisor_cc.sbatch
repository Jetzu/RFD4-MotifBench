#!/usr/bin/env bash
# Origin: cc
# Purpose: Unattended driver for MBR4 evaluation: deploy Modal app, run the resumable client over all 6 sets, resubmit itself until all 180 (set, problem) evaluations exist, then summarize + package.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
# Usage: sbatch scripts/slurm/MBR4_supervisor_cc.sbatch [attempt]
#SBATCH --job-name=MBR4_super
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/MBR4_supervisor_%j.out
set -uo pipefail
ATTEMPT=${1:-1}
P=${MBR4_ROOT}
E=$P/runs/MBR4_N003_motifbench-evaluation-of-rfd4-scaffolds
G=$P/runs/MBR4_N002_rfd4-production-generation-30-motifbench
SETS="indexed_rep1 unindexed_rep1 indexed_rep2 unindexed_rep2 indexed_rep3 unindexed_rep3"
MODAL=${MODAL_BIN_DIR:?set MODAL_BIN_DIR (dir with the modal CLI and its python)}
cd $P
echo "$(date -Is) supervisor attempt $ATTEMPT on $(hostname)"
count_done() { n=0; for s in $SETS; do n=$((n + $(ls $E/results_$s/*/esm_summary.txt 2>/dev/null | wc -l))); done; echo $n; }
echo "done before: $(count_done)/180"
if [[ $(count_done) -lt 180 ]]; then
  $MODAL/modal deploy scripts/run/MBR4_modal_eval_cc.py || { echo "deploy failed"; }
  $MODAL/python -u scripts/run/MBR4_modal_eval_cc.py $(for s in $SETS; do echo $E/configs/MBR4_tasks_$s.tsv; done)
  echo "client exit $?"
fi
N=$(count_done); echo "$(date -Is) done after: $N/180"
if [[ $N -lt 180 ]]; then
  if [[ $ATTEMPT -lt 4 ]]; then
    sbatch $P/scripts/slurm/MBR4_supervisor_cc.sbatch $((ATTEMPT + 1)); exit 0
  fi
  echo "GIVING UP after $ATTEMPT attempts with $N/180"; exit 1
fi
# ---- finalize
PY=${MOTIFBENCH_ENV}/bin/python
for s in $SETS; do bash ${MOTIFBENCH_DIR}/scripts/summarize_results.sh $E/configs/MBR4_config_$s.txt; tail -n 2 $E/results_$s/overall_summary.csv; done
$PY scripts/analysis/MBR4_summarize_triplicates_cc.py --eval-dir $E --out $P/deliverables/summary
$PY scripts/analysis/MBR4_package_submission_cc.py --gen-dir $G --eval-dir $E --out $P/deliverables
echo "$(date -Is) FINISHED: see $P/deliverables/MBR4_README_submission.md"
