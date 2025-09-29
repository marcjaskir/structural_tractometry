#!/bin/bash

group=${1}
sub=${2}

########################################
# Map tract volumes to native surfaces
########################################

bundleseg_sub_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/bundleseg/${group}/${sub}
surface_sub_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces/${group}/${sub}
te2s_outputs_sub_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/te2s/${group}/${sub}

for nii_file in ${bundleseg_sub_dir}/*.nii.gz; do

    # Extract tract label
    tract_label=$(basename ${nii_file} .nii.gz)

    echo "Running TE2S for ${sub} - ${tract_label}"

    te2s_outputs_dir=${te2s_outputs_sub_dir}/${tract_label}; mkdir -p ${te2s_outputs_dir}
        
    # Map tract to native surfaces
    wb_command -volume-to-surface-mapping \
        ${nii_file} \
        ${surface_sub_dir}/${sub}.lh.white.native_acpc.surf.gii \
        ${te2s_outputs_dir}/${sub}.${tract_label}.lh.white.native_acpc.shape.gii \
        -trilinear

    wb_command -volume-to-surface-mapping \
        ${nii_file} \
        ${surface_sub_dir}/${sub}.rh.white.native_acpc.surf.gii \
        ${te2s_outputs_dir}/${sub}.${tract_label}.rh.white.native_acpc.shape.gii \
        -trilinear

done