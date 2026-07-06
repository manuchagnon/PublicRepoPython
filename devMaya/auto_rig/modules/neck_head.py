from maya import cmds

from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.modules.ik_fk import IkFk, Fk
from devMaya.auto_rig.configs.config import Config
from devUi.utils.colors import Colors
from devMaya.auto_rig.component.controller import ControllerShapes, Controller
from devMaya.utils.api import (hinge_constraint,
                               Separator, add_separator_attribute
                               )

class NeckHead(Fk):

    """
    NeckHead module for characters

    NeckHead requires :
    - a joint chain made of two joints : the neck joint and the head joint

    """

    BUILD_ROOT_CTL : bool = False
    BUILD_BENDY : bool = True
    BUILD_OFFSET_CTL : bool = True
    BUILD_MAINTAIN_VOLUME : bool = False

    HINGE_SUFFIX : str = "_global"

    CTL_HEAD_SHAPE : ControllerShapes | str = "box on floor"
    CTL_HEAD_COLOR : Colors | str = "red"

    SCALE_MULTIPLIER : float = 4

    def __init__(self, jnt_list:list[str], name=None, config:Config=None):
        if len(jnt_list) == 3:
            jnt_head_end = jnt_list[2]
        else:
            jnt_head_end = None

        super().__init__(jnt_list=jnt_list[:2], name=name, config=config)

        ctl_head = self.fk_limb.ctls[1]
        ctl_head.shape = self.CTL_HEAD_SHAPE
        ctl_head.color = self.CTL_HEAD_COLOR
        ctl_head.shape_rot = [0, 0, -90]
        ctl_head.shape_scale = self.SCALE * self.SCALE_MULTIPLIER

        ctl_neck = self.fk_limb.ctls[0]
        ctl_neck.shape_scale = 1.5


        if any([self.BUILD_BENDY, self.BUILD_OFFSET_CTL]):
            add_separator_attribute(ctl_head.name, separator_name="Edit_Neck")

        if self.BUILD_BENDY:
            self.fk_limb.create_param_for_bendy(ctl_param=ctl_head)

        if self.BUILD_OFFSET_CTL:
            self.fk_limb.create_param_for_offset_ctl(ctl_param=ctl_head)

    def build_hinge_setup(self, orient_target_module : BaseModule, ctl_param=None):

        ctl_param = self.get_actual_component(self.fk_limb.ctl)

        add_separator_attribute(ctl_param.name, separator_name="Edit_Head")

        hinge_constraint(orient_source=orient_target_module.output,
                         orient_target=self.fk_limb.ctls[1],
                         ctl_blend=self.fk_limb.ctls[1],
                         lct_name=self.LOCATOR_PREFIX + ctl_param.name + self.HINGE_SUFFIX,
                         lct_parent=self.fk_limb.ctls[1].zro_grp_name,
                         suffix=self.HINGE_SUFFIX)
