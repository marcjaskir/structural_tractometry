import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from os.path import join as ospj

covbat_label = "region_stats"
space = "mni"

covbat_outputs_dir = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/covbat/outputs/" + covbat_label + "/" + space


rois = pd.read_csv("/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/4S/atlas-4S156Parcels_dseg.tsv", sep="\t")["label"].tolist()
stats = ["mean", "median"]
measures = [f.name for f in os.scandir(covbat_outputs_dir) if f.is_dir()]

for stat in stats:
    for roi in rois:
        for measure in measures:

            print(f"Creating CovBat QC plot for {roi} {stat} {measure}")

            # Read the CSV file
            csv_path = ospj(covbat_outputs_dir, measure, f"{roi}_{stat}_{measure}_covbat.csv")
            df = pd.read_csv(csv_path)

            # Create figure with 2 subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Get y-axis limits from both datasets
            y_min = min(df[f'{measure}_orig'].min(), df[f'{measure}'].min())
            y_max = max(df[f'{measure}_orig'].max(), df[f'{measure}'].max())

            # Plot original values
            sns.violinplot(data=df, x='bat', y=f'{measure}_orig', ax=ax1, alpha=0.3)
            sns.stripplot(data=df, x='bat', y=f'{measure}_orig', ax=ax1, alpha=0.5, size=2)
            ax1.set_title('Original Values')
            ax1.set_xlabel('Batch')
            ax1.set_ylabel('DKI FA')
            ax1.set_ylim(y_min, y_max)

            # Plot harmonized values
            sns.violinplot(data=df, x='bat', y=f'{measure}', ax=ax2, alpha=0.3)
            sns.stripplot(data=df, x='bat', y=f'{measure}', ax=ax2, alpha=0.5, size=2)
            ax2.set_title('Harmonized Values')
            ax2.set_xlabel('Batch')
            ax2.set_ylabel('DKI FA')
            ax2.set_ylim(y_min, y_max)

            plt.tight_layout()

            # Save the figure in the same directory as the CSV file
            output_dir = os.path.dirname(csv_path)
            output_path = ospj(output_dir, f'{roi}_{stat}_{measure}_covbat_plot.png')
            plt.savefig(output_path, dpi=75, bbox_inches='tight')
            plt.close()