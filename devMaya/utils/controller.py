from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating controllers
"""

def create_FK_ctl(objects=None, parented = False, radius=1, normal=[1, 0, 0], **kwargs):
    """
    Create controllers on selected objects
    """

    # if no objects are provided
    if not objects:
        if "message" in kwargs.keys():
            print(f"Error at creating {kwargs['message']} controllers")
        print("Couldn't create controllers")
        return

    ctl_list = []
    ctl_grp_list = []

    for i in range(len(objects)):
        o = objects[i]
        name = ""

        if "_" in o:
            name = o.split("_")[1]
        ctl = cmds.circle(name=f"ctl_{name}", radius=radius, normal=normal, ch=0)[0]
        ctl_list.append(ctl)
        ctl_grp = cmds.group(name=f"ctl_{name}_grp")
        ctl_grp_list.append(ctl_grp)

        cmds.matchTransform(ctl_grp, o)

        if parented and len(ctl_list) >= 2 :
            cmds.parent(ctl_grp, ctl_list[i-1])

    return ctl_list, ctl_grp_list

def set_ctl_scale(ctl, scale):
    pass

def rotate_ctl(ctl, axis, degree):
    pass