#!/bin/bash

group=hcpaging

qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}
freesurfer_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
qsirecon_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/${group}; mkdir -p ${qsirecon_dir}
logs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/qsirecon/logs; mkdir -p ${logs_dir}

for sub_dir in ${qsiprep_dir}/sub-*; do

    if [[ -d ${sub_dir} ]]; then
        sub=$(basename ${sub_dir})
        
        # Check if qsirecon is finished
        if [[ -f ${qsirecon_dir}/derivatives/qsirecon-DIPYDKI/${sub}.html ]]; then
            if [[ -f ${qsirecon_dir}/derivatives/qsirecon-DSIStudio/${sub}.html ]]; then
                if [[ -f ${qsirecon_dir}/derivatives/qsirecon-MRtrix3_act-HSVS/${sub}.html ]]; then
                    if [[ -f ${qsirecon_dir}/derivatives/qsirecon-NODDI/${sub}.html ]]; then
                        if [[ -f ${qsirecon_dir}/derivatives/qsirecon-TORTOISE_model-MAPMRI/${sub}.html ]]; then
                            if [[ -f ${qsirecon_dir}/derivatives/qsirecon-TORTOISE_model-tensor/${sub}.html ]]; then
                                echo "${sub} already completed qsirecon"
                                continue 
                            fi
                        fi
                    fi
                fi
            fi
        fi

        # Check if qsiprep is finished
        if [[ ! -f ${qsiprep_dir}/${sub}.html ]]; then
            echo "${sub} has not finished qsiprep"
            continue
        fi

        # Check if freesurfer is finished
        if [[ ! -d ${freesurfer_dir}/${sub} ]]; then
            echo "${sub} has not finished freesurfer"
            continue
        elif [[ -f ${freesurfer_dir}/${sub}/scripts/IsRunning.lh+rh ]]; then
            echo "${sub} has not finished freesurfer"
            continue
        fi

        echo "Processing subject ${sub}"

        logs_output=${logs_dir}/${sub}_qsirecon_job-%j.o
        logs_error=${logs_dir}/${sub}_qsirecon_job-%j.e
        sbatch --output=${logs_output} --error=${logs_error} ./qsirecon.sh $sub $group

    fi

done
