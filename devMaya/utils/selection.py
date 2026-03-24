from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
selecting object(s)

"""

def select_object(obj=None):
    if not obj:
        try:
            obj = cmds.ls(sl=1)[0]
        except:
            print("No object Selected")

    try:
        cmds.select(obj)
        return obj
    except:
        print(f"No Object have the name {obj}")
        return None


def select_objects(obj=[]):
    if not obj:
        obj = cmds.ls(sl=1)[0]
    if obj:
        cmds.select(obj)
