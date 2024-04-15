#!/bin/bash
cd /home/yutao4/Sat_Simulator
if [[ -n "$1" ]]; then
  jid0="--dependency=afterok:$1"
else
  jid0=""
fi

jid1=$(sbatch --parsable $jid0 slurm/generate_sat_traces.swb)
jid2=$(sbatch --parsable --dependency=afterok:$jid1 slurm/generate_ground_truth_high_priority.swb)
sbatch --dependency=afterok:$jid1 slurm/run_edge_computing.swb