from maya import cmds
import maya.api.OpenMaya as om


def dot(v1: om.MVector, v2: om.MVector) -> float:
    """ Dot product """
    return v1 * v2
