#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=48GB
#SBATCH --job-name=qsirecon

SUBJ=${1}
GROUP=${2}
# SUBJ=sub-RID0505

# Specify temp directory for apptainer
export APPTAINER_TMPDIR=/home/mjaskir/software/apptainer/apptainer_tmp

# Define key directories
BASE=/mnt/sauce/littlab/users/mjaskir/structural_tractometry
QSIRECON_IMG=${BASE}/code/qsirecon/qsirecon-1.0.0rc2.sif #  path to qsiprep image
FSLIC=${BASE}/code/qsirecon/license.txt
WORK=${BASE}/code/qsirecon/work && mkdir -p ${WORK}
OUTDIR=${BASE}/derivatives/qsirecon/${GROUP}
GLASSER_ATLAS=${BASE}/code/qsirecon/glasser_atlas

cmd="apptainer run \
-B $BASE:/mnt/structural_tractometry \
-B $FSLIC:/mnt/structural_tractometry/code/qsirecon/license.txt \
-B $GLASSER_ATLAS:/glasser_atlas \
$QSIRECON_IMG \
/mnt/structural_tractometry/derivatives/qsiprep/${GROUP} \
/mnt/structural_tractometry/derivatives/qsirecon/${GROUP} \
participant \
--participant-label $SUBJ \
--work-dir /mnt/structural_tractometry/code/qsirecon/work \
--nthreads 4 \
--omp-nthreads 4 \
--atlases 4S456Parcels Glasser \
--datasets /glasser_atlas \
--fs-subjects-dir /mnt/structural_tractometry/derivatives/freesurfer/${GROUP} \
--fs-license-file /mnt/structural_tractometry/code/qsirecon/license.txt \
--recon-spec /mnt/structural_tractometry/code/qsirecon/recon_spec_custom.yaml"

echo $cmd
$cmd
