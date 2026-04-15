from maya import cmds
import math

from devUtils.maths import remap_value


"""
Function that deals with nurbsCurve:
    - place Locators equally along the curve U parameter

"""


def get_parameter_u_with_pos(crv: str, pos) -> int:
    """
    Returns the closest crv U parameter at chosen pos
    """
    npoc = cmds.createNode("nearestPointOnCurve")
    cmds.connectAttr(crv + ".worldSpace", npoc + ".inputCurve")
    for i, axis in enumerate(["X", "Y", "Z"]):
        cmds.setAttr(f"{npoc}.inPosition{axis}", pos[i])

    param_u = cmds.getAttr(npoc + ".parameter")

    cmds.delete(npoc)

    return param_u


def get_pos_with_parameter_u(crv: str, param_u) -> list[float, float, float]:
    """
    Returns the pos at chosen crv U parameter
    """
    poc = cmds.createNode("pointOnCurveInfo", name=f"poc_{crv}")
    cmds.connectAttr(crv + ".worldSpace", poc + ".inputCurve")
    cmds.setAttr(poc + ".parameter", param_u)
    pos = cmds.getAttr(poc + ".position")[0]
    cmds.delete(poc)

    return pos


def constraint_obj_to_crv(crv: str, obj: str, param_u=None):
    """
    Parent the obj to a locator attached to the nearest point on the curve
    """
    pos = cmds.xform(obj, q=1, ws=1, t=1)
    param_u = get_parameter_u_with_pos(crv=crv, pos=pos)
    lct = constraint_lct_to_crv_with_parameter_u(crv=crv, param_u=param_u)
    cmds.parent(obj, lct)


def constraint_lct_to_crv_with_parameter_u(crv: str, param_u: float=0,  constrained: bool=True) -> str:
    poc = cmds.createNode("pointOnCurveInfo", name=f"poc_{crv}")
    cmds.connectAttr(crv + ".worldSpace", poc + ".inputCurve")
    cmds.setAttr(poc + ".parameter", param_u)

    lct = cmds.spaceLocator(name=f"lct_{crv}")[0]
    cmds.connectAttr(poc + ".position", lct + ".translate")
    if not constrained:
        pos = cmds.getAttr(poc + ".position")[0]
        cmds.xform(lct, ws=1, t=pos)
        cmds.delete(poc)

    return lct

def distribute_lct_on_crv(crv: str, inst_number: int, constrained: bool=True, param_u_start: float=0.0, param_u_end: float=1.0):
    """
    Instance Locators equally along the curve

    constrained : if locator are attached to the curve or only placed

    """
    if inst_number <= 0:
        return

    lct_list = []

    for i in range(inst_number):
        param_u = i / (inst_number - 1)
        param_u = remap_value(param_u, old_start=0, old_end=1, new_start=param_u_start, new_end=param_u_end)

        lct = constraint_lct_to_crv_with_parameter_u(crv=crv, param_u=param_u, constrained=constrained)
        new_name = f"{lct}_{i}"
        cmds.rename(lct, new_name)
        lct = new_name

        lct_list.append(lct)

    return lct_list

def create_crv_with_vtx(vtx_list: list[str], suffix="_high"):
    cvs_pos = [cmds.xform(vtx, q=1, ws=1, t=1) for vtx in vtx_list]

    cmds.curve(d=1, p=cvs_pos, n=f"crv_{vtx_list[0].split('_')[-1]}{suffix}")

"""
# créer les joints et locators
for i in range(len(vtx_list)):
    vtx = vtx_list[i]
    jnt = cmds.joint(n=f'jnt_{vtx_name}_{i}')  # jnt enfant
    cmds.select(clear=1)
    pos = cmds.xform(vtx, q=1, ws=1, t=1)
    cmds.xform(jnt, ws=1, t=pos)

    posC = cmds.xform(jnt_eyeCenter, q=1, ws=1, t=1)
    jntC = cmds.joint(n=f'jnt_{vtx_name}Center_{i}')  # jnt center
    cmds.select(clear=1)
    cmds.xform(jntC, ws=1, t=posC)

    cv_pos_list.append(pos)  # ajouter la pos de ce vtx pour la curve

    cmds.parent(jnt, jntC)

    cmds.joint(jntC, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)

    cmds.parent(jntC, jnt_grp)  # mettre les jnt dans un grp


    loc = cmds.spaceLocator(n=f'lct_{vtx}_{i}')[0]  # locator sur jnt enfant
    cmds.xform(loc, ws=1, t=pos)

    cmds.aimConstraint(loc, jntC, mo=1, weight=1, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="object",
                       worldUpObject=locUpVector)

    cmds.parent(loc, lct_grp)  # mettre les lct dans un grp


for lct in lct_list:
    pos = cmds.xform(lct, q=1, ws=1, t=1)
    u = getUParam(pos, crvHigh)

    name = lct.replace("lct_", "pci_")
    pci = cmds.createNode("pointOnCurveInfo", n=name)
    cmds.connectAttr(crvHigh + ".worldSpace", pci + ".inputCurve")
    cmds.setAttr(pci + ".parameter", u)

    cmds.connectAttr(pci + ".position", lct + ".translate")
"""