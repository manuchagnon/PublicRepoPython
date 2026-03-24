import math

from maya import cmds
from maya import OpenMaya as omui


def get_pole_vector_placement(jnt_first, jnt_mid, jnt_last, scale=4):
    """
    With a joint_chain of 3 joints, place a locator with the right pos and rot for pole vector constraint
    """

    pos_start = cmds.xform(jnt_first, q=1, ws=1, t=1)
    pos_mid = cmds.xform(jnt_mid, q=1, ws=1, t=1)
    pos_end = cmds.xform(jnt_last, q=1, ws=1, t=1)

    startV = omui.MVector(pos_start[0], pos_start[1], pos_start[2])
    midV = omui.MVector(pos_mid[0], pos_mid[1], pos_mid[2])
    endV = omui.MVector(pos_end[0], pos_end[1], pos_end[2])

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd

    proj = float(dotP) / float(startEnd.length())

    startEndN = startEnd.normal()

    projV = startEndN * proj

    arrowV = startMid - projV

    arrowV*= scale

    finalV = arrowV + midV

    cross1 = startEnd ^ startMid
    cross1.normalize()

    cross2 = cross1 ^ arrowV
    cross2.normalize()

    arrowV.normalize()

    matrixV = [
        arrowV.x , arrowV.y , arrowV.z , 0 ,
        cross1.x ,cross1.y , cross1.z , 0 ,
        cross2.x , cross2.y , cross2.z , 0,
        0,0,0,1
        ]

    matrixM = omui.MMatrix()

    omui.MScriptUtil.createMatrixFromList(matrixV , matrixM)

    matrixFn = omui.MTransformationMatrix(matrixM)

    rot = matrixFn.eulerRotation()

    loc = cmds.spaceLocator()[0]

    cmds.xform(loc , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
    cmds.xform ( loc , ws = 1 , rotation = ((rot.x/math.pi*180.0), (rot.y/math.pi*180.0), (rot.z/math.pi*180.0)))

    return loc