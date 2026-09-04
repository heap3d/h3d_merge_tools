#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# modo merge command. to avoid modo crash on RMB menu
# ================================

import lx

from h3d_utilites.scripts.h3d_utils import execution_time_alarm


@execution_time_alarm('Modo Merge Meshes')
def main():
    lx.eval('layer.mergeMeshes')


if __name__ == '__main__':
    main()
