from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating groups
"""


def create_grp(obj : str, gizmo_status = 0, gizmo_target_obj = None, suffix = ""):
    """
    Create groups on selected objects

    obj_list: list of objects to create group with
    gizmo_status:
        0 == no gizmo change
        1 == put gizmo at world origin
        2 == put gizmo at choosen object's position
    suffix:
    """

    if suffix != "" and "_" not in suffix:
        suffix = "_" + suffix

    grp = cmds.group(n=f'{obj}{suffix}_grp', empty=1)

    pos = cmds.xform(obj, q=1, ws=1, t=1)
    rot = cmds.xform(obj, q=1, ws=1, rotation=1)
    cmds.xform(grp, ws=1, t=pos, rotation=rot)

    if cmds.listRelatives(obj, parent=1):
        obj_parent = cmds.listRelatives(obj, parent=1)
        cmds.parent(grp, obj_parent)

    cmds.parent(obj, grp)

    if gizmo_status == 1:
        cmds.xform(f'{grp}.scalePivot', ws=1, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.xform(f'{grp}.rotatePivot', ws=1, t=[0, 0, 0], ro=[0, 0, 0])

    elif gizmo_status == 2:
        pos = cmds.xform(gizmo_target_obj, q=1, ws=1, t=1)
        rot = cmds.xform(gizmo_target_obj, q=1, ws=1, ro=1)
        cmds.xform(f'{grp}.scalePivot', ws=1, t=pos, ro=rot)
        cmds.xform(f'{grp}.rotatePivot', ws=1, t=pos, ro=rot)


    return grp


def create_grps(obj_list : list[str] = [], gizmo_status = 0, gizmo_target_obj = None, suffix = "", in_autorig=True) -> list[str]:

    if obj_list == []:
        obj_list = cmds.ls(sl=1)

    grp_created = []

    for obj in obj_list:
        grp = create_grp(obj, gizmo_status = gizmo_status, gizmo_target_obj = gizmo_target_obj, suffix = suffix)
        grp_created.append(grp)

    if not in_autorig:
        cmds.select(grp_created)

    return grp_created