import pandas as pd
import os
from os.path import join as ospj
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import glob
import json
from tqdm import tqdm
from scipy.cluster.hierarchy import linkage, leaves_list
import pickle

# Define outputs directory
outputs_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/stats"

# Make Georgia the font for all plots
plt.rcParams['font.family'] = 'Georgia'

# Specify WM and GM atlases
wm_atlas = "HCP1065"
gm_atlas = "4S156"

# Define directory to GAM outputs
gam_outputs_wm_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/tracts/{wm_atlas}"
gam_outputs_gm_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/regions/{gm_atlas}"

# Define directory to save z-score summaries
gam_outputs_group_summaries_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/"
if not os.path.exists(gam_outputs_group_summaries_dir):
    os.makedirs(gam_outputs_group_summaries_dir)

# Measures files
measures_json_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/scalar_labels_to_filenames.json"
colors_json_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/scalar_labels_to_colors.json"
human_labels_json_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/scalar_labels_to_human.json"

# Load clinical data
clinical_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/clinical_penn_epilepsy_qsirecon.csv"
clinical_df = pd.read_csv(clinical_file)

# Load wm metadata (Fields: label, name, hemi, type)
wm_metadata_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/HCP1065/HCP1065_tract_metadata.csv"
wm_metadata_df = pd.read_csv(wm_metadata_file)

# Load gm metadata (Fields: index, label, network_label, network_label_17network) # Reminder: subcortical, thalamic, and cerebellar regions do not have network assignments
gm_metadata_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/atlas-4S156Parcels_dseg.tsv"
gm_metadata_df = pd.read_csv(gm_metadata_file, sep="\t")

# Add a hemi column
gm_metadata_df["hemi"] = gm_metadata_df["label"].apply(lambda x: "left" if x.startswith("LH") else "right" if x.startswith("RH") else "bilateral")

# Remove cranial nerve and bilateral tracts
wm_metadata_df = wm_metadata_df[~wm_metadata_df["label"].str.startswith("CN")]
wm_metadata_df = wm_metadata_df[wm_metadata_df["hemi"] != "bilateral"]

wm_rois = wm_metadata_df["label"].tolist()
gm_rois = gm_metadata_df["label"].tolist()

# Create a dictionary with keys as group names and values as lists of 'sub' values
sub_groups = {}

# Seizure lateralization
lat_options = ["left", "right", "bilateral", "left > right", "right > left", "generalized", "inconclusive"]
for lat in lat_options:
    sub_groups[f"seizure_lateralization_{lat}"] = clinical_df.loc[clinical_df["seizure_lateralization"] == lat, "sub"].tolist()

# Seizure localization
loc_options = ["frontal", "temporal", "parietal", "occipital", "generalized", "central", "multifocal", "nonlocalizable", "insular"]
for loc in loc_options:
    sub_groups[f"seizure_localization_{loc}"] = clinical_df.loc[clinical_df["seizure_localization"] == loc, "sub"].tolist()

# Seizure lateralization and localization combinations
combos = [
    ("left_temporal", ("temporal", "left")),
    ("right_temporal", ("temporal", "right"))
]
for label, (loc, lat) in combos:
    sub_groups[label] = clinical_df.loc[
        (clinical_df["seizure_localization"] == loc) & (clinical_df["seizure_lateralization"] == lat),
        "sub"
    ].tolist()

# Combine both to temporal
sub_groups["temporal"] = sub_groups["left_temporal"] + sub_groups["right_temporal"]

def get_input_specs(input_data_type="all"):
    """
    Returns roi_dict, stats, and measures based on the input_data_type.
    """
    stats = ["mean"]
    measures_all = list(json.load(open(measures_json_path)).keys())
    wm_test_rois = ["F_L", "F_R", "UF_L", "UF_R", "C_PH_L", "C_PH_R", "ILF_L", "ILF_R"]
    gm_test_rois = ["LH_Hippocampus", "RH_Hippocampus", "LH_Amygdala", "RH_Amygdala"]

    if input_data_type == "all":
        roi_dict = {
            "wm": {"dir": gam_outputs_wm_dir, "rois": wm_rois},
            "gm": {"dir": gam_outputs_gm_dir, "rois": gm_rois}
        }
        measures = measures_all
    elif input_data_type == "gm":
        roi_dict = {"gm": {"dir": gam_outputs_gm_dir, "rois": gm_rois}}
        measures = measures_all
    elif input_data_type == "wm":
        roi_dict = {"wm": {"dir": gam_outputs_wm_dir, "rois": wm_rois}}
        measures = measures_all
    elif input_data_type == "test":
        roi_dict = {
            "wm": {"dir": gam_outputs_wm_dir, "rois": wm_test_rois},
            "gm": {"dir": gam_outputs_gm_dir, "rois": gm_test_rois}
        }
        measures = ["dti_md"]
    elif input_data_type == "test_gm":
        roi_dict = {"gm": {"dir": gam_outputs_gm_dir, "rois": gm_test_rois}}
        measures = ["dti_md"]
    elif input_data_type == "test_wm":
        roi_dict = {"wm": {"dir": gam_outputs_wm_dir, "rois": wm_test_rois}}
        measures = ["dti_md"]
    else:
        raise ValueError(f"Unknown input_data_type: {input_data_type}")
    return roi_dict, stats, measures

def get_z_dict(
    roi_dict, stats, measures, sub_groups, method="mean", z_type="abs"
):
    """
    Returns a nested dictionary:
    {lateralization: {sub: {measure: {roi_base: {"ipsi": z, "contra": z}}}}}
    where z is the summary z-score (mean or sum) for that measure and roi.
    No asymmetries are computed.
    """
    import warnings

    if method not in ["sum", "mean"]:
        raise ValueError(f"Unknown method: {method}. Only 'sum' and 'mean' are allowed.")
    if z_type not in ["raw", "abs"]:
        raise ValueError(f"Unknown z_type: {z_type}. Only 'raw' and 'abs' are allowed.")

    # Build subject lists by lateralization
    left_subs = set(sub_groups.get("left_temporal", []))
    right_subs = set(sub_groups.get("right_temporal", []))
    all_subs = sorted(list(left_subs | right_subs))

    # Build a mapping of all bilateral ROI bases
    rois_gm = roi_dict['gm']['rois']
    rois_wm = roi_dict['wm']['rois']
    rois = rois_wm + rois_gm
    roi_bases = [roi.replace("LH_", "").replace("LH-", "").replace("RH_", "").replace("RH-", "").replace("_L", "").replace("_R", "") for roi in rois]
    roi_bases = list(set(roi_bases))

    # Preload all z-scores: subj -> tissue_type -> roi -> stat -> measure -> z
    subj_measures = {sub: {} for sub in all_subs}
    subj_zscores = {sub: {} for sub in all_subs}
    for tissue_type, info in roi_dict.items():
        gam_outputs_dir = info["dir"]
        rois = info["rois"]
        print(f"Summarizing measures for {tissue_type}")
        for roi in tqdm(rois):
            for stat in stats:
                for measure in measures:
                    gam_outputs_path = ospj(gam_outputs_dir, roi, f"{roi}_{stat}_{measure}_gam.csv")
                    if not os.path.exists(gam_outputs_path):
                        continue
                    try:
                        gam_outputs_df = pd.read_csv(gam_outputs_path)
                        gam_outputs_df = gam_outputs_df[gam_outputs_df["group"] == "penn_epilepsy"]
                        gam_outputs_df = gam_outputs_df[gam_outputs_df["sub"].isin(all_subs)]
                        for _, row in gam_outputs_df.iterrows():
                            sub = row["sub"]
                            if "z" not in gam_outputs_df.columns:
                                continue
                            z_val = row["z"]
                            if z_type == "abs":
                                z_val = np.abs(z_val)
                            subj_zscores[sub].setdefault(tissue_type, {}).setdefault(roi, {}).setdefault(measure, {})[stat] = z_val
                    except Exception:
                        continue

    # Build result dict: {lateralization: {sub: {measure: {roi_base: {"ipsi": z, "contra": z}}}}}
    result_dict = {"left": {}, "right": {}}

    for sub in all_subs:
        if sub in left_subs:
            lat = "left"
        elif sub in right_subs:
            lat = "right"
        else:
            continue  # Only process left/right temporal

        if sub not in result_dict[lat]:
            result_dict[lat][sub] = {}
        for measure in measures:
            if measure not in result_dict[lat][sub]:
                result_dict[lat][sub][measure] = {}
            for roi_base in roi_bases:
                # Identify bilateral ROIs for this base
                bilateral_rois = None
                if f"{roi_base}_L" in rois_wm and f"{roi_base}_R" in rois_wm:
                    bilateral_rois = {"left": f"{roi_base}_L", "right": f"{roi_base}_R"}
                    tissue_type = "wm"
                elif f"LH_{roi_base}" in rois_gm and f"RH_{roi_base}" in rois_gm:
                    bilateral_rois = {"left": f"LH_{roi_base}", "right": f"RH_{roi_base}"}
                    tissue_type = "gm"
                elif f"LH-{roi_base}" in rois_gm and f"RH-{roi_base}" in rois_gm:
                    bilateral_rois = {"left": f"LH-{roi_base}", "right": f"RH-{roi_base}"}
                    tissue_type = "gm"
                else:
                    continue  # Not a bilateral ROI

                # For each, summarize across stats (mean or sum) for this measure only
                z_l_stats = []
                z_r_stats = []
                for stat in stats:
                    z_l_val = subj_zscores.get(sub, {}).get(tissue_type, {}).get(bilateral_rois["left"], {}).get(measure, {}).get(stat, np.nan)
                    z_r_val = subj_zscores.get(sub, {}).get(tissue_type, {}).get(bilateral_rois["right"], {}).get(measure, {}).get(stat, np.nan)
                    if not np.isnan(z_l_val):
                        z_l_stats.append(z_l_val)
                    if not np.isnan(z_r_val):
                        z_r_stats.append(z_r_val)
                z_l = np.sum(z_l_stats) if (z_l_stats and method == "sum") else (np.mean(z_l_stats) if z_l_stats else None)
                z_r = np.sum(z_r_stats) if (z_r_stats and method == "sum") else (np.mean(z_r_stats) if z_r_stats else None)
                if z_l is None or z_r is None or np.isnan(z_l) or np.isnan(z_r):
                    continue

                # Determine ipsi/contra based on subject's lateralization
                if lat == "left":
                    ipsi_z = z_l
                    contra_z = z_r
                elif lat == "right":
                    ipsi_z = z_r
                    contra_z = z_l
                else:
                    continue

                result_dict[lat][sub][measure][roi_base] = {
                    "ipsi": ipsi_z,
                    "contra": contra_z
                }

    return result_dict

roi_dict, stats, measures = get_input_specs(input_data_type="all")
z_dict = get_z_dict(
    roi_dict, stats, measures,
    sub_groups=sub_groups,
    method="mean",
    z_type="abs"
)

# Save dict as pickle to /mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/stats
with open(ospj(outputs_dir, "temporal_zscores.pkl"), "wb") as f:
    pickle.dump(z_dict, f)
