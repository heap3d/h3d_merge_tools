#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# merge first selected meshes to the last selected one (reversed order relative no native modo merge)
# ================================

import modo
import modo.constants as c

from h3d_merge_tools.scripts.safe_merge import safe_merge_meshes


def main():
    selected_meshes: list[modo.Mesh] = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    source_items: list[modo.Mesh] = selected_meshes[:-1]
    target_item: modo.Item = selected_meshes[-1]

    safe_merge_meshes(target_item, source_items)


if __name__ == "__main__":
    main()
