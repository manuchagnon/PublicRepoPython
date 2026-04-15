import os
import json

from maya import cmds
import maya.api.OpenMaya as om

from devMaya.auto_rig.component.base import BaseComponent, ComponentType
from devMaya.utils.group import create_grp
from devUi.utils.api import get_color
from devUtils.maths import remap_value

# class ControllerShape:
#     """
#     Object oriented way of accessing controller's shape
#     """
#
#     @property.setter
#     def rot(self, axis: str, degrees:int):
#         axis_list = ["X", "Y", "Z"]
#         if axis not in axis_list:
#             return
#         if axis == "X":
#             cmds.rotate(degrees, 0, 0, ctl.cvs, a=1, os=1)
#         if axis == "Y":
#             cmds.rotate(0, degrees, 0, ctl.cvs, a=1, os=1)
#         if axis == "Z":
#             cmds.rotate(0, 0, degrees, ctl.cvs, a=1, os=1)

class Controller(BaseComponent):
    """
    A Controller component contains :
        - A nurbsCurve : ctl_name
        - A zero group parent : zro_grp_name
        - A list of offset groups, can be empty
        - A Color value, Degree value, Line width value
        - A Shape
        - A side suffix : _L, _R, or None since its a BaseComponent
    Methods :
        - add offset group
    """

    COMPONENT_TYPE = ComponentType.CONTROLLER

    CONTROLLER_PREFIX = "ctl_"
    ZRO_GROUP_SUFFIX = "_ZRO_grp"

    def __init__(self, name: str = None):

        super().__init__(name)

        if name == None:
            self._name: str = None

            self.has_zro_grp: bool = False

            self.radius: float = None
            self.normal: [int, int, int] = None
            self._offset_grp_list = []

        else:
            if self.CONTROLLER_PREFIX in name and cmds.objExists(name):
                self.build_from_scene_data(name)
            else:
                self.build(name)

    #region -- Builder

    def build(self, name: str, zro_grp=True, radius=1, normal=[0, 1, 0], shape="circle"):
        if self.CONTROLLER_PREFIX in name:
            name_without_prefix = name.split(self.CONTROLLER_PREFIX, 1)[-1]
            self._name = name_without_prefix if name_without_prefix else ""
        else:
            self._name = name

        self.radius = radius
        self.normal = normal
        self._offset_grp_list = []

        ctl = cmds.circle(name=self.name, radius=self.radius, normal=self.normal, ch=0)[0]
        cmds.rename(ctl, self.name)

        self.has_zro_grp = zro_grp
        if zro_grp:
            cmds.group(name=self.zro_grp_name)

    def build_from_scene_data(self, ctl: str):
        # name_rev = ctl[::-1]
        # name = name_rev.replace(self.CONTROLLER_PREFIX[::-1], "", 1)[::-1]
        self._name = ctl.split(self.CONTROLLER_PREFIX, 1)[-1]
        # self._name = name

        self.has_zro_grp = cmds.objExists(self.name + self.ZRO_GROUP_SUFFIX)
        self._offset_grp_list = []

        self.radius = 1
        self.normal = [0, 1, 0]
    #endregion

    #region -- Name

    @BaseComponent.name.getter
    def name(self):
        return self.CONTROLLER_PREFIX + BaseComponent.name.fget(self)

    # @BaseComponent.name.setter
    # def name(self, name):
    #     BaseComponent.name.fset(self, name)
    #     # self._name = self.CONTROLLER_PREFIX + self._name

    #endregion

    #region -- Transform

    @property
    def pos(self):
        return cmds.xform(self.name, q=True, ws=True, t=True)

    @pos.setter
    def pos(self, pos: tuple[float, float, float]):
        if self.has_zro_grp:
            cmds.xform(self.zro_grp_name, ws=True, t=pos)
        else:
            cmds.xform(self.name, ws=True, t=pos)

    @property
    def rot(self):
        cmds.xform(self.name, q=True, ws=True, ro=True)

    @rot.setter
    def rot(self, rot: tuple[float, float, float]):
        if self.has_zro_grp:
            cmds.xform(self.zro_grp_name, ws=True, ro=rot)
        else:
            cmds.xform(self.name, ws=True, ro=rot)

    #endregion

    #region -- Shape NurbsCurve

    @property
    def shapes(self) -> list[str]:
        return cmds.listRelatives(self.name, children=1, shapes=1)

    @property
    def shape(self) -> str:
        return self.shapes[0]

    @shape.setter
    def shape(self, shape_name: str):
        """
        change the shape of the controller by applying a custom shape
        Args:
            - shape_name : the name of the shape to be transformed into,
            has to be one of the keys in the custom shape dictionary
        """
        # get the dictionary containing custom shapes
        shapes = ctl_custom_shapes()

        if not shape_name in shapes:
            return

        color = self.color
        line_width = self.line_width
        cv, degree, periodic = shapes[shape_name].values()

        if isinstance(cv, str) and cv == "circle":
            crv = cmds.circle(r=1, normal=[0, 1, 0], ch=0)[0]
        else:
            crv = cmds.curve(p=cv, degree=degree, periodic=periodic)
        cmds.rename(crv, "ctl_temp")
        crv = "ctl_temp"
        cmds.rename(f"{crv}Shape", "ctl_tempShape")
        new_ctl = Controller()
        new_ctl.build_from_scene_data(crv)

        old_shape_name = self.shape

        cmds.rename(self.shape, self.shape + "TO_DELETE")

        cmds.rename(new_ctl.shape, old_shape_name)

        cmds.parent(new_ctl.shape, self.name, r=1, s=1)  # parent the source shape to the target transform

        cmds.delete(crv)
        cmds.delete(old_shape_name + "TO_DELETE")  # remove old shape

        self.color = color
        self.line_width = line_width

    @property
    def degree(self) -> int:
        return cmds.getAttr(self.shapes[0] + '.degree')

    @property
    def cvs(self):
        return [f"{self.name}.cv[{i}]" for i in range(100) if cmds.objExists(f"{self.name}.cv[{i}]")]

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

    @property
    def line_width(self) -> int:
        return cmds.getAttr(self.shapes[0] + ".lineWidth")

    @line_width.setter
    def line_width(self, width):
        if width < 0:
            width = -1
        cmds.setAttr(self.shapes[0] + ".lineWidth", width)

    @property
    def shape_rot(self) -> tuple[float, float, float]:
        return (0, 0, 0)

    @shape_rot.setter
    def shape_rot(self, rot: tuple[float, float, float]):
        cmds.rotate(rot[0], rot[1], rot[2], self.cvs, a=1, os=1)

    @property
    def shape_scale(self) -> tuple[float, float, float]:
        return (0, 0, 0)

    @shape_scale.setter
    def shape_scale(self, scale: float):
        cmds.scale(scale, scale, scale, self.cvs, a=1, ws=1)

    #endregion

    #region -- Color

    @property
    def color(self) -> tuple[int, int, int]:
        color = cmds.getAttr(f"{self.shape}.overrideColorRGB")[0]
        return tuple([remap_value(c, 0, 1, 0, 255) for c in color])

    @color.setter
    def color(self, color: tuple[int, int, int] | str | int, channels=("R", "G", "B")):
        cmds.setAttr(f"{self.shape}.overrideEnabled", 1)
        cmds.setAttr(f"{self.shape}.overrideRGBColors", 1)

        if isinstance(color, str | int):
            color = get_color(color)
        # elif isinstance(color, int):
        #     color = get_color(color)
        elif isinstance(color, tuple):
            color = [color[0], color[1], color[2]]

        color = [remap_value(c, 0, 255, 0, 1) if c > 1 else 0 for c in color]

        for i, channel in enumerate(channels):
            cmds.setAttr(f"{self.shape}.overrideColor{channel}", color[i])

    # -- Side

    # Overwrite the side_suffix property setter in order to rename the zro_group as well
    @BaseComponent.side_suffix.setter
    def side_suffix(self, side):
        BaseComponent.side_suffix.fset(self, side)
        if self.has_zro_grp and self._side:
            cmds.rename(self.zro_grp_name, self.name + "_" + self._side + self.ZRO_GROUP_SUFFIX)

    #endregion

    #region -- Offset grp

    @property
    def zro_grp_name(self):
        if self.has_zro_grp:
            return self.name + self.ZRO_GROUP_SUFFIX
        else:
            return None

    @property
    def offset_grp_list(self) -> list[str]:
        """
        Find if this controller has offset parents groups above him, until it reaches its ZRO_grp
        Return a maximum of 10 offset groups because i did not want to use a while loop
        """
        if self.has_zro_grp:
            self._offset_grp_list = []
            parent = cmds.listRelatives(self.name, parent=True)[0]
            for i in range(10):
                if parent != self.zro_grp_name:
                    self._offset_grp_list.append(parent)
                    parent = cmds.listRelatives(parent, parent=True)[0]
                else:
                    break
            return self._offset_grp_list
        else:
            return []

    def add_offset_grp(self, gizmo_status = 0, gizmo_target_obj: str | None = None, suffix: str | None=None):
        """
        Add an offset group between this controller and its ZRO_grp
        Useful for copy rotation constraints
        """
        if not suffix:
            suffix = "offset" + str(len(self.offset_grp_list) + 1)
        create_grp(self.name, gizmo_status = gizmo_status, gizmo_target_obj = gizmo_target_obj, suffix = suffix)

    #endregion

def ctl_custom_shapes() -> dict:
    shapes_file_path = r"C:\Documents\2_GIT\MyRepo\devMaya\utils\controller_shapes.json"

    with open(shapes_file_path, mode="r", encoding='utf-8') as shapes_dict:
        shapes = json.load(shapes_dict)

    return shapes

if __name__ == '__main__':
    component = Controller("test")
    print("nom =",component.name)
    component.side_suffix = "L"
    print("true size =", component.side_suffix)
    print("nom =",component.name)


    print("-")

    component = Controller("test_side_02_L")
    print("nom =", component.name)
    print("true size =", component.side_suffix)

    print("-")

    component = Controller("ctl_test_side_02_R")
    print("component =", component, ", type =", component.COMPONENT_TYPE)
    print("nom =", component.name)
    print("true size =", component.side_suffix)
