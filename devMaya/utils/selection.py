from maya import cmds
import maya.api.OpenMaya as om

"""
Functions that deals with :
selecting object(s)
converting range selection into flat list

"""

def select_object(obj=None) -> str | None:
    if not obj:
        sl = cmds.ls(sl=1)
        if sl:
            obj = sl[0]
        else:
            print("No object Selected")
            return None

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

def convert_range_into_list(range:str) -> list[str]:
    return cmds.ls(range, flatten=True)

