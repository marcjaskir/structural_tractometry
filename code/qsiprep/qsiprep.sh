#!/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH --job-name=qsiprep

SUBJ=${1}
GROUP=${2}
SES=${3}

# Specify temp directory for apptainer
export APPTAINER_TMPDIR=/mnt/sauce/littlab/users/mjaskir/software/apptainer/apptainer_tmp

# Define key directories
BASE=/mnt/sauce/littlab/users/mjaskir/structural_tractometry
DATA=/mnt/sauce/littlab/users/mjaskir/penn_neurobridge_epilepsy
QSIPREP_IMG=${BASE}/code/qsiprep/qsiprep-1.0.0.sif #  path to qsiprep image
FSLIC=${BASE}/code/qsiprep/license.txt
# WORK=${BASE}/code/qsiprep/work && mkdir -p ${WORK}
# OUTDIR=${BASE}/derivatives/qsiprep/${SITE}

# Run qsiprep

# If a session is provided, use it
if [[ ${GROUP} == "penn_controls" ]] || [[ ${GROUP} == "penn_epilepsy" ]]; then

    cmd="apptainer run \
    -B $DATA:/mnt/penn_neurobridge_epilepsy \
    -B $BASE:/mnt/structural_tractometry \
    -B $FSLIC:/mnt/structural_tractometry/code/qsiprep/license.txt \
    $QSIPREP_IMG \
    /mnt/penn_neurobridge_epilepsy/ \
    /mnt/structural_tractometry/derivatives/qsiprep/${GROUP} \
    participant \
    --participant-label $SUBJ \
    --session-id $SES \
    --work-dir /mnt/structural_tractometry/code/qsiprep/work \
    --skip-bids-validation \
    --output-resolution 1.25 \
    --unringing-method rpg \
    --denoise-method dwidenoise \
    --fs-license-file /mnt/structural_tractometry/code/qsiprep/license.txt"

elif [[ ${GROUP} == "hcpaging" ]]; then

    cmd="apptainer run \
    -B $BASE:/mnt/structural_tractometry \
    -B $FSLIC:/mnt/structural_tractometry/code/qsiprep/license.txt \
    $QSIPREP_IMG \
    /mnt/structural_tractometry/data/${GROUP} \
    /mnt/structural_tractometry/derivatives/qsiprep/${GROUP} \
    participant \
    --participant-label $SUBJ \
    --work-dir /mnt/structural_tractometry/code/qsiprep/work \
    --skip-bids-validation \
    --output-resolution 1.25 \
    --unringing-method rpg \
    --denoise-method dwidenoise \
    --fs-license-file /mnt/structural_tractometry/code/qsiprep/license.txt"
fi



echo $cmd
$cmd
