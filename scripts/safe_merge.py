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
USERVAL_MARK_COLOR = 'h3d_mrgt_mark_color'
DEFAULT_VMAP_NORMAL_PERFECT_NAME = 'normals'

SELECTED_TYPES = (itype_str(c.MESH_TYPE), itype_str(c.MESHINST_TYPE))


@dataclass
class VMAP_NORMAL_NAMES_STATS:
    vmap_normal_names: set[str]
    multiple_vmap_normal_meshes: set[modo.Item]


@dataclass
class VMAP_NORMAL_ENV:
    vmap_normal_perfect_name: str
    mark_color: str


def main():
    selected_items: list[modo.Item] = [i for i in modo.Scene().selected if i.type in SELECTED_TYPES]

    if len(selected_items) < 2:
        print('Select at least 2 meshes to merge.')
        return

    target_item = selected_items[0]
    merging_items = selected_items[1:]

    env = initialize_env()

    stats = safe_merge_meshes(target_item, merging_items, env.vmap_normal_perfect_name)

    stats_processing(stats, env)


def initialize_env() -> VMAP_NORMAL_ENV:
    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_normal_perfect_name:
        vmap_normal_perfect_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    mark_color_index = int(get_user_value(USERVAL_MARK_COLOR))
    mark_color = color_by_index(mark_color_index)

    return VMAP_NORMAL_ENV(
        vmap_normal_perfect_name=vmap_normal_perfect_name,
        mark_color=mark_color,
    )


def color_by_index(index: int) -> str:
    color_dict = {
        0: 'none',
        1: 'red',
        2: 'magenta',
        3: 'pink',
        4: 'brown',
        5: 'orange',
        6: 'yellow',
        7: 'green',
        8: 'cyan',
        9: 'blue',
        10: 'lightblue',
        11: 'ultramarine',
        12: 'purple',
        13: 'lightpurple',
        14: 'darkgrey',
        15: 'grey',
        16: 'white',
    }
    return color_dict.get(index, 'none')


def safe_merge_meshes(
        target_item: modo.Item,
        merging_items: Iterable[modo.Item],
        perfect_vmap_normal_name: str,
        ) -> VMAP_NORMAL_NAMES_STATS:

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

    merging_meshes = set(meshes + frozen_instances)
    if not all(mesh.type == itype_str(c.MESH_TYPE) for mesh in merging_meshes):
        raise ValueError('All merging items must be of type "mesh".')

    stats = get_vmap_normal_stats((target_item, *merging_meshes))
    merging_meshes -= stats.multiple_vmap_normal_meshes

    if target_item in stats.multiple_vmap_normal_meshes:
        if merging_meshes:
            target_item = merging_meshes.pop()

    if len(stats.vmap_normal_names) > 1 or perfect_vmap_normal_name not in stats.vmap_normal_names:
        rename_vmap_normals((target_item, *merging_meshes), perfect_vmap_normal_name)

    if merging_meshes:
        merge_meshes(target_item, merging_meshes)

    return stats


def stats_processing(stats: VMAP_NORMAL_NAMES_STATS, env: VMAP_NORMAL_ENV, show_ok: bool = False):
    stats_message = ''
    if stats.multiple_vmap_normal_meshes:
        if env.mark_color != 'none':
            color_items(stats.multiple_vmap_normal_meshes, env.mark_color)
            stats_message += f'Meshes with multiple vertex normal maps marked with <{env.mark_color}> color.\n'
        else:
            stats_message += 'Meshes with multiple vertex normal maps detected.\n'

    is_names_differs = len(stats.vmap_normal_names) > 1
    is_valid_name = len(stats.vmap_normal_names) == 1 and env.vmap_normal_perfect_name in stats.vmap_normal_names
    is_empty = not stats.vmap_normal_names

    if is_names_differs or not (is_valid_name or is_empty):
        stats_message += 'Invalid vertex normal map names detected.\n'

    if show_ok and not stats_message:
        stats_message = 'No issues detected with vertex normal map names.'

    if stats_message:
        modo.dialogs.alert(title='Vertex Normal Map Names', dtype='info', message=stats_message)


def get_vmap_normal_stats(meshes: Iterable[modo.Item]) -> VMAP_NORMAL_NAMES_STATS:
    vmap_normal_names = set()
    meshes_with_multiple_vmap_normal_maps = set()
    for mesh in meshes:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f'Mesh {mesh.name} has no vmaps interface.')

        vmap_normal_maps = vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL)
        if len(vmap_normal_maps) > 1:
            meshes_with_multiple_vmap_normal_maps.add(mesh)
        for vmap in vmap_normal_maps:
            vmap_normal_names.add(vmap.name)

    return VMAP_NORMAL_NAMES_STATS(
        vmap_normal_names=vmap_normal_names,
        multiple_vmap_normal_meshes=meshes_with_multiple_vmap_normal_maps,
    )


def color_items(items: Iterable[modo.Item], color: str):
    modo.Scene().deselect()
    for item in items:
        item.select()

    lx.eval(f'item.editorColor {color}')


def rename_vmap_normals(meshes: Iterable[modo.Item], vmap_normal_name: str):
    for mesh in meshes:
        vmaps = mesh.geometry.vmaps
        if vmaps is None:
            raise ValueError(f'Mesh {mesh.name} has no vmaps interface.')

        vmap_normal_maps = vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL)
        for vmap in vmap_normal_maps:
            vmap.name = vmap_normal_name


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
