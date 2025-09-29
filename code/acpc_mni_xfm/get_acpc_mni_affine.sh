#!/bin/bash

group=hcpaging

code_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/acpc_mni_xfm
qsiprep_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}
acpc_mni_xfm_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/acpc_mni_xfm/${group}

for sub_dir in ${qsiprep_group_dir}/sub-*; do
    sub=$(basename ${sub_dir})

    xfm_file=${qsiprep_group_dir}/${sub}/anat/${sub}_from-ACPC_to-MNI152NLin2009cAsym_mode-image_xfm.h5
    if [[ -f ${xfm_file} ]]; then

        outdir=${acpc_mni_xfm_group_dir}/${sub}

	if [[ ! -f ${outdir}/${sub}_from-ACPC_to-MNI152NLin2009cAsym_AffineTransform.mat ]]; then
                echo ${sub}
                mkdir -p ${outdir}
        	CompositeTransformUtil --disassemble ${xfm_file} ${sub}_from-ACPC_to-MNI152NLin2009cAsym

        	# Move transforms to output directory
        	mv ${code_dir}/00_${sub}_from-ACPC_to-MNI152NLin2009cAsym_AffineTransform.mat ${outdir}/${sub}_from-ACPC_to-MNI152NLin2009cAsym_AffineTransform.mat
        	mv ${code_dir}/01_${sub}_from-ACPC_to-MNI152NLin2009cAsym_DisplacementFieldTransform.nii.gz ${outdir}/${sub}_from-ACPC_to-MNI152NLin2009cAsym_DisplacementFieldTransform.nii.gz
        fi
    fi
done
