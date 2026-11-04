#!/usr/bin/env bash
# Origin: cc
# Purpose: Run rfd4-generate (cu128 container, local SLURM GPU) on one condition-spec YAML.
# Usage: MBR4_rfd4_generate_cc.sh <spec.yaml> <out_dir> <num_replicates> <seed> [extra hydra overrides...]
set -euo pipefail
SPEC=$1; OUT=$2; NREP=$3; SEED=$4; shift 4
nvidia-smi -L >/dev/null 2>&1 || { echo "NO GPU on $(hostname)"; exit 99; }
nvidia-smi --query-gpu=name,compute_cap,memory.total --format=csv,noheader
mkdir -p "$OUT"
HERE=$(cd "$(dirname "$0")/../util" && pwd)
export NV=--nv
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
/usr/bin/time -v "$HERE/MBR4_rfd4py_cc.sh" rfd4-generate inputs="$SPEC" out_dir="$OUT" \
  num_replicates="$NREP" seed="$SEED" hf_ckpt_path=/weights/rfd4-proteina/bundle \
  '~metrics' num_workers=2 "$@"
