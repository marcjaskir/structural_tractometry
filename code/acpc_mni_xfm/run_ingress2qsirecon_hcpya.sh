#!/bin/bash

# trekker_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/trekker/hcpya
hcp_raw_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/hcpya/hcp1200/HCP1200
outdir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/acpc_mni_xfm/hcpya
logs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/acpc_mni_xfm/logs
mkdir -p ${logs_dir}

sublist=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/hcp_dwi_trekker_batch-1_hcpya_subjects.csv

n_subs=1

# NOTE: Keep in mind that if not using sublist, fix so that input to ingress2qsirecon_hcpya.sh includes sub- prefix

sub_counter=0
for sub_dir in ${hcp_raw_dir}/100206*; do
# while read -r sub_id; do
    sub_id=$(basename ${sub_dir})
    sub=sub-${sub_id}
    
    # sub_dir=${hcp_raw_dir}/${sub_id}


    # First check if already run
    # if [[ -f ${outdir}/sub-${sub_id}/sub-${sub_id}_from-T1w_to-MNI152NLin2009cAsym_AffineTransform.mat ]]; then
    #     echo "-- Already run for ${sub_id}"
    #     continue
    # fi

    if [[ -f ${outdir}/${sub}/${sub}_from-T1w_to-MNI152NLin2009cAsym_AffineTransform.mat ]]; then
        echo "-- Already run for ${sub_id}"
        continue
    fi

    logs_output=${logs_dir}/ingress2qsirecon_hcpya_${sub}.o
    logs_error=${logs_dir}/ingress2qsirecon_hcpya_${sub}.e

    sbatch --output=${logs_output} --error=${logs_error} --mem=4GB ./ingress2qsirecon_hcpya.sh ${sub}

    sub_counter=$((sub_counter + 1))
    if [[ $sub_counter -ge $n_subs ]]; then
        break
    fi

done
# done < ${sublist}