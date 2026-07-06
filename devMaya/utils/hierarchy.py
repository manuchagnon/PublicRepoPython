from maya import cmds

"""
Functions that deals with outliner hierarchy
"""

def get_children_from_root_node(root: str, recursive=True, shape=False, reverse=True) -> list[str]:
    """
    Get the root children as a list with custom parameters
    """
    if not shape:
        if recursive:
            children = cmds.listRelatives(root, allDescendents=1, type="transform", fullPath=1, noIntermediate=1)
        else:
            children = cmds.listRelatives(root, children=1, type="transform", fullPath=1, noIntermediate=1)
    else:
        if recursive:
            children = cmds.listRelatives(root, allDescendents=1, type="transform", fullPath=1)
        else:
            children = cmds.listRelatives(root, children=1, type="transform", fullPath=1)

    if reverse:
        return children
    else:
        return children[::-1]

def get_hierarchy_list_from_root_node(root: str, shape=False, reverse=True) -> list[str]:
    """
    Get the root children and the root node as a list
    """
    children = get_children_from_root_node(root, shape=shape, reverse=reverse)
    if reverse:
        children.append(root)
    else:
        children.insert(0, root)
    return children


def get_hierarchy_dict_from_root_node(root: str, hierarchy_dict: dict, name=True, position=True, rotation=True, type=True) -> dict[str, dict]:
    """
    Recursively create a nested dictionary with wanted hierarchy information = name, position, rotation, type
    """

    if name:
        hierarchy_dict["name"] = root
    if position:
        hierarchy_dict["position"] = cmds.xform(root, ws=True, q=True, t=True)
    if rotation:
        hierarchy_dict["rotation"] = cmds.xform(root, ws=True, q=True, ro=True)
    if type:
        hierarchy_dict["type"] = cmds.objectType(root)

    children = cmds.listRelatives(root, children=True, shapes=False) or []

    for child in children:
        hierarchy_dict.setdefault("children", {}).setdefault(child, {})
        get_hierarchy_dict_from_root_node(root=child, hierarchy_dict=hierarchy_dict["children"][child], name=name, position=position, rotation=rotation, type=type)

    return hierarchy_dict