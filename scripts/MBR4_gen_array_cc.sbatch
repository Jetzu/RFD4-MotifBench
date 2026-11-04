#!/usr/bin/env bash
# Origin: cc
# Purpose: SLURM array over MBR4_tasks.tsv (spec, out_dir, num_replicates, seed): one rfd4-generate call per task.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=08:00:00
set -euo pipefail
TASKS=$1
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" "$TASKS")
IFS=$'\t' read -r SPEC OUT NREP SEED EXTRA <<< "$LINE"
echo "task $SLURM_ARRAY_TASK_ID on $(hostname): $SPEC -> $OUT nrep=$NREP seed=$SEED extra=${EXTRA:-}"
cd ${MBR4_ROOT}
exec scripts/run/MBR4_rfd4_generate_cc.sh "$SPEC" "$OUT" "$NREP" "$SEED" num_workers=2 ${EXTRA:-}
