
# Per measure, will need:
    # data (df) <- n_subjects x (1 + n_measures)
    # bat (Factor) <- n_subjects x 1 
    # covar <- n_subjects x 2 (age, sex)

import os
from os.path import join as ospj
import pandas as pd
import numpy as np

# SPECIFY LABEL FOR COVBAT INPUTS
tract_stats_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/tract_stats/mni"
covbat_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/tract_stats/mni"

# Create covbat_dir if it doesn't exist
if not os.path.exists(covbat_dir):
    os.makedirs(covbat_dir)

# Define path to demographic data
hcpya_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/hcpya_basic_demo.csv"
penn_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/penn_basic_demo.csv"

# Define tract labels and stats to process
tract_atlas_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/hcp1065/all_nii"
tract_labels = [f for f in os.listdir(tract_atlas_dir) if f.endswith(".nii.gz")]
tract_labels = [f.split(".")[0] for f in tract_labels]
#tract_labels = ["C_FPH_L", "C_FPH_R", "C_PH_L", "C_PH_R", "C_PO_L", "C_PO_R", "F_L", "F_R", "UF_L", "UF_R"]
stats = ["mean", "median"]

# Load in demo data
hcpya_demo = pd.read_csv(hcpya_demo_path)
penn_demo = pd.read_csv(penn_demo_path)

for tract in tract_labels:
    for stat in stats:

        # Initialize empty dataframe/lists for this tract/stat combination
        data = pd.DataFrame()
        bat = []
        covar = []
        for group_dir in os.listdir(tract_stats_dir):
            group_dir_path = ospj(tract_stats_dir, group_dir)
            group = os.path.basename(group_dir_path)
            
            # Iterate over subject directories
            for sub_dir in os.listdir(group_dir_path):
                sub_dir_path = ospj(group_dir_path, sub_dir)
                sub = os.path.basename(sub_dir_path)

                # Check that there are 20 files in sub_dir - if not, skip
                # if len(os.listdir(sub_dir_path)) != 20:
                #     continue

                # Check that their age is not below 22 or above 35
                demo_df = hcpya_demo if group == "hcpya" else penn_demo
                if demo_df.loc[demo_df["sub"] == sub, "age"].values[0] < 22 or demo_df.loc[demo_df["sub"] == sub, "age"].values[0] > 35:
                    continue

                # Load and process stats data
                stat_fname = f"{sub}_tract-{tract}_stats-{stat}.csv"
                stat_df = pd.read_csv(ospj(sub_dir_path, stat_fname))
                stat_df = stat_df.drop(columns=["tract"])
                data = pd.concat([data, stat_df], ignore_index=True)
                
                # Set batch indicator
                if group == "penn_epilepsy":
                    bat.append(0)
                elif group == "penn_controls":
                    bat.append(0)
                elif group == "hcpya":
                    bat.append(1)
                
                # Add age and sex to covar
                age = demo_df.loc[demo_df["sub"] == sub, "age"].values[0]
                sex = demo_df.loc[demo_df["sub"] == sub, "sex"].values[0]

                covar.append([age, sex, group])

        # Save processed data
        data.to_csv(ospj(covbat_dir, f"{tract}_{stat}_data.csv"), index=False)
        pd.DataFrame(bat, columns=["bat"]).to_csv(ospj(covbat_dir, f"{tract}_{stat}_bat.csv"), index=False)
        pd.DataFrame(covar, columns=["age", "sex", "group"]).to_csv(ospj(covbat_dir, f"{tract}_{stat}_covar.csv"), index=False)
