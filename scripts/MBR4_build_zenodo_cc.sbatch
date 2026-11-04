#!/usr/bin/env bash
# Origin: cc
# Purpose: Build the Zenodo-ready MotifBench submission zip for one mode (all 3 replicates: MotifBench-format scaffolds, full evaluation, summaries, raw RFD4 CIFs, configs, inputs, scripts).
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=08:00:00
set -euo pipefail
MODE=$1
P=${MBR4_ROOT}
G=$P/runs/MBR4_N002_rfd4-production-generation-30-motifbench
E=$P/runs/MBR4_N003_motifbench-evaluation-of-rfd4-scaffolds
OUT=$P/deliverables/zenodo; mkdir -p $OUT
S=/tmp/mbr4_zenodo_${MODE}_$$; T=$S/RFD4_${MODE}; mkdir -p $T/inputs $T/scripts
ln -s $P/deliverables/MBR4_leaderboard_issue_${MODE}.md $T/SUBMISSION.md
ln -s $P/deliverables/rfd4_motifbench_repo/MBR4_README.md $T/README.md
for r in 1 2 3; do
  mkdir -p $T/rep$r
  ln -s $G/scaffolds_${MODE}_rep$r $T/rep$r/scaffolds
  ln -s $E/results_${MODE}_rep$r $T/rep$r/results
  ln -s $G/out_${MODE}_rep$r $T/rep$r/rfd4_raw_outputs
  ln -s $E/configs/MBR4_config_${MODE}_rep$r.txt $T/rep$r/config.txt
  [[ $MODE == indexed ]] && ln -s $P/in/specs/indexed/rep$r $T/inputs/specs_rep$r
done
[[ $MODE == unindexed ]] && ln -s $P/in/specs/unindexed $T/inputs/specs
ln -s $P/in/specs/motifs $T/inputs/motifs_merged_chainA
ln -s $P/in/specs/seg_map.json $T/inputs/seg_map.json
ln -s $P/in/rfd3_jsons $T/inputs/contig_jsons
ln -s ${MOTIFBENCH_DIR}/example/contig_specifications.csv $T/inputs/contig_specifications.csv
for f in prep/MBR4_build_specs_cc.py run/MBR4_rfd4_generate_cc.sh slurm/MBR4_gen_array_cc.sbatch analysis/MBR4_convert_to_motifbench_cc.py \
         run/MBR4_eval_case_cc.sh run/MBR4_modal_eval_cc.py slurm/MBR4_supervisor_cc.sbatch analysis/MBR4_summarize_triplicates_cc.py \
         analysis/MBR4_peptide_bond_census_cc.py plot/MBR4_motifbench_figures_up.py; do ln -s $P/scripts/$f $T/scripts/; done
cd $S
rm -f $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip
date; zip -r -q -9 $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip RFD4_${MODE} -x '*/__pycache__/*'
date; ls -la $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip
unzip -l $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip | tail -n 1
for r in 1 2 3; do echo "rep$r pdbs: $(unzip -l $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip "RFD4_${MODE}/rep$r/scaffolds/*/*.pdb" | tail -n 1)"; done
sha256sum $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip > $OUT/MBR4_RFD4_${MODE}_MotifBench_submission.zip.sha256
rm -rf $S
