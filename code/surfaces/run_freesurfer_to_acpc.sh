#!/bin/bash

group=hcpaging

log_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/surfaces/logs; mkdir -p $log_dir

# SBATCH --cpus-per-task=1 --mem=8GB --output=/mnt/sauce/littlab/users/mjaskir/functional_tractometry/derivatives/fmriprep/logs/%j.out

sbatch --cpus-per-task=1 \
    --mem=8GB \
    --job-name=fs_to_acpc_${group} \
    --output=$log_dir/fs_to_acpc_${group}_%j.o \
    --error=$log_dir/fs_to_acpc_${group}_%j.e \
    ./freesurfer_to_acpc.sh ${group}

