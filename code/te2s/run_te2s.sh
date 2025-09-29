#!/bin/bash

# TODO: Will need to update this such that it reads in the tract metadata and determines which end(s) of the tract
# to map (both for association, cortex sides only for projection)

# Specify group to perform TE2S on
group="penn_controls"

# Define input directories
bundleseg_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/bundleseg/${group}
surface_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces/${group}
te2s_group_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/te2s/${group}; mkdir -p ${te2s_group_dir}

# Iterate over subjects with bundleseg outputs
for sub_dir in ${bundleseg_group_dir}/sub-RID0505*; do
    sub=$(basename ${sub_dir})

    # Check if ACPC surfaces exist for this subject
    if [[ ! -d ${surface_group_dir}/${sub} ]]; then
        continue
    fi

    # Check if TE2S outputs exist for this subject
    if [[ -d ${te2s_group_dir}/${sub} ]]; then
        continue
    fi

    python te2s.py ${group} ${sub}

    ./te2s.sh ${group} ${sub}

done
