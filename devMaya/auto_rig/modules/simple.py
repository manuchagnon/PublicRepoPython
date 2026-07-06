from maya import cmds

from .base import BaseModule, ModuleType
from devMaya.auto_rig.component.controller import ControllerShapes, Controller
from devUi.utils.colors import Colors
from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.decorators import use, UseType
from devMaya.utils.api import (Attribute,
                               hinge_constraint

                               )

class Simple(BaseModule):

    TYPE : ModuleType = ModuleType.SIMPLE

    SIMPLE_SUFFIX : str = "_simple"

    CTL_COLOR : Colors | str = "green"
    CTL_SHAPE : ControllerShapes | str = "circle"

    CTL_OFFSET_SUFFIX : str = "_offset"
    CTL_OFFSET_COLOR : Colors | str = "yellow"
    CTL_OFFSET_SHAPE : ControllerShapes | str = "circle"

    HINGE_SUFFIX = "_hinge"

    def __init__(self, jnt : str=None, name=None, no_rot=False, config:Config=None):
        super().__init__(name=name, config=config)
        self._ctl_chain = []

        self._build_simple(jnt, no_rot=no_rot)


    def _build_simple(self, jnt, no_rot):
        ctl_main = Controller(self._name + self.SIMPLE_SUFFIX)
        ctl_main.shape = self.CTL_SHAPE
        ctl_main.color = self.CTL_COLOR
        ctl_main.shape_scale = self.SCALE
        self._ctl_chain.append(ctl_main)

        # duplicate joint
        if not jnt:
            pos = [0, 0, 0]
            rot = [0, 0, 0]
        elif no_rot:
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            rot = [0, 0, 0]
        else:
            pos = cmds.xform(jnt, q=1, ws=1, t=1)
            rot = cmds.xform(jnt, q=1, ws=1, ro=1)
        cmds.select(clear=True)
        new_jnt = cmds.joint(name=jnt + self.SIMPLE_SUFFIX if jnt else "jnt" + self.name + self.SIMPLE_SUFFIX)
        self.jnt = new_jnt

        cmds.parent(new_jnt, self._ctl_chain[-1])

        cmds.xform(ctl_main.zro_grp_name, ws=1, t=pos, ro=rot)

    @property
    def ctls(self):
        return self._ctl_chain

    @property
    def ctl(self):
        return self._ctl_chain[0]

    @use(UseType.MULTIPLE | UseType.UNNECESSARY)
    def add_offset_ctl(self, amount:int, stack_chain: bool=True):
        ctl_created = []
        for i in range(amount):
            ctl = Controller(self.name + str(i) + self.CTL_OFFSET_SUFFIX)
            ctl.shape = self.CTL_OFFSET_SHAPE
            ctl.color = self.CTL_OFFSET_COLOR
            ctl.shape_scale = self.SCALE * (0.65 ** i)
            ctl.shape_rot = [0, -90, 0]

            if i>0:
                cmds.parent(ctl.zro_grp_name, ctl_created[i-1])
            ctl_created.append(ctl)

        if stack_chain:
            cmds.parent(ctl_created[0].zro_grp_name, self._ctl_chain[-1])
        else:
            cmds.parent(ctl_created[0].zro_grp_name, self._ctl_chain[0])
        cmds.matchTransform(ctl_created[0].zro_grp_name, self._ctl_chain[0])
        self._ctl_chain.extend(ctl_created)
        cmds.parent(self.jnt, self._ctl_chain[-1])

    @use(UseType.UNIQUE | UseType.UNNECESSARY)
    def build_hinge_setup(self, orient_target_module : BaseModule, ctl_param=None):

        if not ctl_param:
            ctl_param = self.ctl_param

        hinge_constraint(orient_source=orient_target_module.output,
                         orient_target=self.ctls[0],
                         ctl_blend=ctl_param,
                         lct_name=self.LOCATOR_PREFIX + ctl_param.name + self.HINGE_SUFFIX,
                         lct_parent=self.ctls[0].zro_grp_name,
                         suffix=self.HINGE_SUFFIX)


    def set_input_and_output(self, input : str =None, output : str = None, input_pos=None, output_pos=None):
        super().set_input_and_output(input=self._ctl_chain[0], output=self._ctl_chain[-1], input_pos=input_pos, output_pos=output_pos)

        # cmds.xform(self.input, ws=1, t=self._ctl_chain[0].pos)
        # cmds.xform(self.output, ws=1, t=self._ctl_chain[-1].pos)
        #
        # cmds.parentConstraint(self._ctl_chain[-1], self.output, mo=False)

    def arrange_nodes(self, obj_to_parent=[]):
        self.obj_to_parent = obj_to_parent + [
            self._ctl_chain[0].zro_grp_name,
        ]
        super().arrange_nodes(self.obj_to_parent)

    def bind_jnts(self, bind_jnts:list[str]) -> list[str]:
        # jnt = self.jnt
        bind_jnts += [self.jnt]
        return super().bind_jnts(bind_jnts=bind_jnts)

class Cog(Simple):

    TYPE : ModuleType = ModuleType.COG

    SCALE_MULTIPLIER : float = 1.0

    COG_SUFFIX : str = "_cog"

    CTL_COG_COLOR : Colors | str = "pink"
    CTL_COG_SHAPE : ControllerShapes | str = "box"

    CTL_OFFSET_AMOUNT : int = 0

    CTL_OFFSET_PIVOT_SUFFIX : str = "_pivot"
    CTL_OFFSET_PIVOT_COLOR : Colors | str = "yellow"
    CTL_OFFSET_PIVOT_SHAPE : ControllerShapes | str = "sphere"

    def __init__(self, jnt : str, name=None, no_rot=True, config:Config=None):

        new_config = Config(
            {
            "SIMPLE_SUFFIX": self.COG_SUFFIX,
            "CTL_SHAPE" : self.CTL_COG_SHAPE,
            "CTL_COLOR": self.CTL_COG_COLOR,
            "SCALE" : config.get(key="SCALE") * self.SCALE_MULTIPLIER
            })
        cog_config = config + new_config

        super().__init__(jnt=jnt, name=name, no_rot=no_rot, config=cog_config)

        self.ctl_pivot_offset = None

        if self.CTL_OFFSET_AMOUNT:
            self.add_offset_ctl(amount=self.CTL_OFFSET_AMOUNT)
        self.ctls[0].shape_scale = [self.SCALE*1.7, self.SCALE*0.7, self.SCALE*1.7]

    def build_offset_rotate_pivot_ctl(self):
        """
        Create a ctl which can offset the rotate pivot of the output of the cog
        """
        ctl = Controller(self.jnt + self.CTL_OFFSET_PIVOT_SUFFIX)
        ctl.shape = self.CTL_OFFSET_PIVOT_SHAPE
        ctl.color = self.CTL_OFFSET_PIVOT_COLOR
        ctl.pos = self.ctls[0]
        ctl.shape_scale = self.SCALE * 0.7

        cmds.parent(ctl.zro_grp_name, self.ctls[0])
        dcm = cmds.createNode("decomposeMatrix", name="dcm_" + ctl.name)
        cmds.connectAttr(f"{ctl}.matrix", f"{dcm}.inputMatrix")
        cmds.connectAttr(f"{dcm}.outputTranslate", f"{self.ctls[-1].zro_grp_name}.rotatePivot")
        cmds.connectAttr(f"{dcm}.outputRotate", f"{self.ctls[-1].zro_grp_name}.rotate")

        self.ctl_pivot_offset = ctl

class Scapula(Simple):

    TYPE : ModuleType = ModuleType.SCAPULA

    SCALE_MULTIPLIER : float = 1.7

    SCAPULA_SUFFIX : str = "_scapula"

    CTL_SCAPULA_COLOR : Colors | str = "green"
    CTL_SCAPULA_SHAPE : Colors | str = "panel"

    def __init__(self, jnt : str, name=None, no_rot=False, config:Config=None):
        self.SCALE *= self.SCALE_MULTIPLIER
        new_config = Config(
            {
            "SIMPLE_SUFFIX": self.SCAPULA_SUFFIX,
            "CTL_SHAPE" : self.CTL_SCAPULA_SHAPE,
            "CTL_COLOR": self.CTL_SCAPULA_COLOR,
            "SCALE" : config.get(key="SCALE") * self.SCALE_MULTIPLIER
            })
        scapula_config = config + new_config
        scapula_config.set(key="SCALE", value = scapula_config.get(key="SCALE") * self.SCALE_MULTIPLIER)
        super().__init__(jnt=jnt, name=name, no_rot=no_rot, config=scapula_config)
        self.ctls[0].shape_rot = [90, 0, 0]

class Root(Simple):

    TYPE : ModuleType = ModuleType.ROOT

    SCALE_MULTIPLIER : float = 3.0

    ROOT_SUFFIX : str = "_root"

    CTL_ROOT_COLOR : Colors | str = "green"
    CTL_ROOT_SHAPE : ControllerShapes | str = "root"

    CTL_OFFSET_SHAPE : ControllerShapes | str = "circle and arrow"
    CTL_OFFSET_AMOUNT : int = 2

    def __init__(self, jnt:str=None, name=None, config:Config=None):
        self.SCALE *= self.SCALE_MULTIPLIER

        new_config = Config(
            {
            "SIMPLE_SUFFIX": self.ROOT_SUFFIX,
            "CTL_SHAPE" : self.CTL_ROOT_SHAPE,
            "CTL_COLOR": self.CTL_ROOT_COLOR,
            "SCALE": config.get(key="SCALE") * self.SCALE_MULTIPLIER
            })
        root_config = config + new_config
        root_config.set(key="SCALE", value = root_config.get(key="SCALE") * self.SCALE_MULTIPLIER)
        super().__init__(jnt=jnt, name=name, config=root_config)

        self.add_offset_ctl(amount=self.CTL_OFFSET_AMOUNT)
