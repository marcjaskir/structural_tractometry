#!/bin/bash

hcpya_data_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/hcpya/hcp1200/HCP1200
hcpya_freesurfer_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/hcpya; mkdir -p ${hcpya_freesurfer_dir}

for hcpya_sub_dir in ${hcpya_data_dir}/*; do

    hcpya_sub=$(basename ${hcpya_sub_dir})
    echo ${hcpya_sub}

    hcpya_data_fs_dir=${hcpya_sub_dir}/T1w/${hcpya_sub}
    ls ${hcpya_data_fs_dir}

done