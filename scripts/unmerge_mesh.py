#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# modo unmerge mesh command with execution timer alarm
# ================================


import lx

from h3d_utilites.scripts.h3d_utils import execution_time_alarm


@execution_time_alarm
def main():
    lx.eval('layer.unmergeMeshes')


if __name__ == '__main__':
    main()