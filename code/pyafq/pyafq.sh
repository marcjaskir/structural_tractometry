#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --job-name=pyafq

sub=${1}
group=${2}

source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/structural_tractometry

echo "Starting pyafq at $(date)"
python pyafq.py ${sub} ${group}
echo "Finished pyafq at $(date)"