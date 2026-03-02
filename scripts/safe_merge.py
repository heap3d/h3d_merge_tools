#!/usr/bin/python
# ================================
# (C)2025-2026 Dmytro Holub
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

from h3d_utilites.scripts.h3d_utils import (
    get_user_value,
    parent_items_to,
    get_parent_index,
    itype_str,
)

USERVAL_VMAP_NORMAL_PERFECT_NAME = 'h3d_mrgt_vmap_normal_perfect_name'
DEFAULT_VMAP_NORMAL_PERFECT_NAME = 'normals'

SELECTED_TYPES = (itype_str(c.MESH_TYPE), itype_str(c.MESHINST_TYPE))


@dataclass
class VMAP_NORMAL_NAMES_STATS:
    different_on_different_meshes: bool
    multiple_on_same_mesh: bool


def main():
    selected_items: list[modo.Item] = [i for i in modo.Scene().selected if i.type in SELECTED_TYPES]

    if len(selected_items) < 2:
        print('Select at least 2 meshes to merge.')
        return

    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_normal_perfect_name:
        vmap_normal_perfect_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    target_item = selected_items[0]
    merging_items = selected_items[1:]

    safe_merge_meshes(target_item, merging_items, vmap_normal_perfect_name)


def safe_merge_meshes(target_item: modo.Item, merging_items: Iterable[modo.Item], perfect_vmap_normal_name: str):
    meshes: list[modo.Item] = [i for i in merging_items if i.type == itype_str(c.MESH_TYPE)]
    merging_instances: list[modo.Item] = [i for i in merging_items if i.type == itype_str(c.MESHINST_TYPE)]
    affected_instances = list(set(get_instances_of(meshes)) - set(merging_instances))
    affected_target_instances = list(set(get_instances(target_item)) - set(merging_instances))

    if affected_target_instances:
        target_instance = affected_target_instances[0]
        mesh = get_instance_source(target_instance)

        swap_items(mesh, target_instance)

        target_item = instances_to_meshes((target_instance,))[0]

    if target_item.type == itype_str(c.MESHINST_TYPE):
        try:
            affected_instances.remove(target_item)
        except ValueError:
            pass

        target_item = instances_to_meshes((target_item,))[0]

    while affected_instances:
        affected_instance = affected_instances.pop(0)

        instance_source_mesh = get_instance_source(affected_instance)

        source_affected_instances = list(set(get_instances(instance_source_mesh)) - set(merging_instances))

        instance = source_affected_instances[0]

        swap_items(instance_source_mesh, instance)

        try:
            meshes.remove(instance_source_mesh)
        except ValueError:
            pass

        merging_instances.append(instance)

        for instance in source_affected_instances:
            try:
                affected_instances.remove(instance)
            except ValueError:
                pass

    frozen_instances = instances_to_meshes(merging_instances)

    vmap_normal_maps = set()
    for mesh in [target_item, *meshes, *frozen_instances]:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f'Mesh {mesh.name} has no vmaps interface.')

        vmap_normal_maps.update(vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL))

    merge_meshes(target_item, meshes + frozen_instances)


def merge_meshes(target_item: modo.Item, merging_items: Iterable[modo.Item]):
    if target_item.type != itype_str(c.MESH_TYPE):
        raise ValueError(f'Target item {target_item.name} is not a mesh.')
    if any(mesh.type != itype_str(c.MESH_TYPE) for mesh in merging_items):
        raise ValueError('All merging items must be of type "mesh".')

    modo.Scene().deselect()
    target_item.select()
    for mesh in merging_items:
        mesh.select()

    lx.eval('layer.mergeMeshes true')


def get_vmap_normal_stats(meshes: Iterable[modo.Mesh]) -> VMAP_NORMAL_NAMES_STATS:
    vmap_normal_names = set()
    multiple_on_same_mesh = False
    for mesh in meshes:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f'Mesh {mesh.name} has no vmaps interface.')

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
        raise ValueError(f'Error getting instances for the <{item.name}> item.')
    return instances


def get_instances_of(meshes: list[modo.Item]) -> list[modo.Item]:
    all_instances = []
    for mesh in meshes:
        all_instances.extend(get_instances(mesh))
    return all_instances


def get_instance_source(instance: modo.Item) -> modo.Item:
    if instance is None:
        raise ValueError('instance item error: value is None.')
    if not instance.isAnInstance:
        return instance

    try:
        return instance.itemGraph('source').forward()[0]  # type:ignore
    except IndexError:
        raise ValueError('Failed to get source of instance from item graph "source".')


def instances_to_meshes(items: Iterable[modo.Item]) -> list[modo.Mesh]:
    meshes = []
    modo.Scene().deselect()
    for item in items:
        item.select()

    lx.eval('item.setType Mesh')
    meshes.extend(modo.Scene().selectedByType(itype=c.MESH_TYPE))

    return meshes


def swap_items(item1: modo.Item, item2: modo.Item):
    loc1 = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name='swap_locator1')
    loc2 = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name='swap_locator2')
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


if __name__ == '__main__':
    main()
