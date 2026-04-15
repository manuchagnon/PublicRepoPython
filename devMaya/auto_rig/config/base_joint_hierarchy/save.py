from yaml import load, dump

import maya.cmds as cmds

def save_base_joint_hierarchy_from_dict(hierarchy_dict: dict, path: str="auto"):
    """
    Creates a yaml file containing the custom base joint chain hierarchy for auto rigs modules
    """


