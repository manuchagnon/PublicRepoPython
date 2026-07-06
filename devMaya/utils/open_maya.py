import maya.api.OpenMaya as om
import maya.cmds as cmds

def get_dag_path(node_name: str) -> om.MDagPath:
    sel = om.MSelectionList()
    sel.add(node_name)
    return sel.getDagPath(0)

