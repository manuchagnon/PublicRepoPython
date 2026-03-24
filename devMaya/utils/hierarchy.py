from maya import cmds

"""
Functions that deals with outliner hierarchy
"""

def get_children_from_root_node(root: str, recursive=True, shape=False) -> list[str]:
    if not shape:
        if recursive:
            return cmds.listRelatives(root, allDescendents=1, type="transform", fullPath=1, noIntermediate=1)
        else:
            return cmds.listRelatives(root, children=1, type="transform", fullPath=1, noIntermediate=1)
    else:
        if recursive:
            return cmds.listRelatives(root, allDescendents=1, type="transform", fullPath=1)
        else:
            return cmds.listRelatives(root, children=1, type="transform", fullPath=1)

def get_hierarchy_from_root_node(root: str, shape=False) -> list[str]:
    children = get_children_from_root_node(root, shape=shape)
    children.append(root)
    return children