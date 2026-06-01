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


def create_crv_with_vtx(vtx_list: list[str], prefix="crv_", suffix="_high"):
    cvs_pos = [cmds.xform(vtx, q=1, ws=1, t=1) for vtx in vtx_list]
    crv = cmds.curve(d=1, p=cvs_pos, n=f"{prefix}{vtx_list[0].split('_')[-1]}{suffix}")[0]
    return crv

def create_crv_with_obj_list(obj_list: list[str], degree: int=1, crv_subdivision=2, name="", prefix="crv_", suffix=""):
    """
    Create a nurbsCurve with positions of objects in a list
    """

    if degree == 1:
        cvs_pos = [cmds.xform(obj, q=1, ws=1, t=1) for obj in obj_list]
        crv = cmds.curve(d=1, p=cvs_pos, n=f"{prefix}{name}{suffix}")
        return crv

    if degree == 3:
        crv_list = []
        for i in range(len(obj_list[:-1])):
            obj_start = obj_list[i]
            obj_end = obj_list[i+1]

            pos_start = cmds.xform(obj_start, q=1, ws=1, t=1)
            pos_end = cmds.xform(obj_end, q=1, ws=1, t=1)

            crv = cmds.curve(d=1, p=[pos_start, pos_end], n=f"{prefix}{name}_{i}")
            old_crv = cmds.rebuildCurve(crv, ch=0, rpo=1, rt=0, end=1, kr=1, kcp=0, kep=1, kt=1, s=crv_subdivision, d=3, tol=0.01)

            if i > 0:
                crv = cmds.attachCurve(crv, crv_list[i-1], ch=0, rpo=0, kmk=0, m=0, bb=0.5, bki=0, p=0.1)[0]
                cmds.delete(crv_list[i-1])
                cmds.delete(old_crv)

            crv_list.append(crv)

        cmds.rename(crv, prefix + name + suffix)
        crv = prefix + name + suffix
        cmds.reverseCurve(crv, ch=0)
        return crv
    else:
        return None


