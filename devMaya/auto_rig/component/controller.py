import os
import json

from maya import cmds
import maya.api.OpenMaya as om

from devMaya.auto_rig.component.base import BaseComponent, ComponentType
from devUi.utils.api import get_color

class Controller(BaseComponent):
    """
    A Controller component contains :
        - A nurbsCurve : ctl_name
        - A zero group parent : zro_grp_name
        - A side suffix : _L, _R, or None
    """

    COMPONENT_TYPE = ComponentType.CONTROLLER

    CONTROLLER_PREFIX = "ctl_"
    ZRO_GROUP_SUFFIX = "_ZRO_grp"

    def __init__(self, name: str = None):

        super().__init__(name)

        if name == None:
            self._name: str = None

            self.has_zro_grp: bool = False
            self.zro_grp_name: str = None

            self.radius: float = None
            self.normal: [int, int, int] = None

        else:
            if self.CONTROLLER_PREFIX in name and cmds.objExists(name):
                self.build_from_scene_data(name)
            else:
                self.build(name)

    # -- Builder

    def build(self, name: str, zro_grp=True, radius=1, normal=[0, 1, 0], shape="circle"):
        if self.CONTROLLER_PREFIX in name:
            name_without_prefix = name.split(self.CONTROLLER_PREFIX, 1)[-1]
            self._name = name_without_prefix if name_without_prefix else ""
        else:
            self._name = self.CONTROLLER_PREFIX + name

        self.radius = radius
        self.normal = normal

        ctl = cmds.circle(name=self.name, radius=self.radius, normal=self.normal, ch=0)[0]
        cmds.rename(ctl, self.name)

        self.has_zro_grp = zro_grp
        if zro_grp:
            self.zro_grp_name = self.name + self.ZRO_GROUP_SUFFIX
            cmds.group(name=self.zro_grp_name)
        else:
            self.zro_grp_name = None

    def build_from_scene_data(self, ctl: str):
        # name_rev = ctl[::-1]
        # name = name_rev.replace(self.CONTROLLER_PREFIX[::-1], "", 1)[::-1]
        self._name = ctl.split(self.CONTROLLER_PREFIX, 1)[-1]
        # self._name = name

        self.has_zro_grp = cmds.objExists(self.name + self.ZRO_GROUP_SUFFIX)
        self.zro_grp_name = self.name + self.ZRO_GROUP_SUFFIX

        self.radius = 1
        self.normal = [0, 1, 0]

    # -- Name

    @BaseComponent.name.getter
    def name(self):
        return self.CONTROLLER_PREFIX + BaseComponent.name.fget(self)

    # @BaseComponent.name.setter
    # def name(self, name):
    #     BaseComponent.name.fset(self, name)
    #     # self._name = self.CONTROLLER_PREFIX + self._name

    # -- Transform

    @property
    def pos(self):
        return cmds.xform(self.name, q=True, ws=True, t=True)

    @pos.setter
    def pos(self, pos: [float, float, float]):
        if self.has_zro_grp:
            cmds.xform(self.zro_grp_name, ws=True, t=pos)
        else:
            cmds.xform(self.name, ws=True, t=pos)

    @property
    def rot(self):
        cmds.xform(self.name, q=True, ws=True, ro=True)

    @rot.setter
    def rot(self, rot: [float, float, float]):
        if self.has_zro_grp:
            cmds.xform(self.zro_grp_name, ws=True, ro=rot)
        else:
            cmds.xform(self.name, ws=True, ro=rot)

    # -- Shape NurbsCurve

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

    # -- Color

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



def remap_value(x, old_start, old_end, new_start, new_end):
    """
    Used to remap a color in RGB 0-255 to a color in RGB 0-1
    """
    return new_start + ((x - old_start) / (old_end - old_start)) * (new_end - new_start)

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
