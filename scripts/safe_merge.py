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


def main():
    selected_meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)


if __name__ == "__main__":
    main()
