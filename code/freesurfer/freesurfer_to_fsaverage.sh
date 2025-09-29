#!/bin/bash

group="penn_controls"
sub="sub-RID0505"

freesurfer_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}
output_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}/${sub}/surf
mkdir -p ${output_dir}

apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
export SUBJECTS_DIR=${freesurfer_dir}
mri_surf2surf --srcsubject ${sub} \
--srchemi lh \
--sval thickness \
--srcsurfreg sphere.reg \
--sfmt curv \
--trgsubject fsaverage \
--trghemi lh \
--trgsurfreg sphere.reg \
--tval ${output_dir}/fsaverage.lh.thickness.mgh \
--noreshape \
--cortex
"

# Convert .mgh to .gii
apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
mri_convert ${output_dir}/fsaverage.lh.thickness.mgh \
${output_dir}/fsaverage.lh.thickness.shape.gii \
--in_type mgh \
--out_type gii
"

# Remove .mgh file
rm ${output_dir}/fsaverage.lh.thickness.mgh

# mri_surf2surf --srcsubject ${sub} \
# --srchemi lh \
# --srcsurfreg ${sub}/surf/lh.sphere.reg \
# --trgsubject fsaverage \
# --trghemi lh \
# --trgsurfreg ${sub}/surf/fsaverage.lh.sphere.reg \
# --tval ${sub}/surf/fsaverage.lh.thickness \
# --sval ${sub}/surf/lh.thickness \
# --sfmt curv \
# --noreshape \
# --cortex