import os
from os.path import join as ospj
import pandas as pd
import numpy as np
from tqdm import tqdm
import json


# Inputs
covbat_inputs_type = "regions" # input type (options: tracts, regions)
wm_atlas = "HCP1065"
gm_atlas = "4S156"

# Directories for region and tract stats
region_stats_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/region_stats/{gm_atlas}"
tract_stats_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/tract_stats/{wm_atlas}"

# Output directory - NOTE: Remember to remove _penn when we add in HCP
if covbat_inputs_type == "tracts":
    output_base_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/{covbat_inputs_type}/{wm_atlas}"
elif covbat_inputs_type == "regions":
    output_base_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/inputs/{covbat_inputs_type}/{gm_atlas}"
else:
    raise ValueError(f"Unknown covbat_inputs_type: {covbat_inputs_type}")

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

# Read in measures json
with open(measures_json_path, "r") as f:
    measures = json.load(f)

# Read measures json
measures = list(json.load(open(measures_json_path)).keys())

stats = ["mean", "median"]

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

def append_or_write_df(df, out_path, index_col=None):
    """
    If out_path exists, append df to it. Otherwise, write df as new file.
    If index_col is provided, merge on that column and update/append as needed.
    """
    if os.path.exists(out_path):
        existing_df = pd.read_csv(out_path)
        if index_col is not None:
            # Merge on index_col, update values, append new rows
            existing_df.set_index(index_col, inplace=True)
            df.set_index(index_col, inplace=True)
            # Update existing rows and add new ones
            existing_df.update(df)
            combined_df = pd.concat([existing_df, df[~df.index.isin(existing_df.index)]], axis=0)
            combined_df.reset_index(inplace=True)
            combined_df.to_csv(out_path, index=False)
        else:
            # Concatenate and drop duplicates if any (optional)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_csv(out_path, index=False)
    else:
        df.to_csv(out_path, index=False)

def process_stats_dir(stats_dir, is_region=True):
    """
    Process a stats directory (region or tract).
    For each region/tract, stat, and measure, create three files:
      - {tract}/{tract}_{stat}_data.csv: contains all measures as columns, one row per subject
      - {tract}/{tract}_{stat}_bat.csv: contains a single column 'bat' with scanner_id for each subject
      - {tract}/{tract}_{stat}_covar.csv: contains sub, age, sex, group
    If the output file exists, append group-level data to it; otherwise, write new.
    """
    for group_dir in os.listdir(stats_dir):
        group_dir_path = ospj(stats_dir, group_dir)
        if not os.path.isdir(group_dir_path):
            continue
        group = os.path.basename(group_dir_path)

        files = [f for f in os.listdir(group_dir_path) if f.endswith(".csv")]
        for f in files:

            # Expecting filenames like: region-RegionName_stat-mean.csv or tract-TractName_stat-mean.csv
            if is_region and not f.startswith("region-"):
                continue
            if not is_region and not f.startswith("tract-"):
                continue
            # Parse region/tract and stat
            try:
                base, stat_part = f.split("_stat-")
                name = base.split("-", 1)[1]
                stat = stat_part.replace(".csv", "")
            except Exception:
                continue
            if stat not in stats:
                continue
            df = pd.read_csv(ospj(group_dir_path, f))
            if "sub" not in df.columns:
                continue
            subs = df["sub"].values

            # Prepare output directory for this tract/region
            out_dir = ospj(output_base_dir, name)
            os.makedirs(out_dir, exist_ok=True)
            prefix = name
            out_data_fname = f"{prefix}_{stat}_data.csv"
            out_bat_fname = f"{prefix}_{stat}_bat.csv"
            out_covar_fname = f"{prefix}_{stat}_covar.csv"
            out_data_path = ospj(out_dir, out_data_fname)
            out_bat_path = ospj(out_dir, out_bat_fname)
            out_covar_path = ospj(out_dir, out_covar_fname)

            # --- For each measure, add as a column to the data file ---
            # We'll build a DataFrame with sub as index, and each measure as a column
            # We'll also build bat and covar DataFrames (one row per subject)
            data_dict = {}
            bat_dict = {}
            covar_dict = {}

            for measure in measures:
                if measure not in df.columns:
                    continue
                for i, sub in enumerate(subs):
                    demo = get_subject_demo(sub, group)
                    if demo is None:
                        continue
                    scanner_id = get_subject_scanner(sub, group)
                    if pd.isnull(scanner_id):
                        continue
                    value = df.loc[df["sub"] == sub, measure].values
                    if len(value) == 0:
                        continue
                    value = value[0]
                    # Add measure value to data_dict
                    if sub not in data_dict:
                        data_dict[sub] = {}
                    data_dict[sub][measure] = value
                    # Add scanner_id to bat_dict
                    if sub not in bat_dict:
                        bat_dict[sub] = {"bat": scanner_id}
                    # Add covariates to covar_dict
                    if sub not in covar_dict:
                        covar_dict[sub] = {
                            "sub": demo["sub"],
                            "age": demo["age"],
                            "sex": demo["sex"],
                            "group": demo["group"]
                        }
                    print(f"Processing subject: {sub} | group: {group} | {'region' if is_region else 'tract'}: {name} | stat: {stat} | measure: {measure}")

            if not data_dict:
                continue

            # Convert dicts to DataFrames
            # Data: index=sub, columns=measures
            data_df = pd.DataFrame.from_dict(data_dict, orient="index")
            data_df.index.name = "sub"
            data_df.reset_index(inplace=True)

            # Bat: index=sub, column=bat
            bat_df = pd.DataFrame.from_dict(bat_dict, orient="index")
            bat_df.index.name = "sub"
            bat_df.reset_index(inplace=True)

            # Covar: index=sub, columns=sub, age, sex, group
            covar_df = pd.DataFrame.from_dict(covar_dict, orient="index")
            covar_df.index.name = "sub"
            covar_df.reset_index(drop=True, inplace=True)

            # Save or append *_data.csv (all measures as columns, sub as index)
            append_or_write_df(data_df, out_data_path, index_col="sub")

            # Save or append *_bat.csv (bat column only, sub as index)
            append_or_write_df(bat_df, out_bat_path, index_col="sub")

            # Save or append *_covar.csv (sub, age, sex, group)
            append_or_write_df(covar_df, out_covar_path, index_col="sub")

# --- MAIN ---

if covbat_inputs_type == "regions":
    process_stats_dir(region_stats_dir, is_region=True)
elif covbat_inputs_type == "tracts":
    process_stats_dir(tract_stats_dir, is_region=False)
elif covbat_inputs_type == "t2r":
    process_stats_dir(region_stats_dir, is_region=True)
    process_stats_dir(tract_stats_dir, is_region=False)
else:
    raise ValueError(f"Unknown covbat_inputs_type: {covbat_inputs_type}")
