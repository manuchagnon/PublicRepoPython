from maya import cmds
import maya.api.OpenMaya as om

from devUtils.maths import lerp_vector_three
"""
Functions that deals with :
interpolating positions

TO DO:
Use OpenMaya objects
"""

def lerp_pos(obj1: str | list[str], obj2: str | list[str], factor=0.5):
    """
    Interpolate between two position and return the new position
    """
    if isinstance(obj1, str):
        pos1 = cmds.xform(obj1, query=True, worldSpace=True, translation=True)
    elif isinstance(obj1, list):
        pos1 = obj1

    if isinstance(obj2, str):
        pos2 = cmds.xform(obj2, query=True, worldSpace=True, translation=True)
    elif isinstance(obj2, list):
        pos2 = obj2

    x, y, z = lerp_vector_three(pos1, pos2, factor)


    return (x, y, z)