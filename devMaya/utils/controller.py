import os
import json

from maya import cmds
import maya.api.OpenMaya as om

"""
Objects :
CONTROLLER


Functions :
creating controllers
setting controller scale
rotating controller cvs
change controller color


TO DO:
changing controller shape
"""


class Controller:
    OBJECT_TYPE = "CONTROLLER"

    def __init__(self, ctl_name: str = None):

        if ctl_name == None:
            self.ctl_name: str = None

            self.has_zro_grp: bool = False
            self.zro_grp_name: str = None

            self.radius: float = None
            self.normal: [int, int, int] = None
            self.color: tuple[int, int, int] = None

        else:
            self.build_controller(ctl_name)

    def __repr__(self):
        return self.ctl_name

    def __str__(self):
        return self.ctl_name
    #
    # def __contains__(self, item : str):
    #     return item in self.ctl_name

    def build_controller(self, obj: str, zro_grp=True, radius=1, normal=[0, 1, 0], shape="circle"):
        self.ctl_name = "ctl_" + obj

        self.has_zro_grp = zro_grp
        self.zro_grp_name = self.ctl_name + "_ZRO_grp"

        self.radius = radius
        self.normal = normal

        # cv = get_controller_shape(self.shape)
        # if shape = circle
        ctl = cmds.circle(name=self.ctl_name, radius=self.radius, normal=self.normal, ch=0)[0]
        cmds.rename(ctl, self.ctl_name)

        if self.has_zro_grp:
            ctl_grp = cmds.group(name=self.zro_grp_name)

    def build_controller_from_scene_ctl(self, ctl: str):

        # Filters
        if not cmds.objExists(ctl):
            print("Object doesn't exist")
            return

        shape = ctl + "Shape" if "Shape" not in ctl else ctl
        if not cmds.objectType(shape, isType="nurbsCurve"):
            print("Object is not a nurbsCurve")
            return

        self.ctl_name = ctl

        self.has_zro_grp = cmds.objExists(ctl + "_ZRO_grp")
        self.zro_grp_name = self.ctl_name + "_ZRO_grp"

        self.radius = 1
        self.normal = [0, 1, 0]

        # self.color =

    @property
    def pos(self):
        return cmds.xform(self.ctl_name, q=True, ws=True, t=True)

    @pos.setter
    def pos(self, pos: [float, float, float]):
        cmds.xform(self.ctl_name, q=True, ws=True, t=pos)

    @property
    def rot(self):
        cmds.xform(self.ctl_name, q=True, ws=True, ro=True)

    @rot.setter
    def rot(self, rot: [float, float, float]):
        cmds.xform(self.ctl_name, q=True, ws=True, ro=rot)

    @property
    def shapes(self) -> list[str]:
        return cmds.listRelatives(self.name, children=1, shapes=1)

    @property
    def degree(self) -> int:
        return cmds.getAttr(self.shapes[0] + '.degree')

    @property
    def cvs(self):
        return [f'{self.ctl_name}.cv[{i}]' for i in range(len(f'{self.ctl_name}.cv'))]

    @property
    def cvs_pos(self) -> list[tuple[float, float, float]]:
        cvs = cmds.getAttr(self.shapes[0] + '.cv[*]')
        cvs_pos = []
        for c in cvs:
            cvs_pos.append([
                float(f"{c[0]}"),
                float(f"{c[1]}"),
                float(f"{c[2]}")
            ])
        return cvs_pos

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
        ctl.build_controller_from_scene_ctl(ctl_target)

    return ctl

def get_ctl_shapes(ctl: str) -> list[str]:
    """ Always get ctl shape(s) from provided ctl """
    if cmds.objectType(ctl) == "transform":
        shp = cmds.listRelatives(ctl, children=1, shapes=1)

    elif cmds.objectType(ctl) == "nurbsCurve":
        shp = [ctl]
    else:
        return []

    return shp


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
    ctl.build_controller(obj_name, zro_grp, radius, normal)

    cmds.matchTransform(ctl.zro_grp_name, obj)

    if parent == 1:
        cmds.parent(ctl.zro_grp_name, obj)

    if parent == 2:
        obj_parent = cmds.listRelatives(obj, parent=True, fullPath=1)[0] \
            if cmds.listRelatives(obj, parent=True, fullPath=1) \
            else None
        if obj_parent:
            cmds.parent(ctl.ctl_name, obj_parent)
        cmds.xform(ctl, t=[0, 0, 0], ro=[0, 0, 0])
        cmds.parent(obj, ctl.ctl_name)

    return ctl

def create_ctls(obj_list: list[str], zro_grp=True, parent=0, radius=1, normal=[0, 1, 0], in_autorig=True):
    """
    Create multiple controllers
    """
    if obj_list == []:
        obj_list = cmds.ls(sl=1)

    ctl_list = []

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


def scale_ctl(ctl_target: str | Controller, value: float):
    """
    Scale a controller by accessing its cvs
    """
    ctl = get_ctl(ctl_target)
    if not ctl:
        return None

    cmds.scale(value, value, value, ctl.cvs, a=1, ws=1)

    return ctl

def scale_ctls(ctl_list: list[str | Controller] = [], scale: float = 1):
    """
    Scale multiple controllers
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        scale_ctl(ctl, scale)


def rotate_ctl(ctl_target: str | Controller, axis: str, degrees: int):
    """
    Rotate a controller by accessing its cvs
    """

    ctl = get_ctl(ctl_target)
    if not ctl:
        return None

    if axis == "X":
        cmds.rotate(degrees, 0, 0, ctl.cvs, a=1, os=1)
    if axis == "Y":
        cmds.rotate(0, degrees, 0, ctl.cvs, a=1, os=1)
    if axis == "Z":
        cmds.rotate(0, 0, degrees, ctl.cvs, a=1, os=1)

    return ctl_target

def rotate_ctls(ctl_list: list[str | Controller] = [], axis: str = "X", degrees: int = 90):
    """
    Rotate multiple controllers
    """
    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        rotate_ctl(ctl_target=ctl, axis=axis, degrees=degrees)


def color_ctl(ctl_target : str, color: tuple[int, int, int]):
    """
    Change color for given Controller
    """
    ctl = get_ctl(ctl_target)
    if not ctl:
        return None

    shp = get_ctl_shapes(ctl)[0]
    if not shp:
        return None

    cmds.setAttr(f"{shp}.overrideEnabled", 1)

    def remap_value(x, old_start, old_end, new_start, new_end):
        return new_start + ((x - old_start) / (old_end - old_start)) * (new_end - new_start)

    color = [remap_value(c, 0, 255, 0, 1) if c > 1 else c for c in color ]

    for i, channel in enumerate(["R", "G", "B"]):
        cmds.setAttr(f"{shp}.overrideColor{channel}", color[i])


def color_ctls(ctl_list : list[str | Controller], color: tuple[int, int, int]):

    if ctl_list == []:
        ctl_list = cmds.ls(sl=1)

    for ctl in ctl_list:
        color_ctl(ctl_target=ctl, color=color)





def change_ctl_shape(ctl_target: str, cv: list[tuple[float, float, float]], degree=3):
    ctl = get_ctl(ctl_target)

    shp_target_name = get_ctl_shapes(ctl)[0]
    shp_target_new_name = shp_target_name + "OLD"  # modify its name before giving old one to the new shape
    cmds.rename(shp_target_name, shp_target_new_name)

    ctl_s = cmds.duplicate(ctl_source)[0]

    shp = get_ctl_shapes(ctl_s)[0]

    cmds.rename(shp, shp_target_name)
    shp = shp_target_name

    cmds.parent(shp, ctl, r=1, s=1)  # parent the source shape to the target transform

    cmds.delete(shp_target_new_name)  # remove old shape

def change_ctl_shapes(ctl_list: list[str], cv: list[tuple[float, float, float]], degree = 3):
    """
    Replace shape for provided ctl with new custom shape
    ctl: nurbsCurve or transform
    """
    for ctl in ctl_list:
        change_ctl_shape(ctl, cv = cv, degree = degree)

def change_ctl_shape_by_ctl_source(ctl_list: list[str], ctl_source: str = None):
    """
    Replace shape of provided controllers with shape of the last selected controller
    """
    if not ctl_source:
        ctl_source = ctl_list.pop(-1)

    ctl_src = get_ctl(ctl_source)

    for ctl in ctl_list:
        change_ctl_shape(ctl, cv = ctl_src.cvs_pos, degree = ctl_src.degree)

def ctl_custom_shapes() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shapes_file_path = os.path.join(base_dir, "controller_shapes.json")

    with open(shapes_file_path, mode="r", encoding='utf-8') as shapes_dict:
        shapes = json.load(shapes_dict)

    return shapes

def change_ctl_shape_by_name(ctl_list: list[str], ctl_source: str = None):
    """
    Replace shape of provided controllers with shape from stored shapes in json
    """
    ctl = get_ctl(ctl_source)

    shapes = ctl_custom_shapes()

    try:
        cvs_pos = shapes.get(ctl_source)["cvs_pos"]
        degree = shapes.get(ctl_source)["degree"]
    except KeyError as e:
        print("Couldn't find custom controller shape called", ctl_source,":", e)
        return

    change_ctl_shapes(ctl_list, cv=cvs_pos, degree=degree)




# replaced by property inside object controller
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
