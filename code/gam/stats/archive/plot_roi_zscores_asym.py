import pandas as pd
import os
from os.path import join as ospj
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def plot_roi_zscores_asym(
    roi_dict, stats, measures, method="mean", z_type="abs", n_plot=10, subs=None, networks=False, title=None,
    gm_metadata_df=None, wm_metadata_df=None
):
    """
    Plot the top n_plot ROIs (or networks if networks=True) ranked by summarized z-score asymmetries across measures and stats.
    For each subject, computes ipsilateral - contralateral z-scores within each ROI, then summarizes asymmetries at the ROI level.
    If 'title' is specified, it will be used as the first line of the plot title.
    
    Note: This function requires clinical data to determine ipsilateral vs contralateral for each subject.
    """
    if method not in ["sum", "mean"]:
        raise ValueError(f"Unknown method: {method}. Only 'sum' and 'mean' are allowed.")
    if z_type not in ["raw", "abs"]:
        raise ValueError(f"Unknown z_type: {z_type}. Only 'raw' and 'abs' are allowed.")

    # Nested dict: subj -> tissue_type -> roi -> stat -> measure -> z
    subj_zscores = {}

    # Determine which subjects to use
    all_subs = set()
    if subs is not None:
        all_subs = set(subs)
    else:
        # If subs is None, collect all subjects from all files
        for tissue_type, info in roi_dict.items():
            gam_outputs_dir = info["dir"]
            rois = info["rois"]
            for roi in rois:
                for stat in stats:
                    for measure in measures:
                        gam_outputs_path = ospj(gam_outputs_dir, roi, f"{roi}_{stat}_{measure}_gam.csv")
                        if not os.path.exists(gam_outputs_path):
                            continue
                        try:
                            gam_outputs_df = pd.read_csv(gam_outputs_path)
                            gam_outputs_df = gam_outputs_df[gam_outputs_df["group"] == "penn_epilepsy"]
                            all_subs.update(gam_outputs_df["sub"].unique())
                        except Exception:
                            continue

    all_subs = sorted(list(all_subs))
    for sub in all_subs:
        subj_zscores[sub] = {}

    # For each subject, for each tissue_type, roi, stat, measure, store z-score
    for tissue_type, info in roi_dict.items():
        gam_outputs_dir = info["dir"]
        rois = info["rois"]
        print(f"Collecting z-scores for {tissue_type}")
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
                            # Initialize nested dicts as needed
                            if tissue_type not in subj_zscores[sub]:
                                subj_zscores[sub][tissue_type] = {}
                            if roi not in subj_zscores[sub][tissue_type]:
                                subj_zscores[sub][tissue_type][roi] = {}
                            if stat not in subj_zscores[sub][tissue_type][roi]:
                                subj_zscores[sub][tissue_type][roi][stat] = {}
                            subj_zscores[sub][tissue_type][roi][stat][measure] = z_val
                    except Exception:
                        continue

    # Now compute asymmetries for each ROI
    roi_asym_scores = []
    for tissue_type, info in roi_dict.items():
        rois = info["rois"]
        print(f"Computing asymmetries for {tissue_type}")
        for roi in tqdm(rois):
            # Get the base ROI name (without hemisphere suffix/prefix)
            base_roi = get_base_roi_name(roi, tissue_type)
            if base_roi is None:
                continue  # Skip if we can't determine base ROI
                
            # Find the contralateral ROI
            contra_roi = get_contralateral_roi(roi, tissue_type)
            if contra_roi is None:
                continue  # Skip if we can't find contralateral ROI
                
            # Check if contralateral ROI exists in our data
            if tissue_type not in roi_dict or contra_roi not in roi_dict[tissue_type]["rois"]:
                continue
                
            all_asyms = []
            for sub in all_subs:
                # Compute asymmetry for each stat-measure pair
                for stat in stats:
                    for measure in measures:
                        # Find matching z-scores
                        ipsi_z = None
                        contra_z = None
                        
                        # Get ipsilateral z-score
                        if (sub in subj_zscores and 
                            tissue_type in subj_zscores[sub] and 
                            roi in subj_zscores[sub][tissue_type] and
                            stat in subj_zscores[sub][tissue_type][roi] and
                            measure in subj_zscores[sub][tissue_type][roi][stat]):
                            ipsi_z = subj_zscores[sub][tissue_type][roi][stat][measure]
                        
                        # Get contralateral z-score
                        if (sub in subj_zscores and 
                            tissue_type in subj_zscores[sub] and 
                            contra_roi in subj_zscores[sub][tissue_type] and
                            stat in subj_zscores[sub][tissue_type][contra_roi] and
                            measure in subj_zscores[sub][tissue_type][contra_roi][stat]):
                            contra_z = subj_zscores[sub][tissue_type][contra_roi][stat][measure]
                        
                        # Compute asymmetry if both values exist
                        if ipsi_z is not None and contra_z is not None:
                            asym = ipsi_z - contra_z
                            if z_type == "abs":
                                asym = np.abs(asym)
                            all_asyms.append(asym)
            
            if all_asyms:
                all_asyms = np.array(all_asyms)
                summary_asym = np.sum(all_asyms) if method == "sum" else np.mean(all_asyms)
                roi_asym_scores.append({
                    "tissue": tissue_type,
                    "roi": roi,
                    "base_roi": base_roi,
                    "summary_asym": summary_asym,
                    "n_asyms": len(all_asyms)
                })

    roi_asym_scores_df = pd.DataFrame(roi_asym_scores)
    if roi_asym_scores_df.empty:
        print("No asymmetry scores found for the given ROIs and measures.")
        return roi_asym_scores_df

    if networks:
        roi_asym_scores_df["network"] = roi_asym_scores_df.apply(
            lambda row: get_network_label(row, gm_metadata_df, wm_metadata_df), axis=1
        )
        net_scores = (
            roi_asym_scores_df.groupby(["tissue", "network"])
            .agg({"summary_asym": "mean", "n_asyms": "sum"})
            .reset_index()
            .sort_values("summary_asym", ascending=False)
        )
        top_df = net_scores.head(n_plot)
        color_map = {"wm": "#1f77b4", "gm": "#ff7f0e"}
        colors = [color_map.get(t, "gray") for t in top_df["tissue"]]
        plt.figure(figsize=(12, 6))
        plt.bar(top_df["network"], top_df["summary_asym"], color=colors)
        plt.xlabel("Network")
        plt.ylabel(f"Mean summarized asymmetry ({method}, {z_type})")
        # Compose title
        plot_title = f"Top {n_plot} Networks by mean summarized asymmetry ({method}, {z_type})"
        if title is not None:
            plot_title = f"{title}\n{plot_title}"
        plt.title(plot_title)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
        return top_df

    # Not networks: plot individual ROIs
    roi_asym_scores_df = roi_asym_scores_df.sort_values("summary_asym", ascending=False)
    top_rois = roi_asym_scores_df.head(n_plot).copy()

    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        range(len(top_rois)),
        top_rois["summary_asym"],
        color="blue",
        edgecolor="none"
    )

    # Add outline to GM bars
    for bar, tissue in zip(bars, top_rois["tissue"]):
        if tissue == "gm":
            bar.set_edgecolor("black")
            bar.set_linewidth(3)
        else:
            bar.set_edgecolor("none")

    # Set x-tick labels using base ROI names
    display_labels = [
        get_display_label(row, ipsi=None, gm_metadata_df=gm_metadata_df, wm_metadata_df=wm_metadata_df) 
        for _, row in top_rois.iterrows()
    ]
    plt.xlabel("ROI")
    plt.ylabel(f"{method.capitalize()} {z_type} asymmetry (ipsi - contra)")
    # Compose title
    plot_title = "ROIs ranked by microstructural asymmetry"
    if title is not None:
        plot_title = f"{title}\n{plot_title}"
    plt.title(plot_title)
    plt.xticks(range(len(top_rois)), display_labels, rotation=45, ha="right")

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="blue", lw=6, label="ROI"),
        Line2D([0], [0], color="black", lw=2, label="GM region")
    ]
    plt.legend(handles=legend_elements, loc="best")

    plt.tight_layout()
    plt.show()
    return roi_asym_scores_df


def get_base_roi_name(roi, tissue_type):
    """
    Get the base ROI name without hemisphere information.
    """
    if tissue_type == "gm":
        # Remove "LH-" or "RH-" prefix
        if roi.startswith("LH-") or roi.startswith("RH-") or roi.startswith("LH_") or roi.startswith("RH_"):
            return roi[3:]
        return roi
    elif tissue_type == "wm":
        # Remove "_L" or "_R" suffix
        if roi.endswith("_L") or roi.endswith("_R"):
            return roi[:-2]
        return roi
    return roi


def get_contralateral_roi(roi, tissue_type):
    """
    Get the contralateral ROI name.
    """
    if tissue_type == "gm":
        # Swap LH- and RH- prefixes
        if roi.startswith("LH-") or roi.startswith("LH_"):
            return roi.replace("LH-", "RH-").replace("LH_", "RH_")
        elif roi.startswith("RH-") or roi.startswith("RH_"):
            return roi.replace("RH-", "LH-").replace("RH_", "LH_")
        return None  # Can't determine contralateral for bilateral ROIs
    elif tissue_type == "wm":
        # Swap _L and _R suffixes
        if roi.endswith("_L"):
            return roi[:-2] + "_R"
        elif roi.endswith("_R"):
            return roi[:-2] + "_L"
        return None  # Can't determine contralateral for bilateral ROIs
    return None


def get_display_label(row, ipsi=None, gm_metadata_df=None, wm_metadata_df=None):
    """
    Return display label for ROI, removing hemispheric prefixes/suffixes only if ipsi is specified.
    For WM, use 'name' from metadata if available.
    """
    label = row["roi"]
    if row["tissue"] == "gm":
        # Remove "LH-" or "RH-" prefix if ipsi is specified
        if ipsi is not None and (label.startswith("LH-") or label.startswith("RH-") or label.startswith("LH_") or label.startswith("RH_")):
            label = label[3:]
        return label
    elif row["tissue"] == "wm":
        # Use 'name' from metadata if available
        if wm_metadata_df is not None and "label" in wm_metadata_df.columns and "name" in wm_metadata_df.columns:
            match = wm_metadata_df[wm_metadata_df["label"] == label]
            if not match.empty:
                name = match["name"].values[0]
                # Remove "_L" or "_R" suffix if ipsi is specified
                if ipsi is not None and (name.endswith("_L") or name.endswith("_R")):
                    name = name[:-2]
                return name
        # Fallback: remove "_L" or "_R" from roi label if ipsi is specified
        if ipsi is not None and (label.endswith("_L") or label.endswith("_R")):
            label = label[:-2]
        return label
    return label


def get_network_label(row, gm_metadata_df=None, wm_metadata_df=None):
    """Return network label for a given ROI row using metadata."""
    if row["tissue"] == "gm" and gm_metadata_df is not None:
        match = gm_metadata_df[gm_metadata_df["label"] == row["roi"]]
        if not match.empty:
            return match["network_label"].values[0]
    elif row["tissue"] == "wm" and wm_metadata_df is not None:
        match = wm_metadata_df[wm_metadata_df["label"] == row["roi"]]
        if not match.empty:
            return match["type"].values[0]
    return "Unknown" 