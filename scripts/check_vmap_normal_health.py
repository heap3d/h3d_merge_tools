#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# warn about different names of vertex normal maps or multiple vertex normal maps in one mesh.
# ================================

from typing import Optional

import modo
import modo.constants as c

from h3d_merge_tools.scripts.safe_merge import get_vmap_normal_stats, stats_processing, initialize_env

from h3d_utilites.scripts.h3d_utils import ExecutionTimerAlarm


def main():
    alarm_timer = ExecutionTimerAlarm('Check Vertex Normal Map Names')
    check_vmap_normal_health(show_ok=True, alarm_timer=alarm_timer)


def check_vmap_normal_health(
        show_ok:bool=False,
        alarm_timer: Optional[ExecutionTimerAlarm] = None,
        supress_warnings: bool = False
    ):
    
    meshes = modo.Scene().items(itype=c.MESH_TYPE)
    stats = get_vmap_normal_stats(meshes)

    env = initialize_env()

    if not alarm_timer:
        alarm_timer = ExecutionTimerAlarm('Check Vertex Normal Map Names NO ALARM')
        alarm_timer.enabled = False
    stats_processing(stats, env, alarm_timer, show_ok=show_ok, supress_warnings=supress_warnings)


if __name__ == '__main__':
    main()
