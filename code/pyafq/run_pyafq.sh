#!/bin/bash

group="hcpya"

bundleseg_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/bundleseg/${group}
pyafq_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/pyafq
logs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/pyafq/logs; mkdir -p ${logs_dir}

n_subs=100

sub_counter=0
for sub_dir in ${bundleseg_dir}/sub-*; do

    sub=$(basename ${sub_dir})

    outputs_dir=${pyafq_dir}/${group}/${sub}
    if [[ -d ${outputs_dir} ]]; then
        echo "Outputs directory already exists for ${sub}. Skipping."
        continue
    fi
    mkdir -p ${outputs_dir}

    echo "Running pyAFQ for ${sub}"

    log_output="${logs_dir}/pyafq_${sub}-%j.o"
    log_error="${logs_dir}/pyafq_${sub}-%j.e"
    sbatch --output=${log_output} --error=${log_error} pyafq.sh ${sub} ${group}

    sub_counter=$((sub_counter + 1))
    if [ ${sub_counter} -ge ${n_subs} ]; then
        break
    fi

done
