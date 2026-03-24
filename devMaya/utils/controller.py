import os
import json

from maya import cmds
import maya.api.OpenMaya as om

from devMaya.auto_rig.component.controller import Controller


"""
Functions :
creating controller
setting controller scale
rotating controller cvs
change controller color


TO DO:
changing controller shape
"""

def get_ctl(ctl_target: str | Controller):
    if not ctl_target:
        ctl_target = cmds.ls(sl=1)[0]
        if ctl_target == []:
            return None
        else:
            ctl_target = ctl_target[0]

    if isinstance(ctl_target, Controller):
        ctl = ctl_target
    else:
        ctl = Controller()
        ctl.build_from_scene_data(ctl_target)

    return ctl

# -- Create controller

def create_ctl(obj: str, zro_grp=False, parent=0, radius=1, normal=[0, 1, 0]):
    """
    Create a controller object
    """
    if obj == None:
        obj = cmds.ls(sl=1)
        if obj == []:
            return
        else:
            obj = obj[0]

    if "_" in str(obj):
        obj_name = str(obj).split('_', 1)[1]
    else:
        obj_name = str(obj)

    ctl = Controller()
    ctl.build(obj_name, zro_grp, radius, normal)

    cmds.matchTransform(ctl.zro_grp_name, obj, scale=False, rot=False)
    cmds.xform(ctl.zro_grp_name, s=[1, 1, 1])

    if parent == 1:
        cmds.parent(ctl.zro_grp_name, obj)

    if parent == 2:
        obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0] \
            if cmds.listRelatives(obj, parent=True, fullPath=1) \
            else None
        if obj_parent:
            cmds.parent(ctl.name, obj_parent)
        cmds.xform(ctl, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.parent(obj, ctl.name)

    return ctl

def create_ctls(obj_list: list[str], zro_grp=True, parent=0, radius=1, normal=[0, 1, 0], in_autorig=True):
    """
    Create multiple controllers
    """
    ctl_list = []
    if obj_list == []:
        obj_list = cmds.ls(sl=1)
        if obj_list == []:
            ctl = Controller()
            ctl.build("new", zro_grp, radius, normal)
            ctl_list.append(ctl)


    for obj in obj_list:
        ctl = create_ctl(obj, zro_grp=zro_grp, parent=parent, radius=radius, normal=normal)
        ctl_list.append(ctl)

    if not in_autorig:
        cmds.select(ctl_list)

    return ctl_list

def create_FK_ctl_chain(obj_list: list[str], zro_grp=True, parent=0, radius=1, normal=[0, 1, 0]):
    """
    Create a chain of Fk controllers
    """

    ctl_list = create_ctls(obj_list, zro_grp=zro_grp, parent=parent, radius=radius, normal=normal)

    for i in range(len(ctl_list)):
        if i == 0:
            continue
        cmds.parent(ctl_list[i].name, ctl_list[i - 1].zro_grp_name)

    cmds.select(ctl_list)

    return ctl_list

# -- Scale controller

def scale_ctl(ctl_target: str | Controller, value: float):
    """
    Scale a controller by accessing its cvs
    """
    ctl = get_ctl(ctl_target)
    if not ctl:
        return None

    cmds.scale(value, value, value, ctl.cvs, a=1, ws=1)

    return ctl

def scale_ctls(ctl_list: list[str | Controller] = [], scale: float = 1, in_autorig=True):
    """
    Scale multiple controllers
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        scale_ctl(ctl, scale)

    if not in_autorig:
        cmds.select(ctl_list)

# -- Rotate controller

def rotate_ctl(ctl_target: str | Controller, axis: str, degrees: int):
    """
    Rotate a controller by accessing its cvs
    """
    if isinstance(ctl_target, str):
        ctl = get_ctl(ctl_target)
        if not ctl:
            return None
    else:
        ctl = ctl_target

    if axis == "X":
        cmds.rotate(degrees, 0, 0, ctl.cvs, a=1, os=1)
    if axis == "Y":
        cmds.rotate(0, degrees, 0, ctl.cvs, a=1, os=1)
    if axis == "Z":
        cmds.rotate(0, 0, degrees, ctl.cvs, a=1, os=1)

    return ctl_target

def rotate_ctls(ctl_list: list[str | Controller] = [], axis: str = "X", degrees: int = 90, in_autorig=True):
    """
    Rotate multiple controllers
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        rotate_ctl(ctl_target=ctl, axis=axis, degrees=degrees)

    if not in_autorig:
        cmds.select(ctl_list)

# -- Color controller

def color_ctl(ctl_target : str, color: tuple[int, int, int]):
    """
    Change color for given Controller
    """

    ctl = get_ctl(ctl_target)
    if not ctl:
        return None

    ctl.color = color

def color_ctls(ctl_list : list[str | Controller], color: tuple[int, int, int], in_autorig=True):

    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        color_ctl(ctl_target=ctl, color=color)

    if not in_autorig:
        cmds.select(ctl_list)

# -- Shapes controller

def get_ctl_shapes(ctl: str) -> list[str]:
    """ Always get ctl shape(s) from provided ctl """
    if cmds.objectType(ctl) == "transform":
        shp = cmds.listRelatives(ctl, children=1, shapes=1)

    elif cmds.objectType(ctl) == "nurbsCurve":
        shp = [ctl]
    else:
        return []

    return shp

def change_ctl_shape(ctl_target: str, cv: list[tuple[float, float, float]] | str, degree=3, periodic=0):
    ctl = get_ctl(ctl_target)

    if isinstance(cv, str) and cv == "circle":
        crv = cmds.circle(r=1, normal=[0, 1, 0], ch=0)[0]
    else:
        crv = cmds.curve(p=cv, degree=degree, periodic=periodic)
    cmds.rename(crv, "ctl_temp")
    crv = "ctl_temp"
    cmds.rename(get_ctl_shapes(crv)[0], "ctl_tempShape")
    new_ctl = get_ctl(crv)

    shp_target_name = ctl.shape
    shp_target_new_name = ctl.name + "OLD"  # modify its name before giving old one to the new shape
    cmds.rename(shp_target_name, shp_target_new_name)
    cmds.rename(new_ctl.shape, shp_target_name)

    cmds.parent(new_ctl.shape, ctl, r=1, s=1)  # parent the source shape to the target transform

    cmds.delete(crv)
    cmds.delete(shp_target_new_name)  # remove old shape

def change_ctl_shapes(ctl_list: list[str], cv: list[tuple[float, float, float]], degree = 3, periodic=0, in_autorig=True):
    """
    Replace shape for provided ctl with new custom shape
    ctl: nurbsCurve or transform
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        change_ctl_shape(ctl, cv = cv, degree = degree, periodic=periodic)

    if not in_autorig:
        cmds.select(ctl_list)

def change_ctl_shapes_by_shape_name(ctl_list: list[str], shape_name: str, in_autorig=True):
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    shapes = ctl_custom_shapes()

    if shape_name not in shapes:
        return

    for ctl in ctl_list:
        ctl = Controller(ctl)
        ctl.shape = shape_name

    if not in_autorig:
        cmds.select(ctl_list)

def change_ctl_shapes_by_ctl_source(ctl_list: list[str], ctl_source: str = None, in_autorig=False):
    """
    Replace shape of provided controllers with shape of the last selected controller
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    if not ctl_source:
        ctl_source = ctl_list.pop(-1)

    ctl_src = get_ctl(ctl_source)

    for ctl in ctl_list:
        change_ctl_shape(ctl, cv = ctl_src.cvs_pos, degree = ctl_src.degree)

    if not in_autorig:
        cmds.select(ctl_list[:-2])

def ctl_custom_shapes() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shapes_file_path = os.path.join(base_dir, "controller_shapes.json")

    with open(shapes_file_path, mode="r", encoding='utf-8') as shapes_dict:
        shapes = json.load(shapes_dict)

    return shapes

# replaced by property inside object controller
def select_all_cvs(ctl_list: list[str] = []):
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    cvs_selected = [get_ctl(ctl).cvs for ctl in ctl_list]

    for ctl in ctl_list:
        print(get_ctl(ctl).cvs)

    cmds.select(*cvs_selected)

def get_ctl_cvs_pos(ctl: str | Controller = None) -> list[tuple[float, float, float]]:
    """
    Get cv data from a controller in order to store and rebuild it later
    ctl: nurbsCurve or transform
    """
    ctl = get_ctl(ctl)
    if not ctl:
        return None

    shp = get_ctl_shapes(ctl)
    if not shp:
        return None
    else:
        shp = shp[0]

    cvs = cmds.getAttr(shp + '.cv[*]')

    cv_data = []

    for c in cvs:
        cv_data.append([
            float(f"{c[0]}"),
            float(f"{c[1]}"),
            float(f"{c[2]}")
        ])

    return cv_data

def get_crv_degree(ctl: str | Controller) -> int:
    """
    Get crv degree
    ctl: nurbsCurve or transform
    """
    ctl = get_ctl(ctl)
    if not ctl:
        return None

    shp = get_ctl_shapes(ctl)[0]
    if not shp:
        return None
    else:
        shp = shp[0]

    return cmds.getAttr(shp + '.degree')
