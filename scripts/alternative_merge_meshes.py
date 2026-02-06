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
import lx


def main():
    selected_meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    source_items = selected_meshes[:-1]
    target_item = selected_meshes[-1]

    modo.Scene().deselect()
    modo.Scene().select(target_item)
    for item in source_items:
        item.select()

    lx.eval('layer.mergeMeshes true')


if __name__ == "__main__":
    main()
