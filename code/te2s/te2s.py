import pandas as pd
import json

# Relevant tract_metadatacolumns: label, end1, end2, end1_loc, end2_loc
tract_metadata = pd.read_csv('/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/atlases/HCP1065/HCP1065_tract_metadata.csv')
bundleseg_config = json.load(open('/mnt/sauce/littlab/users/mjaskir/structural_tractometry/code/bundleseg/config/config_HCP1065_association_projection.json'))

# Load tract labels from bundleseg config
tract_labels = list(bundleseg_config.keys())
tract_labels = [tract_label.replace('.trk', '') for tract_label in tract_labels]

for tract_label in tract_labels:

    # Get row from tract_metadata with label
    row = tract_metadata[tract_metadata['label'] == tract_label]

    # Get end1 and end2
    end1 = row['end1'].values[0]
    end2 = row['end2'].values[0]

    # Get end1_loc and end2_loc
    end1_loc = row['end1_loc'].values[0]
    end2_loc = row['end2_loc'].values[0]

    if end1_loc == 'cortex':

        # TODO: At this point, we'll want to load in the corresponding along-tract segments from pyAFQ