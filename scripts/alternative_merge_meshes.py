#!/usr/bin/python
# ================================
# (C)2025-2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# merge first selected meshes to the last selected one (reversed order relative no native modo merge)
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_merge_tools.scripts.safe_merge import (
    DEFAULT_VMAP_NORMAL_PERFECT_NAME,
    USERVAL_VMAP_NORMAL_PERFECT_NAME,
    SELECTED_TYPES,
    safe_merge_meshes,
)


def main():
    selected_items: list[modo.Item] = [i for i in modo.Scene().selected if i.type in SELECTED_TYPES]
    if len(selected_items) < 2:
        print('Select at least 2 meshes to merge.')
        return

    target_mesh: modo.Item = selected_items[-1]
    merging_meshes: list[modo.Item] = selected_items[:-1]

    vmap_normal_perfect_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_normal_perfect_name:
        vmap_normal_perfect_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    safe_merge_meshes(target_mesh, merging_meshes, vmap_normal_perfect_name)


if __name__ == '__main__':
    # h3dd.enable_debug_output()
    main()
