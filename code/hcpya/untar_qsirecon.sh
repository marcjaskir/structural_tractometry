#!/bin/bash

hcpya_qsirecon_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/hcpya

for model_dir in ${hcpya_qsirecon_dir}/derivatives/*; do

    model=$(basename ${model_dir})

    for tar_file in ${model_dir}/*.tar.gz; do

        sub=$(basename ${tar_file} .tar.gz)
        
        # Check if sub is 100206
        # if [[ ${sub} != "100206" ]]; then
        #     continue
        # fi

        # Uncompress and remove .tar.gz file
        mkdir -p ${model_dir}/sub-${sub}
        tar -xzvf ${tar_file} -C ${model_dir}/sub-${sub}
        rm ${tar_file}
        

    done

done


