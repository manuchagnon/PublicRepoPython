from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
creating selection sets,
adding attribute override to sets,

"""


def create_set(obj_list, set_name : str = None):
    if not set_name :
        set_name = obj_list[0] + "_set"

    if cmds.objExists(set_name):
        add_to_set(obj_list, set_name)
    else:
        cmds.sets(name=set_name, empty=True)
        cmds.sets(*obj_list, add=set_name)

def add_to_set(obj_list, set_name):
    if not cmds.objExists(set_name):
        print("No set has the name :", set_name)
        return

    cmds.sets(*obj_list, add=set_name)

