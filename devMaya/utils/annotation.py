from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating annotations to improve clarity in a rig
"""


def create_annotation(obj_target, obj_parent) -> str:
    lct = cmds.spaceLocator(name="lct_" + obj_target + "_annotation")[0]
    pos = cmds.xform(obj_target, q=True, ws=True, t=True)
    cmds.xform(lct, ws=True, t=pos)
    cmds.parent(lct, obj_target)
    cmds.setAttr(f"{lct}.visibility", 0)


    annotation_shape = cmds.annotate(lct, text="")
    annotation = annotation_shape.replace("Shape", "")
    cmds.parent(annotation, obj_parent, s=1)
    cmds.xform(annotation, os=True, t=[0, 0, 0])

    cmds.setAttr(f"{annotation_shape}.overrideEnabled", 1)
    cmds.setAttr(f"{annotation_shape}.overrideDisplayType", 2)

    cmds.rename(annotation, obj_target + "_annotation")
