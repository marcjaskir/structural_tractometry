import os
from os.path import join as ospj
import pandas as pd
import numpy as np
from tqdm import tqdm
import json

# Specify wm_atlas
wm_atlas = "HCP1065"

# Specify pyafq (input) directory
pyafq_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/pyafq"

# Specify covbat (output) directory
covbat_base_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/pyafq"
if not os.path.exists(covbat_base_dir):
    os.makedirs(covbat_base_dir)

# Demographic files
hcpya_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_hcpya.csv"
hcpaging_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_hcpaging.csv"
penn_controls_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_penn_controls.csv"
penn_epilepsy_demo_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_penn_epilepsy.csv"

# Load in demo data
hcpya_demo = pd.read_csv(hcpya_demo_path)
hcpaging_demo = pd.read_csv(hcpaging_demo_path)
penn_controls_demo = pd.read_csv(penn_controls_demo_path)
penn_epilepsy_demo = pd.read_csv(penn_epilepsy_demo_path)

# Scanner files
hcpya_scanner_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_hcpya.csv"
hcpaging_scanner_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_hcpaging.csv"
penn_scanner_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_penn.csv"

# Load in scanner data
hcpya_scanner = pd.read_csv(hcpya_scanner_path)
hcpaging_scanner = pd.read_csv(hcpaging_scanner_path)
penn_scanner = pd.read_csv(penn_scanner_path)

# Measures files
measures_json_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/scalar_labels_to_filenames.json"

# Load in bundleseg json
bundleseg_json_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/bundleseg/config/config_HCP1065_association_projection.json"

# Specify output base directory
output_base_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/pyafq/{wm_atlas}"


# --- HELPERS ---

def get_demo_df(group):
    if group == "penn_epilepsy":
        return penn_epilepsy_demo
    elif group == "penn_controls":
        return penn_controls_demo
    elif group == "hcpya":
        return hcpya_demo
    elif group == "hcpaging":
        return hcpaging_demo
    else:
        raise ValueError(f"Unknown group: {group}")

def get_scanner_df(group):
    if group == "penn_epilepsy" or group == "penn_controls":
        return penn_scanner
    elif group == "hcpya":
        return hcpya_scanner
    elif group == "hcpaging":
        return hcpaging_scanner
    else:
        raise ValueError(f"Unknown group: {group}")

def get_subject_demo(sub, group):
    demo_df = get_demo_df(group)
    row = demo_df.loc[demo_df["sub"] == sub]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "sub": sub,
        "age": row["age"],
        "sex": row["sex"],
        "group": group
    }

def get_subject_scanner(sub, group):
    scanner_df = get_scanner_df(group)
    row = scanner_df.loc[scanner_df["sub"] == sub]
    if row.empty:
        return None
    row = row.iloc[0]
    return row["scanner_id"]

def prep_covbat_pyafq(pyafq_dir):

    # Read measures json
    measures = list(json.load(open(measures_json_path)).keys())

    # Read bundleseg json to infer which tracts were segmented
    tracts = json.load(open(bundleseg_json_path)).keys()
    tracts = [tract.replace(".trk", "") for tract in tracts]

    for tract in tracts:

        print(f"Preparing CovBat inputs for {tract}")

        # Define output directory
        output_dir = ospj(output_base_dir, tract)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for measure in tqdm(measures):

            data_dict = {}
            bat_dict = {}
            covar_dict = {}

            data_fname = f"{tract}_{measure}_data.csv"
            bat_fname = f"{tract}_{measure}_bat.csv"
            covar_fname = f"{tract}_{measure}_covar.csv"

            for group_dir in os.listdir(pyafq_dir):
                group_dir_path = ospj(pyafq_dir, group_dir)

                group = os.path.basename(group_dir_path)

                subs = [f for f in os.listdir(group_dir_path) if f.startswith("sub-")]
                for i, sub in enumerate(subs):

                    # Get demographics for this subject as a dictionary, e.g., {'sub': 'sub-XXXXXX', 'age': 34, 'sex': 'F', 'group': 'hcpya'}
                    demo = get_subject_demo(sub, group)
                    if demo is None:
                        continue

                    # Get scanner ID
                    scanner_id = get_subject_scanner(sub, group)
                    if pd.isnull(scanner_id):
                        continue

                    # Get path to profile
                    profile_path = ospj(group_dir_path, sub, wm_atlas, tract, "profile", f"{measure}_profile-pyafq.csv")
                    if not os.path.exists(profile_path):
                        continue

                    # Read profile
                    profile = pd.read_csv(profile_path, header=None)
                    profile = profile.iloc[:, 0].values

                    # Save sub and profile to data_dict
                    data_dict[sub] = profile

                    # Save scanner_id to bat_dict
                    bat_dict[sub] = {"bat": scanner_id}

                    # Save demographics to covar_dict
                    covar_dict[sub] = {"sub": demo["sub"], "age": demo["age"], "sex": demo["sex"], "group": demo["group"]}
                        
            # Convert dicts to DataFrames
            data_df = pd.DataFrame.from_dict(data_dict, orient="index")
            data_df.index.name = "sub"
            # For the columns containing the profile values, call it {measure}_node{node_index}
            data_df.columns = [f"{measure}_node{i+1}" for i in range(data_df.shape[1])]
            data_df.reset_index(inplace=True)

            # Bat: index=sub, column=bat
            bat_df = pd.DataFrame.from_dict(bat_dict, orient="index")
            bat_df.index.name = "sub"
            bat_df.reset_index(inplace=True)

            # Covar: index=sub, columns=sub, age, sex, group
            covar_df = pd.DataFrame.from_dict(covar_dict, orient="index")
            covar_df.index.name = "sub"
            covar_df.reset_index(drop=True, inplace=True)

            # Save DataFrames
            data_df.to_csv(ospj(output_dir, f"{data_fname}"), index=False)
            bat_df.to_csv(ospj(output_dir, f"{bat_fname}"), index=False)
            covar_df.to_csv(ospj(output_dir, f"{covar_fname}"), index=False)


# --- MAIN ---
prep_covbat_pyafq(pyafq_dir)
