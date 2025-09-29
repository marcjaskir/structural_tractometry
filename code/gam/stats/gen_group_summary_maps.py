import os
import nibabel as nib
import pandas as pd
import numpy as np

# --- User Configurable Inputs ---
group_summary_fname_base = "neuromodulation_abs_z_means_gm_asym"  # Change as needed
top_n_rois = 10  # Set to None to plot all ROIs, or an integer for top N

# --- Paths ---
group_summary_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/group_summaries"
gm_atlas_img = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/tpl-MNI152NLin2009cAsym_atlas-4S156Parcels_res-01_dseg.nii.gz"
gm_atlas_metadata = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/atlas-4S156Parcels_dseg.tsv"
wm_mask_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/HCP1065/all_nii_bin"

# --- Load Data ---
group_summary_path = os.path.join(group_summary_dir, f"{group_summary_fname_base}.csv")
group_summary = pd.read_csv(group_summary_path)

def get_roi_col():
    """Return the correct ROI column name, trying both 'roi' and 'base_roi'."""
    possible_cols = ["roi", "base_roi"]
    for col in possible_cols:
        if col in group_summary.columns:
            return col
    raise ValueError(f"Neither 'roi' nor 'base_roi' found in group_summary columns: {group_summary.columns}")

def get_z_col():
    """Return the correct z-score column name based on file type, trying both summary_z and summary_asym."""
    possible_cols = []
    if group_summary_fname_base.endswith("_asym"):
        possible_cols = ["summary_asym", "summary_z"]
    else:
        possible_cols = ["summary_z", "summary_asym"]
    for col in possible_cols:
        if col in group_summary.columns:
            return col
    raise ValueError(f"Neither 'summary_z' nor 'summary_asym' found in group_summary columns: {group_summary.columns}")

roi_col = get_roi_col()
z_col = get_z_col()

def get_ipsi_hemi():
    """Infer ipsilateral hemisphere from the filename base."""
    fname = group_summary_fname_base.lower()
    if fname.startswith("left_"):
        return "left"
    elif fname.startswith("right_"):
        return "right"
    else:
        return "left"  # Default to left if not specified

ipsi_hemi = get_ipsi_hemi()

if group_summary_fname_base.endswith("_wm"):
    # --- White Matter (tract) mode ---
    wm_summary = group_summary[group_summary['tissue'] == 'wm']

    # Sort by absolute value of z_col, descending
    sorted_wm = wm_summary.reindex(wm_summary[z_col].abs().sort_values(ascending=False).index)

    # Select top N or all
    top_n = sorted_wm.head(top_n_rois) if top_n_rois is not None else sorted_wm

    # Now sort these by z_col (ascending), so most abnormal (highest abs(z)) is last
    top_n_sorted = top_n.sort_values(z_col, ascending=True)

    if top_n_sorted.shape[0] == 0:
        raise ValueError(f"No WM ROIs found in summary for {group_summary_fname_base}")

    # Prepare empty image using the first mask
    first_mask_name = top_n_sorted.iloc[0][roi_col]
    first_mask_path = os.path.join(wm_mask_dir, f"{first_mask_name}.nii.gz")
    first_mask_img = nib.load(first_mask_path)
    mask_shape = first_mask_img.shape
    mask_affine = first_mask_img.affine
    mask_header = first_mask_img.header
    zscore_tract_data = np.zeros(mask_shape, dtype=np.float32)

    # Add tracts in order: lowest to highest z_col (so most abnormal gets precedence)
    for _, row in top_n_sorted.iterrows():
        tract_name = row[roi_col]
        zscore = row[z_col]

        mask_path = os.path.join(wm_mask_dir, f"{tract_name}.nii.gz")
        if not os.path.exists(mask_path):
            print(f"Warning: Mask for {tract_name} not found at {mask_path}, skipping.")
            continue
        mask_img = nib.load(mask_path)
        mask_data = mask_img.get_fdata()
        # Only set voxels where mask==1 and zscore_tract_data is still 0 (so later tracts overwrite earlier)
        update_mask = (mask_data > 0) & (zscore_tract_data == 0)
        zscore_tract_data[update_mask] = zscore

    # Save the new tract z-score image
    if top_n_rois is not None:
        zscore_img_fname = os.path.join(group_summary_dir, f"{group_summary_fname_base}_zscore_top{top_n_rois}.nii.gz")
        print(f"Saved top-{top_n_rois} tract z-score atlas to {zscore_img_fname}")
    else:
        zscore_img_fname = os.path.join(group_summary_dir, f"{group_summary_fname_base}_zscore.nii.gz")
        print(f"Saved all tract z-score atlas to {zscore_img_fname}")
    zscore_img = nib.Nifti1Image(zscore_tract_data, mask_affine, mask_header)
    nib.save(zscore_img, zscore_img_fname)

else:
    # --- Gray Matter (parcel) mode ---
    atlas_img = nib.load(gm_atlas_img)
    atlas_data = atlas_img.get_fdata()
    atlas_meta = pd.read_csv(gm_atlas_metadata, sep="\t")

    # Filter for GM rows in group summary
    gm_summary = group_summary[group_summary['tissue'] == 'gm']

    # Sort by absolute value of z_col, descending
    sorted_gm = gm_summary.reindex(gm_summary[z_col].abs().sort_values(ascending=False).index)

    # Select top N or all
    top_n_gm = sorted_gm.head(top_n_rois) if top_n_rois is not None else sorted_gm

    # For asym files, we need to map atlas label to the correct left/right ROI in the summary
    # Build a mapping from left_roi and right_roi to the row, for fast lookup
    left_roi_map = {}
    right_roi_map = {}
    if group_summary_fname_base.endswith("_asym"):
        # Only keep the columns we need for mapping
        for _, row in top_n_gm.iterrows():
            if "left_roi" in row and pd.notnull(row["left_roi"]):
                left_roi_map[row["left_roi"]] = row
            if "right_roi" in row and pd.notnull(row["right_roi"]):
                right_roi_map[row["right_roi"]] = row
    else:
        # Not asym, just map roi_col to row
        roi_map = {row[roi_col]: row for _, row in top_n_gm.iterrows()}

    # Make a copy of the atlas data to modify
    zscore_atlas_data = np.zeros_like(atlas_data)

    # For each ROI in the atlas metadata, set z-score if present, else 0
    for _, meta_row in atlas_meta.iterrows():
        roi_label = meta_row['label']
        roi_index = meta_row['index']
        zscore = 0

        if group_summary_fname_base.endswith("_asym"):
            # For asym files, only update the ipsilateral hemisphere ROI
            if ipsi_hemi == "left":
                row = left_roi_map.get(roi_label, None)
            else:
                row = right_roi_map.get(roi_label, None)
            if row is not None:
                zscore = row[z_col]
        else:
            # Not asym, just use the mapping from roi_label to z
            row = roi_map.get(roi_label, None)
            if row is not None:
                zscore = row[z_col]

        zscore_atlas_data[atlas_data == roi_index] = zscore

    # Save the new atlas image with z-scores
    if top_n_rois is not None:
        zscore_img_fname = os.path.join(group_summary_dir, f"{group_summary_fname_base}_zscore_top{top_n_rois}.nii.gz")
        print(f"Saved top-{top_n_rois} parcel z-score atlas to {zscore_img_fname}")
    else:
        zscore_img_fname = os.path.join(group_summary_dir, f"{group_summary_fname_base}_zscore.nii.gz")
        print(f"Saved all parcel z-score atlas to {zscore_img_fname}")
    zscore_img = nib.Nifti1Image(zscore_atlas_data, atlas_img.affine, atlas_img.header)
    nib.save(zscore_img, zscore_img_fname)
