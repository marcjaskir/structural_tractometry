import os
import pandas as pd

# Path to the clinical metadata CSV
clinical_csv = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/clinical_penn_epilepsy.csv"

# Path to the qsirecon subject directories
qsirecon_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/penn_epilepsy"

# Load the clinical metadata
clinical_df = pd.read_csv(clinical_csv)

# Get list of subject directory names (sub-*)
subject_dirs = [
    d for d in os.listdir(qsirecon_dir)
    if os.path.isdir(os.path.join(qsirecon_dir, d)) and d.startswith("sub-")
]

# Create a DataFrame from the subject directory names
subjects_df = pd.DataFrame({'sub': subject_dirs})

# Merge the subject directories with the clinical metadata on 'sub'
merged_df = subjects_df.merge(clinical_df, on='sub', how='left')

# Sort by sub
merged_df = merged_df.sort_values("sub")

# Save to /mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata
merged_df.to_csv("/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/clinical_penn_epilepsy_qsirecon.csv", index=False)
