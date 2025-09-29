#!/bin/bash

import_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/import/hcpaging/fmriresults01
output_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/hcpaging; mkdir -p ${output_dir}

for sub_dir in ${import_dir}/HCA*; do
    
    sub_hcp=$(basename ${sub_dir})

    # Remove everything past first underscore and add sub- prefix
    sub_id=${sub_hcp/_*}
    sub=sub-${sub_id}

    # Create sub-dir in output_dir
    mkdir -p ${output_dir}/${sub}

    import_sub_dir=${import_dir}/${sub_hcp}/T1w/${sub_hcp}

    for fs_dir in ${import_sub_dir}/*; do

        if [ -d ${fs_dir} ]; then

            if [ ! -d ${output_dir}/${sub} ]; then

                fs_dir_name=$(basename ${fs_dir})
                mv ${fs_dir} ${output_dir}/${sub}

            fi

        fi

    done

done
