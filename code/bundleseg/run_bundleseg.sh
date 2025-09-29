#!/bin/bash

group=${1}
sub=${2}

source activate /mnt/sauce/littlab/users/mjaskir/software/miniconda3/envs/structural_tractometry

python run_bundleseg.py ${group} ${sub}