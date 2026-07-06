from maya import cmds
import maya.api.OpenMaya as om

from devMaya.auto_rig.component.controller import Controller
from devMaya.utils.attribute import Attribute

"""
Functions that deal with maya constraints and custom constraints :
hinge_setup

Custom functions to create maya constraints, in order to switch to matrix constraints when possible :

"""


def hinge_constraint(orient_source: str, orient_target: Controller, ctl_blend: Controller | str, lct_name="locator", lct_parent: str|None= None, suffix=""):
    """
    Create a constraint setup that lock target orientation 
    """
    lct = cmds.spaceLocator(name=lct_name)[0]

    if lct_parent:
        cmds.parent(lct, lct_parent)
        cmds.makeIdentity(lct)
    cmds.parentConstraint(orient_source, lct, mo=1)

    rot_grp = orient_target.add_offset_grp(suffix="_ORIENT")

    blend = cmds.createNode("blendColors", name="blend_" + orient_source)
    cmds.connectAttr(f"{lct}.rotate", f"{blend}.color1")
    cmds.connectAttr(f"{blend}.output", f"{rot_grp}.rotate")
    cmds.setAttr(f"{blend}.color2B", 0)

    blend_attr = Attribute(long_name=suffix, type="float", min=0.0, max=1.0,
                           node=ctl_blend)
    blend_attr.add_to_node(ctl_blend)
    blend_attr.plug_to(f"{blend}.blender")