import csv
import os

INPUT_PATH = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/data/metadata/hcpaging/imagingcollection01.txt"
OUTPUT_PATH = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/metadata/demo_hcpaging.csv"

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

results = []
seen_subjects = set()

with open(INPUT_PATH, newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    lines = list(reader)
    # Skip the second line (column descriptions)
    if len(lines) > 0 and lines[0][reader.fieldnames[0]].startswith('Description'):
        lines = lines[1:]
    for row in lines:
        sub = row.get('src_subject_id', '').strip()
        age_months = row.get('interview_age', '').strip()
        sex = row.get('sex', '').strip()
        if not sub or not age_months or not sex:
            continue
        try:
            age_years = round(float(age_months) / 12, 1)
        except ValueError:
            continue
            
        subject_id = f'sub-{sub}'
        if subject_id in seen_subjects:
            continue
            
        seen_subjects.add(subject_id)
        results.append({
            'sub': subject_id,
            'age': age_years,
            'sex': sex
        })

# Sort results by subject ID
results.sort(key=lambda x: x['sub'])

with open(OUTPUT_PATH, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['sub', 'age', 'sex'])
    writer.writeheader()
    writer.writerows(results)