import os
import json
import csv
import glob

# Define paths
base_dir = "/mnt/sauce/littlab/users/mjaskir/penn_neurobridge_epilepsy"
output_file = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/scanner_ids_penn.csv"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Initialize results list
results = []

# Iterate through RID directories
for sub_dir in os.listdir(base_dir):
    sub_path = os.path.join(base_dir, sub_dir)
    
    # Skip if not a directory
    if not os.path.isdir(sub_path):
        continue
        
    # Look for research3T session directory
    research_dirs = glob.glob(os.path.join(sub_path, "ses-research3T*"))
    
    if research_dirs:
        # Get first matching session directory
        session_dir = research_dirs[0]
        
        # Look for T1w json file
        t1_jsons = glob.glob(os.path.join(session_dir, "anat", "*_T1w.json"), recursive=True)
        
        if t1_jsons:
            # Get first matching json file
            json_file = t1_jsons[0]
            
            # Read the json and extract scanner ID
            with open(json_file) as f:
                metadata = json.load(f)
                scanner_id = metadata.get('DeviceSerialNumber')
                
                # If DeviceSerialNumber is missing, check ManufacturerModelName
                if not scanner_id:
                    manufacturers_model_name = metadata.get('ManufacturersModelName')
                    if manufacturers_model_name == 'Prisma_fit':
                        scanner_id = '167024'
                
                if scanner_id:
                    results.append({
                        'sub': sub_dir,
                        'scanner_id': scanner_id
                    })

# Sort results by subject ID
results.sort(key=lambda x: x['sub'])

# Write results to CSV
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['sub', 'scanner_id'])
    writer.writeheader()
    writer.writerows(results)
