from maya import cmds
import copy

from devMaya.utils.api import (
    get_hierarchy_list_from_root_node,
    Attribute, Separator, lock_attributes,
    add_separator_attribute
)

from devMaya.auto_rig.configs.config import Config
from devMaya.auto_rig.modules.base import BaseModule, ModuleType
from devMaya.auto_rig.modules.ik_fk import Fk
from devMaya.auto_rig.component.controller import ControllerShapes
from devUi.utils.colors import Colors
from devMaya.auto_rig.decorators import use, UseType

class Spine(Fk):

    """
    Spine module for characters

    Spine requires :
    - a joint chain starting at the root joint until chest_end

    """

    TYPE = ModuleType.SPINE

    BUILD_ROOT_CTL : bool = True
    BUILD_BENDY : bool = True
    BUILD_OFFSET_CTL : bool = True
    BUILD_MAINTAIN_VOLUME : bool = False

    SCALE_MULTIPLIER : float = 4.0

    CTL_FK_SPINE_SHAPE : ControllerShapes | str = "circle"
    CTL_FK_SPINE_COLOR : Colors | str = "green"

    CTL_ROOT_SPINE_SHAPE : ControllerShapes | str = "box"
    CTL_ROOT_SPINE_COLOR : Colors | str = "pink"

    def __init__(self, jnt_list : list[str], name : str = None, config : Config = None):

        new_config = Config({
            "CTL_FK_SHAPE": self.CTL_FK_SPINE_SHAPE,
            "CTL_FK_COLOR": self.CTL_FK_SPINE_COLOR,
            "CTL_ROOT_SHAPE": self.CTL_ROOT_SPINE_SHAPE,
            "CTL_ROOT_COLOR": self.CTL_ROOT_SPINE_COLOR,
            "SCALE" : config.get(key="SCALE") * self.SCALE_MULTIPLIER
        })
        spine_config = config + new_config

        super().__init__(jnt_list=jnt_list, name=name, config=spine_config)

        if any([self.BUILD_BENDY, self.BUILD_OFFSET_CTL, self.BUILD_ROOT_CTL]):
            self.fk_limb.build_ctl_param(name=self.fk_limb.jnts[0])
            ctl_param = self.fk_limb.ctl_param
            pos = self.fk_limb.ctls[-1].pos
            ctl_param.shape = self.CTL_PARAMETER_SHAPE
            ctl_param.shape_rot = [90, 0, -90]
            ctl_param.shape_scale = self.SCALE / 5
            ctl_param.pos = [pos[0], pos[1], pos[2] - (self.SCALE*0.5)]
            cmds.parent(ctl_param.zro_grp_name, self.fk_limb.ctl_grp_name)

            add_separator_attribute(ctl_param.name, separator_name="Edit_Spine")

        if self.BUILD_ROOT_CTL:
            self.fk_limb.create_param_for_root_ctl(ctl_param=ctl_param)

        if self.BUILD_BENDY:
            self.fk_limb.create_param_for_bendy(ctl_param=ctl_param)

        if self.BUILD_OFFSET_CTL:
            self.fk_limb.create_param_for_offset_ctl(ctl_param=ctl_param)


