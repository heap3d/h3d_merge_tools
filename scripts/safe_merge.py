#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# warn about different names of vertex normal maps in selected meshes when trying to merge them.
# ================================

from dataclasses import dataclass
from typing import Iterable

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import get_user_value


USERVAL_VMAP_NORMAL_PERFECT_NAME = "h3d_mrgt_vmap_normal_perfect_name"
DEFAULT_VMAP_NORMAL_PERFECT_NAME = "normals"


@dataclass
class VMAP_NORMAL_NAMES_STATS:
    different_on_different_meshes: bool
    multiple_on_same_mesh: bool


def main():
    selected_meshes: list[modo.Mesh] = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    if len(selected_meshes) < 2:
        print("Select at least 2 meshes to merge.")
        return

    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_normal_perfect_name:
        vmap_normal_perfect_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    target_mesh = selected_meshes[0]
    merging_meshes = selected_meshes[1:]

    safe_merge_meshes(target_mesh, merging_meshes, vmap_normal_perfect_name)


def safe_merge_meshes(target_mesh: modo.Mesh, merging_meshes: Iterable[modo.Mesh], perfect_vmap_normal_name: str):

    vmap_normal_maps = set()
    for mesh in [target_mesh, *merging_meshes]:
        vmap_normal_maps.update(mesh.geometry.vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL))

    print(vmap_normal_maps)

    merge_meshes(target_mesh, merging_meshes)


def merge_meshes(target_mesh: modo.Mesh, merging_meshes: Iterable[modo.Mesh]):
    modo.Scene().deselect()
    target_mesh.select()
    for mesh in merging_meshes:
        mesh.select()

    lx.eval('layer.mergeMeshes true')


def get_vmap_normal_stats(meshes: Iterable[modo.Mesh]) -> VMAP_NORMAL_NAMES_STATS:
    vmap_normal_names = set()
    multiple_on_same_mesh = False
    for mesh in meshes:
        vmap_normal_maps = mesh.geometry.vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL)
        if len(vmap_normal_maps) > 1:
            multiple_on_same_mesh = True
        for vmap in vmap_normal_maps:
            vmap_normal_names.add(vmap.name)

    different_on_different_meshes = len(vmap_normal_names) > 1

    return VMAP_NORMAL_NAMES_STATS(
        different_on_different_meshes=different_on_different_meshes,
        multiple_on_same_mesh=multiple_on_same_mesh
    )


if __name__ == "__main__":
    main()
