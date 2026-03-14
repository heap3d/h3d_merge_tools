#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# warn about different names of vertex normal maps or multiple vertex normal maps in one mesh.
# ================================

import modo
import modo.constants as c

from h3d_merge_tools.scripts.safe_merge import get_vmap_normal_stats, stats_processing, initialize_env


def main():
    meshes = modo.Scene().items(itype=c.MESH_TYPE)

    stats = get_vmap_normal_stats(meshes)

    env = initialize_env()

    stats_processing(stats, env, show_ok=True)


if __name__ == '__main__':
    main()
