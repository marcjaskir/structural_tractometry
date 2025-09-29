#!/bin/bash

logs_dir="/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/trekker/logs"; mkdir -p ${logs_dir}

sbatch --job-name=convert_tck_to_trk \
    --output=${logs_dir}/convert_tck_to_trk.o \
    --error=${logs_dir}/convert_tck_to_trk.e \
    --cpus-per-task=4 \
    --mem=48GB \
    ./convert_tck_to_trk.sh