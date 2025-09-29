#!/bin/bash

sub=sub-HCA9938309

qsiprep_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsiprep/hcpaging
qsirecon_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/hcpaging
trekker_dir=/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/trekker/hcpaging

# Check qsiprep subject directory
if [[ -d $qsiprep_dir/${sub} ]]; then
    rm -rf $qsiprep_dir/${sub}
    rm $qsiprep_dir/${sub}.html
fi

# Check qsirecon subject directory
if [[ -d $qsirecon_dir/${sub} ]]; then
    rm -rf $qsirecon_dir/${sub}
fi

# Check qsirecon derivatives directories/html files
if [[ -d $qsirecon_dir/derivatives/qsirecon-DIPYDKI/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-DIPYDKI/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-DIPYDKI/${sub}.html
fi

if [[ -d $qsirecon_dir/derivatives/qsirecon-DSIStudio/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-DSIStudio/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-DSIStudio/${sub}.html
fi

if [[ -d $qsirecon_dir/derivatives/qsirecon-MRtrix3_act-HSVS/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-MRtrix3_act-HSVS/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-MRtrix3_act-HSVS/${sub}.html
fi

if [[ -d $qsirecon_dir/derivatives/qsirecon-NODDI/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-NODDI/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-NODDI/${sub}.html
fi

if [[ -d $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-MAPMRI/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-MAPMRI/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-MAPMRI/${sub}.html
fi

if [[ -d $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-tensor/${sub} ]]; then
    rm -rf $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-tensor/${sub}
    rm $qsirecon_dir/derivatives/qsirecon-TORTOISE_model-tensor/${sub}.html
fi

# Check trekker subject directory
if [[ -d $trekker_dir/${sub} ]]; then
    rm -rf $trekker_dir/${sub}
fi