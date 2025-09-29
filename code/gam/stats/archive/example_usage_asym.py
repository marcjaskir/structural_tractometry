"""
Example usage of plot_roi_zscores_asym function

This script demonstrates how to use the new plot_roi_zscores_asym function
to compute and visualize microstructural asymmetries in epilepsy patients.
"""

import pandas as pd
import os
from os.path import join as ospj
from plot_roi_zscores_asym import plot_roi_zscores_asym

# Example setup (you'll need to adapt this to your actual data paths)
def example_usage():
    """
    Example usage of the plot_roi_zscores_asym function.
    """
    
    # Load metadata (adapt paths to your actual data)
    wm_metadata_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/HCP1065/HCP1065_tract_metadata.csv"
    gm_metadata_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/atlas-4S156Parcels_dseg.tsv"
    
    wm_metadata_df = pd.read_csv(wm_metadata_file)
    gm_metadata_df = pd.read_csv(gm_metadata_file, sep="\t")
    
    # Add hemisphere column to GM metadata
    gm_metadata_df["hemi"] = gm_metadata_df["label"].apply(
        lambda x: "left" if x.startswith("LH") else "right" if x.startswith("RH") else "bilateral"
    )
    
    # Define ROI dictionary (adapt to your actual data)
    roi_dict = {
        "wm": {
            "dir": "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/tracts/HCP1065",
            "rois": ["F_L", "F_R", "CST_L", "CST_R"]  # Example ROIs
        },
        "gm": {
            "dir": "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/regions/4S156",
            "rois": ["LH_Hippocampus", "RH_Hippocampus", "LH_Amygdala", "RH_Amygdala"]  # Example ROIs
        }
    }
    
    # Define stats and measures
    stats = ["mean"]
    measures = ["dti_md", "dti_fa"]  # Example measures
    
    # Example subject lists (adapt to your actual data)
    left_temporal_subs = ["sub-001", "sub-002", "sub-003"]  # Example subjects
    right_temporal_subs = ["sub-004", "sub-005", "sub-006"]  # Example subjects
    
    # Example 1: Analyze asymmetries for left temporal seizures
    print("Analyzing asymmetries for left temporal seizures...")
    left_asymmetries = plot_roi_zscores_asym(
        roi_dict=roi_dict,
        stats=stats,
        measures=measures,
        method="mean",
        z_type="abs",
        n_plot=10,
        subs=left_temporal_subs,
        networks=False,
        title="Left temporal seizures - microstructural asymmetries",
        gm_metadata_df=gm_metadata_df,
        wm_metadata_df=wm_metadata_df
    )
    
    # Save results
    output_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/gam/outputs/group_summaries"
    left_asymmetries.to_csv(ospj(output_dir, "left_temporal_seizures_asymmetries.csv"), index=False)
    
    # Example 2: Analyze asymmetries for right temporal seizures
    print("Analyzing asymmetries for right temporal seizures...")
    right_asymmetries = plot_roi_zscores_asym(
        roi_dict=roi_dict,
        stats=stats,
        measures=measures,
        method="mean",
        z_type="abs",
        n_plot=10,
        subs=right_temporal_subs,
        networks=False,
        title="Right temporal seizures - microstructural asymmetries",
        gm_metadata_df=gm_metadata_df,
        wm_metadata_df=wm_metadata_df
    )
    
    # Save results
    right_asymmetries.to_csv(ospj(output_dir, "right_temporal_seizures_asymmetries.csv"), index=False)
    
    # Example 3: Network-level analysis
    print("Analyzing network-level asymmetries...")
    network_asymmetries = plot_roi_zscores_asym(
        roi_dict=roi_dict,
        stats=stats,
        measures=measures,
        method="mean",
        z_type="abs",
        n_plot=10,
        subs=left_temporal_subs + right_temporal_subs,
        networks=True,
        title="Network-level microstructural asymmetries",
        gm_metadata_df=gm_metadata_df,
        wm_metadata_df=wm_metadata_df
    )
    
    # Save network results
    network_asymmetries.to_csv(ospj(output_dir, "network_asymmetries.csv"), index=False)
    
    print("Analysis complete! Results saved to:", output_dir)


if __name__ == "__main__":
    example_usage() 