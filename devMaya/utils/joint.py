from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating joints
"""

def create_jnt(obj_list = None, parent = 1, suffix="") -> list[str]:
    """
    Create joints under the selected objects

    obj_list: list of objects to create joints under
    parent:
        0 == no parenting
        1 == jnt is parented to obj
        2 == jnt is parent of obj
    suffix:
    """

    if not obj_list: # if no list is provided, use the selected objects ([] if no selection)
        obj_list = cmds.ls(sl=1)

    if suffix:
        suffix = "_" + suffix

    cmds.select(clear=1)

    jnt_created = []

    for obj in obj_list:
        if "_" in obj:
            obj_name = obj.split('_', 1)[1]
        else:
            obj_name = obj

        jnt = cmds.joint(n=f'jnt_{obj_name}{suffix}')
        cmds.select(clear=1)

        if parent == 1:
            cmds.parent(jnt, obj)
            cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])

        if parent == 2:
            obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0]
            cmds.parent(jnt, obj_parent)
            cmds.xform(jnt, t=[0, 0, 0], ro=[0, 0, 0])

            cmds.parent(obj, jnt)

        jnt_created.append(jnt)

    # Select the obj back
    cmds.select(obj_list)

    return jnt_created