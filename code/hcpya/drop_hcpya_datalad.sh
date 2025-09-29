#!/bin/bash

hcp_raw_dir="/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/hcpya/hcp1200/HCP1200"

# Activate datalad environment with conda
source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/datalad

for sub_dir in ${hcp_raw_dir}/*; do
    sub=$(basename ${sub_dir})
    echo ${sub}
    if [[ -f ${sub_dir}/T1w/Diffusion/data.nii.gz ]]; then
        datalad drop ${sub_dir}/T1w/Diffusion/data.nii.gz
    fi
    echo "--------------------------------"
done