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
# Activate conda environment
########################################
source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/structural_tractometry

########################################
# Check for required files
########################################

surface_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces/${group}
fs_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}

scalar_files="lh.area rh.area lh.curv rh.curv lh.jacobian_white rh.jacobian_white lh.sulc rh.sulc lh.thickness rh.thickness lh.volume rh.volume"

for sub_dir in ${surface_dir}/sub-*; do
    sub=$(basename ${sub_dir})
    echo ${sub}

    # Skip if ${sub}.lh.thickness.native_acpc.shape.gii exists
    if [[ -f ${sub_dir}/${sub}.lh.thickness.native_acpc.shape.gii ]]; then
        echo "-- Skipping - scalars already converted for ${sub}"
        continue
    fi

    # Check that lta file exists
    if [[ ! -f ${sub_dir}/${sub}.freesurfer-to-native_acpc.xfm.lta ]]; then
        echo "No lta file for ${sub}"
        continue
    fi

    # Check that left and right white surfaces in ACPC exist
    lh_white_acpc=${sub_dir}/${sub}.lh.white.native_acpc.surf.gii
    rh_white_acpc=${sub_dir}/${sub}.rh.white.native_acpc.surf.gii
    lh_pial_acpc=${sub_dir}/${sub}.lh.pial.native_acpc.surf.gii
    rh_pial_acpc=${sub_dir}/${sub}.rh.pial.native_acpc.surf.gii
    if [[ ! -f ${lh_white_acpc} || ! -f ${rh_white_acpc} ]]; then
        echo "-- Missing lh.white or rh.white surface in ACPC for ${sub}"
        continue
    fi
    if [[ ! -f ${lh_pial_acpc} || ! -f ${rh_pial_acpc} ]]; then
        echo "-- Missing lh.pial or rh.pial surface in ACPC for ${sub}"
        continue
    fi

    # Set structure of white and pial surfaces
    wb_command -set-structure ${lh_white_acpc} CORTEX_LEFT
    wb_command -set-structure ${rh_white_acpc} CORTEX_RIGHT
    wb_command -set-structure ${lh_pial_acpc} CORTEX_LEFT
    wb_command -set-structure ${rh_pial_acpc} CORTEX_RIGHT

    # Check that scalar files exist
    for scalar_file in ${scalar_files}; do
        if [[ ! -f ${fs_dir}/${sub}/surf/${scalar_file} ]]; then
            echo "-- No ${scalar_file} file for ${sub}"
            continue
        fi

        hemi=$(echo ${scalar_file} | cut -d '.' -f 1)

        echo "-- ${scalar_file}"

        # Convert Freesurfer surfaces to GIFTIs
        if [[ ${hemi} == "lh" ]]; then
            mris_convert \
                -c ${fs_dir}/${sub}/surf/${scalar_file} \
                ${lh_white_acpc} \
                ./${sub}.${scalar_file}.native_acpc.shape.gii
        elif [[ ${hemi} == "rh" ]]; then
            mris_convert \
                -c ${fs_dir}/${sub}/surf/${scalar_file} \
                ${rh_white_acpc} \
                ./${sub}.${scalar_file}.native_acpc.shape.gii
        fi

        # Move to surface directory
        mv ./unknown.${sub}.${scalar_file}.native_acpc.shape.gii ${sub_dir}/${sub}.${scalar_file}.native_acpc.shape.gii

        # Set structure of scalar file
        if [[ ${hemi} == "lh" ]]; then
            wb_command -set-structure ${sub_dir}/${sub}.${scalar_file}.native_acpc.shape.gii CORTEX_LEFT
        elif [[ ${hemi} == "rh" ]]; then
            wb_command -set-structure ${sub_dir}/${sub}.${scalar_file}.native_acpc.shape.gii CORTEX_RIGHT
        fi
        
    done

    echo ""


done
