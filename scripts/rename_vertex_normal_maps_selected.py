#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# rename vertex normal maps of selected meshes to specified name.
# Warn if multiple vertex normal maps are found on a mesh.
# ================================

import modo

from h3d_merge_tools.scripts.safe_merge import get_vmap_normal_stats, initialize_env, rename_vmap_normals


def main():
    selected_meshes = modo.Scene().selectedByType('mesh')

    env = initialize_env()
    stats = get_vmap_normal_stats(selected_meshes)

    valid_meshes = set(selected_meshes) - stats.multiple_vmap_normal_meshes
    rename_vmap_normals(valid_meshes, env.vmap_normal_perfect_name)


if __name__ == '__main__':
    main()
