#!/bin/bash

group=hcpaging

# sub_list=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/subjects_controls.csv
# sub_list=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/subjects_penn_epilepsy.csv
# sub_list=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/splits/hcpaging_covbat_training_subs.csv
sub_list=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/trekker_batch-1_subs_hcpaging.csv
data_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/${group}
qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}; mkdir -p ${qsiprep_dir}
logs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/qsiprep/logs; mkdir -p ${logs_dir}

# Run qsiprep
# for sub in $(cat ${sub_list}); do

# for sub_dir in ${data_dir}/sub-HCA7*; do
for sub in $(cat ${sub_list}); do
    # sub=$(basename ${sub_dir})

    # or penn_epilepsy
    if [[ ${group} == "penn_controls" ]] || [[ ${group} == "penn_epilepsy" ]]; then
    
        for ses_dir in ${data_dir}/${sub}/ses-research3T*; do
            ses=$(basename ${ses_dir})

            # Skip if subject is already processed
            if [ -d ${qsiprep_dir}/${sub} ]; then
                echo "Subject ${sub} already processed, skipping"
                continue
            fi

            echo "Running qsiprep for subject ${sub}"

            logs_output=${logs_dir}/${sub}_qsiprep_job-%j.o
            logs_error=${logs_dir}/${sub}_qsiprep_job-%j.e
            sbatch --output=${logs_output} --error=${logs_error} ./qsiprep.sh $sub $group $ses

        done

    elif [[ ${group} == "hcpaging" ]]; then

        if [ -d ${qsiprep_dir}/${sub} ]; then
            echo "Subject ${sub} already processed, skipping"
            continue
        fi

        echo "Running qsiprep for subject ${sub}"
        logs_output=${logs_dir}/${sub}_qsiprep_job-%j.o
        logs_error=${logs_dir}/${sub}_qsiprep_job-%j.e
        sbatch --output=${logs_output} --error=${logs_error} ./qsiprep.sh $sub $group
    fi

done
