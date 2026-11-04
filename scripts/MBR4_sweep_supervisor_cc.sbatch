#!/usr/bin/env bash
# Origin: cc
# Purpose: Unattended driver for the N005 recycle-strategy sweep: finish generation (Modal + cluster array), convert the 12 sets, evaluate on Modal, summarize; resubmits itself until done.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
# Usage: sbatch scripts/slurm/MBR4_sweep_supervisor_cc.sbatch <cluster_gen_array_jobid> [attempt]
#SBATCH --job-name=MBR4_sweep
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/MBR4_sweep_supervisor_%j.out
set -uo pipefail
CLUSTER_JOB=$1; ATTEMPT=${2:-1}
P=${MBR4_ROOT}
R=$P/runs/MBR4_N005_rfd4-recycle-strategy-sweep-thinking-low
M=${MODAL_BIN_DIR:?set MODAL_BIN_DIR (dir with the modal CLI and its python)}
S=$(dirname "$(command -v sbatch)")
cd $P
SETS=""; for st in low high; do for m in indexed unindexed; do for r in 1 2 3; do SETS="$SETS ${m}_rep${r}_$st"; done; done; done
ncif() { ls $R/out_$1/inference_samples 2>/dev/null | wc -l; }
npdb() { ls $R/scaffolds_$1/*/*.pdb 2>/dev/null | wc -l; }
ndone() { n=0; for s in $SETS; do n=$((n + $(ls $R/results_$s/*/esm_summary.txt 2>/dev/null | wc -l))); done; echo $n; }
echo "$(date -Is) sweep supervisor attempt $ATTEMPT on $(hostname)"

# ---- 1. generation
$M/modal deploy scripts/run/MBR4_modal_rfd4_gen_cc.py || echo "gen deploy failed"
$M/python -u scripts/run/MBR4_modal_rfd4_gen_cc.py $R/MBR4_tasks_gen_modal.tsv; echo "modal gen client exit $?"
while $S/squeue -h -j $CLUSTER_JOB 2>/dev/null | grep -q .; do sleep 300; done
for s in $SETS; do
  if [[ $(ncif $s) -lt 3000 ]]; then
    echo "set $s has $(ncif $s)/3000 after cluster+modal -> regenerating its chunks on Modal"
    grep -P "\t$R/out_$s\t" $R/MBR4_tasks_gen_cluster.tsv $R/MBR4_tasks_gen_modal.tsv -h > $R/MBR4_tasks_gen_refill_$s.tsv
    $M/python -u scripts/run/MBR4_modal_rfd4_gen_cc.py $R/MBR4_tasks_gen_refill_$s.tsv
  fi
done
for s in $SETS; do echo "gen $s: $(ncif $s)/3000"; done

# ---- 2. conversion (parallel SLURM jobs)
JOBS=""
for s in $SETS; do
  if [[ $(ncif $s) -ge 3000 && $(npdb $s) -lt 3000 ]]; then
    m=${s%%_rep*}; rest=${s#*_rep}; r=${rest%%_*}; st=${rest#*_}
    J=$($S/sbatch --parsable --job-name=MBR4_N005c --output=$P/logs/MBR4_N005_convert_${s}_%j.out \
        --export=ALL,GEN_DIR=$R,EVAL_DIR=$R $P/scripts/slurm/MBR4_convert_set_cc.sbatch $m $r _$st)
    JOBS="$JOBS $J"
  fi
done
for J in $JOBS; do while $S/squeue -h -j $J 2>/dev/null | grep -q .; do sleep 120; done; done
for s in $SETS; do echo "scaffolds $s: $(npdb $s)/3000"; done

# ---- 3. evaluation on Modal (official evaluate_bbs.sh; resumable client)
TASKS=""; for s in $SETS; do [[ -f $R/configs/MBR4_tasks_$s.tsv && $(npdb $s) -ge 3000 ]] && TASKS="$TASKS $R/configs/MBR4_tasks_$s.tsv"; done
if [[ -n "$TASKS" && $(ndone) -lt 360 ]]; then
  $M/python -u scripts/run/MBR4_modal_eval_cc.py $TASKS; echo "eval client exit $?"
fi
N=$(ndone); echo "$(date -Is) evaluations done: $N/360"
if [[ $N -lt 360 ]]; then
  if [[ $ATTEMPT -lt 4 ]]; then $S/sbatch $P/scripts/slurm/MBR4_sweep_supervisor_cc.sbatch $CLUSTER_JOB $((ATTEMPT + 1)); exit 0; fi
  echo "GIVING UP after $ATTEMPT attempts with $N/360"; exit 1
fi

# ---- 4. summaries
PY=${MOTIFBENCH_ENV}/bin/python
for s in $SETS; do bash ${MOTIFBENCH_DIR}/scripts/summarize_results.sh $R/configs/MBR4_config_$s.txt; tail -n 1 $R/results_$s/overall_summary.csv; done
RES=$(ls -d $P/.agent-research/results/N005*)
$PY scripts/plot/MBR4_sweep_figures_cc.py --out $RES
echo "$(date -Is) SWEEP FINISHED: $RES"
