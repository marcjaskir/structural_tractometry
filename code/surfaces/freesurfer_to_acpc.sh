#!/bin/bash

########################################
# Read in group
########################################
group=${1}

########################################
# Read in license file
########################################
FS_LICENSE=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/qsiprep/license.txt

########################################
# Check for required files
########################################

qsirecon_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/${group}

for sub_dir in ${qsirecon_group_dir}/sub-*; do

    sub=$(basename $sub_dir)

    qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}/${sub}
    hcp_raw_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/hcpya/hcp1200/HCP1200
    fs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}/${sub}
    xfm_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces/${group}/${sub}

    # Check for a Freesurfer nu.mgz image
    if [[ ! -f ${fs_dir}/mri/nu.mgz ]]; then
        echo "No Freesurfer nu.mgz image for ${sub}"
        continue
    fi

    # Check for T1w ACPC image
    if [[ ${group} == "penn_epilepsy" || ${group} == "penn_controls" || ${group} == "hcpaging" ]]; then
        t1w=${qsiprep_dir}/anat/${sub}_space-ACPC_desc-preproc_T1w.nii.gz
    elif [[ ${group} == "hcpya" ]]; then
        hcp_id=$(echo ${sub} | sed 's/sub-//')
        t1w=${hcp_raw_dir}/${hcp_id}/T1w/T1w_acpc_dc_restore.nii.gz
    fi

    if [[ ! -f ${t1w} ]]; then
        echo "No T1w ACPC image for ${sub}"
        continue
    fi

    ########################################
    # Create output directories
    ########################################

    # Create xfm_dir if it doesn't exist
    if [[ ! -d ${xfm_dir} ]]; then
        mkdir -p ${xfm_dir}
    fi

    ########################################
    # Harmonize filetypes and orientations of Freesurfer and QSIPrep images
    ########################################

    ###############
    # Freesurfer
    ###############

    # Convert Freesurfer reference volumes (nu.mgz) to NIFTIs
    apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
    export SUBJECTS_DIR=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
    mri_convert --in_type mgz \
                --out_type nii \
                ${fs_dir}/mri/nu.mgz \
                ${xfm_dir}/${sub}.freesurfer.nu.LIA.nii.gz
    "

    # Change orientation of Freesurfer reference volumes to LAS+
    apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
    export SUBJECTS_DIR=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
    mri_convert --in_type nii \
                --out_type nii \
                --out_orientation LAS+ \
                ${xfm_dir}/${sub}.freesurfer.nu.LIA.nii.gz \
                ${xfm_dir}/${sub}.freesurfer.nu.nii.gz
    rm ${xfm_dir}/${sub}.freesurfer.nu.LIA.nii.gz
    "

    # Convert Freesurfer surfaces to GIFTIs
    # Keep in mind that --to-scanner is necessary but was not implemented in the Freesurfer 5.3 HCP XNAT apptainer image)
    mris_convert --to-scanner \
        ${fs_dir}/surf/lh.pial \
        ${xfm_dir}/${sub}.lh.pial.freesurfer.surf.gii

    mris_convert --to-scanner \
        ${fs_dir}/surf/rh.pial \
        ${xfm_dir}/${sub}.rh.pial.freesurfer.surf.gii

    mris_convert --to-scanner \
        ${fs_dir}/surf/lh.white \
        ${xfm_dir}/${sub}.lh.white.freesurfer.surf.gii

    mris_convert --to-scanner \
        ${fs_dir}/surf/rh.white \
        ${xfm_dir}/${sub}.rh.white.freesurfer.surf.gii

    ###############
    # QSIPrep
    ###############

    # Change orientation of QSIPrep T1w files to LAS+
    apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
    export SUBJECTS_DIR=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
    mri_convert --in_type nii \
                --out_type nii \
                --out_orientation LAS+ \
                ${t1w} \
                ${xfm_dir}/${sub}.native_acpc.desc-preproc_T1w.nii.gz
    "

    ########################################
    # Warp Freesurfer volume to QSIPrep volume
    ########################################

    # Compute affine
    flirt -in ${xfm_dir}/${sub}.freesurfer.nu.nii.gz \
        -ref ${xfm_dir}/${sub}.native_acpc.desc-preproc_T1w.nii.gz \
        -out ${xfm_dir}/${sub}.native_acpc.nu.nii.gz \
        -omat ${xfm_dir}/${sub}.freesurfer-to-native_acpc.xfm.mat

    # # Convert affine to lta format
    lta_convert --infsl ${xfm_dir}/${sub}.freesurfer-to-native_acpc.xfm.mat \
                --src ${xfm_dir}/${sub}.freesurfer.nu.nii.gz \
                --trg ${xfm_dir}/${sub}.native_acpc.desc-preproc_T1w.nii.gz \
                --outlta ${xfm_dir}/${sub}.freesurfer-to-native_acpc.xfm.lta
    rm ${xfm_dir}/${sub}.freesurfer-to-native_acpc.xfm.mat

    source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/structural_tractometry
    python freesurfer_to_acpc.py ${sub} ${group}

done