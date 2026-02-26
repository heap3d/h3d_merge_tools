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

from h3d_utilites.scripts.h3d_utils import get_user_value, parent_items_to, get_parent_index


USERVAL_VMAP_NORMAL_PERFECT_NAME = "h3d_mrgt_vmap_normal_perfect_name"
DEFAULT_VMAP_NORMAL_PERFECT_NAME = "normals"


@dataclass
class VMAP_NORMAL_NAMES_STATS:
    different_on_different_meshes: bool
    multiple_on_same_mesh: bool


def main():
    selected_meshes: list[modo.Item] = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    selected_instances: list[modo.Item] = modo.Scene().selectedByType(itype=c.MESHINST_TYPE)
    affected_instances = list(set(get_instances_of(selected_meshes)) - set(selected_instances))

    if len(selected_meshes) < 2:
        print("Select at least 2 meshes to merge.")
        return

    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_normal_perfect_name:
        vmap_normal_perfect_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    if affected_instances:
        mesh_instance = affected_instances[0]
        mesh = get_instance_source(mesh_instance)
        swap_items(mesh, mesh_instance)

        selected_meshes.remove(mesh)

    converted_meshes = instances_to_meshes(selected_instances)

    target_mesh = selected_meshes[0]
    merging_meshes = selected_meshes[1:] + converted_meshes

    safe_merge_meshes(target_mesh, merging_meshes, vmap_normal_perfect_name)


def safe_merge_meshes(target_mesh: modo.Item, merging_meshes: Iterable[modo.Item], perfect_vmap_normal_name: str):
    if target_mesh.type != 'mesh':
        raise ValueError(f"Target mesh {target_mesh.name} is not a mesh.")
    if any(mesh.type != 'mesh' for mesh in merging_meshes):
        raise ValueError("All merging items must be of type 'mesh'.")

    vmap_normal_maps = set()
    for mesh in [target_mesh, *merging_meshes]:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f"Mesh {mesh.name} has no vmaps interface.")

        vmap_normal_maps.update(vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL))

    print(vmap_normal_maps)

    merge_meshes(target_mesh, merging_meshes)


def merge_meshes(target_mesh: modo.Item, merging_meshes: Iterable[modo.Item]):
    if target_mesh.type != 'mesh':
        raise ValueError(f"Target mesh {target_mesh.name} is not a mesh.")
    if any(mesh.type != 'mesh' for mesh in merging_meshes):
        raise ValueError("All merging items must be of type 'mesh'.")

    modo.Scene().deselect()
    target_mesh.select()
    for mesh in merging_meshes:
        mesh.select()

    lx.eval('layer.mergeMeshes true')


def get_vmap_normal_stats(meshes: Iterable[modo.Mesh]) -> VMAP_NORMAL_NAMES_STATS:
    vmap_normal_names = set()
    multiple_on_same_mesh = False
    for mesh in meshes:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f"Mesh {mesh.name} has no vmaps interface.")

        vmap_normal_maps = vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL)
        if len(vmap_normal_maps) > 1:
            multiple_on_same_mesh = True
        for vmap in vmap_normal_maps:
            vmap_normal_names.add(vmap.name)

    different_on_different_meshes = len(vmap_normal_names) > 1

    return VMAP_NORMAL_NAMES_STATS(
        different_on_different_meshes=different_on_different_meshes,
        multiple_on_same_mesh=multiple_on_same_mesh
    )


def get_instances(item: modo.Item) -> list[modo.Item]:
    instances = item.itemGraph('source').reverse()
    if not isinstance(instances, list):
        raise ValueError(f'Error getting instances for the <{item.name}> item')
    return instances


def get_instances_of(meshes: list[modo.Item]) -> list[modo.Item]:
    all_instances = []
    for mesh in meshes:
        all_instances.extend(get_instances(mesh))
    return all_instances


def get_instance_source(instance: modo.Item) -> modo.Item:
    if instance is None:
        raise ValueError('instance item error: value is None')
    if not instance.isAnInstance:
        return instance

    try:
        return instance.itemGraph('source').forward()[0]  # type:ignore
    except IndexError:
        raise ValueError('Failed to get source of instance from item graph "source"')


def instances_to_meshes(items: Iterable[modo.Item]) -> list[modo.Mesh]:
    meshes = []
    modo.Scene().deselect()
    for item in items:
        item.select()

    lx.eval('item.setType Mesh')
    meshes.extend(modo.Scene().selectedByType(itype=c.MESH_TYPE))

    return meshes


def swap_items(item1: modo.Item, item2: modo.Item):
    loc1 = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name="swap_locator1")
    loc2 = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name="swap_locator2")
    item1_parent = item1.parent
    item1_parent_index = get_parent_index(item1)
    item2_parent = item2.parent
    item2_parent_index = get_parent_index(item2)

    parent_items_to((loc1,), item1, inplace=False)
    parent_items_to((loc1,), item1_parent, index=item1_parent_index, inplace=True)

    parent_items_to((loc2,), item2, inplace=False)
    parent_items_to((loc2,), item2_parent, index=item2_parent_index, inplace=True)

    reset_transform(item1)
    reset_transform(item2)

    parent_items_to((item1,), loc2, inplace=False)
    parent_items_to((item1,), item2_parent, index=item2_parent_index, inplace=True)

    parent_items_to((item2,), loc1, inplace=False)
    parent_items_to((item2,), item1_parent, index=item1_parent_index, inplace=True)

    modo.Scene().removeItems(loc1)
    modo.Scene().removeItems(loc2)


def reset_transform(item: modo.Item):
    item.select(replace=True)
    lx.eval('transform.reset all')


if __name__ == "__main__":
    main()
