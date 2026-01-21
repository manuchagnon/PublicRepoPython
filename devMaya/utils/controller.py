from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating controllers
setting controller scale
rotating controller cvs
changing controller shape
"""

def create_FK_ctl(obj_list : list[str], parented = False, parent=0, radius=1, normal=[1, 0, 0]):
    """
    Create controllers on selected obj_list
    parented : to make the created controllers parented to eachother in a FK chain
    parent : to make controller
    """

    ctl_list = []
    ctl_grp_list = []

    if obj_list == []:
        obj_list = cmds.ls(sl=1)

    for i in range(len(obj_list)):
        obj = obj_list[i]
        name = ""

        if "_" in obj:
            name = obj.split("_")[1]

        # To do : replace by customizable ctl
        ctl = cmds.circle(name=f"ctl_{name}", radius=radius, normal=normal, ch=0)[0]

        ctl_list.append(ctl)
        ctl_grp = cmds.group(name=f"ctl_{name}_grp")
        ctl_grp_list.append(ctl_grp)
        cmds.parent(ctl, ctl_grp)

        cmds.matchTransform(ctl_grp, obj)

        if parented and len(ctl_list) >= 2 :
            cmds.parent(ctl_grp, ctl_list[i-1])

        if parent == 1:
            cmds.parent(ctl_grp, obj)

        if parent == 2:
            obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0]
            cmds.parent(ctl, obj_parent)
            cmds.xform(ctl, t=[0, 0, 0], ro=[0, 0, 0])
            cmds.parent(obj, ctl)

    return ctl_list, ctl_grp_list

def set_ctl_scale(ctl_list : list[str], scale : float):
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for i in range(len(ctl_list)):
        ctl = ctl_list[i]

        selected_cv = []
        try:
            for i_cv in range(len(f'{ctl}.cv')):
                selected_cv.append(f'{ctl}.cv[{i_cv}]')

            cmds.scale(scale, scale, scale, selected_cv, a=1, ws=1)
        except:
            print("Object", ctl, "has no cv")
            continue

    return ctl_list

def rotate_ctl(ctl_list : list[str], axis : str, degrees : int):
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for i in range(len(ctl_list)):
        ctl = ctl_list[i]

        selected_cv = []
        try:
            for i_cv in range(len(f'{ctl}.cv')):
                selected_cv.append(f'{ctl}.cv[{i_cv}]')

            if axis == "X":
                cmds.rotate(degrees, 0, 0, selected_cv, a=1, os=1)
            if axis == "Y":
                cmds.rotate(0, degrees, 0, selected_cv, a=1, os=1)
            if axis == "Z":
                cmds.rotate(0, 0, degrees, selected_cv, a=1, os=1)

        except:
            print("Object", ctl, "has no cv")
            continue

    return ctl_list

def change_ctl_shape(shape : str, ctl_list = []):
    pass
