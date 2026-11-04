#!/usr/bin/env bash
# Origin: cc
# Purpose: SLURM array over an eval task list (case, config, workdir): one official MotifBench evaluate_bbs.sh per task.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=10:00:00
set -uo pipefail
TASKS=$1
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" "$TASKS")
IFS=$'\t' read -r CASE CFG WD <<< "$LINE"
exec ${MBR4_ROOT}/scripts/run/MBR4_eval_case_cc.sh "$CASE" "$CFG" "$WD"
