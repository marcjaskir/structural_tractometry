#!/bin/bash

group="hcpya"

source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/structural_tractometry

trekker_dir="/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/trekker/${group}"
xfm_dir="/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/acpc_mni_xfm/${group}"
logs_dir="/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/bundleseg/logs" && mkdir -p ${logs_dir}

# Set the maximum number of subjects to submit
n_subs=150

sub_counter=0
for sub_dir in ${trekker_dir}/sub-*; do
    sub=$(basename ${sub_dir})
    echo ${sub}

    # Check for .trk file
    trk_file=${sub_dir}/${sub}_space-ACPC_desc-preproc_trekker.trk
    if [ ! -f ${trk_file} ]; then
        continue
    fi

    # Check for affine transform file
    if [[ ${group} == "penn_epilepsy" || ${group} == "penn_controls" || ${group} == "hcpaging" ]]; then
        xfm_file="${xfm_dir}/${sub}/${sub}_from-ACPC_to-MNI152NLin2009cAsym_AffineTransform.mat"
    elif [[ ${group} == "hcpya" ]]; then
        xfm_file="${xfm_dir}/${sub}/${sub}_from-T1w_to-MNI152NLin2009cAsym_AffineTransform.mat"
    fi
    if [ ! -f ${xfm_file} ]; then
        continue
    fi
    
    # Check if outputs directory already exists
    outputs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/bundleseg/${group}/${sub}
    if [ -d ${outputs_dir} ]; then
        continue
    fi

    sbatch --job-name=bundleseg_${sub}_${group} \
        --output=${logs_dir}/bundleseg_${group}_${sub}.o \
        --error=${logs_dir}/bundleseg_${group}_${sub}.e \
        --cpus-per-task=8 \
        --mem=48GB \
        ./run_bundleseg.sh ${group} ${sub}

    # Increment subject counter
    sub_counter=$((sub_counter + 1))
    if [[ ${sub_counter} -ge ${n_subs} ]]; then
        break
    fi

done
