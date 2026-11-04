#!/usr/bin/env bash
# Origin: cc
# Purpose: Convert one generated set (mode, rep) into a MotifBench scaffolds dir + write its eval task list.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=03:00:00
set -euo pipefail
MODE=$1; REP=$2; SUF=${3:-}   # optional set suffix, e.g. _low / _high (N005 sweep)
P=${MBR4_ROOT}
G=${GEN_DIR:-$P/runs/MBR4_N002_rfd4-production-generation-30-motifbench}
E=${EVAL_DIR:-$P/runs/MBR4_N003_motifbench-evaluation-of-rfd4-scaffolds}
OUT=$G/scaffolds_${MODE}_rep$REP$SUF
cd $P
LAYOUT=()
[[ $MODE == indexed ]] && LAYOUT=(--layout in/specs/indexed/rep$REP/layout.tsv)
rm -f "$OUT/MBR4_qc.tsv"
scripts/util/MBR4_rfd4py_cc.sh python scripts/analysis/MBR4_convert_to_motifbench_cc.py --mode $MODE \
  --samples $G/out_${MODE}_rep$REP$SUF/inference_samples --seg-map in/specs/seg_map.json \
  --motif-dir ${MOTIFBENCH_DIR}/motif_pdbs --out "$OUT" "${LAYOUT[@]}"
n=$(ls $OUT/*/*.pdb | wc -l); echo "PDBs: $n"
awk -F'\t' '$3=="MISSING"' $OUT/MBR4_qc.tsv | head
for c in $(ls -d $OUT/[0-9]*_* | xargs -n1 basename); do
  printf "%s\t%s\t%s\n" "$c" "$E/configs/MBR4_config_${MODE}_rep$REP$SUF.txt" "$E/work_${MODE}_rep$REP$SUF"
done > $E/configs/MBR4_tasks_${MODE}_rep$REP$SUF.tsv
