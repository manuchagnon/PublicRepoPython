from maya import cmds
import maya.api.OpenMaya as om

"""
CURRENTLY NOT WORKING

Functions that deal with matrix constraints :
Aim 
Parent offset False
"""

PREFIX = {
    "decompose" : "dcm_",
    "aim" : "am_",
}

def create_decompose_matrix_node(name):
    return cmds.createNode("decomposeMatrix", name=PREFIX["decompose"] + name)

def aim_matrix_constraint(target, constrained, offset=False, primary_axis=[1, 0, 0], secondary_axis=[0, 1, 0]):
    """
    Aim constraint with Matrix
    """

    matrix = cmds.createNode("aimMatrix", name=PREFIX["aim"] + target)
    cmds.connectAttr(f"{target}.worldMatrix[0]", f"{matrix}.primaryTargetMatrix")

    if not primary_axis == [1, 0, 0]:
        cmds.setAttr(f"{matrix}.primaryInputAxis", primary_axis)
    if not secondary_axis == [0, 1, 0]:
        cmds.setAttr(f"{matrix}.secondaryInputAxis", secondary_axis)

    decompose = create_decompose_matrix_node(name=PREFIX["decompose"] + target)

    cmds.connectAttr(f"{matrix}.outputMatrix", f"{decompose}.inputMatrix")

    cmds.connectAttr(f"{decompose}.outputRotate", f"{constrained}.rotate")

    return matrix


def get_world_matrix(dag_path: om.MDagPath) -> om.MMatrix:
    """ Return world matrix """
    return dag_path.inclusiveMatrix()


def extract_axes_from_matrix(matrix: om.MMatrix) -> dict:
    """
    Extract chosen axes from matrix
    """
    x_axis = om.MVector(matrix[0], matrix[1], matrix[2]).normalize()
    y_axis = om.MVector(matrix[4], matrix[5], matrix[6]).normalize()
    z_axis = om.MVector(matrix[8], matrix[9], matrix[10]).normalize()

    return {"X": x_axis, "Y": y_axis, "Z": z_axis}




