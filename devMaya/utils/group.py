from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating groups
"""


def create_grp(obj_list = None, gizmo = 0, gizmo_target_obj = None, suffix = "") -> list[str]:
    """
    Create groups on selected objects

    obj_list: list of objects to create group with
    gizmo:
        0 == no gizmo change
        1 == put gizmo at world origin
        2 == put gizmo at choosen object's position
    suffix:
    """

    grp_created = []

    if suffix != "":
        suffix = "_" + suffix

    for obj in obj_list:
        grp = cmds.group(n=f'{obj}_{suffix}_grp', empty=1)

        pos = cmds.xform(obj, q=1, ws=1, t=1)
        rot = cmds.xform(obj, q=1, ws=1, rotation=1)
        cmds.xform(grp, ws=1, t=pos, rotation=rot)

        if cmds.listRelatives(obj, parent=1):
            obj_parent = cmds.listRelatives(obj, parent=1)
            cmds.parent(grp, obj_parent)

        cmds.parent(obj, grp)


        if gizmo == "world":
            cmds.xform(f'{grp}.scalePivot', ws=1, t=[0, 0, 0], ro=[0, 0, 0])
            cmds.xform(f'{grp}.rotatePivot', ws=1, t=[0, 0, 0], ro=[0, 0, 0])

        elif gizmo:
            pos = cmds.xform(gizmo, q=1, ws=1, t=1)
            rot = cmds.xform(gizmo, q=1, ws=1, ro=1)
            print("rot =", rot, "pos = ", pos)
            cmds.xform(f'{grp}.scalePivot', ws=1, t=pos, ro=rot)
            cmds.xform(f'{grp}.rotatePivot', ws=1, t=pos, ro=rot)

        grp_created.append(grp)

    return grp_created