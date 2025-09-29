import nibabel as nib
import numpy as np
import os
from os.path import join as ospj

def save_surf_without_medial_wall(surface_path, label_path, output_path):
    """
    Loads a GIFTI surface file, removes the medial wall vertices,
    and saves the new surface file.

    Parameters:
    - surface_path (str): The path to the input .surf.gii file.
    - label_path (str): The path to the FreeSurfer label file defining the cortex.
    - output_path (str): The path where the new .surf.gii file will be saved.
    """
    # 1. Load the surface geometry and the cortex label file
    surf = nib.load(surface_path)
    cortex_label = nib.freesurfer.read_label(label_path)

    # 2. Get the original vertices and triangles
    coords = surf.darrays[0].data
    tris = surf.darrays[1].data

    # 3. Create a mask for cortical vertices
    # FreeSurfer label files contain the vertex indices for the cortex.
    all_vertices = np.arange(len(coords))
    cortex_mask = np.zeros(len(coords), dtype=bool)
    cortex_mask[cortex_label] = True

    # 4. Remove vertices that are not part of the cortex
    # This keeps only the vertices that are part of the cortex mask.
    cortex_coords = coords[cortex_mask]

    # 5. Filter the triangles
    # Remove any triangle that contains a vertex from the medial wall.
    # To do this, we need to create a mapping from old vertex indices to new ones.
    old_to_new_indices = -np.ones(len(coords), dtype=int)
    old_to_new_indices[cortex_mask] = np.arange(len(cortex_coords))

    # Keep triangles where all three vertices are in the cortex.
    valid_tris_mask = cortex_mask[tris].all(axis=1)
    cortex_tris = tris[valid_tris_mask]

    # 6. Re-index the remaining triangles to use the new vertex indices
    reindexed_cortex_tris = old_to_new_indices[cortex_tris]

    # 7. Create new GIFTI data arrays
    # Create the data array for the new, filtered vertices.
    new_coords_darray = nib.gifti.GiftiDataArray(
        data=cortex_coords.astype(np.float32),
        intent='NIFTI_INTENT_POINTSET'
    )
    # Create the data array for the new, re-indexed triangles.
    new_tris_darray = nib.gifti.GiftiDataArray(
        data=reindexed_cortex_tris.astype(np.int32),
        intent='NIFTI_INTENT_TRIANGLE'
    )

    # 8. Create a new GIFTI image and save it
    new_surf = nib.gifti.GiftiImage(darrays=[new_coords_darray, new_tris_darray])
    nib.save(new_surf, output_path)

# --- Example Usage ---
# Replace with your actual file paths
group = 'penn_controls'

surfaces_dir = '/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/surfaces'
fs_dir = '/mnt/sauce/littlab/users/mjaskir/structural_tractometry/derivatives/freesurfer'

for sub in sorted(os.listdir(ospj(surfaces_dir, group))):
    # Check that it begins with sub-
    if sub.startswith('sub-'):
        
        lh_output_file = ospj(surfaces_dir, group, sub, f'{sub}.lh.white.native_acpc.no_medial_wall.surf.gii')
        rh_output_file = ospj(surfaces_dir, group, sub, f'{sub}.rh.white.native_acpc.no_medial_wall.surf.gii')

        # Skip if both files already exist
        if os.path.exists(lh_output_file) and os.path.exists(rh_output_file):
            continue

        lh_surface_file = ospj(surfaces_dir, group, sub, f'{sub}.lh.white.native_acpc.surf.gii')
        rh_surface_file = ospj(surfaces_dir, group, sub, f'{sub}.rh.white.native_acpc.surf.gii')
        lh_cortex_label_file = ospj(fs_dir, group, sub, 'label', f'lh.cortex.label')
        rh_cortex_label_file = ospj(fs_dir, group, sub, 'label', f'rh.cortex.label')

        # Skip any surface or label file that does not exist
        if not os.path.exists(lh_surface_file) or not os.path.exists(rh_surface_file) or not os.path.exists(lh_cortex_label_file) or not os.path.exists(rh_cortex_label_file):
            continue

        print(f'Removing medial wall for {sub}')

        save_surf_without_medial_wall(lh_surface_file, lh_cortex_label_file, lh_output_file)
        save_surf_without_medial_wall(rh_surface_file, rh_cortex_label_file, rh_output_file)