import nibabel as nib
from nilearn import surface, datasets, plotting
from nilearn.plotting import show
import numpy as np
import os
from os.path import join as ospj
import sys

'''
This script uses nilearn vol_to_surf to map volumetric diffusion MRI parameter maps at different cortical depths
'''

# sub = sys.argv[1]
# group = sys.argv[2]
sub = "sub-RID0505"
group = "penn_controls"

# Define paths to Freesurfer and cortical profiles directories
surfaces_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces/{group}/{sub}"
freesurfer_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer/{group}/{sub}"
qsirecon_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/{group}/{sub}"
cortical_profiles_dir = f"/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/cortical_profiles/{group}/{sub}"
if not os.path.exists(cortical_profiles_dir):
    os.makedirs(cortical_profiles_dir)

# Define paths to pial and white matter surfaces from Freesurfer in native space
pial_lh = ospj(surfaces_dir, f"{sub}.lh.pial.native_acpc.surf.gii")
pial_rh = ospj(surfaces_dir, f"{sub}.rh.pial.native_acpc.surf.gii")
white_lh = ospj(surfaces_dir, f"{sub}.lh.white.native_acpc.surf.gii")
white_rh = ospj(surfaces_dir, f"{sub}.rh.white.native_acpc.surf.gii")

# Define path to example diffusion MRI parameter map
scalar_path = "/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/qsirecon/penn_controls/derivatives/qsirecon-DSIStudio/sub-RID0505/ses-research3Tv03/dwi/sub-RID0505_ses-research3Tv03_space-ACPC_model-tensor_param-md_dwimap.nii.gz"
scalar_img = nib.load(scalar_path)

def vol_to_surf_by_depth(img, depths, surf_pial, surf_white):
    """
    Extract cortical profiles at multiple depths
    
    Parameters:
    -----------
    img : nibabel image
        The volumetric image to sample
    depths : list or array
        List of depth values (0=white matter, 1=pial surface)
    surf_pial : str
        Path to pial surface
    surf_white : str  
        Path to white matter surface
        
    Returns:
    --------
    surf_data : array
        Surface data with shape (n_vertices, n_depths)
    """
    surf_data = surface.vol_to_surf(
                        img, # should be the diffusion MRI parameter map
                        surf_pial, # should be the pial surface
                        kind='depth', 
                        depth=depths,  # Pass the depths list directly
                        inner_mesh=surf_white, # should be the white matter surface
                        )
    return(surf_data)

for depth in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:

    scalar_cortical_profile_left = vol_to_surf_by_depth(scalar_img, [depth], pial_lh, white_lh)
    print(len(scalar_cortical_profile_left))
    print(scalar_cortical_profile_left)