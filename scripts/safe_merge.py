#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# warn about different names of vertex normal maps in selected meshes when trying to merge them.
# ================================

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import get_user_value


USERVAL_VMAP_NORMAL_PERFECT_NAME = "h3d_mrgt_vmap_normal_perfect_name"


def main():
    selected_meshes: list[modo.Mesh] = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    if len(selected_meshes) < 2:
        lx.out("Select at least 2 meshes to merge.")
        return

    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)

    target_mesh = selected_meshes[0]
    meshes = selected_meshes[1:]

    safe_merge_meshes(target_mesh, meshes)


def safe_merge_meshes(target_mesh: modo.Mesh, meshes: list[modo.Mesh]):

    vmap_normal_maps = set()
    for mesh in [target_mesh, *meshes]:
        vmap_normal_maps.update(mesh.geometry.vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL))

    print(vmap_normal_maps)

    merge_meshes(target_mesh, meshes)


def merge_meshes(target_mesh: modo.Mesh, meshes: list[modo.Mesh]):
    modo.Scene().deselect()
    target_mesh.select()
    for mesh in meshes:
        mesh.select()

    lx.eval('layer.mergeMeshes true')


if __name__ == "__main__":
    main()
