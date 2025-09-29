
# Per measure, will need:
    # data (df) <- n_subjects x (1 + n_measures)
    # bat (Factor) <- n_subjects x 1 
    # covar <- n_subjects x 2 (age, sex)

import os
from os.path import join as ospj
import pandas as pd
import numpy as np
from tqdm import tqdm

# Specify input/output directories
tract_stats_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/tract_stats/mni"
covbat_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/tract_stats/mni"

# Create covbat_dir if it doesn't exist
if not os.path.exists(covbat_dir):
    os.makedirs(covbat_dir)

# Define path to demographic data
hcpya_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/hcpya_basic_demo.csv"
penn_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/penn_basic_demo.csv"

# Define tract labels
tract_atlas_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/hcp1065/all_nii"
tract_labels = [f for f in os.listdir(tract_atlas_dir) if f.endswith(".nii.gz")]
tract_labels = [f.split(".")[0] for f in tract_labels]

# Define stats
stats = ["mean", "median"]

# Load in demo data
hcpya_demo = pd.read_csv(hcpya_demo_path)
penn_demo = pd.read_csv(penn_demo_path)

for tract in tqdm(tract_labels):
    for stat in stats:

        # Initialize empty dataframe/lists for this tract/stat combination
        data = pd.DataFrame()
        bat = []
        covar = []
        for group_dir in os.listdir(tract_stats_dir):
            group_dir_path = ospj(tract_stats_dir, group_dir)
            group = os.path.basename(group_dir_path)

            # Load .csv file corresponding to region and stat
            tract_stat_fname = f"tract-{tract}_stat-{stat}.csv"
            tract_stat_df = pd.read_csv(ospj(group_dir_path, tract_stat_fname))
            subs = tract_stat_df["sub"].values
            
            # Iterate over subject directories
            for sub in subs:

                # Check that there are 20 files in sub_dir - if not, skip
                # if len(os.listdir(sub_dir_path)) != 20:
                #     continue

                # Check that their age is not below 22 or above 35
                demo_df = hcpya_demo if group == "hcpya" else penn_demo
                if demo_df.loc[demo_df["sub"] == sub, "age"].values[0] < 22 or demo_df.loc[demo_df["sub"] == sub, "age"].values[0] > 35:
                    continue

                # Add subjects' data
                tract_stat_sub_df = tract_stat_df[tract_stat_df["sub"] == sub]
                tract_stat_sub_df = tract_stat_sub_df.drop(columns=["sub"])
                data = pd.concat([data, tract_stat_sub_df], ignore_index=True)
                
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

                covar.append([sub, age, sex, group])

        # Save processed data
        data.to_csv(ospj(covbat_dir, f"{tract}_{stat}_data.csv"), index=False)
        pd.DataFrame(bat, columns=["bat"]).to_csv(ospj(covbat_dir, f"{tract}_{stat}_bat.csv"), index=False)
        pd.DataFrame(covar, columns=["sub","age", "sex", "group"]).to_csv(ospj(covbat_dir, f"{tract}_{stat}_covar.csv"), index=False)
