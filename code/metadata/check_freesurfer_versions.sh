#!/bin/bash

# Count and print subjects without Freesurfer 7.1
count=0
for stamp in /mnt/leif/littlab/data/Human_Data/CNT_iEEG_BIDS/sub-*/derivatives/freesurfer/scripts/build-stamp.txt; do
    if [ -f "$stamp" ]; then
        # Read first line of build-stamp.txt
        first_line=$(head -n 1 "$stamp")
        # Check if it doesn't start with expected version
        if [[ ! "$first_line" =~ ^freesurfer-linux-centos6_x86_64-7.1.0 ]]; then
            echo "=== $stamp ==="
            cat "$stamp"
            echo
            ((count++))
        fi
    fi
done

echo "Total subjects without Freesurfer 7.1: $count"
