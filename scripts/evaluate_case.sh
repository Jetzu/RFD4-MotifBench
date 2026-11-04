#!/usr/bin/env bash
# Run the official MotifBench evaluate_bbs.sh for one case/config from a writable work dir (shared checkout is read-only).
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
# Usage: evaluate_case.sh <case> <config.txt> <workdir>
# On Pascal GPUs (sm_61) the motif_bench env's torch (cu128, sm_70+) is overlaid with torch 2.8.0+cu126.
set -uo pipefail
CASE=$1; CFG=$2; WD=$3
E=${MOTIFBENCH_ENV}
export CUDA_HOME=$E PATH=$E/bin:$PATH
nvidia-smi -L >/dev/null 2>&1 || { echo "NO GPU on $(hostname)"; exit 99; }
CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1)
echo "case $CASE cfg $CFG host $(hostname) gpu $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) cc $CC"
if [[ ${CC%%.*} -lt 7 ]]; then export PYTHONPATH=${PASCAL_TORCH_OVERLAY}${PYTHONPATH:+:$PYTHONPATH}; echo "using cu126 overlay"; fi
export TRITON_CACHE_DIR=/tmp/mbr4_triton
mkdir -p "$WD/$CASE" && touch "$WD/setup.cfg" && cd "$WD/$CASE"  # setup.cfg = root marker for Scaffold-Lab rootutils (it chdirs there, writes tmp/)
START=$(date +%s)
bash ${MOTIFBENCH_DIR}/scripts/evaluate_bbs.sh "$CASE" "$CFG" "hydra.run.dir=$WD/$CASE/hydra"
RC=$?
echo "exit $RC after $(( $(date +%s) - START )) s"
exit $RC
