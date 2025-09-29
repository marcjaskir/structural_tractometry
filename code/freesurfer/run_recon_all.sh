#!/bin/bash

group=hcpaging

qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}
freesurfer_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
logs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/freesurfer/logs

# Make parent freesurfer directory if it doesn't exist
if [[ ! -d ${freesurfer_dir} ]]; then
    mkdir -p ${freesurfer_dir}
fi

# Iterate over subdirectories in qsiprep_dir
for sub_dir in ${qsiprep_dir}/sub-*; do
    sub=$(basename ${sub_dir})

    # Skip subjects except for sub-RID0505
    #if [[ ${sub} != "sub-RID0505" ]]; then
    #    continue
    #fi

    if [[ -d ${sub_dir} ]]; then

        # Check if qsiprep finished based on .html file
        if [[ -f ${qsiprep_dir}/${sub}.html ]]; then

            # Check if subject exists in freesurfer directory
            if [[ ! -d ${freesurfer_dir}/${sub} ]]; then

                echo "Running recon-all for ${sub}"
                logs_output=${logs_dir}/${sub}_recon-all_job-%j.o
                logs_error=${logs_dir}/${sub}_recon-all_job-%j.e
                sbatch --output=${logs_output} --error=${logs_error} ./recon_all.sh ${sub} ${group}


            fi

        fi

    fi

done
