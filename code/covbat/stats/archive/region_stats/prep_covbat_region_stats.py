
# Per measure, will need:
    # data (df) <- n_subjects x (1 + n_measures)
    # bat (Factor) <- n_subjects x 1 
    # covar <- n_subjects x 2 (age, sex)

import os
from os.path import join as ospj
import pandas as pd
import numpy as np
from tqdm import tqdm

# Specify CovBat method
method = "reference-penn"

# Specify input/output directories
region_stats_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/region_stats/mni"
covbat_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/region_stats/mni/{method}"

# Create covbat_dir if it doesn't exist
if not os.path.exists(covbat_dir):
    os.makedirs(covbat_dir)

# Define path to demographic data
hcpya_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_hcpya.csv"
hcpaging_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_hcpaging.csv"
penn_controls_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_penn_controls.csv"
penn_epilepsy_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_penn_epilepsy.csv"

# Load in demo data
hcpya_demo = pd.read_csv(hcpya_demo_path)
hcpaging_demo = pd.read_csv(hcpaging_demo_path)
penn_controls_demo = pd.read_csv(penn_controls_demo_path)
penn_epilepsy_demo = pd.read_csv(penn_epilepsy_demo_path)

# Define path to scanner_ids data
hcpya_scanner_ids_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_hcpya.csv"
hcpaging_scanner_ids_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_hcpaging.csv"
penn_scanner_ids_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_penn.csv"

# Load in scanner_ids data
hcpya_scanner_ids = pd.read_csv(hcpya_scanner_ids_path)
hcpaging_scanner_ids = pd.read_csv(hcpaging_scanner_ids_path)
penn_scanner_ids = pd.read_csv(penn_scanner_ids_path)

# Merge scanner IDs with demographics
hcpya_demo = pd.merge(hcpya_demo, hcpya_scanner_ids, on='sub', how='left')
hcpaging_demo = pd.merge(hcpaging_demo, hcpaging_scanner_ids, on='sub', how='left')
penn_controls_demo = pd.merge(penn_controls_demo, penn_scanner_ids, on='sub', how='left')
penn_epilepsy_demo = pd.merge(penn_epilepsy_demo, penn_scanner_ids, on='sub', how='left')

# Load atlas-4S156Parcels_dseg.tsv
atlas_metadata = pd.read_csv("/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/atlas-4S156Parcels_dseg.tsv", sep="\t")
region_labels = atlas_metadata["label"].values

# Define stats
stats = ["mean", "median"]

for region in tqdm(region_labels):
    for stat in stats:

        # Initialize empty dataframe/lists for this tract/stat combination
        data = pd.DataFrame()
        bat = []
        covar = []
        for group_dir in os.listdir(region_stats_dir):
            group_dir_path = ospj(region_stats_dir, group_dir)
            group = os.path.basename(group_dir_path)

            # Load .csv file corresponding to region and stat
            region_stat_fname = f"region-{region}_stat-{stat}.csv"
            region_stat_df = pd.read_csv(ospj(group_dir_path, region_stat_fname))
            subs = region_stat_df["sub"].values
            
            # Iterate over subject directories
            for sub in subs:

                # Load in correct demographics. check serial number for that subject if necessary
                if group == "penn_epilepsy":
                    demo_df = penn_epilepsy_demo
                elif group == "penn_controls":
                    demo_df = penn_controls_demo
                elif group == "hcpya":
                    demo_df = hcpya_demo
                elif group == "hcpaging":
                    demo_df = hcpaging_demo

                # Add subjects' data
                region_stat_sub_df = region_stat_df[region_stat_df["sub"] == sub]
                region_stat_sub_df = region_stat_sub_df.drop(columns=["sub"])
                data = pd.concat([data, region_stat_sub_df], ignore_index=True)
                
                if method == "reference-penn":

                    if group == "penn_epilepsy":
                        bat.append(0)
                    elif group == "penn_controls":
                        bat.append(0)
                    elif group == "hcpya":
                        bat.append(1)
                    elif group == "hcpaging":

                        # Determine batch number based on scanner_id in demo_df
                        # [166007 166038  67089  67026  67064  67040]
                        scanner_id = demo_df.loc[demo_df["sub"] == sub, "scanner_id"].values[0]
                        if scanner_id == 166007:
                            bat.append(2)
                        elif scanner_id == 166038:
                            bat.append(3)
                        elif scanner_id == 67026:
                            bat.append(4)
                        elif scanner_id == 67089:
                            bat.append(5)
                        elif scanner_id == 67040:
                            bat.append(6)
                        elif scanner_id == 67064:
                            bat.append(7)

                # Add age and sex to covar
                age = demo_df.loc[demo_df["sub"] == sub, "age"].values[0]
                sex = demo_df.loc[demo_df["sub"] == sub, "sex"].values[0]

                covar.append([sub, age, sex, group])

        # Save processed data
        data.to_csv(ospj(covbat_dir, f"{region}_{stat}_data.csv"), index=False)
        pd.DataFrame(bat, columns=["bat"]).to_csv(ospj(covbat_dir, f"{region}_{stat}_bat.csv"), index=False)
        pd.DataFrame(covar, columns=["sub","age", "sex", "group"]).to_csv(ospj(covbat_dir, f"{region}_{stat}_covar.csv"), index=False)
