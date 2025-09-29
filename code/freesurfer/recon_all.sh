#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=32GB
#SBATCH --job-name=recon_all

sub=${1}
group=${2}

qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/${group}
freesurfer_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/${group}

apptainer exec -B /mnt/sauce:/mnt/sauce --writable-tmpfs -e /mnt/sauce/littlab/users/mjaskir/software/apptainer/freesurfer_5.3.0-HCP_XNAT.simg /bin/bash -c "
export SUBJECTS_DIR=${freesurfer_dir}
recon-all -i ${qsiprep_dir}/${sub}/anat/${sub}_space-ACPC_desc-preproc_T1w.nii.gz -s ${sub} -all
"