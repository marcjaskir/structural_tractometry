import os
import json
import sys
from os.path import join as ospj
from smriprep.interfaces.surf import normalize_surfs

########################################
# Read in subject ID as argument
########################################
sub = sys.argv[1]
group = sys.argv[2]

fs_dir = ospj('/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer', group, sub)
xfm_dir = ospj('/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces', group, sub)
if not os.path.exists(xfm_dir):
    os.makedirs(xfm_dir)

########################################
# Check for required files
########################################

# Check for pial surface files
pial_files = [ospj(xfm_dir, f) for f in os.listdir(xfm_dir) if f.endswith('pial.freesurfer.surf.gii')]
if len(pial_files) != 2:
    print('Missing pial surface files for %s' % sub)
    exit(1)

# Check for white surface files
white_files = [ospj(xfm_dir, f) for f in os.listdir(xfm_dir) if f.endswith('white.freesurfer.surf.gii')]
if len(white_files) != 2:
    print('Missing white surface files for %s' % sub)
    exit(1)

# Check for .lta transformation file
lta_files = [ospj(xfm_dir, f) for f in os.listdir(xfm_dir) if f.endswith('.lta')]
if len(lta_files) != 1:
    print('Missing .lta transformation file for %s' % sub)
    exit(1)

########################################
# Apply Freesurfer to native AC-PC volume transformation to surfaces
########################################

print('Transforming pial surfaces...')

# Apply transformation to pial surfaces
for pial_file in pial_files:

    # Get hemisphere
    hemi = pial_file.split('/')[-1].split('.')[1]

    # Apply transformation
    converted_surf = normalize_surfs(pial_file, lta_files[0], newpath=xfm_dir)

    # Move the converted surface to the xfm_dir
    os.rename(converted_surf, ospj(xfm_dir, f"{sub}.{hemi}.pial.native_acpc.surf.gii"))

print('Transforming white surfaces...')

# Apply transformation to white surfaces
for white_file in white_files:

    # Get hemisphere
    hemi = white_file.split('/')[-1].split('.')[1]

    # Apply transformation
    converted_surf = normalize_surfs(white_file, lta_files[0], newpath=xfm_dir)

    # Move the converted surface to the xfm_dir
    os.rename(converted_surf, ospj(xfm_dir, f"{sub}.{hemi}.white.native_acpc.surf.gii"))

# Clean up unnecessary files
os.remove(ospj(xfm_dir, f"{sub}.freesurfer.nu.nii.gz"))
os.remove(ospj(xfm_dir, f"{sub}.native_acpc.nu.nii.gz"))
os.remove(ospj(xfm_dir, f"{sub}.native_acpc.desc-preproc_T1w.nii.gz"))